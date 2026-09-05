@echo off
REM Xerox Utility -- full automatic setup for office PCs.
REM Python (winget - choco - direct) - packages - printer find -
REM shortcuts (+ autostart). Just double-click.
setlocal EnableDelayedExpansion
cd /d "%~dp0"
set APPDIR=%CD%

echo === Xerox Utility full setup ===
echo.
echo [1/6] Checking Python 3.11+...
python --version >nul 2>&1
if not errorlevel 1 goto :pyfound
goto :install_python

:install_python
echo Python not found -- installing it automatically...
echo.
echo --- trying winget ---
where winget >nul 2>&1
if not errorlevel 1 (
  winget install -e --id Python.Python.3.11 --accept-package-agreements --accept-source-agreements
)
python --version >nul 2>&1
if not errorlevel 1 goto :pyfound

echo.
echo --- trying Chocolatey ---
where choco >nul 2>&1
if errorlevel 1 (
  echo Chocolatey not found -- installing it first (may ask for admin approval)...
  powershell -NoProfile -ExecutionPolicy Bypass -Command "Set-ExecutionPolicy Bypass -Scope Process -Force; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))"
  set "PATH=%ALLUSERSPROFILE%\chocolatey\bin;%PATH%"
)
where choco >nul 2>&1
if not errorlevel 1 (
  choco install -y python
  set "PATH=%ALLUSERSPROFILE%\chocolatey\bin;%PATH%"
)
python --version >nul 2>&1
if not errorlevel 1 goto :pyfound

echo.
echo --- downloading Python directly ---
curl -L -o "%TEMP%\python-setup.exe" https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe
echo Installing quietly (Windows may ask for admin approval)...
"%TEMP%\python-setup.exe" /quiet InstallAllUsers=1 PrependPath=1
del "%TEMP%\python-setup.exe" >nul 2>&1
set "PATH=%ProgramFiles%\Python311;%ProgramFiles%\Python311\Scripts;%LOCALAPPDATA%\Programs\Python\Python311;%LOCALAPPDATA%\Programs\Python\Python311\Scripts;%PATH%"
python --version >nul 2>&1
if not errorlevel 1 goto :pyfound

echo [ERROR] Automatic install failed everywhere.
echo Please install Python 3.11+ from https://www.python.org/downloads/
echo ticking "Add python.exe to PATH", then run this file again.
pause
exit /b 1

:pyfound
for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PYVER=%%v
echo Found Python %PYVER%.

echo.
echo [2/6] Installing ALL required packages...
python -m pip install --upgrade pip >nul 2>&1
python -m pip install -r requirements.txt
if errorlevel 1 (
  echo System install blocked -- retrying for this user only...
  python -m pip install --user -r requirements.txt
)
if errorlevel 1 (
  echo [ERROR] Package install failed. Check your internet connection,
  echo then run this file again.
  pause
  exit /b 1
)

echo.
echo [3/6] Verifying every package...
python -c "import requests, PIL, pypdf, img2pdf, windows_toasts, customtkinter, pystray" 2>nul
if errorlevel 1 (
  echo [ERROR] At least one package is missing or broken.
  echo Run this file again; if it keeps failing, pass the messages above to support.
  pause
  exit /b 1
)
echo requests, Pillow, pypdf, img2pdf, windows-toasts, customtkinter, pystray -- all OK.

echo.
echo [4/6] Finding your printer and choosing its folder...
python setup_helper.py
if errorlevel 1 (
  echo [NOTE] Printer setup did not finish -- the app is installed, though.
  echo Re-run this file once the printer is reachable.
)

echo.
echo [5/6] Creating shortcuts and folders...
if not exist "%USERPROFILE%\Documents\Scans" mkdir "%USERPROFILE%\Documents\Scans"
powershell -NoProfile -Command "$s=(New-Object -COM WScript.Shell).CreateShortcut($env:USERPROFILE+'\Desktop\Xerox Utility.lnk'); $s.TargetPath='!APPDIR!\run.bat'; $s.WorkingDirectory='!APPDIR!'; $s.Save()"
if errorlevel 1 (
  echo [NOTE] Desktop shortcut failed -- just double-click run.bat in this folder instead.
) else (
  echo Desktop shortcut created.
)
set /p AUTO="Start Xerox Utility automatically at login? [Y/n] "
if /i "!AUTO:~0,1!"=="N" (
  echo OK -- start it by hand after login.
) else (
  powershell -NoProfile -Command "$s=(New-Object -COM WScript.Shell).CreateShortcut($env:APPDATA+'\Microsoft\Windows\Start Menu\Programs\Startup\Xerox Utility.lnk'); $s.TargetPath='!APPDIR!\run.bat'; $s.WorkingDirectory='!APPDIR!'; $s.Save()"
  if errorlevel 1 (
    echo [NOTE] Autostart shortcut failed -- start the app by hand after login.
  ) else (
    echo It will now start on its own every login.
  )
)

echo.
echo [6/6] All set! See guide.md for everyday use.
set /p STARTNOW="Start Xerox Utility now? [Y/N] "
if /i "!STARTNOW:~0,1!"=="Y" call run.bat
pause
