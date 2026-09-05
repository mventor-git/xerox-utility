@echo off
REM Double-click starter for Xerox Utility. No typing needed.
cd /d "%~dp0"
python -m src.app.tray
pause
