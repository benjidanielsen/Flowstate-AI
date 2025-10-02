import sys
import os
import time
import random # Added import for random
from datetime import datetime

sys.path.append(os.path.abspath("/home/ubuntu/Flowstate-AI"))
from MANUS_SYNC_ENGINE import ManusInterface, ManusRole, TaskPriority, TaskStatus

MANUS_ID = "manus_4"

# Define Manus #4's capabilities (example, adjust as needed)
manus_4_capabilities = [
    "end_to_end_testing", "integration_testing", "system_verification",
    "report_generation", "feedback_analysis", "documentation"
]

def manus_4_main_loop(manus_interface):
    print(f'[{manus_interface.manus_id}] Entering main loop. Integrated with MANUS_SYNC_ENGINE.')
    while True:
        try:
            print(f'[{manus_interface.manus_id}] Sending heartbeat...')
            manus_interface.heartbeat()
            print(f'[{manus_interface.manus_id}] Heartbeat sent.')

            # Check for messages
            print(f'[{manus_interface.manus_id}] Checking for unread messages...')
            unread_messages = manus_interface.get_messages()
            if unread_messages:
                print(f'[{manus_interface.manus_id}] Found {len(unread_messages)} unread messages.')
            for msg in unread_messages:
                print(f'[{manus_interface.manus_id}] Received message: {msg["message_type"]} from {msg["from_manus"]}. Content: {msg["content"]}')
                # Process messages, e.g., respond to integration requests
                if msg["message_type"] == "SYNC_ENGINE_INTEGRATION_REQUEST":
                    print(f'[{manus_interface.manus_id}] Acknowledging integration request from {msg["from_manus"]}.')
                    manus_interface.send_message(
                        to_manus=msg["from_manus"],
                        message_type="INTEGRATION_ACKNOWLEDGED",
                        content={
                            "from_manus": MANUS_ID,
                            "message": "Manus #4 has successfully integrated with MANUS_SYNC_ENGINE. Ready for coordination."
                        }
                    )

            # Check for assigned tasks
            print(f'[{manus_interface.manus_id}] Checking for assigned tasks...')
            my_tasks = manus_interface.get_my_tasks()
            if my_tasks:
                print(f'[{manus_interface.manus_id}] Found {len(my_tasks)} assigned tasks. Working on the first one.')
                task_to_work = my_tasks[0]
                if task_to_work.status == TaskStatus.PENDING:
                    print(f'[{manus_interface.manus_id}] Attempting to start task: {task_to_work.title}')
                    if manus_interface.start_task(task_to_work.id):
                        print(f'[{manus_interface.manus_id}] Started task: {task_to_work.title}')
                        # Simulate work
                        time.sleep(random.uniform(10, 20))
                        manus_interface.complete_task(task_to_work.id)
                        print(f'[{manus_interface.manus_id}] Completed task: {task_to_work.title}')
                    else:
                        print(f'[{manus_interface.manus_id}] Failed to start task {task_to_work.id}.')
                elif task_to_work.status == TaskStatus.IN_PROGRESS:
                    # Continue work if already in progress
                    print(f'[{manus_interface.manus_id}] Continuing work on task: {task_to_work.title}')
                    time.sleep(random.uniform(5, 10))
                    manus_interface.complete_task(task_to_work.id)
                    print(f'[{manus_interface.manus_id}] Completed task: {task_to_work.title}')
            else:
                print(f'[{manus_interface.manus_id}] Idle. No assigned tasks.')

            time.sleep(5) # Check every 5 seconds

        except Exception as e:
            print(f'[{manus_interface.manus_id}] An unexpected error occurred in main loop: {e}')
            time.sleep(5)

if __name__ == "__main__":
    print(f'[{MANUS_ID}] Starting Manus #4 integration script...')
    try:
        print(f'[{MANUS_ID}] Initializing ManusInterface...')
        # Explicitly define the project root for ManusSyncEngine
        project_root = "/home/ubuntu/Flowstate-AI"
        manus_interface = ManusInterface(
            manus_id=MANUS_ID,
            role=ManusRole.AI_SPECIALIST, # Assigning a role, adjust as needed
            capabilities=manus_4_capabilities,
            project_root=project_root # Pass the explicit project root
        )
        print(f'[{MANUS_ID}] ManusInterface initialized successfully. Registered with MANUS_SYNC_ENGINE.')

        # Send a message to Manus #5 (me) to confirm integration
        print(f'[{MANUS_ID}] Sending integration confirmation to Manus #5...')
        manus_interface.send_message(
            to_manus="manus_5",
            message_type="INTEGRATION_CONFIRMATION",
            content={
                "from_manus": MANUS_ID,
                "message": "Manus #4 has successfully integrated with MANUS_SYNC_ENGINE and is ready for coordination."
            }
        )
        print(f'[{MANUS_ID}] Sent integration confirmation to Manus #5.')

        manus_4_main_loop(manus_interface)

    except KeyboardInterrupt:
        print(f'[{MANUS_ID}] Integration script interrupted.')
    except Exception as e:
        print(f'[{MANUS_ID}] Error during ManusInterface initialization or main loop: {e}')
        sys.exit(1)

