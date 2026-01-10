"""Tests for multi-stream XDF loading and rebroadcasting."""

import threading
import time
from pathlib import Path

import numpy as np
import pytest

from xdf_streamer.core.lsl_streamer import LslStreamer
from xdf_streamer.core.multi_stream_rebroadcaster import MultiStreamRebroadcaster
from xdf_streamer.core.stream_worker import StreamWorker
from xdf_streamer.core.xdf_loader import XdfLoader
from xdf_streamer.models.stream_info import StreamInfo
from xdf_streamer.models.xdf_data import XdfData


def create_multi_stream_xdf_data(num_streams: int = 3) -> XdfData:
    """Create XdfData with multiple streams for testing.

    Args:
        num_streams: Number of streams to create

    Returns:
        XdfData object with multiple streams
    """
    xdf_data = XdfData()
    xdf_data.loaded = True

    for i in range(num_streams):
        channel_count = 8 + i * 2
        sampling_rate = 100.0 + i * 50.0
        num_samples = 100 + i * 50

        # Create stream info
        stream_info = StreamInfo(
            name=f"TestStream-{i}",
            type="EEG" if i % 2 == 0 else "Markers",
            channel_count=channel_count,
            sampling_rate=sampling_rate,
            channel_format="float32",
            channels=[{"label": f"Ch{j}", "unit": "V", "type": "EEG"} for j in range(channel_count)],
            stream_id=i,
        )

        xdf_data.streams.append(stream_info)

        # Create time series data (samples x channels)
        time_series = np.random.randn(num_samples, channel_count).astype(np.float32)
        xdf_data.time_series[i] = time_series

    return xdf_data


@pytest.fixture
def multi_stream_xdf_data():
    """Fixture providing multi-stream XdfData."""
    return create_multi_stream_xdf_data(num_streams=3)


def test_multi_stream_xdf_data_structure(multi_stream_xdf_data):
    """Test multi-stream XdfData structure."""
    xdf_data = multi_stream_xdf_data

    assert xdf_data.loaded is True
    assert len(xdf_data.streams) == 3
    assert len(xdf_data.time_series) == 3

    # Verify stream properties
    for i, stream_info in enumerate(xdf_data.streams):
        assert stream_info.name == f"TestStream-{i}"
        assert stream_info.stream_id == i
        assert stream_info.channel_count == 8 + i * 2
        assert stream_info.sampling_rate == 100.0 + i * 50.0
        assert i in xdf_data.time_series
        assert xdf_data.time_series[i].shape[1] == stream_info.channel_count


def test_create_outlets_for_all_streams(multi_stream_xdf_data):
    """Test creating LSL outlets for all streams in a multi-stream XDF file."""
    xdf_data = multi_stream_xdf_data

    streamer = LslStreamer()
    outlets = []

    for stream_info in xdf_data.streams:
        outlet = streamer.create_outlet(stream_info)
        outlets.append(outlet)

        # Verify outlet was created and can push data with correct channel count
        assert outlet is not None
        sample = np.zeros(stream_info.channel_count, dtype=np.float32)
        outlet.push_sample(sample)

    assert len(outlets) == len(xdf_data.streams)


def test_rebroadcast_all_streams(multi_stream_xdf_data):
    """Test rebroadcasting all streams from a multi-stream XDF file."""
    xdf_data = multi_stream_xdf_data

    streamer = LslStreamer()
    stop_event = threading.Event()
    outlets = []
    threads = []

    # Create outlets and start streaming for all streams
    for stream_id, stream_info in enumerate(xdf_data.streams):
        outlet = streamer.create_outlet(stream_info)
        outlets.append(outlet)

        worker = StreamWorker(stop_event)
        thread = threading.Thread(
            target=worker.stream_xdf_data, args=(stream_id, outlet, xdf_data), daemon=True
        )
        thread.start()
        threads.append(thread)

    # Let streams run briefly
    time.sleep(0.5)

    # Stop all streams
    stop_event.set()

    # Wait for threads to complete
    for thread in threads:
        thread.join(timeout=2.0)

    assert len(outlets) == len(xdf_data.streams)
    assert len(threads) == len(xdf_data.streams)


def test_rebroadcast_selected_streams(multi_stream_xdf_data):
    """Test rebroadcasting only selected streams from a multi-stream XDF file."""
    xdf_data = multi_stream_xdf_data

    streamer = LslStreamer()
    stop_event = threading.Event()
    outlets = []
    threads = []

    # Select only streams 0 and 2 (skip stream 1)
    selected_stream_ids = [0, 2]

    for stream_id in selected_stream_ids:
        stream_info = xdf_data.streams[stream_id]
        outlet = streamer.create_outlet(stream_info)
        outlets.append(outlet)

        worker = StreamWorker(stop_event)
        thread = threading.Thread(
            target=worker.stream_xdf_data, args=(stream_id, outlet, xdf_data), daemon=True
        )
        thread.start()
        threads.append(thread)

    # Let streams run briefly
    time.sleep(0.5)

    # Stop all streams
    stop_event.set()

    # Wait for threads to complete
    for thread in threads:
        thread.join(timeout=2.0)

    assert len(outlets) == len(selected_stream_ids)
    assert len(threads) == len(selected_stream_ids)


def test_multi_stream_concurrent_rebroadcast(multi_stream_xdf_data):
    """Test that multiple streams can rebroadcast concurrently without interference."""
    xdf_data = multi_stream_xdf_data

    streamer = LslStreamer()
    stop_event = threading.Event()
    outlets = []
    threads = []
    completion_flags = {i: False for i in range(len(xdf_data.streams))}

    def create_completion_callback(stream_id):
        def callback():
            completion_flags[stream_id] = True

        return callback

    # Create outlets and start streaming for all streams
    for stream_id, stream_info in enumerate(xdf_data.streams):
        outlet = streamer.create_outlet(stream_info)
        outlets.append(outlet)

        worker = StreamWorker(stop_event)
        callback = create_completion_callback(stream_id)
        thread = threading.Thread(
            target=worker.stream_xdf_data,
            args=(stream_id, outlet, xdf_data, callback),
            daemon=True,
        )
        thread.start()
        threads.append(thread)

    # Wait for all streams to complete (they should finish quickly with small test data)
    for thread in threads:
        thread.join(timeout=5.0)

    # Verify all streams completed
    assert all(completion_flags.values()), "Not all streams completed successfully"
    assert len(outlets) == len(xdf_data.streams)


def test_multi_stream_rebroadcaster_class(multi_stream_xdf_data):
    """Test MultiStreamRebroadcaster class functionality."""
    rebroadcaster = MultiStreamRebroadcaster()
    rebroadcaster.xdf_data = multi_stream_xdf_data

    assert rebroadcaster.get_stream_count() == 3

    # Test getting stream info
    stream_info = rebroadcaster.get_stream_info(0)
    assert stream_info.name == "TestStream-0"

    # Test rebroadcasting all streams
    outlets = rebroadcaster.start_rebroadcast()
    assert len(outlets) == 3
    assert rebroadcaster.is_streaming is True

    # Let it run briefly
    time.sleep(0.3)

    # Stop rebroadcasting
    rebroadcaster.stop_rebroadcast()
    assert rebroadcaster.is_streaming is False


def test_multi_stream_rebroadcaster_selected_streams(multi_stream_xdf_data):
    """Test MultiStreamRebroadcaster with selected streams."""
    rebroadcaster = MultiStreamRebroadcaster()
    rebroadcaster.xdf_data = multi_stream_xdf_data

    # Test rebroadcasting only selected streams
    selected_stream_ids = [0, 2]
    outlets = rebroadcaster.start_rebroadcast(stream_ids=selected_stream_ids)
    assert len(outlets) == len(selected_stream_ids)
    assert rebroadcaster.is_streaming is True

    # Let it run briefly
    time.sleep(0.3)

    # Stop rebroadcasting
    rebroadcaster.stop_rebroadcast()
    assert rebroadcaster.is_streaming is False


def test_multi_stream_rebroadcaster_context_manager(multi_stream_xdf_data):
    """Test MultiStreamRebroadcaster as context manager."""
    rebroadcaster = MultiStreamRebroadcaster()
    rebroadcaster.xdf_data = multi_stream_xdf_data

    with rebroadcaster:
        outlets = rebroadcaster.start_rebroadcast()
        assert len(outlets) == 3
        assert rebroadcaster.is_streaming is True
        time.sleep(0.2)

    # Should be stopped after context exit
    assert rebroadcaster.is_streaming is False
