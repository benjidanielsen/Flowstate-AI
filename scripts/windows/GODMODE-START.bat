@echo off
title FlowState-AI GODMODE - Ultimate Autonomous Development System
color 0A

echo.
echo  ███████╗██╗      ██████╗ ██╗    ██╗███████╗████████╗ █████╗ ████████╗███████╗       █████╗ ██╗
echo  ██╔════╝██║     ██╔═══██╗██║    ██║██╔════╝╚══██╔══╝██╔══██╗╚══██╔══╝██╔════╝      ██╔══██╗██║
echo  █████╗  ██║     ██║   ██║██║ █╗ ██║███████╗   ██║   ███████║   ██║   █████╗  █████╗███████║██║
echo  ██╔══╝  ██║     ██║   ██║██║███╗██║╚════██║   ██║   ██╔══██║   ██║   ██╔══╝  ╚════╝██╔══██║██║
echo  ██║     ███████╗╚██████╔╝╚███╔███╔╝███████║   ██║   ██║  ██║   ██║   ███████╗      ██║  ██║██║
echo  ╚═╝     ╚══════╝ ╚═════╝  ╚══╝╚══╝ ╚══════╝   ╚═╝   ╚═╝  ╚═╝   ╚═╝   ╚══════╝      ╚═╝  ╚═╝╚═╝
echo.
echo                            🤖 GODMODE AUTONOMOUS DEVELOPMENT SYSTEM 🤖
echo                                    ⚡ NO LIMITS • NO SETUP • NO ERRORS ⚡
echo.

REM ============================================================================
REM                           GODMODE SAFETY PROTOCOLS
REM ============================================================================

echo [🛡️] Activating GODMODE Safety Protocols...

REM Create safety backup
if not exist "GODMODE-BACKUP" mkdir GODMODE-BACKUP
xcopy /E /I /Y . GODMODE-BACKUP\ >nul 2>&1

REM Check if first run
if not exist "GODMODE-INITIALIZED.flag" (
    echo [🔧] FIRST RUN DETECTED - INITIALIZING GODMODE SYSTEM...
    goto FIRST_RUN_SETUP
)

REM ============================================================================
REM                           GODMODE MAIN EXECUTION
REM ============================================================================

:MAIN_EXECUTION
echo [🚀] LAUNCHING AI GODS DEVELOPMENT ARMY...

REM Kill any existing processes to prevent conflicts
taskkill /F /IM node.exe >nul 2>&1
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM code.exe >nul 2>&1

REM Wait for processes to fully terminate
timeout /t 2 >nul

REM Start the AI Gods system
echo [🤖] Starting Project Manager AI...
start /B "ProjectManager" cmd /c "python ai-gods\project-manager.py"

echo [💻] Starting Backend Developer AI...
start /B "BackendDev" cmd /c "python ai-gods\backend-developer.py"

echo [🎨] Starting Frontend Developer AI...
start /B "FrontendDev" cmd /c "python ai-gods\frontend-developer.py"

echo [🗄️] Starting Database AI...
start /B "DatabaseAI" cmd /c "python ai-gods\database-ai.py"

echo [🔬] Starting Tester AI...
start /B "TesterAI" cmd /c "python ai-gods\tester-ai.py"

echo [🛠️] Starting Fixer AI...
start /B "FixerAI" cmd /c "python ai-gods\fixer-ai.py"

echo [🚀] Starting DevOps AI...
start /B "DevOpsAI" cmd /c "python ai-gods\devops-ai.py"

echo [📚] Starting Documentation AI...
start /B "DocsAI" cmd /c "python ai-gods\documentation-ai.py"

echo [🆘] Starting Support AI (Your Personal IT God)...
start /B "SupportAI" cmd /c "python ai-gods\support-ai.py"

REM Start monitoring dashboard
echo [📊] Starting GODMODE Dashboard...
start /B "Dashboard" cmd /c "python godmode-dashboard\app.py"

REM Start VSCode with project
echo [💻] Launching VSCode with GODMODE Extensions...
if exist "portable-tools\vscode\Code.exe" (
    start "" "portable-tools\vscode\Code.exe" .
) else (
    start "" code .
)

REM Start development servers
echo [🌐] Starting Development Servers...
start /B "Backend" cmd /c "cd backend && npm run dev"
start /B "Frontend" cmd /c "cd frontend && npm run dev"

echo.
echo ✅ GODMODE SYSTEM FULLY ACTIVATED!
echo.
echo 🎯 AI GODS STATUS:
echo    • 9 Autonomous AI Agents: ACTIVE
echo    • Development Servers: RUNNING
echo    • VSCode: LAUNCHED
echo    • Dashboard: http://localhost:3333
echo    • Frontend: http://localhost:3000
echo    • Backend API: http://localhost:3001
echo    • AI Chat: http://localhost:3333/chat
echo.
echo 💬 GODMODE COMMANDS:
echo    • Type 'chat' to talk to AI Gods
echo    • Type 'status' to check system health
echo    • Type 'deploy' to deploy to production
echo    • Type 'fix' to auto-fix any issues
echo    • Type 'stop' to shutdown safely
echo.

:COMMAND_LOOP
set /p command="GODMODE> "

if /i "%command%"=="chat" (
    start http://localhost:3333/chat
    goto COMMAND_LOOP
)

if /i "%command%"=="status" (
    python godmode-tools\system-status.py
    goto COMMAND_LOOP
)

if /i "%command%"=="deploy" (
    python ai-gods\devops-ai.py --deploy-now
    goto COMMAND_LOOP
)

if /i "%command%"=="fix" (
    python ai-gods\support-ai.py --emergency-fix
    goto COMMAND_LOOP
)

if /i "%command%"=="stop" (
    goto SAFE_SHUTDOWN
)

if /i "%command%"=="help" (
    echo.
    echo 🤖 GODMODE AI COMMANDS:
    echo    chat   - Open AI chat interface
    echo    status - Check system health
    echo    deploy - Deploy to production
    echo    fix    - Emergency auto-fix
    echo    stop   - Safe shutdown
    echo    help   - Show this help
    echo.
    goto COMMAND_LOOP
)

echo Unknown command. Type 'help' for available commands.
goto COMMAND_LOOP

REM ============================================================================
REM                           FIRST RUN SETUP
REM ============================================================================

:FIRST_RUN_SETUP
echo [🔧] GODMODE FIRST RUN SETUP - MAKING EVERYTHING PERFECT...

REM Check Windows version and architecture
echo [🔍] Detecting system configuration...
for /f "tokens=2 delims==" %%i in ('wmic os get version /value ^| find "="') do set winver=%%i
for /f "tokens=2 delims==" %%i in ('wmic os get osarchitecture /value ^| find "="') do set arch=%%i

echo [💻] Windows Version: %winver%
echo [🏗️] Architecture: %arch%

REM Create necessary directories
echo [📁] Creating GODMODE directory structure...
if not exist "ai-gods" mkdir ai-gods
if not exist "portable-tools" mkdir portable-tools
if not exist "godmode-dashboard" mkdir godmode-dashboard
if not exist "godmode-tools" mkdir godmode-tools
if not exist "safety-nets" mkdir safety-nets
if not exist "cheat-codes" mkdir cheat-codes

REM Download and setup portable tools
echo [⬇️] Downloading portable development tools...
python godmode-setup\download-tools.py

REM Setup AI models
echo [🧠] Setting up local AI models...
python godmode-setup\setup-ai-models.py

REM Configure Git automatically
echo [🔧] Auto-configuring Git...
python godmode-setup\auto-git-config.py

REM Install dependencies
echo [📦] Installing all dependencies...
call npm install
cd backend && call npm install && cd ..
cd frontend && call npm install && cd ..

REM Run initial database setup
echo [🗄️] Setting up database...
cd backend && npm run migrate && cd ..

REM Create initialization flag
echo GODMODE-INITIALIZED > GODMODE-INITIALIZED.flag

echo [✅] GODMODE SYSTEM INITIALIZED SUCCESSFULLY!
echo [🚀] Proceeding to main execution...

goto MAIN_EXECUTION

REM ============================================================================
REM                           SAFE SHUTDOWN
REM ============================================================================

:SAFE_SHUTDOWN
echo [🛑] INITIATING SAFE GODMODE SHUTDOWN...

REM Save all work
echo [💾] Auto-saving all work...
python ai-gods\project-manager.py --save-all-work

REM Commit to Git
echo [📝] Auto-committing to Git...
git add .
git commit -m "🤖 GODMODE AI Session - Auto-save before shutdown"

REM Kill all processes gracefully
echo [🔄] Stopping AI Gods gracefully...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM node.exe >nul 2>&1

echo [✅] GODMODE SHUTDOWN COMPLETE
echo [💾] All work saved and committed to Git
echo [🔄] Run GODMODE-START.bat again to resume development
pause
exit

REM ============================================================================
REM                           ERROR HANDLING
REM ============================================================================

:ERROR_HANDLER
echo [🚨] GODMODE ERROR DETECTED - ACTIVATING EMERGENCY PROTOCOLS...
python safety-nets\emergency-recovery.py
echo [🔧] Attempting auto-recovery...
timeout /t 5
goto MAIN_EXECUTION
