"""Command-line interface for multi-stream XDF rebroadcasting."""

import argparse
import signal
import sys
from pathlib import Path

from .core.multi_stream_rebroadcaster import MultiStreamRebroadcaster


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Rebroadcast XDF file streams via LSL")
    parser.add_argument("xdf_file", type=Path, help="Path to XDF file")
    parser.add_argument(
        "--streams",
        type=str,
        help="Comma-separated list of stream IDs to rebroadcast (e.g., '0,1,2'). Default: all streams",
    )
    parser.add_argument(
        "--list-streams",
        action="store_true",
        help="List available streams and exit",
    )

    args = parser.parse_args()

    if not args.xdf_file.exists():
        print(f"Error: XDF file not found: {args.xdf_file}", file=sys.stderr)
        sys.exit(1)

    rebroadcaster = MultiStreamRebroadcaster()

    try:
        # Load XDF file
        print(f"Loading XDF file: {args.xdf_file}")
        xdf_data = rebroadcaster.load_xdf(args.xdf_file)
        print(f"Loaded {rebroadcaster.get_stream_count()} stream(s)")

        # List streams if requested
        if args.list_streams:
            print("\nAvailable streams:")
            for i, stream_info in enumerate(xdf_data.streams):
                print(f"  Stream {i}: {stream_info.name}")
                print(f"    Type: {stream_info.type}")
                print(f"    Channels: {stream_info.channel_count}")
                print(f"    Sampling Rate: {stream_info.sampling_rate} Hz")
                print(f"    Format: {stream_info.channel_format}")
            sys.exit(0)

        # Parse stream IDs
        stream_ids = None
        if args.streams:
            try:
                stream_ids = [int(s.strip()) for s in args.streams.split(",")]
            except ValueError:
                print(f"Error: Invalid stream IDs format: {args.streams}", file=sys.stderr)
                sys.exit(1)

        # Start rebroadcasting
        print("\nStarting rebroadcast...")
        if stream_ids:
            print(f"Rebroadcasting streams: {stream_ids}")
        else:
            print("Rebroadcasting all streams")

        outlets = rebroadcaster.start_rebroadcast(stream_ids=stream_ids)

        print(f"Created {len(outlets)} LSL outlet(s)")
        for i, outlet in enumerate(outlets):
            stream_id = stream_ids[i] if stream_ids else i
            stream_info = xdf_data.streams[stream_id]
            print(f"  Outlet {i} (Stream {stream_id}): {stream_info.name}")

        print("\nStreaming... Press Ctrl+C to stop")

        # Handle interrupt signal
        def signal_handler(sig, frame):
            print("\n\nStopping rebroadcast...")
            rebroadcaster.stop_rebroadcast()
            print("Stopped.")
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Wait for streaming to complete or interrupt
        for thread in rebroadcaster.stream_threads:
            thread.join()

        print("\nAll streams completed.")

    except KeyboardInterrupt:
        print("\n\nStopping rebroadcast...")
        rebroadcaster.stop_rebroadcast()
        print("Stopped.")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        rebroadcaster.stop_rebroadcast()
        sys.exit(1)


if __name__ == "__main__":
    main()
