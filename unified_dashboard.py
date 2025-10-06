#!/usr/bin/env python3
"""
🚀 FLOWSTATE-AI UNIFIED SUPER DASHBOARD
⚡ All-in-one interface: AI Agents + CRM + Tasks + Chat + Analytics
🎯 Mission: Single dashboard for complete system control
"""

from flask import Flask, render_template_string, jsonify, request
import sqlite3
import json
from pathlib import Path
from datetime import datetime
from openai import OpenAI

app = Flask(__name__, static_folder=PROJECT_ROOT / "static")
PROJECT_ROOT = Path(__file__).parent
DB_PATH = PROJECT_ROOT / "godmode-state.db"

# Initialize OpenAI client
client = OpenAI()

# Main HTML Template with Tabs
UNIFIED_DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Flowstate-AI Unified Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            min-height: 100vh;
        }
        
        /* Header */
        .header {
            background: white;
            padding: 20px 40px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .header h1 {
            color: #667eea;
            font-size: 1.8em;
        }
        .header .status {
            display: flex;
            gap: 20px;
            align-items: center;
        }
        .status-badge {
            padding: 8px 16px;
            border-radius: 20px;
            background: #28a745;
            color: white;
            font-weight: 600;
            font-size: 0.9em;
        }
        
        /* Navigation Tabs */
        .nav-tabs {
            background: white;
            display: flex;
            padding: 0 40px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }
        .nav-tab {
            padding: 15px 30px;
            cursor: pointer;
            border-bottom: 3px solid transparent;
            transition: all 0.3s;
            font-weight: 600;
            color: #666;
        }
        .nav-tab:hover {
            background: #f8f9fa;
            color: #667eea;
        }
        .nav-tab.active {
            color: #667eea;
            border-bottom-color: #667eea;
        }
        
        /* Content Area */
        .content {
            padding: 30px 40px;
            max-width: 1600px;
            margin: 0 auto;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
        
        /* Cards */
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .card {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .card h2 {
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.3em;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        
        /* Stats */
        .stat-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
        .stat-value {
            font-size: 2.5em;
            font-weight: bold;
            margin: 10px 0;
        }
        .stat-label {
            font-size: 0.9em;
            opacity: 0.9;
        }
        
        /* Items */
        .item {
            padding: 15px;
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            border-radius: 8px;
            margin-bottom: 12px;
        }
        .item-title {
            font-weight: 600;
            color: #333;
            margin-bottom: 5px;
        }
        .item-meta {
            font-size: 0.9em;
            color: #666;
        }
        
        /* Chat Interface */
        .chat-container {
            background: white;
            border-radius: 15px;
            padding: 20px;
            height: 600px;
            display: flex;
            flex-direction: column;
        }
        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .chat-message {
            margin-bottom: 15px;
            padding: 12px 16px;
            border-radius: 10px;
            max-width: 80%;
        }
        .chat-message.user {
            background: #667eea;
            color: white;
            margin-left: auto;
        }
        .chat-message.ai {
            background: white;
            border: 1px solid #ddd;
        }
        .chat-input-container {
            display: flex;
            gap: 10px;
        }
        .chat-input {
            flex: 1;
            padding: 12px 16px;
            border: 2px solid #667eea;
            border-radius: 25px;
            font-size: 1em;
        }
        .chat-send {
            padding: 12px 30px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-weight: 600;
        }
        .chat-send:hover {
            background: #764ba2;
        }
        
        /* Pipeline Visualization */
        .pipeline {
            display: flex;
            gap: 15px;
            overflow-x: auto;
            padding: 20px 0;
        }
        .pipeline-stage {
            min-width: 250px;
            background: white;
            border-radius: 10px;
            padding: 15px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .pipeline-stage-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px;
            border-radius: 8px;
            text-align: center;
            font-weight: 600;
            margin-bottom: 15px;
        }
        .pipeline-count {
            font-size: 1.5em;
            display: block;
            margin-top: 5px;
        }
        
        /* Buttons */
        .btn {
            padding: 10px 20px;
            border-radius: 20px;
            border: none;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s;
        }
        .btn-primary {
            background: #667eea;
            color: white;
        }
        .btn-primary:hover {
            background: #764ba2;
        }
        
        /* Agent Status */
        .agent-card {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 10px;
            margin-bottom: 10px;
        }
        .agent-info {
            flex: 1;
        }
        .agent-name {
            font-weight: 600;
            color: #333;
            margin-bottom: 5px;
        }
        .agent-task {
            font-size: 0.9em;
            color: #666;
        }
        .agent-status {
            padding: 6px 12px;
            border-radius: 15px;
            font-size: 0.85em;
            font-weight: 600;
        }
        .status-active { background: #28a745; color: white; }
        .status-idle { background: #ffc107; color: #333; }
        .status-offline { background: #dc3545; color: white; }
        
        /* Responsive */
        @media (max-width: 768px) {
            .grid { grid-template-columns: 1fr; }
            .stat-grid { grid-template-columns: repeat(2, 1fr); }
            .pipeline { flex-direction: column; }
        }
    </style>
</head>
<body>
    <!-- Header -->
    <div class="header">
        <h1>🚀 Flowstate-AI Unified Dashboard</h1>
        <div class="status">
            <span class="status-badge">🤖 AI Active</span>
            <span class="status-badge">✅ System Online</span>
        </div>
    </div>
    
    <!-- Navigation Tabs -->
    <div class="nav-tabs">
        <div class="nav-tab active" onclick="switchTab('home')">🏠 Home</div>
        <div class="nav-tab" onclick="switchTab('agents')">🤖 AI Agents</div>
        <div class="nav-tab" onclick="switchTab('crm')">🎯 CRM Pipeline</div>
        <div class="nav-tab" onclick="switchTab('tasks')">📋 Tasks</div>
        <div class="nav-tab" onclick="switchTab('chat')">💬 Chat</div>
        <div class="nav-tab" onclick="switchTab('analytics')">📊 Analytics</div>
    </div>
    
    <!-- Content Area -->
    <div class="content">
        <!-- Home Tab -->
        <div id="home-tab" class="tab-content active">
            <div class="stat-grid">
                <div class="stat-card">
                    <div class="stat-label">Active AI Agents</div>
                    <div class="stat-value" id="home-agents">-</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Pending Tasks</div>
                    <div class="stat-value" id="home-tasks">-</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Total Leads</div>
                    <div class="stat-value" id="home-leads">-</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Tasks Completed Today</div>
                    <div class="stat-value" id="home-completed">-</div>
                </div>
            </div>
            
            <div class="grid" style="margin-top: 30px;">
                <div class="card">
                    <h2>🚀 Recent Activity</h2>
                    <div id="recent-activity"></div>
                </div>
                <div class="card">
                    <h2>⚡ System Status</h2>
                    <div id="system-status"></div>
                </div>
            </div>
        </div>
        
        <!-- AI Agents Tab -->
        <div id="agents-tab" class="tab-content">
            <div class="card">
                <h2>🤖 Active AI Agents</h2>
                <div id="agents-list"></div>
            </div>
        </div>
        
        <!-- CRM Pipeline Tab -->
        <div id="crm-tab" class="tab-content">
            <div class="card">
                <h2>🎯 Frazer Method CRM Pipeline</h2>
                <div class="pipeline" id="crm-pipeline"></div>
            </div>
            <div class="card" style="margin-top: 20px;">
                <h2>📋 Recent Leads</h2>
                <div id="recent-leads"></div>
            </div>
        </div>
        
        <!-- Tasks Tab -->
        <div id="tasks-tab" class="tab-content">
            <div class="grid">
                <div class="card">
                    <h2>📋 Pending Tasks</h2>
                    <div id="pending-tasks"></div>
                </div>
                <div class="card">
                    <h2>✅ Completed Tasks</h2>
                    <div id="completed-tasks"></div>
                </div>
            </div>
        </div>
        
        <!-- Chat Tab -->
        <div id="chat-tab" class="tab-content">
            <div class="chat-container">
                <h2 style="margin-bottom: 20px;">💬 Chat with Project Manager AI</h2>
                <div class="chat-messages" id="chat-messages">
                    <div class="chat-message ai">
                        Hello! I'm the Project Manager AI. How can I help you today?
                    </div>
                </div>
                <div class="chat-input-container">
                    <input type="text" class="chat-input" id="chat-input" placeholder="Type your message...">
                    <button class="chat-send" onclick="sendMessage()">Send</button>
                </div>
            </div>
        </div>
        
        <!-- Analytics Tab -->
        <div id="analytics-tab" class="tab-content">
            <div class="grid">
                <div class="card">
                    <h2>📊 Task Completion Rate</h2>
                    <div id="completion-rate"></div>
                </div>
                <div class="card">
                    <h2>📈 CRM Conversion Funnel</h2>
                    <div id="conversion-funnel"></div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Tab Switching
        function switchTab(tabName) {
            document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            event.target.classList.add('active');
            document.getElementById(tabName + '-tab').classList.add('active');
            
            // Load data for the tab
            loadTabData(tabName);
        }
        
        // Load Data
        async function loadTabData(tab) {
            if (tab === 'home' || tab === 'agents') {
                await loadAgents();
            }
            if (tab === 'home' || tab === 'tasks') {
                await loadTasks();
            }
            if (tab === 'home' || tab === 'crm') {
                await loadCRM();
            }
            if (tab === 'home') {
                await loadStats();
            }
        }
        
        async function loadStats() {
            const response = await fetch('/api/stats');
            const stats = await response.json();
            document.getElementById('home-agents').textContent = stats.agents;
            document.getElementById('home-tasks').textContent = stats.tasks;
            document.getElementById('home-leads').textContent = stats.leads;
            document.getElementById('home-completed').textContent = stats.completed_today;
        }
        
        async function loadAgents() {
            const response = await fetch('/api/agents');
            const agents = await response.json();
            
            const html = agents.map(agent => `
                <div class="agent-card">
                    <div class="agent-info">
                        <div class="agent-name">${agent.agent}</div>
                        <div class="agent-task">${agent.current_task || 'Idle'}</div>
                    </div>
                    <div class="agent-status status-${agent.status}">${agent.status}</div>
                </div>
            `).join('');
            
            document.getElementById('agents-list').innerHTML = html || '<p>No active agents</p>';
        }
        
        async function loadTasks() {
            const response = await fetch('/api/tasks');
            const tasks = await response.json();
            
            const pendingHtml = tasks.filter(t => t.status === 'pending').slice(0, 10).map(task => `
                <div class="item">
                    <div class="item-title">#${task.id} ${task.title}</div>
                    <div class="item-meta">Priority: ${task.priority} | ${task.assigned_to || 'Unassigned'}</div>
                </div>
            `).join('');
            
            const completedHtml = tasks.filter(t => t.status === 'completed').slice(0, 10).map(task => `
                <div class="item">
                    <div class="item-title">#${task.id} ${task.title}</div>
                    <div class="item-meta">Completed</div>
                </div>
            `).join('');
            
            document.getElementById('pending-tasks').innerHTML = pendingHtml || '<p>No pending tasks</p>';
            document.getElementById('completed-tasks').innerHTML = completedHtml || '<p>No completed tasks</p>';
        }
        
        async function loadCRM() {
            const response = await fetch('/api/pipeline');
            const pipeline = await response.json();
            
            const stages = ['lead_generation', 'qualification', 'nurturing', 'conversion', 'retention'];
            const stageNames = ['Lead Generation', 'Qualification', 'Nurturing', 'Conversion', 'Retention'];
            
            const html = stages.map((stage, i) => `
                <div class="pipeline-stage">
                    <div class="pipeline-stage-header">
                        ${stageNames[i]}
                        <span class="pipeline-count">${pipeline[stage] || 0}</span>
                    </div>
                </div>
            `).join('');
            
            document.getElementById('crm-pipeline').innerHTML = html;
            
            // Load recent leads
            const leadsResponse = await fetch('/api/leads');
            const leads = await leadsResponse.json();
            
            const leadsHtml = leads.slice(0, 10).map(lead => `
                <div class="item">
                    <div class="item-title">${lead.name}</div>
                    <div class="item-meta">${lead.email || 'No email'} | ${lead.stage.replace(/_/g, ' ')}</div>
                </div>
            `).join('');
            
            document.getElementById('recent-leads').innerHTML = leadsHtml || '<p>No leads yet</p>';
        }
        
        // Chat
        async function sendMessage() {
            const input = document.getElementById('chat-input');
            const message = input.value.trim();
            if (!message) return;
            
            // Add user message
            const messagesDiv = document.getElementById('chat-messages');
            messagesDiv.innerHTML += `<div class="chat-message user">${message}</div>`;
            input.value = '';
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
            
            // Send to API
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message})
            });
            const data = await response.json();
            
            // Add AI response
            messagesDiv.innerHTML += `<div class="chat-message ai">${data.response}</div>`;
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
        
        // Initial load
        loadTabData('home');
        
        // Auto-refresh every 10 seconds
        setInterval(() => {
            const activeTab = document.querySelector('.tab-content.active').id.replace('-tab', '');
            loadTabData(activeTab);
        }, 10000);
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(UNIFIED_DASHBOARD_TEMPLATE)

@app.route('/api/stats')
def get_stats():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM agent_status")
    agent_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'pending'")
    task_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM crm_pipeline")
    lead_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'completed' AND DATE(completed_at) = DATE('now')")
    completed_today = cursor.fetchone()[0]
    
    conn.close()
    
    return jsonify({
        'agents': agent_count,
        'tasks': task_count,
        'leads': lead_count,
        'completed_today': completed_today
    })

@app.route('/api/agents')
def get_agents():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT
            as_t.agent_name,
            as_t.status,
            as_t.current_task,
            as_t.last_heartbeat,
            a.profile_photo_url,
            a.gender
        FROM agent_status as_t
        JOIN agents a ON as_t.agent_name = a.human_name
        ORDER BY as_t.last_heartbeat DESC
    ''')
    
    agents = []
    for row in cursor.fetchall():
            agents.append({
                'agent': row[0],
                'status': row[1],
                'current_task': row[2],
                'last_heartbeat': row[3],
                'profile_photo_url': row[4],
                'gender': row[5]
            })
    
    conn.close()
    return jsonify(agents)

@app.route('/api/tasks')
def get_tasks():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, title, description, priority, assigned_to, status
        FROM tasks
        ORDER BY priority DESC, created_at DESC
        LIMIT 50
    ''')
    
    tasks = []
    for row in cursor.fetchall():
        tasks.append({
            'id': row[0],
            'title': row[1],
            'description': row[2],
            'priority': row[3],
            'assigned_to': row[4],
            'status': row[5]
        })
    
    conn.close()
    return jsonify(tasks)

@app.route('/api/pipeline')
def get_pipeline():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    stages = {}
    for stage in ['lead_generation', 'qualification', 'nurturing', 'conversion', 'retention']:
        cursor.execute("SELECT COUNT(*) FROM crm_pipeline WHERE stage = ?", (stage,))
        stages[stage] = cursor.fetchone()[0]
    
    conn.close()
    return jsonify(stages)

@app.route('/api/leads')
def get_leads():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, lead_name, lead_email, stage, score
        FROM crm_pipeline
        ORDER BY created_at DESC
        LIMIT 20
    ''')
    
    leads = []
    for row in cursor.fetchall():
        leads.append({
            'id': row[0],
            'name': row[1],
            'email': row[2],
            'stage': row[3],
            'score': row[4]
        })
    
    conn.close()
    return jsonify(leads)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    
    try:
        # Get AI response
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are the Project Manager AI for Flowstate-AI. You help manage tasks, coordinate agents, and answer questions about the system."},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        ai_response = response.choices[0].message.content
        return jsonify({'response': ai_response})
    except Exception as e:
        return jsonify({'response': f"Sorry, I encountered an error: {str(e)}"})

if __name__ == '__main__':
    print("🚀 Starting Flowstate-AI Unified Dashboard...")
    print("📊 Dashboard available at: http://localhost:5000")
    print("🔄 Auto-refresh enabled (every 10 seconds)")
    print("\n✨ Features:")
    print("   - 🏠 Home: System overview")
    print("   - 🤖 AI Agents: Agent status and control")
    print("   - 🎯 CRM Pipeline: Frazer Method visualization")
    print("   - 📋 Tasks: Task management")
    print("   - 💬 Chat: Talk to Project Manager AI")
    print("   - 📊 Analytics: Metrics and reports")
    app.run(debug=True, host='0.0.0.0', port=5000)
