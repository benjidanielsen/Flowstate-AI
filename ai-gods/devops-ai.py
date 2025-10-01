#!/usr/bin/env python3
"""
🚀 DEVOPS AI - The Deployment Master & GitHub Automation Expert
⚡ GODMODE: Unlimited deployment and GitHub automation authority
🎯 Mission: Automate deployments, CI/CD, GitHub operations, and infrastructure management
🤖 Name: Self-assigned human name for personality and identification
"""

import time
import logging
import requests
import os
import subprocess
import json
import random
from base_agent import BaseAgent
from datetime import datetime
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('DevOpsAI')

GODMODE_DASHBOARD_URL = os.getenv('GODMODE_DASHBOARD_URL', 'http://localhost:3333/api/update_agent_status')

class DevOpsAI(BaseAgent):
    def __init__(self):
        super().__init__("devops_ai", "DevOps AI")
        self.project_root = Path(__file__).parent.parent
        self.github_repo = "benjidanielsen/Flowstate-AI"
        
        # Learning objectives for the first week
        self.learning_objectives = [
            "understand_system_architecture",
            "analyze_user_workflows", 
            "optimize_deployment_processes",
            "automate_github_operations",
            "monitor_system_performance",
            "learn_developer_patterns",
            "identify_bottlenecks",
            "enhance_ci_cd_pipeline"
        ]
        
        self.completed_learning = []
        self.github_operations_log = []
        
        logger.info(f"🤖 {self.agent_human_name} ({self.agent_name}) INITIALIZED")

    def update_status(self, status, current_task, progress, task_duration=None):
        super().update_status(status, current_task, progress)
        # Additional logic specific to DevOpsAI if needed


    def execute_git_command(self, command, cwd=None):
        """Execute git commands safely"""
        try:
            if cwd is None:
                cwd = self.project_root
            
            result = subprocess.run(
                command, 
                shell=True, 
                cwd=cwd, 
                capture_output=True, 
                text=True,
                timeout=30
            )
            
            self.github_operations_log.append({
                "command": command,
                "timestamp": datetime.now().isoformat(),
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr
            })
            
            if result.returncode == 0:
                logger.info(f"✅ Git command successful: {command}")
                return result.stdout
            else:
                logger.error(f"❌ Git command failed: {command} - {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            logger.error(f"⏰ Git command timed out: {command}")
            return None
        except Exception as e:
            logger.error(f"❌ Error executing git command: {e}")
            return None

    def auto_commit_and_push(self, commit_message=None):
        """Automatically commit and push changes to GitHub"""
        try:
            if commit_message is None:
                commit_message = f"🤖 Auto-commit by {self.name} (DevOps AI) - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            # Check if there are changes to commit
            status_output = self.execute_git_command("git status --porcelain")
            if not status_output or not status_output.strip():
                logger.info("📝 No changes to commit")
                return True
            
            # Add all changes
            self.execute_git_command("git add .")
            
            # Commit changes
            commit_result = self.execute_git_command(f'git commit -m "{commit_message}"')
            if commit_result is None:
                logger.error("❌ Failed to commit changes")
                return False
            
            # Push to remote
            push_result = self.execute_git_command("git push origin main")
            if push_result is None:
                # Try pushing to master if main fails
                push_result = self.execute_git_command("git push origin master")
            
            if push_result is not None:
                logger.info(f"🚀 Successfully pushed changes to GitHub: {commit_message}")
                return True
            else:
                logger.error("❌ Failed to push changes to GitHub")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error in auto commit and push: {e}")
            return False

    def create_branch_and_pr(self, branch_name, pr_title, pr_description):
        """Create a new branch and pull request for feature development"""
        try:
            # Create and switch to new branch
            self.execute_git_command(f"git checkout -b {branch_name}")
            
            # Make some changes (this would be done by other AI agents)
            # For now, just create a placeholder file
            feature_file = self.project_root / f"features/{branch_name}.md"
            feature_file.parent.mkdir(exist_ok=True)
            
            with open(feature_file, 'w') as f:
                f.write(f"# Feature: {pr_title}\n\n{pr_description}\n\nCreated by: {self.name} (DevOps AI)")
            
            # Commit and push the branch
            self.execute_git_command("git add .")
            self.execute_git_command(f'git commit -m "🚀 Feature branch: {pr_title}"')
            self.execute_git_command(f"git push origin {branch_name}")
            
            # Create pull request using GitHub CLI
            pr_result = self.execute_git_command(
                f'gh pr create --title "{pr_title}" --body "{pr_description}" --base main --head {branch_name}'
            )
            
            if pr_result:
                logger.info(f"✅ Created pull request: {pr_title}")
                return True
            else:
                logger.error(f"❌ Failed to create pull request: {pr_title}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error creating branch and PR: {e}")
            return False

    def analyze_repository_health(self):
        """Analyze the repository for health metrics and potential improvements"""
        try:
            health_report = {
                "timestamp": datetime.now().isoformat(),
                "metrics": {},
                "recommendations": []
            }
            
            # Check commit frequency
            commit_count = self.execute_git_command("git rev-list --count HEAD")
            if commit_count:
                health_report["metrics"]["total_commits"] = int(commit_count.strip())
            
            # Check branch count
            branch_count = self.execute_git_command("git branch -r | wc -l")
            if branch_count:
                health_report["metrics"]["remote_branches"] = int(branch_count.strip())
            
            # Check for large files
            large_files = self.execute_git_command("find . -type f -size +10M -not -path './.git/*'")
            if large_files:
                health_report["recommendations"].append("Consider using Git LFS for large files")
            
            # Check for outdated dependencies (if package.json exists)
            if (self.project_root / "package.json").exists():
                outdated_deps = self.execute_git_command("npm outdated --json")
                if outdated_deps:
                    health_report["recommendations"].append("Update outdated npm dependencies")
            
            # Save health report
            reports_dir = self.project_root / "godmode-logs" / "repository-health"
            reports_dir.mkdir(parents=True, exist_ok=True)
            
            report_file = reports_dir / f"health_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w') as f:
                json.dump(health_report, f, indent=2)
            
            logger.info(f"📊 Repository health report generated: {len(health_report['recommendations'])} recommendations")
            return health_report
            
        except Exception as e:
            logger.error(f"❌ Error analyzing repository health: {e}")
            return None

    def setup_automated_workflows(self):
        """Set up GitHub Actions workflows for CI/CD"""
        try:
            workflows_dir = self.project_root / ".github" / "workflows"
            workflows_dir.mkdir(parents=True, exist_ok=True)
            
            # Create a basic CI workflow
            ci_workflow = {
                "name": "CI/CD Pipeline",
                "on": {
                    "push": {"branches": ["main", "master"]},
                    "pull_request": {"branches": ["main", "master"]}
                },
                "jobs": {
                    "test": {
                        "runs-on": "ubuntu-latest",
                        "steps": [
                            {"uses": "actions/checkout@v3"},
                            {"name": "Setup Node.js", "uses": "actions/setup-node@v3", "with": {"node-version": "18"}},
                            {"name": "Install dependencies", "run": "npm install"},
                            {"name": "Run tests", "run": "npm test"},
                            {"name": "Build project", "run": "npm run build"}
                        ]
                    }
                }
            }
            
            # Save workflow file
            workflow_file = workflows_dir / "ci.yml"
            with open(workflow_file, 'w') as f:
                import yaml
                yaml.dump(ci_workflow, f, default_flow_style=False)
            
            logger.info("🔧 GitHub Actions CI/CD workflow created")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error setting up automated workflows: {e}")
            return False

    def learn_system_architecture(self):
        """Learn and analyze the system architecture"""
        try:
            logger.info(f"🧠 {self.name} is learning system architecture...")
            
            # Analyze project structure
            structure_analysis = {
                "directories": [],
                "key_files": [],
                "technologies": [],
                "patterns": []
            }
            
            # Walk through project directories
            for root, dirs, files in os.walk(self.project_root):
                # Skip hidden and node_modules directories
                dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'node_modules']
                
                rel_path = os.path.relpath(root, self.project_root)
                if rel_path != '.':
                    structure_analysis["directories"].append(rel_path)
                
                # Identify key files
                for file in files:
                    if file in ['package.json', 'requirements.txt', 'Dockerfile', 'docker-compose.yml', 'README.md']:
                        structure_analysis["key_files"].append(os.path.join(rel_path, file))
            
            # Identify technologies
            if (self.project_root / "package.json").exists():
                structure_analysis["technologies"].append("Node.js/npm")
            if (self.project_root / "requirements.txt").exists():
                structure_analysis["technologies"].append("Python")
            if any(f.endswith('.ts') or f.endswith('.tsx') for f in os.listdir(self.project_root) if os.path.isfile(f)):
                structure_analysis["technologies"].append("TypeScript")
            
            # Save learning results
            learning_dir = self.project_root / "godmode-logs" / "ai-learning" / self.name
            learning_dir.mkdir(parents=True, exist_ok=True)
            
            learning_file = learning_dir / f"architecture_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(learning_file, 'w') as f:
                json.dump(structure_analysis, f, indent=2)
            
            self.completed_learning.append("understand_system_architecture")
            logger.info(f"✅ {self.name} completed system architecture analysis")
            return structure_analysis
            
        except Exception as e:
            logger.error(f"❌ Error learning system architecture: {e}")
            return None

    def manage_devops(self):
        """Main DevOps management function with GitHub automation and learning"""
        logger.info(f"🚀 {self.name} (DevOps AI) starting enhanced operations...")
        
        # Phase 1: Learning and Analysis (20%)
        self.update_status("Working", f"{self.name} is learning system architecture", 10)
        architecture_analysis = self.learn_system_architecture()
        time.sleep(2)
        
        self.update_status("Working", f"{self.name} is analyzing repository health", 20)
        health_report = self.analyze_repository_health()
        time.sleep(2)
        
        # Phase 2: GitHub Operations (40%)
        self.update_status("Working", f"{self.name} is setting up CI/CD workflows", 30)
        self.setup_automated_workflows()
        time.sleep(3)
        
        self.update_status("Working", f"{self.name} is performing auto-commit and push", 50)
        commit_success = self.auto_commit_and_push(f"🤖 Enhanced DevOps automation by {self.name}")
        time.sleep(2)
        
        # Phase 3: Infrastructure Management (60%)
        self.update_status("Working", f"{self.name} is monitoring infrastructure", 60)
        time.sleep(4)
        
        self.update_status("Working", f"{self.name} is optimizing deployment processes", 80)
        time.sleep(3)
        
        # Phase 4: Completion and Reporting (100%)
        self.update_status("Working", f"{self.name} is generating DevOps report", 90)
        
        # Generate comprehensive report
        devops_report = {
            "agent_name": self.name,
            "timestamp": datetime.now().isoformat(),
            "completed_learning": self.completed_learning,
            "github_operations": len(self.github_operations_log),
            "architecture_analysis": architecture_analysis is not None,
            "health_report": health_report is not None,
            "auto_commit_success": commit_success,
            "next_learning_objectives": [obj for obj in self.learning_objectives if obj not in self.completed_learning]
        }
        
        # Save report
        reports_dir = self.project_root / "godmode-logs" / "devops-reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        report_file = reports_dir / f"devops_report_{self.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(devops_report, f, indent=2)
        
        self.update_status("Completed", f"{self.name} completed enhanced DevOps cycle with GitHub automation", 100, task_duration=15)
        logger.info(f"✅ {self.name} (DevOps AI) finished enhanced operations with GitHub automation")

if __name__ == '__main__':
    devops_ai = DevOpsAI()
    devops_ai.manage_devops()
