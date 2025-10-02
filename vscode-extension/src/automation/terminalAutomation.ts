import * as vscode from 'vscode';
import { CommunicationManager } from '../communication/communicationManager';

export class TerminalAutomationModule {
    private terminals: Map<string, vscode.Terminal> = new Map();
    
    constructor(
        private context: vscode.ExtensionContext,
        private communicationManager: CommunicationManager
    ) {
        // Listen for terminal commands from backend
        this.communicationManager.on('terminal_command', async (data) => {
            await this.executeCommand(data.command, data.terminalName);
        });
        
        // Clean up terminals on disposal
        vscode.window.onDidCloseTerminal(terminal => {
            for (const [name, term] of this.terminals.entries()) {
                if (term === terminal) {
                    this.terminals.delete(name);
                    break;
                }
            }
        });
    }
    
    async executeCommand(command: string, terminalName: string = 'FlowState-AI'): Promise<void> {
        const terminal = this.getOrCreateTerminal(terminalName);
        terminal.show();
        terminal.sendText(command);
    }
    
    async executeCommandWithOutput(command: string, terminalName: string = 'FlowState-AI'): Promise<string> {
        // Note: VSCode doesn't provide direct terminal output capture
        // This is a workaround using child_process
        const { exec } = require('child_process');
        
        return new Promise((resolve, reject) => {
            exec(command, { cwd: this.getWorkspacePath() }, (error: any, stdout: string, stderr: string) => {
                if (error) {
                    reject(new Error(stderr || error.message));
                } else {
                    resolve(stdout);
                }
            });
        });
    }
    
    async runNpmScript(scriptName: string): Promise<void> {
        await this.executeCommand(`npm run ${scriptName}`, 'NPM Scripts');
    }
    
    async runPythonScript(scriptPath: string, args: string[] = []): Promise<void> {
        const command = `python3 ${scriptPath} ${args.join(' ')}`;
        await this.executeCommand(command, 'Python Scripts');
    }
    
    async installNpmPackage(packageName: string, dev: boolean = false): Promise<void> {
        const flag = dev ? '--save-dev' : '--save';
        await this.executeCommand(`npm install ${flag} ${packageName}`, 'Package Installation');
    }
    
    async installPipPackage(packageName: string): Promise<void> {
        await this.executeCommand(`pip3 install ${packageName}`, 'Package Installation');
    }
    
    async runTests(testType: 'unit' | 'integration' | 'e2e' = 'unit'): Promise<void> {
        let command: string;
        
        switch (testType) {
            case 'unit':
                command = 'npm test';
                break;
            case 'integration':
                command = 'npm run test:integration';
                break;
            case 'e2e':
                command = 'npm run test:e2e';
                break;
        }
        
        await this.executeCommand(command, 'Tests');
    }
    
    async startDevelopmentServer(): Promise<void> {
        await this.executeCommand('npm run dev', 'Dev Server');
    }
    
    async buildProject(): Promise<void> {
        await this.executeCommand('npm run build', 'Build');
    }
    
    async gitCommitAndPush(message: string): Promise<void> {
        const terminal = this.getOrCreateTerminal('Git');
        terminal.show();
        terminal.sendText('git add .');
        
        // Wait a bit for add to complete
        await this.sleep(1000);
        
        terminal.sendText(`git commit -m "${message}"`);
        
        // Wait for commit
        await this.sleep(2000);
        
        terminal.sendText('git push');
    }
    
    async runDatabaseMigrations(): Promise<void> {
        await this.executeCommand('npm run migrate', 'Database');
    }
    
    async startAIAgents(): Promise<void> {
        await this.executeCommand('python3 ai-gods/project-manager.py', 'AI Agents');
    }
    
    async stopAIAgents(): Promise<void> {
        // Send interrupt signal
        const terminal = this.terminals.get('AI Agents');
        if (terminal) {
            // VSCode doesn't provide direct way to send Ctrl+C
            // We'll dispose the terminal instead
            terminal.dispose();
            this.terminals.delete('AI Agents');
        }
    }
    
    private getOrCreateTerminal(name: string): vscode.Terminal {
        let terminal = this.terminals.get(name);
        
        if (!terminal || terminal.exitStatus !== undefined) {
            terminal = vscode.window.createTerminal({
                name,
                cwd: this.getWorkspacePath()
            });
            this.terminals.set(name, terminal);
        }
        
        return terminal;
    }
    
    private getWorkspacePath(): string {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (!workspaceFolder) {
            throw new Error('No workspace folder open');
        }
        return workspaceFolder.uri.fsPath;
    }
    
    private sleep(ms: number): Promise<void> {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    
    dispose(): void {
        for (const terminal of this.terminals.values()) {
            terminal.dispose();
        }
        this.terminals.clear();
    }
}
