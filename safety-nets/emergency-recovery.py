#!/usr/bin/env python3
"""
Emergency Recovery for FlowState-AI GODMODE
Handles system crashes, hung processes, and error recovery
"""

import sys
import subprocess
import os
import signal
from pathlib import Path

class EmergencyRecovery:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        
    def kill_hanging_processes(self):
        """Kill any hanging FlowState-AI processes"""
        print("🚨 EMERGENCY RECOVERY ACTIVATED")
        print("📋 Checking for hanging processes...")
        
        processes_to_kill = [
            "python.*ai-gods",
            "python.*godmode-dashboard",
            "python.*MANUS_SYNC_ENGINE",
            "node.*dev",
            "node.*backend",
            "node.*frontend"
        ]
        
        killed_count = 0
        for process_pattern in processes_to_kill:
            try:
                result = subprocess.run(
                    ["pkill", "-9", "-f", process_pattern],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    killed_count += 1
                    print(f"  ✅ Killed processes matching: {process_pattern}")
            except Exception as e:
                print(f"  ⚠️  Could not kill {process_pattern}: {e}")
        
        if killed_count > 0:
            print(f"✅ Killed {killed_count} hanging process groups")
        else:
            print("ℹ️  No hanging processes found")
    
    def check_port_availability(self):
        """Check if required ports are available"""
        print("\n📊 Checking port availability...")
        
        ports_to_check = {
            3000: "Frontend",
            3001: "Backend API",
            3333: "GODMODE Dashboard"
        }
        
        for port, service in ports_to_check.items():
            try:
                result = subprocess.run(
                    ["lsof", "-i", f":{port}"],
                    capture_output=True,
                    text=True
                )
                if result.stdout:
                    print(f"  ⚠️  Port {port} ({service}) is in use")
                    # Try to free the port
                    subprocess.run(
                        ["fuser", "-k", f"{port}/tcp"],
                        capture_output=True
                    )
                    print(f"  ✅ Freed port {port}")
                else:
                    print(f"  ✅ Port {port} ({service}) is available")
            except Exception as e:
                print(f"  ℹ️  Could not check port {port}: {e}")
    
    def check_database_status(self):
        """Check if database is accessible"""
        print("\n💾 Checking database status...")
        
        db_paths = [
            self.project_root / "backend" / "data" / "flowstate.db",
            self.project_root / ".manus-sync" / "sync_engine.db",
            self.project_root / "maccs" / "coordination.db"
        ]
        
        for db_path in db_paths:
            if db_path.exists():
                print(f"  ✅ Database found: {db_path.name}")
                # Check if database is locked
                try:
                    import sqlite3
                    conn = sqlite3.connect(str(db_path), timeout=1.0)
                    conn.execute("SELECT 1")
                    conn.close()
                    print(f"  ✅ Database {db_path.name} is accessible")
                except sqlite3.OperationalError as e:
                    print(f"  ⚠️  Database {db_path.name} is locked: {e}")
                except Exception as e:
                    print(f"  ⚠️  Database {db_path.name} error: {e}")
            else:
                print(f"  ℹ️  Database not found: {db_path.name} (will be created on next run)")
    
    def check_git_status(self):
        """Check Git repository status"""
        print("\n📦 Checking Git status...")
        
        try:
            os.chdir(self.project_root)
            
            # Check for uncommitted changes
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True
            )
            
            if result.stdout.strip():
                print("  ⚠️  Uncommitted changes detected:")
                print(result.stdout)
            else:
                print("  ✅ Working directory is clean")
            
            # Check current branch
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True,
                text=True
            )
            branch = result.stdout.strip()
            print(f"  ℹ️  Current branch: {branch}")
            
        except Exception as e:
            print(f"  ⚠️  Could not check Git status: {e}")
    
    def cleanup_temp_files(self):
        """Clean up temporary files and logs"""
        print("\n🧹 Cleaning up temporary files...")
        
        patterns_to_clean = [
            "**/__pycache__",
            "**/*.pyc",
            "**/*.pyo",
            "**/.pytest_cache",
            "**/node_modules/.cache"
        ]
        
        cleaned_count = 0
        for pattern in patterns_to_clean:
            try:
                for path in self.project_root.rglob(pattern.split("/")[-1]):
                    if path.is_dir():
                        import shutil
                        shutil.rmtree(path, ignore_errors=True)
                        cleaned_count += 1
                    elif path.is_file():
                        path.unlink(missing_ok=True)
                        cleaned_count += 1
            except Exception as e:
                pass
        
        if cleaned_count > 0:
            print(f"  ✅ Cleaned {cleaned_count} temporary items")
        else:
            print("  ℹ️  No temporary files to clean")
    
    def provide_recovery_suggestions(self):
        """Provide suggestions for next steps"""
        print("\n💡 Recovery Suggestions:")
        print("  1. Try running GODMODE-START.sh again")
        print("  2. Check logs in godmode-dashboard/ for error details")
        print("  3. Verify all dependencies are installed:")
        print("     - cd backend && npm install")
        print("     - pip3 install -r requirements.txt (if exists)")
        print("  4. If issues persist, check GitHub for updates:")
        print("     - git pull origin main")
        print("  5. For database issues, backup and reset:")
        print("     - mv backend/data/flowstate.db backend/data/flowstate.db.backup")
        print("     - npm run migrate (in backend directory)")
    
    def run_full_recovery(self):
        """Run complete emergency recovery process"""
        print("=" * 60)
        print("🚨 FLOWSTATE-AI EMERGENCY RECOVERY")
        print("=" * 60)
        
        self.kill_hanging_processes()
        self.check_port_availability()
        self.check_database_status()
        self.check_git_status()
        self.cleanup_temp_files()
        self.provide_recovery_suggestions()
        
        print("\n" + "=" * 60)
        print("✅ Emergency recovery complete")
        print("=" * 60)

def main():
    recovery = EmergencyRecovery()
    recovery.run_full_recovery()
    return 0

if __name__ == "__main__":
    sys.exit(main())
