"""Example: Multi-stream XDF rebroadcasting."""

import time
from pathlib import Path

from xdf_streamer.core.multi_stream_rebroadcaster import MultiStreamRebroadcaster


def main():
    """Example usage of MultiStreamRebroadcaster."""
    # Example 1: Rebroadcast all streams
    print("Example 1: Rebroadcast all streams from XDF file")
    print("-" * 60)

    xdf_file = Path("path/to/your/file.xdf")  # Replace with actual XDF file path

    if not xdf_file.exists():
        print(f"XDF file not found: {xdf_file}")
        print("Please update the path to a valid XDF file.")
        return

    rebroadcaster = MultiStreamRebroadcaster()

    try:
        # Load XDF file
        print(f"Loading XDF file: {xdf_file}")
        xdf_data = rebroadcaster.load_xdf(xdf_file)
        print(f"Loaded {rebroadcaster.get_stream_count()} stream(s)")

        # Display stream information
        print("\nStream information:")
        for i in range(rebroadcaster.get_stream_count()):
            stream_info = rebroadcaster.get_stream_info(i)
            print(f"  Stream {i}: {stream_info.name}")
            print(f"    Type: {stream_info.type}")
            print(f"    Channels: {stream_info.channel_count}")
            print(f"    Sampling Rate: {stream_info.sampling_rate} Hz")

        # Start rebroadcasting all streams
        print("\nStarting rebroadcast of all streams...")
        outlets = rebroadcaster.start_rebroadcast()

        print(f"Created {len(outlets)} LSL outlet(s)")
        for i, outlet in enumerate(outlets):
            stream_info = rebroadcaster.get_stream_info(i)
            print(f"  Outlet {i}: {stream_info.name} ({stream_info.channel_count} channels, {stream_info.sampling_rate} Hz)")

        print("\nStreaming... Press Ctrl+C to stop")
        # Wait for streaming to complete or interrupt
        for thread in rebroadcaster.stream_threads:
            thread.join()

        print("\nAll streams completed.")

    except KeyboardInterrupt:
        print("\n\nStopping rebroadcast...")
        rebroadcaster.stop_rebroadcast()
        print("Stopped.")
    except Exception as e:
        print(f"Error: {e}")
        rebroadcaster.stop_rebroadcast()

    # Example 2: Rebroadcast selected streams
    print("\n\nExample 2: Rebroadcast selected streams")
    print("-" * 60)

    rebroadcaster2 = MultiStreamRebroadcaster()

    try:
        xdf_data = rebroadcaster2.load_xdf(xdf_file)
        print(f"Loaded {rebroadcaster2.get_stream_count()} stream(s)")

        # Select only streams 0 and 2
        selected_stream_ids = [0, 2]
        print(f"\nRebroadcasting only streams: {selected_stream_ids}")

        outlets = rebroadcaster2.start_rebroadcast(stream_ids=selected_stream_ids)
        print(f"Created {len(outlets)} LSL outlet(s)")

        # Let it run briefly
        time.sleep(2.0)

        rebroadcaster2.stop_rebroadcast()
        print("Stopped.")

    except Exception as e:
        print(f"Error: {e}")
        rebroadcaster2.stop_rebroadcast()

    # Example 3: Using context manager
    print("\n\nExample 3: Using context manager")
    print("-" * 60)

    try:
        with MultiStreamRebroadcaster() as rebroadcaster3:
            xdf_data = rebroadcaster3.load_xdf(xdf_file)
            print(f"Loaded {rebroadcaster3.get_stream_count()} stream(s)")

            outlets = rebroadcaster3.start_rebroadcast()
            print(f"Created {len(outlets)} LSL outlet(s)")

            # Stream will automatically stop when exiting context
            time.sleep(2.0)

        print("Context exited - streaming stopped automatically.")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
