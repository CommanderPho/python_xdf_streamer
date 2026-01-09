# Setup Scripts

## download_liblsl.py

Automatically downloads and sets up liblsl for your platform (Windows, Linux, macOS).

### Usage

```bash
# Basic usage - downloads to ~/.local/lib/liblsl
uv run python scripts/download_liblsl.py

# With automatic environment variable setup
uv run python scripts/download_liblsl.py --set-env

# Custom installation directory
uv run python scripts/download_liblsl.py --dir ~/libs/liblsl --set-env
```

### What it does

1. Detects your platform (Windows/Linux/macOS) and architecture
2. Downloads the appropriate liblsl binary from GitHub releases
3. Extracts and installs it to the specified directory
4. Optionally sets the `PYLSL_LIB` environment variable

### Platform Support

- ✅ Linux (x86_64, aarch64)
- ✅ macOS (x86_64, arm64)
- ✅ Windows (x86_64)

### Output Location

Default: `~/.local/lib/liblsl/`
- Linux/macOS: `lib/liblsl.so` or `lib/liblsl.dylib`
- Windows: `bin/lsl.dll`
