#!/usr/bin/env python3
"""
📋 LOAD MASTER PLAN INTO DATABASE
⚡ Imports all tasks from MASTER_7DAY_PLAN.json into the database
"""

import json
import sqlite3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
DB_PATH = PROJECT_ROOT / "godmode-state.db"
PLAN_PATH = PROJECT_ROOT / "MASTER_7DAY_PLAN.json"

def load_plan():
    """Load the master plan and insert all tasks into database"""
    
    print("📋 Loading Master 7-Day Plan...")
    
    # Load the plan
    with open(PLAN_PATH, 'r') as f:
        plan = json.load(f)
    
    print(f"✅ Plan loaded: {plan['total_tasks']} tasks over {plan['duration_days']} days")
    
    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Clear existing pending tasks (optional - comment out if you want to keep them)
    # cursor.execute("DELETE FROM tasks WHERE status = 'pending'")
    # print("🗑️  Cleared existing pending tasks")
    
    total_inserted = 0
    
    # Insert tasks from each day
    for day_plan in plan['days']:
        day_num = day_plan['day']
        focus = day_plan['focus']
        
        print(f"\n📅 Day {day_num}: {focus}")
        print(f"   Tasks: {len(day_plan['tasks'])}")
        
        for task in day_plan['tasks']:
            try:
                # Check if task already exists
                cursor.execute("SELECT id FROM tasks WHERE id = ?", (task['id'],))
                if cursor.fetchone():
                    print(f"   ⏭️  Task #{task['id']} already exists, skipping")
                    continue
                
                # Insert task
                cursor.execute('''
                    INSERT INTO tasks (id, title, description, priority, assigned_to, status)
                    VALUES (?, ?, ?, ?, ?, 'pending')
                ''', (
                    task['id'],
                    task['title'],
                    task['description'],
                    task['priority'],
                    task['assigned_to']
                ))
                
                total_inserted += 1
                print(f"   ✅ Task #{task['id']}: {task['title']}")
                
            except Exception as e:
                print(f"   ❌ Failed to insert task #{task['id']}: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"\n{'='*60}")
    print(f"🎉 MASTER PLAN LOADED SUCCESSFULLY!")
    print(f"{'='*60}")
    print(f"✅ Total tasks inserted: {total_inserted}")
    print(f"📊 Database: {DB_PATH}")
    print(f"\n💡 Next steps:")
    print(f"   1. Start the autonomous AI developer")
    print(f"   2. Watch it work through all tasks")
    print(f"   3. Monitor progress in the dashboard")
    print(f"\n🚀 Ready to start autonomous development!")

if __name__ == "__main__":
    load_plan()
