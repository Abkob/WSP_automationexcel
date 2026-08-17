@echo off
setlocal
title WSP Offline System - Uninstall
set "UNINSTALL_SCRIPT=%~dp0scripts\uninstall.ps1"
cd /d "%TEMP%"

powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%UNINSTALL_SCRIPT%"
set "UNINSTALL_EXIT=%ERRORLEVEL%"

echo.
if not "%UNINSTALL_EXIT%"=="0" (
    echo Uninstall did not complete.
) else (
    echo WSP Offline System was removed.
)
echo.
pause
exit /b %UNINSTALL_EXIT%
