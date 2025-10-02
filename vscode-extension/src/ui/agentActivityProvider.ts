import * as vscode from 'vscode';
import { CommunicationManager } from '../communication/communicationManager';

export class AgentActivityProvider implements vscode.TreeDataProvider<AgentActivityItem> {
    private _onDidChangeTreeData: vscode.EventEmitter<AgentActivityItem | undefined | null | void> = new vscode.EventEmitter<AgentActivityItem | undefined | null | void>();
    readonly onDidChangeTreeData: vscode.Event<AgentActivityItem | undefined | null | void> = this._onDidChangeTreeData.event;
    
    constructor(private communicationManager: CommunicationManager) {
        // Listen for updates from backend
        this.communicationManager.on('agent_status_update', () => {
            this.refresh();
        });
        
        // Refresh every 5 seconds
        setInterval(() => this.refresh(), 5000);
    }
    
    refresh(): void {
        this._onDidChangeTreeData.fire();
    }
    
    getTreeItem(element: AgentActivityItem): vscode.TreeItem {
        return element;
    }
    
    async getChildren(element?: AgentActivityItem): Promise<AgentActivityItem[]> {
        if (!element) {
            // Root level - show agents
            try {
                const agents = await this.communicationManager.getAgentStatus();
                return agents.map(agent => new AgentActivityItem(
                    agent.agent_id,
                    agent.status,
                    agent.current_task,
                    agent.progress,
                    vscode.TreeItemCollapsibleState.None
                ));
            } catch (error) {
                return [new AgentActivityItem(
                    'Error loading agents',
                    'ERROR',
                    '',
                    0,
                    vscode.TreeItemCollapsibleState.None
                )];
            }
        }
        
        return [];
    }
}

class AgentActivityItem extends vscode.TreeItem {
    constructor(
        public readonly label: string,
        public readonly status: string,
        public readonly currentTask: string,
        public readonly progress: number,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState
    ) {
        super(label, collapsibleState);
        
        this.tooltip = `${this.label}\nStatus: ${status}\nTask: ${currentTask || 'Idle'}\nProgress: ${progress}%`;
        this.description = `${progress}% - ${currentTask || 'Idle'}`;
        
        // Set icon based on status
        if (status === 'ACTIVE') {
            this.iconPath = new vscode.ThemeIcon('pulse', new vscode.ThemeColor('charts.green'));
        } else if (status === 'ERROR') {
            this.iconPath = new vscode.ThemeIcon('error', new vscode.ThemeColor('charts.red'));
        } else {
            this.iconPath = new vscode.ThemeIcon('circle-outline', new vscode.ThemeColor('charts.gray'));
        }
    }
}
