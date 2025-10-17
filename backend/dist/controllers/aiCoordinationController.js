"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.getStatus = exports.sendTask = void 0;
const aiCoordinationService_1 = require("../services/aiCoordinationService");
const logger_1 = __importDefault(require("../utils/logger"));
const aiCoordinationService = new aiCoordinationService_1.AICoordinationService();
const sendTask = async (req, res) => {
    try {
        const { taskType, payload } = req.body;
        const result = await aiCoordinationService.sendTaskToAIWorker(taskType, payload);
        res.status(200).json(result);
    }
    catch (error) {
        logger_1.default.error('Error sending task to AI worker:', error);
        res.status(500).json({ message: 'Failed to send task to AI worker', error: error.message });
    }
};
exports.sendTask = sendTask;
const getStatus = async (req, res) => {
    try {
        const status = await aiCoordinationService.getAIWorkerStatus();
        res.status(200).json(status);
    }
    catch (error) {
        logger_1.default.error('Error getting AI worker status:', error);
        res.status(500).json({ message: 'Failed to get AI worker status', error: error.message });
    }
};
exports.getStatus = getStatus;
//# sourceMappingURL=aiCoordinationController.js.map