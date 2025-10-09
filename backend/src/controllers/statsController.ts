import { Request, Response } from 'express';
import { StatsService } from '../services/statsService';

export class StatsController {
  private statsService = new StatsService();

  getPipelineStats = async (_req: Request, res: Response) => {
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
    } catch (err) {
      console.error('Error getting pipeline stats:', err);
      res.status(500).json({ error: 'Internal server error' });
    }
  };
}

