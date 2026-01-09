"""Tests for LSL streamer."""

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
    assert outlet.info().name() == "TestStream"
    assert outlet.info().channel_count() == 32
    assert outlet.info().nominal_srate() == 1000.0


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
    info = outlet.info()
    desc = info.desc()
    chns = desc.child("channels")
    assert chns is not None
