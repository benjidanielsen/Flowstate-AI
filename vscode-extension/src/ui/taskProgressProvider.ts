import * as vscode from 'vscode';
import { CommunicationManager } from '../communication/communicationManager';

export class TaskProgressProvider implements vscode.TreeDataProvider<TaskProgressItem> {
    private _onDidChangeTreeData: vscode.EventEmitter<TaskProgressItem | undefined | null | void> = new vscode.EventEmitter<TaskProgressItem | undefined | null | void>();
    readonly onDidChangeTreeData: vscode.Event<TaskProgressItem | undefined | null | void> = this._onDidChangeTreeData.event;
    
    constructor(private communicationManager: CommunicationManager) {
        // Listen for updates from backend
        this.communicationManager.on('task_update', () => {
            this.refresh();
        });
        
        // Refresh every 5 seconds
        setInterval(() => this.refresh(), 5000);
    }
    
    refresh(): void {
        this._onDidChangeTreeData.fire();
    }
    
    getTreeItem(element: TaskProgressItem): vscode.TreeItem {
        return element;
    }
    
    async getChildren(element?: TaskProgressItem): Promise<TaskProgressItem[]> {
        if (!element) {
            // Root level - show tasks
            try {
                const tasks = await this.communicationManager.getTasks();
                
                // Group tasks by status
                const grouped: { [key: string]: any[] } = {
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
                
                const items: TaskProgressItem[] = [];
                
                // Add in progress tasks
                if (grouped['IN_PROGRESS'].length > 0) {
                    items.push(new TaskProgressItem(
                        `In Progress (${grouped['IN_PROGRESS'].length})`,
                        'IN_PROGRESS',
                        '',
                        vscode.TreeItemCollapsibleState.Expanded,
                        true
                    ));
                    items.push(...grouped['IN_PROGRESS'].map(task => 
                        new TaskProgressItem(
                            task.name || task.id,
                            task.status,
                            task.assigned_to || 'Unassigned',
                            vscode.TreeItemCollapsibleState.None,
                            false
                        )
                    ));
                }
                
                // Add queued tasks
                if (grouped['QUEUED'].length > 0) {
                    items.push(new TaskProgressItem(
                        `Queued (${grouped['QUEUED'].length})`,
                        'QUEUED',
                        '',
                        vscode.TreeItemCollapsibleState.Collapsed,
                        true
                    ));
                }
                
                // Add completed tasks (limit to 5)
                if (grouped['COMPLETED'].length > 0) {
                    items.push(new TaskProgressItem(
                        `Completed (${grouped['COMPLETED'].length})`,
                        'COMPLETED',
                        '',
                        vscode.TreeItemCollapsibleState.Collapsed,
                        true
                    ));
                }
                
                return items;
            } catch (error) {
                return [new TaskProgressItem(
                    'Error loading tasks',
                    'ERROR',
                    '',
                    vscode.TreeItemCollapsibleState.None,
                    false
                )];
            }
        }
        
        return [];
    }
}

class TaskProgressItem extends vscode.TreeItem {
    constructor(
        public readonly label: string,
        public readonly status: string,
        public readonly assignedTo: string,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState,
        public readonly isGroup: boolean
    ) {
        super(label, collapsibleState);
        
        if (!isGroup) {
            this.tooltip = `${this.label}\nStatus: ${status}\nAssigned to: ${assignedTo}`;
            this.description = assignedTo;
            
            // Set icon based on status
            if (status === 'IN_PROGRESS') {
                this.iconPath = new vscode.ThemeIcon('sync~spin', new vscode.ThemeColor('charts.blue'));
            } else if (status === 'COMPLETED') {
                this.iconPath = new vscode.ThemeIcon('check', new vscode.ThemeColor('charts.green'));
            } else if (status === 'FAILED') {
                this.iconPath = new vscode.ThemeIcon('x', new vscode.ThemeColor('charts.red'));
            } else {
                this.iconPath = new vscode.ThemeIcon('clock', new vscode.ThemeColor('charts.yellow'));
            }
        } else {
            this.iconPath = new vscode.ThemeIcon('folder');
        }
    }
}
