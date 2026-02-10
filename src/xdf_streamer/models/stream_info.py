"""Stream information data model."""

from typing import Dict, List, Optional
from attrs import define, field

@define(slots=False)
class StreamInfo:
    """Information about a data stream."""

    name: str = field()
    type: str = field()
    channel_count: int = field()
    sampling_rate: float = field()
    channel_format: str = field()  # "float32", "double64", "int8", etc.
    channels: List[Dict[str, str]] = field()  # Channel metadata
    stream_id: int = field()
    source_id: Optional[str] = field(default=None)
    hostname: Optional[str] = field(default=None)
    session_id: Optional[str] = field(default=None)
    uid: Optional[str] = field(default=None)
    version: int = field(default=0)