# Quick Start Guide

## 1. Install Python Dependencies

```bash
uv sync --all-extras
```

## 2. Install liblsl (One-Time Setup)

Run the automatic setup script:

```bash
uv run python scripts/download_liblsl.py --set-env
```

This will:
- ✅ Detect your platform (Windows/Linux/macOS)
- ✅ Download the correct liblsl binary
- ✅ Install it to `~/.local/lib/liblsl`
- ✅ Create the `liblsl.so` symlink (Linux/macOS)
- ✅ Set `PYLSL_LIB` for the current session

**Note**: If you already ran the script before the symlink fix, run:
```bash
uv run python scripts/fix_liblsl_symlink.py
```

## 3. Make PYLSL_LIB Permanent

### Linux/macOS

Add to `~/.bashrc` or `~/.zshrc`:
```bash
export PYLSL_LIB="$HOME/.local/lib/liblsl/lib/liblsl.so"  # Linux
# or
export PYLSL_LIB="$HOME/.local/lib/liblsl/lib/liblsl.dylib"  # macOS
```

Then reload:
```bash
source ~/.bashrc  # or ~/.zshrc
```

### Windows

**PowerShell** (add to profile):
```powershell
$env:PYLSL_LIB = "$HOME\.local\lib\liblsl\bin\lsl.dll"
```

**Command Prompt** (permanent):
```cmd
setx PYLSL_LIB "%USERPROFILE%\.local\lib\liblsl\bin\lsl.dll"
```

## 4. Verify Installation

```bash
export PYLSL_LIB="$HOME/.local/lib/liblsl/lib/liblsl.so"  # Linux/macOS
# or
export PYLSL_LIB="$HOME\.local\lib\liblsl\bin\lsl.dll"  # Windows

uv run python -c "import pylsl; print('✓ pylsl imported successfully')"
```

## 5. Run the Application

```bash
uv run python src/main.py
```

## Troubleshooting

### pylsl can't find liblsl

1. Check `PYLSL_LIB` is set:
   ```bash
   echo $PYLSL_LIB  # Linux/macOS
   echo %PYLSL_LIB%  # Windows
   ```

2. Verify file exists:
   ```bash
   ls -la "$PYLSL_LIB"  # Linux/macOS
   dir "%PYLSL_LIB%"    # Windows
   ```

3. If symlink is missing (Linux/macOS):
   ```bash
   uv run python scripts/fix_liblsl_symlink.py
   ```

4. Re-run setup script:
   ```bash
   uv run python scripts/download_liblsl.py --set-env
   ```

### Platform-Specific Issues

**Linux**: May need to install system dependencies:
```bash
# For extracting archives
sudo apt-get install libbz2-dev dpkg-deb

# For liblsl runtime dependencies (required!)
sudo apt-get install libpugixml1

sudo apt-get install libpugixml1v5 libpugixml-dev

```

**Missing libpugixml error**: If you see `libpugixml.so.1: cannot open shared object file`, install it:
```bash
sudo apt-get install libpugixml1
```

**macOS**: May need to allow unsigned binaries:
```bash
xattr -d com.apple.quarantine ~/.local/lib/liblsl/lib/liblsl.dylib
```

**Windows**: Ensure you have admin rights for system-wide installation, or use user directory.
