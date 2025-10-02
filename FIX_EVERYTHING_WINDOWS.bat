@echo off
REM ========================================
REM FlowState-AI Fix Everything Script
REM ========================================
REM Attempts to fix all common issues automatically

echo.
echo ========================================
echo  FlowState-AI Automatic Repair
echo ========================================
echo.
echo This script will attempt to fix common issues:
echo   - Stop all running services
echo   - Clear temporary files
echo   - Reinstall dependencies
echo   - Rebuild frontend
echo   - Reset database (optional)
echo.
echo This may take 3-5 minutes.
echo.
pause

REM ========================================
REM Step 1: Stop all services
REM ========================================

echo.
echo [1/6] Stopping all services...
call STOP_FLOWSTATE_WINDOWS.bat >nul 2>&1
timeout /t 3 /nobreak >nul
echo [OK] Services stopped

REM ========================================
REM Step 2: Clear temporary files
REM ========================================

echo [2/6] Clearing temporary files...

REM Clear Python cache
if exist "__pycache__\" rmdir /s /q __pycache__
if exist "godmode-dashboard\__pycache__\" rmdir /s /q godmode-dashboard\__pycache__
if exist "ai-gods\__pycache__\" rmdir /s /q ai-gods\__pycache__

REM Clear npm cache
call npm cache clean --force >nul 2>&1

REM Clear logs
if exist "logs\" (
    del /q logs\*.log >nul 2>&1
)
if exist "godmode-dashboard\logs\" (
    del /q godmode-dashboard\logs\*.log >nul 2>&1
)

echo [OK] Temporary files cleared

REM ========================================
REM Step 3: Reinstall Python packages
REM ========================================

echo [3/6] Reinstalling Python packages...
python -m pip install --upgrade pip --quiet
python -m pip install --force-reinstall --quiet ^
    flask ^
    flask-socketio ^
    flask-cors ^
    psutil ^
    fastapi ^
    uvicorn ^
    requests ^
    python-dotenv ^
    schedule ^
    pydantic

if %errorlevel% neq 0 (
    echo [WARNING] Some Python packages may have failed
) else (
    echo [OK] Python packages reinstalled
)

REM ========================================
REM Step 4: Reinstall Node.js packages
REM ========================================

echo [4/6] Reinstalling Node.js packages...

REM Root packages
if exist "node_modules\" rmdir /s /q node_modules
call npm install --silent --no-audit --no-fund
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install root packages
    pause
    exit /b 1
)

REM Backend packages
cd backend
if exist "node_modules\" rmdir /s /q node_modules
call npm install --silent --no-audit --no-fund
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install backend packages
    cd ..
    pause
    exit /b 1
)
cd ..

REM Frontend packages
cd frontend
if exist "node_modules\" rmdir /s /q node_modules
call npm install --silent --no-audit --no-fund
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install frontend packages
    cd ..
    pause
    exit /b 1
)
cd ..

echo [OK] Node.js packages reinstalled

REM ========================================
REM Step 5: Rebuild frontend
REM ========================================

echo [5/6] Rebuilding frontend...
cd frontend
if exist "dist\" rmdir /s /q dist
call npm run build >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Frontend build failed
    echo Trying again with verbose output...
    call npm run build
    if %errorlevel% neq 0 (
        cd ..
        pause
        exit /b 1
    )
)
cd ..
echo [OK] Frontend rebuilt

REM ========================================
REM Step 6: Database reset (optional)
REM ========================================

echo [6/6] Reset database? (Y/N)
echo WARNING: This will delete all your data!
set /p RESET_DB=
if /i "%RESET_DB%"=="Y" (
    if exist "backend\data\*.db" (
        del /q backend\data\*.db
        echo [OK] Database reset
    ) else (
        echo [INFO] No database found to reset
    )
) else (
    echo [OK] Database preserved
)

REM ========================================
REM Repair Complete
REM ========================================

echo.
echo ========================================
echo  Repair Complete!
echo ========================================
echo.
echo All fixes have been applied.
echo.
echo Would you like to start the system now? (Y/N)
set /p START_NOW=
if /i "%START_NOW%"=="Y" (
    echo.
    echo Starting FlowState-AI...
    call START_FLOWSTATE_WINDOWS.bat
) else (
    echo.
    echo You can start the system later with:
    echo START_FLOWSTATE_WINDOWS.bat
    echo.
)

pause
