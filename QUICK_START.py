#!/usr/bin/env python3
"""
🚀 FLOWSTATE-AI QUICK START
⚡ Rapid deployment script to get core AI agents operational
🎯 Focus: Get the system running fast with minimal configuration
"""

import os
import sys
import subprocess
import time
from pathlib import Path

# Set up the project root and Python path
PROJECT_ROOT = Path(__file__).parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))
os.environ["PYTHONPATH"] = str(PROJECT_ROOT)

print("🚀 FLOWSTATE-AI QUICK START")
print(f"📁 Project Root: {PROJECT_ROOT}")
print(f"🐍 Python: {sys.executable}")
print(f"📦 Python Path: {sys.path[0]}")
print()

# Check if pipenv is available
try:
    subprocess.run(["pipenv", "--version"], check=True, capture_output=True)
    PYTHON_CMD = ["pipenv", "run", "python"]
    print("✅ Using pipenv environment")
except (subprocess.CalledProcessError, FileNotFoundError):
    PYTHON_CMD = [sys.executable]
    print("⚠️  Pipenv not found, using system Python")

print()

# Start the backend server
print("🔧 Starting Node.js Backend...")
backend_process = subprocess.Popen(
    ["npm", "start"],
    cwd=PROJECT_ROOT / "backend",
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
)
print("✅ Backend starting on port 3001")
time.sleep(3)

# Start the GODMODE Orchestrator
print()
print("🤖 Starting GODMODE Orchestrator...")
orchestrator_cmd = PYTHON_CMD + ["-m", "ai_gods.godmode_orchestrator_v2"]
orchestrator_process = subprocess.Popen(
    orchestrator_cmd,
    cwd=PROJECT_ROOT,
    env={**os.environ, "PYTHONPATH": str(PROJECT_ROOT)},
)
print("✅ GODMODE Orchestrator started")
time.sleep(5)

# Start the frontend
print()
print("🎨 Starting Frontend...")
frontend_process = subprocess.Popen(
    ["npm", "run", "preview"],
    cwd=PROJECT_ROOT / "frontend",
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
)
print("✅ Frontend starting on port 4173")

print()
print("=" * 60)
print("🎉 FLOWSTATE-AI IS NOW RUNNING!")
print("=" * 60)
print()
print("📊 Access Points:")
print("   - Backend API: http://localhost:3001")
print("   - Frontend: http://localhost:4173")
print("   - Logs: ./godmode-logs/")
print()
print("🛑 Press Ctrl+C to stop all services")
print()

try:
    # Keep the script running
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print()
    print("🛑 Shutting down...")
    orchestrator_process.terminate()
    backend_process.terminate()
    frontend_process.terminate()
    print("✅ All services stopped")
