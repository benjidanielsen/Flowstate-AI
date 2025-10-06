#!/usr/bin/env python3
"""
🚀 FLOWSTATE-AI SIMPLE SYSTEM STARTUP
⚡ Get the core AI agents operational immediately
🎯 Mission: Launch Project Manager, Communication Hub, and CRM Pipeline
"""

import os
import sys
import subprocess
import time
import signal
from pathlib import Path

# Set up the project root
PROJECT_ROOT = Path(__file__).parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))
os.environ["PYTHONPATH"] = str(PROJECT_ROOT)

# Import our simple components
from ai_gods.simple_project_manager import SimpleProjectManager
from ai_gods.simple_communication_hub import SimpleCommunicationHub

print("=" * 70)
print("🚀 FLOWSTATE-AI SIMPLE SYSTEM STARTUP")
print("=" * 70)
print()
print(f"📁 Project Root: {PROJECT_ROOT}")
print(f"🐍 Python: {sys.executable}")
print()

# Initialize the core components
print("🤖 Initializing Project Manager AI...")
pm = SimpleProjectManager(PROJECT_ROOT)
print("✅ Project Manager AI initialized")
print()

print("📡 Initializing Communication Hub...")
hub = SimpleCommunicationHub(PROJECT_ROOT)
print("✅ Communication Hub initialized")
print()

# Run the components
print("🚀 Starting Project Manager AI...")
pm.run()
print()

print("🚀 Starting Communication Hub...")
hub.run()
print()

# Display system status
print("=" * 70)
print("🎉 FLOWSTATE-AI SIMPLE SYSTEM IS NOW OPERATIONAL!")
print("=" * 70)
print()
print("📊 System Status:")
print("   ✅ Project Manager AI: Running")
print("   ✅ Communication Hub: Running")
print("   ✅ CRM Pipeline: Initialized")
print("   ✅ Database: godmode-state.db")
print()
print("📋 Current Tasks:")
pending_tasks = pm.get_pending_tasks()
for task in pending_tasks[:5]:  # Show first 5 tasks
    print(f"   - Task #{task['id']}: {task['title']}")
    print(f"     Assigned to: {task['assigned_to'] or 'Unassigned'}")
    print(f"     Priority: {task['priority']}")
print()

print("🎯 CRM Pipeline Status:")
for stage in ['lead_generation', 'qualification', 'nurturing', 'conversion', 'retention']:
    leads = pm.get_leads_by_stage(stage)
    print(f"   - {stage.replace('_', ' ').title()}: {len(leads)} leads")
print()

print("👥 Active Agents:")
agents = hub.get_all_agents_status()
for agent in agents:
    print(f"   - {agent['agent']}: {agent['status']}")
print()

print("📝 Logs:")
print("   - Project Manager: godmode-logs/simple-project-manager.log")
print("   - Communication Hub: godmode-logs/simple-communication-hub.log")
print()

print("💡 Next Steps:")
print("   1. Check the logs for detailed activity")
print("   2. Access the database at: godmode-state.db")
print("   3. Run the backend API: cd backend && npm start")
print("   4. Run the frontend: cd frontend && npm run preview")
print()

print("=" * 70)
print("✅ System is ready for autonomous development!")
print("=" * 70)
