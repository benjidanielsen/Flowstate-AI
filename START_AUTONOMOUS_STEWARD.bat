@echo off
REM Autonomous VS Code Project Steward - Startup Script (Windows)
REM Starts the autonomous steward system for continuous repository improvement

echo ==========================================
echo   AUTONOMOUS VS CODE PROJECT STEWARD
echo ==========================================
echo.

REM Get project root
set PROJECT_ROOT=%~dp0
cd /d "%PROJECT_ROOT%"

REM Check if Python is available
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python 3 is required but not found
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

REM Check Python version
for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo Python version: %PYTHON_VERSION%

REM Ensure log directory exists
if not exist "godmode-logs" mkdir godmode-logs

REM Check if PROGRESS.md exists
if not exist "PROGRESS.md" (
    echo Creating PROGRESS.md...
    (
        echo # Autonomous Project Steward - Progress Log
        echo.
        echo This file tracks all autonomous improvements made by the VS Code Project Steward.
        echo.
        echo ---
        echo.
        echo ## %date% %time% – Session Start
        echo - Why: Initializing autonomous VS Code project steward system
        echo - Changes: Created PROGRESS.md tracking file
        echo - Commands: Initial repository scan
        echo - Result: Repository structure analyzed, baseline established
        echo - Next: Begin DISCOVER → PLAN → EXECUTE → REPEAT loop
        echo.
    ) > PROGRESS.md
)

echo.
echo Configuration:
echo    - Project Root: %PROJECT_ROOT%
echo    - Progress Log: PROGRESS.md
echo    - System Log: godmode-logs/autonomous-steward.log
echo.
echo Safety Rules Active:
echo    - No destructive operations (rm -rf, sudo, etc.)
echo    - No secrets/credentials handling
echo    - No irreversible external effects (publish, deploy)
echo    - No resource abuse (jobs ^>30 min)
echo.
echo Operating Loop:
echo    DISCOVER → PLAN → EXECUTE → REPEAT
echo.
echo To stop: Press Ctrl+C
echo.
echo ==========================================
echo Starting Autonomous Steward...
echo ==========================================
echo.

REM Run the steward
python "%PROJECT_ROOT%ai-gods\autonomous_steward.py"

REM Cleanup on exit
echo.
echo Autonomous Steward stopped
echo Check PROGRESS.md for completed work
echo Check godmode-logs\autonomous-steward.log for details
pause
