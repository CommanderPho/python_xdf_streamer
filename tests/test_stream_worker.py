"""Tests for stream worker."""

import threading
import time

import numpy as np
import pylsl

from xdf_streamer.core.lsl_streamer import LslStreamer
from xdf_streamer.core.stream_worker import StreamWorker
from xdf_streamer.models.stream_info import StreamInfo
from xdf_streamer.models.xdf_data import XdfData


def test_stream_worker_synthetic():
    """Test synthetic data streaming."""
    stop_event = threading.Event()
    worker = StreamWorker(stop_event)

    # Create a test outlet
    streamer = LslStreamer()
    stream_info = StreamInfo(
        name="TestSynthetic",
        type="EEG",
        channel_count=4,
        sampling_rate=100.0,
        channel_format="float32",
        channels=[],
        stream_id=0,
    )
    outlet = streamer.create_outlet(stream_info)

    # Stream for a short time
    def stream_short():
        worker.stream_synthetic_data(outlet, 100, 4)
        stop_event.set()

    thread = threading.Thread(target=stream_short, daemon=True)
    thread.start()
    time.sleep(0.1)  # Let it stream briefly
    stop_event.set()
    thread.join(timeout=1.0)


def test_stream_worker_xdf():
    """Test XDF data streaming."""
    stop_event = threading.Event()
    worker = StreamWorker(stop_event)

    # Create test XDF data
    stream_info = StreamInfo(
        name="TestXDF",
        type="EEG",
        channel_count=2,
        sampling_rate=10.0,  # Low rate for testing
        channel_format="float32",
        channels=[],
        stream_id=0,
    )
    xdf_data = XdfData()
    xdf_data.streams = [stream_info]
    # Create small test data: 5 samples x 2 channels
    xdf_data.time_series[0] = np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0], [7.0, 8.0], [9.0, 10.0]])

    # Create outlet
    streamer = LslStreamer()
    outlet = streamer.create_outlet(stream_info)

    # Stream the data
    thread = threading.Thread(target=worker.stream_xdf_data, args=(0, outlet, xdf_data), daemon=True)
    thread.start()
    thread.join(timeout=2.0)  # Should complete quickly with only 5 samples
