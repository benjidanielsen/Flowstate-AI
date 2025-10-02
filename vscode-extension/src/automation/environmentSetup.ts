import * as vscode from 'vscode';
import { CommunicationManager } from '../communication/communicationManager';
import * as path from 'path';
import * as fs from 'fs';

export class EnvironmentSetupModule {
    constructor(
        private context: vscode.ExtensionContext,
        private communicationManager: CommunicationManager
    ) {}
    
    async setupEnvironment(): Promise<void> {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (!workspaceFolder) {
            vscode.window.showErrorMessage('No workspace folder open');
            return;
        }
        
        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: 'Setting up FlowState-AI environment',
            cancellable: false
        }, async (progress) => {
            // Step 1: Install recommended extensions
            progress.report({ increment: 10, message: 'Installing VSCode extensions...' });
            await this.installRecommendedExtensions();
            
            // Step 2: Check and install Node.js dependencies
            progress.report({ increment: 20, message: 'Installing Node.js dependencies...' });
            await this.installNodeDependencies(workspaceFolder.uri.fsPath);
            
            // Step 3: Check and install Python dependencies
            progress.report({ increment: 20, message: 'Installing Python dependencies...' });
            await this.installPythonDependencies(workspaceFolder.uri.fsPath);
            
            // Step 4: Setup database
            progress.report({ increment: 20, message: 'Setting up database...' });
            await this.setupDatabase(workspaceFolder.uri.fsPath);
            
            // Step 5: Configure workspace settings
            progress.report({ increment: 20, message: 'Configuring workspace settings...' });
            await this.configureWorkspace();
            
            // Step 6: Create necessary directories
            progress.report({ increment: 10, message: 'Creating directories...' });
            await this.createDirectories(workspaceFolder.uri.fsPath);
            
            progress.report({ increment: 100, message: 'Setup complete!' });
        });
        
        vscode.window.showInformationMessage('✅ FlowState-AI environment setup complete!');
    }
    
    private async installRecommendedExtensions(): Promise<void> {
        const recommendedExtensions = [
            'ms-python.python',
            'ms-vscode.vscode-typescript-next',
            'dbaeumer.vscode-eslint',
            'esbenp.prettier-vscode',
            'GitHub.copilot'
        ];
        
        for (const extensionId of recommendedExtensions) {
            const extension = vscode.extensions.getExtension(extensionId);
            if (!extension) {
                try {
                    await vscode.commands.executeCommand('workbench.extensions.installExtension', extensionId);
                    console.log(`Installed extension: ${extensionId}`);
                } catch (error) {
                    console.error(`Failed to install extension ${extensionId}:`, error);
                }
            }
        }
    }
    
    private async installNodeDependencies(rootPath: string): Promise<void> {
        const packageJsonPath = path.join(rootPath, 'package.json');
        
        if (fs.existsSync(packageJsonPath)) {
            const terminal = vscode.window.createTerminal('FlowState-AI Setup');
            terminal.show();
            terminal.sendText('npm install');
            
            // Wait for installation to complete
            await this.waitForTerminalCommand(terminal, 60000);
        }
    }
    
    private async installPythonDependencies(rootPath: string): Promise<void> {
        const requirementsPath = path.join(rootPath, 'python-worker', 'requirements.txt');
        
        if (fs.existsSync(requirementsPath)) {
            const terminal = vscode.window.createTerminal('FlowState-AI Setup');
            terminal.show();
            terminal.sendText(`pip3 install -r ${requirementsPath}`);
            
            // Wait for installation to complete
            await this.waitForTerminalCommand(terminal, 60000);
        }
    }
    
    private async setupDatabase(rootPath: string): Promise<void> {
        const terminal = vscode.window.createTerminal('FlowState-AI Setup');
        terminal.show();
        terminal.sendText('npm run migrate');
        
        // Wait for migration to complete
        await this.waitForTerminalCommand(terminal, 30000);
    }
    
    private async configureWorkspace(): Promise<void> {
        const config = vscode.workspace.getConfiguration();
        
        // Configure TypeScript settings
        await config.update('typescript.tsdk', 'node_modules/typescript/lib', vscode.ConfigurationTarget.Workspace);
        
        // Configure Python settings
        await config.update('python.linting.enabled', true, vscode.ConfigurationTarget.Workspace);
        await config.update('python.linting.pylintEnabled', true, vscode.ConfigurationTarget.Workspace);
        await config.update('python.formatting.provider', 'black', vscode.ConfigurationTarget.Workspace);
        
        // Configure editor settings
        await config.update('editor.formatOnSave', true, vscode.ConfigurationTarget.Workspace);
        await config.update('editor.codeActionsOnSave', {
            'source.fixAll.eslint': true
        }, vscode.ConfigurationTarget.Workspace);
    }
    
    private async createDirectories(rootPath: string): Promise<void> {
        const directories = [
            'godmode-logs',
            'godmode-dashboard',
            'godmode-tools',
            'safety-nets',
            'ai-communication',
            'task-queues',
            'progress-tracking'
        ];
        
        for (const dir of directories) {
            const dirPath = path.join(rootPath, dir);
            if (!fs.existsSync(dirPath)) {
                fs.mkdirSync(dirPath, { recursive: true });
                console.log(`Created directory: ${dir}`);
            }
        }
    }
    
    private async waitForTerminalCommand(terminal: vscode.Terminal, timeout: number): Promise<void> {
        return new Promise((resolve) => {
            setTimeout(() => {
                resolve();
            }, timeout);
        });
    }
    
    async checkEnvironment(): Promise<{
        nodeInstalled: boolean;
        pythonInstalled: boolean;
        gitInstalled: boolean;
        dependenciesInstalled: boolean;
    }> {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (!workspaceFolder) {
            return {
                nodeInstalled: false,
                pythonInstalled: false,
                gitInstalled: false,
                dependenciesInstalled: false
            };
        }
        
        const rootPath = workspaceFolder.uri.fsPath;
        
        return {
            nodeInstalled: await this.checkCommand('node --version'),
            pythonInstalled: await this.checkCommand('python3 --version'),
            gitInstalled: await this.checkCommand('git --version'),
            dependenciesInstalled: fs.existsSync(path.join(rootPath, 'node_modules'))
        };
    }
    
    private async checkCommand(command: string): Promise<boolean> {
        try {
            const { exec } = require('child_process');
            return new Promise((resolve) => {
                exec(command, (error: any) => {
                    resolve(!error);
                });
            });
        } catch {
            return false;
        }
    }
}
