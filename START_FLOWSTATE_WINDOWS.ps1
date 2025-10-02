# ========================================
# FlowState-AI One-Click Startup (PowerShell)
# ========================================
# This script starts all FlowState-AI components with one click
# Run this in PowerShell: .\START_FLOWSTATE_WINDOWS.ps1

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " FlowState-AI CRM System" -ForegroundColor Cyan
Write-Host " One-Click Startup for Windows" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[OK] Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.11+ from https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "Make sure to check 'Add Python to PATH' during installation" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if Node.js is installed
try {
    $nodeVersion = node --version 2>&1
    Write-Host "[OK] Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Node.js is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Node.js LTS from https://nodejs.org/" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Get script directory
$ProjectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectDir

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Step 1: Installing Dependencies" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Install Python dependencies
Write-Host "[1/4] Installing Python packages..." -ForegroundColor Yellow
python -m pip install --quiet flask flask-socketio flask-cors psutil fastapi uvicorn requests python-dotenv schedule pydantic

# Install Node.js dependencies if needed
if (-not (Test-Path "node_modules")) {
    Write-Host "[2/4] Installing root Node.js packages..." -ForegroundColor Yellow
    npm install --silent
}

if (-not (Test-Path "backend\node_modules")) {
    Write-Host "[3/4] Installing backend packages..." -ForegroundColor Yellow
    Set-Location backend
    npm install --silent
    Set-Location ..
}

if (-not (Test-Path "frontend\node_modules")) {
    Write-Host "[4/4] Installing frontend packages..." -ForegroundColor Yellow
    Set-Location frontend
    npm install --silent
    Set-Location ..
}

Write-Host ""
Write-Host "[OK] All dependencies installed!" -ForegroundColor Green
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Step 2: Building Frontend" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Set-Location frontend
if (-not (Test-Path "dist")) {
    Write-Host "Building frontend for production..." -ForegroundColor Yellow
    npm run build
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Frontend build failed" -ForegroundColor Red
        Set-Location ..
        Read-Host "Press Enter to exit"
        exit 1
    }
} else {
    Write-Host "[OK] Frontend already built" -ForegroundColor Green
}
Set-Location ..

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Step 3: Starting Services" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Create logs directory
if (-not (Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" | Out-Null
}

# Start Manus Sync Engine
Write-Host "[1/4] Starting Manus Sync Engine..." -ForegroundColor Yellow
Start-Process -FilePath "python" -ArgumentList "MANUS_SYNC_ENGINE_ENHANCED.py" -WindowStyle Minimized -WorkingDirectory $ProjectDir
Start-Sleep -Seconds 2

# Start Godmode Dashboard
Write-Host "[2/4] Starting Godmode Dashboard..." -ForegroundColor Yellow
Start-Process -FilePath "python" -ArgumentList "app_enhanced.py" -WindowStyle Minimized -WorkingDirectory "$ProjectDir\godmode-dashboard"
Start-Sleep -Seconds 3

# Start Backend API
Write-Host "[3/4] Starting Backend API..." -ForegroundColor Yellow
Start-Process -FilePath "cmd" -ArgumentList "/c", "npx ts-node src/index.ts" -WindowStyle Minimized -WorkingDirectory "$ProjectDir\backend"
Start-Sleep -Seconds 5

# Start Frontend Server
Write-Host "[4/4] Starting Frontend Server..." -ForegroundColor Yellow
Start-Process -FilePath "python" -ArgumentList "-m", "http.server", "3000" -WindowStyle Minimized -WorkingDirectory "$ProjectDir\frontend\dist"
Start-Sleep -Seconds 2

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " FlowState-AI is Starting Up!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Please wait 10-15 seconds for all services to initialize..." -ForegroundColor Yellow
Write-Host ""
Start-Sleep -Seconds 10

Write-Host "========================================" -ForegroundColor Green
Write-Host " System Ready!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Your FlowState-AI CRM is now running!" -ForegroundColor Green
Write-Host ""
Write-Host "Access your system at:" -ForegroundColor Cyan
Write-Host "  Frontend:  http://localhost:3000" -ForegroundColor White
Write-Host "  Backend:   http://localhost:3001/api" -ForegroundColor White
Write-Host "  Dashboard: http://localhost:3333" -ForegroundColor White
Write-Host ""
Write-Host "All services are running in background windows." -ForegroundColor Yellow
Write-Host "To stop services, close those windows or run STOP_FLOWSTATE_WINDOWS.ps1" -ForegroundColor Yellow
Write-Host ""
Write-Host "Opening dashboard in your browser..." -ForegroundColor Cyan
Write-Host ""

# Open the dashboard in default browser
Start-Process "http://localhost:3333"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Press any key to exit this window" -ForegroundColor Cyan
Write-Host " (Services will continue running)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Read-Host ""
