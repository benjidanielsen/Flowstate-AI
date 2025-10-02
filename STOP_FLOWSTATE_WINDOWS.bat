@echo off
REM ========================================
REM FlowState-AI Stop Script (Windows)
REM ========================================
REM This script stops all FlowState-AI services

echo.
echo ========================================
echo  Stopping FlowState-AI Services
echo ========================================
echo.

REM Stop Python processes
echo Stopping Python services...
taskkill /F /FI "WINDOWTITLE eq Manus Sync Engine*" >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq Godmode Dashboard*" >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq Frontend Server*" >nul 2>&1

REM Stop Node.js processes
echo Stopping Node.js services...
taskkill /F /FI "WINDOWTITLE eq Backend API*" >nul 2>&1

REM Alternative: Kill by port (if windows are closed but processes still running)
echo Checking for processes on ports 3000, 3001, 3333...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3000 ^| findstr LISTENING') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3001 ^| findstr LISTENING') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3333 ^| findstr LISTENING') do taskkill /F /PID %%a >nul 2>&1

echo.
echo [OK] All FlowState-AI services stopped!
echo.
timeout /t 3 /nobreak >nul
