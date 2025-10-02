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
exports.CodeManipulationModule = void 0;
const vscode = __importStar(require("vscode"));
const path = __importStar(require("path"));
const fs = __importStar(require("fs"));
class CodeManipulationModule {
    constructor(context, communicationManager) {
        this.context = context;
        this.communicationManager = communicationManager;
        // Listen for code manipulation requests from backend
        this.communicationManager.on('code_manipulation', async (data) => {
            await this.handleCodeManipulationRequest(data);
        });
    }
    async handleCodeManipulationRequest(request) {
        try {
            switch (request.action) {
                case 'create':
                    await this.createFile(request.file, request.content || '');
                    break;
                case 'modify':
                    await this.modifyFile(request.file, request.content || '');
                    break;
                case 'delete':
                    await this.deleteFile(request.file);
                    break;
                case 'insert':
                    await this.insertCode(request.file, request.position, request.content || '');
                    break;
                case 'replace':
                    await this.replaceCode(request.file, request.searchText, request.replaceText);
                    break;
            }
            vscode.window.showInformationMessage(`✅ Code manipulation completed: ${request.action} ${request.file}`);
        }
        catch (error) {
            vscode.window.showErrorMessage(`❌ Code manipulation failed: ${error.message}`);
        }
    }
    async createFile(filePath, content) {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (!workspaceFolder) {
            throw new Error('No workspace folder open');
        }
        const fullPath = path.join(workspaceFolder.uri.fsPath, filePath);
        const dirPath = path.dirname(fullPath);
        // Create directory if it doesn't exist
        if (!fs.existsSync(dirPath)) {
            fs.mkdirSync(dirPath, { recursive: true });
        }
        // Write file
        fs.writeFileSync(fullPath, content, 'utf8');
        // Open the file in editor
        const document = await vscode.workspace.openTextDocument(fullPath);
        await vscode.window.showTextDocument(document);
    }
    async modifyFile(filePath, content) {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (!workspaceFolder) {
            throw new Error('No workspace folder open');
        }
        const fullPath = path.join(workspaceFolder.uri.fsPath, filePath);
        if (!fs.existsSync(fullPath)) {
            throw new Error(`File not found: ${filePath}`);
        }
        // Open the file
        const document = await vscode.workspace.openTextDocument(fullPath);
        const editor = await vscode.window.showTextDocument(document);
        // Replace entire content
        const edit = new vscode.WorkspaceEdit();
        const fullRange = new vscode.Range(document.positionAt(0), document.positionAt(document.getText().length));
        edit.replace(document.uri, fullRange, content);
        await vscode.workspace.applyEdit(edit);
        await document.save();
    }
    async deleteFile(filePath) {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (!workspaceFolder) {
            throw new Error('No workspace folder open');
        }
        const fullPath = path.join(workspaceFolder.uri.fsPath, filePath);
        if (fs.existsSync(fullPath)) {
            fs.unlinkSync(fullPath);
        }
    }
    async insertCode(filePath, position, content) {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (!workspaceFolder) {
            throw new Error('No workspace folder open');
        }
        const fullPath = path.join(workspaceFolder.uri.fsPath, filePath);
        if (!fs.existsSync(fullPath)) {
            throw new Error(`File not found: ${filePath}`);
        }
        const document = await vscode.workspace.openTextDocument(fullPath);
        const editor = await vscode.window.showTextDocument(document);
        const edit = new vscode.WorkspaceEdit();
        edit.insert(document.uri, position, content);
        await vscode.workspace.applyEdit(edit);
        await document.save();
    }
    async replaceCode(filePath, searchText, replaceText) {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (!workspaceFolder) {
            throw new Error('No workspace folder open');
        }
        const fullPath = path.join(workspaceFolder.uri.fsPath, filePath);
        if (!fs.existsSync(fullPath)) {
            throw new Error(`File not found: ${filePath}`);
        }
        const document = await vscode.workspace.openTextDocument(fullPath);
        const editor = await vscode.window.showTextDocument(document);
        const text = document.getText();
        const index = text.indexOf(searchText);
        if (index === -1) {
            throw new Error(`Text not found: ${searchText}`);
        }
        const startPos = document.positionAt(index);
        const endPos = document.positionAt(index + searchText.length);
        const range = new vscode.Range(startPos, endPos);
        const edit = new vscode.WorkspaceEdit();
        edit.replace(document.uri, range, replaceText);
        await vscode.workspace.applyEdit(edit);
        await document.save();
    }
    async applyDiagnosticFix(diagnostic, fix) {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            throw new Error('No active editor');
        }
        const document = editor.document;
        const edit = new vscode.WorkspaceEdit();
        edit.replace(document.uri, diagnostic.range, fix);
        await vscode.workspace.applyEdit(edit);
        await document.save();
    }
    async formatDocument(filePath) {
        let document;
        if (filePath) {
            const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
            if (!workspaceFolder) {
                throw new Error('No workspace folder open');
            }
            const fullPath = path.join(workspaceFolder.uri.fsPath, filePath);
            document = await vscode.workspace.openTextDocument(fullPath);
        }
        else {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                throw new Error('No active editor');
            }
            document = editor.document;
        }
        await vscode.commands.executeCommand('editor.action.formatDocument');
        await document.save();
    }
    async refactorCode(filePath, refactoringType, range) {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (!workspaceFolder) {
            throw new Error('No workspace folder open');
        }
        const fullPath = path.join(workspaceFolder.uri.fsPath, filePath);
        const document = await vscode.workspace.openTextDocument(fullPath);
        await vscode.window.showTextDocument(document);
        // Trigger refactoring command based on type
        switch (refactoringType) {
            case 'extract_method':
                await vscode.commands.executeCommand('editor.action.refactor', {
                    kind: 'refactor.extract.function'
                });
                break;
            case 'rename':
                await vscode.commands.executeCommand('editor.action.rename');
                break;
            case 'inline':
                await vscode.commands.executeCommand('editor.action.refactor', {
                    kind: 'refactor.inline'
                });
                break;
        }
    }
}
exports.CodeManipulationModule = CodeManipulationModule;
//# sourceMappingURL=codeManipulation.js.map