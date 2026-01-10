"""GUI application entry point."""

import logging
import sys

from PyQt6.QtWidgets import QApplication

from xdf_streamer.gui.main_window import MainWindow


def setup_logging():
    """Configure logging to output to console."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.StreamHandler(sys.stdout),
        ]
    )


def main():
    """Run GUI application."""
    setup_logging()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
