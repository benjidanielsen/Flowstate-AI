@echo off
REM GODMODE AI System Startup Script for Windows
REM This script starts the FlowState-AI GODMODE system on Windows

echo.
echo ========================================
echo   GODMODE AI SYSTEM - Windows Startup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python 3.11+ and ensure it\'s added to PATH.
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed or not in PATH.
    echo Please install Node.js LTS version.
    pause
    exit /b 1
)

REM Run the Python startup script which includes pre-startup checks and fixes
echo.
echo Starting GODMODE AI System with pre-startup checks and fixes...
echo.
python godmode_start.py

pause
