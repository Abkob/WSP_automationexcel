@echo off
setlocal
title WSP Offline System Setup
cd /d "%~dp0"

start "" powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -STA -File "%~dp0scripts\install_gui.ps1"
exit /b 0
