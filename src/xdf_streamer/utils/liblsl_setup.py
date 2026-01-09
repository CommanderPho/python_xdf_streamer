"""Automatic liblsl library detection and setup."""

import os
import platform
from pathlib import Path
from typing import Optional


def find_liblsl() -> Optional[Path]:
    """Find liblsl library file.
    
    Checks in order:
    1. PYLSL_LIB environment variable
    2. Common installation locations
    3. System library paths
    
    Returns:
        Path to liblsl library if found, None otherwise
    """
    system = platform.system()
    
    # Library names by platform
    lib_names = {
        "Linux": "liblsl.so",
        "Darwin": "liblsl.dylib",
        "Windows": "lsl.dll",
    }
    lib_name = lib_names.get(system)
    if not lib_name:
        return None
    
    # Check PYLSL_LIB environment variable first
    pylsl_lib = os.environ.get("PYLSL_LIB")
    if pylsl_lib:
        lib_path = Path(pylsl_lib)
        if lib_path.exists():
            return lib_path
    
    # Common installation locations
    search_paths = []
    
    if system == "Windows":
        # Windows common paths
        search_paths.extend([
            Path.home() / ".local" / "lib" / "liblsl" / "bin" / lib_name,
            Path.home() / "libs" / "liblsl" / "bin" / lib_name,
            Path("C:\\libs\\liblsl\\bin") / lib_name,
        ])
    else:
        # Unix-like common paths
        search_paths.extend([
            Path.home() / ".local" / "lib" / "liblsl" / "lib" / lib_name,
            Path.home() / "libs" / "liblsl" / "lib" / lib_name,
            Path("/usr/local/lib") / lib_name,
            Path("/usr/lib") / lib_name,
        ])
    
    # Check search paths
    for path in search_paths:
        if path.exists():
            return path
    
    # Try to find in system library paths (Unix-like)
    if system != "Windows":
        import ctypes.util
        lib_path_str = ctypes.util.find_library("lsl")
        if lib_path_str:
            return Path(lib_path_str)
    
    return None


def ensure_liblsl_available() -> Path:
    """Ensure liblsl is available, raise error if not found.
    
    Returns:
        Path to liblsl library
        
    Raises:
        RuntimeError: If liblsl is not found
    """
    lib_path = find_liblsl()
    
    if lib_path is None:
        system = platform.system()
        lib_name = {
            "Linux": "liblsl.so",
            "Darwin": "liblsl.dylib",
            "Windows": "lsl.dll",
        }.get(system, "liblsl")
        
        raise RuntimeError(
            f"liblsl library ({lib_name}) not found.\n\n"
            "Please install liblsl using one of these methods:\n"
            "1. Run: python scripts/download_liblsl.py --set-env\n"
            "2. Download from: https://github.com/sccn/liblsl/releases\n"
            "   Then set PYLSL_LIB environment variable\n"
            "3. Install system package (Linux): sudo apt-get install liblsl\n"
            f"\nCurrent PYLSL_LIB: {os.environ.get('PYLSL_LIB', 'not set')}"
        )
    
    # Set PYLSL_LIB if not already set
    if "PYLSL_LIB" not in os.environ:
        os.environ["PYLSL_LIB"] = str(lib_path.absolute())
    
    return lib_path


def setup_pylsl_import():
    """Setup pylsl import by ensuring liblsl is available."""
    try:
        ensure_liblsl_available()
    except RuntimeError as e:
        # Don't fail here, let pylsl handle the error with better message
        pass
