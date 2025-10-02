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
exports.SystemStatusProvider = void 0;
const vscode = __importStar(require("vscode"));
class SystemStatusProvider {
    constructor(communicationManager) {
        this.communicationManager = communicationManager;
        this._onDidChangeTreeData = new vscode.EventEmitter();
        this.onDidChangeTreeData = this._onDidChangeTreeData.event;
        // Listen for updates from backend
        this.communicationManager.on('system_status_update', () => {
            this.refresh();
        });
        // Refresh every 10 seconds
        setInterval(() => this.refresh(), 10000);
    }
    refresh() {
        this._onDidChangeTreeData.fire();
    }
    getTreeItem(element) {
        return element;
    }
    async getChildren(element) {
        if (!element) {
            // Root level - show system metrics
            try {
                const status = await this.communicationManager.getSystemStatus();
                return [
                    new SystemStatusItem('System Status', status.system_status || 'UNKNOWN', vscode.TreeItemCollapsibleState.None),
                    new SystemStatusItem('Active Agents', String(status.active_agents || 0), vscode.TreeItemCollapsibleState.None),
                    new SystemStatusItem('Total Tasks', String(status.total_tasks || 0), vscode.TreeItemCollapsibleState.None),
                    new SystemStatusItem('Queued Tasks', String(status.queued_tasks || 0), vscode.TreeItemCollapsibleState.None),
                    new SystemStatusItem('In Progress', String(status.in_progress_tasks || 0), vscode.TreeItemCollapsibleState.None),
                    new SystemStatusItem('Completed', String(status.completed_tasks || 0), vscode.TreeItemCollapsibleState.None),
                    new SystemStatusItem('Failed', String(status.failed_tasks || 0), vscode.TreeItemCollapsibleState.None),
                    new SystemStatusItem('GODMODE', status.godmode_enabled ? 'ENABLED' : 'DISABLED', vscode.TreeItemCollapsibleState.None)
                ];
            }
            catch (error) {
                return [new SystemStatusItem('Error', 'Failed to load system status', vscode.TreeItemCollapsibleState.None)];
            }
        }
        return [];
    }
}
exports.SystemStatusProvider = SystemStatusProvider;
class SystemStatusItem extends vscode.TreeItem {
    constructor(label, value, collapsibleState) {
        super(label, collapsibleState);
        this.label = label;
        this.value = value;
        this.collapsibleState = collapsibleState;
        this.description = value;
        this.tooltip = `${this.label}: ${value}`;
        // Set icon based on label
        if (label === 'System Status') {
            if (value === 'ACTIVE') {
                this.iconPath = new vscode.ThemeIcon('check-all', new vscode.ThemeColor('charts.green'));
            }
            else if (value === 'ERROR') {
                this.iconPath = new vscode.ThemeIcon('warning', new vscode.ThemeColor('charts.red'));
            }
            else {
                this.iconPath = new vscode.ThemeIcon('circle-outline', new vscode.ThemeColor('charts.gray'));
            }
        }
        else if (label === 'GODMODE') {
            if (value === 'ENABLED') {
                this.iconPath = new vscode.ThemeIcon('shield', new vscode.ThemeColor('charts.green'));
            }
            else {
                this.iconPath = new vscode.ThemeIcon('shield', new vscode.ThemeColor('charts.gray'));
            }
        }
        else {
            this.iconPath = new vscode.ThemeIcon('info');
        }
    }
}
//# sourceMappingURL=systemStatusProvider.js.map