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
exports.EnvironmentSetupModule = void 0;
const vscode = __importStar(require("vscode"));
const path = __importStar(require("path"));
const fs = __importStar(require("fs"));
class EnvironmentSetupModule {
    constructor(context, communicationManager) {
        this.context = context;
        this.communicationManager = communicationManager;
    }
    async setupEnvironment() {
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
    async installRecommendedExtensions() {
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
                }
                catch (error) {
                    console.error(`Failed to install extension ${extensionId}:`, error);
                }
            }
        }
    }
    async installNodeDependencies(rootPath) {
        const packageJsonPath = path.join(rootPath, 'package.json');
        if (fs.existsSync(packageJsonPath)) {
            const terminal = vscode.window.createTerminal('FlowState-AI Setup');
            terminal.show();
            terminal.sendText('npm install');
            // Wait for installation to complete
            await this.waitForTerminalCommand(terminal, 60000);
        }
    }
    async installPythonDependencies(rootPath) {
        const requirementsPath = path.join(rootPath, 'python-worker', 'requirements.txt');
        if (fs.existsSync(requirementsPath)) {
            const terminal = vscode.window.createTerminal('FlowState-AI Setup');
            terminal.show();
            terminal.sendText(`pip3 install -r ${requirementsPath}`);
            // Wait for installation to complete
            await this.waitForTerminalCommand(terminal, 60000);
        }
    }
    async setupDatabase(rootPath) {
        const terminal = vscode.window.createTerminal('FlowState-AI Setup');
        terminal.show();
        terminal.sendText('npm run migrate');
        // Wait for migration to complete
        await this.waitForTerminalCommand(terminal, 30000);
    }
    async configureWorkspace() {
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
    async createDirectories(rootPath) {
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
    async waitForTerminalCommand(terminal, timeout) {
        return new Promise((resolve) => {
            setTimeout(() => {
                resolve();
            }, timeout);
        });
    }
    async checkEnvironment() {
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
    async checkCommand(command) {
        try {
            const { exec } = require('child_process');
            return new Promise((resolve) => {
                exec(command, (error) => {
                    resolve(!error);
                });
            });
        }
        catch {
            return false;
        }
    }
}
exports.EnvironmentSetupModule = EnvironmentSetupModule;
//# sourceMappingURL=environmentSetup.js.map