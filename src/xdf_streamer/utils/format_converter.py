"""Channel format conversion utilities."""

# Lazy import pylsl to avoid errors when liblsl is not installed
_pylsl = None


def _get_pylsl():
    """Lazy import pylsl."""
    global _pylsl
    if _pylsl is None:
        try:
            import pylsl
            _pylsl = pylsl
        except RuntimeError as e:
            raise RuntimeError(
                "pylsl requires liblsl binary library. "
                "Install with: conda install -c conda-forge liblsl "
                "or set PYLSL_LIB environment variable. "
                f"Original error: {e}"
            ) from e
    return _pylsl


def _get_channel_format_map():
    """Get channel format mapping (lazy)."""
    pylsl = _get_pylsl()
    return {
        "float32": pylsl.cf_float32,
        "double64": pylsl.cf_double64,
        "int8": pylsl.cf_int8,
        "int16": pylsl.cf_int16,
        "int32": pylsl.cf_int32,
        "int64": pylsl.cf_int64,
        "string": pylsl.cf_string,
    }


def map_channel_format(xdf_format: str) -> int:
    """Map XDF channel format string to LSL channel format constant.

    Args:
        xdf_format: XDF channel format string (e.g., "float32", "cf_float32", "double64")

    Returns:
        LSL channel format constant

    Raises:
        ValueError: If format is not supported
        RuntimeError: If pylsl/libsl is not available
    """
    if isinstance(xdf_format, str) and xdf_format.startswith("cf_"):
        xdf_format = xdf_format[3:]
    format_map = _get_channel_format_map()
    if xdf_format not in format_map:
        raise ValueError(f"Unsupported channel format: {xdf_format}")
    return format_map[xdf_format]


# For backward compatibility, but will raise error if pylsl not available
try:
    CHANNEL_FORMAT_MAP = _get_channel_format_map()
except RuntimeError:
    CHANNEL_FORMAT_MAP = {}  # Empty dict if pylsl not available
