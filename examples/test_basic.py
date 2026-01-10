"""Basic test script to verify code structure without requiring LSL."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test that core modules can be imported."""
    print("Testing imports...")
    
    # Test models
    from xdf_streamer.models.stream_info import StreamInfo
    from xdf_streamer.models.xdf_data import XdfData
    print("✓ Models imported")
    
    # Test utilities (that don't require pylsl)
    from xdf_streamer.utils.timing import get_precise_time, calculate_sleep_duration
    from xdf_streamer.utils.validators import validate_sampling_rate, validate_stream
    print("✓ Utilities imported")
    
    # Test core (may fail if pylsl not available)
    try:
        from xdf_streamer.core.xdf_loader import XdfLoader
        print("✓ XDF Loader imported")
    except Exception as e:
        print(f"✗ XDF Loader import failed: {e}")
    
    try:
        from xdf_streamer.core.stream_worker import StreamWorker
        print("✓ Stream Worker imported")
    except Exception as e:
        print(f"✗ Stream Worker import failed: {e}")
    
    try:
        from xdf_streamer.core.lsl_streamer import LslStreamer
        print("✓ LSL Streamer imported")
    except Exception as e:
        print(f"✗ LSL Streamer import failed (expected if liblsl not installed): {e}")
    
    try:
        from xdf_streamer.gui.main_window import MainWindow
        print("✓ GUI Main Window imported")
    except Exception as e:
        print(f"✗ GUI import failed: {e}")
    
    print("\nBasic structure test complete!")

def test_data_models():
    """Test data model creation."""
    print("\nTesting data models...")
    
    from xdf_streamer.models.stream_info import StreamInfo
    from xdf_streamer.models.xdf_data import XdfData
    
    stream_info = StreamInfo(
        name="TestStream",
        type="EEG",
        channel_count=32,
        sampling_rate=1000.0,
        channel_format="float32",
        channels=[],
        stream_id=0,
    )
    print(f"✓ Created StreamInfo: {stream_info.name}")
    
    xdf_data = XdfData()
    xdf_data.streams.append(stream_info)
    print(f"✓ Created XdfData with {len(xdf_data.streams)} stream(s)")
    
    print("Data models test complete!")

def test_validators():
    """Test validators."""
    print("\nTesting validators...")
    
    from xdf_streamer.models.stream_info import StreamInfo
    from xdf_streamer.utils.validators import validate_sampling_rate, validate_stream
    
    assert validate_sampling_rate(100.0) == True
    assert validate_sampling_rate(0.0) == False
    print("✓ Sampling rate validation works")
    
    stream_info = StreamInfo(
        name="Test",
        type="EEG",
        channel_count=32,
        sampling_rate=1000.0,
        channel_format="float32",
        channels=[],
        stream_id=0,
    )
    is_valid, msg = validate_stream(stream_info)
    assert is_valid == True
    print("✓ Stream validation works")
    
    print("Validators test complete!")

if __name__ == "__main__":
    print("=" * 50)
    print("Python XDF Streamer - Basic Structure Test")
    print("=" * 50)
    
    test_imports()
    test_data_models()
    test_validators()
    
    print("\n" + "=" * 50)
    print("All basic tests passed!")
    print("=" * 50)
