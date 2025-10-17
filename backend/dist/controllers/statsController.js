"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.StatsController = void 0;
const statsService_1 = require("../services/statsService");
class StatsController {
    constructor() {
        this.statsService = new statsService_1.StatsService();
        this.getPipelineStats = async (_req, res) => {
            try {
                const countsByStatus = await this.statsService.countsByStatus();
                const dmoCounters = await this.statsService.dmoCounters();
                const extraCounts = await this.statsService.extraCounts();
                const customerDemographics = await this.statsService.getCustomerDemographics();
                const interactionSummary = await this.statsService.getInteractionSummary();
                const pipelineConversionRates = await this.statsService.getPipelineConversionRates();
                res.json({
                    countsByStatus,
                    dmoCounters,
                    extraCounts,
                    customerDemographics,
                    interactionSummary,
                    pipelineConversionRates,
                });
            }
            catch (err) {
                console.error('Error getting pipeline stats:', err);
                res.status(500).json({ error: 'Internal server error' });
            }
        };
    }
}
exports.StatsController = StatsController;
//# sourceMappingURL=statsController.js.map