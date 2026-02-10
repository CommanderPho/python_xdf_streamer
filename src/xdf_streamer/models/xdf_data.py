"""XDF data container."""

from pathlib import Path
from typing import Dict, List

import numpy as np
from attrs import define, field, Factory

from .stream_info import StreamInfo


@define(slots=False)
class XdfData:
    """Container for loaded XDF file data."""
    streams: List[StreamInfo] = field(default=Factory(list))
    time_series: Dict[int, np.ndarray] = field(default=Factory(dict))  # stream_id -> data array
    file_path: Path = field(default=None)

    xdf_streams: List[Dict] = field(default=Factory(list))
    xdf_header: Dict = field(default=Factory(dict))

    loaded: bool = field(default=False)
