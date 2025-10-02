#!/usr/bin/env python3.11
"""
Reset Tasks in MACCS v3.0
==========================
Reset tasks that were incorrectly marked as completed back to AVAILABLE status.

Author: Manus 7
Date: October 2, 2025
"""

import sqlite3
import os

def main():
    repo_path = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(repo_path, 'maccs', 'coordination.db')
    
    # Tasks to reset (all except TASK-110 which was actually completed)
    tasks_to_reset = [
        'TASK-101', 'TASK-102', 'TASK-103', 'TASK-104', 'TASK-105',
        'TASK-106', 'TASK-107', 'TASK-108', 'TASK-109'
    ]
    
    print("[reset_tasks] Resetting incorrectly completed tasks...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    for task_id in tasks_to_reset:
        cursor.execute('''
            UPDATE tasks 
            SET status = 'AVAILABLE', 
                claimed_by = NULL, 
                claimed_at = NULL,
                completed_at = NULL,
                approved_by = NULL,
                approved_at = NULL
            WHERE task_id = ?
        ''', (task_id,))
        print(f"[reset_tasks] ✓ Reset {task_id} to AVAILABLE")
    
    conn.commit()
    conn.close()
    
    print(f"[reset_tasks] Successfully reset {len(tasks_to_reset)} tasks")

if __name__ == '__main__':
    main()
