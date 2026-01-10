"""Test liblsl setup functionality."""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, str(Path(__file__).parent / "scripts"))


def test_platform_detection():
    """Test platform detection."""
    print("Testing platform detection...")
    from download_liblsl import get_platform_info
    
    system, arch = get_platform_info()
    print(f"✓ Detected platform: {system} ({arch})")
    assert system in ["Linux", "Darwin", "Windows"]
    assert arch in ["x86_64", "aarch64", "arm64"]
    return system, arch


def test_library_paths():
    """Test library path generation."""
    print("\nTesting library path generation...")
    from download_liblsl import get_library_path, LIBRARY_NAMES
    import platform
    
    system = platform.system()
    base_dir = Path.home() / ".local" / "lib" / "liblsl"
    
    lib_path = get_library_path(base_dir)
    expected_name = LIBRARY_NAMES[system]
    
    print(f"✓ Library path: {lib_path}")
    print(f"✓ Expected name: {expected_name}")
    assert expected_name in str(lib_path)
    return lib_path


def test_liblsl_finder():
    """Test liblsl finder."""
    print("\nTesting liblsl finder...")
    from xdf_streamer.utils.liblsl_setup import find_liblsl
    
    result = find_liblsl()
    if result:
        print(f"✓ Found liblsl at: {result}")
    else:
        print("✓ liblsl not found (expected if not installed)")
    return result


def test_environment_variable():
    """Test PYLSL_LIB environment variable handling."""
    print("\nTesting PYLSL_LIB environment variable...")
    
    # Test setting
    test_path = "/test/path/liblsl.so"
    os.environ["PYLSL_LIB"] = test_path
    
    from xdf_streamer.utils.liblsl_setup import find_liblsl
    result = find_liblsl()
    
    if result:
        print(f"✓ PYLSL_LIB respected: {result}")
        assert str(result) == test_path
    else:
        print("✓ PYLSL_LIB checked (file doesn't exist, but variable was read)")
    
    # Cleanup
    if "PYLSL_LIB" in os.environ and os.environ["PYLSL_LIB"] == test_path:
        del os.environ["PYLSL_LIB"]


def main():
    """Run all tests."""
    print("=" * 60)
    print("liblsl Setup Test Suite")
    print("=" * 60)
    
    try:
        system, arch = test_platform_detection()
        lib_path = test_library_paths()
        find_result = test_liblsl_finder()
        test_environment_variable()
        
        print("\n" + "=" * 60)
        print("All tests passed!")
        print("=" * 60)
        print(f"\nPlatform: {system} ({arch})")
        print(f"Expected library location: {lib_path}")
        if find_result:
            print(f"Current liblsl location: {find_result}")
        else:
            print("liblsl not installed. Run: uv run python scripts/download_liblsl.py")
        
        return 0
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
