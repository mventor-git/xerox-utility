@echo off
REM Xerox Utility remover. Shortcuts + packages go; your files stay unless you say so.
setlocal EnableDelayedExpansion
cd /d "%~dp0"

echo === Removing Xerox Utility ===
del "%USERPROFILE%\Desktop\Xerox Utility.lnk" >nul 2>&1
del "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\Xerox Utility.lnk" >nul 2>&1
echo Shortcuts removed.
echo Python packages are left alone (other software may share them).

set /p WIPE="Also delete settings, history and the trash archive in %%APPDATA%%\Xerox Utility? [y/N] "
if /i "!WIPE!"=="Y" (
  rmdir /s /q "%APPDATA%\Xerox Utility"
  echo App data wiped.
) else (
  echo App data kept -- your trash archive is still there.
)
echo Done. Delete this folder by hand if you want it gone too.
pause
