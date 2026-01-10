"""Multi-stream XDF rebroadcasting functionality."""

import threading
from pathlib import Path
from typing import Callable, List, Optional

# Try to ensure liblsl is available before importing pylsl
try:
    from ..utils.liblsl_setup import setup_pylsl_import
    setup_pylsl_import()
except ImportError:
    pass  # liblsl_setup may not be available

import pylsl

from ..models.xdf_data import XdfData
from .lsl_streamer import LslStreamer
from .stream_worker import StreamWorker
from .xdf_loader import XdfLoader


class MultiStreamRebroadcaster:
    """Rebroadcast multiple streams from an XDF file via LSL outlets."""

    def __init__(self):
        """Initialize multi-stream rebroadcaster."""
        self.xdf_loader = XdfLoader()
        self.lsl_streamer = LslStreamer()
        self.xdf_data: Optional[XdfData] = None
        self.outlets: List[pylsl.StreamOutlet] = []
        self.stream_threads: List[threading.Thread] = []
        self.stop_event = threading.Event()
        self.is_streaming = False

    def load_xdf(self, file_path: Path | str) -> XdfData:
        """Load XDF file.

        Args:
            file_path: Path to XDF file

        Returns:
            XdfData object containing loaded streams

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is invalid
        """
        self.xdf_data = self.xdf_loader.load_xdf(file_path)
        return self.xdf_data

    def start_rebroadcast(
        self,
        stream_ids: Optional[List[int]] = None,
        on_stream_complete: Optional[Callable[[int], None]] = None,
        on_all_complete: Optional[Callable] = None,
    ) -> List[pylsl.StreamOutlet]:
        """Start rebroadcasting streams.

        Args:
            stream_ids: List of stream IDs to rebroadcast (None = all streams)
            on_stream_complete: Optional callback called when each stream completes (stream_id)
            on_all_complete: Optional callback called when all streams complete

        Returns:
            List of created LSL outlets

        Raises:
            ValueError: If no XDF data is loaded or stream_ids are invalid
        """
        if self.xdf_data is None or not self.xdf_data.loaded:
            raise ValueError("No XDF data loaded. Call load_xdf() first.")

        if self.is_streaming:
            raise ValueError("Already streaming. Call stop_rebroadcast() first.")

        if stream_ids is None:
            stream_ids = list(range(len(self.xdf_data.streams)))

        # Validate stream IDs
        for stream_id in stream_ids:
            if stream_id < 0 or stream_id >= len(self.xdf_data.streams):
                raise ValueError(f"Invalid stream_id: {stream_id}")

        self.stop_event.clear()
        self.is_streaming = True
        self.outlets.clear()
        self.stream_threads.clear()

        completion_count = {"count": 0, "lock": threading.Lock()}
        total_streams = len(stream_ids)

        def create_completion_callback(stream_id):
            def callback():
                if on_stream_complete:
                    on_stream_complete(stream_id)
                with completion_count["lock"]:
                    completion_count["count"] += 1
                    if completion_count["count"] == total_streams and on_all_complete:
                        on_all_complete()

            return callback

        # Create outlets and start streaming for selected streams
        for stream_id in stream_ids:
            stream_info = self.xdf_data.streams[stream_id]
            outlet = self.lsl_streamer.create_outlet(stream_info)
            self.outlets.append(outlet)

            worker = StreamWorker(self.stop_event)
            callback = create_completion_callback(stream_id)
            thread = threading.Thread(
                target=worker.stream_xdf_data,
                args=(stream_id, outlet, self.xdf_data, callback),
                daemon=True,
            )
            thread.start()
            self.stream_threads.append(thread)

        return self.outlets

    def stop_rebroadcast(self, timeout: float = 2.0) -> None:
        """Stop rebroadcasting all streams.

        Args:
            timeout: Maximum time to wait for threads to finish
        """
        if not self.is_streaming:
            return

        self.stop_event.set()

        # Wait for threads to finish
        for thread in self.stream_threads:
            thread.join(timeout=timeout)

        self.stream_threads.clear()
        self.outlets.clear()
        self.is_streaming = False

    def get_stream_count(self) -> int:
        """Get number of streams in loaded XDF file.

        Returns:
            Number of streams (0 if no file loaded)
        """
        if self.xdf_data is None or not self.xdf_data.loaded:
            return 0
        return len(self.xdf_data.streams)

    def get_stream_info(self, stream_id: int):
        """Get stream information for a specific stream.

        Args:
            stream_id: Stream identifier

        Returns:
            StreamInfo object

        Raises:
            ValueError: If no data loaded or invalid stream_id
        """
        if self.xdf_data is None or not self.xdf_data.loaded:
            raise ValueError("No XDF data loaded")
        if stream_id < 0 or stream_id >= len(self.xdf_data.streams):
            raise ValueError(f"Invalid stream_id: {stream_id}")
        return self.xdf_data.streams[stream_id]

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - stop streaming."""
        self.stop_rebroadcast()
