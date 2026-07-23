[CmdletBinding()]
param(
    [switch]$SkipDependencies,
    [switch]$SkipModel,
    [switch]$SkipShortcuts,
    [switch]$NoLaunch
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

$AppDirectory = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
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

New-Item -ItemType Directory -Path $DataDirectory -Force | Out-Null
Start-Transcript -Path $LogPath -Append | Out-Null

function Write-Step {
    param([string]$Message)
    Write-Host ""
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Test-PythonCandidate {
    param([string]$Executable, [string[]]$PrefixArguments = @())

    try {
        $versionText = & $Executable @PrefixArguments -c "import sys; print('.'.join(map(str, sys.version_info[:3])))" 2>$null
        if ($LASTEXITCODE -ne 0 -or -not $versionText) {
            return $null
        }
        $version = [Version]($versionText | Select-Object -Last 1)
        if ($version -lt $MinimumPython) {
            return $null
        }
        return [pscustomobject]@{
            Executable = $Executable
            PrefixArguments = $PrefixArguments
            Version = $version
        }
    }
    catch {
        return $null
    }
}

function Find-CompatiblePython {
    if (Test-Path -LiteralPath $VenvPython) {
        $existingEnvironmentPython = Test-PythonCandidate -Executable $VenvPython
        if ($existingEnvironmentPython) {
            return $existingEnvironmentPython
        }
    }

    $pyLauncher = Get-Command "py.exe" -ErrorAction SilentlyContinue
    if ($pyLauncher) {
        foreach ($selector in @("-3.12", "-3.13", "-3.11")) {
            $candidate = Test-PythonCandidate -Executable $pyLauncher.Source -PrefixArguments @($selector)
            if ($candidate) {
                return $candidate
            }
        }
    }

    foreach ($commandName in @("python.exe", "python3.exe")) {
        $command = Get-Command $commandName -ErrorAction SilentlyContinue
        if ($command) {
            $candidate = Test-PythonCandidate -Executable $command.Source
            if ($candidate) {
                return $candidate
            }
        }
    }

    $knownPaths = @(
        (Join-Path $env:LOCALAPPDATA "Programs\Python\Python312\python.exe"),
        (Join-Path $env:LOCALAPPDATA "Programs\Python\Python313\python.exe"),
        (Join-Path $env:LOCALAPPDATA "Programs\Python\Python311\python.exe")
    )
    foreach ($path in $knownPaths) {
        if (Test-Path -LiteralPath $path) {
            $candidate = Test-PythonCandidate -Executable $path
            if ($candidate) {
                return $candidate
            }
        }
    }
    return $null
}

function Install-Python {
    Write-Step "Python 3.11+ was not found; installing Python $PreferredPython for this user"
    $winget = Get-Command "winget.exe" -ErrorAction SilentlyContinue
    if (-not $winget) {
        Start-Process "https://www.python.org/downloads/windows/"
        throw "Python is missing and Windows Package Manager (winget) is unavailable. Install 64-bit Python 3.11 or 3.12 from python.org, select 'Add python.exe to PATH', then run INSTALL_WSP.bat again."
    }

    & $winget.Source install --id "Python.Python.$PreferredPython" --exact --source winget --scope user --accept-package-agreements --accept-source-agreements --silent
    if ($LASTEXITCODE -ne 0) {
        throw "winget could not install Python $PreferredPython (exit code $LASTEXITCODE)."
    }
}

function Invoke-Checked {
    param(
        [string]$FilePath,
        [string[]]$Arguments,
        [string]$FailureMessage
    )
    & $FilePath @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "$FailureMessage (exit code $LASTEXITCODE)."
    }
}

function New-WspShortcut {
    param([string]$ShortcutPath)

    $shell = New-Object -ComObject WScript.Shell
    $shortcut = $shell.CreateShortcut($ShortcutPath)
    $shortcut.TargetPath = $VenvPythonw
    $shortcut.Arguments = "`"$Launcher`""
    $shortcut.WorkingDirectory = $AppDirectory
    $shortcut.Description = "Open the WSP Offline System"
    if (Test-Path -LiteralPath $ShortcutIcon) {
        $shortcut.IconLocation = "$ShortcutIcon,0"
    }
    else {
        $shortcut.IconLocation = "$VenvPythonw,0"
    }
    $shortcut.Save()
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
    Remove-Item -LiteralPath $resolvedEnvironment -Recurse -Force
}

try {
    Write-Host ""
    Write-Host "WSP Offline System setup" -ForegroundColor White
    Write-Host "Application folder: $AppDirectory"
    Write-Host "Detailed log:      $LogPath"

    if (-not (Test-Path -LiteralPath $Requirements)) {
        throw "requirements.txt was not found in $AppDirectory."
    }
    if (-not (Test-Path -LiteralPath $Launcher)) {
        throw "wsp_launcher.pyw was not found in $AppDirectory."
    }

    $python = Find-CompatiblePython
    if (-not $python) {
        Install-Python
        $python = Find-CompatiblePython
    }
    if (-not $python) {
        throw "Python installation finished, but a compatible Python executable still could not be found. Restart Windows and run INSTALL_WSP.bat again."
    }
    Write-Host "[OK] Python $($python.Version) found." -ForegroundColor Green

    Write-Step "Creating the private Python environment"
    if ((Test-Path -LiteralPath $VenvPython) -and -not (Test-PythonCandidate -Executable $VenvPython)) {
        Write-Host "The existing environment is broken or belongs to another computer. Rebuilding it..." -ForegroundColor Yellow
        Remove-BrokenVirtualEnvironment
    }
    if (-not (Test-Path -LiteralPath $VenvPython)) {
        $venvArguments = @($python.PrefixArguments) + @("-m", "venv", $VirtualEnvironment)
        Invoke-Checked -FilePath $python.Executable -Arguments $venvArguments -FailureMessage "Could not create the WSP virtual environment"
        Write-Host "[OK] Created $VirtualEnvironment" -ForegroundColor Green
    }
    else {
        Write-Host "[OK] Existing environment found; it will be repaired in place." -ForegroundColor Green
    }

    if (-not $SkipDependencies) {
        Write-Step "Installing all required packages (the first run can take a while)"
        Invoke-Checked -FilePath $VenvPython -Arguments @("-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel") -FailureMessage "Could not update the Python package installer"
        Invoke-Checked -FilePath $VenvPython -Arguments @("-m", "pip", "install", "--requirement", $Requirements) -FailureMessage "Could not install WSP requirements"
        Invoke-Checked -FilePath $VenvPython -Arguments @("-m", "pip", "check") -FailureMessage "Installed package compatibility check failed"
        Write-Host "[OK] Python packages are installed and compatible." -ForegroundColor Green
    }
    else {
        Write-Host "[SKIP] Dependency installation was skipped." -ForegroundColor Yellow
    }

    if (-not $SkipModel) {
        Write-Step "Installing the local AI search model (about 670 MB)"
        New-Item -ItemType Directory -Path $ModelDirectory -Force | Out-Null
        $previousHfHome = $env:HF_HOME
        try {
            $env:HF_HOME = $ModelDirectory
            Invoke-Checked -FilePath $VenvPython -Arguments @((Join-Path $PSScriptRoot "download_mxbai.py")) -FailureMessage "Could not download or verify the local AI model"
        }
        finally {
            $env:HF_HOME = $previousHfHome
        }
        Write-Host "[OK] Local AI model is ready in $ModelDirectory" -ForegroundColor Green
    }
    else {
        Write-Host "[SKIP] AI model installation was skipped." -ForegroundColor Yellow
    }

    Write-Step "Preparing WSP folders"
    $WorkspaceDirectory = Split-Path -Parent $AppDirectory
    $ImportDirectory = Join-Path $WorkspaceDirectory "Import Folder"
    $ExportDirectory = Join-Path $WorkspaceDirectory "Export Folder"
    foreach ($directory in @(
        $ImportDirectory,
        (Join-Path $ImportDirectory "archive"),
        $ExportDirectory,
        (Join-Path $DataDirectory "backups"),
        (Join-Path $DataDirectory "logs"),
        (Join-Path $DataDirectory "semantic_index")
    )) {
        New-Item -ItemType Directory -Path $directory -Force | Out-Null
    }
    Write-Host "[OK] Import Folder: $ImportDirectory" -ForegroundColor Green
    Write-Host "[OK] Export Folder: $ExportDirectory" -ForegroundColor Green
    try {
        & $VenvPython (Join-Path $PSScriptRoot "create_shortcut_icon.py") | Out-Null
        if ($LASTEXITCODE -ne 0) {
            throw "Icon generator returned exit code $LASTEXITCODE."
        }
        Write-Host "[OK] Desktop icon artwork prepared." -ForegroundColor Green
    }
    catch {
        Write-Host "[WARN] Could not prepare the branded icon; Windows will use the Python application icon." -ForegroundColor Yellow
    }

    if (-not $SkipShortcuts) {
        Write-Step "Creating Desktop and Start Menu shortcuts"
        $DesktopDirectory = [Environment]::GetFolderPath("Desktop")
        $ProgramsDirectory = [Environment]::GetFolderPath("Programs")
        if (-not $DesktopDirectory) {
            throw "Windows did not return a Desktop folder path."
        }
        if (-not $ProgramsDirectory) {
            throw "Windows did not return a Start Menu Programs folder path."
        }
        $DesktopShortcut = Join-Path $DesktopDirectory "WSP Offline System.lnk"
        $StartMenuShortcut = Join-Path $ProgramsDirectory "WSP Offline System.lnk"
        New-WspShortcut -ShortcutPath $DesktopShortcut
        New-WspShortcut -ShortcutPath $StartMenuShortcut
        Write-Host "[OK] Desktop shortcut: $DesktopShortcut" -ForegroundColor Green
        Write-Host "[OK] Start Menu shortcut: $StartMenuShortcut" -ForegroundColor Green
    }
    else {
        Write-Host "[SKIP] Shortcut creation was skipped." -ForegroundColor Yellow
    }

    Write-Step "Installation complete"
    Write-Host "Place the newest .xlsx or .xlsm file in:" -ForegroundColor White
    Write-Host "  $ImportDirectory" -ForegroundColor White
    Write-Host ""
    Write-Host "Open the app with the 'WSP Offline System' desktop shortcut." -ForegroundColor White

    if (-not $NoLaunch) {
        Write-Host "Starting WSP Offline System..."
        Start-Process -FilePath $VenvPythonw -ArgumentList "`"$Launcher`"" -WorkingDirectory $AppDirectory
    }

    Stop-Transcript | Out-Null
    exit 0
}
catch {
    Write-Host ""
    Write-Host "INSTALLATION ERROR: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Detailed log: $LogPath" -ForegroundColor Yellow
    try { Stop-Transcript | Out-Null } catch {}
    exit 1
}
