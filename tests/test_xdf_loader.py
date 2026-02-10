"""Tests for XDF loader, including channel metadata parsing."""

import pytest

from xdf_streamer.core.xdf_loader import XdfLoader
from xdf_streamer.models.stream_info import StreamInfo


def test_parse_stream_info_channels_from_stream_desc():
    """Channel info under stream['desc']['channels']['channel'] is parsed and normalized."""
    loader = XdfLoader()
    stream = {
        "info": {
            "name": ["MyEEG"],
            "type": ["EEG"],
            "channel_count": ["2"],
            "nominal_srate": ["250"],
            "channel_format": ["float32"],
        },
        "desc": {
            "channels": {
                "channel": [
                    {"label": ["Fp1"], "unit": ["V"], "type": ["EEG"]},
                    {"label": ["Fp2"], "unit": ["V"], "type": ["EEG"]},
                ],
            },
        },
    }
    info = loader._parse_stream_info(stream, 0)
    assert info.channel_count == 2
    assert len(info.channels) == 2
    assert info.channels[0]["label"] == "Fp1"
    assert info.channels[0]["unit"] == "V"
    assert info.channels[1]["label"] == "Fp2"


def test_parse_stream_info_channels_from_info_desc():
    """Channel info under info['desc']['channels']['channel'] is parsed and normalized."""
    loader = XdfLoader()
    stream = {
        "info": {
            "name": ["MyEEG"],
            "type": ["EEG"],
            "channel_count": ["2"],
            "nominal_srate": ["250"],
            "channel_format": ["float32"],
            "desc": {
                "channels": {
                    "channel": [
                        {"label": ["Cz"], "unit": ["microvolts"]},
                        {"label": ["Pz"], "unit": ["microvolts"]},
                    ],
                },
            },
        },
    }
    info = loader._parse_stream_info(stream, 0)
    assert info.channel_count == 2
    assert len(info.channels) == 2
    assert info.channels[0]["label"] == "Cz"
    assert info.channels[0]["unit"] == "microvolts"
    assert info.channels[1]["label"] == "Pz"


def test_parse_stream_info_single_channel_normalized_to_list():
    """Single channel (dict not list) is normalized and list-valued fields become strings."""
    loader = XdfLoader()
    stream = {
        "info": {
            "name": ["Markers"],
            "type": ["Markers"],
            "channel_count": ["1"],
            "nominal_srate": ["0"],
            "channel_format": ["string"],
            "desc": {
                "channels": {
                    "channel": {"label": ["Marker"], "type": ["Markers"]},
                },
            },
        },
    }
    info = loader._parse_stream_info(stream, 0)
    assert info.channel_count == 1
    assert len(info.channels) == 1
    assert info.channels[0]["label"] == "Marker"
    assert info.channels[0]["type"] == "Markers"


def test_parse_stream_info_placeholder_channels_when_empty():
    """When channel_count > 0 and no channel metadata, placeholder labels are used."""
    loader = XdfLoader()
    stream = {
        "info": {
            "name": ["NoChannels"],
            "type": ["EEG"],
            "channel_count": ["4"],
            "nominal_srate": ["128"],
            "channel_format": ["float32"],
        },
    }
    info = loader._parse_stream_info(stream, 0)
    assert info.channel_count == 4
    assert len(info.channels) == 4
    assert info.channels[0]["label"] == "Ch1"
    assert info.channels[0]["type"] == "Unknown"
    assert info.channels[3]["label"] == "Ch4"
