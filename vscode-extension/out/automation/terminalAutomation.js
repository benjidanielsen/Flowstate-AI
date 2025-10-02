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
exports.TerminalAutomationModule = void 0;
const vscode = __importStar(require("vscode"));
class TerminalAutomationModule {
    constructor(context, communicationManager) {
        this.context = context;
        this.communicationManager = communicationManager;
        this.terminals = new Map();
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
    async executeCommand(command, terminalName = 'FlowState-AI') {
        const terminal = this.getOrCreateTerminal(terminalName);
        terminal.show();
        terminal.sendText(command);
    }
    async executeCommandWithOutput(command, terminalName = 'FlowState-AI') {
        // Note: VSCode doesn't provide direct terminal output capture
        // This is a workaround using child_process
        const { exec } = require('child_process');
        return new Promise((resolve, reject) => {
            exec(command, { cwd: this.getWorkspacePath() }, (error, stdout, stderr) => {
                if (error) {
                    reject(new Error(stderr || error.message));
                }
                else {
                    resolve(stdout);
                }
            });
        });
    }
    async runNpmScript(scriptName) {
        await this.executeCommand(`npm run ${scriptName}`, 'NPM Scripts');
    }
    async runPythonScript(scriptPath, args = []) {
        const command = `python3 ${scriptPath} ${args.join(' ')}`;
        await this.executeCommand(command, 'Python Scripts');
    }
    async installNpmPackage(packageName, dev = false) {
        const flag = dev ? '--save-dev' : '--save';
        await this.executeCommand(`npm install ${flag} ${packageName}`, 'Package Installation');
    }
    async installPipPackage(packageName) {
        await this.executeCommand(`pip3 install ${packageName}`, 'Package Installation');
    }
    async runTests(testType = 'unit') {
        let command;
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
    async startDevelopmentServer() {
        await this.executeCommand('npm run dev', 'Dev Server');
    }
    async buildProject() {
        await this.executeCommand('npm run build', 'Build');
    }
    async gitCommitAndPush(message) {
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
    async runDatabaseMigrations() {
        await this.executeCommand('npm run migrate', 'Database');
    }
    async startAIAgents() {
        await this.executeCommand('python3 ai-gods/project-manager.py', 'AI Agents');
    }
    async stopAIAgents() {
        // Send interrupt signal
        const terminal = this.terminals.get('AI Agents');
        if (terminal) {
            // VSCode doesn't provide direct way to send Ctrl+C
            // We'll dispose the terminal instead
            terminal.dispose();
            this.terminals.delete('AI Agents');
        }
    }
    getOrCreateTerminal(name) {
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
    getWorkspacePath() {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (!workspaceFolder) {
            throw new Error('No workspace folder open');
        }
        return workspaceFolder.uri.fsPath;
    }
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    dispose() {
        for (const terminal of this.terminals.values()) {
            terminal.dispose();
        }
        this.terminals.clear();
    }
}
exports.TerminalAutomationModule = TerminalAutomationModule;
//# sourceMappingURL=terminalAutomation.js.map