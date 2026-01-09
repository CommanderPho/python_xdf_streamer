"""Stream information data model."""

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class StreamInfo:
    """Information about a data stream."""

    name: str
    type: str
    channel_count: int
    sampling_rate: float
    channel_format: str  # "float32", "double64", "int8", etc.
    channels: List[Dict[str, str]]  # Channel metadata
    stream_id: int
