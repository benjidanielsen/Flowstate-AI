import { Request, Response } from 'express';
import Joi from 'joi';
import featureFlagService from '../services/featureFlagService';
import logger from '../utils/logger';

const upsertSchema = Joi.object({
  description: Joi.string().allow('', null),
  rolloutPhase: Joi.string().optional(),
  enabled: Joi.boolean().optional(),
  rolloutPercentage: Joi.number().integer().min(0).max(100).optional(),
  metadata: Joi.object().unknown(true).optional(),
});

export class FeatureFlagController {
  list = async (_req: Request, res: Response) => {
    try {
      const flags = await featureFlagService.listFlags();
      res.json(flags);
    } catch (err) {
      logger.error('Failed to list feature flags', err);
      res.status(500).json({ error: 'Failed to list feature flags' });
    }
  };

  get = async (req: Request, res: Response) => {
    try {
      const { key } = req.params;
      const flag = await featureFlagService.getFlag(key);
      if (!flag) {
        return res.status(404).json({ error: `Feature flag ${key} not found` });
      }

      const evaluation = await featureFlagService.shouldServe(key, {
        accountId: (req.query.accountId as string) || ((req as any).user?.accountId || (req as any).user?.account_id),
        userId: (req.query.userId as string) || ((req as any).user?.id || (req as any).user?.user_id),
        customerId: req.query.customerId as string,
      });

      res.json({ flag, enabledForContext: evaluation });
    } catch (err) {
      logger.error('Failed to fetch feature flag', err);
      res.status(500).json({ error: 'Failed to fetch feature flag' });
    }
  };

  upsert = async (req: Request, res: Response) => {
    try {
      const { error, value } = upsertSchema.validate(req.body, { abortEarly: false });
      if (error) {
        return res.status(400).json({ error: 'Invalid feature flag payload', details: error.details });
      }

      const flag = await featureFlagService.upsertFlag(req.params.key, value);
      res.json(flag);
    } catch (err) {
      logger.error('Failed to update feature flag', err);
      res.status(500).json({ error: 'Failed to update feature flag' });
    }
  };

  getActive = async (_req: Request, res: Response) => {
    try {
      const flags = await featureFlagService.getActiveFlags();
      res.json(flags);
    } catch (err) {
      logger.error('Failed to fetch active feature flags', err);
      res.status(500).json({ error: 'Failed to fetch active feature flags' });
    }
  };
}

export default new FeatureFlagController();
