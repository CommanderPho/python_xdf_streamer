# Python XDF Streamer

A Python application that streams signals from XDF files to Lab Streaming Layer (LSL), replicating the functionality of the C++ [XDF Streamer](https://github.com/CommanderPho/App-XDFStreamer).

## Features

- **XDF File Loading**: Load and parse XDF files containing neuroimaging/EEG data streams
- **LSL Streaming**: Stream data from XDF files to Lab Streaming Layer for real-time processing
- **Synthetic Signal Generation**: Generate random/synthetic signals for testing purposes
- **Multi-Stream Support**: Handle multiple streams simultaneously with independent threads
- **GUI Interface**: User-friendly graphical interface for configuration and control

## Requirements

- Python >= 3.10
- **liblsl**: Lab Streaming Layer binary library (required for pylsl)
  - **Recommended**: Use the automatic download script (see Quick Setup below)
  - **System dependencies** (Linux): `libpugixml1` (install via `sudo apt-get install libpugixml1`)
  - See [INSTALLATION.md](INSTALLATION.md) for detailed setup instructions

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd python_xdf_streamer
```

2. Install dependencies using uv:
```bash
uv sync --all-extras
```

3. Install liblsl (required for LSL functionality):

**Recommended: Automatic Setup** (works on Windows, Linux, macOS):
```bash
uv run python scripts/download_liblsl.py --set-env
```

This will automatically:
- Detect your platform
- Download the correct liblsl binary
- Install it to `~/.local/lib/liblsl`
- Set the `PYLSL_LIB` environment variable
- **Create/update `.env` file** in repository root (automatically loaded)

**Alternative: Manual Setup**
- Download from: https://github.com/sccn/liblsl/releases
- Extract and set `PYLSL_LIB` environment variable or add to `.env` file
- See [INSTALLATION.md](INSTALLATION.md) for detailed instructions

**Note**: The `.env` file is automatically created and loaded, so no manual shell configuration is needed. If you prefer system-wide setup, add to your shell config:
- Linux/macOS: `export PYLSL_LIB="$HOME/.local/lib/liblsl/lib/liblsl.so"`
- Windows: `setx PYLSL_LIB "$HOME\.local\lib\liblsl\bin\lsl.dll"`

## Usage

### GUI Mode

Run the graphical interface:
```bash
uv run python src/main.py
```

Or:
```bash
uv run python src/gui_main.py
```

### Features

1. **Load XDF File**: Click "..." to browse and select an XDF file, then click "Load"
2. **Select Streams**: Check the streams you want to stream in the tree widget
3. **Configure Sampling Rate**: Adjust the sampling rate if needed
4. **Stream**: Click "Stream" to start streaming to LSL
5. **Stop**: Click "Stop" to stop streaming

### Synthetic Signals

Check "Generate Random Signals" to stream synthetic test data:
- Configure channel count, stream name, type, and format
- Useful for testing without XDF files

## Project Structure

```
python_xdf_streamer/
├── src/
│   ├── xdf_streamer/
│   │   ├── core/          # Core functionality
│   │   │   ├── xdf_loader.py
│   │   │   ├── lsl_streamer.py
│   │   │   └── stream_worker.py
│   │   ├── gui/           # GUI components
│   │   │   └── main_window.py
│   │   ├── models/         # Data models
│   │   │   ├── stream_info.py
│   │   │   └── xdf_data.py
│   │   └── utils/          # Utilities
│   │       ├── format_converter.py
│   │       ├── timing.py
│   │       └── validators.py
│   ├── main.py
│   └── gui_main.py
├── tests/                  # Unit tests
├── examples/               # Example scripts
└── docs/                   # Documentation
```

## Testing

Run tests (note: some tests require liblsl to be installed):
```bash
uv run pytest tests/ -v
```

Run tests that don't require LSL:
```bash
uv run pytest tests/test_timing.py tests/test_validators.py -v
```

## Development

Install development dependencies:
```bash
uv sync --all-extras
```

This includes:
- pytest and pytest-qt for testing
- black for code formatting
- mypy for type checking
- ruff for linting

## Quick Setup

```bash
# 1. Install Python dependencies
uv sync --all-extras

# 2. Install liblsl (automatic, cross-platform)
uv run python scripts/download_liblsl.py --set-env
# This automatically creates a .env file - no additional configuration needed!

# 3. Run the application
uv run python src/main.py
```

See [QUICKSTART.md](QUICKSTART.md) for detailed setup instructions.

## License

[Add your license here]

## Acknowledgments

Based on the C++ XDF Streamer application: https://github.com/CommanderPho/App-XDFStreamer
