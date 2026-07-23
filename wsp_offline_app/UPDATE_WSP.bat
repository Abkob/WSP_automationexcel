@echo off
setlocal
title WSP Offline System - Update or Repair
cd /d "%~dp0"

echo.
echo  Updating/repairing the WSP environment...
echo.
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\install.ps1" -NoLaunch
set "UPDATE_EXIT=%ERRORLEVEL%"

echo.
if not "%UPDATE_EXIT%"=="0" (
    echo  Update/repair did not complete. See data\install.log.
) else (
    echo  Update/repair completed successfully.
)
echo.
pause
exit /b %UPDATE_EXIT%
