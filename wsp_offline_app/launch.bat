@echo off
REM Launch WSP Offline System — no console window appears.
REM Double-click this file, or use the desktop shortcut created by setup.bat.

if not exist "%~dp0.venv\Scripts\pythonw.exe" (
    echo ERROR: Virtual environment not found.
    echo Please run setup.bat first.
    pause
    exit /b 1
)

start "" "%~dp0.venv\Scripts\pythonw.exe" "%~dp0wsp_launcher.pyw"
