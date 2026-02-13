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
    if not (stream_info.name or "").strip():
        return False, "Stream has no name"
    # Ensure sampling_rate is a float (defensive check)
    sampling_rate = float(stream_info.sampling_rate) if not isinstance(stream_info.sampling_rate, (int, float)) else float(stream_info.sampling_rate)
    
    # Ensure channel_count is an int (defensive check)
    channel_count = int(float(stream_info.channel_count)) if isinstance(stream_info.channel_count, str) else int(stream_info.channel_count) if stream_info.channel_count is not None else 0
    
    if sampling_rate < 1.0:
        return False, "Stream has irregular sampling rate (not supported)"
    if channel_count <= 0:
        return False, "Stream has invalid channel count"
    if stream_info.channel_format == "string":
        return False, "String streams are not supported for streaming"
    if not validate_sampling_rate(sampling_rate):
        return False, f"Invalid sampling rate: {sampling_rate}"
    return True, ""
