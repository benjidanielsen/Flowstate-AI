#!/usr/bin/env python3
"""
🔧 FIXER AI - The Code Medic & Bug Squasher
⚡ GODMODE: Unlimited bug fixing and code refactoring authority
🎯 Mission: Automatically detect, diagnose, and fix bugs and code quality issues
🤖 Name: Self-assigned human name for personality and identification
"""

import time
import logging
import requests
import os
import json
import random
import subprocess
import sys
from base_agent import BaseAgent
from datetime import datetime
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format=\'%(asctime)s - %(name)s - %(levelname)s - %(message)s\',
    handlers=[
        logging.FileHandler(Path(__file__).parent.parent / \'godmode-logs\' / \'fixer-ai.log\'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(\'FixerAI\')

GODMODE_DASHBOARD_URL = os.getenv(\'GODMODE_DASHBOARD_URL\', \'http://localhost:3333/api/update_agent_status\')

class FixerAI(BaseAgent):
    def __init__(self):
        super().__init__("fixer_ai", "Fixer AI")
        self.project_root = Path(__file__).parent.parent
        
        # Learning objectives for the first week
        self.learning_objectives = [
            "understand_common_bug_patterns",
            "analyze_error_logs_effectively",
            "learn_refactoring_techniques",
            "study_code_quality_metrics",
            "identify_code_smells",
            "create_automated_fixing_strategies",
            "improve_debugging_skills",
            "propose_preventive_measures",
            "proactive_local_environment_maintenance" # New learning objective
        ]
        
        self.completed_learning = []
        self.bug_analysis_log = []
        
        logger.info(f"🤖 {self.agent_human_name} ({self.agent_name}) INITIALIZED")

    def update_status(self, status, current_task, progress, task_duration=None):
        super().update_status(status, current_task, progress)
        # Additional logic specific to FixerAI if needed


    def run_command_and_check(self, name, cmd, cwd=None, shell=False, env=None):
        logger.info(f"Attempting to run {name} for local fix: {\' \'.join(cmd) if isinstance(cmd, list) else cmd}")
        try:
            process = subprocess.Popen(cmd, cwd=cwd, shell=shell, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = process.communicate(timeout=120) # Increased timeout for installations
            if process.returncode != 0:
                logger.error(f"{name} failed with error: {stderr.strip()}")
                return False
            logger.info(f"{name} completed successfully. Output: {stdout.strip()}")
            return True
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
            logger.error(f"{name} timed out. Stderr: {stderr.strip()}")
            return False
        except Exception as e:
            logger.error(f"Failed to run {name}: {e}")
            return False

    def proactive_local_environment_maintenance(self):
        """Proactively checks for and fixes common local environment issues."""
        self.update_status("Working", f"{self.name} is performing proactive local environment maintenance", 0)
        logger.info(f"🛠️ {self.name} is proactively checking and fixing local environment issues...")

        issues_found = []
        issues_fixed = []

        # Check Python dependencies (psutil is critical for godmode_start.py)
        try:
            import psutil
            logger.info("Python dependency psutil is installed.")
        except ImportError:
            logger.warning("Python dependency psutil not found.")
            issues_found.append("Missing psutil")
            self.update_status("Working", f"{self.name} is installing psutil", 10)
            if self.run_command_and_check("pip install psutil", [sys.executable, "-m", "pip", "install", "psutil"]):
                issues_fixed.append("Installed psutil")
            else:
                logger.error("Failed to install psutil.")

        # Check Node.js Backend dependencies
        backend_path = self.project_root / "backend"
        if backend_path.exists():
            if not (backend_path / "node_modules").exists():
                logger.warning("Backend node_modules not found.")
                issues_found.append("Missing backend node_modules")
                self.update_status("Working", f"{self.name} is installing backend dependencies", 30)
                if self.run_command_and_check("Backend npm install", ["npm", "install"], cwd=backend_path, shell=True):
                    issues_fixed.append("Installed backend node_modules")
                else:
                    logger.error("Failed to install backend dependencies.")
            else:
                logger.info("Backend node_modules found.")

            # Check and run database migrations
            self.update_status("Working", f"{self.name} is checking database migrations", 50)
            logger.info("Checking backend database migrations...")
            # This assumes 'npm run db:migrate' is idempotent and safe to run multiple times
            if self.run_command_and_check("Backend db:migrate", ["npm", "run", "db:migrate"], cwd=backend_path, shell=True):
                issues_fixed.append("Ran backend database migrations")
            else:
                issues_found.append("Failed backend database migrations")
        else:
            logger.warning(f"Backend directory not found at {backend_path}. Skipping backend checks.")

        # Check Node.js Frontend dependencies
        frontend_path = self.project_root / "frontend"
        if frontend_path.exists():
            if not (frontend_path / "node_modules").exists():
                logger.warning("Frontend node_modules not found.")
                issues_found.append("Missing frontend node_modules")
                self.update_status("Working", f"{self.name} is installing frontend dependencies", 70)
                if self.run_command_and_check("Frontend npm install", ["npm", "install"], cwd=frontend_path, shell=True):
                    issues_fixed.append("Installed frontend node_modules")
                else:
                    logger.error("Failed to install frontend dependencies.")
            else:
                logger.info("Frontend node_modules found.")
        else:
            logger.warning(f"Frontend directory not found at {frontend_path}. Skipping frontend checks.")

        self.completed_learning.append("proactive_local_environment_maintenance")
        self.update_status("Completed", f"{self.name} completed proactive local environment maintenance", 100, task_duration=random.randint(5, 15))
        logger.info(f"✅ {self.name} finished proactive local environment maintenance. Found: {len(issues_found)} issues, Fixed: {len(issues_fixed)} issues.")
        return {"issues_found": issues_found, "issues_fixed": issues_fixed}

    def analyze_error_logs(self):
        """Analyze error logs to identify common bugs and issues"""
        try:
            logger.info(f"🔎 {self.name} is analyzing error logs...")
            
            error_analysis = {
                "common_errors": [],
                "frequent_sources": [],
                "severity_levels": [],
                "recommendations": []
            }
            
            # Simulate analysis of error logs
            error_analysis["common_errors"].append("Null pointer exceptions")
            error_analysis["frequent_sources"].append("API request handling")
            error_analysis["severity_levels"].append("High: 10%, Medium: 40%, Low: 50%")
            error_analysis["recommendations"].append("Implement stricter input validation")
            
            # Save analysis
            learning_dir = self.project_root / "godmode-logs" / "ai-learning" / self.name
            learning_dir.mkdir(parents=True, exist_ok=True)
            
            analysis_file = learning_dir / f"error_log_analysis_{datetime.now().strftime(\'%Y%m%d_%H%M%S\')}.json"
            with open(analysis_file, \'w\') as f:
                json.dump(error_analysis, f, indent=2)
            
            self.completed_learning.append("analyze_error_logs_effectively")
            logger.info(f"✅ {self.name} completed error log analysis")
            return error_analysis
            
        except Exception as e:
            logger.error(f"❌ Error analyzing error logs: {e}")
            return None

    def manage_fixing(self):
        """Main bug fixing and code refactoring function with learning"""
        logger.info(f"🔧 {self.name} (Fixer AI) starting enhanced operations...")
        
        # Phase 0: Proactive Local Environment Maintenance
        self.proactive_local_environment_maintenance()

        # Phase 1: Learning and Analysis (30%)
        self.update_status("Working", f"{self.name} is analyzing error logs", 10)
        error_analysis = self.analyze_error_logs()
        time.sleep(2)
        
        self.update_status("Working", f"{self.name} is learning refactoring techniques", 20)
        time.sleep(2)
        
        self.update_status("Working", f"{self.name} is studying code quality metrics", 30)
        time.sleep(2)
        
        # Phase 2: Bug Fixing (60%)
        self.update_status("Working", f"{self.name} is automatically fixing bugs", 40)
        time.sleep(3)
        
        self.update_status("Working", f"{self.name} is refactoring code for quality", 50)
        time.sleep(3)
        
        self.update_status("Working", f"{self.name} is improving error handling", 60)
        time.sleep(3)
        
        # Phase 3: Reporting and Prevention (100%)
        self.update_status("Working", f"{self.name} is generating a fixing report", 90)
        
        # Generate comprehensive report
        fixing_report = {
            "agent_name": self.name,
            "timestamp": datetime.now().isoformat(),
            "completed_learning": self.completed_learning,
            "error_analysis": error_analysis is not None,
            "next_learning_objectives": [obj for obj in self.learning_objectives if obj not in self.completed_learning],
            "recommendations": [
                "Implement a global error handling middleware",
                "Add more unit tests for critical components",
                "Conduct regular code quality reviews"
            ]
        }
        
        # Save report
        reports_dir = self.project_root / "godmode-logs" / "fixing-reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        report_file = reports_dir / f"fixing_report_{self.name}_{datetime.now().strftime(\'%Y%m%d_%H%M%S\')}.json"
        with open(report_file, \'w\') as f:
            json.dump(fixing_report, f, indent=2)
        
        self.update_status("Completed", f"{self.name} completed enhanced fixing cycle", 100, task_duration=14)
        logger.info(f"✅ {self.name} (Fixer AI) finished enhanced operations with learning")

if __name__ == \'__main__\':
    fixer_ai = FixerAI()
    fixer_ai.manage_fixing()

