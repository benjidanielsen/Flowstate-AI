@echo off
REM ========================================
REM FlowState-AI Windows Installer
REM ========================================
REM Complete automated setup for Windows
REM Checks dependencies, installs packages, and configures everything

setlocal enabledelayedexpansion

echo.
echo ========================================
echo  FlowState-AI CRM System
echo  Windows Installation Wizard
echo ========================================
echo.
echo This installer will set up everything you need.
echo It will take 2-5 minutes depending on your internet speed.
echo.
pause

REM ========================================
REM Step 1: Check Prerequisites
REM ========================================

echo.
echo ========================================
echo  Step 1: Checking Prerequisites
echo ========================================
echo.

set "PYTHON_OK=0"
set "NODE_OK=0"
set "GIT_OK=0"

REM Check Python
echo [1/3] Checking Python...
python --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PYTHON_VER=%%v
    echo [OK] Python !PYTHON_VER! is installed
    set "PYTHON_OK=1"
) else (
    echo [MISSING] Python is not installed
    echo.
    echo Please install Python 3.11 or newer from:
    echo https://www.python.org/downloads/
    echo.
    echo IMPORTANT: Check "Add Python to PATH" during installation!
    echo.
    start https://www.python.org/downloads/
    echo Opening download page in your browser...
    echo.
    echo After installing Python, restart this installer.
    pause
    exit /b 1
)

REM Check Node.js
echo [2/3] Checking Node.js...
node --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=1" %%v in ('node --version 2^>^&1') do set NODE_VER=%%v
    echo [OK] Node.js !NODE_VER! is installed
    set "NODE_OK=1"
) else (
    echo [MISSING] Node.js is not installed
    echo.
    echo Please install Node.js LTS from:
    echo https://nodejs.org/
    echo.
    start https://nodejs.org/
    echo Opening download page in your browser...
    echo.
    echo After installing Node.js, restart this installer.
    pause
    exit /b 1
)

REM Check Git (optional but recommended)
echo [3/3] Checking Git...
git --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=3" %%v in ('git --version 2^>^&1') do set GIT_VER=%%v
    echo [OK] Git !GIT_VER! is installed
    set "GIT_OK=1"
) else (
    echo [INFO] Git is not installed (optional)
)

echo.
echo [OK] All required prerequisites are installed!
echo.

REM ========================================
REM Step 2: Install Python Packages
REM ========================================

echo ========================================
echo  Step 2: Installing Python Packages
echo ========================================
echo.

echo This may take 1-2 minutes...
echo.

REM Upgrade pip first
echo [1/2] Upgrading pip...
python -m pip install --upgrade pip --quiet

REM Install required packages
echo [2/2] Installing Flask, FastAPI, and other packages...
python -m pip install --quiet ^
    flask==3.0.0 ^
    flask-socketio==5.3.5 ^
    flask-cors==4.0.0 ^
    psutil==5.9.6 ^
    fastapi==0.104.1 ^
    uvicorn==0.24.0 ^
    requests==2.31.0 ^
    python-dotenv==1.0.0 ^
    schedule==1.2.0 ^
    pydantic==2.5.0 ^
    python-engineio==4.8.0 ^
    python-socketio==5.10.0 ^
    simple-websocket==1.0.0

if %errorlevel% neq 0 (
    echo.
    echo [WARNING] Some packages may have failed to install
    echo The system may still work, but some features might be limited
    echo.
    pause
) else (
    echo.
    echo [OK] All Python packages installed successfully!
    echo.
)

REM ========================================
REM Step 3: Install Node.js Packages
REM ========================================

echo ========================================
echo  Step 3: Installing Node.js Packages
echo ========================================
echo.

echo This may take 2-3 minutes...
echo.

REM Get project directory
set "PROJECT_DIR=%~dp0"
cd /d "%PROJECT_DIR%"

REM Install root packages
if not exist "node_modules\" (
    echo [1/3] Installing root packages...
    call npm install --silent --no-audit --no-fund
    if !errorlevel! neq 0 (
        echo [ERROR] Failed to install root packages
        echo Trying again with verbose output...
        call npm install
        if !errorlevel! neq 0 (
            echo [ERROR] Installation failed. Check your internet connection.
            pause
            exit /b 1
        )
    )
) else (
    echo [1/3] Root packages already installed
)

REM Install backend packages
if not exist "backend\node_modules\" (
    echo [2/3] Installing backend packages...
    cd backend
    call npm install --silent --no-audit --no-fund
    if !errorlevel! neq 0 (
        echo [ERROR] Failed to install backend packages
        echo Trying again with verbose output...
        call npm install
        if !errorlevel! neq 0 (
            cd ..
            echo [ERROR] Installation failed. Check your internet connection.
            pause
            exit /b 1
        )
    )
    cd ..
) else (
    echo [2/3] Backend packages already installed
)

REM Install frontend packages
if not exist "frontend\node_modules\" (
    echo [3/3] Installing frontend packages...
    cd frontend
    call npm install --silent --no-audit --no-fund
    if !errorlevel! neq 0 (
        echo [ERROR] Failed to install frontend packages
        echo Trying again with verbose output...
        call npm install
        if !errorlevel! neq 0 (
            cd ..
            echo [ERROR] Installation failed. Check your internet connection.
            pause
            exit /b 1
        )
    )
    cd ..
) else (
    echo [3/3] Frontend packages already installed
)

echo.
echo [OK] All Node.js packages installed successfully!
echo.

REM ========================================
REM Step 4: Build Frontend
REM ========================================

echo ========================================
echo  Step 4: Building Frontend
echo ========================================
echo.

cd frontend

if exist "dist\" (
    echo Frontend is already built. Rebuild? (Y/N)
    set /p REBUILD=
    if /i "!REBUILD!"=="Y" (
        echo Rebuilding frontend...
        rmdir /s /q dist
        call npm run build
        if !errorlevel! neq 0 (
            echo [ERROR] Frontend build failed
            cd ..
            pause
            exit /b 1
        )
    ) else (
        echo [OK] Using existing build
    )
) else (
    echo Building frontend for production...
    call npm run build
    if !errorlevel! neq 0 (
        echo [ERROR] Frontend build failed
        cd ..
        pause
        exit /b 1
    )
)

cd ..

echo.
echo [OK] Frontend built successfully!
echo.

REM ========================================
REM Step 5: Create Directories
REM ========================================

echo ========================================
echo  Step 5: Setting Up Directories
echo ========================================
echo.

if not exist "logs\" mkdir logs
if not exist "backend\data\" mkdir backend\data
if not exist "godmode-dashboard\logs\" mkdir godmode-dashboard\logs
if not exist "godmode-dashboard\static\" mkdir godmode-dashboard\static
if not exist "godmode-dashboard\templates\" mkdir godmode-dashboard\templates

echo [OK] All directories created!
echo.

REM ========================================
REM Step 6: Create Desktop Shortcuts
REM ========================================

echo ========================================
echo  Step 6: Creating Desktop Shortcuts
echo ========================================
echo.

set "DESKTOP=%USERPROFILE%\Desktop"

REM Create shortcut to start script
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%TEMP%\CreateShortcut.vbs"
echo sLinkFile = "%DESKTOP%\Start FlowState-AI.lnk" >> "%TEMP%\CreateShortcut.vbs"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%TEMP%\CreateShortcut.vbs"
echo oLink.TargetPath = "%PROJECT_DIR%START_FLOWSTATE_WINDOWS.bat" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.WorkingDirectory = "%PROJECT_DIR%" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.Description = "Start FlowState-AI CRM System" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.Save >> "%TEMP%\CreateShortcut.vbs"
cscript //nologo "%TEMP%\CreateShortcut.vbs"
del "%TEMP%\CreateShortcut.vbs"

REM Create shortcut to stop script
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%TEMP%\CreateShortcut.vbs"
echo sLinkFile = "%DESKTOP%\Stop FlowState-AI.lnk" >> "%TEMP%\CreateShortcut.vbs"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%TEMP%\CreateShortcut.vbs"
echo oLink.TargetPath = "%PROJECT_DIR%STOP_FLOWSTATE_WINDOWS.bat" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.WorkingDirectory = "%PROJECT_DIR%" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.Description = "Stop FlowState-AI CRM System" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.Save >> "%TEMP%\CreateShortcut.vbs"
cscript //nologo "%TEMP%\CreateShortcut.vbs"
del "%TEMP%\CreateShortcut.vbs"

echo [OK] Desktop shortcuts created!
echo.

REM ========================================
REM Installation Complete
REM ========================================

echo.
echo ========================================
echo  Installation Complete!
echo ========================================
echo.
echo FlowState-AI is now installed and ready to use!
echo.
echo Desktop shortcuts created:
echo   - Start FlowState-AI.lnk
echo   - Stop FlowState-AI.lnk
echo.
echo To start the system:
echo   1. Double-click "Start FlowState-AI" on your desktop
echo   OR
echo   2. Run START_FLOWSTATE_WINDOWS.bat from this folder
echo.
echo The system will open in your browser automatically.
echo.
echo ========================================
echo  Would you like to start it now? (Y/N)
echo ========================================
set /p START_NOW=
if /i "!START_NOW!"=="Y" (
    echo.
    echo Starting FlowState-AI...
    call START_FLOWSTATE_WINDOWS.bat
) else (
    echo.
    echo You can start FlowState-AI anytime by double-clicking
    echo the desktop shortcut or running START_FLOWSTATE_WINDOWS.bat
    echo.
)

pause
