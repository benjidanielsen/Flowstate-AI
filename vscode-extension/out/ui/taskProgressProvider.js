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
exports.TaskProgressProvider = void 0;
const vscode = __importStar(require("vscode"));
class TaskProgressProvider {
    constructor(communicationManager) {
        this.communicationManager = communicationManager;
        this._onDidChangeTreeData = new vscode.EventEmitter();
        this.onDidChangeTreeData = this._onDidChangeTreeData.event;
        // Listen for updates from backend
        this.communicationManager.on('task_update', () => {
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
            // Root level - show tasks
            try {
                const tasks = await this.communicationManager.getTasks();
                // Group tasks by status
                const grouped = {
                    'IN_PROGRESS': [],
                    'QUEUED': [],
                    'COMPLETED': [],
                    'FAILED': []
                };
                tasks.forEach(task => {
                    const status = task.status || 'QUEUED';
                    if (grouped[status]) {
                        grouped[status].push(task);
                    }
                });
                const items = [];
                // Add in progress tasks
                if (grouped['IN_PROGRESS'].length > 0) {
                    items.push(new TaskProgressItem(`In Progress (${grouped['IN_PROGRESS'].length})`, 'IN_PROGRESS', '', vscode.TreeItemCollapsibleState.Expanded, true));
                    items.push(...grouped['IN_PROGRESS'].map(task => new TaskProgressItem(task.name || task.id, task.status, task.assigned_to || 'Unassigned', vscode.TreeItemCollapsibleState.None, false)));
                }
                // Add queued tasks
                if (grouped['QUEUED'].length > 0) {
                    items.push(new TaskProgressItem(`Queued (${grouped['QUEUED'].length})`, 'QUEUED', '', vscode.TreeItemCollapsibleState.Collapsed, true));
                }
                // Add completed tasks (limit to 5)
                if (grouped['COMPLETED'].length > 0) {
                    items.push(new TaskProgressItem(`Completed (${grouped['COMPLETED'].length})`, 'COMPLETED', '', vscode.TreeItemCollapsibleState.Collapsed, true));
                }
                return items;
            }
            catch (error) {
                return [new TaskProgressItem('Error loading tasks', 'ERROR', '', vscode.TreeItemCollapsibleState.None, false)];
            }
        }
        return [];
    }
}
exports.TaskProgressProvider = TaskProgressProvider;
class TaskProgressItem extends vscode.TreeItem {
    constructor(label, status, assignedTo, collapsibleState, isGroup) {
        super(label, collapsibleState);
        this.label = label;
        this.status = status;
        this.assignedTo = assignedTo;
        this.collapsibleState = collapsibleState;
        this.isGroup = isGroup;
        if (!isGroup) {
            this.tooltip = `${this.label}\nStatus: ${status}\nAssigned to: ${assignedTo}`;
            this.description = assignedTo;
            // Set icon based on status
            if (status === 'IN_PROGRESS') {
                this.iconPath = new vscode.ThemeIcon('sync~spin', new vscode.ThemeColor('charts.blue'));
            }
            else if (status === 'COMPLETED') {
                this.iconPath = new vscode.ThemeIcon('check', new vscode.ThemeColor('charts.green'));
            }
            else if (status === 'FAILED') {
                this.iconPath = new vscode.ThemeIcon('x', new vscode.ThemeColor('charts.red'));
            }
            else {
                this.iconPath = new vscode.ThemeIcon('clock', new vscode.ThemeColor('charts.yellow'));
            }
        }
        else {
            this.iconPath = new vscode.ThemeIcon('folder');
        }
    }
}
//# sourceMappingURL=taskProgressProvider.js.map