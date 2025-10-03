@echo off
REM ========================================
REM FlowState-AI One-Click Startup (Windows)
REM ========================================
REM This script starts all FlowState-AI components with one click
REM No manual configuration needed!

echo.
echo ========================================
echo  FlowState-AI CRM System
echo  One-Click Startup for Windows
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.11+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed or not in PATH
    echo Please install Node.js LTS from https://nodejs.org/
    pause
    exit /b 1
)

echo [OK] Python found: 
python --version
echo [OK] Node.js found: 
node --version
echo.

REM Get the directory where this script is located
set "PROJECT_DIR=%~dp0"
cd /d "%PROJECT_DIR%"

echo ========================================
echo  Step 1: Installing Dependencies
echo ========================================
echo.

REM Install Python dependencies
echo [1/4] Installing Python packages...
python -m pip install --quiet flask flask-socketio flask-cors psutil fastapi uvicorn requests python-dotenv schedule pydantic
if %errorlevel% neq 0 (
    echo [WARNING] Some Python packages may have failed to install
)

REM Install Node.js dependencies if needed
if not exist "node_modules\" (
    echo [2/4] Installing root Node.js packages...
    call npm install --silent
)

if not exist "backend\node_modules\" (
    echo [3/4] Installing backend packages...
    cd backend
    call npm install --silent
    cd ..
)

if not exist "frontend\node_modules\" (
    echo [4/4] Installing frontend packages...
    cd frontend
    call npm install --silent
    cd ..
)

echo.
echo [OK] All dependencies installed!
echo.

echo ========================================
echo  Step 2: Building Frontend
echo ========================================
echo.

cd frontend
if not exist "dist\" (
    echo Building frontend for production...
    call npm run build
    if %errorlevel% neq 0 (
        echo [ERROR] Frontend build failed
        cd ..
        pause
        exit /b 1
    )
) else (
    echo [OK] Frontend already built
)
cd ..

echo.
echo ========================================
echo  Step 3: Starting Services
echo ========================================
echo.

REM Create logs directory
if not exist "logs\" mkdir logs

REM Start Manus Sync Engine
echo [1/5] Starting Manus Sync Engine...
start "Manus Sync Engine" /MIN python MANUS_SYNC_ENGINE_ENHANCED.py
timeout /t 2 /nobreak >nul

REM Start AI Agents for Autonomous Development
echo [2/5] Starting Autonomous AI Agents...
start "AI Agents" /MIN python LAUNCH_AI_AGENTS.py
timeout /t 3 /nobreak >nul

REM Start Godmode Dashboard
echo [3/5] Starting Godmode Dashboard...
cd godmode-dashboard
start "Godmode Dashboard" /MIN python app_enhanced.py
cd ..
timeout /t 3 /nobreak >nul

REM Start Backend API
echo [4/5] Starting Backend API...
cd backend
start "Backend API" /MIN cmd /c "npx ts-node src/index.ts"
cd ..
timeout /t 5 /nobreak >nul

REM Start Frontend Server
echo [5/5] Starting Frontend Server...
cd frontend\dist
start "Frontend Server" /MIN python -m http.server 3000
cd ..\..
timeout /t 2 /nobreak >nul

echo.
echo ========================================
echo  FlowState-AI is Starting Up!
echo ========================================
echo.
echo Please wait 10-15 seconds for all services to initialize...
echo.
timeout /t 10 /nobreak >nul

echo ========================================
echo  System Ready!
echo ========================================
echo.
echo Your FlowState-AI CRM is now running!
echo.
echo Access your system at:
echo   Frontend:  http://localhost:3000
echo   Backend:   http://localhost:3001/api
echo   Dashboard: http://localhost:3333
echo.
echo All services are running in background windows.
echo Close those windows to stop the services.
echo.
echo Opening dashboard in your browser...
echo.

REM Open the dashboard in default browser
start http://localhost:3333

echo.
echo ========================================
echo  Press any key to exit this window
echo  (Services will continue running)
echo ========================================
pause >nul
