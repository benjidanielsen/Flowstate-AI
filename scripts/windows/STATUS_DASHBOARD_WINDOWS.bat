@echo off
REM ========================================
REM FlowState-AI Live Status Dashboard
REM ========================================
REM Real-time monitoring of system status

title FlowState-AI Status Dashboard
color 0A

:LOOP
cls
echo.
echo ========================================
echo  FlowState-AI Live Status Dashboard
echo ========================================
echo  %DATE% %TIME%
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [32m[OK][0m Python: Installed
) else (
    echo [31m[X][0m Python: Not Found
)

REM Check Node.js
node --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [32m[OK][0m Node.js: Installed
) else (
    echo [31m[X][0m Node.js: Not Found
)

echo.
echo ========================================
echo  Service Status
echo ========================================
echo.

REM Check Frontend (Port 3000)
netstat -ano | findstr :3000 | findstr LISTENING >nul 2>&1
if %errorlevel% equ 0 (
    echo [32m[RUNNING][0m Frontend Server (Port 3000)
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3000 ^| findstr LISTENING') do (
        echo            PID: %%a
    )
) else (
    echo [33m[STOPPED][0m Frontend Server (Port 3000)
)

REM Check Backend (Port 3001)
netstat -ano | findstr :3001 | findstr LISTENING >nul 2>&1
if %errorlevel% equ 0 (
    echo [32m[RUNNING][0m Backend API (Port 3001)
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3001 ^| findstr LISTENING') do (
        echo            PID: %%a
    )
) else (
    echo [33m[STOPPED][0m Backend API (Port 3001)
)

REM Check Dashboard (Port 3333)
netstat -ano | findstr :3333 | findstr LISTENING >nul 2>&1
if %errorlevel% equ 0 (
    echo [32m[RUNNING][0m Godmode Dashboard (Port 3333)
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3333 ^| findstr LISTENING') do (
        echo            PID: %%a
    )
) else (
    echo [33m[STOPPED][0m Godmode Dashboard (Port 3333)
)

REM Check for Python processes (Sync Engine)
tasklist | findstr python.exe >nul 2>&1
if %errorlevel% equ 0 (
    echo [32m[RUNNING][0m Python Processes (Sync Engine)
) else (
    echo [33m[STOPPED][0m Python Processes (Sync Engine)
)

echo.
echo ========================================
echo  Quick Actions
echo ========================================
echo.
echo  [1] Start System
echo  [2] Stop System
echo  [3] Open Frontend (localhost:3000)
echo  [4] Open Dashboard (localhost:3333)
echo  [5] Run Health Check
echo  [R] Refresh Status
echo  [Q] Quit
echo.
echo ========================================

REM Auto-refresh every 5 seconds if no input
choice /c 12345RQ /t 5 /d R /n >nul 2>&1
if errorlevel 7 goto END
if errorlevel 6 goto LOOP
if errorlevel 5 goto HEALTH
if errorlevel 4 goto DASHBOARD
if errorlevel 3 goto FRONTEND
if errorlevel 2 goto STOP
if errorlevel 1 goto START

:START
cls
echo Starting FlowState-AI...
call START_FLOWSTATE_WINDOWS.bat
goto LOOP

:STOP
cls
echo Stopping FlowState-AI...
call STOP_FLOWSTATE_WINDOWS.bat
timeout /t 3 /nobreak >nul
goto LOOP

:FRONTEND
start http://localhost:3000
goto LOOP

:DASHBOARD
start http://localhost:3333
goto LOOP

:HEALTH
cls
call CHECK_SYSTEM_WINDOWS.bat
pause
goto LOOP

:END
echo.
echo Exiting status dashboard...
timeout /t 1 /nobreak >nul
exit
