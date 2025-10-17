"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.QualificationController = void 0;
const database_1 = __importDefault(require("../database"));
const dbManager = database_1.default.getInstance();
class QualificationController {
    constructor() {
        this.saveQualification = async (req, res) => {
            const { customer_id, prospect_why, qualification_data } = req.body;
            if (!customer_id) {
                return res.status(400).json({ error: 'customer_id is required' });
            }
            try {
                const db = dbManager.getDb();
                await new Promise((resolve, reject) => {
                    db.run('UPDATE customers SET prospect_why = ?, qualification_data = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?', [prospect_why || '', JSON.stringify(qualification_data || {}), customer_id], (err) => {
                        if (err)
                            reject(err);
                        else
                            resolve(null);
                    });
                });
                res.json({ success: true, message: 'Qualification saved successfully' });
            }
            catch (error) {
                console.error('Error saving qualification:', error);
                res.status(500).json({ error: 'Failed to save qualification' });
            }
        };
        this.getQualification = async (req, res) => {
            const { id } = req.params;
            try {
                const db = dbManager.getDb();
                const customer = await new Promise((resolve, reject) => {
                    db.get('SELECT id, name, prospect_why, qualification_data FROM customers WHERE id = ?', [id], (err, row) => {
                        if (err)
                            reject(err);
                        else
                            resolve(row);
                    });
                });
                if (!customer) {
                    return res.status(404).json({ error: 'Customer not found' });
                }
                // Parse qualification_data if it's a string
                if (customer.qualification_data && typeof customer.qualification_data === 'string') {
                    try {
                        customer.qualification_data = JSON.parse(customer.qualification_data);
                    }
                    catch (e) {
                        customer.qualification_data = {};
                    }
                }
                res.json(customer);
            }
            catch (error) {
                console.error('Error getting qualification:', error);
                res.status(500).json({ error: 'Failed to get qualification' });
            }
        };
    }
}
exports.QualificationController = QualificationController;
//# sourceMappingURL=qualificationController.js.map