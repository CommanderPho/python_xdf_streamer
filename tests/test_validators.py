"""Tests for validators."""

from xdf_streamer.models.stream_info import StreamInfo
from xdf_streamer.utils.validators import validate_sampling_rate, validate_stream


def test_validate_sampling_rate():
    """Test sampling rate validation."""
    assert validate_sampling_rate(100.0) is True
    assert validate_sampling_rate(1000.0) is True
    assert validate_sampling_rate(0.0) is False
    assert validate_sampling_rate(-10.0) is False
    assert validate_sampling_rate(2000000.0) is False  # Too high


def test_validate_stream():
    """Test stream validation."""
    valid_stream = StreamInfo(
        name="TestStream",
        type="EEG",
        channel_count=32,
        sampling_rate=1000.0,
        channel_format="float32",
        channels=[],
        stream_id=0,
    )
    is_valid, msg = validate_stream(valid_stream)
    assert is_valid is True
    assert msg == ""

    # Test irregular rate
    irregular_stream = StreamInfo(
        name="TestStream",
        type="EEG",
        channel_count=32,
        sampling_rate=0.5,  # Irregular
        channel_format="float32",
        channels=[],
        stream_id=0,
    )
    is_valid, msg = validate_stream(irregular_stream)
    assert is_valid is False
    assert "irregular" in msg.lower()

    # Test string format
    string_stream = StreamInfo(
        name="TestStream",
        type="EEG",
        channel_count=1,
        sampling_rate=100.0,
        channel_format="string",
        channels=[],
        stream_id=0,
    )
    is_valid, msg = validate_stream(string_stream)
    assert is_valid is False
    assert "string" in msg.lower()

    # Test invalid channel count
    invalid_channels = StreamInfo(
        name="TestStream",
        type="EEG",
        channel_count=0,
        sampling_rate=100.0,
        channel_format="float32",
        channels=[],
        stream_id=0,
    )
    is_valid, msg = validate_stream(invalid_channels)
    assert is_valid is False
