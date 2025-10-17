"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.CustomerController = void 0;
const customerService_1 = require("../services/customerService");
const types_1 = require("../types");
const joi_1 = __importDefault(require("joi"));
const statsService_1 = require("../services/statsService");
const SOURCE_ENUM = ['ig', 'messenger', 'whatsapp', 'web', 'ads', 'manual', 'other'];
const customerCreateSchema = joi_1.default.object({
    name: joi_1.default.string().min(1).required(),
    email: joi_1.default.string().email().optional(),
    phone: joi_1.default.string().optional(),
    status: joi_1.default.string().valid(...Object.values(types_1.PipelineStatus)).optional(),
    notes: joi_1.default.string().optional(),
    next_action: joi_1.default.string().optional(),
    next_action_date: joi_1.default.date().iso().optional(),
    source: joi_1.default.string().valid(...SOURCE_ENUM).optional(),
    prospect_why: joi_1.default.string().optional(), // Frazer Method: Required for Qualified stage
    handle_ig: joi_1.default.string().optional(),
    handle_whatsapp: joi_1.default.string().optional(),
    country: joi_1.default.string().optional(),
    language: joi_1.default.string().optional(),
    utm_json: joi_1.default.object({
        source: joi_1.default.string().optional(),
        medium: joi_1.default.string().optional(),
        campaign: joi_1.default.string().optional(),
        content: joi_1.default.string().optional(),
        term: joi_1.default.string().optional(),
    }).unknown(false).optional(),
    consent_json: joi_1.default.object().optional(),
});
const customerUpdateSchema = customerCreateSchema.fork(['name'], (s) => s.optional());
class CustomerController {
    constructor() {
        this.getAllCustomers = async (req, res) => {
            try {
                const { status, search, source, country, language, next_action, sortBy, sortOrder } = req.query;
                const customers = await this.customerService.getAllCustomers({
                    status: status,
                    search: search,
                    source: source,
                    country: country,
                    language: language,
                    next_action: next_action,
                    sortBy: sortBy,
                    sortOrder: sortOrder,
                });
                res.json(customers);
            }
            catch (error) {
                console.error("Error fetching customers:", error);
                res.status(500).json({ error: "Internal server error" });
            }
        };
        this.getCustomerById = async (req, res) => {
            try {
                const { id } = req.params;
                const customer = await this.customerService.getCustomerById(id);
                if (!customer) {
                    return res.status(404).json({ error: 'Customer not found' });
                }
                res.json(customer);
            }
            catch (error) {
                console.error('Error fetching customer:', error);
                res.status(500).json({ error: 'Internal server error' });
            }
        };
        this.createCustomer = async (req, res) => {
            try {
                const { error, value } = customerCreateSchema.validate(req.body, { abortEarly: false });
                if (error) {
                    return res.status(400).json({ error: 'Invalid payload', details: error.details });
                }
                const customer = await this.customerService.createCustomer(value);
                res.status(201).json(customer);
            }
            catch (error) {
                console.error('Error creating customer:', error);
                res.status(500).json({ error: 'Internal server error' });
            }
        };
        this.updateCustomer = async (req, res) => {
            try {
                const { id } = req.params;
                const { error, value } = customerUpdateSchema.validate(req.body, { abortEarly: false });
                if (error) {
                    return res.status(400).json({ error: 'Invalid payload', details: error.details });
                }
                // Frazer Method: Enforce prospect_why requirement for Qualified stage
                if (value.status === types_1.PipelineStatus.QUALIFIED && !value.prospect_why) {
                    return res.status(400).json({
                        error: 'Prospect WHY is required to move to Qualified stage',
                        frazer_rule: 'Cannot qualify prospect without understanding their core motivation'
                    });
                }
                const customer = await this.customerService.updateCustomer(id, value);
                if (!customer) {
                    return res.status(404).json({ error: 'Customer not found' });
                }
                res.json(customer);
            }
            catch (error) {
                console.error('Error updating customer:', error);
                res.status(500).json({ error: 'Internal server error' });
            }
        };
        this.deleteCustomer = async (req, res) => {
            try {
                const { id } = req.params;
                const deleted = await this.customerService.deleteCustomer(id);
                if (!deleted) {
                    return res.status(404).json({ error: 'Customer not found' });
                }
                res.status(204).send();
            }
            catch (error) {
                console.error('Error deleting customer:', error);
                res.status(500).json({ error: 'Internal server error' });
            }
        };
        this.moveToNextStage = async (req, res) => {
            try {
                const { id } = req.params;
                const customer = await this.customerService.moveCustomerToNextStage(id);
                if (!customer) {
                    return res.status(404).json({ error: 'Customer not found' });
                }
                res.json(customer);
            }
            catch (error) {
                console.error('Error moving customer to next stage:', error);
                res.status(500).json({ error: 'Internal server error' });
            }
        };
        this.getPipelineStats = async (req, res) => {
            try {
                const counts_by_status = await this.statsService.countsByStatus();
                const dmo = await this.statsService.dmoCounters();
                const extras = await this.statsService.extraCounts();
                res.json({ counts_by_status, dmo_today: dmo.today, dmo_week: dmo.week, ...extras });
            }
            catch (error) {
                console.error('Error fetching pipeline stats:', error);
                res.status(500).json({ error: 'Internal server error' });
            }
        };
        this.customerService = new customerService_1.CustomerService();
        this.statsService = new statsService_1.StatsService();
    }
}
exports.CustomerController = CustomerController;
//# sourceMappingURL=customerController.js.map