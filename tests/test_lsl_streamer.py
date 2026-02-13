"""Tests for LSL streamer."""

import numpy as np

from xdf_streamer.core.lsl_streamer import LslStreamer
from xdf_streamer.models.stream_info import StreamInfo


def _channel_labels_from_lsl_info(lsl_stream_info):
    """Read back channel label values from a pylsl StreamInfo's desc."""
    desc = lsl_stream_info.desc()
    ch = desc.first_child()
    while not ch.empty():
        if ch.name() == "channels":
            break
        ch = ch.next_sibling()
    else:
        return []
    if ch.empty():
        return []
    labels = []
    node = ch.first_child()
    while not node.empty():
        if node.name() == "channel":
            labels.append(node.child_value("label"))
        node = node.next_sibling()
    return labels


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


def test_outlet_channel_metadata_list_values_written_as_strings():
    """Channel dicts with list values are written as single string (e.g. 'Fp1' not \"['Fp1']\")."""
    streamer = LslStreamer()
    channels_with_list_values = [{"label": ["Fp1"], "unit": ["V"]}, {"label": ["Fp2"], "unit": ["V"]}]
    stream_info = StreamInfo(
        name="TestStream",
        type="EEG",
        channel_count=2,
        sampling_rate=100.0,
        channel_format="float32",
        channels=channels_with_list_values,
        stream_id=0,
    )
    lsl_info = streamer._configure_stream_metadata(stream_info, None)
    labels = _channel_labels_from_lsl_info(lsl_info)
    assert labels == ["Fp1", "Fp2"], "Channel labels must be normalized strings, not list repr"


def test_create_outlet_empty_name_uses_fallback():
    """Creating outlet with empty name uses fallback 'UnnamedStream' so LSL accepts it."""
    streamer = LslStreamer()
    stream_info = StreamInfo(
        name="",
        type="EEG",
        channel_count=2,
        sampling_rate=100.0,
        channel_format="float32",
        channels=[],
        stream_id=0,
    )
    lsl_info = streamer._configure_stream_metadata(stream_info, None)
    assert lsl_info.name() == "UnnamedStream"
    outlet = streamer.create_outlet(stream_info)
    assert outlet is not None
