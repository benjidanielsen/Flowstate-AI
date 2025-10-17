"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.AICoordinationService = void 0;
const logger_1 = __importDefault(require("../utils/logger"));
const axios_1 = __importDefault(require("axios"));
class AICoordinationService {
    constructor() {
        this.pythonWorkerUrl = process.env.PYTHON_WORKER_URL || 'http://localhost:8000'; // Default to local FastAPI
    }
    async sendTaskToAIWorker(taskType, payload) {
        logger_1.default.info(`Sending task '${taskType}' to AI worker`, { payload });
        try {
            const response = await axios_1.default.post(`${this.pythonWorkerUrl}/ai-task/${taskType}`, payload);
            logger_1.default.info(`AI worker responded to task '${taskType}'`, { responseData: response.data });
            return response.data;
        }
        catch (error) {
            logger_1.default.error(`Error sending task '${taskType}' to AI worker: ${error.message}`, { error });
            throw new Error(`Failed to communicate with AI worker: ${error.message}`);
        }
    }
    async getAIWorkerStatus() {
        logger_1.default.info('Checking AI worker status');
        try {
            const response = await axios_1.default.get(`${this.pythonWorkerUrl}/health`);
            logger_1.default.info('AI worker status check successful', { status: response.data.status });
            return response.data;
        }
        catch (error) {
            logger_1.default.error(`Error checking AI worker status: ${error.message}`, { error });
            throw new Error(`Failed to get AI worker status: ${error.message}`);
        }
    }
}
exports.AICoordinationService = AICoordinationService;
//# sourceMappingURL=aiCoordinationService.js.map