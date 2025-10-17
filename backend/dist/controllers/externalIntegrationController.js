"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.deleteIntegration = exports.updateIntegration = exports.getIntegrationsByCustomer = exports.createIntegration = void 0;
const externalIntegrationService_1 = require("../services/externalIntegrationService");
const logger_1 = __importDefault(require("../utils/logger"));
const externalIntegrationService = new externalIntegrationService_1.ExternalIntegrationService();
const createIntegration = async (req, res) => {
    try {
        const { customer_id, type, config } = req.body;
        const newIntegration = await externalIntegrationService.createIntegration({ customer_id, type, config });
        res.status(201).json(newIntegration);
    }
    catch (error) {
        logger_1.default.error('Error creating external integration:', error);
        res.status(500).json({ message: 'Failed to create integration' });
    }
};
exports.createIntegration = createIntegration;
const getIntegrationsByCustomer = async (req, res) => {
    try {
        const { customerId } = req.params;
        const integrations = await externalIntegrationService.getIntegrationsByCustomer(customerId);
        res.status(200).json(integrations);
    }
    catch (error) {
        logger_1.default.error('Error fetching external integrations:', error);
        res.status(500).json({ message: 'Failed to fetch integrations' });
    }
};
exports.getIntegrationsByCustomer = getIntegrationsByCustomer;
const updateIntegration = async (req, res) => {
    try {
        const { id } = req.params;
        const updates = req.body;
        const updatedIntegration = await externalIntegrationService.updateIntegration(id, updates);
        res.status(200).json(updatedIntegration);
    }
    catch (error) {
        logger_1.default.error('Error updating external integration:', error);
        res.status(500).json({ message: 'Failed to update integration' });
    }
};
exports.updateIntegration = updateIntegration;
const deleteIntegration = async (req, res) => {
    try {
        const { id } = req.params;
        await externalIntegrationService.deleteIntegration(id);
        res.status(204).send();
    }
    catch (error) {
        logger_1.default.error('Error deleting external integration:', error);
        res.status(500).json({ message: 'Failed to delete integration' });
    }
};
exports.deleteIntegration = deleteIntegration;
//# sourceMappingURL=externalIntegrationController.js.map