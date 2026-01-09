"""GUI application entry point."""

import sys

from PyQt6.QtWidgets import QApplication

from xdf_streamer.gui.main_window import MainWindow


def main():
    """Run GUI application."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
