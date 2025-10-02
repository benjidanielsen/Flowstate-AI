import * as vscode from 'vscode';
import { CommunicationManager } from '../communication/communicationManager';

export class SystemStatusProvider implements vscode.TreeDataProvider<SystemStatusItem> {
    private _onDidChangeTreeData: vscode.EventEmitter<SystemStatusItem | undefined | null | void> = new vscode.EventEmitter<SystemStatusItem | undefined | null | void>();
    readonly onDidChangeTreeData: vscode.Event<SystemStatusItem | undefined | null | void> = this._onDidChangeTreeData.event;
    
    constructor(private communicationManager: CommunicationManager) {
        // Listen for updates from backend
        this.communicationManager.on('system_status_update', () => {
            this.refresh();
        });
        
        // Refresh every 10 seconds
        setInterval(() => this.refresh(), 10000);
    }
    
    refresh(): void {
        this._onDidChangeTreeData.fire();
    }
    
    getTreeItem(element: SystemStatusItem): vscode.TreeItem {
        return element;
    }
    
    async getChildren(element?: SystemStatusItem): Promise<SystemStatusItem[]> {
        if (!element) {
            // Root level - show system metrics
            try {
                const status = await this.communicationManager.getSystemStatus();
                
                return [
                    new SystemStatusItem(
                        'System Status',
                        status.system_status || 'UNKNOWN',
                        vscode.TreeItemCollapsibleState.None
                    ),
                    new SystemStatusItem(
                        'Active Agents',
                        String(status.active_agents || 0),
                        vscode.TreeItemCollapsibleState.None
                    ),
                    new SystemStatusItem(
                        'Total Tasks',
                        String(status.total_tasks || 0),
                        vscode.TreeItemCollapsibleState.None
                    ),
                    new SystemStatusItem(
                        'Queued Tasks',
                        String(status.queued_tasks || 0),
                        vscode.TreeItemCollapsibleState.None
                    ),
                    new SystemStatusItem(
                        'In Progress',
                        String(status.in_progress_tasks || 0),
                        vscode.TreeItemCollapsibleState.None
                    ),
                    new SystemStatusItem(
                        'Completed',
                        String(status.completed_tasks || 0),
                        vscode.TreeItemCollapsibleState.None
                    ),
                    new SystemStatusItem(
                        'Failed',
                        String(status.failed_tasks || 0),
                        vscode.TreeItemCollapsibleState.None
                    ),
                    new SystemStatusItem(
                        'GODMODE',
                        status.godmode_enabled ? 'ENABLED' : 'DISABLED',
                        vscode.TreeItemCollapsibleState.None
                    )
                ];
            } catch (error) {
                return [new SystemStatusItem(
                    'Error',
                    'Failed to load system status',
                    vscode.TreeItemCollapsibleState.None
                )];
            }
        }
        
        return [];
    }
}

class SystemStatusItem extends vscode.TreeItem {
    constructor(
        public readonly label: string,
        public readonly value: string,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState
    ) {
        super(label, collapsibleState);
        
        this.description = value;
        this.tooltip = `${this.label}: ${value}`;
        
        // Set icon based on label
        if (label === 'System Status') {
            if (value === 'ACTIVE') {
                this.iconPath = new vscode.ThemeIcon('check-all', new vscode.ThemeColor('charts.green'));
            } else if (value === 'ERROR') {
                this.iconPath = new vscode.ThemeIcon('warning', new vscode.ThemeColor('charts.red'));
            } else {
                this.iconPath = new vscode.ThemeIcon('circle-outline', new vscode.ThemeColor('charts.gray'));
            }
        } else if (label === 'GODMODE') {
            if (value === 'ENABLED') {
                this.iconPath = new vscode.ThemeIcon('shield', new vscode.ThemeColor('charts.green'));
            } else {
                this.iconPath = new vscode.ThemeIcon('shield', new vscode.ThemeColor('charts.gray'));
            }
        } else {
            this.iconPath = new vscode.ThemeIcon('info');
        }
    }
}
