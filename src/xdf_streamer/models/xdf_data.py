"""XDF data container."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

import numpy as np

from .stream_info import StreamInfo


@dataclass
class XdfData:
    """Container for loaded XDF file data."""

    streams: List[StreamInfo] = field(default_factory=list)
    time_series: Dict[int, np.ndarray] = field(default_factory=dict)  # stream_id -> data array
    file_path: Path = None
    loaded: bool = False
