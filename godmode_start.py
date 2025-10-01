import subprocess
import sys
import os
import time
import logging
import psutil
from pathlib import Path
import signal

# --- Configuration ---
LOG_DIR = Path("godmode-logs")
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "godmode_start.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("GODMODE_START")

PROJECT_ROOT = Path(__file__).parent

# Define color codes for console output (cross-platform compatible)
class Colors:
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'

processes = []

# --- Helper Functions ---
def run_command(name, cmd, cwd=PROJECT_ROOT, shell=False, check=False, capture_output=False):
    cmd_str = ' '.join(cmd) if isinstance(cmd, list) else cmd
    logger.info(f"{Colors.CYAN}Attempting to run {name}: {cmd_str} in {cwd}{Colors.RESET}")
    try:
        process = subprocess.Popen(cmd, cwd=cwd, shell=shell, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if check:
            stdout, stderr = process.communicate(timeout=120) # Increased timeout for npm installs
            if process.returncode != 0:
                logger.error(f"{Colors.RED}{name} failed with error: {stderr.strip()}{Colors.RESET}")
                return False
            logger.info(f"{Colors.GREEN}{name} completed successfully.{Colors.RESET}")
            return True
        else:
            processes.append({"name": name, "process": process, "stdout": process.stdout, "stderr": process.stderr})
            logger.info(f"{Colors.GREEN}{name} started successfully with PID: {process.pid}{Colors.RESET}")
            return process
    except subprocess.TimeoutExpired:
        process.kill()
        stdout, stderr = process.communicate()
        logger.error(f"{Colors.RED}{name} timed out. Stderr: {stderr.strip()}{Colors.RESET}")
        return False
    except Exception as e:
        logger.error(f"{Colors.RED}Failed to run {name}: {e}{Colors.RESET}")
        return False

def kill_process_tree(pid):
    try:
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)
        for child in children:
            child.terminate()
        parent.terminate()
        gone, alive = psutil.wait_procs(children + [parent], timeout=5)
        for p in alive:
            p.kill()
        logger.info(f"{Colors.YELLOW}Killed process tree for PID {pid}{Colors.RESET}")
    except psutil.NoSuchProcess:
        logger.warning(f"{Colors.YELLOW}Process {pid} not found, likely already terminated.{Colors.RESET}")
    except Exception as e:
        logger.error(f"{Colors.RED}Error killing process tree for PID {pid}: {e}{Colors.RESET}")

def cleanup_processes():
    logger.info(f"{Colors.YELLOW}Initiating cleanup of all spawned processes...{Colors.RESET}")
    for p_info in processes:
        proc = p_info["process"]
        if proc.poll() is None:  # Process is still running
            logger.info(f"{Colors.YELLOW}Terminating {p_info['name']} (PID: {proc.pid})...{Colors.RESET}")
            kill_process_tree(proc.pid)
    logger.info(f"{Colors.GREEN}All processes cleaned up.{Colors.RESET}")

def signal_handler(sig, frame):
    logger.info(f"{Colors.YELLOW}Signal {sig} received. Shutting down...{Colors.RESET}")
    cleanup_processes()
    sys.exit(0)

# Register signal handlers for graceful shutdown
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def pre_startup_check_and_fix(project_root):
    logger.info(f"{Colors.BLUE}Running pre-startup checks and fixes...{Colors.RESET}")

    # Check Python dependencies (psutil)
    try:
        import psutil
        logger.info(f"{Colors.GREEN}psutil is installed.{Colors.RESET}")
    except ImportError:
        logger.warning(f"{Colors.YELLOW}psutil not found. Installing...{Colors.RESET}")
        if not run_command("pip install psutil", [sys.executable, "-m", "pip", "install", "psutil"], check=True):
            logger.error(f"{Colors.RED}Failed to install psutil. Please install it manually: pip install psutil{Colors.RESET}")
            sys.exit(1)

    # Check Node.js Backend dependencies
    backend_path = project_root / "backend"
    if backend_path.exists():
        if not (backend_path / "node_modules").exists():
            logger.warning(f"{Colors.YELLOW}Backend node_modules not found. Installing dependencies...{Colors.RESET}")
            if not run_command("Backend npm install", "npm install", cwd=backend_path, shell=True, check=True):
                logger.error(f"{Colors.RED}Backend npm install failed. Please check the logs for details.{Colors.RESET}")
                sys.exit(1)
        else:
            logger.info(f"{Colors.GREEN}Backend node_modules found.{Colors.RESET}")

        # Run database migrations
        logger.info(f"{Colors.BLUE}Running backend database migrations...{Colors.RESET}")
        if not run_command("Backend db:migrate", "npm run db:migrate", cwd=backend_path, shell=True, check=True):
            logger.error(f"{Colors.RED}Backend db:migrate failed. Please check the logs for details.{Colors.RESET}")
            sys.exit(1)
    else:
        logger.error(f"{Colors.RED}Backend directory not found at {backend_path}. Cannot perform backend checks.{Colors.RESET}")

    # Check Node.js Frontend dependencies
    frontend_path = project_root / "frontend"
    if frontend_path.exists():
        if not (frontend_path / "node_modules").exists():
            logger.warning(f"{Colors.YELLOW}Frontend node_modules not found. Installing dependencies...{Colors.RESET}")
            if not run_command("Frontend npm install", "npm install", cwd=frontend_path, shell=True, check=True):
                logger.error(f"{Colors.RED}Failed to install frontend dependencies. Please run \'npm install\' in the frontend directory manually.{Colors.RESET}")
                sys.exit(1)
        else:
            logger.info(f"{Colors.GREEN}Frontend node_modules found.{Colors.RESET}")
    else:
        logger.error(f"{Colors.RED}Frontend directory not found at {frontend_path}. Cannot perform frontend checks.{Colors.RESET}")

    logger.info(f"{Colors.GREEN}Pre-startup checks and fixes completed successfully.{Colors.RESET}")

if __name__ == "__main__":
    project_root = Path(__file__).parent
    os.chdir(project_root) # Ensure we are in the project root

    # Create godmode-logs directory if it doesn't exist
    (project_root / "godmode-logs").mkdir(exist_ok=True)

    logger.info(f"{Colors.BLUE}Starting GODMODE AI System...{Colors.RESET}")

    pre_startup_check_and_fix(project_root)

    # 1. Start Flask Dashboard
    dashboard_path = project_root / "godmode-dashboard"
    if dashboard_path.exists():
        run_command("GODMODE Dashboard", [sys.executable, "app.py"], cwd=dashboard_path)
    else:
        logger.error(f"{Colors.RED}GODMODE Dashboard directory not found at {dashboard_path}{Colors.RESET}")

    # 2. Start Node.js Backend
    backend_path = project_root / "backend"
    if backend_path.exists():
        run_command("Node.js Backend", "npm run start", cwd=backend_path, shell=True)
    else:
        logger.error(f"{Colors.RED}Backend directory not found at {backend_path}{Colors.RESET}")

    # 3. Start Node.js Frontend
    frontend_path = project_root / "frontend"
    if frontend_path.exists():
        run_command("Node.js Frontend", "npm run dev", cwd=frontend_path, shell=True)
    else:
        logger.error(f"{Colors.RED}Frontend directory not found at {frontend_path}{Colors.RESET}")

    # 4. Start Python AI Agents
    ai_gods_path = project_root / "ai-gods"
    if ai_gods_path.exists():
        ai_scripts = [
            "project-manager.py",
            "backend-developer.py",
            "frontend-developer.py",
            "database-ai.py",
            "tester-ai.py",
            "fixer-ai.py",
            "devops-ai.py",
            "documentation-ai.py",
            "support-ai.py",
            "innovation-ai.py",
            "ai-communication-hub.py",
            "collective-memory-system.py"
        ]
        for script in ai_scripts:
            script_path = ai_gods_path / script
            if script_path.exists():
                run_command(f"AI Agent: {script}", [sys.executable, str(script_path)], cwd=project_root)
            else:
                logger.warning(f"{Colors.YELLOW}AI Agent script not found: {script_path}. Skipping.{Colors.RESET}")
    else:
        logger.error(f"{Colors.RED}AI Gods directory not found at {ai_gods_path}{Colors.RESET}")

    logger.info(f"{Colors.GREEN}GODMODE AI System initialization complete. Monitoring processes...{Colors.RESET}")
    logger.info(f"{Colors.BLUE}Dashboard: http://localhost:3333{Colors.RESET}")
    logger.info(f"{Colors.BLUE}Frontend: http://localhost:3000{Colors.RESET}")
    logger.info(f"{Colors.BLUE}Backend API: http://localhost:3001{Colors.RESET}")

    try:
        while True:
            # Periodically check if processes are still running
            for p_info in list(processes): # Iterate over a copy to allow removal
                proc = p_info["process"]
                if proc.poll() is not None: # Process has terminated
                    logger.warning(f"{Colors.RED}{p_info['name']} (PID: {proc.pid}) has terminated with exit code {proc.returncode}.{Colors.RESET}")
                    processes.remove(p_info)
            if not processes:
                logger.warning(f"{Colors.RED}All core GODMODE processes have terminated. Shutting down.{Colors.RESET}")
                break
            time.sleep(5)
    except KeyboardInterrupt:
        logger.info(f"{Colors.YELLOW}KeyboardInterrupt received. Shutting down...{Colors.RESET}")
    finally:
        cleanup_processes()
        logger.info(f"{Colors.GREEN}GODMODE AI System shutdown complete.{Colors.RESET}")


