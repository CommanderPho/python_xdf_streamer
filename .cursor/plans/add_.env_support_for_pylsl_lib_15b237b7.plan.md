---
name: Add .env support for PYLSL_LIB
overview: Add support for a repository-local .env file to specify PYLSL_LIB, eliminating the need for users to manually modify shell configuration files. The download script will automatically write to .env, and the library detection code will load it.
todos:
  - id: add_dotenv_dependency
    content: Add python-dotenv to pyproject.toml dependencies
    status: completed
  - id: update_liblsl_setup
    content: Update liblsl_setup.py to load .env file from repository root before checking PYLSL_LIB
    status: completed
  - id: update_download_script
    content: Modify download_liblsl.py to write PYLSL_LIB to .env file when --set-env is used
    status: completed
  - id: create_env_example
    content: Create .env.example template file with platform-specific examples
    status: completed
  - id: update_gitignore
    content: Add .env to .gitignore to prevent committing local configuration
    status: completed
  - id: update_documentation
    content: Update QUICKSTART.md, INSTALLATION.md, README.md, and CROSS_PLATFORM_SETUP.md to mention .env file support
    status: completed
---

# Add .env File Support for PYLSL_LIB Configuration

## Overview

Add support for a repository-local `.env` file to store `PYLSL_LIB` path, making setup easier without requiring shell configuration changes. The download script will automatically write to `.env`, and the library detection will load it.

## Implementation Steps

### 1. Add python-dotenv Dependency

- Add `python-dotenv` to `pyproject.toml` dependencies
- This will be used to load `.env` files

### 2. Update Library Detection (`src/xdf_streamer/utils/liblsl_setup.py`)

- Import `load_dotenv` from `dotenv` at the top
- Add a function to load `.env` from the repository root (find it by looking for `pyproject.toml` or `.git` directory)
- Call `load_dotenv()` early in `find_liblsl()` before checking `PYLSL_LIB` environment variable
- This ensures `.env` values are loaded before any other checks

### 3. Update Download Script (`scripts/download_liblsl.py`)

- Import `load_dotenv` and `dotenv_values` from `dotenv`
- Modify `set_pylsl_lib_env()` to:
- Set the environment variable (current behavior)
- Also write to `.env` file in repository root
- Use `dotenv_values` to preserve existing `.env` entries
- Add `--write-env` flag (or make it automatic with `--set-env`) to write to `.env`
- Find repository root by looking for `pyproject.toml` or `.git` directory

### 4. Create .env.example Template

- Create `.env.example` file with example `PYLSL_LIB` path
- Include platform-specific examples in comments
- This serves as documentation and template for users

### 5. Update .gitignore

- Add `.env` to `.gitignore` to prevent committing local paths

### 6. Update Documentation

- Update `QUICKSTART.md` to mention `.env` file option
- Update `INSTALLATION.md` to include `.env` as an option
- Update `README.md` to mention `.env` support
- Update `CROSS_PLATFORM_SETUP.md` to document `.env` support

## File Changes Summary

- `pyproject.toml`: Add `python-dotenv` dependency
- `src/xdf_streamer/utils/liblsl_setup.py`: Load `.env` file before checking environment variables
- `scripts/download_liblsl.py`: Write to `.env` file when `--set-env` is used
- `.env.example`: Create template file
- `.gitignore`: Add `.env` entry
- Documentation files: Update with `.env` information

## Priority Order

1. Environment variable (highest priority)
2. `.env` file in repository root
3. Common installation locations (existing behavior)
4. System library paths (existing behavior)

This ensures backward compatibility while adding the new convenience feature.