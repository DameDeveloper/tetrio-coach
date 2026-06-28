$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$BuildDir = Join-Path $ProjectRoot "dist\TetrioCoach"
$InstallDir = Join-Path $env:LOCALAPPDATA "TetrioCoach"

if (-not (Test-Path $BuildDir)) {
    throw "먼저 build_windows.ps1로 빌드해 주세요. 찾을 수 없는 경로: $BuildDir"
}

Write-Host "Installing to $InstallDir ..."
New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
Copy-Item -Path (Join-Path $BuildDir "*") -Destination $InstallDir -Recurse -Force

$exePath = Join-Path $InstallDir "TetrioCoach.exe"
if (-not (Test-Path $exePath)) {
    throw "설치 후 실행 파일을 찾을 수 없습니다: $exePath"
}

$WScriptShell = New-Object -ComObject WScript.Shell
$ShortcutPath = Join-Path ([Environment]::GetFolderPath("Desktop")) "TetrioCoach.lnk"
$Shortcut = $WScriptShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $exePath
$Shortcut.WorkingDirectory = $InstallDir
$Shortcut.IconLocation = $exePath
$Shortcut.Save()

Write-Host "Installed."
Write-Host "Desktop shortcut created: $ShortcutPath"
