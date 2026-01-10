---
name: Persist Last XDF File Path
overview: Add functionality to remember and persist the last navigated directory when selecting .xdf files, using Qt's QSettings for cross-platform persistence across application launches.
todos:
  - id: add_qsettings_import
    content: Add QSettings import to main_window.py
    status: completed
  - id: initialize_qsettings
    content: Initialize QSettings instance in MainWindow.__init__
    status: completed
  - id: load_last_path
    content: Load last XDF directory from QSettings on initialization
    status: completed
  - id: update_file_dialog
    content: Update _on_browse_clicked() to use last directory in file dialog
    status: completed
  - id: save_last_path
    content: Save selected file directory to QSettings after file selection
    status: completed
---

# Persist Last XDF File Path

## Overview

Implement persistent storage of the last used directory path when selecting .xdf files. The path will be remembered within a session and persist across application launches using Qt's QSettings.

## Implementation

### 1. Update MainWindow to Use QSettings

**File**: [`src/xdf_streamer/gui/main_window.py`](src/xdf_streamer/gui/main_window.py)

- Import `QSettings` from `PyQt6.QtCore`
- Add a `QSettings` instance in `__init__` to manage persistent settings
- Define a settings key constant for the last file path (e.g., `"last_xdf_directory"`)

### 2. Load Last Path on Initialization

**File**: [`src/xdf_streamer/gui/main_window.py`](src/xdf_streamer/gui/main_window.py)

- In `__init__`, load the last used directory from QSettings
- Store it as an instance variable (e.g., `self.last_xdf_directory`)
- If no previous path exists, default to empty string (which will use OS default)

### 3. Update File Dialog to Use Last Path

**File**: [`src/xdf_streamer/gui/main_window.py`](src/xdf_streamer/gui/main_window.py)

- Modify `_on_browse_clicked()` method (line 175-181)
- Change `QFileDialog.getOpenFileName()` to use `self.last_xdf_directory` as the initial directory instead of empty string
- Extract the directory from the selected file path and save it to QSettings

### 4. Save Path When File is Selected

**File**: [`src/xdf_streamer/gui/main_window.py`](src/xdf_streamer/gui/main_window.py)

- In `_on_browse_clicked()`, after a file is selected:
- Extract the directory from the selected file path using `Path(file_path).parent`
- Save the directory path to QSettings
- Update `self.last_xdf_directory` for the current session

## Technical Details

- **QSettings Organization**: Use `QSettings("python-xdf-streamer", "xdf-streamer")` for proper organization
- **Path Handling**: Use `Path` objects for cross-platform path handling, convert to string for QSettings
- **Default Behavior**: If no previous path exists, QFileDialog will use the OS default (usually user's home or Documents folder)
- **Directory vs File**: Store the directory path, not the full file path, so the dialog opens in the correct folder

## Code Changes Summary

1. Add QSettings import and initialization in `MainWindow.__init__`
2. Load last directory in `__init__`
3. Update `_on_browse_clicked()` to:

- Use last directory as initial path in file dialog
- Save selected file's directory to QSettings after selection

## Benefits

- Improved UX: Users don't have to navigate to the same folder repeatedly
- Cross-platform: QSettings handles Windows registry, macOS plist, and Linux config files automatically
- No external dependencies: Uses built-in Qt functionality
- Persistent: Settings survive application restarts