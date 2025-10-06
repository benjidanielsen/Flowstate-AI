#!/usr/bin/env python3
"""
🔧 GIT OPERATIONS TOOL
⚡ Handles all Git operations - commit, push, pull, branch management
🎯 Mission: Automate version control operations
"""

import subprocess
import logging
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('GitOperations')

class GitOperations:
    """Handles Git operations for the project"""
    
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.configure_git()
    
    def configure_git(self):
        """Configure git with default settings"""
        try:
            subprocess.run(['git', 'config', 'user.name', 'Flowstate-AI System'], 
                         cwd=self.repo_path, check=False, capture_output=True)
            subprocess.run(['git', 'config', 'user.email', 'system@flowstate-ai.dev'], 
                         cwd=self.repo_path, check=False, capture_output=True)
            logger.info("✅ Git configured")
        except Exception as e:
            logger.warning(f"⚠️  Could not configure git: {e}")
    
    def get_status(self) -> Dict:
        """Get current git status"""
        try:
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  cwd=self.repo_path, 
                                  capture_output=True, 
                                  text=True,
                                  check=True)
            
            lines = result.stdout.strip().split('\n') if result.stdout.strip() else []
            
            status = {
                'modified': [],
                'added': [],
                'deleted': [],
                'untracked': [],
                'total_changes': len(lines)
            }
            
            for line in lines:
                if not line:
                    continue
                
                status_code = line[:2]
                file_path = line[3:]
                
                if status_code.startswith('M'):
                    status['modified'].append(file_path)
                elif status_code.startswith('A'):
                    status['added'].append(file_path)
                elif status_code.startswith('D'):
                    status['deleted'].append(file_path)
                elif status_code.startswith('??'):
                    status['untracked'].append(file_path)
            
            return status
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to get git status: {e}")
            return {'error': str(e)}
    
    def add_files(self, files: Optional[List[str]] = None) -> bool:
        """Add files to staging area"""
        try:
            if files:
                for file in files:
                    subprocess.run(['git', 'add', file], 
                                 cwd=self.repo_path, 
                                 check=True,
                                 capture_output=True)
                logger.info(f"✅ Added {len(files)} files")
            else:
                subprocess.run(['git', 'add', '.'], 
                             cwd=self.repo_path, 
                             check=True,
                             capture_output=True)
                logger.info("✅ Added all changes")
            
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to add files: {e}")
            return False
    
    def commit(self, message: str) -> bool:
        """Commit staged changes"""
        try:
            result = subprocess.run(['git', 'commit', '-m', message], 
                                  cwd=self.repo_path, 
                                  capture_output=True,
                                  text=True)
            
            if result.returncode == 0:
                logger.info(f"✅ Committed: {message[:50]}...")
                return True
            else:
                logger.info("ℹ️  No changes to commit")
                return True
                
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to commit: {e}")
            return False
    
    def commit_all(self, message: str) -> bool:
        """Add all changes and commit"""
        if self.add_files():
            return self.commit(message)
        return False
    
    def get_current_branch(self) -> Optional[str]:
        """Get the name of the current branch"""
        try:
            result = subprocess.run(['git', 'branch', '--show-current'], 
                                  cwd=self.repo_path, 
                                  capture_output=True,
                                  text=True,
                                  check=True)
            
            branch = result.stdout.strip()
            logger.info(f"📍 Current branch: {branch}")
            return branch
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to get current branch: {e}")
            return None
    
    def create_branch(self, branch_name: str, checkout: bool = True) -> bool:
        """Create a new branch"""
        try:
            subprocess.run(['git', 'branch', branch_name], 
                         cwd=self.repo_path, 
                         check=True,
                         capture_output=True)
            
            logger.info(f"✅ Created branch: {branch_name}")
            
            if checkout:
                return self.checkout_branch(branch_name)
            
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to create branch: {e}")
            return False
    
    def checkout_branch(self, branch_name: str) -> bool:
        """Checkout a branch"""
        try:
            subprocess.run(['git', 'checkout', branch_name], 
                         cwd=self.repo_path, 
                         check=True,
                         capture_output=True)
            
            logger.info(f"✅ Checked out branch: {branch_name}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to checkout branch: {e}")
            return False
    
    def get_commit_log(self, count: int = 10) -> List[Dict]:
        """Get recent commit history"""
        try:
            result = subprocess.run(
                ['git', 'log', f'-{count}', '--pretty=format:%H|%an|%ae|%ad|%s'], 
                cwd=self.repo_path, 
                capture_output=True,
                text=True,
                check=True
            )
            
            commits = []
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                
                parts = line.split('|')
                if len(parts) >= 5:
                    commits.append({
                        'hash': parts[0],
                        'author_name': parts[1],
                        'author_email': parts[2],
                        'date': parts[3],
                        'message': parts[4]
                    })
            
            logger.info(f"📜 Retrieved {len(commits)} commits")
            return commits
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to get commit log: {e}")
            return []
    
    def get_diff(self, file_path: Optional[str] = None) -> str:
        """Get diff of changes"""
        try:
            cmd = ['git', 'diff']
            if file_path:
                cmd.append(file_path)
            
            result = subprocess.run(cmd, 
                                  cwd=self.repo_path, 
                                  capture_output=True,
                                  text=True,
                                  check=True)
            
            return result.stdout
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to get diff: {e}")
            return ""
    
    def create_smart_commit_message(self, status: Dict) -> str:
        """Generate a smart commit message based on changes"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        modified_count = len(status.get('modified', []))
        added_count = len(status.get('added', []))
        deleted_count = len(status.get('deleted', []))
        
        parts = []
        if added_count > 0:
            parts.append(f"Added {added_count} file(s)")
        if modified_count > 0:
            parts.append(f"Modified {modified_count} file(s)")
        if deleted_count > 0:
            parts.append(f"Deleted {deleted_count} file(s)")
        
        if not parts:
            return f"Update - {timestamp}"
        
        return f"Auto-commit: {', '.join(parts)} - {timestamp}"
    
    def auto_commit_changes(self) -> bool:
        """Automatically commit all changes with a smart message"""
        status = self.get_status()
        
        if status.get('total_changes', 0) == 0:
            logger.info("ℹ️  No changes to commit")
            return True
        
        message = self.create_smart_commit_message(status)
        return self.commit_all(message)
    
    def get_file_history(self, file_path: str, count: int = 5) -> List[Dict]:
        """Get commit history for a specific file"""
        try:
            result = subprocess.run(
                ['git', 'log', f'-{count}', '--pretty=format:%H|%an|%ad|%s', '--', file_path], 
                cwd=self.repo_path, 
                capture_output=True,
                text=True,
                check=True
            )
            
            commits = []
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                
                parts = line.split('|')
                if len(parts) >= 4:
                    commits.append({
                        'hash': parts[0],
                        'author': parts[1],
                        'date': parts[2],
                        'message': parts[3]
                    })
            
            return commits
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to get file history: {e}")
            return []

if __name__ == "__main__":
    print("🔧 Git Operations Tool")
    print("=" * 60)
    
    project_root = Path(__file__).parent.parent.parent
    git = GitOperations(project_root)
    
    print("\n📊 Current Status:")
    status = git.get_status()
    print(f"  Modified: {len(status.get('modified', []))}")
    print(f"  Added: {len(status.get('added', []))}")
    print(f"  Deleted: {len(status.get('deleted', []))}")
    print(f"  Untracked: {len(status.get('untracked', []))}")
    
    print(f"\n📍 Current Branch: {git.get_current_branch()}")
    
    print("\n📜 Recent Commits:")
    commits = git.get_commit_log(5)
    for i, commit in enumerate(commits, 1):
        print(f"  {i}. {commit['message'][:60]}")
        print(f"     by {commit['author_name']} on {commit['date']}")
    
    print("\n✅ Git Operations ready!")
