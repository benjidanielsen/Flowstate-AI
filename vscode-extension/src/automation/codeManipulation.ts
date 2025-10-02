import * as vscode from 'vscode';
import { CommunicationManager } from '../communication/communicationManager';
import * as path from 'path';
import * as fs from 'fs';

export interface CodeEdit {
    file: string;
    action: 'create' | 'modify' | 'delete' | 'insert' | 'replace';
    content?: string;
    position?: vscode.Position;
    range?: vscode.Range;
    searchText?: string;
    replaceText?: string;
}

export class CodeManipulationModule {
    constructor(
        private context: vscode.ExtensionContext,
        private communicationManager: CommunicationManager
    ) {
        // Listen for code manipulation requests from backend
        this.communicationManager.on('code_manipulation', async (data) => {
            await this.handleCodeManipulationRequest(data);
        });
    }
    
    async handleCodeManipulationRequest(request: CodeEdit): Promise<void> {
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
                    await this.insertCode(request.file, request.position!, request.content || '');
                    break;
                case 'replace':
                    await this.replaceCode(request.file, request.searchText!, request.replaceText!);
                    break;
            }
            
            vscode.window.showInformationMessage(`✅ Code manipulation completed: ${request.action} ${request.file}`);
        } catch (error: any) {
            vscode.window.showErrorMessage(`❌ Code manipulation failed: ${error.message}`);
        }
    }
    
    async createFile(filePath: string, content: string): Promise<void> {
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
    
    async modifyFile(filePath: string, content: string): Promise<void> {
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
        const fullRange = new vscode.Range(
            document.positionAt(0),
            document.positionAt(document.getText().length)
        );
        edit.replace(document.uri, fullRange, content);
        
        await vscode.workspace.applyEdit(edit);
        await document.save();
    }
    
    async deleteFile(filePath: string): Promise<void> {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (!workspaceFolder) {
            throw new Error('No workspace folder open');
        }
        
        const fullPath = path.join(workspaceFolder.uri.fsPath, filePath);
        
        if (fs.existsSync(fullPath)) {
            fs.unlinkSync(fullPath);
        }
    }
    
    async insertCode(filePath: string, position: vscode.Position, content: string): Promise<void> {
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
    
    async replaceCode(filePath: string, searchText: string, replaceText: string): Promise<void> {
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
    
    async applyDiagnosticFix(diagnostic: vscode.Diagnostic, fix: string): Promise<void> {
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
    
    async formatDocument(filePath?: string): Promise<void> {
        let document: vscode.TextDocument;
        
        if (filePath) {
            const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
            if (!workspaceFolder) {
                throw new Error('No workspace folder open');
            }
            
            const fullPath = path.join(workspaceFolder.uri.fsPath, filePath);
            document = await vscode.workspace.openTextDocument(fullPath);
        } else {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                throw new Error('No active editor');
            }
            document = editor.document;
        }
        
        await vscode.commands.executeCommand('editor.action.formatDocument');
        await document.save();
    }
    
    async refactorCode(filePath: string, refactoringType: string, range: vscode.Range): Promise<void> {
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
