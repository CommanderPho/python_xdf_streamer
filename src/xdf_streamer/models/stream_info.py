"""Stream information data model."""

import datetime
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


    n_samples: int = field(default=0)
    n_channels: int = field(default=0)
    effective_srate: float = field(default=-1)

    created_at: Optional[str] = field(default=None)
    first_timestamp: Optional[float] = field(default=None)
    last_timestamp: Optional[float] = field(default=None)
    sample_count: Optional[float] = field(default=None)
    created_at_dt: Optional[datetime.datetime] = field(default=None)
    first_timestamp_dt: Optional[datetime.datetime] = field(default=None)
    last_timestamp_dt: Optional[datetime.datetime] = field(default=None)
    stream_start_datetime: Optional[datetime.datetime] = field(default=None)
    stream_start_lsl_local_offset_seconds: Optional[float] = field(default=None)
    recording_start_datetime: Optional[datetime.datetime] = field(default=None)
    recording_start_lsl_local_offset_seconds: Optional[float] = field(default=None)
    nominal_srate: Optional[float] = field(default=None)
