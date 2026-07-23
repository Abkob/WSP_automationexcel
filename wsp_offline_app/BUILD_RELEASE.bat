@echo off
setlocal
title WSP Offline System - Build Release Package
cd /d "%~dp0"

powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\build_release.ps1"
set "BUILD_EXIT=%ERRORLEVEL%"

echo.
if not "%BUILD_EXIT%"=="0" (
    echo Release build failed.
) else (
    echo Release package is ready in the dist folder.
)
echo.
pause
exit /b %BUILD_EXIT%
