@echo off
REM Launcher: ASCII only, so no code-page issues. All text is printed by serve.py
cd /d "%~dp0"
python serve.py
if errorlevel 1 py serve.py
pause
