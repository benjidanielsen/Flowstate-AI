document.addEventListener('DOMContentLoaded', function() {
    // Function to switch tabs
    function switchTab(tabName) {
        document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

        const activeNavItem = document.querySelector(`.nav-item[data-tab="${tabName}"]`);
        if (activeNavItem) {
            activeNavItem.classList.add('active');
        }
        const activeTabContent = document.getElementById(`${tabName}-tab`);
        if (activeTabContent) {
            activeTabContent.classList.add('active');
        }
        document.getElementById('current-tab-title').textContent = activeNavItem ? activeNavItem.textContent.trim() : 'Home';
        loadTabData(tabName);
    }

    // Event listeners for navigation items
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', function() {
            switchTab(this.dataset.tab);
        });
    });

    // Load Data Functions
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
                <img src="${agent.profile_photo_url}" alt="${agent.human_name}" class="agent-avatar">
                <div class="agent-name">${agent.human_name} (${agent.agent_number})</div>
                <div class="agent-role">${agent.role}</div>
                <div class="agent-status-badge ${agent.status === 'active' ? 'active' : 'idle'}">${agent.status}</div>
                <div class="agent-task">${agent.current_task || 'Idle'}</div>
                <div class="agent-stats">
                    <div class="agent-stat-item">
                        <div class="agent-stat-value">${agent.tasks_completed}</div>
                        <div class="agent-stat-label">Completed</div>
                    </div>
                    <div class="agent-stat-item">
                        <div class="agent-stat-value">${agent.tasks_failed}</div>
                        <div class="agent-stat-label">Failed</div>
                    </div>
                </div>
            </div>
        `).join('');
        
        document.getElementById('agents-list').innerHTML = html || '<p>No active agents</p>';
    }

    async function loadTasks() {
        const response = await fetch('/api/tasks');
        const tasks = await response.json();
        
        const pendingHtml = tasks.filter(t => t.status === 'pending' || t.status === 'in_progress').map(task => `
            <div class="task-item ${task.status}">
                <div class="task-title">#${task.id} ${task.title}</div>
                <div class="task-meta">Status: ${task.status} | Priority: ${task.priority} | Assigned: ${task.assigned_to || 'Unassigned'}</div>
            </div>
        `).join('');

        const completedHtml = tasks.filter(t => t.status === 'completed').map(task => `
            <div class="task-item ${task.status}">
                <div class="task-title">#${task.id} ${task.title}</div>
                <div class="task-meta">Completed by: ${task.assigned_to || 'N/A'} | ${new Date(task.completed_at).toLocaleString()}</div>
            </div>
        `).join('');
        
        document.getElementById('pending-tasks').innerHTML = pendingHtml || '<p>No pending tasks</p>';
        document.getElementById('completed-tasks').innerHTML = completedHtml || '<p>No completed tasks</p>';
    }

    async function loadCRM() {
        const response = await fetch('/api/crm');
        const crmData = await response.json();
        
        const pipelineHtml = crmData.pipeline.map(stage => `
            <div class="pipeline-stage">
                <div class="pipeline-stage-header">${stage.name} <span class="count">(${stage.leads.length})</span></div>
                ${stage.leads.map(lead => `
                    <div class="lead-item">
                        <div class="lead-name">${lead.name}</div>
                        <div class="lead-email">${lead.email}</div>
                    </div>
                `).join('')}
            </div>
        `).join('');
        document.getElementById('crm-pipeline').innerHTML = pipelineHtml || '<p>No CRM data</p>';

        const recentLeadsHtml = crmData.recent_leads.map(lead => `
            <div class="item">
                <div class="item-title">${lead.name}</div>
                <div class="item-meta">${lead.email} | ${lead.stage}</div>
            </div>
        `).join('');
        document.getElementById('recent-leads').innerHTML = recentLeadsHtml || '<p>No recent leads</p>';
    }

    async function loadActivityLog() {
        const response = await fetch('/api/activity_log');
        const activities = await response.json();

        const html = activities.map(activity => `
            <div class="activity-item">
                <div class="activity-item-header">
                    <span>${activity.agent_name} (${activity.agent_number})</span>
                    <span>${new Date(activity.timestamp).toLocaleString()}</span>
                </div>
                <div class="activity-item-description">${activity.description}</div>
                <div class="activity-item-details">${activity.details}</div>
            </div>
        `).join('');
        document.getElementById('recent-activity').innerHTML = html || '<p>No recent activity</p>';
    }

    async function loadSystemStatus() {
        const response = await fetch('/api/system_status');
        const status = await response.json();
        document.getElementById('system-status').innerHTML = `
            <p><strong>Uptime:</strong> ${status.uptime}</p>
            <p><strong>Python Version:</strong> ${status.python_version}</p>
            <p><strong>Node.js Version:</strong> ${status.nodejs_version}</p>
            <p><strong>Database Size:</strong> ${status.db_size}</p>
            <p><strong>Last Git Commit:</strong> ${status.last_git_commit}</p>
        `;
    }

    async function sendMessage() {
        const chatInput = document.getElementById('chat-input');
        const message = chatInput.value;
        if (!message.trim()) return;

        const chatMessages = document.getElementById('chat-messages');
        
        // Add user message with profile
        const userMessageHTML = `
            <div class="chat-message user">
                <div class="chat-message-header">
                    <img src="https://ui-avatars.com/api/?name=Admin&background=10B981&color=fff&size=40&bold=true" alt="Admin" class="chat-avatar">
                    <div class="chat-message-info">
                        <span class="chat-agent-name">You</span>
                        <span class="chat-timestamp">${new Date().toLocaleTimeString('en-US', {hour: '2-digit', minute: '2-digit'})}</span>
                    </div>
                </div>
                <div class="chat-message-content">${message}</div>
            </div>
        `;
        chatMessages.innerHTML += userMessageHTML;
        chatInput.value = '';
        chatMessages.scrollTop = chatMessages.scrollHeight;

        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: message })
        });
        const data = await response.json();
        
        // Add AI response with profile
        const aiMessageHTML = `
            <div class="chat-message ai">
                <div class="chat-message-header">
                    <img src="https://ui-avatars.com/api/?name=PM&background=4F46E5&color=fff&size=40&bold=true" alt="PM AI" class="chat-avatar">
                    <div class="chat-message-info">
                        <span class="chat-agent-name">Project Manager AI</span>
                        <span class="chat-timestamp">${new Date().toLocaleTimeString('en-US', {hour: '2-digit', minute: '2-digit'})}</span>
                    </div>
                </div>
                <div class="chat-message-content">${data.response}</div>
            </div>
        `;
        chatMessages.innerHTML += aiMessageHTML;
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Load data based on active tab
    function loadTabData(tabName) {
        switch(tabName) {
            case 'home':
                loadStats();
                loadActivityLog();
                loadSystemStatus();
                break;
            case 'agents':
                loadAgents();
                break;
            case 'tasks':
                loadTasks();
                break;
            case 'crm':
                loadCRM();
                break;
            case 'logout':
                window.location.href = '/logout';
                break;
        }
    }

    // Make sendMessage globally accessible
    window.sendMessage = sendMessage;

    // Initial load and periodic refresh
    let currentActiveTab = 'home';
    switchTab(currentActiveTab);

    setInterval(() => {
        const activeTabElement = document.querySelector('.nav-item.active');
        if (activeTabElement) {
            currentActiveTab = activeTabElement.dataset.tab;
        }
        loadTabData(currentActiveTab);
    }, 5000); // Refresh every 5 seconds

    // Initial load of all data for home tab
    loadStats();
    loadActivityLog();
    loadSystemStatus();
    loadAgents();
    loadTasks();
    loadCRM();
});

