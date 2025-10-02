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
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.CommunicationManager = void 0;
const axios_1 = __importDefault(require("axios"));
const ws_1 = __importDefault(require("ws"));
const vscode = __importStar(require("vscode"));
class CommunicationManager {
    constructor(backendUrl, websocketUrl) {
        this.backendUrl = backendUrl;
        this.websocketUrl = websocketUrl;
        this.ws = null;
        this.messageHandlers = new Map();
        this.reconnectInterval = null;
        this.httpClient = axios_1.default.create({
            baseURL: backendUrl,
            timeout: 30000,
            headers: {
                'Content-Type': 'application/json'
            }
        });
    }
    async connect() {
        return new Promise((resolve, reject) => {
            try {
                this.ws = new ws_1.default(this.websocketUrl);
                this.ws.on('open', () => {
                    console.log('✅ WebSocket connected');
                    this.startHeartbeat();
                    resolve();
                });
                this.ws.on('message', (data) => {
                    try {
                        const message = JSON.parse(data.toString());
                        this.handleMessage(message);
                    }
                    catch (error) {
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
            }
            catch (error) {
                reject(error);
            }
        });
    }
    disconnect() {
        if (this.reconnectInterval) {
            clearInterval(this.reconnectInterval);
            this.reconnectInterval = null;
        }
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
    }
    attemptReconnect() {
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
    startHeartbeat() {
        setInterval(() => {
            if (this.ws && this.ws.readyState === ws_1.default.OPEN) {
                this.ws.send(JSON.stringify({ type: 'heartbeat' }));
            }
        }, 30000);
    }
    handleMessage(message) {
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
    on(messageType, handler) {
        if (!this.messageHandlers.has(messageType)) {
            this.messageHandlers.set(messageType, []);
        }
        this.messageHandlers.get(messageType).push(handler);
    }
    off(messageType, handler) {
        const handlers = this.messageHandlers.get(messageType);
        if (handlers) {
            const index = handlers.indexOf(handler);
            if (index > -1) {
                handlers.splice(index, 1);
            }
        }
    }
    async sendCommand(command, params) {
        try {
            const response = await this.httpClient.post('/api/command', {
                command,
                params
            });
            return response.data;
        }
        catch (error) {
            console.error('Error sending command:', error);
            throw new Error(`Failed to send command: ${error.message}`);
        }
    }
    async getAgentStatus() {
        try {
            const response = await this.httpClient.get('/api/agents/status');
            return response.data;
        }
        catch (error) {
            console.error('Error getting agent status:', error);
            return [];
        }
    }
    async getTasks() {
        try {
            const response = await this.httpClient.get('/api/tasks');
            return response.data;
        }
        catch (error) {
            console.error('Error getting tasks:', error);
            return [];
        }
    }
    async getSystemStatus() {
        try {
            const response = await this.httpClient.get('/api/system/status');
            return response.data;
        }
        catch (error) {
            console.error('Error getting system status:', error);
            return {
                status: 'unknown',
                agents: 0,
                tasks: 0
            };
        }
    }
    async askQuestion(question, topic) {
        try {
            const response = await this.httpClient.post('/api/communication/question', {
                question,
                topic,
                from_agent: 'vscode-extension'
            });
            return response.data.answer || 'No response received';
        }
        catch (error) {
            console.error('Error asking question:', error);
            throw new Error(`Failed to ask question: ${error.message}`);
        }
    }
    async shareKnowledge(topic, content, tags) {
        try {
            await this.httpClient.post('/api/communication/knowledge', {
                topic,
                content,
                tags,
                from_agent: 'vscode-extension'
            });
        }
        catch (error) {
            console.error('Error sharing knowledge:', error);
            throw new Error(`Failed to share knowledge: ${error.message}`);
        }
    }
    async searchKnowledge(query, tags) {
        try {
            const response = await this.httpClient.get('/api/communication/knowledge/search', {
                params: { query, tags: tags?.join(',') }
            });
            return response.data;
        }
        catch (error) {
            console.error('Error searching knowledge:', error);
            return [];
        }
    }
}
exports.CommunicationManager = CommunicationManager;
//# sourceMappingURL=communicationManager.js.map