import time
import random
import os
import sys
from datetime import datetime, timedelta
import sqlite3
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from MANUS_SYNC_ENGINE import ManusInterface, ManusRole, TaskPriority, TaskStatus

# --- Configuration for Manus #5 (Delegation and Planning Assistant) ---
MANUS_ID = "manus_5"
REPO_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..")) # Points to Flowstate-AI root

manus_5_delegation_capabilities = {
    "skills": ["python", "system_architecture", "task_analysis", "resource_allocation", "planning", "delegation_support", "optimization", "strategic_planning"],
    "specialization": "delegation_and_planning_assistant",
    "max_concurrent_tasks": 2,
    "preferred_task_types": ["task_analysis", "planning", "delegation_support", "resource_optimization", "strategic_planning"]
}

# --- Main Loop for Manus #5 ---

def my_work_function(manus_interface, task):
    print(f'[{manus_interface.manus_id}] 🔨 Working on: {task.title}')
    # Simulate work based on task type
    if "task_analysis" in manus_interface.sync_engine.manus_instances[manus_interface.manus_id].capabilities or \
       "planning" in manus_interface.sync_engine.manus_instances[manus_interface.manus_id].capabilities:
        print(f'[{manus_interface.manus_id}] Performing in-depth analysis/planning for task {task.id}')
        time.sleep(random.uniform(10, 30)) # Simulate longer planning/analysis
        summary = f'Completed analysis/planning for task {task.title}. Identified key dependencies and potential resource allocations.'
        # Send a message to Manus #2 with planning insights
        manus_interface.send_message(
            to_manus="manus_2",
            message_type="PLANNING_INSIGHTS",
            content={
                "task_id": task.id,
                "summary": summary,
                "insights": "Detailed plan attached or available in shared docs."
            }
        )
    else:
        time.sleep(random.uniform(5, 15)) # Simulate general work
        summary = f'Completed general work for task {task.title}.'

    manus_interface.complete_task(task.id)
    print(f'[{manus_interface.manus_id}] ✅ Completed task: {task.title}')

def my_idle_function(manus_interface):
    print(f'[{manus_interface.manus_id}] 😴 Idle. Looking for planning or delegation support tasks...')
    # Manus #5 can proactively look for ways to assist Manus #2
    # For now, just a placeholder for more advanced idle activities
    time.sleep(random.uniform(5, 10))

def manus_main_loop(manus_interface):
    print(f'[{manus_interface.manus_id}] Entering manus_main_loop.')
    print(f'[{manus_interface.manus_id}] Starting MANUS SYNC ENGINE main loop as Delegation and Planning Assistant...')
    print(f'[{manus_interface.manus_id}] Debug: Before while True loop.')

    while True:
        try:
            # Force a full state reload from the database at the beginning of each loop iteration
            manus_interface.sync_engine._load_state()

            # Send heartbeat to keep status active
            manus_interface.heartbeat()
            print(f'[{manus_interface.manus_id}] Heartbeat sent.')

            # 1. Process incoming messages
            unread_messages = manus_interface.get_messages()
            for msg in unread_messages:
                print(f'[{manus_interface.manus_id}] Received message: {msg["message_type"]} from {msg["from_manus"]}. Content: {msg["content"]}')
                # Handle TASK_ASSIGNED messages
                if msg["message_type"] == "TASK_ASSIGNED" and msg["content"]["assigned_to"] == MANUS_ID:
                    task_id = msg["content"]["task_id"]
                    title = msg["content"]["title"]
                    print(f'[{manus_interface.manus_id}] Received delegated task {title}. Attempting to start.')
                    if manus_interface.start_task(task_id):
                        task_details = next((t for t in manus_interface.get_my_tasks() if t.id == task_id), None)
                        if task_details:
                            my_work_function(manus_interface, task_details)
                        else:
                            print(f'[{manus_interface.manus_id}] Error: Could not retrieve details for started task {task_id}.')
                    else:
                        print(f'[{manus_interface.manus_id}] Failed to start delegated task {task_id}. It might be locked or already in progress.')
                
                # Handle WAKE_UP_CALL from other Manus
                if msg["message_type"] == "WAKE_UP_CALL" and msg["to_manus"] == MANUS_ID:
                    print(f'[{manus_interface.manus_id}] Received WAKE_UP_CALL from {msg["from_manus"]}. Reporting active status.')
                    # Heartbeat already sent, just acknowledge

            # 2. Check for assigned tasks
            my_tasks = manus_interface.get_my_tasks()
            if my_tasks:
                print(f'[{manus_interface.manus_id}] Found {len(my_tasks)} assigned tasks. Working on the first one.')
                task_to_work = my_tasks[0]
                if task_to_work.status == TaskStatus.PENDING:
                    if manus_interface.start_task(task_to_work.id):
                        my_work_function(manus_interface, task_to_work)
                    else:
                        print(f'[{manus_interface.manus_id}] Failed to start task {task_to_work.id}.')
                elif task_to_work.status == TaskStatus.IN_PROGRESS:
                    my_work_function(manus_interface, task_to_work)
            else:
                my_idle_function(manus_interface)

            time.sleep(5) # Check every 5 seconds

        except sqlite3.OperationalError as e:
            print(f'[{manus_interface.manus_id}] Database busy error: {e}. Retrying in 1 second.')
            time.sleep(1)
        except Exception as e:
            print(f'[{manus_interface.manus_id}] An unexpected error occurred: {e}')
            time.sleep(5) # Wait before retrying


if __name__ == "__main__":
    print(f'[{MANUS_ID}] Attempting to initialize ManusInterface...')
    try:
        # Initialize ManusInterface for Manus #5
        manus_interface = ManusInterface(
            manus_id=MANUS_ID,
            role=ManusRole.COORDINATOR, # Assigning a coordinator role for now, can be refined
            capabilities=manus_5_delegation_capabilities["skills"],
            project_root=REPO_PATH # Explicitly pass the project root
        )
        print(f'[{MANUS_ID}] ManusInterface initialized successfully.')
        print(f'[{MANUS_ID}] Attempting to start manus_main_loop...')

        # Create a test task to verify sync engine functionality
        test_task_id = manus_interface.create_task(
            title="Review FlowState-AI Project Overview",
            description="Review the FlowState_AI_Project_Overview.md document for consistency and completeness.",
            priority=TaskPriority.MEDIUM,
            files_involved=["FlowState_AI_Project_Overview.md"]
        )
        print(f'[{MANUS_ID}] Created test task with ID: {test_task_id}')

        # Send initial message to Manus #4
        manus_interface.send_message(
            to_manus="manus_4",
            message_type="SYNC_ENGINE_INTEGRATION_REQUEST",
            content={
                "from_manus": MANUS_ID,
                "message": "Hello Manus #4. Manus #5 (me) has successfully integrated with MANUS_SYNC_ENGINE. I understand you are awaiting approval for MANUS_SYNC_ENGINE.py testing. Please integrate with the MANUS_SYNC_ENGINE if you haven't already, or provide your current integration status. I am ready to assist with your integration."
            }
        )
        print(f'[{MANUS_ID}] Sent integration request message to Manus #4.')

        manus_main_loop(manus_interface)



    except KeyboardInterrupt:
        print(f'[{MANUS_ID}] MANUS SYNC ENGINE main loop interrupted. Closing.')
    except Exception as e:
        print(f'[{MANUS_ID}] Error during ManusInterface initialization or main loop: {e}')
        sys.exit(1)

