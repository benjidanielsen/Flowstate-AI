# GODMODE AI System Startup Script for Windows PowerShell
# This script starts the FlowState-AI GODMODE system on Windows

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  GODMODE AI SYSTEM - Windows Startup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH." -ForegroundColor Red
    Write-Host "Please install Python 3.11+ and ensure it's added to PATH." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if Node.js is installed
try {
    $nodeVersion = node --version 2>&1
    Write-Host "Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Node.js is not installed or not in PATH." -ForegroundColor Red
    Write-Host "Please install Node.js LTS version." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Install psutil if not already installed
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
pip install psutil

# Run the Python startup script
Write-Host ""
Write-Host "Starting GODMODE AI System..." -ForegroundColor Green
Write-Host ""
python godmode_start.py

Read-Host "Press Enter to exit"
