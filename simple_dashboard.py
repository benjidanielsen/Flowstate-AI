#!/usr/bin/env python3
"""
🎨 FLOWSTATE-AI SIMPLE DASHBOARD
⚡ Web interface for managing AI agents and CRM pipeline
🎯 Mission: Provide visual interface for system interaction
"""

from flask import Flask, render_template_string, jsonify, request
import sqlite3
import json
from pathlib import Path
from datetime import datetime

app = Flask(__name__)
PROJECT_ROOT = Path(__file__).parent
DB_PATH = PROJECT_ROOT / "godmode-state.db"

# HTML Template
DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Flowstate-AI Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        .header {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 30px;
            text-align: center;
        }
        .header h1 {
            color: #667eea;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .header p {
            color: #666;
            font-size: 1.1em;
        }
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
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.15);
        }
        .card h2 {
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.5em;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        .stat {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 10px;
            margin-bottom: 10px;
        }
        .stat-label {
            font-weight: 600;
            color: #555;
        }
        .stat-value {
            font-size: 1.3em;
            font-weight: bold;
            color: #667eea;
        }
        .task-item, .lead-item, .agent-item {
            padding: 15px;
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            border-radius: 8px;
            margin-bottom: 12px;
            transition: all 0.3s ease;
        }
        .task-item:hover, .lead-item:hover, .agent-item:hover {
            background: #e9ecef;
            transform: translateX(5px);
        }
        .task-title, .lead-name {
            font-weight: 600;
            color: #333;
            margin-bottom: 8px;
        }
        .task-meta, .lead-meta {
            font-size: 0.9em;
            color: #666;
        }
        .priority-high { border-left-color: #dc3545; }
        .priority-medium { border-left-color: #ffc107; }
        .priority-low { border-left-color: #28a745; }
        .status-online { color: #28a745; }
        .status-offline { color: #dc3545; }
        .status-idle { color: #ffc107; }
        .pipeline-stage {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 10px;
            text-align: center;
            font-weight: 600;
        }
        .pipeline-count {
            font-size: 2em;
            display: block;
            margin-top: 5px;
        }
        .refresh-btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 25px;
            font-size: 1em;
            cursor: pointer;
            transition: all 0.3s ease;
            margin: 20px auto;
            display: block;
        }
        .refresh-btn:hover {
            background: #764ba2;
            transform: scale(1.05);
        }
        .empty-state {
            text-align: center;
            padding: 30px;
            color: #999;
            font-style: italic;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Flowstate-AI Dashboard</h1>
            <p>AI Agent Coordination & CRM Pipeline Management</p>
        </div>
        
        <div class="grid">
            <!-- System Stats -->
            <div class="card">
                <h2>📊 System Status</h2>
                <div class="stat">
                    <span class="stat-label">Active Agents</span>
                    <span class="stat-value" id="agent-count">-</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Pending Tasks</span>
                    <span class="stat-value" id="task-count">-</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Total Leads</span>
                    <span class="stat-value" id="lead-count">-</span>
                </div>
            </div>
            
            <!-- CRM Pipeline -->
            <div class="card">
                <h2>🎯 CRM Pipeline (Frazer Method)</h2>
                <div id="pipeline-stages"></div>
            </div>
            
            <!-- Active Agents -->
            <div class="card">
                <h2>👥 Active Agents</h2>
                <div id="agents-list"></div>
            </div>
        </div>
        
        <div class="grid">
            <!-- Pending Tasks -->
            <div class="card">
                <h2>📋 Pending Tasks</h2>
                <div id="tasks-list"></div>
            </div>
            
            <!-- Recent Leads -->
            <div class="card">
                <h2>🎯 Recent Leads</h2>
                <div id="leads-list"></div>
            </div>
        </div>
        
        <button class="refresh-btn" onclick="loadData()">🔄 Refresh Data</button>
    </div>
    
    <script>
        async function loadData() {
            try {
                // Load system stats
                const statsResponse = await fetch('/api/stats');
                const stats = await statsResponse.json();
                document.getElementById('agent-count').textContent = stats.agents;
                document.getElementById('task-count').textContent = stats.tasks;
                document.getElementById('lead-count').textContent = stats.leads;
                
                // Load pipeline
                const pipelineResponse = await fetch('/api/pipeline');
                const pipeline = await pipelineResponse.json();
                const pipelineHTML = Object.entries(pipeline).map(([stage, count]) => 
                    `<div class="pipeline-stage">
                        ${stage.replace(/_/g, ' ').toUpperCase()}
                        <span class="pipeline-count">${count}</span>
                    </div>`
                ).join('');
                document.getElementById('pipeline-stages').innerHTML = pipelineHTML || '<div class="empty-state">No pipeline data</div>';
                
                // Load agents
                const agentsResponse = await fetch('/api/agents');
                const agents = await agentsResponse.json();
                const agentsHTML = agents.map(agent => 
                    `<div class="agent-item">
                        <div class="task-title">
                            <span class="status-${agent.status}"">●</span> ${agent.agent}
                        </div>
                        <div class="task-meta">Status: ${agent.status} | Task: ${agent.current_task || 'None'}</div>
                    </div>`
                ).join('');
                document.getElementById('agents-list').innerHTML = agentsHTML || '<div class="empty-state">No active agents</div>';
                
                // Load tasks
                const tasksResponse = await fetch('/api/tasks');
                const tasks = await tasksResponse.json();
                const tasksHTML = tasks.map(task => {
                    const priorityClass = task.priority >= 9 ? 'priority-high' : task.priority >= 5 ? 'priority-medium' : 'priority-low';
                    return `<div class="task-item ${priorityClass}">
                        <div class="task-title">#${task.id} ${task.title}</div>
                        <div class="task-meta">Assigned: ${task.assigned_to || 'Unassigned'} | Priority: ${task.priority}</div>
                    </div>`;
                }).join('');
                document.getElementById('tasks-list').innerHTML = tasksHTML || '<div class="empty-state">No pending tasks</div>';
                
                // Load leads
                const leadsResponse = await fetch('/api/leads');
                const leads = await leadsResponse.json();
                const leadsHTML = leads.map(lead => 
                    `<div class="lead-item">
                        <div class="lead-name">${lead.name}</div>
                        <div class="lead-meta">
                            ${lead.email || 'No email'} | Stage: ${lead.stage.replace(/_/g, ' ')}
                        </div>
                    </div>`
                ).join('');
                document.getElementById('leads-list').innerHTML = leadsHTML || '<div class="empty-state">No leads yet</div>';
                
            } catch (error) {
                console.error('Error loading data:', error);
            }
        }
        
        // Load data on page load
        loadData();
        
        // Auto-refresh every 10 seconds
        setInterval(loadData, 10000);
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(DASHBOARD_TEMPLATE)

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
    
    conn.close()
    
    return jsonify({
        'agents': agent_count,
        'tasks': task_count,
        'leads': lead_count
    })

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

@app.route('/api/agents')
def get_agents():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT agent_name, status, current_task, last_heartbeat
        FROM agent_status
        ORDER BY last_heartbeat DESC
    ''')
    
    agents = []
    for row in cursor.fetchall():
        agents.append({
            'agent': row[0],
            'status': row[1],
            'current_task': row[2],
            'last_heartbeat': row[3]
        })
    
    conn.close()
    return jsonify(agents)

@app.route('/api/tasks')
def get_tasks():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, title, description, priority, assigned_to
        FROM tasks
        WHERE status = 'pending'
        ORDER BY priority DESC, created_at ASC
        LIMIT 10
    ''')
    
    tasks = []
    for row in cursor.fetchall():
        tasks.append({
            'id': row[0],
            'title': row[1],
            'description': row[2],
            'priority': row[3],
            'assigned_to': row[4]
        })
    
    conn.close()
    return jsonify(tasks)

@app.route('/api/leads')
def get_leads():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, lead_name, lead_email, stage, score
        FROM crm_pipeline
        ORDER BY created_at DESC
        LIMIT 10
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

if __name__ == '__main__':
    print("🎨 Starting Flowstate-AI Simple Dashboard...")
    print("📊 Dashboard will be available at: http://localhost:5000")
    print("🔄 Auto-refresh enabled (every 10 seconds)")
    app.run(debug=True, host='0.0.0.0', port=5000)
