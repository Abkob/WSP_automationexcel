@echo off
title WSP Offline System — Update
setlocal

echo.
echo  ============================================================
echo   WSP Offline System — Update
echo  ============================================================
echo.

REM ── Check the venv exists ─────────────────────────────────────────────────
if not exist "%~dp0.venv\Scripts\activate" (
    echo  ERROR: Virtual environment not found. Run setup.bat first.
    pause
    exit /b 1
)

REM ── Pull latest code (if running from a git repo) ─────────────────────────
git -C "%~dp0" pull 2>nul
if errorlevel 1 (
    echo  Note: git pull skipped (not a git repo or no network).
    echo  If you received updated files on a USB, copy them manually
    echo  into this folder and then run update.bat again.
    echo.
)

REM ── Sync packages in case requirements.txt changed ────────────────────────
echo  Checking for package updates...
"%~dp0.venv\Scripts\pip" install -r "%~dp0requirements.txt" --quiet
if errorlevel 1 (
    echo  WARNING: pip install reported an error.
)

echo.
echo  ============================================================
echo   Update complete. Launch the app as usual.
echo  ============================================================
echo.
pause
endlocal
