@echo off
REM ========================================
REM Stop Autonomous AI Agents (Windows)
REM ========================================

echo.
echo ========================================
echo  Stopping AI Agents
echo ========================================
echo.

REM Stop the AI agent launcher
taskkill /F /FI "WINDOWTITLE eq AI Agents*" >nul 2>&1

REM Stop individual AI agent processes
echo Stopping AI agent processes...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *project-manager*" >nul 2>&1
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *innovation*" >nul 2>&1
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *democracy*" >nul 2>&1
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *communication*" >nul 2>&1
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *memory*" >nul 2>&1

echo.
echo [OK] AI agents stopped
echo.
timeout /t 2 /nobreak >nul
