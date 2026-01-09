#!/usr/bin/env python3
"""Download and setup liblsl for the current platform."""

import os
import platform
import shutil
import sys
import tarfile
import zipfile
from pathlib import Path
from urllib.request import urlretrieve

# liblsl release information
LIBLSL_RELEASE_URL = "https://github.com/sccn/liblsl/releases/download/v1.16.2"
LIBLSL_VERSION = "1.16.2"

# Linux distribution detection for .deb files
LINUX_DISTROS = {
    "jammy": "jammy_amd64",  # Ubuntu 22.04
    "focal": "focal_amd64",  # Ubuntu 20.04
    "bionic": "bionic_amd64",  # Ubuntu 18.04
    "noble": "noble_amd64",  # Ubuntu 24.04
    "bookworm": "bookworm_arm64",  # Debian 12 ARM64
}

# Platform-specific file names (matching actual GitHub release files)
# Note: Linux uses .deb files, macOS/Windows use archives
PLATFORM_FILES = {
    "Linux": {
        "x86_64": "jammy",  # Will be converted to liblsl-1.16.2-jammy_amd64.deb
        "aarch64": "bookworm",  # Will be converted to liblsl-1.16.2-bookworm_arm64.deb
    },
    "Darwin": {
        "x86_64": f"liblsl-{LIBLSL_VERSION}-OSX_amd64.tar.bz2",
        "arm64": f"liblsl-{LIBLSL_VERSION}-OSX_amd64.tar.bz2",  # Use x86_64 version (Rosetta compatible)
    },
    "Windows": {
        "x86_64": f"liblsl-{LIBLSL_VERSION}-Win_amd64.zip",
        "i386": f"liblsl-{LIBLSL_VERSION}-Win_i386.zip",
    },
}

# Library file names by platform
LIBRARY_NAMES = {
    "Linux": "liblsl.so",
    "Darwin": "liblsl.dylib",
    "Windows": "lsl.dll",
}


def get_platform_info():
    """Get platform information."""
    system = platform.system()
    machine = platform.machine().lower()
    
    # Normalize machine names
    if machine in ["x86_64", "amd64"]:
        arch = "x86_64"
    elif machine in ["aarch64", "arm64"]:
        arch = "arm64" if system == "Darwin" else "aarch64"
    elif machine in ["i386", "i686"]:
        arch = "i386"
    else:
        arch = machine
    
    return system, arch


def detect_linux_distro():
    """Detect Linux distribution for .deb file selection."""
    try:
        import distro
        distro_id = distro.id()
        distro_version = distro.version()
        
        # Map to known distributions
        if distro_id == "ubuntu":
            if distro_version.startswith("22"):
                return "jammy"
            elif distro_version.startswith("20"):
                return "focal"
            elif distro_version.startswith("18"):
                return "bionic"
            elif distro_version.startswith("24"):
                return "noble"
        elif distro_id == "debian":
            if "12" in distro_version or "bookworm" in distro_version.lower():
                return "bookworm"
    except ImportError:
        # Try /etc/os-release
        try:
            with open("/etc/os-release", "r") as f:
                content = f.read().lower()
                if "ubuntu" in content:
                    if "22.04" in content or "jammy" in content:
                        return "jammy"
                    elif "20.04" in content or "focal" in content:
                        return "focal"
                    elif "18.04" in content or "bionic" in content:
                        return "bionic"
                    elif "24.04" in content or "noble" in content:
                        return "noble"
                elif "debian" in content and "12" in content:
                    return "bookworm"
        except Exception:
            pass
    
    # Default to jammy (most common)
    return "jammy"


def get_library_path(base_dir: Path) -> Path:
    """Get the path to the liblsl library file."""
    system = platform.system()
    lib_name = LIBRARY_NAMES[system]
    
    if system == "Windows":
        return base_dir / "bin" / lib_name
    else:
        return base_dir / "lib" / lib_name


def download_file(url: str, dest: Path) -> Path:
    """Download a file from URL to destination."""
    print(f"Downloading {url}...")
    print(f"Destination: {dest}")
    
    def show_progress(block_num, block_size, total_size):
        if total_size > 0:
            percent = min(100, (block_num * block_size * 100) // total_size)
            print(f"\rProgress: {percent}%", end="", flush=True)
    
    try:
        urlretrieve(url, dest, show_progress)
        print()  # New line after progress
        return dest
    except Exception as e:
        print(f"\nError downloading file: {e}")
        raise


def extract_deb(deb_path: Path, extract_to: Path):
    """Extract .deb file (which is actually an ar archive)."""
    import subprocess
    
    print(f"Extracting {deb_path.name}...")
    extract_to.mkdir(parents=True, exist_ok=True)
    
    # .deb files are ar archives containing data.tar.xz or data.tar.gz
    # Use dpkg-deb if available, otherwise extract manually
    try:
        # Try using dpkg-deb (most reliable)
        result = subprocess.run(
            ["dpkg-deb", "-x", str(deb_path), str(extract_to)],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print("Extraction complete (using dpkg-deb).")
            return
    except FileNotFoundError:
        pass
    
    # Manual extraction: .deb is an ar archive
    try:
        import arfile  # May not be available
        with open(deb_path, "rb") as f:
            ar = arfile.ArFile(f)
            for member in ar.getmembers():
                if member.name.startswith("data.tar"):
                    data_tar = ar.extractfile(member)
                    if member.name.endswith(".xz"):
                        import lzma
                        data_tar = lzma.decompress(data_tar.read())
                    elif member.name.endswith(".gz"):
                        import gzip
                        data_tar = gzip.decompress(data_tar.read())
                    else:
                        data_tar = data_tar.read()
                    
                    # Extract the tar
                    import io
                    tar_ref = tarfile.open(fileobj=io.BytesIO(data_tar))
                    tar_ref.extractall(extract_to)
                    print("Extraction complete (manual).")
                    return
    except ImportError:
        pass
    
    # Fallback: try using ar command
    try:
        temp_ar = extract_to / "temp_ar"
        subprocess.run(["ar", "x", str(deb_path)], cwd=extract_to, check=True)
        # Find data.tar.*
        for data_tar in extract_to.glob("data.tar.*"):
            if data_tar.suffix == ".xz":
                subprocess.run(["tar", "xf", str(data_tar)], cwd=extract_to, check=True)
            elif data_tar.suffix == ".gz":
                subprocess.run(["tar", "xzf", str(data_tar)], cwd=extract_to, check=True)
            else:
                subprocess.run(["tar", "xf", str(data_tar)], cwd=extract_to, check=True)
            data_tar.unlink()  # Clean up
        print("Extraction complete (using ar command).")
        return
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass
    
    raise RuntimeError(
        "Could not extract .deb file. Please install 'dpkg-deb' or 'ar' command, "
        "or install liblsl using your system package manager: sudo apt-get install liblsl"
    )


def extract_archive(archive_path: Path, extract_to: Path):
    """Extract archive to destination."""
    print(f"Extracting {archive_path.name} to {extract_to}...")
    extract_to.mkdir(parents=True, exist_ok=True)
    
    if archive_path.suffix == ".deb":
        extract_deb(archive_path, extract_to)
    elif archive_path.suffix == ".zip":
        with zipfile.ZipFile(archive_path, "r") as zip_ref:
            zip_ref.extractall(extract_to)
    elif archive_path.suffixes == [".tar", ".bz2"] or archive_path.suffix == ".tar.bz2":
        with tarfile.open(archive_path, "r:bz2") as tar_ref:
            tar_ref.extractall(extract_to)
    else:
        raise ValueError(f"Unsupported archive format: {archive_path.suffix}")
    
    print("Extraction complete.")


def find_library_in_extracted(extract_dir: Path) -> tuple[Path, Path]:
    """Find the library file in extracted directory.
    
    Returns:
        Tuple of (symlink_path, actual_library_path)
        If no symlink exists, both will be the same path
    """
    system = platform.system()
    lib_name = LIBRARY_NAMES[system]
    
    symlink_path = None
    actual_lib_path = None
    
    # For Linux .deb files, check usr/lib first
    if system == "Linux":
        usr_lib = extract_dir / "usr" / "lib"
        if usr_lib.exists():
            # First, look for the symlink liblsl.so
            symlink_candidate = usr_lib / lib_name
            if symlink_candidate.exists():
                symlink_path = symlink_candidate
                # Resolve symlink to get actual file
                if symlink_candidate.is_symlink():
                    actual_lib_path = symlink_candidate.resolve()
                else:
                    actual_lib_path = symlink_candidate
            else:
                # Look for versioned library files
                for lib_file in sorted(usr_lib.rglob("liblsl.so*"), reverse=True):
                    if lib_file.is_file() and not lib_file.is_symlink():
                        actual_lib_path = lib_file
                        # Create symlink path pointing to this file
                        symlink_path = usr_lib / lib_name
                        break
    
    # If not found in usr/lib, search elsewhere
    if actual_lib_path is None:
        # Search for library file
        if system == "Windows":
            search_paths = [extract_dir / "bin" / lib_name, extract_dir / lib_name]
        else:
            search_paths = [extract_dir / "lib" / lib_name, extract_dir / lib_name]
        
        # Also search recursively
        for root, dirs, files in os.walk(extract_dir):
            if lib_name in files:
                found_path = Path(root) / lib_name
                if found_path.exists():
                    actual_lib_path = found_path.resolve() if found_path.is_symlink() else found_path
                    symlink_path = found_path
                    break
        
        # Check direct paths
        if actual_lib_path is None:
            for path in search_paths:
                if path.exists():
                    actual_lib_path = path.resolve() if path.is_symlink() else path
                    symlink_path = path
                    break
    
    if actual_lib_path is None:
        raise FileNotFoundError(f"Could not find {lib_name} in extracted archive")
    
    # If no symlink found, use actual lib path for both
    if symlink_path is None:
        symlink_path = actual_lib_path
    
    return symlink_path, actual_lib_path


def setup_liblsl(libs_dir: Path = None) -> Path:
    """Download and setup liblsl for current platform.
    
    Args:
        libs_dir: Directory to install liblsl (defaults to ~/.local/lib/liblsl)
    
    Returns:
        Path to the liblsl library file
    """
    if libs_dir is None:
        libs_dir = Path.home() / ".local" / "lib" / "liblsl"
    
    system, arch = get_platform_info()
    
    print(f"Platform: {system} ({arch})")
    print(f"Installation directory: {libs_dir}")
    
    # Check if already installed (check for symlink first, then versioned file)
    lib_path = get_library_path(libs_dir)
    if lib_path.exists():
        print(f"✓ liblsl already installed at: {lib_path}")
        return lib_path
    # Also check if versioned library exists but symlink is missing
    if system != "Windows":
        lib_dir = libs_dir / "lib"
        if lib_dir.exists():
            versioned_libs = list(lib_dir.glob("liblsl.so.*"))
            if versioned_libs:
                # Create missing symlink
                versioned_lib = sorted(versioned_libs, key=lambda p: p.stat().st_mtime, reverse=True)[0]
                symlink_path = lib_dir / "liblsl.so"
                if not symlink_path.exists():
                    symlink_path.symlink_to(versioned_lib.name)
                    print(f"✓ Created missing symlink: {symlink_path} -> {versioned_lib.name}")
                return symlink_path
    
    # Get download URL
    if system not in PLATFORM_FILES:
        raise ValueError(f"Unsupported platform: {system}")
    
    # Handle Linux .deb file selection
    if system == "Linux":
        if arch == "aarch64":
            # Use bookworm for ARM64
            distro_key = PLATFORM_FILES[system]["aarch64"]
            deb_suffix = LINUX_DISTROS.get(distro_key, "bookworm_arm64")
            filename = f"liblsl-{LIBLSL_VERSION}-{deb_suffix}.deb"
        else:
            # Detect distribution for x86_64
            distro = detect_linux_distro()
            if distro in LINUX_DISTROS:
                deb_suffix = LINUX_DISTROS[distro]
                filename = f"liblsl-{LIBLSL_VERSION}-{deb_suffix}.deb"
            else:
                # Default to jammy
                deb_suffix = LINUX_DISTROS["jammy"]
                filename = f"liblsl-{LIBLSL_VERSION}-{deb_suffix}.deb"
    elif arch not in PLATFORM_FILES[system]:
        # For macOS, try x86_64 version for arm64 (may work via Rosetta)
        if system == "Darwin" and arch == "arm64":
            filename = PLATFORM_FILES[system]["x86_64"]
        else:
            raise ValueError(f"Unsupported architecture for {system}: {arch}")
    else:
        filename = PLATFORM_FILES[system][arch]
    
    url = f"{LIBLSL_RELEASE_URL}/{filename}"
    
    # Create temp directory for download
    temp_dir = libs_dir.parent / ".liblsl_temp"
    temp_dir.mkdir(parents=True, exist_ok=True)
    archive_path = temp_dir / filename
    
    try:
        # Download
        if not archive_path.exists():
            download_file(url, archive_path)
        else:
            print(f"Using existing archive: {archive_path}")
        
        # Extract
        extract_dir = temp_dir / "extracted"
        if extract_dir.exists():
            shutil.rmtree(extract_dir)
        extract_archive(archive_path, extract_dir)
        
        # Find library (returns symlink path and actual library path)
        symlink_path, actual_lib_path = find_library_in_extracted(extract_dir)
        
        # Copy to final location
        libs_dir.mkdir(parents=True, exist_ok=True)
        if system == "Windows":
            (libs_dir / "bin").mkdir(exist_ok=True)
            lib_dir = libs_dir / "bin"
        else:
            (libs_dir / "lib").mkdir(exist_ok=True)
            lib_dir = libs_dir / "lib"
        
        # Copy the actual library file (resolve symlinks to get the real file)
        if actual_lib_path.is_symlink():
            actual_lib_path = actual_lib_path.resolve()
        actual_final_path = lib_dir / actual_lib_path.name
        shutil.copy2(actual_lib_path, actual_final_path)
        
        # Create symlink if needed (Linux/macOS)
        if system != "Windows":
            symlink_final_path = lib_dir / lib_name
            # Remove existing symlink/file if it exists
            if symlink_final_path.exists() or symlink_final_path.is_symlink():
                symlink_final_path.unlink()
            # Create symlink pointing to the actual library
            symlink_final_path.symlink_to(actual_final_path.name)
            print(f"✓ liblsl installed at: {symlink_final_path} -> {actual_final_path.name}")
            final_path = symlink_final_path  # Return symlink path for PYLSL_LIB
        else:
            print(f"✓ liblsl installed at: {actual_final_path}")
            final_path = actual_final_path
        
        # Cleanup
        shutil.rmtree(temp_dir)
        
        return final_path
        
    except Exception as e:
        print(f"Error during setup: {e}")
        if temp_dir.exists():
            print(f"Temporary files remain in: {temp_dir}")
        raise


def set_pylsl_lib_env(lib_path: Path):
    """Set PYLSL_LIB environment variable."""
    lib_path_str = str(lib_path.absolute())
    os.environ["PYLSL_LIB"] = lib_path_str
    print(f"✓ Set PYLSL_LIB={lib_path_str}")
    
    # Also print instructions for permanent setup
    print("\nTo make this permanent, add to your shell configuration:")
    if platform.system() == "Windows":
        print(f'  setx PYLSL_LIB "{lib_path_str}"')
    else:
        print(f'  export PYLSL_LIB="{lib_path_str}"')
        print("  Add this line to ~/.bashrc or ~/.zshrc")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Download and setup liblsl")
    parser.add_argument(
        "--dir",
        type=Path,
        default=None,
        help="Directory to install liblsl (default: ~/.local/lib/liblsl)",
    )
    parser.add_argument(
        "--set-env",
        action="store_true",
        help="Set PYLSL_LIB environment variable",
    )
    
    args = parser.parse_args()
    
    try:
        lib_path = setup_liblsl(args.dir)
        
        if args.set_env:
            set_pylsl_lib_env(lib_path)
        else:
            print(f"\nTo use liblsl, set PYLSL_LIB environment variable:")
            print(f'  export PYLSL_LIB="{lib_path.absolute()}"')
        
        return 0
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
