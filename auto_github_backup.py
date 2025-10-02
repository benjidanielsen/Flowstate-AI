#!/usr/bin/env python3
"""
🔄 AUTOMATED GITHUB BACKUP SYSTEM
Automatically commits and pushes changes to GitHub every 5 minutes
"""

import subprocess
import time
import os
from datetime import datetime
from pathlib import Path

# Configuration
REPO_PATH = Path("/home/ubuntu/Flowstate-AI")
BACKUP_INTERVAL = 300  # 5 minutes in seconds
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
REPO_URL = f"https://{GITHUB_TOKEN}@github.com/benjidanielsen/Flowstate-AI.git" if GITHUB_TOKEN else "https://github.com/benjidanielsen/Flowstate-AI.git"

def run_command(command, cwd=None):
    """Execute a shell command and return the result."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd or REPO_PATH,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        print(f"❌ Command timed out: {command}")
        return False, "", "Timeout"
    except Exception as e:
        print(f"❌ Error executing command: {e}")
        return False, "", str(e)

def configure_git():
    """Configure Git with credentials."""
    print("🔧 Configuring Git...")
    run_command("git config user.name 'Manus AI'")
    run_command("git config user.email 'manus@flowstate-ai.local'")
    run_command(f"git remote set-url origin {REPO_URL}")
    print("✅ Git configured")

def check_for_changes():
    """Check if there are any changes to commit."""
    success, stdout, _ = run_command("git status --porcelain")
    return success and len(stdout.strip()) > 0

def commit_and_push():
    """Commit and push changes to GitHub."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Pull first to get latest changes
    print(f"🔄 [{timestamp}] Pulling latest changes...")
    pull_success, _, pull_error = run_command("git pull origin main --no-edit")
    if not pull_success and "Already up to date" not in pull_error:
        print(f"⚠️  Pull had issues: {pull_error}")
    
    # Check for changes after pull
    if not check_for_changes():
        print(f"⏭️  [{timestamp}] No changes to commit")
        return True
    
    print(f"📝 [{timestamp}] Changes detected, committing...")
    
    # Add all changes
    success, _, error = run_command("git add -A")
    if not success:
        print(f"❌ Failed to add changes: {error}")
        return False
    
    # Commit changes
    commit_message = f"🤖 Automated backup: {timestamp}"
    success, _, error = run_command(f'git commit -m "{commit_message}"')
    if not success:
        print(f"❌ Failed to commit: {error}")
        return False
    
    # Push to GitHub
    print(f"⬆️  Pushing to GitHub...")
    success, stdout, error = run_command("git push origin main")
    if not success:
        print(f"❌ Failed to push: {error}")
        return False
    
    print(f"✅ [{timestamp}] Successfully backed up to GitHub")
    return True

def main():
    """Main backup loop."""
    print("🚀 Starting Automated GitHub Backup System")
    print(f"📁 Repository: {REPO_PATH}")
    print(f"⏰ Backup interval: {BACKUP_INTERVAL} seconds (5 minutes)")
    print("=" * 60)
    
    # Initial Git configuration
    configure_git()
    
    # Initial backup
    commit_and_push()
    
    # Continuous backup loop
    backup_count = 0
    while True:
        try:
            time.sleep(BACKUP_INTERVAL)
            backup_count += 1
            print(f"\n🔄 Backup #{backup_count}")
            commit_and_push()
        except KeyboardInterrupt:
            print("\n\n🛑 Backup system stopped by user")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            print("⏳ Waiting 60 seconds before retry...")
            time.sleep(60)

if __name__ == "__main__":
    main()
