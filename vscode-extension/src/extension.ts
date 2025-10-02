import * as vscode from 'vscode';
import { CommunicationManager } from './communication/communicationManager';
import { EnvironmentSetupModule } from './automation/environmentSetup';
import { CodeManipulationModule } from './automation/codeManipulation';
import { TerminalAutomationModule } from './automation/terminalAutomation';
import { DashboardProvider } from './ui/dashboardProvider';
import { AgentActivityProvider } from './ui/agentActivityProvider';
import { TaskProgressProvider } from './ui/taskProgressProvider';
import { SystemStatusProvider } from './ui/systemStatusProvider';

let communicationManager: CommunicationManager;
let environmentSetup: EnvironmentSetupModule;
let codeManipulation: CodeManipulationModule;
let terminalAutomation: TerminalAutomationModule;
let dashboardProvider: DashboardProvider;

export function activate(context: vscode.ExtensionContext) {
    console.log('🚀 FlowState-AI GODMODE Extension is now active!');

    // Initialize communication manager
    const config = vscode.workspace.getConfiguration('flowstate-ai');
    const backendUrl = config.get<string>('backendUrl') || 'http://localhost:3001';
    const websocketUrl = config.get<string>('websocketUrl') || 'ws://localhost:3001';
    
    communicationManager = new CommunicationManager(backendUrl, websocketUrl);
    
    // Initialize automation modules
    environmentSetup = new EnvironmentSetupModule(context, communicationManager);
    codeManipulation = new CodeManipulationModule(context, communicationManager);
    terminalAutomation = new TerminalAutomationModule(context, communicationManager);
    
    // Initialize UI providers
    const agentActivityProvider = new AgentActivityProvider(communicationManager);
    const taskProgressProvider = new TaskProgressProvider(communicationManager);
    const systemStatusProvider = new SystemStatusProvider(communicationManager);
    dashboardProvider = new DashboardProvider(context.extensionUri, communicationManager);
    
    // Register tree view providers
    vscode.window.registerTreeDataProvider('flowstate-ai.agentActivity', agentActivityProvider);
    vscode.window.registerTreeDataProvider('flowstate-ai.taskProgress', taskProgressProvider);
    vscode.window.registerTreeDataProvider('flowstate-ai.systemStatus', systemStatusProvider);
    
    // Register commands
    context.subscriptions.push(
        vscode.commands.registerCommand('flowstate-ai.startGodmode', async () => {
            await startGodmode();
        })
    );
    
    context.subscriptions.push(
        vscode.commands.registerCommand('flowstate-ai.stopGodmode', async () => {
            await stopGodmode();
        })
    );
    
    context.subscriptions.push(
        vscode.commands.registerCommand('flowstate-ai.showDashboard', () => {
            dashboardProvider.show();
        })
    );
    
    context.subscriptions.push(
        vscode.commands.registerCommand('flowstate-ai.setupEnvironment', async () => {
            await environmentSetup.setupEnvironment();
        })
    );
    
    context.subscriptions.push(
        vscode.commands.registerCommand('flowstate-ai.fixEverything', async () => {
            const result = await vscode.window.showWarningMessage(
                'This will attempt to automatically fix all detected issues. Continue?',
                'Yes', 'No'
            );
            
            if (result === 'Yes') {
                await fixEverything();
            }
        })
    );
    
    // Auto-setup if enabled
    const autoSetup = config.get<boolean>('autoSetup');
    if (autoSetup && isFlowStateAIProject()) {
        vscode.window.showInformationMessage('FlowState-AI project detected. Starting auto-setup...');
        environmentSetup.setupEnvironment();
    }
    
    // Connect to backend
    communicationManager.connect().then(() => {
        vscode.window.showInformationMessage('✅ Connected to FlowState-AI backend');
    }).catch((error) => {
        vscode.window.showErrorMessage(`❌ Failed to connect to FlowState-AI backend: ${error.message}`);
    });
}

export function deactivate() {
    console.log('🛑 FlowState-AI GODMODE Extension is now deactivated');
    
    if (communicationManager) {
        communicationManager.disconnect();
    }
}

async function startGodmode() {
    try {
        vscode.window.showInformationMessage('🚀 Starting GODMODE...');
        
        // Start the backend services
        await terminalAutomation.executeCommand('python3 ai-gods/project-manager.py', 'GODMODE');
        
        // Show the dashboard
        dashboardProvider.show();
        
        vscode.window.showInformationMessage('✅ GODMODE activated!');
    } catch (error: any) {
        vscode.window.showErrorMessage(`❌ Failed to start GODMODE: ${error.message}`);
    }
}

async function stopGodmode() {
    try {
        vscode.window.showInformationMessage('🛑 Stopping GODMODE...');
        
        // Send stop signal to backend
        await communicationManager.sendCommand('stop_godmode', {});
        
        vscode.window.showInformationMessage('✅ GODMODE stopped');
    } catch (error: any) {
        vscode.window.showErrorMessage(`❌ Failed to stop GODMODE: ${error.message}`);
    }
}

async function fixEverything() {
    try {
        vscode.window.showInformationMessage('🔧 Running auto-fix...');
        
        // Trigger the autonomous development self-healing
        await communicationManager.sendCommand('fix_everything', {});
        
        vscode.window.showInformationMessage('✅ Auto-fix completed!');
    } catch (error: any) {
        vscode.window.showErrorMessage(`❌ Auto-fix failed: ${error.message}`);
    }
}

function isFlowStateAIProject(): boolean {
    const workspaceFolders = vscode.workspace.workspaceFolders;
    if (!workspaceFolders) {
        return false;
    }
    
    // Check for FlowState-AI specific files/folders
    const fs = require('fs');
    const path = require('path');
    const rootPath = workspaceFolders[0].uri.fsPath;
    
    return fs.existsSync(path.join(rootPath, 'ai-gods')) &&
           fs.existsSync(path.join(rootPath, 'GODMODE_AI_AGENT_PLAN.md'));
}
