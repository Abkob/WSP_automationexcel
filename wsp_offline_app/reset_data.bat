@echo off
title WSP Offline System — Reset Data
echo.
echo  WARNING: This will permanently delete all student data,
echo  backups, exports, and the search index.
echo  The app must NOT be running when you do this.
echo.
if not exist "%~dp0.venv\Scripts\python.exe" (
    echo  ERROR: Virtual environment not found. Run setup.bat first.
    pause
    exit /b 1
)
"%~dp0.venv\Scripts\python.exe" "%~dp0scripts\reset_data.py"
pause
