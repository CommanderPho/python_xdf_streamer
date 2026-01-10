"""Thread worker for streaming data."""

import logging
import random
import threading
import time
from typing import Optional

import numpy as np

# Try to ensure liblsl is available before importing pylsl
try:
    from ..utils.liblsl_setup import setup_pylsl_import
    setup_pylsl_import()
except ImportError:
    pass  # liblsl_setup may not be available

import pylsl

from ..models.xdf_data import XdfData
from ..utils.timing import calculate_sleep_duration, get_precise_time

logger = logging.getLogger(__name__)


class StreamWorker:
    """Worker thread for streaming data to LSL."""

    def __init__(self, stop_event: threading.Event):
        """Initialize stream worker.

        Args:
            stop_event: Threading event to signal stop
        """
        self.stop_event = stop_event

    def stream_xdf_data(self, stream_id: int, outlet: pylsl.StreamOutlet, xdf_data: XdfData, on_complete: Optional[callable] = None) -> None:
        """Stream data from XDF file to LSL outlet.

        Args:
            stream_id: Stream identifier
            outlet: LSL stream outlet
            xdf_data: XDF data container
            on_complete: Optional callback when streaming completes
        """
        try:
            if stream_id not in xdf_data.time_series:
                raise ValueError(f"Stream {stream_id} not found in XDF data")

            stream_info = xdf_data.streams[stream_id]
            time_series = xdf_data.time_series[stream_id]

            # Ensure sampling_rate is a float (defensive check)
            sampling_rate = float(stream_info.sampling_rate) if not isinstance(stream_info.sampling_rate, (int, float)) else float(stream_info.sampling_rate)
            # Ensure channel_count is an int (defensive check)
            channel_count = int(float(stream_info.channel_count)) if isinstance(stream_info.channel_count, str) else int(stream_info.channel_count) if stream_info.channel_count is not None else 0
            sampling_interval = 1.0 / sampling_rate if sampling_rate > 0 else 0.0

            logger.info(f"Starting XDF stream {stream_id}: {stream_info.name} (rate: {sampling_rate} Hz, channels: {channel_count})")
            start_time = get_precise_time()

            # Ensure time_series is samples x channels
            if time_series.ndim == 1:
                time_series = time_series.reshape(-1, 1)
            elif time_series.shape[0] < time_series.shape[1] and time_series.shape[1] == channel_count:
                time_series = time_series.T

            num_samples = time_series.shape[0]

            for t in range(num_samples):
                if self.stop_event.is_set():
                    logger.info(f"Stream {stream_id} stopped by user")
                    break

                # Calculate target time
                target_time = start_time + t * sampling_interval
                sleep_duration = calculate_sleep_duration(target_time)

                if sleep_duration > 0:
                    time.sleep(sleep_duration)

                # Extract sample (row t)
                sample = time_series[t, :].tolist()

                # Ensure correct number of channels
                if len(sample) != channel_count:
                    sample = sample[:channel_count] if len(sample) > channel_count else sample + [0.0] * (channel_count - len(sample))

                try:
                    outlet.push_sample(sample)
                except Exception as e:
                    logger.error(f"Error pushing sample for stream {stream_id} at sample {t}: {e}", exc_info=True)
                    break

            logger.info(f"Stream {stream_id} completed ({num_samples} samples)")
            if on_complete:
                on_complete()
        except Exception as e:
            logger.error(f"Fatal error in stream_xdf_data for stream {stream_id}: {e}", exc_info=True)
            if on_complete:
                on_complete()

    def stream_synthetic_data(self, outlet: pylsl.StreamOutlet, sampling_rate: int, channel_count: int) -> None:
        """Stream synthetic random data to LSL outlet.

        Args:
            outlet: LSL stream outlet
            sampling_rate: Sampling rate in Hz
            channel_count: Number of channels
        """
        try:
            logger.info(f"Starting synthetic stream (rate: {sampling_rate} Hz, channels: {channel_count})")
            sampling_interval = 1.0 / sampling_rate
            start_time = get_precise_time()

            t = 0
            while not self.stop_event.is_set():
                target_time = start_time + t * sampling_interval
                sleep_duration = calculate_sleep_duration(target_time)

                if sleep_duration > 0:
                    time.sleep(sleep_duration)

                # Generate random sample
                sample = [(random.random() * 3.0 - 1.5) for _ in range(channel_count)]

                try:
                    outlet.push_sample(sample)
                except Exception as e:
                    logger.error(f"Error pushing synthetic sample at iteration {t}: {e}", exc_info=True)
                    break

                t += 1

            logger.info(f"Synthetic stream stopped after {t} samples")
        except Exception as e:
            logger.error(f"Fatal error in stream_synthetic_data: {e}", exc_info=True)
