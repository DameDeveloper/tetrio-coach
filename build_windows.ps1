$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

Write-Host "Installing build dependencies..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt pyinstaller

$AppName = "TetrioCoach"

Write-Host "Cleaning previous build output..."
Remove-Item -Recurse -Force ".\build", ".\dist" -ErrorAction SilentlyContinue

Write-Host "Building executable..."
python -m PyInstaller `
    --noconsole `
    --onedir `
    --clean `
    --name $AppName `
    --collect-all matplotlib `
    ".\tetrio_coach.py"

Write-Host ""
Write-Host "Build complete."
Write-Host "Executable folder: $ProjectRoot\dist\$AppName"
Write-Host "Run: $ProjectRoot\dist\$AppName\$AppName.exe"
