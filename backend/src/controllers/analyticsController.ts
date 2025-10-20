import { Request, Response } from 'express';
import Joi from 'joi';
import analyticsIngestionService from '../services/analyticsIngestionService';
import featureFlagService from '../services/featureFlagService';
import logger from '../utils/logger';

const eventSchema = Joi.object({
  eventName: Joi.string().required(),
  eventType: Joi.string().required(),
  customerId: Joi.string().optional(),
  accountId: Joi.string().optional(),
  userId: Joi.string().optional(),
  source: Joi.string().optional(),
  payload: Joi.object().unknown(true).optional(),
  metadata: Joi.object().unknown(true).optional(),
  occurredAt: Joi.alternatives(Joi.date().iso(), Joi.string()).optional(),
  correlationId: Joi.string().optional(),
  recommendationId: Joi.string().optional(),
});

const recommendationSchema = Joi.object({
  recommendationId: Joi.string().required(),
  agentName: Joi.string().optional(),
  customerId: Joi.string().optional(),
  accountId: Joi.string().optional(),
  recommendationType: Joi.string().optional(),
  priority: Joi.number().optional(),
  score: Joi.number().optional(),
  context: Joi.object().unknown(true).optional(),
  metadata: Joi.object().unknown(true).optional(),
  generatedAt: Joi.alternatives(Joi.date().iso(), Joi.string()).optional(),
  accepted: Joi.boolean().optional(),
  outcome: Joi.string().optional(),
  feedback: Joi.object().unknown(true).optional(),
});

export class AnalyticsController {
  ingestEvent = async (req: Request, res: Response) => {
    try {
      const { error, value } = eventSchema.validate(req.body, { abortEarly: false });
      if (error) {
        return res.status(400).json({ error: 'Invalid analytics event payload', details: error.details });
      }

      const actor = (req as any).user || {};
      const accountId = actor.accountId || actor.account_id;
      const userId = actor.id || actor.userId || actor.user_id;
      const enabled = await featureFlagService.shouldServe('analytics_event_ingestion', {
        accountId: value.accountId || accountId,
        userId: value.userId || userId,
        customerId: value.customerId,
      });

      if (!enabled) {
        logger.debug('Analytics event ingestion skipped due to feature flag disablement');
        return res.status(202).json({ status: 'skipped', reason: 'Feature flag disabled for context' });
      }

      const event = await analyticsIngestionService.recordEvent(value);
      res.status(201).json(event);
    } catch (err) {
      logger.error('Failed to ingest analytics event', err);
      res.status(500).json({ error: 'Failed to ingest analytics event' });
    }
  };

  ingestRecommendation = async (req: Request, res: Response) => {
    try {
      const { error, value } = recommendationSchema.validate(req.body, { abortEarly: false });
      if (error) {
        return res.status(400).json({ error: 'Invalid recommendation payload', details: error.details });
      }

      const actor = (req as any).user || {};
      const accountId = actor.accountId || actor.account_id;
      const userId = actor.id || actor.userId || actor.user_id;
      const enabled = await featureFlagService.shouldServe('analytics_recommendation_logging', {
        accountId: value.accountId || accountId,
        userId,
        customerId: value.customerId,
        fallbackId: value.agentName,
      });

      if (!enabled) {
        logger.debug('Recommendation logging skipped due to feature flag disablement');
        return res.status(202).json({ status: 'skipped', reason: 'Feature flag disabled for context' });
      }

      const recommendation = await analyticsIngestionService.recordRecommendation(value);
      res.status(201).json(recommendation);
    } catch (err) {
      logger.error('Failed to ingest recommendation analytics', err);
      res.status(500).json({ error: 'Failed to ingest recommendation analytics' });
    }
  };

  getSummary = async (req: Request, res: Response) => {
    try {
      const actor = (req as any).user || {};
      const accountId = actor.accountId || actor.account_id;
      const userId = actor.id || actor.userId || actor.user_id;
      const enabled = await featureFlagService.shouldServe('analytics_dashboards', {
        accountId,
        userId,
      });

      if (!enabled) {
        return res.status(403).json({ error: 'Analytics dashboards are not enabled for this account yet.' });
      }

      const summary = await analyticsIngestionService.getSummary();
      res.json(summary);
    } catch (err) {
      logger.error('Failed to load analytics summary', err);
      res.status(500).json({ error: 'Failed to load analytics summary' });
    }
  };

  getRecentEvents = async (req: Request, res: Response) => {
    try {
      const actor = (req as any).user || {};
      const accountId = actor.accountId || actor.account_id;
      const userId = actor.id || actor.userId || actor.user_id;
      const enabled = await featureFlagService.shouldServe('analytics_event_ingestion', {
        accountId,
        userId,
      });

      if (!enabled) {
        return res.status(403).json({ error: 'Event analytics are not enabled for this account yet.' });
      }

      const limit = Math.min(parseInt((req.query.limit as string) || '25', 10), 200);
      const events = await analyticsIngestionService.getRecentEvents(limit, {
        customerId: req.query.customerId as string,
        eventType: req.query.eventType as string,
      });
      res.json(events);
    } catch (err) {
      logger.error('Failed to load recent analytics events', err);
      res.status(500).json({ error: 'Failed to load recent analytics events' });
    }
  };
}

export default new AnalyticsController();
