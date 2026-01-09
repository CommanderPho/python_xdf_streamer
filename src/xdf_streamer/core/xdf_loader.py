"""XDF file loading and parsing."""

from pathlib import Path
from typing import List

import numpy as np
import pyxdf

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

        self.xdf_data = XdfData()
        self.xdf_data.file_path = file_path

        for stream_id, stream in enumerate(streams):
            stream_info = self._parse_stream_info(stream, stream_id)
            self.xdf_data.streams.append(stream_info)

            # Extract time series data
            if "time_series" in stream and stream["time_series"] is not None:
                time_series = np.array(stream["time_series"])
                # Transpose if needed: channels x samples
                if time_series.ndim == 2 and time_series.shape[0] < time_series.shape[1]:
                    time_series = time_series.T
                self.xdf_data.time_series[stream_id] = time_series

        self.xdf_data.loaded = True
        return self.xdf_data

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
        if channel_count == 0 and "time_series" in stream and stream["time_series"] is not None:
            time_series = np.array(stream["time_series"])
            if time_series.ndim == 1:
                channel_count = 1
            else:
                channel_count = time_series.shape[1] if time_series.shape[0] > time_series.shape[1] else time_series.shape[0]

        # Get sampling rate
        nominal_srate = info.get("nominal_srate", [0.0])[0] if isinstance(info.get("nominal_srate"), list) else info.get("nominal_srate", 0.0)

        # Parse channel information
        channels = []
        desc = info.get("desc", {})
        if desc:
            chns = desc.get("channels", {})
            if chns:
                chn_list = chns.get("channel", [])
                if not isinstance(chn_list, list):
                    chn_list = [chn_list]
                for chn in chn_list:
                    if isinstance(chn, dict):
                        channels.append(chn)

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
