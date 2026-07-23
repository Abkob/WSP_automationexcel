@echo off
setlocal
cd /d "%~dp0"

if not exist "%~dp0.venv\Scripts\pythonw.exe" (
    echo WSP is not installed yet. Starting the installer...
    call "%~dp0INSTALL_WSP.bat"
    exit /b %ERRORLEVEL%
)

start "" "%~dp0.venv\Scripts\pythonw.exe" "%~dp0wsp_launcher.pyw"
exit /b 0
