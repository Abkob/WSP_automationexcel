@echo off
title WSP Offline System — Setup
setlocal

echo.
echo  ============================================================
echo   WSP Offline System — Setup / Reinstall
echo  ============================================================
echo.

REM ── Check Python ──────────────────────────────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo  ERROR: Python is not installed or not in PATH.
    echo.
    echo  Please install Python 3.11 or newer from:
    echo    https://www.python.org/downloads/
    echo.
    echo  Make sure to check "Add Python to PATH" during install.
    pause
    exit /b 1
)

for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PYVER=%%v
echo  [OK] Python %PYVER% found.
echo.

REM ── Create virtual environment ────────────────────────────────────────────
echo  [1/3] Setting up virtual environment...
if not exist "%~dp0.venv\Scripts\activate" (
    python -m venv "%~dp0.venv"
    if errorlevel 1 (
        echo  ERROR: Could not create virtual environment.
        pause
        exit /b 1
    )
    echo       Created new .venv
) else (
    echo       Existing .venv found — will update packages if needed.
)

REM ── Install / update packages ─────────────────────────────────────────────
echo.
echo  [2/3] Installing Python packages...
echo        (First run: ~10 minutes.  Subsequent runs: ~30 seconds.)
echo.
"%~dp0.venv\Scripts\pip" install --upgrade pip --quiet
"%~dp0.venv\Scripts\pip" install -r "%~dp0requirements.txt" --quiet
if errorlevel 1 (
    echo.
    echo  ERROR: Package installation failed.
    echo  Make sure you are connected to the internet for first-time setup.
    pause
    exit /b 1
)
echo  [OK] Packages installed.

REM ── Desktop shortcut ──────────────────────────────────────────────────────
echo.
echo  [3/3] Creating desktop shortcut...
powershell -ExecutionPolicy Bypass -File "%~dp0scripts\create_shortcut.ps1"
if errorlevel 1 (
    echo  WARNING: Could not create shortcut automatically.
    echo  You can still launch the app with launch.bat.
)

REM ── Done ──────────────────────────────────────────────────────────────────
echo.
echo  ============================================================
echo   Setup complete!
echo.
echo   To start the app:
echo     • Double-click the "WSP Offline System" shortcut on your desktop
echo     • Or double-click launch.bat in this folder
echo.
echo   The app opens in your browser automatically.
echo   A tray icon appears in the taskbar (bottom-right corner).
echo   Right-click the tray icon and choose "Exit" to stop the app.
echo  ============================================================
echo.
pause
endlocal
