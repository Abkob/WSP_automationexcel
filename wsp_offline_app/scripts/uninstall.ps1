[CmdletBinding()]
param([switch]$DeleteData)

$ErrorActionPreference = "Stop"
$AppDirectory = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$InstallRoot = Split-Path -Parent $AppDirectory
$ExpectedRoot = [IO.Path]::GetFullPath((Join-Path $env:LOCALAPPDATA "WSP Offline System"))
$DesktopDirectory = [Environment]::GetFolderPath("Desktop")
$ProgramsDirectory = [Environment]::GetFolderPath("Programs")

function Assert-SafeUninstallTarget {
    $resolvedRoot = [IO.Path]::GetFullPath($InstallRoot).TrimEnd("\")
    $resolvedExpected = $ExpectedRoot.TrimEnd("\")
    if (-not $resolvedRoot.Equals($resolvedExpected, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to remove an unexpected folder: $resolvedRoot"
    }
    if ((Split-Path -Leaf $resolvedRoot) -ne "WSP Offline System") {
        throw "Unexpected installation folder name: $resolvedRoot"
    }
}

try {
    Assert-SafeUninstallTarget
    Write-Host "WSP Offline System uninstall" -ForegroundColor White
    Write-Host "Installed folder: $InstallRoot"

    if (-not $DeleteData) {
        $answer = Read-Host "Delete the local database, imported files, exports, and backups too? [y/N]"
        $DeleteData = $answer -match "^(y|yes)$"
    }

    Get-CimInstance Win32_Process -Filter "Name = 'python.exe' OR Name = 'pythonw.exe'" |
        Where-Object { $_.CommandLine -and $_.CommandLine.IndexOf($AppDirectory, [StringComparison]::OrdinalIgnoreCase) -ge 0 } |
        ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }

    if ($DesktopDirectory) {
        Remove-Item -LiteralPath (Join-Path $DesktopDirectory "WSP Offline System.lnk") -Force -ErrorAction SilentlyContinue
        Remove-Item -LiteralPath (Join-Path $DesktopDirectory "WSP Import Folder.lnk") -Force -ErrorAction SilentlyContinue
    }
    if ($ProgramsDirectory) {
        Remove-Item -LiteralPath (Join-Path $ProgramsDirectory "WSP Offline System") -Recurse -Force -ErrorAction SilentlyContinue
    }

    if (-not $DeleteData) {
        $backupRoot = Join-Path ([Environment]::GetFolderPath("MyDocuments")) ("WSP Offline System Data " + (Get-Date -Format "yyyyMMdd-HHmmss"))
        New-Item -ItemType Directory -Path $backupRoot -Force | Out-Null
        foreach ($itemName in @("data", "Import Folder", "Export Folder")) {
            $source = if ($itemName -eq "data") { Join-Path $AppDirectory $itemName } else { Join-Path $InstallRoot $itemName }
            if (Test-Path -LiteralPath $source) {
                Move-Item -LiteralPath $source -Destination (Join-Path $backupRoot $itemName) -Force
            }
        }
        Write-Host "Local data was preserved at: $backupRoot" -ForegroundColor Yellow
    }

    Set-Location -LiteralPath $env:TEMP
    Remove-Item -LiteralPath $InstallRoot -Recurse -Force
    Write-Host "Uninstall completed." -ForegroundColor Green
    exit 0
}
catch {
    Write-Host "UNINSTALL ERROR: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
