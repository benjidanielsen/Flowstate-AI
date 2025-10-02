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
exports.AgentActivityProvider = void 0;
const vscode = __importStar(require("vscode"));
class AgentActivityProvider {
    constructor(communicationManager) {
        this.communicationManager = communicationManager;
        this._onDidChangeTreeData = new vscode.EventEmitter();
        this.onDidChangeTreeData = this._onDidChangeTreeData.event;
        // Listen for updates from backend
        this.communicationManager.on('agent_status_update', () => {
            this.refresh();
        });
        // Refresh every 5 seconds
        setInterval(() => this.refresh(), 5000);
    }
    refresh() {
        this._onDidChangeTreeData.fire();
    }
    getTreeItem(element) {
        return element;
    }
    async getChildren(element) {
        if (!element) {
            // Root level - show agents
            try {
                const agents = await this.communicationManager.getAgentStatus();
                return agents.map(agent => new AgentActivityItem(agent.agent_id, agent.status, agent.current_task, agent.progress, vscode.TreeItemCollapsibleState.None));
            }
            catch (error) {
                return [new AgentActivityItem('Error loading agents', 'ERROR', '', 0, vscode.TreeItemCollapsibleState.None)];
            }
        }
        return [];
    }
}
exports.AgentActivityProvider = AgentActivityProvider;
class AgentActivityItem extends vscode.TreeItem {
    constructor(label, status, currentTask, progress, collapsibleState) {
        super(label, collapsibleState);
        this.label = label;
        this.status = status;
        this.currentTask = currentTask;
        this.progress = progress;
        this.collapsibleState = collapsibleState;
        this.tooltip = `${this.label}\nStatus: ${status}\nTask: ${currentTask || 'Idle'}\nProgress: ${progress}%`;
        this.description = `${progress}% - ${currentTask || 'Idle'}`;
        // Set icon based on status
        if (status === 'ACTIVE') {
            this.iconPath = new vscode.ThemeIcon('pulse', new vscode.ThemeColor('charts.green'));
        }
        else if (status === 'ERROR') {
            this.iconPath = new vscode.ThemeIcon('error', new vscode.ThemeColor('charts.red'));
        }
        else {
            this.iconPath = new vscode.ThemeIcon('circle-outline', new vscode.ThemeColor('charts.gray'));
        }
    }
}
//# sourceMappingURL=agentActivityProvider.js.map