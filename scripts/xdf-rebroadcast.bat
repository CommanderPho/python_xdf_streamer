@echo off
cd /d "%~dp0.."
uv run xdf-rebroadcast %*
