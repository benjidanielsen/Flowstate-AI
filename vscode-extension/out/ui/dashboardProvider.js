"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.DashboardProvider = void 0;
const vscode = __importStar(require("vscode"));
class DashboardProvider {
    constructor(extensionUri, communicationManager) {
        this.extensionUri = extensionUri;
        this.communicationManager = communicationManager;
    }
    show() {
        if (this.panel) {
            this.panel.reveal(vscode.ViewColumn.One);
        }
        else {
            this.panel = vscode.window.createWebviewPanel('flowstateAIDashboard', 'FlowState-AI Dashboard', vscode.ViewColumn.One, {
                enableScripts: true,
                retainContextWhenHidden: true
            });
            this.panel.webview.html = this.getHtmlContent();
            // Handle messages from the webview
            this.panel.webview.onDidReceiveMessage(message => this.handleWebviewMessage(message), undefined, []);
            // Start updating dashboard
            this.startUpdates();
            // Clean up when panel is closed
            this.panel.onDidDispose(() => {
                this.stopUpdates();
                this.panel = undefined;
            });
        }
    }
    startUpdates() {
        // Update dashboard every 2 seconds
        this.updateInterval = setInterval(async () => {
            await this.updateDashboard();
        }, 2000);
        // Initial update
        this.updateDashboard();
    }
    stopUpdates() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = undefined;
        }
    }
    async updateDashboard() {
        if (!this.panel) {
            return;
        }
        try {
            const [agentStatus, tasks, systemStatus] = await Promise.all([
                this.communicationManager.getAgentStatus(),
                this.communicationManager.getTasks(),
                this.communicationManager.getSystemStatus()
            ]);
            this.panel.webview.postMessage({
                type: 'update',
                data: {
                    agents: agentStatus,
                    tasks,
                    system: systemStatus,
                    timestamp: new Date().toISOString()
                }
            });
        }
        catch (error) {
            console.error('Error updating dashboard:', error);
        }
    }
    async handleWebviewMessage(message) {
        switch (message.command) {
            case 'startGodmode':
                await vscode.commands.executeCommand('flowstate-ai.startGodmode');
                break;
            case 'stopGodmode':
                await vscode.commands.executeCommand('flowstate-ai.stopGodmode');
                break;
            case 'fixEverything':
                await vscode.commands.executeCommand('flowstate-ai.fixEverything');
                break;
            case 'refresh':
                await this.updateDashboard();
                break;
        }
    }
    getHtmlContent() {
        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FlowState-AI Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: #1e1e1e;
            color: #d4d4d4;
            padding: 20px;
        }
        
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #3c3c3c;
        }
        
        .header h1 {
            font-size: 28px;
            font-weight: 600;
            color: #4ec9b0;
        }
        
        .controls {
            display: flex;
            gap: 10px;
        }
        
        button {
            background: #0e639c;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            transition: background 0.2s;
        }
        
        button:hover {
            background: #1177bb;
        }
        
        button.danger {
            background: #d73a49;
        }
        
        button.danger:hover {
            background: #cb2431;
        }
        
        button.success {
            background: #28a745;
        }
        
        button.success:hover {
            background: #22863a;
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: #252526;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #4ec9b0;
        }
        
        .stat-card h3 {
            font-size: 14px;
            color: #858585;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .stat-card .value {
            font-size: 32px;
            font-weight: 700;
            color: #4ec9b0;
        }
        
        .section {
            background: #252526;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        
        .section h2 {
            font-size: 20px;
            margin-bottom: 20px;
            color: #4ec9b0;
        }
        
        .agent-list {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        
        .agent-item {
            background: #1e1e1e;
            padding: 15px;
            border-radius: 6px;
            border-left: 4px solid #569cd6;
        }
        
        .agent-item.active {
            border-left-color: #4ec9b0;
        }
        
        .agent-item.error {
            border-left-color: #f48771;
        }
        
        .agent-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .agent-name {
            font-size: 16px;
            font-weight: 600;
            color: #d4d4d4;
        }
        
        .agent-status {
            font-size: 12px;
            padding: 4px 12px;
            border-radius: 12px;
            background: #3c3c3c;
            color: #858585;
        }
        
        .agent-status.active {
            background: #4ec9b0;
            color: #1e1e1e;
        }
        
        .agent-task {
            font-size: 14px;
            color: #858585;
            margin-bottom: 10px;
        }
        
        .progress-bar {
            width: 100%;
            height: 8px;
            background: #3c3c3c;
            border-radius: 4px;
            overflow: hidden;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #4ec9b0, #569cd6);
            transition: width 0.3s ease;
        }
        
        .task-list {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        
        .task-item {
            background: #1e1e1e;
            padding: 12px;
            border-radius: 6px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .task-name {
            font-size: 14px;
            color: #d4d4d4;
        }
        
        .task-status {
            font-size: 12px;
            padding: 3px 10px;
            border-radius: 10px;
            background: #3c3c3c;
            color: #858585;
        }
        
        .timestamp {
            text-align: right;
            font-size: 12px;
            color: #858585;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 FlowState-AI GODMODE Dashboard</h1>
        <div class="controls">
            <button onclick="sendCommand('startGodmode')" class="success">Start GODMODE</button>
            <button onclick="sendCommand('stopGodmode')" class="danger">Stop</button>
            <button onclick="sendCommand('fixEverything')">Fix Everything</button>
            <button onclick="sendCommand('refresh')">Refresh</button>
        </div>
    </div>
    
    <div class="stats">
        <div class="stat-card">
            <h3>Active Agents</h3>
            <div class="value" id="activeAgents">0</div>
        </div>
        <div class="stat-card">
            <h3>Tasks Queued</h3>
            <div class="value" id="tasksQueued">0</div>
        </div>
        <div class="stat-card">
            <h3>Tasks Completed</h3>
            <div class="value" id="tasksCompleted">0</div>
        </div>
        <div class="stat-card">
            <h3>System Status</h3>
            <div class="value" id="systemStatus">IDLE</div>
        </div>
    </div>
    
    <div class="section">
        <h2>AI Agent Activity</h2>
        <div class="agent-list" id="agentList">
            <p style="color: #858585;">No agents active</p>
        </div>
    </div>
    
    <div class="section">
        <h2>Task Progress</h2>
        <div class="task-list" id="taskList">
            <p style="color: #858585;">No tasks</p>
        </div>
    </div>
    
    <div class="timestamp" id="timestamp">Last updated: Never</div>
    
    <script>
        const vscode = acquireVsCodeApi();
        
        function sendCommand(command) {
            vscode.postMessage({ command });
        }
        
        window.addEventListener('message', event => {
            const message = event.data;
            
            if (message.type === 'update') {
                updateDashboard(message.data);
            }
        });
        
        function updateDashboard(data) {
            // Update stats
            document.getElementById('activeAgents').textContent = data.agents?.length || 0;
            document.getElementById('tasksQueued').textContent = data.system?.queued_tasks || 0;
            document.getElementById('tasksCompleted').textContent = data.system?.completed_tasks || 0;
            document.getElementById('systemStatus').textContent = data.system?.system_status || 'UNKNOWN';
            
            // Update agent list
            const agentList = document.getElementById('agentList');
            if (data.agents && data.agents.length > 0) {
                agentList.innerHTML = data.agents.map(agent => \`
                    <div class="agent-item \${agent.status === 'ACTIVE' ? 'active' : ''}">
                        <div class="agent-header">
                            <span class="agent-name">\${agent.agent_id}</span>
                            <span class="agent-status \${agent.status === 'ACTIVE' ? 'active' : ''}">\${agent.status}</span>
                        </div>
                        <div class="agent-task">\${agent.current_task || 'Idle'}</div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: \${agent.progress || 0}%"></div>
                        </div>
                    </div>
                \`).join('');
            } else {
                agentList.innerHTML = '<p style="color: #858585;">No agents active</p>';
            }
            
            // Update task list
            const taskList = document.getElementById('taskList');
            if (data.tasks && data.tasks.length > 0) {
                taskList.innerHTML = data.tasks.slice(0, 10).map(task => \`
                    <div class="task-item">
                        <span class="task-name">\${task.name || task.id}</span>
                        <span class="task-status">\${task.status}</span>
                    </div>
                \`).join('');
            } else {
                taskList.innerHTML = '<p style="color: #858585;">No tasks</p>';
            }
            
            // Update timestamp
            document.getElementById('timestamp').textContent = 
                'Last updated: ' + new Date(data.timestamp).toLocaleTimeString();
        }
    </script>
</body>
</html>`;
    }
}
exports.DashboardProvider = DashboardProvider;
//# sourceMappingURL=dashboardProvider.js.map