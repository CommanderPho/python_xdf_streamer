# Installation Guide - liblsl and UV Compatibility

## The Challenge

`pylsl` (Python Lab Streaming Layer) requires the **liblsl binary library** to be available. This is a C/C++ shared library (`.so` on Linux, `.dylib` on macOS, `.dll` on Windows), not a Python package, so it cannot be installed via `uv` or `pip`.

## Mixing Conda/Mamba with UV: Is it Safe?

**Short answer**: It can work, but requires careful setup and isn't ideal.

### How it Works
- Conda installs liblsl into its environment's library path
- UV creates a separate virtual environment
- `pylsl` needs to find liblsl in the system library search path

### Potential Issues
1. **Path conflicts**: Conda and UV environments are separate
2. **Version conflicts**: Different library versions in different locations
3. **Maintenance complexity**: Two package managers to maintain
4. **Deployment issues**: Harder to reproduce environments

## Recommended Solutions (Best to Worst)

### Option 1: System Package Manager (Best for Linux)
Install liblsl system-wide using your distribution's package manager:

```bash
# Ubuntu/Debian
sudo apt-get install liblsl

# Fedora/RHEL
sudo dnf install liblsl

# Arch Linux
sudo pacman -S liblsl
```

**Pros**: 
- Clean separation from Python package management
- Available system-wide
- Easy to maintain

**Cons**: 
- Requires root/sudo access
- May not have latest version

### Option 2: Automatic Download Script (Best for Cross-Platform) ⭐ RECOMMENDED

Use the provided script to automatically download and setup liblsl:

```bash
# Run the setup script
uv run python scripts/download_liblsl.py --set-env

# Or specify custom directory
uv run python scripts/download_liblsl.py --dir ~/libs/liblsl --set-env
```

The script will:
- Detect your platform (Windows/Linux/macOS)
- Download the appropriate liblsl binary
- Install it to `~/.local/lib/liblsl` (or custom directory)
- Set `PYLSL_LIB` environment variable for the current session
- **Automatically create/update `.env` file** in repository root (recommended)

**Recommended: .env file** (automatically created)

The script automatically creates a `.env` file in the repository root with the correct `PYLSL_LIB` path. This file is automatically loaded when you run the application, so no additional configuration is needed! The `.env` file is git-ignored, so it won't be committed to the repository.

**Alternative: Shell Configuration**

If you prefer to set it system-wide, add to your shell configuration:

**Linux/macOS** (`~/.bashrc` or `~/.zshrc`):
```bash
export PYLSL_LIB="$HOME/.local/lib/liblsl/lib/liblsl.so"  # Linux
# or
export PYLSL_LIB="$HOME/.local/lib/liblsl/lib/liblsl.dylib"  # macOS
```

**Windows** (PowerShell profile or System Environment Variables):
```powershell
$env:PYLSL_LIB = "$HOME\.local\lib\liblsl\bin\lsl.dll"
# Or use setx for permanent:
setx PYLSL_LIB "$HOME\.local\lib\liblsl\bin\lsl.dll"
```

**Pros**:
- ✅ Fully automated cross-platform setup
- ✅ Works seamlessly with UV
- ✅ No mixing of package managers
- ✅ Easy to update (just re-run script)
- ✅ Library auto-detection built into the code
- ✅ Automatic `.env` file creation (no manual shell configuration needed)

**Cons**:
- Requires internet connection for first download

### Option 3: Conda Environment Variable (If Using Conda)
If you have conda installed, you can use it just for liblsl and point UV to it:

```bash
# Create a minimal conda environment just for liblsl
conda create -n liblsl-only liblsl -c conda-forge
conda activate liblsl-only

# Find where conda installed liblsl
conda env config vars list  # or check conda env path

# Set PYLSL_LIB to point to conda's liblsl
export PYLSL_LIB=$(conda info --base)/envs/liblsl-only/lib/liblsl.so

# Now use UV normally
cd python_xdf_streamer
uv sync
```

**Pros**:
- Easy to get liblsl
- Can keep UV for Python packages

**Cons**:
- Still mixing package managers
- Need to maintain conda environment
- More complex setup

### Option 4: Full Conda Environment (If You Prefer Conda)
Use conda for everything:

```bash
conda create -n xdf-streamer python=3.10
conda activate xdf-streamer
conda install -c conda-forge liblsl
pip install pylsl pyxdf numpy PyQt6  # or use conda for these too
```

**Pros**:
- Single package manager
- Conda handles binary dependencies well

**Cons**:
- Abandons UV (if you prefer UV)
- Larger environment

## Recommended Approach for This Project

**For development**: Use **Option 2** (manual download + PYLSL_LIB)
- Keeps UV as the primary package manager
- No mixing of package managers
- Easy to document and reproduce

**For production/deployment**: Use **Option 1** (system package manager) if on Linux
- Most reliable
- Standard approach

## Verification

After setting up liblsl, verify it works:

```bash
# Set PYLSL_LIB if using manual/conda approach
export PYLSL_LIB=/path/to/liblsl.so

# Test import
uv run python -c "import pylsl; print('✓ pylsl imported successfully')"
```

## Troubleshooting

### pylsl can't find liblsl
1. Check `PYLSL_LIB` is set correctly: `echo $PYLSL_LIB`
2. Verify file exists: `ls -la $PYLSL_LIB`
3. Check library dependencies: `ldd $PYLSL_LIB` (Linux)
4. Try setting in Python: `import os; os.environ['PYLSL_LIB'] = '/path/to/liblsl.so'`

### Library version mismatch
- Ensure liblsl version matches pylsl requirements
- Check pylsl documentation for compatible versions

### Path issues with conda
- Make sure conda environment is activated when finding liblsl path
- Use absolute paths in PYLSL_LIB
