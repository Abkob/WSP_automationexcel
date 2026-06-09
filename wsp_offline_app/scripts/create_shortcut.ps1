# Creates a desktop shortcut that silently launches WSP Offline System.
# Run this from setup.bat, or execute directly with:
#   powershell -ExecutionPolicy Bypass -File scripts\create_shortcut.ps1

$AppDir    = Split-Path $PSScriptRoot -Parent
$PythonW   = Join-Path $AppDir ".venv\Scripts\pythonw.exe"
$Launcher  = Join-Path $AppDir "wsp_launcher.pyw"
$Desktop   = [Environment]::GetFolderPath("Desktop")
$Shortcut  = Join-Path $Desktop "WSP Offline System.lnk"

if (-not (Test-Path $PythonW)) {
    Write-Host "ERROR: $PythonW not found. Run setup.bat first." -ForegroundColor Red
    exit 1
}

$Shell = New-Object -ComObject WScript.Shell
$Link  = $Shell.CreateShortcut($Shortcut)

$Link.TargetPath       = $PythonW
$Link.Arguments        = "`"$Launcher`""
$Link.WorkingDirectory = $AppDir
$Link.WindowStyle      = 7          # SW_SHOWMINNOACTIVE — prevents any window flash
$Link.Description      = "WSP Offline Student Search System"

# Use AUB seal as icon if present, otherwise fall back to Python icon
$IconCandidate = Join-Path $AppDir "app\static\aub-seal.ico"
if (Test-Path $IconCandidate) {
    $Link.IconLocation = $IconCandidate
} else {
    $Link.IconLocation = "$PythonW,0"
}

$Link.Save()
Write-Host "Shortcut created: $Shortcut" -ForegroundColor Green
