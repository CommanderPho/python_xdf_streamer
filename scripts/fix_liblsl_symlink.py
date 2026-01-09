#!/usr/bin/env python3
"""Fix missing liblsl.so symlink in existing installation."""

import sys
from pathlib import Path

lib_dir = Path.home() / ".local" / "lib" / "liblsl" / "lib"

if not lib_dir.exists():
    print(f"Error: {lib_dir} does not exist")
    sys.exit(1)

# Find versioned library
versioned_libs = list(lib_dir.glob("liblsl.so.*"))
if not versioned_libs:
    print(f"Error: No versioned liblsl library found in {lib_dir}")
    sys.exit(1)

# Get the most recent version
versioned_lib = sorted(versioned_libs, key=lambda p: p.stat().st_mtime, reverse=True)[0]
symlink_path = lib_dir / "liblsl.so"

# Remove existing symlink/file if it exists
if symlink_path.exists() or symlink_path.is_symlink():
    symlink_path.unlink()

# Create symlink
symlink_path.symlink_to(versioned_lib.name)
print(f"✓ Created symlink: {symlink_path} -> {versioned_lib.name}")
print(f"\nUpdate PYLSL_LIB:")
print(f'  export PYLSL_LIB="{symlink_path}"')
