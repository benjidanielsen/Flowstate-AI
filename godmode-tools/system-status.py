#!/usr/bin/env python3
"""
System Status Monitor for FlowState-AI GODMODE
Provides real-time status of all system components
"""

import sys
import subprocess
import os
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import json

class SystemStatus:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        
    def get_running_processes(self):
        """Get all running FlowState-AI processes"""
        print("🤖 AI Gods & Processes Status:")
        print("=" * 60)
        
        process_patterns = {
            "Project Manager": "python.*project-manager.py",
            "AI Communication Hub": "python.*ai-communication-hub.py",
            "AI Democracy": "python.*ai-democracy-system.py",
            "Collective Memory": "python.*collective-memory-system.py",
            "Innovation AI": "python.*innovation-ai.py",
            "GODMODE Dashboard": "python.*godmode-dashboard",
            "Sync Engine": "python.*MANUS_SYNC_ENGINE",
            "Backend API": "node.*backend",
            "Frontend Dev": "node.*frontend"
        }
        
        running_count = 0
        for name, pattern in process_patterns.items():
            try:
                result = subprocess.run(
                    ["pgrep", "-f", pattern],
                    capture_output=True,
                    text=True
                )
                if result.stdout.strip():
                    pids = result.stdout.strip().split("\n")
                    print(f"  ✅ {name:<25} Running (PID: {', '.join(pids)})")
                    running_count += 1
                else:
                    print(f"  ❌ {name:<25} Not running")
            except Exception as e:
                print(f"  ⚠️  {name:<25} Status unknown: {e}")
        
        print(f"\n📊 Total: {running_count}/{len(process_patterns)} processes running\n")
        return running_count
    
    def check_port_status(self):
        """Check status of required ports"""
        print("🌐 Port Status:")
        print("=" * 60)
        
        ports = {
            3000: "Frontend (React)",
            3001: "Backend API (Express)",
            3333: "GODMODE Dashboard"
        }
        
        available_count = 0
        for port, service in ports.items():
            try:
                result = subprocess.run(
                    ["lsof", "-i", f":{port}"],
                    capture_output=True,
                    text=True
                )
                if result.stdout:
                    # Port is in use
                    lines = result.stdout.strip().split("\n")
                    if len(lines) > 1:
                        # Extract process info from second line
                        parts = lines[1].split()
                        process_name = parts[0] if parts else "unknown"
                        pid = parts[1] if len(parts) > 1 else "unknown"
                        print(f"  ✅ Port {port:<5} {service:<25} In use by {process_name} (PID: {pid})")
                    else:
                        print(f"  ✅ Port {port:<5} {service:<25} In use")
                else:
                    print(f"  ⚪ Port {port:<5} {service:<25} Available (not in use)")
                    available_count += 1
            except Exception as e:
                print(f"  ⚠️  Port {port:<5} {service:<25} Status unknown")
        
        print()
        return available_count
    
    def check_database_status(self):
        """Check database health and statistics"""
        print("💾 Database Status:")
        print("=" * 60)
        
        databases = [
            ("Main CRM", self.project_root / "backend" / "data" / "flowstate.db"),
            ("Sync Engine", self.project_root / ".manus-sync" / "sync_engine.db"),
            ("MACCS Coordination", self.project_root / "maccs" / "coordination.db")
        ]
        
        for name, db_path in databases:
            if db_path.exists():
                try:
                    conn = sqlite3.connect(str(db_path), timeout=1.0)
                    cursor = conn.cursor()
                    
                    # Get database size
                    size_bytes = db_path.stat().st_size
                    size_kb = size_bytes / 1024
                    
                    # Get table count
                    cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
                    table_count = cursor.fetchone()[0]
                    
                    # Get last modified time
                    mtime = datetime.fromtimestamp(db_path.stat().st_mtime)
                    time_ago = datetime.now() - mtime
                    
                    if time_ago.total_seconds() < 60:
                        time_str = f"{int(time_ago.total_seconds())}s ago"
                    elif time_ago.total_seconds() < 3600:
                        time_str = f"{int(time_ago.total_seconds() / 60)}m ago"
                    else:
                        time_str = f"{int(time_ago.total_seconds() / 3600)}h ago"
                    
                    print(f"  ✅ {name:<20} {size_kb:.1f} KB, {table_count} tables, modified {time_str}")
                    
                    conn.close()
                except sqlite3.OperationalError:
                    print(f"  ⚠️  {name:<20} Locked (in use by another process)")
                except Exception as e:
                    print(f"  ⚠️  {name:<20} Error: {e}")
            else:
                print(f"  ⚪ {name:<20} Not created yet")
        
        print()
    
    def check_git_status(self):
        """Check Git repository status"""
        print("📦 Git Repository Status:")
        print("=" * 60)
        
        try:
            os.chdir(self.project_root)
            
            # Get current branch
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True,
                text=True
            )
            branch = result.stdout.strip()
            print(f"  📍 Current branch: {branch}")
            
            # Check for uncommitted changes
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True
            )
            
            if result.stdout.strip():
                lines = result.stdout.strip().split("\n")
                print(f"  ⚠️  Uncommitted changes: {len(lines)} files")
            else:
                print(f"  ✅ Working directory clean")
            
            # Get last commit info
            result = subprocess.run(
                ["git", "log", "-1", "--pretty=format:%h - %s (%cr)"],
                capture_output=True,
                text=True
            )
            if result.stdout:
                print(f"  📝 Last commit: {result.stdout}")
            
            # Check if ahead/behind remote
            result = subprocess.run(
                ["git", "rev-list", "--left-right", "--count", "origin/main...HEAD"],
                capture_output=True,
                text=True
            )
            if result.stdout:
                behind, ahead = result.stdout.strip().split()
                if int(behind) > 0:
                    print(f"  ⬇️  Behind remote by {behind} commits")
                if int(ahead) > 0:
                    print(f"  ⬆️  Ahead of remote by {ahead} commits")
                if int(behind) == 0 and int(ahead) == 0:
                    print(f"  ✅ In sync with remote")
            
        except Exception as e:
            print(f"  ⚠️  Could not check Git status: {e}")
        
        print()
    
    def check_manus_coordination(self):
        """Check MACCS v3.0 coordination status"""
        print("🤝 Manus Coordination (MACCS v3.0):")
        print("=" * 60)
        
        try:
            maccs_db = self.project_root / "maccs" / "coordination.db"
            if maccs_db.exists():
                conn = sqlite3.connect(str(maccs_db))
                cursor = conn.cursor()
                
                # Get active Manus instances
                cursor.execute("""
                    SELECT manus_id, status, current_task, last_update
                    FROM heartbeats
                    ORDER BY last_update DESC
                """)
                
                instances = cursor.fetchall()
                if instances:
                    active_count = 0
                    for manus_id, status, current_task, last_update in instances:
                        # Check if heartbeat is recent (within 5 minutes)
                        try:
                            last_update_dt = datetime.fromisoformat(last_update.replace('Z', '+00:00'))
                            time_diff = datetime.now(last_update_dt.tzinfo) - last_update_dt
                            is_active = time_diff.total_seconds() < 300  # 5 minutes
                            
                            if is_active:
                                active_count += 1
                                status_icon = "✅"
                            else:
                                status_icon = "⏰"
                            
                            # Truncate task description
                            task_short = current_task[:40] + "..." if len(current_task) > 40 else current_task
                            print(f"  {status_icon} {manus_id:<12} {status:<15} {task_short}")
                        except:
                            print(f"  ⚠️  {manus_id:<12} {status:<15} (timestamp parse error)")
                    
                    print(f"\n  📊 Active: {active_count}/{len(instances)} Manus instances")
                else:
                    print("  ⚪ No Manus instances registered yet")
                
                # Get task count
                cursor.execute("SELECT COUNT(*) FROM tasks")
                task_count = cursor.fetchone()[0]
                print(f"  📋 Tasks in queue: {task_count}")
                
                conn.close()
            else:
                print("  ⚪ MACCS database not initialized yet")
        except Exception as e:
            print(f"  ⚠️  Could not check Manus coordination: {e}")
        
        print()
    
    def check_resource_usage(self):
        """Check system resource usage"""
        print("💻 System Resources:")
        print("=" * 60)
        
        try:
            # CPU usage
            result = subprocess.run(
                ["top", "-bn1"],
                capture_output=True,
                text=True
            )
            if result.stdout:
                lines = result.stdout.split("\n")
                for line in lines:
                    if "Cpu(s)" in line:
                        print(f"  🔥 {line.strip()}")
                        break
            
            # Memory usage
            result = subprocess.run(
                ["free", "-h"],
                capture_output=True,
                text=True
            )
            if result.stdout:
                lines = result.stdout.split("\n")
                if len(lines) > 1:
                    print(f"  🧠 Memory: {lines[1]}")
            
            # Disk usage
            result = subprocess.run(
                ["df", "-h", str(self.project_root)],
                capture_output=True,
                text=True
            )
            if result.stdout:
                lines = result.stdout.split("\n")
                if len(lines) > 1:
                    print(f"  💿 Disk: {lines[1]}")
            
        except Exception as e:
            print(f"  ⚠️  Could not check resource usage: {e}")
        
        print()
    
    def show_quick_actions(self):
        """Show available quick actions"""
        print("⚡ Quick Actions:")
        print("=" * 60)
        print("  • Start system:    ./GODMODE-START.sh")
        print("  • Stop all:        pkill -f 'python.*ai-gods|node.*dev'")
        print("  • View logs:       tail -f godmode-dashboard/logs/*.log")
        print("  • Emergency fix:   python3 safety-nets/emergency-recovery.py")
        print("  • Update code:     git pull origin main")
        print("  • Backend setup:   cd backend && npm install && npm run build")
        print()
    
    def run_full_status_check(self):
        """Run complete system status check"""
        print("\n" + "=" * 60)
        print("🎮 FLOWSTATE-AI GODMODE - SYSTEM STATUS")
        print("=" * 60)
        print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60 + "\n")
        
        self.get_running_processes()
        self.check_port_status()
        self.check_database_status()
        self.check_manus_coordination()
        self.check_git_status()
        self.check_resource_usage()
        self.show_quick_actions()
        
        print("=" * 60)
        print("✅ Status check complete")
        print("=" * 60 + "\n")

def main():
    status = SystemStatus()
    status.run_full_status_check()
    return 0

if __name__ == "__main__":
    sys.exit(main())
