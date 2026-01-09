"""Tests for timing utilities."""

import time

from xdf_streamer.utils.timing import calculate_sleep_duration, get_precise_time


def test_get_precise_time():
    """Test precise time function."""
    t1 = get_precise_time()
    time.sleep(0.01)
    t2 = get_precise_time()
    assert t2 > t1
    assert (t2 - t1) >= 0.01


def test_calculate_sleep_duration():
    """Test sleep duration calculation."""
    current = get_precise_time()
    target = current + 0.1
    duration = calculate_sleep_duration(target, current)
    assert abs(duration - 0.1) < 0.001

    # Test past target
    duration = calculate_sleep_duration(current - 0.1, current)
    assert duration < 0
