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
exports.activate = activate;
exports.deactivate = deactivate;
const vscode = __importStar(require("vscode"));
const communicationManager_1 = require("./communication/communicationManager");
const environmentSetup_1 = require("./automation/environmentSetup");
const codeManipulation_1 = require("./automation/codeManipulation");
const terminalAutomation_1 = require("./automation/terminalAutomation");
const dashboardProvider_1 = require("./ui/dashboardProvider");
const agentActivityProvider_1 = require("./ui/agentActivityProvider");
const taskProgressProvider_1 = require("./ui/taskProgressProvider");
const systemStatusProvider_1 = require("./ui/systemStatusProvider");
let communicationManager;
let environmentSetup;
let codeManipulation;
let terminalAutomation;
let dashboardProvider;
function activate(context) {
    console.log('🚀 FlowState-AI GODMODE Extension is now active!');
    // Initialize communication manager
    const config = vscode.workspace.getConfiguration('flowstate-ai');
    const backendUrl = config.get('backendUrl') || 'http://localhost:3001';
    const websocketUrl = config.get('websocketUrl') || 'ws://localhost:3001';
    communicationManager = new communicationManager_1.CommunicationManager(backendUrl, websocketUrl);
    // Initialize automation modules
    environmentSetup = new environmentSetup_1.EnvironmentSetupModule(context, communicationManager);
    codeManipulation = new codeManipulation_1.CodeManipulationModule(context, communicationManager);
    terminalAutomation = new terminalAutomation_1.TerminalAutomationModule(context, communicationManager);
    // Initialize UI providers
    const agentActivityProvider = new agentActivityProvider_1.AgentActivityProvider(communicationManager);
    const taskProgressProvider = new taskProgressProvider_1.TaskProgressProvider(communicationManager);
    const systemStatusProvider = new systemStatusProvider_1.SystemStatusProvider(communicationManager);
    dashboardProvider = new dashboardProvider_1.DashboardProvider(context.extensionUri, communicationManager);
    // Register tree view providers
    vscode.window.registerTreeDataProvider('flowstate-ai.agentActivity', agentActivityProvider);
    vscode.window.registerTreeDataProvider('flowstate-ai.taskProgress', taskProgressProvider);
    vscode.window.registerTreeDataProvider('flowstate-ai.systemStatus', systemStatusProvider);
    // Register commands
    context.subscriptions.push(vscode.commands.registerCommand('flowstate-ai.startGodmode', async () => {
        await startGodmode();
    }));
    context.subscriptions.push(vscode.commands.registerCommand('flowstate-ai.stopGodmode', async () => {
        await stopGodmode();
    }));
    context.subscriptions.push(vscode.commands.registerCommand('flowstate-ai.showDashboard', () => {
        dashboardProvider.show();
    }));
    context.subscriptions.push(vscode.commands.registerCommand('flowstate-ai.setupEnvironment', async () => {
        await environmentSetup.setupEnvironment();
    }));
    context.subscriptions.push(vscode.commands.registerCommand('flowstate-ai.fixEverything', async () => {
        const result = await vscode.window.showWarningMessage('This will attempt to automatically fix all detected issues. Continue?', 'Yes', 'No');
        if (result === 'Yes') {
            await fixEverything();
        }
    }));
    // Auto-setup if enabled
    const autoSetup = config.get('autoSetup');
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
function deactivate() {
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
    }
    catch (error) {
        vscode.window.showErrorMessage(`❌ Failed to start GODMODE: ${error.message}`);
    }
}
async function stopGodmode() {
    try {
        vscode.window.showInformationMessage('🛑 Stopping GODMODE...');
        // Send stop signal to backend
        await communicationManager.sendCommand('stop_godmode', {});
        vscode.window.showInformationMessage('✅ GODMODE stopped');
    }
    catch (error) {
        vscode.window.showErrorMessage(`❌ Failed to stop GODMODE: ${error.message}`);
    }
}
async function fixEverything() {
    try {
        vscode.window.showInformationMessage('🔧 Running auto-fix...');
        // Trigger the autonomous development self-healing
        await communicationManager.sendCommand('fix_everything', {});
        vscode.window.showInformationMessage('✅ Auto-fix completed!');
    }
    catch (error) {
        vscode.window.showErrorMessage(`❌ Auto-fix failed: ${error.message}`);
    }
}
function isFlowStateAIProject() {
    const workspaceFolders = vscode.workspace.workspaceFolders;
    if (!workspaceFolders) {
        return false;
    }
    // Check for FlowState-AI specific files/folders
    const fs = require('fs');
    const path = require('path');
    const rootPath = workspaceFolders[0].uri.fsPath;
    return fs.existsSync(path.join(rootPath, 'ai-gods')) &&
        fs.existsSync(path.join(rootPath, 'docs', 'godmode', 'GODMODE_AI_AGENT_PLAN.md'));
}
//# sourceMappingURL=extension.js.map