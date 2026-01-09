"""Utility modules."""

from .timing import calculate_sleep_duration, get_precise_time
from .validators import validate_sampling_rate, validate_stream

# Lazy import format_converter to avoid pylsl import errors
try:
    from .format_converter import CHANNEL_FORMAT_MAP, map_channel_format
    __all__ = [
        "CHANNEL_FORMAT_MAP",
        "map_channel_format",
        "calculate_sleep_duration",
        "get_precise_time",
        "validate_sampling_rate",
        "validate_stream",
    ]
except RuntimeError:
    # pylsl not available, skip format_converter exports
    __all__ = [
        "calculate_sleep_duration",
        "get_precise_time",
        "validate_sampling_rate",
        "validate_stream",
    ]
