[CmdletBinding()]
param(
    [switch]$Preview,
    [string]$CapturePath
)

$ErrorActionPreference = "Stop"
$ScriptDirectory = Split-Path -Parent $MyInvocation.MyCommand.Path
$AppSourceDirectory = [IO.Path]::GetFullPath((Join-Path $ScriptDirectory ".."))
$InstallerScript = Join-Path $ScriptDirectory "install.ps1"
$LogoPath = Join-Path $AppSourceDirectory "app\static\aub-logo-horizontal.png"
$IconPath = Join-Path $AppSourceDirectory "app\static\wsp.ico"
$InstalledAppDirectory = Join-Path $env:LOCALAPPDATA "WSP Offline System\wsp_offline_app"
$InstalledPythonw = Join-Path $InstalledAppDirectory ".venv\Scripts\pythonw.exe"
$InstalledLauncher = Join-Path $InstalledAppDirectory "wsp_launcher.pyw"
$UiTempDirectory = Join-Path $env:TEMP ("wsp_installer_ui_" + [guid]::NewGuid().ToString("N"))
$StdoutPath = Join-Path $UiTempDirectory "setup-output.log"
$StderrPath = Join-Path $UiTempDirectory "setup-errors.log"
$script:InstallProcess = $null
$script:InstallRunning = $false
$script:InstallerExitCode = 1
$script:LastOutput = ""

try {
    Add-Type -AssemblyName PresentationFramework, PresentationCore, WindowsBase
}
catch {
    Write-Error "The graphical installer is unavailable: $($_.Exception.Message)"
    exit 60
}

[xml]$Xaml = @'
<Window xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        Title="WSP Offline System Setup"
        Width="960" Height="650" MinWidth="960" MinHeight="650"
        WindowStartupLocation="CenterScreen" ResizeMode="NoResize"
        Background="#F4F6FA" FontFamily="Segoe UI" Icon="{x:Null}">
  <Window.Resources>
    <LinearGradientBrush x:Key="BrandGradient" StartPoint="0,0" EndPoint="1,1">
      <GradientStop Color="#111A2E" Offset="0"/>
      <GradientStop Color="#19243D" Offset="0.52"/>
      <GradientStop Color="#65002E" Offset="1"/>
    </LinearGradientBrush>
    <Style x:Key="PrimaryButton" TargetType="Button">
      <Setter Property="Background" Value="#8A002F"/>
      <Setter Property="Foreground" Value="White"/>
      <Setter Property="BorderThickness" Value="0"/>
      <Setter Property="FontWeight" Value="SemiBold"/>
      <Setter Property="FontSize" Value="14"/>
      <Setter Property="Height" Value="42"/>
      <Setter Property="Padding" Value="22,0"/>
      <Setter Property="Cursor" Value="Hand"/>
      <Setter Property="Template">
        <Setter.Value>
          <ControlTemplate TargetType="Button">
            <Border x:Name="ButtonBorder" Background="{TemplateBinding Background}" CornerRadius="8">
              <ContentPresenter HorizontalAlignment="Center" VerticalAlignment="Center"/>
            </Border>
            <ControlTemplate.Triggers>
              <Trigger Property="IsMouseOver" Value="True"><Setter TargetName="ButtonBorder" Property="Background" Value="#A30A43"/></Trigger>
              <Trigger Property="IsEnabled" Value="False"><Setter TargetName="ButtonBorder" Property="Opacity" Value="0.48"/></Trigger>
            </ControlTemplate.Triggers>
          </ControlTemplate>
        </Setter.Value>
      </Setter>
    </Style>
    <Style x:Key="SecondaryButton" TargetType="Button" BasedOn="{StaticResource PrimaryButton}">
      <Setter Property="Background" Value="#E9EDF4"/>
      <Setter Property="Foreground" Value="#27344B"/>
      <Setter Property="Template">
        <Setter.Value>
          <ControlTemplate TargetType="Button">
            <Border x:Name="ButtonBorder" Background="{TemplateBinding Background}" CornerRadius="8" BorderBrush="#D7DDE8" BorderThickness="1">
              <ContentPresenter HorizontalAlignment="Center" VerticalAlignment="Center"/>
            </Border>
            <ControlTemplate.Triggers>
              <Trigger Property="IsMouseOver" Value="True"><Setter TargetName="ButtonBorder" Property="Background" Value="#DDE3ED"/></Trigger>
              <Trigger Property="IsEnabled" Value="False"><Setter TargetName="ButtonBorder" Property="Opacity" Value="0.48"/></Trigger>
            </ControlTemplate.Triggers>
          </ControlTemplate>
        </Setter.Value>
      </Setter>
    </Style>
  </Window.Resources>

  <Grid>
    <Grid.ColumnDefinitions><ColumnDefinition Width="320"/><ColumnDefinition Width="*"/></Grid.ColumnDefinitions>

    <Border Grid.Column="0" Background="{StaticResource BrandGradient}">
      <Grid Margin="34,34,34,30">
        <Grid.RowDefinitions><RowDefinition Height="Auto"/><RowDefinition Height="*"/><RowDefinition Height="Auto"/></Grid.RowDefinitions>
        <Border Background="White" CornerRadius="12" Padding="16" Height="104" VerticalAlignment="Top">
          <Image x:Name="AubLogo" Stretch="Uniform"/>
        </Border>
        <StackPanel Grid.Row="1" VerticalAlignment="Center">
          <Border Background="#33FFFFFF" BorderBrush="#55FFFFFF" BorderThickness="1" CornerRadius="12" Padding="11,6" HorizontalAlignment="Left" Margin="0,0,0,18">
            <TextBlock Text="WORK STUDY PROGRAM" Foreground="#FFE4EE" FontSize="11" FontWeight="Bold"/>
          </Border>
          <TextBlock Text="Student intelligence, ready for work." Foreground="White" FontSize="29" FontWeight="Bold" TextWrapping="Wrap" LineHeight="36"/>
          <TextBlock Text="A secure local workspace for reviewing applicants, searching skills, importing Excel data, and managing placements." Foreground="#D8DFEC" FontSize="14" TextWrapping="Wrap" LineHeight="22" Margin="0,17,0,0"/>
          <StackPanel Margin="0,28,0,0">
            <TextBlock Text="OK  Private installation for this computer" Foreground="#EDF2F8" FontSize="13" Margin="0,0,0,10"/>
            <TextBlock Text="OK  Offline semantic search model" Foreground="#EDF2F8" FontSize="13" Margin="0,0,0,10"/>
            <TextBlock Text="OK  Desktop and Start Menu shortcuts" Foreground="#EDF2F8" FontSize="13"/>
          </StackPanel>
        </StackPanel>
        <StackPanel Grid.Row="2">
          <TextBlock Text="AMERICAN UNIVERSITY OF BEIRUT" Foreground="#F6D8E3" FontWeight="SemiBold" FontSize="11"/>
          <TextBlock Text="Windows 10/11 | 64-bit | Local installation" Foreground="#AEB9CA" FontSize="11" Margin="0,5,0,0"/>
        </StackPanel>
      </Grid>
    </Border>

    <Grid Grid.Column="1" Margin="42,34,42,30">
      <Grid.RowDefinitions><RowDefinition Height="Auto"/><RowDefinition Height="Auto"/><RowDefinition Height="*"/><RowDefinition Height="Auto"/></Grid.RowDefinitions>

      <Grid>
        <Grid.ColumnDefinitions><ColumnDefinition Width="*"/><ColumnDefinition Width="Auto"/></Grid.ColumnDefinitions>
        <StackPanel>
          <TextBlock Text="WSP Offline System" Foreground="#8A002F" FontSize="12" FontWeight="Bold"/>
          <TextBlock x:Name="InstallerTitle" Text="Preparing your installation" Foreground="#111A2E" FontSize="27" FontWeight="Bold" Margin="0,5,0,0"/>
          <TextBlock x:Name="InstallerSubtitle" Text="Setup will verify this computer and install every required component." Foreground="#68758B" FontSize="13" Margin="0,8,0,0"/>
        </StackPanel>
        <Border Grid.Column="1" x:Name="StatusPill" Background="#FDEAF1" CornerRadius="14" Padding="13,7" VerticalAlignment="Top">
          <TextBlock x:Name="StatusText" Text="STARTING" Foreground="#8A002F" FontSize="11" FontWeight="Bold"/>
        </Border>
      </Grid>

      <StackPanel Grid.Row="1" Margin="0,24,0,20">
        <ProgressBar x:Name="InstallProgress" Height="7" Minimum="0" Maximum="100" Value="8" Foreground="#A0003A" Background="#E1E6EF" BorderThickness="0"/>
        <Grid Margin="0,9,0,0">
          <TextBlock x:Name="ProgressDetail" Text="Starting verified setup..." Foreground="#4D5B72" FontSize="12"/>
          <TextBlock x:Name="ProgressStep" Text="Step 1 of 6" Foreground="#8B96A8" FontSize="12" HorizontalAlignment="Right"/>
        </Grid>
      </StackPanel>

      <Grid Grid.Row="2">
        <Grid.RowDefinitions>
          <RowDefinition Height="Auto"/><RowDefinition Height="Auto"/><RowDefinition Height="Auto"/>
          <RowDefinition Height="Auto"/><RowDefinition Height="Auto"/><RowDefinition Height="Auto"/><RowDefinition Height="*"/>
        </Grid.RowDefinitions>

        <Grid x:Name="Step1" Grid.Row="0" Margin="0,0,0,11">
          <Grid.ColumnDefinitions><ColumnDefinition Width="34"/><ColumnDefinition Width="*"/></Grid.ColumnDefinitions>
          <Border x:Name="Step1Marker" Width="24" Height="24" CornerRadius="12" Background="#8A002F" VerticalAlignment="Center"><TextBlock x:Name="Step1Mark" Text="1" Foreground="White" HorizontalAlignment="Center" VerticalAlignment="Center" FontSize="11" FontWeight="Bold"/></Border>
          <StackPanel Grid.Column="1"><TextBlock x:Name="Step1Title" Text="Check this computer" Foreground="#18233A" FontSize="14" FontWeight="SemiBold"/><TextBlock x:Name="Step1Detail" Text="Windows, package integrity, and available space" Foreground="#7A8699" FontSize="11" Margin="0,2,0,0"/></StackPanel>
        </Grid>
        <Grid x:Name="Step2" Grid.Row="1" Margin="0,0,0,11">
          <Grid.ColumnDefinitions><ColumnDefinition Width="34"/><ColumnDefinition Width="*"/></Grid.ColumnDefinitions>
          <Border x:Name="Step2Marker" Width="24" Height="24" CornerRadius="12" Background="#E1E6EE" VerticalAlignment="Center"><TextBlock x:Name="Step2Mark" Text="2" Foreground="#718096" HorizontalAlignment="Center" VerticalAlignment="Center" FontSize="11" FontWeight="Bold"/></Border>
          <StackPanel Grid.Column="1"><TextBlock x:Name="Step2Title" Text="Install application files" Foreground="#5F6C80" FontSize="14" FontWeight="SemiBold"/><TextBlock x:Name="Step2Detail" Text="Copy the verified WSP application into Local AppData" Foreground="#929CAC" FontSize="11" Margin="0,2,0,0"/></StackPanel>
        </Grid>
        <Grid x:Name="Step3" Grid.Row="2" Margin="0,0,0,11">
          <Grid.ColumnDefinitions><ColumnDefinition Width="34"/><ColumnDefinition Width="*"/></Grid.ColumnDefinitions>
          <Border x:Name="Step3Marker" Width="24" Height="24" CornerRadius="12" Background="#E1E6EE" VerticalAlignment="Center"><TextBlock x:Name="Step3Mark" Text="3" Foreground="#718096" HorizontalAlignment="Center" VerticalAlignment="Center" FontSize="11" FontWeight="Bold"/></Border>
          <StackPanel Grid.Column="1"><TextBlock x:Name="Step3Title" Text="Create private Python environment" Foreground="#5F6C80" FontSize="14" FontWeight="SemiBold"/><TextBlock x:Name="Step3Detail" Text="Keep WSP isolated from other software" Foreground="#929CAC" FontSize="11" Margin="0,2,0,0"/></StackPanel>
        </Grid>
        <Grid x:Name="Step4" Grid.Row="3" Margin="0,0,0,11">
          <Grid.ColumnDefinitions><ColumnDefinition Width="34"/><ColumnDefinition Width="*"/></Grid.ColumnDefinitions>
          <Border x:Name="Step4Marker" Width="24" Height="24" CornerRadius="12" Background="#E1E6EE" VerticalAlignment="Center"><TextBlock x:Name="Step4Mark" Text="4" Foreground="#718096" HorizontalAlignment="Center" VerticalAlignment="Center" FontSize="11" FontWeight="Bold"/></Border>
          <StackPanel Grid.Column="1"><TextBlock x:Name="Step4Title" Text="Install required packages" Foreground="#5F6C80" FontSize="14" FontWeight="SemiBold"/><TextBlock x:Name="Step4Detail" Text="Database, Excel, web UI, and local AI dependencies" Foreground="#929CAC" FontSize="11" Margin="0,2,0,0"/></StackPanel>
        </Grid>
        <Grid x:Name="Step5" Grid.Row="4" Margin="0,0,0,11">
          <Grid.ColumnDefinitions><ColumnDefinition Width="34"/><ColumnDefinition Width="*"/></Grid.ColumnDefinitions>
          <Border x:Name="Step5Marker" Width="24" Height="24" CornerRadius="12" Background="#E1E6EE" VerticalAlignment="Center"><TextBlock x:Name="Step5Mark" Text="5" Foreground="#718096" HorizontalAlignment="Center" VerticalAlignment="Center" FontSize="11" FontWeight="Bold"/></Border>
          <StackPanel Grid.Column="1"><TextBlock x:Name="Step5Title" Text="Prepare offline AI search" Foreground="#5F6C80" FontSize="14" FontWeight="SemiBold"/><TextBlock x:Name="Step5Detail" Text="Download and verify the local embedding model" Foreground="#929CAC" FontSize="11" Margin="0,2,0,0"/></StackPanel>
        </Grid>
        <Grid x:Name="Step6" Grid.Row="5" Margin="0,0,0,14">
          <Grid.ColumnDefinitions><ColumnDefinition Width="34"/><ColumnDefinition Width="*"/></Grid.ColumnDefinitions>
          <Border x:Name="Step6Marker" Width="24" Height="24" CornerRadius="12" Background="#E1E6EE" VerticalAlignment="Center"><TextBlock x:Name="Step6Mark" Text="6" Foreground="#718096" HorizontalAlignment="Center" VerticalAlignment="Center" FontSize="11" FontWeight="Bold"/></Border>
          <StackPanel Grid.Column="1"><TextBlock x:Name="Step6Title" Text="Verify and create shortcuts" Foreground="#5F6C80" FontSize="14" FontWeight="SemiBold"/><TextBlock x:Name="Step6Detail" Text="Run diagnostics and add Desktop/Start Menu access" Foreground="#929CAC" FontSize="11" Margin="0,2,0,0"/></StackPanel>
        </Grid>

        <Border Grid.Row="6" Background="#F0F3F8" BorderBrush="#E0E5ED" BorderThickness="1" CornerRadius="8" Padding="12" VerticalAlignment="Stretch">
          <TextBox x:Name="InstallLog" Background="Transparent" BorderThickness="0" Foreground="#566278" FontFamily="Consolas" FontSize="10.5" IsReadOnly="True" AcceptsReturn="True" TextWrapping="NoWrap" VerticalScrollBarVisibility="Auto" HorizontalScrollBarVisibility="Auto"/>
        </Border>
      </Grid>

      <Grid Grid.Row="3" Margin="0,20,0,0">
        <TextBlock x:Name="InstallLocation" Text="Installs privately under Local AppData" Foreground="#8994A6" FontSize="11" VerticalAlignment="Center"/>
        <StackPanel Orientation="Horizontal" HorizontalAlignment="Right">
          <Button x:Name="CloseButton" Content="Please wait..." Style="{StaticResource SecondaryButton}" IsEnabled="False" Margin="0,0,10,0"/>
          <Button x:Name="LaunchButton" Content="Launch WSP" Style="{StaticResource PrimaryButton}" Visibility="Collapsed"/>
        </StackPanel>
      </Grid>
    </Grid>
  </Grid>
</Window>
'@

$reader = New-Object System.Xml.XmlNodeReader $Xaml
$Window = [Windows.Markup.XamlReader]::Load($reader)

$ControlNames = @(
    "AubLogo", "InstallerTitle", "InstallerSubtitle", "StatusPill", "StatusText",
    "InstallProgress", "ProgressDetail", "ProgressStep", "InstallLog", "InstallLocation",
    "CloseButton", "LaunchButton"
)
foreach ($name in $ControlNames) { Set-Variable -Name $name -Value $Window.FindName($name) }
for ($index = 1; $index -le 6; $index++) {
    Set-Variable -Name "Step${index}Marker" -Value $Window.FindName("Step${index}Marker")
    Set-Variable -Name "Step${index}Mark" -Value $Window.FindName("Step${index}Mark")
    Set-Variable -Name "Step${index}Title" -Value $Window.FindName("Step${index}Title")
    Set-Variable -Name "Step${index}Detail" -Value $Window.FindName("Step${index}Detail")
}

try {
    $bitmap = New-Object Windows.Media.Imaging.BitmapImage
    $bitmap.BeginInit()
    $bitmap.CacheOption = [Windows.Media.Imaging.BitmapCacheOption]::OnLoad
    $bitmap.UriSource = New-Object Uri($LogoPath, [UriKind]::Absolute)
    $bitmap.EndInit()
    $AubLogo.Source = $bitmap
    if (Test-Path -LiteralPath $IconPath) {
        $Window.Icon = [Windows.Media.Imaging.BitmapFrame]::Create((New-Object Uri($IconPath, [UriKind]::Absolute)))
    }
}
catch {
    # Branding remains usable even if Windows cannot decode an image on a specific machine.
}

function New-SolidBrush([string]$Color) {
    return New-Object Windows.Media.SolidColorBrush ([Windows.Media.ColorConverter]::ConvertFromString($Color))
}

function Set-StepState {
    param([int]$Number, [ValidateSet("pending", "active", "complete", "failed")][string]$State)
    $marker = Get-Variable -Name "Step${Number}Marker" -ValueOnly
    $mark = Get-Variable -Name "Step${Number}Mark" -ValueOnly
    $title = Get-Variable -Name "Step${Number}Title" -ValueOnly
    $detail = Get-Variable -Name "Step${Number}Detail" -ValueOnly
    switch ($State) {
        "complete" {
            $marker.Background = New-SolidBrush "#138A68"
            $mark.Text = "OK"
            $mark.FontSize = 8
            $mark.Foreground = New-SolidBrush "#FFFFFF"
            $title.Foreground = New-SolidBrush "#18233A"
            $detail.Foreground = New-SolidBrush "#7A8699"
        }
        "active" {
            $marker.Background = New-SolidBrush "#8A002F"
            $mark.Text = [string]$Number
            $mark.FontSize = 11
            $mark.Foreground = New-SolidBrush "#FFFFFF"
            $title.Foreground = New-SolidBrush "#8A002F"
            $detail.Foreground = New-SolidBrush "#69768A"
        }
        "failed" {
            $marker.Background = New-SolidBrush "#B42318"
            $mark.Text = "!"
            $mark.FontSize = 11
            $mark.Foreground = New-SolidBrush "#FFFFFF"
            $title.Foreground = New-SolidBrush "#B42318"
        }
        default {
            $marker.Background = New-SolidBrush "#E1E6EE"
            $mark.Text = [string]$Number
            $mark.FontSize = 11
            $mark.Foreground = New-SolidBrush "#718096"
            $title.Foreground = New-SolidBrush "#5F6C80"
            $detail.Foreground = New-SolidBrush "#929CAC"
        }
    }
}

function Set-CurrentStage {
    param([int]$Stage, [string]$Message)
    for ($index = 1; $index -le 6; $index++) {
        if ($index -lt $Stage) { Set-StepState -Number $index -State "complete" }
        elseif ($index -eq $Stage) { Set-StepState -Number $index -State "active" }
        else { Set-StepState -Number $index -State "pending" }
    }
    $ProgressStep.Text = "Step $Stage of 6"
    $ProgressDetail.Text = $Message
    $InstallProgress.Value = [Math]::Min(92, 8 + (($Stage - 1) * 17))
}

function Get-CombinedOutput {
    $standard = if (Test-Path -LiteralPath $StdoutPath) { Get-Content -LiteralPath $StdoutPath -Raw -ErrorAction SilentlyContinue } else { "" }
    $errors = if (Test-Path -LiteralPath $StderrPath) { Get-Content -LiteralPath $StderrPath -Raw -ErrorAction SilentlyContinue } else { "" }
    return (($standard, $errors | Where-Object { $_ }) -join [Environment]::NewLine).Trim()
}

function Update-InstallerUi {
    $output = Get-CombinedOutput
    if ($output -and $output -ne $script:LastOutput) {
        $script:LastOutput = $output
        $InstallLog.Text = $output
        $InstallLog.ScrollToEnd()
    }

    if ($output -match "Creating Desktop and Start Menu shortcuts|Running the final application verification") {
        Set-CurrentStage 6 "Verifying the application and creating shortcuts..."
    }
    elseif ($output -match "Downloading and validating the offline AI search model") {
        Set-CurrentStage 5 "Preparing the offline AI model..."
    }
    elseif ($output -match "Installing and validating required packages") {
        Set-CurrentStage 4 "Installing verified application packages..."
    }
    elseif ($output -match "Creating the private application environment") {
        Set-CurrentStage 3 "Creating WSP's private environment..."
    }
    elseif ($output -match "Installing application files") {
        Set-CurrentStage 2 "Copying the WSP application..."
    }
    else {
        Set-CurrentStage 1 "Checking Windows, package integrity, and disk space..."
    }
}

function Complete-Installation {
    param([int]$ExitCode)
    $script:InstallRunning = $false
    $script:InstallerExitCode = $ExitCode
    Update-InstallerUi

    if ($ExitCode -eq 0) {
        for ($index = 1; $index -le 6; $index++) { Set-StepState -Number $index -State "complete" }
        $InstallProgress.Value = 100
        $InstallerTitle.Text = "WSP is ready to use"
        $InstallerSubtitle.Text = "Installation passed every verification check. Your Desktop shortcut is ready."
        $StatusPill.Background = New-SolidBrush "#E6F5EF"
        $StatusText.Foreground = New-SolidBrush "#087455"
        $StatusText.Text = "INSTALLED"
        $ProgressDetail.Text = "Installation and shortcut creation completed successfully."
        $ProgressStep.Text = "Complete"
        $CloseButton.Content = "Close"
        $CloseButton.IsEnabled = $true
        $LaunchButton.Visibility = "Visible"
    }
    else {
        Set-StepState -Number 6 -State "failed"
        $InstallerTitle.Text = "Setup needs attention"
        $InstallerSubtitle.Text = "The installation stopped safely. Review the details below, then run setup again."
        $StatusPill.Background = New-SolidBrush "#FDECEC"
        $StatusText.Foreground = New-SolidBrush "#B42318"
        $StatusText.Text = "NOT INSTALLED"
        $ProgressDetail.Text = "Installation did not complete. No success shortcut was created."
        $CloseButton.Content = "Close"
        $CloseButton.IsEnabled = $true
    }
}

function Start-Installation {
    New-Item -ItemType Directory -Path $UiTempDirectory -Force | Out-Null
    Set-Content -LiteralPath $StdoutPath -Value "" -Encoding Utf8
    Set-Content -LiteralPath $StderrPath -Value "" -Encoding Utf8
    Set-CurrentStage 1 "Checking Windows, package integrity, and disk space..."
    $StatusText.Text = "INSTALLING"
    $InstallLocation.Text = "Install location: $InstalledAppDirectory"

    try {
        $arguments = @(
            "-NoLogo", "-NoProfile", "-ExecutionPolicy", "Bypass",
            "-File", ('"' + $InstallerScript + '"'), "-NoLaunch"
        )
        $script:InstallProcess = Start-Process -FilePath "powershell.exe" -ArgumentList $arguments -PassThru -WindowStyle Hidden -RedirectStandardOutput $StdoutPath -RedirectStandardError $StderrPath
        $script:InstallRunning = $true
    }
    catch {
        Set-Content -LiteralPath $StderrPath -Value $_.Exception.Message -Encoding Utf8
        Complete-Installation -ExitCode 1
    }
}

function Save-WindowPreview {
    param([string]$Path)
    if (-not $Path) { return }
    $parent = Split-Path -Parent ([IO.Path]::GetFullPath($Path))
    if ($parent) { New-Item -ItemType Directory -Path $parent -Force | Out-Null }
    $Window.UpdateLayout()
    $width = [Math]::Max(1, [int][Math]::Ceiling($Window.ActualWidth))
    $height = [Math]::Max(1, [int][Math]::Ceiling($Window.ActualHeight))
    $bitmap = New-Object Windows.Media.Imaging.RenderTargetBitmap($width, $height, 96, 96, [Windows.Media.PixelFormats]::Pbgra32)
    $bitmap.Render($Window)
    $encoder = New-Object Windows.Media.Imaging.PngBitmapEncoder
    $encoder.Frames.Add([Windows.Media.Imaging.BitmapFrame]::Create($bitmap))
    $stream = [IO.File]::Create([IO.Path]::GetFullPath($Path))
    try { $encoder.Save($stream) }
    finally { $stream.Dispose() }
}

$Timer = New-Object Windows.Threading.DispatcherTimer
$Timer.Interval = [TimeSpan]::FromMilliseconds(450)
$Timer.Add_Tick({
    if (-not $script:InstallRunning -or -not $script:InstallProcess) { return }
    Update-InstallerUi
    $script:InstallProcess.Refresh()
    if ($script:InstallProcess.HasExited) {
        $exitCode = $script:InstallProcess.ExitCode
        Complete-Installation -ExitCode $exitCode
    }
})

$CloseButton.Add_Click({ $Window.Close() })
$LaunchButton.Add_Click({
    if ((Test-Path -LiteralPath $InstalledPythonw) -and (Test-Path -LiteralPath $InstalledLauncher)) {
        Start-Process -FilePath $InstalledPythonw -ArgumentList ('"' + $InstalledLauncher + '"') -WorkingDirectory $InstalledAppDirectory -WindowStyle Hidden
        $Window.Close()
    }
    else {
        [Windows.MessageBox]::Show("The WSP launcher could not be found. Run the installer again to repair the installation.", "WSP Offline System", "OK", "Warning") | Out-Null
    }
})

$Window.Add_Closing({
    param($sender, $eventArgs)
    if ($script:InstallRunning) {
        [Windows.MessageBox]::Show("Setup is still working. Please wait until installation finishes.", "WSP Offline System Setup", "OK", "Information") | Out-Null
        $eventArgs.Cancel = $true
    }
})

$Window.Add_ContentRendered({
    $Timer.Start()
    if ($Preview) {
        $script:InstallerExitCode = 0
        Set-CurrentStage 4 "Installing verified application packages..."
        $StatusText.Text = "INSTALLING"
        $InstallLocation.Text = "Install location: $InstalledAppDirectory"
        $InstallLog.Text = "WSP Offline System - verified one-click setup`r`n`r`n[OK] Windows 64-bit verified.`r`n[OK] Installer package checksums are valid.`r`n[OK] Application files installed.`r`n`r`nInstalling required packages..."
        $CloseButton.Content = "Close preview"
        $CloseButton.IsEnabled = $true
        if ($CapturePath) {
            Save-WindowPreview -Path $CapturePath
            $Window.Close()
        }
    }
    else {
        Start-Installation
    }
})

$null = $Window.ShowDialog()
$Timer.Stop()
exit $script:InstallerExitCode
