@echo off
REM ========================================
REM FlowState-AI System Health Checker
REM ========================================
REM Diagnoses issues and checks if everything is working

echo.
echo ========================================
echo  FlowState-AI System Health Check
echo ========================================
echo.

set "ISSUES=0"

REM Check Python
echo [1/7] Checking Python...
python --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=2" %%v in ('python --version 2^>^&1') do echo [OK] Python %%v
) else (
    echo [ERROR] Python not found
    set /a ISSUES+=1
)

REM Check Node.js
echo [2/7] Checking Node.js...
node --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=1" %%v in ('node --version 2^>^&1') do echo [OK] Node.js %%v
) else (
    echo [ERROR] Node.js not found
    set /a ISSUES+=1
)

REM Check npm
echo [3/7] Checking npm...
npm --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=1" %%v in ('npm --version 2^>^&1') do echo [OK] npm %%v
) else (
    echo [ERROR] npm not found
    set /a ISSUES+=1
)

REM Check Python packages
echo [4/7] Checking Python packages...
python -c "import flask, flask_socketio, psutil" >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Required Python packages installed
) else (
    echo [WARNING] Some Python packages may be missing
    echo Run: python -m pip install flask flask-socketio psutil
    set /a ISSUES+=1
)

REM Check Node modules
echo [5/7] Checking Node.js packages...
if exist "node_modules\" (
    echo [OK] Root node_modules found
) else (
    echo [WARNING] Root node_modules missing
    echo Run: npm install
    set /a ISSUES+=1
)

if exist "backend\node_modules\" (
    echo [OK] Backend node_modules found
) else (
    echo [WARNING] Backend node_modules missing
    echo Run: cd backend ^&^& npm install
    set /a ISSUES+=1
)

if exist "frontend\node_modules\" (
    echo [OK] Frontend node_modules found
) else (
    echo [WARNING] Frontend node_modules missing
    echo Run: cd frontend ^&^& npm install
    set /a ISSUES+=1
)

REM Check frontend build
echo [6/7] Checking frontend build...
if exist "frontend\dist\" (
    echo [OK] Frontend is built
) else (
    echo [WARNING] Frontend not built
    echo Run: cd frontend ^&^& npm run build
    set /a ISSUES+=1
)

REM Check if services are running
echo [7/7] Checking running services...
netstat -ano | findstr :3000 >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Frontend running on port 3000
) else (
    echo [INFO] Frontend not running
)

netstat -ano | findstr :3001 >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Backend running on port 3001
) else (
    echo [INFO] Backend not running
)

netstat -ano | findstr :3333 >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Dashboard running on port 3333
) else (
    echo [INFO] Dashboard not running
)

echo.
echo ========================================
echo  Health Check Complete
echo ========================================
echo.

if %ISSUES% equ 0 (
    echo [OK] System is healthy! No issues found.
    echo.
    echo If services are not running, start them with:
    echo START_FLOWSTATE_WINDOWS.bat
) else (
    echo [WARNING] Found %ISSUES% issue(s)
    echo.
    echo To fix issues:
    echo 1. Run INSTALL_WINDOWS.bat to reinstall dependencies
    echo 2. Check the messages above for specific fixes
    echo 3. Restart your computer if issues persist
)

echo.
pause
