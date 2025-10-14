#!/usr/bin/env python3
"""
🎨 FLOWSTATE-AI SIMPLE DASHBOARD
⚡ Web interface for managing AI agents and CRM pipeline
🎯 Mission: Provide visual interface for system interaction
"""

from flask import Flask, render_template_string, jsonify
import sqlite3
from pathlib import Path
from contextlib import closing
from typing import Iterable, List, Optional

app = Flask(__name__)
PROJECT_ROOT = Path(__file__).parent
DB_PATH = PROJECT_ROOT / "godmode-state.db"
PIPELINE_STAGES = [
    "lead_generation",
    "qualification",
    "nurturing",
    "conversion",
    "retention",
]


def fetch_all(query: str, params: Iterable = ()) -> Optional[List[sqlite3.Row]]:
    """Execute a SELECT query and return all rows or None on failure.

    Returning ``None`` instead of an empty list allows callers to
    differentiate between a successful query with no rows and an error such
    as a missing database or table. This keeps the API responses resilient
    even when the dashboard is launched before the SQLite state has been
    initialised.
    """

    if not DB_PATH.exists():
        app.logger.warning("Dashboard database not found at %s", DB_PATH)
        return None

    try:
        with closing(sqlite3.connect(DB_PATH)) as conn:
            conn.row_factory = sqlite3.Row
            with closing(conn.cursor()) as cursor:
                cursor.execute(query, params)
                # ``fetchall`` returns a list, so explicitly convert it to
                # ensure the data survives once the connection closes.
                return list(cursor.fetchall())
    except sqlite3.Error as exc:  # pragma: no cover - defensive logging
        app.logger.error("Database query failed: %s", exc)
        return None


def _database_unavailable_response(payload):
    response = {"error": "database_unavailable"}
    if isinstance(payload, dict):
        response.update(payload)
    else:
        response["data"] = payload
    return jsonify(response), 503

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
    stats = {'agents': 0, 'tasks': 0, 'leads': 0}

    agent_row = fetch_all("SELECT COUNT(*) AS count FROM agent_status")
    if agent_row is None:
        return _database_unavailable_response(stats)
    stats['agents'] = agent_row[0]['count'] if agent_row else 0

    task_row = fetch_all("SELECT COUNT(*) AS count FROM tasks WHERE status = 'pending'")
    if task_row is None:
        return _database_unavailable_response(stats)
    stats['tasks'] = task_row[0]['count'] if task_row else 0

    lead_row = fetch_all("SELECT COUNT(*) AS count FROM crm_pipeline")
    if lead_row is None:
        return _database_unavailable_response(stats)
    stats['leads'] = lead_row[0]['count'] if lead_row else 0

    return jsonify(stats)

@app.route('/api/pipeline')
def get_pipeline():
    stages = {stage: 0 for stage in PIPELINE_STAGES}

    for stage in PIPELINE_STAGES:
        rows = fetch_all("SELECT COUNT(*) AS count FROM crm_pipeline WHERE stage = ?", (stage,))
        if rows is None:
            return _database_unavailable_response(stages)
        stages[stage] = rows[0]['count'] if rows else 0

    return jsonify(stages)

@app.route('/api/agents')
def get_agents():
    rows = fetch_all(
        '''
        SELECT agent_name, status, current_task, last_heartbeat
        FROM agent_status
        ORDER BY last_heartbeat DESC
        '''
    )
    if rows is None:
        return _database_unavailable_response([])

    agents = [
        {
            'agent': row['agent_name'],
            'status': row['status'],
            'current_task': row['current_task'],
            'last_heartbeat': row['last_heartbeat'],
        }
        for row in rows
    ]

    return jsonify(agents)

@app.route('/api/tasks')
def get_tasks():
    rows = fetch_all(
        '''
        SELECT id, title, description, priority, assigned_to
        FROM tasks
        WHERE status = 'pending'
        ORDER BY priority DESC, created_at ASC
        LIMIT 10
        '''
    )
    if rows is None:
        return _database_unavailable_response([])

    tasks = [
        {
            'id': row['id'],
            'title': row['title'],
            'description': row['description'],
            'priority': row['priority'],
            'assigned_to': row['assigned_to'],
        }
        for row in rows
    ]

    return jsonify(tasks)

@app.route('/api/leads')
def get_leads():
    rows = fetch_all(
        '''
        SELECT id, lead_name, lead_email, stage, score
        FROM crm_pipeline
        ORDER BY created_at DESC
        LIMIT 10
        '''
    )
    if rows is None:
        return _database_unavailable_response([])

    leads = [
        {
            'id': row['id'],
            'name': row['lead_name'],
            'email': row['lead_email'],
            'stage': row['stage'],
            'score': row['score'],
        }
        for row in rows
    ]

    return jsonify(leads)

if __name__ == '__main__':
    print("🎨 Starting Flowstate-AI Simple Dashboard...")
    print("📊 Dashboard will be available at: http://localhost:5000")
    print("🔄 Auto-refresh enabled (every 10 seconds)")
    app.run(debug=True, host='0.0.0.0', port=5000)
