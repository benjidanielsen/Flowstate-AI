@echo off
REM ========================================
REM Start Autonomous AI Agents (Windows)
REM ========================================
REM Launches all AI agents for 24/7 autonomous development

echo.
echo ========================================
echo  Starting Autonomous AI Agent System
echo ========================================
echo.

REM Get project directory
set "PROJECT_DIR=%~dp0"
cd /d "%PROJECT_DIR%"

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found
    echo Please install Python 3.11+ and add to PATH
    pause
    exit /b 1
)

echo [1/2] Launching AI agents...
start "AI Agents" /MIN python LAUNCH_AI_AGENTS.py

REM Wait a moment for agents to start
timeout /t 5 /nobreak >nul

echo [2/2] Checking agent status...
if exist "godmode-logs\agent-status.json" (
    echo.
    echo ========================================
    echo  AI Agents Launched Successfully!
    echo ========================================
    echo.
    echo Your AI agents are now running autonomously:
    echo   - Collective Memory System
    echo   - Communication Hub
    echo   - AI Democracy System
    echo   - Innovation AI
    echo   - Project Manager AI
    echo.
    echo These agents will:
    echo   - Work 24/7 without user intervention
    echo   - Make autonomous development decisions
    echo   - Coordinate via AI democracy voting
    echo   - Generate innovative ideas
    echo   - Manage project tasks automatically
    echo.
    echo Status: godmode-logs\agent-status.json
    echo Logs: godmode-logs\ai-launcher.log
    echo.
    echo ========================================
    echo  Autonomous Development Mode: ACTIVE
    echo ========================================
) else (
    echo.
    echo [WARNING] Could not verify agent status
    echo Check godmode-logs\ai-launcher.log for details
)

echo.
pause
