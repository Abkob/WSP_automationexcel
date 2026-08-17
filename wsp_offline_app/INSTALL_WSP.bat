@echo off
setlocal
title WSP Offline System - One-Click Installer

cd /d "%~dp0"

echo.
echo  ============================================================
echo   WSP Offline System - One-Click Installer
echo  ============================================================
echo.
echo  This installs Python when needed, creates the private app
echo  environment, installs all packages and the local AI model,
echo  verifies the complete installation, and creates shortcuts.
echo.
echo  Install location:
echo  %LOCALAPPDATA%\WSP Offline System
echo.

powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\install.ps1"
set "INSTALL_EXIT=%ERRORLEVEL%"

echo.
if not "%INSTALL_EXIT%"=="0" (
    echo  Installation did not complete.
    echo  Review the error above and the install log, then run this file again.
    echo  Log: %LOCALAPPDATA%\WSP Offline System\wsp_offline_app\data\install.log
) else (
    echo  Installation completed successfully.
)
echo.
pause
exit /b %INSTALL_EXIT%
