"""Timing utilities for precise sample rate control."""

import time
from typing import Optional


def get_precise_time() -> float:
    """Get high-resolution current time.

    Returns:
        Current time in seconds using perf_counter
    """
    return time.perf_counter()


def calculate_sleep_duration(target_time: float, current_time: Optional[float] = None) -> float:
    """Calculate sleep duration to reach target time.

    Args:
        target_time: Target time in seconds
        current_time: Current time (if None, uses get_precise_time())

    Returns:
        Sleep duration in seconds (may be negative if already past target)
    """
    if current_time is None:
        current_time = get_precise_time()
    return target_time - current_time
