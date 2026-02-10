"""XDF file loading and parsing."""

from datetime import datetime, timezone
from copy import deepcopy
from typing import Dict, List, Tuple, Optional, Callable, Union, Any
from nptyping import NDArray

from pathlib import Path
import numpy as np
import pandas as pd
import pyxdf

from phopylslhelper.core.data_modalities import DataModalityType
from phopylslhelper.general_helpers import unwrap_single_element_listlike_if_needed, readable_dt_str, from_readable_dt_str, localize_datetime_to_timezone, tz_UTC, tz_Eastern, _default_tz
from phopylslhelper.easy_time_sync import EasyTimeSyncParsingMixin


from ..models.stream_info import StreamInfo
from ..models.xdf_data import XdfData


class XdfLoader:
    """Load and parse XDF files."""

    def __init__(self):
        """Initialize XDF loader."""
        self.xdf_data: XdfData = XdfData()

    def load_xdf(self, file_path: Path | str) -> XdfData:
        """Load XDF file and parse streams.

        Args:
            file_path: Path to XDF file

        Returns:
            XdfData object containing loaded streams and data

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is invalid or cannot be parsed
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"XDF file not found: {file_path}")

        try:
            streams, header = pyxdf.load_xdf(str(file_path))
        except Exception as e:
            raise ValueError(f"Failed to load XDF file: {e}") from e

        if not streams:
            raise ValueError("No streams found in XDF file")

        # self.xdf_data = XdfData()
        self.xdf_data = XdfData(xdf_streams=streams, xdf_header=header, file_path=file_path)
        # self.xdf_data.file_path = file_path

        for stream_id, stream in enumerate(streams):
            parsed_stream_successfully: bool = False
            try:
                stream_info_dict, stream_datetimes, stream_timestamp_df = self._try_pho_custom_parse_stream_info(stream=stream, stream_id=stream_id)
                streams_timestamp_dfs[name] = stream_timestamp_df
                stream_info = StreamInfo(**stream_info_dict, stream_id=stream_id)

                parsed_stream_successfully = True
            except Exception as e:
                raise e


            if not parsed_stream_successfully:
                stream_info = self._parse_stream_info(stream, stream_id)
                self.xdf_data.streams.append(stream_info)

            # Extract time series data
            if "time_series" in stream and stream["time_series"] is not None:
                time_series = np.array(stream["time_series"])
                # Transpose if needed: channels x samples
                if time_series.ndim == 2 and time_series.shape[0] < time_series.shape[1]:
                    time_series = time_series.T
                self.xdf_data.time_series[stream_id] = time_series
        ## END for stream_id, stream in enumerate(streams)...

        self.xdf_data.loaded = True
        return self.xdf_data


    def _try_helper_parse_custom_stream_info(self, stream: dict, stream_info_dict: dict, file_datetime: datetime, fail_on_exception: bool=False) -> Dict:
        ## stream info keys:
        for a_key in ('type', 'stream_id', 'effective_srate', 'hostname', 'source_id', 'channel_count', 'channel_format', 'type', 'created_at', 'source_id', 'version', 'uid'):
            try:
                a_value = stream['info'].get(a_key, None)
                a_value = unwrap_single_element_listlike_if_needed(a_value)
                if a_value is not None:
                    stream_info_dict[a_key] = a_value

            except Exception as e:
                if fail_on_exception:
                    raise
                else:
                    print(f'_try_helper_parse_custom_stream_info(stream: {stream}, ...): \n\terror: {e}\n\tcontinuing...')
            
        ## stream footer:
        for a_key in ('first_timestamp', 'last_timestamp', 'sample_count'):
            try:
                a_value = stream.get('footer', {}).get('info', {}).get(a_key, None)
                a_value = unwrap_single_element_listlike_if_needed(a_value)
                if a_value is not None:
                    stream_info_dict[a_key] = float(a_value)

            except Exception as e:
                if fail_on_exception:
                    raise
                else:
                    print(f'_try_helper_parse_custom_stream_info(stream: {stream}, ...): \n\terror: {e}\n\tcontinuing...')


        ## Update the timestamp keys to float values, and the create a datetime column by adding them to the `file_datetime`
        timestamp_keys = ('created_at', 'first_timestamp', 'last_timestamp')
        for a_key in timestamp_keys:
            try:
                if stream_info_dict.get(a_key, None) is not None:
                    a_ts_value: float = float(stream_info_dict[a_key]) # ['169993.1081304000']
                    a_ts_value_dt: datetime = file_datetime + pd.Timedelta(nanoseconds=a_ts_value)
                    a_dt_key: str = f'{a_key}_dt'
                    stream_info_dict[a_dt_key] = a_ts_value_dt
                    print(f'\t{a_dt_key}: {readable_dt_str(a_ts_value_dt)}')

            except Exception as e:
                if fail_on_exception:
                    raise
                else:
                    print(f'_try_helper_parse_custom_stream_info(stream: {stream}, ...): \n\terror: {e}\n\tcontinuing...')

                

        ## try to get the special marker timestamp helpers:
        try:
            desc_info_dict = dict(stream['info'].get('desc', [{}])[0])
            stream_info_dict = EasyTimeSyncParsingMixin.parse_and_add_lsl_outlet_info_from_desc(desc_info_dict=desc_info_dict, stream_info_dict=stream_info_dict, should_fail_on_missing=False) ## Returns the updated `stream_info_dict`
        except Exception as e:
            if fail_on_exception:
                raise
            else:
                print(f'_try_helper_parse_custom_stream_info(stream: {stream}, ...): \n\terror: {e}\n\tcontinuing...')
        
        return stream_info_dict


    def _try_pho_custom_parse_stream_info(self, stream: dict, stream_id: int, skipped_stream_names=None, file_datetime=None, debug_print:bool=True) -> Optional[StreamInfo]:
        """ 
        stream_info_dict, stream_datetimes, stream_timestamp_df = 

        streams_timestamp_dfs[name] = stream_timestamp_df

        """
        if skipped_stream_names is None:
            skipped_stream_names = []

        header = self.xdf_data.xdf_header

        if file_datetime is None:
            file_datetime: datetime = datetime.strptime(header['info']['datetime'][0], "%Y-%m-%dT%H:%M:%S%z") # '2025-09-11T17:04:20-0400' -> datetime.datetime(2025, 9, 11, 17, 4, 20, tzinfo=datetime.timezone(datetime.timedelta(days=-1, seconds=72000)))           
            file_datetime = file_datetime.astimezone(timezone.utc)

        name: str = stream['info']['name'][0]
        
        stream_name_to_modality_dict: Dict = DataModalityType.get_stream_name_to_modality_dict()
        a_modality: DataModalityType = stream_name_to_modality_dict.get(name, None)
        if a_modality is not None:
            a_modality = a_modality.value

        if debug_print:
            print(f'======== STREAM "{name}":')
        
        fs = float(stream['info']['nominal_srate'][0])
        stream_info_dict: Dict = {'name': name, 'fs': fs}

        # sample_count: int = stream['footer']['info']['sample_count'][0]

        if (len(stream['time_series']) == 0):
            print(f'\tWARN: skipping empty stream: "{name}"')
            return None ## skip this stream
        elif (name in skipped_stream_names):
            print(f'\tWARN: skipping "{name}" with name in skipped_stream_names: {skipped_stream_names}')
            return None  ## skip this stream
        else:
            n_samples, n_channels = np.shape(stream['time_series'])
            stream_info_dict.update(**{'n_samples': n_samples, 'n_channels': n_channels})

            stream_info_dict = self._try_helper_parse_custom_stream_info(stream=stream, stream_info_dict=stream_info_dict, file_datetime=file_datetime, fail_on_exception=False)

            # ## stream info keys:
            # for a_key in ('type', 'stream_id', 'effective_srate', 'hostname', 'source_id', 'channel_count', 'channel_format', 'type', 'created_at', 'source_id', 'version', 'uid'):
            #     a_value = stream['info'].get(a_key, None)
            #     a_value = unwrap_single_element_listlike_if_needed(a_value)
            #     if a_value is not None:
            #         stream_info_dict[a_key] = a_value

            # ## stream footer:
            # for a_key in ('first_timestamp', 'last_timestamp', 'sample_count'):
            #     a_value = stream.get('footer', {}).get('info', {}).get(a_key, None)
            #     a_value = unwrap_single_element_listlike_if_needed(a_value)
            #     if a_value is not None:
            #         stream_info_dict[a_key] = float(a_value)

            # ## Update the timestamp keys to float values, and the create a datetime column by adding them to the `file_datetime`
            # timestamp_keys = ('created_at', 'first_timestamp', 'last_timestamp')
            # for a_key in timestamp_keys:
            #     if stream_info_dict.get(a_key, None) is not None:
            #         a_ts_value: float = float(stream_info_dict[a_key]) # ['169993.1081304000']
            #         a_ts_value_dt: datetime = file_datetime + pd.Timedelta(nanoseconds=a_ts_value)
            #         a_dt_key: str = f'{a_key}_dt'
            #         stream_info_dict[a_dt_key] = a_ts_value_dt
            #         print(f'\t{a_dt_key}: {readable_dt_str(a_ts_value_dt)}')
                    

            # ## try to get the special marker timestamp helpers:
            # desc_info_dict = dict(stream['info'].get('desc', [{}])[0])
            # stream_info_dict = EasyTimeSyncParsingMixin.parse_and_add_lsl_outlet_info_from_desc(desc_info_dict=desc_info_dict, stream_info_dict=stream_info_dict, should_fail_on_missing=False) ## Returns the updated `stream_info_dict`
            
            ## Add stream info dict to the stream_infos list:
            # stream_infos.append(stream_info_dict)
            ## OUTPUTS: stream_info_dict

            ## Process Data:
            stream_first_timestamp: float = float(stream['footer']['info']['first_timestamp'][0]) # 29605.4462984
            stream_last_timestamp: float = float(stream['footer']['info']['last_timestamp'][0]) # 30373.1166288

            stream_first_timestamp = pd.Timedelta(seconds=stream_first_timestamp)
            stream_last_timestamp = pd.Timedelta(seconds=stream_last_timestamp)

            stream_approx_dur_sec: float = (stream_last_timestamp - stream_first_timestamp).total_seconds()
            if debug_print:
                print(f'\tstream_approx_dur_sec: {stream_approx_dur_sec}')

            stream_timestamps = deepcopy(np.array(stream['time_stamps']))
            stream_clock_times = deepcopy(np.array(stream['clock_times']))

            if debug_print:
                print(f'\tstream_timestamps: {stream_timestamps.tolist()}')
                print(f'\tstream_clock_times: {stream_clock_times.tolist()}')

            zeroed_stream_timestamps = deepcopy(stream_timestamps)
            zeroed_stream_clock_times = deepcopy(stream_clock_times)

            if len(zeroed_stream_timestamps) > 0:
                assert stream_info_dict.get('stream_start_lsl_local_offset_seconds', None) is not None
                # zeroed_stream_timestamps = zeroed_stream_timestamps - zeroed_stream_timestamps[0] ## subtract out the first timestamp
                zeroed_stream_timestamps = zeroed_stream_timestamps - stream_info_dict['stream_start_lsl_local_offset_seconds']
            if len(zeroed_stream_clock_times) > 0:
                zeroed_stream_clock_times = zeroed_stream_clock_times - zeroed_stream_clock_times[0] ## subtract out the first timestamp
            
            zeroed_stream_timestamps_dt = np.array([pd.Timedelta(seconds=v) for v in zeroed_stream_timestamps]) ## convert to timedelta (for no reason)
            # stream_datetimes = np.array([stream_info_dict.get('recording_start_datetime', file_datetime) + pd.Timedelta(seconds=v) for v in zeroed_stream_timestamps]) ## List[datetime]
            assert stream_info_dict.get('stream_start_datetime', None) is not None
            stream_datetimes = np.array([stream_info_dict.get('stream_start_datetime', file_datetime) + pd.Timedelta(seconds=v) for v in zeroed_stream_timestamps]) ## compatibility

            ## OUTPUTS: stream_datetimes

            ## post-zeroed:
            if debug_print:
                print(f'\tpost-zeroed stream_timestamps: {stream_timestamps.tolist()}')
                print(f'\tpost-zeroed stream_clock_times: {stream_clock_times.tolist()}')

            ## STREAM OUTPUTS: stream_timestamps, stream_clock_times, zeroed_stream_timestamps, zeroed_stream_clock_times, zeroed_stream_timestamps_dt, stream_datetimes
            # a_raw_df: pd.DataFrame = pd.DataFrame(dict(onset=zeroed_stream_timestamps, onset_dt=zeroed_stream_timestamps_dt, duration=([0.0] * len(zeroed_stream_timestamps_dt)), description=logger_strings))
            # all_annotations.append(a_raw_df)

            ## UPDATE: `streams_timestamp_dfs`
            stream_timestamp_df = pd.DataFrame(dict(stream_timestamps=stream_timestamps,
                zeroed_stream_timestamps=zeroed_stream_timestamps, zeroed_stream_timestamps_dt=zeroed_stream_timestamps_dt,
                # stream_clock_times=stream_clock_times,  zeroed_stream_clock_times=zeroed_stream_clock_times,
                stream_datetimes = stream_datetimes,
            ))

            # ## In lightweight mode, only collect bare stream metadata and skip heavy data processing:
            # if not should_load_full_file_data:
            #     continue

            return stream_info_dict, stream_datetimes, stream_timestamp_df



    def _parse_stream_info(self, stream: dict, stream_id: int) -> StreamInfo:
        """Parse stream information from XDF stream dict.

        Args:
            stream: XDF stream dictionary
            stream_id: Stream identifier

        Returns:
            StreamInfo object
        """
        info = stream.get("info", {})
        name = info.get("name", [""])[0] if isinstance(info.get("name"), list) else info.get("name", f"Stream-{stream_id}")
        stream_type = info.get("type", [""])[0] if isinstance(info.get("type"), list) else info.get("type", "Unknown")

        # Get channel format
        channel_format = info.get("channel_format", [""])[0] if isinstance(info.get("channel_format"), list) else info.get("channel_format", "float32")

        # Get channel count
        channel_count = info.get("channel_count", [0])[0] if isinstance(info.get("channel_count"), list) else info.get("channel_count", 0)
        # Ensure it's an int (handle string values from XDF)
        if isinstance(channel_count, str):
            channel_count = int(float(channel_count))  # Convert string -> float -> int
        elif channel_count is not None:
            channel_count = int(channel_count)
        else:
            channel_count = 0
        
        if channel_count == 0 and "time_series" in stream and stream["time_series"] is not None:
            time_series = np.array(stream["time_series"])
            if time_series.ndim == 1:
                channel_count = 1
            else:
                channel_count = time_series.shape[1] if time_series.shape[0] > time_series.shape[1] else time_series.shape[0]

        # Get sampling rate
        nominal_srate = info.get("nominal_srate", [0.0])[0] if isinstance(info.get("nominal_srate"), list) else info.get("nominal_srate", 0.0)
        # Ensure it's a float (handle string values from XDF)
        if isinstance(nominal_srate, str):
            nominal_srate = float(nominal_srate)
        else:
            nominal_srate = float(nominal_srate) if nominal_srate is not None else 0.0

        ## Custom Parsing:
        fs = float(stream['info']['nominal_srate'][0])
        stream_info_dict: Dict = {'name': name, 'fs': fs}
        stream_info_dict = self._try_helper_parse_custom_stream_info(stream=stream, stream_info_dict=stream_info_dict, file_datetime=file_datetime, fail_on_exception=False)

        # Parse channel information: desc may be at stream level or under info (pyxdf layout)
        channels = []
        desc = stream.get("desc", {}) or info.get("desc", {})
        if desc and isinstance(desc, dict):
            chns = desc.get("channels", {})
            if chns and isinstance(chns, dict):
                chn_list = chns.get("channel", [])
                if not isinstance(chn_list, list):
                    chn_list = [chn_list]
                for chn in chn_list:
                    if isinstance(chn, dict):
                        # Normalize: pyxdf often uses list-valued fields (e.g. {"label": ["Fp1"]})
                        normalized = {}
                        for k, v in chn.items():
                            if isinstance(v, list):
                                normalized[k] = str(v[0]) if v else ""
                            else:
                                normalized[k] = str(v) if v is not None else ""
                        channels.append(normalized)
        # Fallback: when XDF has no channel metadata, use placeholder labels
        if channel_count > 0 and len(channels) == 0:
            channels = [{"label": f"Ch{i+1}", "type": "Unknown"} for i in range(channel_count)]

        # stream_info_dict, stream_datetimes, stream_timestamp_df = 

        return StreamInfo(
            name=name,
            type=stream_type,
            channel_count=channel_count,
            sampling_rate=nominal_srate,
            channel_format=channel_format,
            channels=channels,
            stream_id=stream_id,
        )

    def get_streams(self) -> List[StreamInfo]:
        """Get list of all streams.

        Returns:
            List of StreamInfo objects
        """
        return self.xdf_data.streams

    def get_time_series(self, stream_id: int) -> np.ndarray:
        """Get time series data for a stream.

        Args:
            stream_id: Stream identifier

        Returns:
            NumPy array of time series data (samples x channels)

        Raises:
            KeyError: If stream_id not found
        """
        if stream_id not in self.xdf_data.time_series:
            raise KeyError(f"Stream {stream_id} not found")
        return self.xdf_data.time_series[stream_id]

    def validate_stream(self, stream_id: int) -> tuple[bool, str]:
        """Validate a stream.

        Args:
            stream_id: Stream identifier

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.xdf_data.loaded:
            return False, "No XDF file loaded"
        if stream_id >= len(self.xdf_data.streams):
            return False, f"Invalid stream_id: {stream_id}"
        from ..utils.validators import validate_stream
        return validate_stream(self.xdf_data.streams[stream_id])
