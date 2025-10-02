#!/usr/bin/env python3.11
"""
Complete Task via MACCS v3.0
=============================
Quick script to mark a task as completed in the MACCS v3.0 system.

Author: Manus 7
Date: October 2, 2025
"""

import sys
import os

# Add maccs directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'maccs'))

# Import the MACCS client
import maccs_client
MACCSClientV3 = maccs_client.MACCSClientV3

def main():
    if len(sys.argv) < 2:
        print("Usage: python3.11 complete_task.py <task_id> [result_summary]")
        sys.exit(1)
    
    task_id = sys.argv[1]
    result_summary = sys.argv[2] if len(sys.argv) > 2 else "Task completed successfully"
    
    print(f"[complete_task] Marking {task_id} as COMPLETED...")
    
    # Initialize MACCS client
    repo_path = os.path.dirname(os.path.abspath(__file__))
    client = MACCSClientV3('manus_7', repo_path)
    
    try:
        # Complete the task
        client.complete_task(task_id, result_summary)
        print(f"[complete_task] ✓ Successfully marked {task_id} as COMPLETED")
        print(f"[complete_task] Result: {result_summary}")
        
    except Exception as e:
        print(f"[complete_task] Error completing task: {e}")
        raise
    finally:
        client.close()

if __name__ == '__main__':
    main()
