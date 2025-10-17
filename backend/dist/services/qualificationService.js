"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.QualificationService = void 0;
const database_1 = __importDefault(require("../database"));
const eventLogService_1 = require("./eventLogService");
class QualificationService {
    constructor() {
        this.requiredFields = ['prospect_why', 'desired_outcome', 'timeline', 'decision_maker'];
        this.eventLogService = new eventLogService_1.EventLogService();
    }
    /**
     * Save qualification data for a customer
     */
    async saveQualification(customerId, qualificationData) {
        const db = database_1.default.getInstance().getDb();
        return new Promise((resolve, reject) => {
            db.run(`UPDATE customers 
         SET prospect_why = ?, qualification_data = ?, updated_at = CURRENT_TIMESTAMP 
         WHERE id = ?`, [
                qualificationData.prospect_why || '',
                JSON.stringify(qualificationData),
                customerId
            ], (err) => {
                if (err) {
                    reject(err);
                }
                else {
                    // Log qualification event
                    this.eventLogService.logEvent('qualification_updated', {
                        customer_id: customerId,
                        fields_updated: Object.keys(qualificationData)
                    }, customerId);
                    resolve();
                }
            });
        });
    }
    /**
     * Get qualification data for a customer
     */
    async getQualification(customerId) {
        const db = database_1.default.getInstance().getDb();
        return new Promise((resolve, reject) => {
            db.get('SELECT prospect_why, qualification_data FROM customers WHERE id = ?', [customerId], (err, row) => {
                if (err) {
                    reject(err);
                }
                else if (!row) {
                    resolve(null);
                }
                else {
                    let qualificationData = {};
                    if (row.qualification_data) {
                        try {
                            qualificationData = JSON.parse(row.qualification_data);
                        }
                        catch (e) {
                            console.error('Error parsing qualification_data:', e);
                        }
                    }
                    // Ensure prospect_why is included
                    if (row.prospect_why) {
                        qualificationData.prospect_why = row.prospect_why;
                    }
                    resolve(qualificationData);
                }
            });
        });
    }
    /**
     * Check if a customer is qualified based on Frazer Method requirements
     */
    async checkQualification(customerId) {
        const qualificationData = await this.getQualification(customerId);
        if (!qualificationData) {
            return {
                is_qualified: false,
                qualification_score: 0,
                missing_fields: this.requiredFields,
                qualification_data: {}
            };
        }
        const missingFields = [];
        let filledFields = 0;
        // Check required fields
        for (const field of this.requiredFields) {
            const value = qualificationData[field];
            if (!value || (typeof value === 'string' && value.trim() === '')) {
                missingFields.push(field);
            }
            else {
                filledFields++;
            }
        }
        const qualificationScore = Math.round((filledFields / this.requiredFields.length) * 100);
        const isQualified = missingFields.length === 0;
        return {
            is_qualified: isQualified,
            qualification_score: qualificationScore,
            missing_fields: missingFields,
            qualification_data: qualificationData
        };
    }
    /**
     * Validate if a customer can move to a specific pipeline stage
     */
    async canMoveToStage(customerId, targetStage) {
        // Stages that require qualification
        const qualificationRequiredStages = ['qualified', 'presentation_sent', 'follow_up', 'closed_won'];
        if (!qualificationRequiredStages.includes(targetStage)) {
            return { allowed: true };
        }
        const qualificationResult = await this.checkQualification(customerId);
        if (!qualificationResult.is_qualified) {
            return {
                allowed: false,
                reason: `Customer must be qualified before moving to ${targetStage}. Missing fields: ${qualificationResult.missing_fields.join(', ')}`
            };
        }
        return { allowed: true };
    }
    /**
     * Get qualification statistics for all customers
     */
    async getQualificationStats() {
        const db = database_1.default.getInstance().getDb();
        return new Promise((resolve, reject) => {
            db.all('SELECT id FROM customers', async (err, rows) => {
                if (err) {
                    reject(err);
                }
                else {
                    const totalCustomers = rows.length;
                    let qualifiedCount = 0;
                    let totalScore = 0;
                    for (const row of rows) {
                        const result = await this.checkQualification(row.id);
                        if (result.is_qualified) {
                            qualifiedCount++;
                        }
                        totalScore += result.qualification_score;
                    }
                    const averageScore = totalCustomers > 0 ? Math.round(totalScore / totalCustomers) : 0;
                    const qualificationRate = totalCustomers > 0 ? Math.round((qualifiedCount / totalCustomers) * 100) : 0;
                    resolve({
                        total_customers: totalCustomers,
                        qualified_customers: qualifiedCount,
                        average_qualification_score: averageScore,
                        qualification_rate: qualificationRate
                    });
                }
            });
        });
    }
}
exports.QualificationService = QualificationService;
//# sourceMappingURL=qualificationService.js.map