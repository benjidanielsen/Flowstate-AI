"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.QualificationController = void 0;
const qualificationService_1 = require("../services/qualificationService");
const logger_1 = __importDefault(require("../utils/logger"));
const qualificationService = new qualificationService_1.QualificationService();
class QualificationController {
    async createQualification(req, res) {
        try {
            const { customer_id, question, expected_answer, status, agent_name } = req.body;
            if (!customer_id || !question || !expected_answer || !status) {
                res.status(400).json({ error: 'customer_id, question, expected_answer, and status are required' });
                return;
            }
            const qualification = await qualificationService.createQualification({
                customer_id,
                question,
                expected_answer,
                status,
                agent_name,
            });
            res.status(201).json(qualification);
        }
        catch (error) {
            logger_1.default.error('Error creating qualification:', error);
            res.status(500).json({ error: 'Failed to create qualification' });
        }
    }
    async getQualificationById(req, res) {
        try {
            const { id } = req.params;
            const qualification = await qualificationService.getQualificationById(id);
            if (!qualification) {
                res.status(404).json({ error: 'Qualification not found' });
                return;
            }
            res.json(qualification);
        }
        catch (error) {
            logger_1.default.error('Error getting qualification by ID:', error);
            res.status(500).json({ error: 'Failed to get qualification' });
        }
    }
    async updateQualificationStatus(req, res) {
        try {
            const { id } = req.params;
            const { status } = req.body;
            if (!status) {
                res.status(400).json({ error: 'status is required' });
                return;
            }
            const updatedQualification = await qualificationService.updateQualificationStatus(id, status);
            if (!updatedQualification) {
                res.status(404).json({ error: 'Qualification not found' });
                return;
            }
            res.json(updatedQualification);
        }
        catch (error) {
            logger_1.default.error('Error updating qualification status:', error);
            res.status(500).json({ error: 'Failed to update qualification status' });
        }
    }
    async recordQualificationAnswer(req, res) {
        try {
            const { qualification_id, answer, is_correct, agent_name } = req.body;
            if (!qualification_id || !answer || typeof is_correct !== 'boolean') {
                res.status(400).json({ error: 'qualification_id, answer, and is_correct are required' });
                return;
            }
            const qualificationAnswer = await qualificationService.recordQualificationAnswer({
                qualification_id,
                answer,
                is_correct,
                agent_name,
            });
            res.status(201).json(qualificationAnswer);
        }
        catch (error) {
            logger_1.default.error('Error recording qualification answer:', error);
            res.status(500).json({ error: 'Failed to record qualification answer' });
        }
    }
    async getAnswersForQualification(req, res) {
        try {
            const { qualificationId } = req.params;
            const answers = await qualificationService.getAnswersForQualification(qualificationId);
            res.json(answers);
        }
        catch (error) {
            logger_1.default.error('Error getting answers for qualification:', error);
            res.status(500).json({ error: 'Failed to get answers for qualification' });
        }
    }
    async getQualificationsByCustomerId(req, res) {
        try {
            const { customerId } = req.params;
            const qualifications = await qualificationService.getQualificationsByCustomerId(customerId);
            res.json(qualifications);
        }
        catch (error) {
            logger_1.default.error('Error getting qualifications by customer ID:', error);
            res.status(500).json({ error: 'Failed to get qualifications by customer ID' });
        }
    }
    async getPendingQualifications(req, res) {
        try {
            const qualifications = await qualificationService.getPendingQualifications();
            res.json(qualifications);
        }
        catch (error) {
            logger_1.default.error('Error getting pending qualifications:', error);
            res.status(500).json({ error: 'Failed to get pending qualifications' });
        }
    }
    async deleteQualification(req, res) {
        try {
            const { id } = req.params;
            const success = await qualificationService.deleteQualification(id);
            if (!success) {
                res.status(404).json({ error: 'Qualification not found' });
                return;
            }
            res.status(204).send(); // No Content
        }
        catch (error) {
            logger_1.default.error('Error deleting qualification:', error);
            res.status(500).json({ error: 'Failed to delete qualification' });
        }
    }
    async deleteQualificationAnswer(req, res) {
        try {
            const { id } = req.params;
            const success = await qualificationService.deleteQualificationAnswer(id);
            if (!success) {
                res.status(404).json({ error: 'Qualification answer not found' });
                return;
            }
            res.status(204).send(); // No Content
        }
        catch (error) {
            logger_1.default.error('Error deleting qualification answer:', error);
            res.status(500).json({ error: 'Failed to delete qualification answer' });
        }
    }
    async getCustomerQualificationSummary(req, res) {
        try {
            const summary = await qualificationService.getCustomerQualificationSummary();
            res.json(summary);
        }
        catch (error) {
            logger_1.default.error('Error getting customer qualification summary:', error);
            res.status(500).json({ error: 'Failed to get customer qualification summary' });
        }
    }
}
exports.QualificationController = QualificationController;
exports.default = new QualificationController();
//# sourceMappingURL=qualificationController.js.map