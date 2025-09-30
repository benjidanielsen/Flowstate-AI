import os
import logging
from flask import Flask, render_template, jsonify, request
from datetime import datetime
import random

# Configure logging
logging.basicConfig(level=logging.INFO, format=\'%(asctime)s - %(levelname)s - %(message)s\')

app = Flask(__name__)

# Base URL for profile pictures (replace with actual hosting if needed)
PROFILE_PICTURE_BASE_URL = "https://randomuser.me/api/portraits/"

# In-memory storage for agent status and tasks (for demonstration)
agent_status = {
    "project_manager": {"agent_human_name": "Emily", "gender": "female", "profile_picture": f"{PROFILE_PICTURE_BASE_URL}women/{random.randint(1, 99)}.jpg", "status": "Idle", "current_task": "None", "progress": 0, "last_update": None, "tasks_completed_24h": 0, "longest_task_1": {"name": "None", "duration": 0}, "longest_task_2": {"name": "None", "duration": 0}},
    "backend_developer": {"agent_human_name": "Henry", "gender": "male", "profile_picture": f"{PROFILE_PICTURE_BASE_URL}men/{random.randint(1, 99)}.jpg", "status": "Idle", "current_task": "None", "progress": 0, "last_update": None, "tasks_completed_24h": 0, "longest_task_1": {"name": "None", "duration": 0}, "longest_task_2": {"name": "None", "duration": 0}},
    "frontend_developer": {"agent_human_name": "Sophia", "gender": "female", "profile_picture": f"{PROFILE_PICTURE_BASE_URL}women/{random.randint(1, 99)}.jpg", "status": "Idle", "current_task": "None", "progress": 0, "last_update": None, "tasks_completed_24h": 0, "longest_task_1": {"name": "None", "duration": 0}, "longest_task_2": {"name": "None", "duration": 0}},
    "database_ai": {"agent_human_name": "Robert", "gender": "male", "profile_picture": f"{PROFILE_PICTURE_BASE_URL}men/{random.randint(1, 99)}.jpg", "status": "Idle", "current_task": "None", "progress": 0, "last_update": None, "tasks_completed_24h": 0, "longest_task_1": {"name": "None", "duration": 0}, "longest_task_2": {"name": "None", "duration": 0}},
    "tester_ai": {"agent_human_name": "Olivia", "gender": "female", "profile_picture": f"{PROFILE_PICTURE_BASE_URL}women/{random.randint(1, 99)}.jpg", "status": "Idle", "current_task": "None", "progress": 0, "last_update": None, "tasks_completed_24h": 0, "longest_task_1": {"name": "None", "duration": 0}, "longest_task_2": {"name": "None", "duration": 0}},
    "fixer_ai": {"agent_human_name": "Mason", "gender": "male", "profile_picture": f"{PROFILE_PICTURE_BASE_URL}men/{random.randint(1, 99)}.jpg", "status": "Idle", "current_task": "None", "progress": 0, "last_update": None, "tasks_completed_24h": 0, "longest_task_1": {"name": "None", "duration": 0}, "longest_task_2": {"name": "None", "duration": 0}},
    "devops_ai": {"agent_human_name": "Joshua", "gender": "male", "profile_picture": f"{PROFILE_PICTURE_BASE_URL}men/{random.randint(1, 99)}.jpg", "status": "Idle", "current_task": "None", "progress": 0, "last_update": None, "tasks_completed_24h": 0, "longest_task_1": {"name": "None", "duration": 0}, "longest_task_2": {"name": "None", "duration": 0}},
    "documentation_ai": {"agent_human_name": "Grace", "gender": "female", "profile_picture": f"{PROFILE_PICTURE_BASE_URL}women/{random.randint(1, 99)}.jpg", "status": "Idle", "current_task": "None", "progress": 0, "last_update": None, "tasks_completed_24h": 0, "longest_task_1": {"name": "None", "duration": 0}, "longest_task_2": {"name": "None", "duration": 0}},
    "support_ai": {"agent_human_name": "Chloe", "gender": "female", "profile_picture": f"{PROFILE_PICTURE_BASE_URL}women/{random.randint(1, 99)}.jpg", "status": "Idle", "current_task": "None", "progress": 0, "last_update": None, "tasks_completed_24h": 0, "longest_task_1": {"name": "None", "duration": 0}, "longest_task_2": {"name": "None", "duration": 0}},
    "innovation_ai": {"agent_human_name": "Noah", "gender": "male", "profile_picture": f"{PROFILE_PICTURE_BASE_URL}men/{random.randint(1, 99)}.jpg", "status": "Idle", "current_task": "None", "progress": 0, "last_update": None, "tasks_completed_24h": 0, "longest_task_1": {"name": "None", "duration": 0}, "longest_task_2": {"name": "None", "duration": 0}},
    "ai_communication_hub": {"agent_human_name": "Ava", "gender": "female", "profile_picture": f"{PROFILE_PICTURE_BASE_URL}women/{random.randint(1, 99)}.jpg", "status": "Idle", "current_task": "None", "progress": 0, "last_update": None, "tasks_completed_24h": 0, "longest_task_1": {"name": "None", "duration": 0}, "longest_task_2": {"name": "None", "duration": 0}},
    "collective_memory_system": {"agent_human_name": "Liam", "gender": "male", "profile_picture": f"{PROFILE_PICTURE_BASE_URL}men/{random.randint(1, 99)}.jpg", "status": "Idle", "current_task": "None", "progress": 0, "last_update": None, "tasks_completed_24h": 0, "longest_task_1": {"name": "None", "duration": 0}, "longest_task_2": {"name": "None", "duration": 0}}
}

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
        if gender: # Update gender and regenerate profile picture if provided
            agent_status[agent_name]["gender"] = gender
            if gender == "male":
                agent_status[agent_name]["profile_picture"] = f"{PROFILE_PICTURE_BASE_URL}men/{random.randint(1, 99)}.jpg"
            elif gender == "female":
                agent_status[agent_name]["profile_picture"] = f"{PROFILE_PICTURE_BASE_URL}women/{random.randint(1, 99)}.jpg"

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
    return render_template("chat.html") # Placeholder for a chat interface

if __name__ == "__main__":
    # Create a templates directory if it doesn't exist
    os.makedirs("templates", exist_ok=True)

    # Create a simple index.html for the dashboard
    with open("templates/index.html", "w") as f:
        f.write("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GODMODE AI Dashboard</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #1e1e1e; color: #d4d4d4; margin: 0; padding: 20px; }
        .container { max-width: 1200px; margin: auto; background-color: #252526; padding: 20px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2); }
        h1 { color: #007acc; text-align: center; margin-bottom: 30px; }
        .agent-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .agent-card { background-color: #333333; padding: 15px; border-radius: 6px; border-left: 5px solid #007acc; transition: transform 0.2s ease-in-out; display: flex; align-items: center; }
        .agent-card:hover { transform: translateY(-5px); }
        .agent-card img { width: 60px; height: 60px; border-radius: 50%; margin-right: 15px; border: 2px solid #007acc; object-fit: cover; }
        .agent-info { flex-grow: 1; }
        .agent-card h2 { color: #60a5fa; margin-top: 0; margin-bottom: 5px; font-size: 1.4em; }
        .agent-card p { margin: 5px 0; line-height: 1.5; }
        .agent-card .status { font-weight: bold; color: #4CAF50; }
        .agent-card .status.Idle { color: #9e9e9e; }
        .agent-card .status.Working { color: #FFC107; }
        .agent-card .status.Error { color: #F44336; }
        .progress-bar-container { background-color: #555; border-radius: 5px; height: 10px; margin-top: 10px; overflow: hidden; }
        .progress-bar { background-color: #007acc; height: 100%; width: 0%; border-radius: 5px; transition: width 0.5s ease-in-out; }
        .task-info { font-size: 0.9em; color: #bbb; }
        .header-links { text-align: center; margin-bottom: 20px; }
        .header-links a { color: #007acc; text-decoration: none; margin: 0 15px; font-size: 1.1em; }
        .header-links a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="container">
        <h1>GODMODE AI Dashboard</h1>
        <div class="header-links">
            <a href="/">Dashboard</a>
            <a href="/chat">AI Chat</a>
        </div>
        <div class="agent-grid" id="agent-grid">
            <!-- Agent cards will be loaded here by JavaScript -->
        </div>
    </div>

    <script>
        function fetchAgentStatus() {
            fetch('/api/agent_status')
                .then(response => response.json())
                .then(data => {
                    const agentGrid = document.getElementById('agent-grid');
                    agentGrid.innerHTML = ''; // Clear existing cards
                    for (const agentKey in data) {
                        const agent = data[agentKey];
                        const agentCard = document.createElement('div');
                        agentCard.className = 'agent-card';
                        agentCard.innerHTML = `
                            <img src="${agent.profile_picture}" alt="${agent.agent_human_name}">
                            <div class="agent-info">
                                <h2>${agent.agent_human_name} (${agentKey.replace(/_/g, ' ').toUpperCase()})</h2>
                                <p>Status: <span class="status ${agent.status}">${agent.status}</span></p>
                                <p class="task-info">Current Task: ${agent.current_task}</p>
                                <div class="progress-bar-container">
                                    <div class="progress-bar" style="width: ${agent.progress}%;"></div>
                                </div>
                                <p class="task-info">Progress: ${agent.progress}%</p>
                                <p class="task-info">Last Update: ${agent.last_update ? new Date(agent.last_update).toLocaleString() : 'N/A'}</p>
                                <p class="task-info">Tasks Completed (24h): ${agent.tasks_completed_24h}</p>
                                <p class="task-info">Longest Task 1: ${agent.longest_task_1.name} (${agent.longest_task_1.duration}s)</p>
                                <p class="task-info">Longest Task 2: ${agent.longest_task_2.name} (${agent.longest_task_2.duration}s)</p>
                            </div>
                        `;
                        agentGrid.appendChild(agentCard);
                    }
                })
                .catch(error => console.error('Error fetching agent status:', error));
        }

        // Fetch status every 3 seconds
        setInterval(fetchAgentStatus, 3000);
        // Initial fetch
        fetchAgentStatus();
    </script>
</body>
</html>
""")

    # Create a simple chat.html for the chat interface
    with open("templates/chat.html", "w") as f:
        f.write("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Chat Interface</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #1e1e1e; color: #d4d4d4; margin: 0; padding: 20px; }
        .container { max-width: 800px; margin: auto; background-color: #252526; padding: 20px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2); }
        h1 { color: #007acc; text-align: center; margin-bottom: 30px; }
        .chat-window { background-color: #333333; border-radius: 6px; padding: 15px; height: 400px; overflow-y: scroll; margin-bottom: 20px; border: 1px solid #555; }
        .message { margin-bottom: 10px; display: flex; align-items: flex-start; }
        .message.user { justify-content: flex-end; }
        .message.ai { justify-content: flex-start; }
        .message img { width: 40px; height: 40px; border-radius: 50%; margin: 0 10px; object-fit: cover; border: 2px solid #007acc; }
        .message-content { background-color: #444; padding: 10px 15px; border-radius: 15px; max-width: 70%; }
        .message.user .message-content { background-color: #007acc; color: white; }
        .message.ai .message-content { background-color: #555; color: #d4d4d4; }
        .input-area { display: flex; margin-top: 20px; }
        .input-area input { flex-grow: 1; padding: 10px; border: 1px solid #555; border-radius: 5px; background-color: #444; color: #d4d4d4; margin-right: 10px; }
        .input-area button { padding: 10px 15px; background-color: #007acc; color: white; border: none; border-radius: 5px; cursor: pointer; }
        .input-area button:hover { background-color: #005f99; }
        .header-links { text-align: center; margin-bottom: 20px; }
        .header-links a { color: #007acc; text-decoration: none; margin: 0 15px; font-size: 1.1em; }
        .header-links a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="container">
        <h1>AI Chat Interface</h1>
        <div class="header-links">
            <a href="/">Dashboard</a>
            <a href="/chat">AI Chat</a>
        </div>
        <div class="chat-window" id="chat-window">
            <!-- Chat messages will appear here -->
        </div>
        <div class="input-area">
            <input type="text" id="chat-input" placeholder="Type your message...">
            <button onclick="sendMessage()">Send</button>
        </div>
    </div>

    <script>
        const agentProfiles = {
            "project_manager": { "name": "Emily", "profile_picture": "" }, // Will be filled from /api/agent_status
            "backend_developer": { "name": "Henry", "profile_picture": "" },
            "frontend_developer": { "name": "Sophia", "profile_picture": "" },
            "database_ai": { "name": "Robert", "profile_picture": "" },
            "tester_ai": { "name": "Olivia", "profile_picture": "" },
            "fixer_ai": { "name": "Mason", "profile_picture": "" },
            "devops_ai": { "name": "Joshua", "profile_picture": "" },
            "documentation_ai": { "name": "Grace", "profile_picture": "" },
            "support_ai": { "name": "Chloe", "profile_picture": "" },
            "innovation_ai": { "name": "Noah", "profile_picture": "" },
            "ai_communication_hub": { "name": "Ava", "profile_picture": "" },
            "collective_memory_system": { "name": "Liam", "profile_picture": "" }
        };

        function fetchAgentProfiles() {
            fetch('/api/agent_status')
                .then(response => response.json())
                .then(data => {
                    for (const agentKey in data) {
                        if (agentProfiles[agentKey]) {
                            agentProfiles[agentKey].name = data[agentKey].agent_human_name;
                            agentProfiles[agentKey].profile_picture = data[agentKey].profile_picture;
                        }
                    }
                })
                .catch(error => console.error('Error fetching agent profiles:', error));
        }

        // Fetch profiles once on load
        fetchAgentProfiles();

        function sendMessage() {
            const chatInput = document.getElementById('chat-input');
            const chatWindow = document.getElementById('chat-window');
            const messageText = chatInput.value.trim();

            if (messageText) {
                // Display user message
                const userMessageDiv = document.createElement('div');
                userMessageDiv.className = 'message user';
                userMessageDiv.innerHTML = `
                    <div class="message-content">${messageText}</div>
                    <img src="https://randomuser.me/api/portraits/lego/1.jpg" alt="You">
                `;
                chatWindow.appendChild(userMessageDiv);

                // Simulate AI response (replace with actual AI interaction)
                // For demonstration, let's pick a random AI to respond
                const agentKeys = Object.keys(agentProfiles);
                const randomAgentKey = agentKeys[Math.floor(Math.random() * agentKeys.length)];
                const respondingAgent = agentProfiles[randomAgentKey];

                const aiMessageDiv = document.createElement('div');
                aiMessageDiv.className = 'message ai';
                aiMessageDiv.innerHTML = `
                    <img src="${respondingAgent.profile_picture}" alt="${respondingAgent.name}">
                    <div class="message-content">${respondingAgent.name}: I received your message: "${messageText}"</div>
                `;
                chatWindow.appendChild(aiMessageDiv);

                chatInput.value = ''; // Clear input
                chatWindow.scrollTop = chatWindow.scrollHeight; // Scroll to bottom
            }
        }

        // Allow sending message with Enter key
        document.getElementById('chat-input').addEventListener('keypress', function(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        });
    </script>
</body>
</html>
""")

    app.run(host="0.0.0.0", port=3333, debug=True)

