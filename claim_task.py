#!/usr/bin/env python3.11
"""
Claim Task via MACCS v3.0
=========================
Quick script to claim a task from the MACCS v3.0 system.

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
        print("Usage: python3.11 claim_task.py <task_id>")
        sys.exit(1)
    
    task_id = sys.argv[1]
    
    print(f"[claim_task] Claiming {task_id} for manus_7...")
    
    # Initialize MACCS client
    repo_path = os.path.dirname(os.path.abspath(__file__))
    client = MACCSClientV3('manus_7', repo_path)
    
    try:
        # Claim the task
        client.claim_task(task_id)
        print(f"[claim_task] ✓ Successfully claimed {task_id}")
        
    except Exception as e:
        print(f"[claim_task] Error claiming task: {e}")
        raise
    finally:
        client.close()

if __name__ == '__main__':
    main()
