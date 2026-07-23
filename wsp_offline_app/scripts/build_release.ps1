[CmdletBinding()]
param(
    [string]$OutputDirectory
)

$ErrorActionPreference = "Stop"
$AppDirectory = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
if (-not $OutputDirectory) {
    $OutputDirectory = Join-Path $AppDirectory "dist"
}
$OutputDirectory = [IO.Path]::GetFullPath($OutputDirectory)
$Version = (Get-Content -LiteralPath (Join-Path $AppDirectory "version.txt") -Raw).Trim()
$PackageName = "WSP_Offline_System_v$Version"
$StageDirectory = Join-Path $OutputDirectory $PackageName
$StageAppDirectory = Join-Path $StageDirectory "wsp_offline_app"
$ZipPath = Join-Path $OutputDirectory "$PackageName.zip"

function Assert-SafeStagePath {
    $resolvedOutput = [IO.Path]::GetFullPath($OutputDirectory).TrimEnd("\")
    $resolvedStage = [IO.Path]::GetFullPath($StageDirectory)
    if (-not $resolvedStage.StartsWith("$resolvedOutput\", [StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to clean a staging path outside the selected output directory: $resolvedStage"
    }
    if ((Split-Path -Leaf $resolvedStage) -ne $PackageName) {
        throw "Unexpected staging folder name: $resolvedStage"
    }
}

function Copy-ReleaseItem {
    param([string]$RelativePath)
    $source = Join-Path $AppDirectory $RelativePath
    $destination = Join-Path $StageAppDirectory $RelativePath
    if (-not (Test-Path -LiteralPath $source)) {
        throw "Required release item is missing: $source"
    }
    $parent = Split-Path -Parent $destination
    New-Item -ItemType Directory -Path $parent -Force | Out-Null
    Copy-Item -LiteralPath $source -Destination $destination -Recurse -Force
}

Assert-SafeStagePath
New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null
if (Test-Path -LiteralPath $StageDirectory) {
    Remove-Item -LiteralPath $StageDirectory -Recurse -Force
}
if (Test-Path -LiteralPath $ZipPath) {
    Remove-Item -LiteralPath $ZipPath -Force
}
New-Item -ItemType Directory -Path $StageAppDirectory -Force | Out-Null

foreach ($item in @(
    "app",
    "database",
    "services",
    "config.py",
    "main.py",
    "wsp_launcher.pyw",
    "requirements.txt",
    "pyproject.toml",
    "README.md",
    "version.txt",
    "INSTALL_WSP.bat",
    "LAUNCH_WSP.bat",
    "UPDATE_WSP.bat",
    "scripts\install.ps1",
    "scripts\download_mxbai.py",
    "scripts\bundle_model.py",
    "scripts\create_shortcut_icon.py"
)) {
    Copy-ReleaseItem -RelativePath $item
}

Get-ChildItem -LiteralPath $StageAppDirectory -Recurse -Directory -Force |
    Where-Object { $_.Name -in @("__pycache__", ".pytest_cache") } |
    Sort-Object FullName -Descending |
    Remove-Item -Recurse -Force
Get-ChildItem -LiteralPath $StageAppDirectory -Recurse -File -Force |
    Where-Object { $_.Extension -in @(".pyc", ".pyo") } |
    Remove-Item -Force

$RootInstaller = @'
@echo off
call "%~dp0wsp_offline_app\INSTALL_WSP.bat"
exit /b %ERRORLEVEL%
'@
Set-Content -LiteralPath (Join-Path $StageDirectory "INSTALL WSP - ONE CLICK.bat") -Value $RootInstaller -Encoding Ascii

$StartHere = @'
WSP OFFLINE SYSTEM - START HERE

1. Keep this entire folder together.
2. Double-click "INSTALL WSP - ONE CLICK.bat".
3. Wait for the installer to finish. Internet is required the first time.
4. Put the newest .xlsx or .xlsm workbook in "Import Folder".
5. Open "WSP Offline System" from the Desktop.

See wsp_offline_app\README.md for the complete guide.
'@
Set-Content -LiteralPath (Join-Path $StageDirectory "README - START HERE.txt") -Value $StartHere -Encoding Utf8

foreach ($folderName in @("Import Folder", "Export Folder")) {
    $folder = Join-Path $StageDirectory $folderName
    New-Item -ItemType Directory -Path $folder -Force | Out-Null
}
Set-Content -LiteralPath (Join-Path $StageDirectory "Import Folder\PUT_NEWEST_EXCEL_FILE_HERE.txt") -Value "Place the newest .xlsx or .xlsm WSP workbook in this folder. The app ignores this text file." -Encoding Utf8
Set-Content -LiteralPath (Join-Path $StageDirectory "Export Folder\FILTERED_EXPORTS_APPEAR_HERE.txt") -Value "Filtered Excel exports created by WSP appear in this folder." -Encoding Utf8

Compress-Archive -LiteralPath $StageDirectory -DestinationPath $ZipPath -CompressionLevel Optimal
Remove-Item -LiteralPath $StageDirectory -Recurse -Force

Write-Host ""
Write-Host "Release package created:" -ForegroundColor Green
Write-Host $ZipPath
