"""Runner for the GUI entry point (src/gui_main.py). Used by the `uv run gui` script."""

import runpy
from pathlib import Path


def main():
    """Run the GUI by executing src/gui_main.py. Works when cwd is project root (e.g. uv run gui)."""
    cwd = Path.cwd()
    script_path = cwd / "src" / "gui_main.py"
    if not script_path.exists():
        script_path = Path(__file__).resolve().parent.parent / "gui_main.py"
    runpy.run_path(str(script_path), run_name="__main__")
