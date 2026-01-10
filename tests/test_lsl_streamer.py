"""Tests for LSL streamer."""

import numpy as np

from xdf_streamer.core.lsl_streamer import LslStreamer
from xdf_streamer.models.stream_info import StreamInfo


def test_create_outlet():
    """Test outlet creation."""
    streamer = LslStreamer()
    stream_info = StreamInfo(
        name="TestStream",
        type="EEG",
        channel_count=32,
        sampling_rate=1000.0,
        channel_format="float32",
        channels=[],
        stream_id=0,
    )
    outlet = streamer.create_outlet(stream_info)
    assert outlet is not None
    # Verify outlet can push data (indirect verification it was created correctly)
    sample = np.zeros(32, dtype=np.float32)
    outlet.push_sample(sample)


def test_create_outlet_with_channels():
    """Test outlet creation with channel metadata."""
    streamer = LslStreamer()
    channels = [{"label": "C1", "unit": "V"}, {"label": "C2", "unit": "V"}]
    stream_info = StreamInfo(
        name="TestStream",
        type="EEG",
        channel_count=2,
        sampling_rate=100.0,
        channel_format="float32",
        channels=channels,
        stream_id=0,
    )
    outlet = streamer.create_outlet(stream_info)
    assert outlet is not None
    # Verify outlet can push data with correct channel count
    sample = np.zeros(2, dtype=np.float32)
    outlet.push_sample(sample)
