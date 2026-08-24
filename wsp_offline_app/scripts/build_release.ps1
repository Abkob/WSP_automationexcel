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
    "docs",
    "config.py",
    "main.py",
    "wsp_launcher.pyw",
    "requirements.txt",
    "requirements.lock.txt",
    "pyproject.toml",
    "README.md",
    "TASK_CHECKLIST.md",
    "version.txt",
    "INSTALL_WSP.bat",
    "LAUNCH_WSP.bat",
    "UPDATE_WSP.bat",
    "UNINSTALL_WSP.bat",
    "scripts\install.ps1",
    "scripts\install_gui.ps1",
    "scripts\uninstall.ps1",
    "scripts\verify_install.py",
    "scripts\download_mxbai.py",
    "scripts\bundle_model.py",
    "scripts\create_shortcut_icon.py",
    "scripts\audit_semantic_index.py"
)) {
    Copy-ReleaseItem -RelativePath $item
}

Get-ChildItem -LiteralPath $StageAppDirectory -Recurse -Directory -Force |
    Where-Object { $_.Name -in @("__pycache__", ".pytest_cache") } |
    Sort-Object FullName -Descending |
    Remove-Item -Recurse -Force
Get-ChildItem -LiteralPath $StageAppDirectory -Recurse -File -Force |
    Where-Object { $_.Extension -in @(".pyc", ".pyo") -or $_.Name.StartsWith("~$") } |
    Remove-Item -Force

$RootInstaller = @'
@echo off
start "" powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -STA -File "%~dp0wsp_offline_app\scripts\install_gui.ps1"
exit /b 0
'@
Set-Content -LiteralPath (Join-Path $StageDirectory "INSTALL WSP - ONE CLICK.bat") -Value $RootInstaller -Encoding Ascii

$StartHere = @'
WSP OFFLINE SYSTEM - START HERE

1. Extract the ZIP completely; keep this folder together during setup.
2. Double-click "INSTALL WSP - ONE CLICK.bat".
3. Wait while setup checks the package, Python, dependencies, model, and app.
4. WSP installs under Local AppData and creates Desktop/Start Menu shortcuts.
5. After setup succeeds, this extracted installer folder can be deleted.
6. Open "WSP Offline System" from the Desktop.

See wsp_offline_app\README.md for the complete guide.
'@
Set-Content -LiteralPath (Join-Path $StageDirectory "README - START HERE.txt") -Value $StartHere -Encoding Utf8

foreach ($folderName in @("Import Folder", "Export Folder")) {
    $folder = Join-Path $StageDirectory $folderName
    New-Item -ItemType Directory -Path $folder -Force | Out-Null
}
Set-Content -LiteralPath (Join-Path $StageDirectory "Import Folder\PUT_NEWEST_EXCEL_FILE_HERE.txt") -Value "Place the newest .xlsx or .xlsm WSP workbook in this folder. The app ignores this text file." -Encoding Utf8
Set-Content -LiteralPath (Join-Path $StageDirectory "Export Folder\FILTERED_EXPORTS_APPEAR_HERE.txt") -Value "Filtered Excel exports created by WSP appear in this folder." -Encoding Utf8

$ManifestLines = Get-ChildItem -LiteralPath $StageDirectory -Recurse -File -Force |
    Sort-Object FullName |
    ForEach-Object {
        $relativePath = $_.FullName.Substring($StageDirectory.Length + 1)
        $hash = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash
        "$hash|$relativePath"
    }
Set-Content -LiteralPath (Join-Path $StageDirectory "PACKAGE_MANIFEST.sha256") -Value $ManifestLines -Encoding Ascii

Compress-Archive -LiteralPath $StageDirectory -DestinationPath $ZipPath -CompressionLevel Optimal
$ZipHashPath = "$ZipPath.sha256"
$ZipHash = (Get-FileHash -LiteralPath $ZipPath -Algorithm SHA256).Hash
Set-Content -LiteralPath $ZipHashPath -Value "$ZipHash  $([IO.Path]::GetFileName($ZipPath))" -Encoding Ascii
Remove-Item -LiteralPath $StageDirectory -Recurse -Force

Write-Host ""
Write-Host "Release package created:" -ForegroundColor Green
Write-Host $ZipPath
Write-Host "SHA-256:" -ForegroundColor Green
Write-Host $ZipHashPath
