# Platform File Mapping

This document shows how the download script maps platforms to actual GitHub release files.

## Actual GitHub Release Files

From https://github.com/sccn/liblsl/releases/tag/v1.16.2:

### Linux (.deb files)
- `liblsl-1.16.2-bionic_amd64.deb` (Ubuntu 18.04)
- `liblsl-1.16.2-focal_amd64.deb` (Ubuntu 20.04)
- `liblsl-1.16.2-jammy_amd64.deb` (Ubuntu 22.04) ⭐ Default
- `liblsl-1.16.2-noble_amd64.deb` (Ubuntu 24.04)
- `liblsl-1.16.2-bookworm_arm64.deb` (Debian 12 ARM64)

### macOS (.tar.bz2 files)
- `liblsl-1.16.2-OSX_amd64.tar.bz2` (x86_64 and ARM64 via Rosetta)

### Windows (.zip files)
- `liblsl-1.16.2-Win_amd64.zip` (64-bit)
- `liblsl-1.16.2-Win_i386.zip` (32-bit)

## Script Mapping

The script automatically:
1. Detects platform (Linux/macOS/Windows)
2. Detects architecture (x86_64/aarch64/arm64/i386)
3. For Linux: Detects distribution and selects appropriate .deb file
4. Downloads and extracts the correct file
5. Finds and installs the library

## Distribution Detection

The script tries to detect Linux distribution by:
1. Using `distro` package if available
2. Reading `/etc/os-release`
3. Defaulting to `jammy` (Ubuntu 22.04) if detection fails
