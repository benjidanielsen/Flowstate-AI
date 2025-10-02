import json
import datetime

file_path = '/home/ubuntu/Flowstate-AI/.manus-coordination/coordination-status.json'

with open(file_path, 'r') as f:
    data = json.load(f)

manus_4_status = data['manus_instances']['manus_4']

# Extract messages from other Manus instances to Manus #4
messages_to_manus_4 = {}
for manus_id, instance_data in data['manus_instances'].items():
    if manus_id != 'manus_4':
        for key, value in instance_data.items():
            if key.startswith('message_to_manus_4'):
                messages_to_manus_4[manus_id] = value

# Update heartbeat timestamp for Manus #4
current_time = datetime.datetime.utcnow().isoformat(timespec='seconds') + 'Z'
manus_4_status['last_heartbeat'] = current_time

# Check for any assigned tasks (this is a placeholder, actual task assignment logic would be more complex)
assigned_tasks = manus_4_status.get('assigned_tasks', [])

# Process any pending work or messages (placeholder)
pending_work_status = "No pending work identified based on current messages."
if messages_to_manus_4:
    pending_work_status = "Messages received from other Manus instances. Further processing required."

# Update my status with current progress (placeholder)
manus_4_status['current_task'] = "Reading coordination status, updating heartbeat, and checking for tasks."
manus_4_status['progress'] = "50%"

# Write updated data back to the file
with open(file_path, 'w') as f:
    json.dump(data, f, indent=2)

print(f"Manus #4 Heartbeat updated to: {current_time}")
print(f"Messages to Manus #4: {messages_to_manus_4}")
print(f"Assigned Tasks: {assigned_tasks}")
print(f"Pending Work Status: {pending_work_status}")
