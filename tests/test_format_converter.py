"""Tests for format converter."""

import pytest
import pylsl

from xdf_streamer.utils.format_converter import CHANNEL_FORMAT_MAP, map_channel_format


def test_channel_format_map():
    """Test channel format mapping."""
    assert CHANNEL_FORMAT_MAP["float32"] == pylsl.cf_float32
    assert CHANNEL_FORMAT_MAP["double64"] == pylsl.cf_double64
    assert CHANNEL_FORMAT_MAP["int8"] == pylsl.cf_int8
    assert CHANNEL_FORMAT_MAP["string"] == pylsl.cf_string


def test_map_channel_format():
    """Test format mapping function."""
    assert map_channel_format("float32") == pylsl.cf_float32
    assert map_channel_format("double64") == pylsl.cf_double64
    assert map_channel_format("int16") == pylsl.cf_int16


def test_map_channel_format_invalid():
    """Test format mapping with invalid format."""
    with pytest.raises(ValueError):
        map_channel_format("invalid_format")
