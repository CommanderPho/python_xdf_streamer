"""LSL stream creation and management."""

from typing import List, Optional

# Try to ensure liblsl is available before importing pylsl
try:
    from ..utils.liblsl_setup import setup_pylsl_import
    setup_pylsl_import()
except ImportError:
    pass  # liblsl_setup may not be available

import pylsl

from ..models.stream_info import StreamInfo
from ..utils.format_converter import map_channel_format


class LslStreamer:
    """Create and manage LSL stream outlets."""

    def create_outlet(self, stream_info: StreamInfo, source_id: Optional[str] = None) -> pylsl.StreamOutlet:
        """Create an LSL stream outlet from stream information.

        Args:
            stream_info: Stream information
            source_id: Optional source identifier (defaults to stream name)

        Returns:
            LSL StreamOutlet object
        """
        stream_info_lsl = self._configure_stream_metadata(stream_info, source_id)
        outlet = pylsl.StreamOutlet(stream_info_lsl)
        return outlet

    def _configure_stream_metadata(self, stream_info: StreamInfo, source_id: Optional[str] = None) -> pylsl.StreamInfo:
        """Configure LSL stream metadata from StreamInfo.

        Args:
            stream_info: Stream information
            source_id: Optional source identifier

        Returns:
            Configured LSL StreamInfo object
        """
        if source_id is None:
            source_id = f"RT_Sender_SimulationPC_{stream_info.name}"

        channel_format = map_channel_format(stream_info.channel_format)

        # Create stream info
        info = pylsl.StreamInfo(
            name=stream_info.name,
            type=stream_info.type,
            channel_count=stream_info.channel_count,
            nominal_srate=stream_info.sampling_rate,
            channel_format=channel_format,
            source_id=source_id,
        )

        # Add channel descriptions if available
        if stream_info.channels:
            desc = info.desc().append_child("channels")
            for channel in stream_info.channels:
                chn = desc.append_child("channel")
                for key, value in channel.items():
                    chn.append_child_value(key, str(value))

        return info
