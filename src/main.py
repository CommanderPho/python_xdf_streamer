"""Main entry point (CLI mode - future implementation)."""

import sys

from PyQt6.QtWidgets import QApplication

from xdf_streamer.gui.main_window import MainWindow


def main():
    """Main entry point."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
