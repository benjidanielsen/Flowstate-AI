import os
import logging
from flask import Flask, render_template, jsonify, request, send_from_directory
from datetime import datetime
import random
import json
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash
from flask import make_response

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = Flask(__name__)

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "benjidanielsen")
ADMIN_PASSWORD_HASH = generate_password_hash(os.getenv("ADMIN_PASSWORD", "Sagemaster123"))

def check_auth(username, password):
    return username == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD_HASH, password)

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return make_response('Could not verify your access level for that URL.', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})
        return f(*args, **kwargs)
    return decorated

# Base URL for profile pictures (replace with actual hosting if needed)
PROFILE_PICTURE_BASE_URL = "/static/profile_pictures/" # Base URL for static profile pictures

# In-memory storage for agent status and tasks (for demonstration)
agent_status = {
    "project_manager": {"agent_human_name": "Emily", "gender": "female", "profile_picture": f"{PROFILE_PICTURE_BASE_URL}default.png", "status": "Idle", "current_task": "None", "progress": 0, "last_update": None, "tasks_completed_24h": 0, "longest_task_1": {"name": "None", "duration": 0}, "longest_task_2": {"name": "None", "duration": 0}},
    "backend_developer": {"agent_human_name": "Henry", "gender": "male", "profile_picture": f"{PROFILE_PICTURE_BASE_URL}default.png", "status": "Idle", "current_task": "None", "progress": 0, "last_update": None, "tasks_completed_24h": 0, "longest_task_1": {"name": "None", "duration": 0}, "longest_task_2": {"name": "None", "duration": 0}},
    "frontend_developer": {"agent_human_name": "Sophia", "gender": "female", "profile_picture": f"{PROFILE_PICTURE_BASE_URL}default.png", "status": "Idle", "current_task": "None", "progress": 0, "last_update": None, "tasks_completed_24h": 0, "longest_task_1": {"name": "None", "duration": 0}, "longest_task_2": {"name": "None", "duration": 0}},
    "database_ai": {"agent_human_name": "Robert", "gender": "male", "profile_picture": f"{PROFILE_PICTURE_BASE_URL}default.png", "status": "Idle", "current_task": "None", "progress": 0, "last_update": None, "tasks_completed_24h": 0, "longest_task_1": {"name": "None", "duration": 0}, "longest_task_2": {"name": "None", "duration": 0}},
    "tester_ai": {"agent_human_name": "Olivia", "gender": "female", "profile_picture": f"{PROFILE_PICTURE_BASE_URL}default.png", "status": "Idle", "current_task": "None", "progress": 0, "last_update": None, "tasks_completed_24h": 0, "longest_task_1": {"name": "None", "duration": 0}, "longest_task_2": {"name": "None", "duration": 0}},
    "fixer_ai": {"agent_human_name": "Mason", "gender": "male", "profile_picture": f"{PROFILE_PICTURE_BASE_URL}default.png", "status": "Idle", "current_task": "None", "progress": 0, "last_update": None, "tasks_completed_24h": 0, "longest_task_1": {"name": "None", "duration": 0}, "longest_task_2": {"name": "None", "duration": 0}},
    "devops_ai": {"agent_human_name": "Joshua", "gender": "male", "profile_picture": f"{PROFILE_PICTURE_BASE_URL}default.png", "status": "Idle", "current_task": "None", "progress": 0, "last_update": None, "tasks_completed_24h": 0, "longest_task_1": {"name": "None", "duration": 0}, "longest_task_2": {"name": "None", "duration": 0}},
    "documentation_ai": {"agent_human_name": "Grace", "gender": "female", "profile_picture": f"{PROFILE_PICTURE_BASE_URL}default.png", "status": "Idle", "current_task": "None", "progress": 0, "last_update": None, "tasks_completed_24h": 0, "longest_task_1": {"name": "None", "duration": 0}, "longest_task_2": {"name": "None", "duration": 0}},
    "support_ai": {"agent_human_name": "Chloe", "gender": "female", "profile_picture": f"{PROFILE_PICTURE_BASE_URL}default.png", "status": "Idle", "current_task": "None", "progress": 0, "last_update": None, "tasks_completed_24h": 0, "longest_task_1": {"name": "None", "duration": 0}, "longest_task_2": {"name": "None", "duration": 0}},
    "innovation_ai": {"agent_human_name": "Noah", "gender": "male", "profile_picture": f"{PROFILE_PICTURE_BASE_URL}default.png", "status": "Idle", "current_task": "None", "progress": 0, "last_update": None, "tasks_completed_24h": 0, "longest_task_1": {"name": "None", "duration": 0}, "longest_task_2": {"name": "None", "duration": 0}},
    "ai_communication_hub": {"agent_human_name": "Ava", "gender": "female", "profile_picture": f"{PROFILE_PICTURE_BASE_URL}default.png", "status": "Idle", "current_task": "None", "progress": 0, "last_update": None, "tasks_completed_24h": 0, "longest_task_1": {"name": "None", "duration": 0}, "longest_task_2": {"name": "None", "duration": 0}},
    "collective_memory_system": {"agent_human_name": "Liam", "gender": "male", "profile_picture": f"{PROFILE_PICTURE_BASE_URL}default.png", "status": "Idle", "current_task": "None", "progress": 0, "last_update": None, "tasks_completed_24h": 0, "longest_task_1": {"name": "None", "duration": 0}, "longest_task_2": {"name": "None", "duration": 0}}
}

# In-memory storage for chat messages (for demonstration)
chat_messages = []

# In-memory storage for agent-to-agent messages (for demonstration)
agent_messages = []

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/agent_status", methods=["GET"])
def get_agent_status():
    return jsonify(agent_status)

@app.route("/api/update_agent_status", methods=["POST"])
def update_agent_status():
    data = request.get_json()
    agent_name = data.get("agent_name")
    agent_human_name = data.get("agent_human_name")
    gender = data.get("gender")
    status = data.get("status")
    current_task = data.get("current_task")
    progress = data.get("progress")
    task_duration = data.get("task_duration") # Duration of the completed task in seconds

    if agent_name and agent_name in agent_status:
        agent_status[agent_name]["status"] = status
        agent_status[agent_name]["current_task"] = current_task
        agent_status[agent_name]["progress"] = progress
        agent_status[agent_name]["last_update"] = datetime.now().isoformat()
        if agent_human_name: # Update human name if provided
            agent_status[agent_name]["agent_human_name"] = agent_human_name
        if gender: # Update gender
            agent_status[agent_name]["gender"] = gender
        profile_picture = data.get("profile_picture")
        if profile_picture:
            agent_status[agent_name]["profile_picture"] = profile_picture

        if status == "Completed" and task_duration is not None:
            agent_status[agent_name]["tasks_completed_24h"] += 1
            # Update longest tasks
            if task_duration > agent_status[agent_name]["longest_task_1"]["duration"]:
                agent_status[agent_name]["longest_task_2"] = agent_status[agent_name]["longest_task_1"]
                agent_status[agent_name]["longest_task_1"] = {"name": current_task, "duration": task_duration}
            elif task_duration > agent_status[agent_name]["longest_task_2"]["duration"]:
                agent_status[agent_name]["longest_task_2"] = {"name": current_task, "duration": task_duration}

        logging.info(f"Updated {agent_name}: Status={status}, Task={current_task}, Progress={progress}")
        return jsonify({"message": "Status updated successfully"}), 200
    return jsonify({"error": "Invalid agent name or data"}), 400

@app.route("/chat")
def chat_interface():
    return render_template("chat.html")

@app.route("/api/chat_messages", methods=["GET"])
def get_chat_messages():
    return jsonify(chat_messages)

@app.route("/api/send_chat_message", methods=["POST"])
def send_chat_message():
    data = request.get_json()
    sender = data.get("sender")
    message = data.get("message")
    agent_key = data.get("agent_key") # Optional: for sending message to a specific agent

    if sender and message:
        timestamp = datetime.now().isoformat()
        chat_messages.append({"sender": sender, "message": message, "timestamp": timestamp, "agent_key": agent_key})
        logging.info(f"Chat message from {sender}: {message}")
        return jsonify({"message": "Message sent successfully"}), 200
    return jsonify({"error": "Sender and message are required"}), 400

@app.route("/admin")
@requires_auth
def admin_dashboard():
    return render_template("admin.html")

@app.route("/api/logs/<log_file_name>")
def get_logs(log_file_name):
    log_path = os.path.join(os.path.dirname(app.root_path), "godmode-logs", log_file_name)
    if os.path.exists(log_path):
        with open(log_path, "r") as f:
            logs = f.readlines()
        return jsonify(logs)
    return jsonify({"error": "Log file not found"}), 404

@app.route("/api/agent_messages", methods=["GET"])
def get_agent_messages():
    """Get all agent-to-agent messages for the admin dashboard."""
    return jsonify(agent_messages)

@app.route("/api/agent_message", methods=["POST"])
def receive_agent_message():
    """Receive and store agent-to-agent messages."""
    data = request.get_json()
    sender = data.get("sender")
    receiver = data.get("receiver")
    message_type = data.get("type")
    content = data.get("content")
    timestamp = data.get("timestamp", datetime.now().isoformat())

    if sender and receiver and message_type and content:
        agent_messages.append({
            "sender": sender,
            "receiver": receiver,
            "type": message_type,
            "content": content,
            "timestamp": timestamp
        })
        logging.info(f"Agent message from {sender} to {receiver} (Type: {message_type}): {content}")
        return jsonify({"message": "Agent message received successfully"}), 200
    return jsonify({"error": "Missing required message parameters"}), 400


