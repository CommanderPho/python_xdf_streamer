# Python XDF Streamer - Implementation Plan

## Overview
This document outlines a robust Python implementation plan for replicating the functionality of the C++ XDF Streamer application (https://github.com/CommanderPho/App-XDFStreamer), which streams signals from XDF files to Lab Streaming Layer (LSL).

## Core Functionality Analysis

### Primary Features
1. **XDF File Loading**: Load and parse XDF files containing neuroimaging/EEG data streams
2. **LSL Streaming**: Stream data from XDF files to Lab Streaming Layer for real-time processing
3. **Synthetic Signal Generation**: Generate random/synthetic signals for testing purposes
4. **Multi-Stream Support**: Handle multiple streams simultaneously with independent threads
5. **GUI Interface**: User-friendly graphical interface for configuration and control

### Key Technical Requirements
- XDF file parsing (Extensible Data Format)
- Lab Streaming Layer (LSL) integration
- Multi-threaded streaming with proper synchronization
- Precise timing control for sample rate maintenance
- Channel format conversion (float32, double64, int8, int16, int32, int64, string)
- Stream metadata handling (channel names, types, etc.)

## Architecture Design

### 1. Project Structure
```
python_xdf_streamer/
├── src/
│   ├── xdf_streamer/
│   │   ├── __init__.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── xdf_loader.py          # XDF file loading and parsing
│   │   │   ├── lsl_streamer.py        # LSL stream creation and management
│   │   │   └── stream_worker.py       # Thread worker for streaming data
│   │   ├── gui/
│   │   │   ├── __init__.py
│   │   │   ├── main_window.py         # Main GUI window
│   │   │   ├── widgets/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── stream_tree.py     # Tree widget for stream display
│   │   │   │   └── config_panel.py    # Configuration panel widgets
│   │   │   └── dialogs.py             # Message dialogs
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   ├── timing.py              # Timing utilities for sample rate
│   │   │   ├── format_converter.py    # Channel format conversion
│   │   │   └── validators.py          # Input validation
│   │   └── models/
│   │       ├── __init__.py
│   │       ├── stream_info.py         # Stream information data models
│   │       └── xdf_data.py            # XDF data structures
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_xdf_loader.py
│   │   ├── test_lsl_streamer.py
│   │   ├── test_stream_worker.py
│   │   └── fixtures/
│   │       └── sample.xdf
│   ├── main.py                         # Application entry point
│   └── gui_main.py                     # GUI application entry point
├── docs/
│   ├── API.md
│   └── USER_GUIDE.md
├── examples/
│   ├── basic_streaming.py
│   └── synthetic_signals.py
├── pyproject.toml
├── README.md
└── IMPLEMENTATION_PLAN.md
```

### 2. Core Components

#### 2.1 XDF Loader (`xdf_loader.py`)
**Responsibilities:**
- Load XDF files using Python XDF library (pyxdf or similar)
- Parse stream metadata (name, type, channel count, sampling rate, format)
- Extract time series data
- Handle channel information
- Validate file format and stream integrity
- Error handling for corrupted or invalid files

**Key Methods:**
- `load_xdf(file_path: Path) -> XdfData`
- `get_streams() -> List[StreamInfo]`
- `get_time_series(stream_id: int) -> np.ndarray`
- `validate_stream(stream_id: int) -> bool`

**Dependencies:**
- `pyxdf` or `pylsl` with XDF support
- `numpy` for data arrays
- `pathlib` for file handling

#### 2.2 LSL Streamer (`lsl_streamer.py`)
**Responsibilities:**
- Create LSL stream outlets
- Configure stream metadata (name, type, channel count, sampling rate, format)
- Map XDF channel formats to LSL channel formats
- Handle channel descriptions and metadata
- Manage stream lifecycle

**Key Methods:**
- `create_outlet(stream_info: StreamInfo) -> StreamOutlet`
- `map_channel_format(xdf_format: str) -> lsl.channel_format_t`
- `configure_stream_metadata(stream_info: StreamInfo) -> lsl.StreamInfo`

**Dependencies:**
- `pylsl` (Python Lab Streaming Layer library)

#### 2.3 Stream Worker (`stream_worker.py`)
**Responsibilities:**
- Thread-based streaming execution
- Maintain precise timing for sample rate
- Push samples to LSL outlet at correct intervals
- Handle stop signals gracefully
- Support both XDF data and synthetic data streaming

**Key Methods:**
- `stream_xdf_data(stream_id: int, outlet: StreamOutlet, xdf_data: XdfData) -> None`
- `stream_synthetic_data(outlet: StreamOutlet, sampling_rate: int, channel_count: int) -> None`
- `stop_streaming() -> None`

**Dependencies:**
- `threading` for thread management
- `time` for timing control
- `numpy` for data generation

#### 2.4 GUI Main Window (`main_window.py`)
**Responsibilities:**
- Main application window
- UI component layout and management
- Event handling (button clicks, file selection, etc.)
- State management (loaded/streaming/stopped)
- Integration of all components

**Key Components:**
- File browser button and path input
- Load/Unload button
- Stream selection tree widget
- Sampling rate spinbox
- Random signal checkbox and configuration panel
- Stream/Stop button
- Status messages

**Dependencies:**
- `PyQt5` or `PyQt6` or `PySide6` for GUI
- `QTreeWidget`, `QPushButton`, `QLineEdit`, `QSpinBox`, `QCheckBox`, etc.

### 3. Data Models

#### 3.1 StreamInfo (`models/stream_info.py`)
```python
@dataclass
class StreamInfo:
    name: str
    type: str
    channel_count: int
    sampling_rate: float
    channel_format: str  # "float32", "double64", "int8", etc.
    channels: List[Dict[str, str]]  # Channel metadata
    stream_id: int
```

#### 3.2 XdfData (`models/xdf_data.py`)
```python
@dataclass
class XdfData:
    streams: List[StreamInfo]
    time_series: Dict[int, np.ndarray]  # stream_id -> data array
    file_path: Path
    loaded: bool = False
```

## Implementation Phases

### Phase 1: Core Infrastructure (Week 1)
**Goals:** Set up project structure and basic functionality

1. **Project Setup**
   - Configure `pyproject.toml` with dependencies
   - Set up development environment
   - Create package structure

2. **Dependencies Installation**
   - `pylsl` - Lab Streaming Layer Python bindings
   - `pyxdf` or `pylsl` with XDF support - XDF file reading
   - `numpy` - Numerical operations
   - `PyQt6` or `PySide6` - GUI framework
   - `pytest` - Testing framework

3. **Basic XDF Loading**
   - Implement XDF file loader
   - Parse stream metadata
   - Extract time series data
   - Unit tests for XDF loading

### Phase 2: LSL Integration (Week 1-2)
**Goals:** Implement LSL streaming functionality

1. **LSL Stream Creation**
   - Create stream outlets
   - Configure stream metadata
   - Map channel formats
   - Handle channel descriptions

2. **Streaming Logic**
   - Implement timing control
   - Sample pushing mechanism
   - Error handling

3. **Testing**
   - Test LSL stream creation
   - Test sample pushing
   - Verify timing accuracy

### Phase 3: Multi-Threading (Week 2)
**Goals:** Implement concurrent streaming

1. **Thread Management**
   - Create thread worker class
   - Implement thread pool for multiple streams
   - Thread-safe stop mechanism
   - Proper cleanup on thread termination

2. **Synchronization**
   - Mutex/lock for shared state
   - Thread-safe flag checking
   - Graceful shutdown

3. **Testing**
   - Test multi-stream scenarios
   - Test thread cleanup
   - Stress testing

### Phase 4: GUI Implementation (Week 2-3)
**Goals:** Build user interface

1. **Main Window**
   - Layout design
   - Widget creation and configuration
   - Event handlers

2. **Stream Tree Widget**
   - Display stream information
   - Checkbox selection
   - Expandable tree structure

3. **Configuration Panel**
   - File path input
   - Sampling rate control
   - Random signal options
   - Channel format selection

4. **User Interactions**
   - File browser dialog
   - Load/unload functionality
   - Stream start/stop
   - Status messages

### Phase 5: Synthetic Signal Generation (Week 3)
**Goals:** Implement random signal generation

1. **Signal Generator**
   - Random data generation
   - Configurable parameters (rate, channels, format)
   - Continuous streaming

2. **GUI Integration**
   - Show/hide configuration panel
   - Update UI state
   - Display synthetic stream info

### Phase 6: Polish & Testing (Week 3-4)
**Goals:** Refinement and comprehensive testing

1. **Error Handling**
   - File loading errors
   - Invalid stream handling
   - Irregular sampling rate detection
   - Network/LSL connection errors

2. **Validation**
   - Input validation
   - Stream validation
   - Rate validation

3. **Documentation**
   - API documentation
   - User guide
   - Code comments

4. **Testing**
   - Unit tests for all components
   - Integration tests
   - GUI testing
   - End-to-end testing with real XDF files

## Technical Specifications

### Dependencies

#### Required Libraries
```toml
[project]
dependencies = [
    "pylsl>=1.16.0",           # Lab Streaming Layer
    "pyxdf>=1.16.0",            # XDF file reading (or use pylsl's XDF support)
    "numpy>=1.24.0",            # Numerical operations
    "PyQt6>=6.5.0",             # GUI framework (or PySide6)
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-qt>=4.2.0",         # Qt testing
    "black>=23.0.0",
    "mypy>=1.5.0",
    "ruff>=0.1.0",
]
```

### Key Algorithms

#### 1. Timing Control for Streaming
```python
def stream_with_timing(outlet, samples, sampling_rate):
    sampling_interval = 1.0 / sampling_rate
    start_time = time.perf_counter()
    
    for t, sample in enumerate(samples):
        # Check stop flag
        if stop_flag.is_set():
            break
        
        # Calculate target time
        target_time = start_time + t * sampling_interval
        current_time = time.perf_counter()
        sleep_duration = target_time - current_time
        
        if sleep_duration > 0:
            time.sleep(sleep_duration)
        
        # Push sample
        outlet.push_sample(sample)
```

#### 2. Channel Format Mapping
```python
CHANNEL_FORMAT_MAP = {
    "float32": lsl.cf_float32,
    "double64": lsl.cf_double64,
    "int8": lsl.cf_int8,
    "int16": lsl.cf_int16,
    "int32": lsl.cf_int32,
    "int64": lsl.cf_int64,
    "string": lsl.cf_string,
}
```

#### 3. Multi-Stream Thread Management
```python
class StreamManager:
    def __init__(self):
        self.threads: List[Thread] = []
        self.stop_event = threading.Event()
    
    def start_streams(self, streams: List[StreamConfig]):
        self.stop_event.clear()
        for stream in streams:
            thread = threading.Thread(
                target=self._stream_worker,
                args=(stream,)
            )
            thread.start()
            self.threads.append(thread)
    
    def stop_streams(self):
        self.stop_event.set()
        for thread in self.threads:
            thread.join()
        self.threads.clear()
```

## Error Handling Strategy

### File Loading Errors
- Invalid file path → Show error dialog
- Corrupted XDF file → Show error with details
- Unsupported format → Show format error

### Streaming Errors
- LSL connection failure → Show connection error
- Invalid stream configuration → Validate before starting
- Thread creation failure → Show system error

### Runtime Errors
- Sample rate violations → Warn user
- Irregular sampling rates → Reject stream with message
- Thread crashes → Log error and stop gracefully

## Testing Strategy

### Unit Tests
- XDF file loading with various formats
- Stream metadata parsing
- Channel format conversion
- Timing calculations
- Thread management

### Integration Tests
- End-to-end streaming from XDF to LSL
- Multi-stream scenarios
- Start/stop cycles
- Error recovery

### GUI Tests
- Widget interactions
- File dialogs
- Button states
- Tree widget operations

### Performance Tests
- Large XDF files
- High sampling rates
- Many concurrent streams
- Memory usage

## GUI Design Considerations

### Layout
- **Top Section**: Configuration panel with file path, sampling rate, random signal checkbox
- **Middle Section**: Stream tree widget (XDF streams or synthetic stream info)
- **Bottom Section**: Stream/Stop button

### User Experience
- Clear visual feedback for all actions
- Disable controls during streaming
- Show stream status
- Informative error messages
- Intuitive file selection

### Accessibility
- Keyboard shortcuts
- Tooltips for all controls
- Clear labels
- Error messages in plain language

## Performance Considerations

### Memory Management
- Stream data lazily when possible
- Clear data after streaming completes
- Use generators for large datasets

### Timing Precision
- Use `time.perf_counter()` for high-resolution timing
- Minimize overhead in streaming loop
- Consider using `time.sleep()` with small intervals

### Thread Efficiency
- Minimize lock contention
- Use thread-safe data structures
- Efficient stop flag checking

## Future Enhancements (Post-MVP)

1. **Advanced Features**
   - Stream filtering/selection
   - Playback speed control
   - Loop playback option
   - Stream recording

2. **Visualization**
   - Real-time signal visualization
   - Stream statistics display
   - Timing accuracy metrics

3. **CLI Mode**
   - Command-line interface
   - Scriptable streaming
   - Configuration file support

4. **Performance Improvements**
   - Cython optimizations
   - Parallel data processing
   - Memory-mapped file access

## Risk Mitigation

### Technical Risks
- **XDF library compatibility**: Test with various XDF file versions
- **LSL version compatibility**: Pin LSL version, test compatibility
- **GUI framework choice**: Choose stable, well-maintained framework
- **Threading issues**: Extensive testing, use proven patterns

### Project Risks
- **Scope creep**: Stick to MVP features first
- **Timeline**: Buffer time for unexpected issues
- **Dependencies**: Pin versions, have fallback options

## Success Criteria

1. ✅ Load XDF files successfully
2. ✅ Display stream information correctly
3. ✅ Stream data to LSL with accurate timing
4. ✅ Support multiple concurrent streams
5. ✅ Generate synthetic signals
6. ✅ Provide intuitive GUI
7. ✅ Handle errors gracefully
8. ✅ Comprehensive test coverage (>80%)
9. ✅ Documentation complete

## Next Steps

1. Review and approve this plan
2. Set up development environment
3. Initialize project structure
4. Begin Phase 1 implementation
5. Regular progress reviews
