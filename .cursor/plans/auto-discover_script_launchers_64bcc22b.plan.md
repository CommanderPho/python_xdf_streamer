---
name: Auto-discover Script Launchers
overview: Create a VS Code tasks.json configuration that automatically discovers and creates launcher tasks for all scripts defined in pyproject.toml's [project.scripts] section, using uv run for cross-platform execution.
todos:
  - id: create_tasks_json
    content: Create .vscode/tasks.json with base task configuration and xdf-rebroadcast launcher task
    status: pending
  - id: add_input_variables
    content: Add input variables for common script arguments (file paths, stream IDs, etc.)
    status: pending
    dependencies:
      - create_tasks_json
isProject: false
---

# Auto-discover Script Launchers from pyproject.toml

## Overview

Create VS Code tasks that automatically discover and execute scripts defined in `pyproject.toml` under `[project.scripts]`. This provides a cross-platform way to run commands like `xdf-rebroadcast` directly from VS Code's Command Palette.

## Implementation

### 1. Create `.vscode/tasks.json`

Create a tasks configuration file that:

- Defines a base task template for running scripts via `uv run`
- Includes a task for the existing `xdf-rebroadcast` script
- Uses `uv run` which is cross-platform and handles virtual environment activation automatically
- Allows passing arguments to scripts via VS Code's task input system

### 2. Task Structure

Each task will:

- Use `uv run <script-name>` as the command
- Support argument passing through VS Code's input variables
- Be discoverable via Command Palette (Ctrl+Shift+P → "Tasks: Run Task")
- Work on Windows, Linux, and macOS

### 3. Future Extensibility

The structure will make it easy to add more scripts as they're added to `pyproject.toml`:

- Simply add new task entries following the same pattern
- Or create a script that parses `pyproject.toml` and generates tasks automatically (future enhancement)

## Files to Create/Modify

- `**.vscode/tasks.json**` (new file): VS Code tasks configuration with launcher tasks

## Example Task Format

```json
{
  "label": "xdf-rebroadcast",
  "type": "shell",
  "command": "uv run xdf-rebroadcast",
  "args": ["${input:xdfFile}"],
  "problemMatcher": []
}
```

This allows running `xdf-rebroadcast` with file path input through VS Code's UI.