"""Input validation utilities."""

from ..models.stream_info import StreamInfo


def validate_sampling_rate(rate: float) -> bool:
    """Validate that sampling rate is positive and reasonable.

    Args:
        rate: Sampling rate in Hz

    Returns:
        True if valid, False otherwise
    """
    return rate > 0.0 and rate <= 1000000.0  # Reasonable upper limit


def validate_stream(stream_info: StreamInfo) -> tuple[bool, str]:
    """Validate stream information.

    Args:
        stream_info: Stream information to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if stream_info.sampling_rate < 1.0:
        return False, "Stream has irregular sampling rate (not supported)"
    if stream_info.channel_count <= 0:
        return False, "Stream has invalid channel count"
    if stream_info.channel_format == "string":
        return False, "String streams are not supported for streaming"
    if not validate_sampling_rate(stream_info.sampling_rate):
        return False, f"Invalid sampling rate: {stream_info.sampling_rate}"
    return True, ""
