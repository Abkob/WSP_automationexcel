[CmdletBinding()]
param(
    [switch]$SkipDependencies,
    [switch]$SkipModel,
    [switch]$SkipShortcuts,
    [switch]$NoLaunch,
    [string]$InstallDirectory
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"
$SourceDirectory = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$DefaultInstallRoot = Join-Path $env:LOCALAPPDATA "WSP Offline System"
if (-not $InstallDirectory) {
    $InstallDirectory = Join-Path $DefaultInstallRoot "wsp_offline_app"
}
$AppDirectory = [IO.Path]::GetFullPath($InstallDirectory)
$InstallRoot = Split-Path -Parent $AppDirectory
$DataDirectory = Join-Path $AppDirectory "data"
$LogPath = Join-Path $DataDirectory "install.log"
$VirtualEnvironment = Join-Path $AppDirectory ".venv"
$VenvPython = Join-Path $VirtualEnvironment "Scripts\python.exe"
$VenvPythonw = Join-Path $VirtualEnvironment "Scripts\pythonw.exe"
$Launcher = Join-Path $AppDirectory "wsp_launcher.pyw"
$Requirements = Join-Path $AppDirectory "requirements.txt"
$ModelDirectory = Join-Path $AppDirectory ".models"
$ShortcutIcon = Join-Path $AppDirectory "app\static\wsp.ico"
$MinimumPython = [Version]"3.11"
$PreferredPython = "3.12"
$MinimumFreeBytes = 6GB
$TranscriptStarted = $false

function Write-Step {
    param([string]$Message)
    Write-Host ""
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Write-Check {
    param([string]$Message)
    Write-Host "[OK] $Message" -ForegroundColor Green
}

function Assert-SafeInstallPath {
    if (-not $env:LOCALAPPDATA) {
        throw "Windows did not provide a Local AppData folder."
    }
    $resolvedLocal = [IO.Path]::GetFullPath($env:LOCALAPPDATA).TrimEnd("\")
    $resolvedApp = [IO.Path]::GetFullPath($AppDirectory)
    if (-not $resolvedApp.StartsWith("$resolvedLocal\", [StringComparison]::OrdinalIgnoreCase)) {
        throw "The install folder must be inside Local AppData: $resolvedLocal"
    }
    if ((Split-Path -Leaf $resolvedApp) -ne "wsp_offline_app") {
        throw "The application folder must be named wsp_offline_app."
    }
}

function Assert-SourcePayload {
    foreach ($relativePath in @(
        "app", "database", "services", "scripts", "docs", "config.py", "main.py",
        "wsp_launcher.pyw", "requirements.txt", "README.md", "TASK_CHECKLIST.md", "version.txt",
        "LAUNCH_WSP.bat", "UPDATE_WSP.bat", "UNINSTALL_WSP.bat"
    )) {
        $path = Join-Path $SourceDirectory $relativePath
        if (-not (Test-Path -LiteralPath $path)) {
            throw "The installer package is incomplete. Missing: $relativePath"
        }
    }
}

function Test-PackageIntegrity {
    $packageRoot = Split-Path -Parent $SourceDirectory
    $manifestPath = Join-Path $packageRoot "PACKAGE_MANIFEST.sha256"
    if (-not (Test-Path -LiteralPath $manifestPath)) {
        Write-Host "[INFO] Package checksum manifest is not present (developer/repair mode)." -ForegroundColor Yellow
        return
    }
    foreach ($line in Get-Content -LiteralPath $manifestPath) {
        if (-not $line.Trim()) { continue }
        $parts = $line.Split("|", 2)
        if ($parts.Count -ne 2) { throw "The package checksum manifest is invalid." }
        $expectedHash = $parts[0].Trim()
        $relativePath = $parts[1].Trim()
        $filePath = Join-Path $packageRoot $relativePath
        if (-not (Test-Path -LiteralPath $filePath -PathType Leaf)) {
            throw "Package verification failed. Missing file: $relativePath"
        }
        $actualHash = (Get-FileHash -LiteralPath $filePath -Algorithm SHA256).Hash
        if (-not $actualHash.Equals($expectedHash, [StringComparison]::OrdinalIgnoreCase)) {
            throw "Package verification failed. Damaged or changed file: $relativePath"
        }
    }
    Write-Check "Installer package checksums are valid."
}

function Test-FreeSpace {
    $root = [IO.Path]::GetPathRoot($AppDirectory)
    $driveName = $root.TrimEnd("\").TrimEnd(":")
    $drive = Get-PSDrive -Name $driveName -ErrorAction Stop
    if ($drive.Free -lt $MinimumFreeBytes) {
        $availableGb = [Math]::Round($drive.Free / 1GB, 1)
        throw "At least 6 GB of free disk space is required. Available: $availableGb GB."
    }
    Write-Check ("Disk space verified ({0:N1} GB free)." -f ($drive.Free / 1GB))
}

function Copy-ApplicationPayload {
    $sourceFull = [IO.Path]::GetFullPath($SourceDirectory).TrimEnd("\")
    $targetFull = [IO.Path]::GetFullPath($AppDirectory).TrimEnd("\")
    if ($sourceFull.Equals($targetFull, [StringComparison]::OrdinalIgnoreCase)) {
        Write-Check "Application files are already in the installed location."
        return
    }

    Write-Step "Installing application files"
    New-Item -ItemType Directory -Path $AppDirectory -Force | Out-Null
    foreach ($relativePath in @(
        "app", "database", "services", "scripts", "docs", "config.py", "main.py",
        "wsp_launcher.pyw", "requirements.txt", "requirements.lock.txt",
        "pyproject.toml", "README.md", "TASK_CHECKLIST.md", "version.txt", "INSTALL_WSP.bat",
        "LAUNCH_WSP.bat", "UPDATE_WSP.bat", "UNINSTALL_WSP.bat"
    )) {
        $source = Join-Path $SourceDirectory $relativePath
        if (-not (Test-Path -LiteralPath $source)) {
            continue
        }
        $destination = Join-Path $AppDirectory $relativePath
        if ((Get-Item -LiteralPath $source).PSIsContainer) {
            New-Item -ItemType Directory -Path $destination -Force | Out-Null
            Get-ChildItem -LiteralPath $source -Force | Copy-Item -Destination $destination -Recurse -Force
        }
        else {
            $parent = Split-Path -Parent $destination
            New-Item -ItemType Directory -Path $parent -Force | Out-Null
            Copy-Item -LiteralPath $source -Destination $destination -Force
        }
    }
    Write-Check "Application files installed to $AppDirectory"
}

function Test-PythonCandidate {
    param([string]$Executable, [string[]]$PrefixArguments = @())
    try {
        $versionText = & $Executable @PrefixArguments -c "import sys; print('.'.join(map(str, sys.version_info[:3])))" 2>$null
        if ($LASTEXITCODE -ne 0 -or -not $versionText) { return $null }
        $version = [Version]($versionText | Select-Object -Last 1)
        if ($version -lt $MinimumPython -or $version.Major -ne 3 -or $version.Minor -gt 13) { return $null }
        return [pscustomobject]@{ Executable = $Executable; PrefixArguments = $PrefixArguments; Version = $version }
    }
    catch { return $null }
}

function Find-CompatiblePython {
    if (Test-Path -LiteralPath $VenvPython) {
        $candidate = Test-PythonCandidate -Executable $VenvPython
        if ($candidate) { return $candidate }
    }
    $pyLauncher = Get-Command "py.exe" -ErrorAction SilentlyContinue
    if ($pyLauncher) {
        foreach ($selector in @("-3.12", "-3.13", "-3.11")) {
            $candidate = Test-PythonCandidate -Executable $pyLauncher.Source -PrefixArguments @($selector)
            if ($candidate) { return $candidate }
        }
    }
    foreach ($commandName in @("python.exe", "python3.exe")) {
        $command = Get-Command $commandName -ErrorAction SilentlyContinue
        if ($command) {
            $candidate = Test-PythonCandidate -Executable $command.Source
            if ($candidate) { return $candidate }
        }
    }
    foreach ($path in @(
        (Join-Path $env:LOCALAPPDATA "Programs\Python\Python312\python.exe"),
        (Join-Path $env:LOCALAPPDATA "Programs\Python\Python313\python.exe"),
        (Join-Path $env:LOCALAPPDATA "Programs\Python\Python311\python.exe")
    )) {
        if (Test-Path -LiteralPath $path) {
            $candidate = Test-PythonCandidate -Executable $path
            if ($candidate) { return $candidate }
        }
    }
    return $null
}

function Install-Python {
    Write-Step "Installing Python $PreferredPython for the current user"
    $winget = Get-Command "winget.exe" -ErrorAction SilentlyContinue
    if (-not $winget) {
        throw "Python 3.11+ is missing and winget is unavailable. Install 64-bit Python 3.12 from python.org, enable Add Python to PATH, then run the installer again."
    }
    & $winget.Source install --id "Python.Python.$PreferredPython" --exact --source winget --scope user --accept-package-agreements --accept-source-agreements --silent
    if ($LASTEXITCODE -ne 0) {
        throw "winget could not install Python $PreferredPython (exit code $LASTEXITCODE)."
    }
}

function Invoke-Checked {
    param([string]$FilePath, [string[]]$Arguments, [string]$FailureMessage)
    & $FilePath @Arguments
    if ($LASTEXITCODE -ne 0) { throw "$FailureMessage (exit code $LASTEXITCODE)." }
}

function Remove-BrokenVirtualEnvironment {
    $resolvedApp = [IO.Path]::GetFullPath($AppDirectory).TrimEnd("\")
    $resolvedEnvironment = [IO.Path]::GetFullPath($VirtualEnvironment)
    if (-not $resolvedEnvironment.StartsWith("$resolvedApp\", [StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to remove a virtual environment outside the application folder: $resolvedEnvironment"
    }
    if ((Split-Path -Leaf $resolvedEnvironment) -ne ".venv") {
        throw "Unexpected virtual environment path: $resolvedEnvironment"
    }
    Remove-Item -LiteralPath $VirtualEnvironment -Recurse -Force
}

function New-Shortcut {
    param(
        [string]$ShortcutPath,
        [string]$TargetPath,
        [string]$Arguments = "",
        [string]$Description = "WSP Offline System"
    )
    $parent = Split-Path -Parent $ShortcutPath
    New-Item -ItemType Directory -Path $parent -Force | Out-Null
    $shell = New-Object -ComObject WScript.Shell
    $shortcut = $shell.CreateShortcut($ShortcutPath)
    $shortcut.TargetPath = $TargetPath
    $shortcut.Arguments = $Arguments
    $shortcut.WorkingDirectory = $AppDirectory
    $shortcut.Description = $Description
    if (Test-Path -LiteralPath $ShortcutIcon) { $shortcut.IconLocation = "$ShortcutIcon,0" }
    $shortcut.Save()
}

function Write-InstallManifest {
    $version = (Get-Content -LiteralPath (Join-Path $AppDirectory "version.txt") -Raw).Trim()
    $manifest = [ordered]@{
        product = "WSP Offline System"
        version = $version
        installed_at = (Get-Date).ToString("o")
        install_directory = $AppDirectory
        python = (& $VenvPython -c "import platform; print(platform.python_version())")
        verification = "passed"
    }
    $manifest | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $DataDirectory "install_manifest.json") -Encoding Utf8
}

try {
    Write-Host ""
    Write-Host "WSP Offline System - verified one-click setup" -ForegroundColor White
    Write-Host "Source folder:  $SourceDirectory"
    Write-Host "Install folder: $AppDirectory"

    Write-Step "Running pre-installation checks"
    if ($env:OS -ne "Windows_NT") { throw "This installer supports Windows 10 and Windows 11 only." }
    if (-not [Environment]::Is64BitOperatingSystem) { throw "A 64-bit version of Windows is required." }
    Assert-SafeInstallPath
    Assert-SourcePayload
    Test-PackageIntegrity
    Test-FreeSpace
    Copy-ApplicationPayload

    New-Item -ItemType Directory -Path $DataDirectory -Force | Out-Null
    Start-Transcript -Path $LogPath -Append | Out-Null
    $TranscriptStarted = $true
    Write-Host "Detailed log: $LogPath"

    $python = Find-CompatiblePython
    if (-not $python) {
        Install-Python
        $python = Find-CompatiblePython
    }
    if (-not $python) {
        throw "Python installation completed, but Python could not be found. Restart Windows and run the installer again."
    }
    Write-Check "Python $($python.Version) is compatible."

    Write-Step "Creating the private application environment"
    if ((Test-Path -LiteralPath $VenvPython) -and -not (Test-PythonCandidate -Executable $VenvPython)) {
        Write-Host "The existing environment is invalid and will be rebuilt." -ForegroundColor Yellow
        Remove-BrokenVirtualEnvironment
    }
    if (-not (Test-Path -LiteralPath $VenvPython)) {
        $venvArguments = @($python.PrefixArguments) + @("-m", "venv", $VirtualEnvironment)
        Invoke-Checked -FilePath $python.Executable -Arguments $venvArguments -FailureMessage "Could not create the private Python environment"
    }
    Write-Check "Private Python environment is ready."

    if (-not $SkipDependencies) {
        Write-Step "Installing and validating required packages"
        Invoke-Checked -FilePath $VenvPython -Arguments @("-m", "pip", "install", "--disable-pip-version-check", "--upgrade", "pip", "setuptools", "wheel") -FailureMessage "Could not update pip"
        Invoke-Checked -FilePath $VenvPython -Arguments @("-m", "pip", "install", "--disable-pip-version-check", "--requirement", $Requirements) -FailureMessage "Could not install WSP requirements"
        Invoke-Checked -FilePath $VenvPython -Arguments @("-m", "pip", "check") -FailureMessage "Package compatibility verification failed"
        Write-Check "All required packages are installed and compatible."
    }
    else { Write-Host "[SKIP] Dependency installation was skipped." -ForegroundColor Yellow }

    if (-not $SkipModel) {
        Write-Step "Downloading and validating the offline AI search model"
        New-Item -ItemType Directory -Path $ModelDirectory -Force | Out-Null
        $previousHfHome = $env:HF_HOME
        try {
            $env:HF_HOME = $ModelDirectory
            Invoke-Checked -FilePath $VenvPython -Arguments @((Join-Path $AppDirectory "scripts\download_mxbai.py")) -FailureMessage "Could not download or verify the offline AI model"
        }
        finally { $env:HF_HOME = $previousHfHome }
        Write-Check "Offline AI model is installed and can create embeddings."
    }
    else { Write-Host "[SKIP] AI model installation was skipped." -ForegroundColor Yellow }

    Write-Step "Preparing data, import, and export folders"
    $ImportDirectory = Join-Path $InstallRoot "Import Folder"
    $ExportDirectory = Join-Path $InstallRoot "Export Folder"
    foreach ($directory in @(
        $ImportDirectory, (Join-Path $ImportDirectory "archive"), $ExportDirectory,
        (Join-Path $DataDirectory "backups"), (Join-Path $DataDirectory "logs"),
        (Join-Path $DataDirectory "semantic_index")
    )) { New-Item -ItemType Directory -Path $directory -Force | Out-Null }
    Write-Check "Import and export folders are ready."

    try {
        & $VenvPython (Join-Path $AppDirectory "scripts\create_shortcut_icon.py") | Out-Null
        if ($LASTEXITCODE -ne 0) { throw "Icon generator failed." }
    }
    catch { Write-Host "[WARN] The branded icon could not be created; installation will continue." -ForegroundColor Yellow }

    Write-Step "Running the final application verification"
    $verifyArguments = @((Join-Path $AppDirectory "scripts\verify_install.py"))
    if ($SkipModel) { $verifyArguments += "--skip-model" }
    Invoke-Checked -FilePath $VenvPython -Arguments $verifyArguments -FailureMessage "Final application verification failed"
    Write-Check "Database, imports, web application, and local runtime passed verification."

    if (-not $SkipShortcuts) {
        Write-Step "Creating Desktop and Start Menu shortcuts"
        $DesktopDirectory = [Environment]::GetFolderPath("Desktop")
        $ProgramsDirectory = [Environment]::GetFolderPath("Programs")
        if (-not $DesktopDirectory -or -not $ProgramsDirectory) { throw "Windows shortcut folders could not be located." }
        $StartMenuDirectory = Join-Path $ProgramsDirectory "WSP Offline System"
        New-Shortcut -ShortcutPath (Join-Path $DesktopDirectory "WSP Offline System.lnk") -TargetPath $VenvPythonw -Arguments "`"$Launcher`"" -Description "Open WSP Offline System"
        New-Shortcut -ShortcutPath (Join-Path $DesktopDirectory "WSP Import Folder.lnk") -TargetPath "$env:WINDIR\explorer.exe" -Arguments "`"$ImportDirectory`"" -Description "Open the WSP Excel import folder"
        New-Shortcut -ShortcutPath (Join-Path $StartMenuDirectory "WSP Offline System.lnk") -TargetPath $VenvPythonw -Arguments "`"$Launcher`"" -Description "Open WSP Offline System"
        New-Shortcut -ShortcutPath (Join-Path $StartMenuDirectory "WSP Import Folder.lnk") -TargetPath "$env:WINDIR\explorer.exe" -Arguments "`"$ImportDirectory`"" -Description "Open the WSP Excel import folder"
        New-Shortcut -ShortcutPath (Join-Path $StartMenuDirectory "Update or Repair WSP.lnk") -TargetPath (Join-Path $AppDirectory "UPDATE_WSP.bat") -Description "Update or repair WSP Offline System"
        New-Shortcut -ShortcutPath (Join-Path $StartMenuDirectory "Uninstall WSP.lnk") -TargetPath (Join-Path $AppDirectory "UNINSTALL_WSP.bat") -Description "Uninstall WSP Offline System"
        Write-Check "Desktop and Start Menu shortcuts were created."
    }
    else { Write-Host "[SKIP] Shortcut creation was skipped." -ForegroundColor Yellow }

    Write-InstallManifest
    Write-Step "Installation verified successfully"
    Write-Host "Installed at: $AppDirectory" -ForegroundColor White
    Write-Host "Import Excel files here: $ImportDirectory" -ForegroundColor White
    Write-Host "You can safely delete the extracted installer folder now." -ForegroundColor White

    if (-not $NoLaunch) {
        Write-Host "Starting WSP Offline System..."
        Start-Process -FilePath $VenvPythonw -ArgumentList "`"$Launcher`"" -WorkingDirectory $AppDirectory -WindowStyle Hidden
    }

    if ($TranscriptStarted) { Stop-Transcript | Out-Null; $TranscriptStarted = $false }
    exit 0
}
catch {
    Write-Host ""
    Write-Host "INSTALLATION ERROR: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Detailed log (when available): $LogPath" -ForegroundColor Yellow
    if ($TranscriptStarted) { try { Stop-Transcript | Out-Null } catch {} }
    exit 1
}
