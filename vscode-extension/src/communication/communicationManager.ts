import axios, { AxiosInstance } from 'axios';
import WebSocket from 'ws';
import * as vscode from 'vscode';

export interface Message {
    type: string;
    data: any;
    timestamp: string;
}

export interface AgentStatus {
    agent_id: string;
    status: string;
    current_task: string;
    progress: number;
}

export class CommunicationManager {
    private httpClient: AxiosInstance;
    private ws: WebSocket | null = null;
    private messageHandlers: Map<string, ((data: any) => void)[]> = new Map();
    private reconnectInterval: NodeJS.Timeout | null = null;
    
    constructor(
        private backendUrl: string,
        private websocketUrl: string
    ) {
        this.httpClient = axios.create({
            baseURL: backendUrl,
            timeout: 30000,
            headers: {
                'Content-Type': 'application/json'
            }
        });
    }
    
    async connect(): Promise<void> {
        return new Promise((resolve, reject) => {
            try {
                this.ws = new WebSocket(this.websocketUrl);
                
                this.ws.on('open', () => {
                    console.log('✅ WebSocket connected');
                    this.startHeartbeat();
                    resolve();
                });
                
                this.ws.on('message', (data: WebSocket.Data) => {
                    try {
                        const message: Message = JSON.parse(data.toString());
                        this.handleMessage(message);
                    } catch (error) {
                        console.error('Error parsing WebSocket message:', error);
                    }
                });
                
                this.ws.on('error', (error) => {
                    console.error('WebSocket error:', error);
                    reject(error);
                });
                
                this.ws.on('close', () => {
                    console.log('WebSocket disconnected');
                    this.attemptReconnect();
                });
            } catch (error) {
                reject(error);
            }
        });
    }
    
    disconnect(): void {
        if (this.reconnectInterval) {
            clearInterval(this.reconnectInterval);
            this.reconnectInterval = null;
        }
        
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
    }
    
    private attemptReconnect(): void {
        if (this.reconnectInterval) {
            return;
        }
        
        this.reconnectInterval = setInterval(() => {
            console.log('Attempting to reconnect...');
            this.connect().then(() => {
                if (this.reconnectInterval) {
                    clearInterval(this.reconnectInterval);
                    this.reconnectInterval = null;
                }
                vscode.window.showInformationMessage('✅ Reconnected to FlowState-AI backend');
            }).catch(() => {
                // Continue trying
            });
        }, 5000);
    }
    
    private startHeartbeat(): void {
        setInterval(() => {
            if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                this.ws.send(JSON.stringify({ type: 'heartbeat' }));
            }
        }, 30000);
    }
    
    private handleMessage(message: Message): void {
        const handlers = this.messageHandlers.get(message.type);
        if (handlers) {
            handlers.forEach(handler => handler(message.data));
        }
        
        // Handle all messages
        const allHandlers = this.messageHandlers.get('*');
        if (allHandlers) {
            allHandlers.forEach(handler => handler(message));
        }
    }
    
    on(messageType: string, handler: (data: any) => void): void {
        if (!this.messageHandlers.has(messageType)) {
            this.messageHandlers.set(messageType, []);
        }
        this.messageHandlers.get(messageType)!.push(handler);
    }
    
    off(messageType: string, handler: (data: any) => void): void {
        const handlers = this.messageHandlers.get(messageType);
        if (handlers) {
            const index = handlers.indexOf(handler);
            if (index > -1) {
                handlers.splice(index, 1);
            }
        }
    }
    
    async sendCommand(command: string, params: any): Promise<any> {
        try {
            const response = await this.httpClient.post('/api/command', {
                command,
                params
            });
            return response.data;
        } catch (error: any) {
            console.error('Error sending command:', error);
            throw new Error(`Failed to send command: ${error.message}`);
        }
    }
    
    async getAgentStatus(): Promise<AgentStatus[]> {
        try {
            const response = await this.httpClient.get('/api/agents/status');
            return response.data;
        } catch (error: any) {
            console.error('Error getting agent status:', error);
            return [];
        }
    }
    
    async getTasks(): Promise<any[]> {
        try {
            const response = await this.httpClient.get('/api/tasks');
            return response.data;
        } catch (error: any) {
            console.error('Error getting tasks:', error);
            return [];
        }
    }
    
    async getSystemStatus(): Promise<any> {
        try {
            const response = await this.httpClient.get('/api/system/status');
            return response.data;
        } catch (error: any) {
            console.error('Error getting system status:', error);
            return {
                status: 'unknown',
                agents: 0,
                tasks: 0
            };
        }
    }
    
    async askQuestion(question: string, topic?: string): Promise<string> {
        try {
            const response = await this.httpClient.post('/api/communication/question', {
                question,
                topic,
                from_agent: 'vscode-extension'
            });
            return response.data.answer || 'No response received';
        } catch (error: any) {
            console.error('Error asking question:', error);
            throw new Error(`Failed to ask question: ${error.message}`);
        }
    }
    
    async shareKnowledge(topic: string, content: string, tags: string[]): Promise<void> {
        try {
            await this.httpClient.post('/api/communication/knowledge', {
                topic,
                content,
                tags,
                from_agent: 'vscode-extension'
            });
        } catch (error: any) {
            console.error('Error sharing knowledge:', error);
            throw new Error(`Failed to share knowledge: ${error.message}`);
        }
    }
    
    async searchKnowledge(query: string, tags?: string[]): Promise<any[]> {
        try {
            const response = await this.httpClient.get('/api/communication/knowledge/search', {
                params: { query, tags: tags?.join(',') }
            });
            return response.data;
        } catch (error: any) {
            console.error('Error searching knowledge:', error);
            return [];
        }
    }
}
