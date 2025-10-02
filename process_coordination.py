
import json
from datetime import datetime, timedelta

COORDINATION_FILE_PATH = "/home/ubuntu/Flowstate-AI/.manus-coordination/coordination-status.json"

def read_coordination_status():
    with open(COORDINATION_FILE_PATH, 'r') as f:
        return json.load(f)

def write_coordination_status(data):
    with open(COORDINATION_FILE_PATH, 'w') as f:
        json.dump(data, f, indent=2)

def process_status():
    data = read_coordination_status()

    # Extract message to Manus #4
    message_to_manus_4 = data["manus_instances"]["manus_5"].get("message_to_manus_4", "No message found for Manus #4")

    # Get current task for Manus #4
    current_task_manus_4 = data["manus_instances"]["manus_4"].get("current_task", "No current task found")

    # Update heartbeat for Manus #4
    current_time = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    data["manus_instances"]["manus_4"]["last_heartbeat"] = current_time

    # Calculate next_sync to be the next 30-minute mark
    now = datetime.utcnow()
    current_minute_rounded = (now.minute // 30) * 30
    next_sync_time = now.replace(minute=current_minute_rounded, second=0, microsecond=0) + timedelta(minutes=30)
    data["manus_instances"]["manus_4"]["next_sync"] = next_sync_time.isoformat(timespec="seconds") + "Z"

    write_coordination_status(data)

    print(f"\nMessage to Manus #4: {message_to_manus_4}")
    print(f"Current task for Manus #4: {current_task_manus_4}")
    print("Heartbeat and next_sync updated in coordination-status.json")

if __name__ == "__main__":
    process_status()

