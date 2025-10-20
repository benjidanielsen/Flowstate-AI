import { Request, Response } from 'express';
import Joi from 'joi';
import { pipelineService } from '../services/pipelineService';
import logger from '../utils/logger';

const pipelineSchema = Joi.object({
  name: Joi.string().min(2).max(120).required(),
  description: Joi.string().allow('', null),
  stages: Joi.array().items(
    Joi.object({
      id: Joi.string().uuid().optional(),
      name: Joi.string().min(1).max(120).required(),
      description: Joi.string().allow('', null),
      position: Joi.number().integer().min(0).required(),
      metadata: Joi.object().default({})
    })
  ).optional()
});

const stageSchema = Joi.object({
  name: Joi.string().min(1).max(120).required(),
  description: Joi.string().allow('', null),
  position: Joi.number().integer().min(0).required(),
  metadata: Joi.object().default({})
});

const assignSchema = Joi.object({
  stageId: Joi.string().uuid().required()
});

export class PipelineController {
  list = async (_req: Request, res: Response) => {
    try {
      const pipelines = await pipelineService.listPipelines();
      res.json(pipelines);
    } catch (error) {
      logger.error('Failed to list pipelines', error);
      res.status(500).json({ error: 'Failed to list pipelines' });
    }
  };

  getById = async (req: Request, res: Response) => {
    try {
      const pipeline = await pipelineService.getPipelineById(req.params.pipelineId);
      if (!pipeline) {
        return res.status(404).json({ error: 'Pipeline not found' });
      }
      res.json(pipeline);
    } catch (error) {
      logger.error('Failed to fetch pipeline', error);
      res.status(500).json({ error: 'Failed to fetch pipeline' });
    }
  };

  create = async (req: Request, res: Response) => {
    const { error, value } = pipelineSchema.validate(req.body, { abortEarly: false });
    if (error) {
      return res.status(400).json({ error: 'Invalid payload', details: error.details });
    }

    try {
      const pipeline = await pipelineService.createPipeline(value);
      res.status(201).json(pipeline);
    } catch (err) {
      logger.error('Failed to create pipeline', err);
      res.status(500).json({ error: 'Failed to create pipeline' });
    }
  };

  upsertStage = async (req: Request, res: Response) => {
    const { error, value } = stageSchema.validate(req.body, { abortEarly: false });
    if (error) {
      return res.status(400).json({ error: 'Invalid payload', details: error.details });
    }

    try {
      const stage = await pipelineService.upsertStage(req.params.pipelineId, {
        ...value,
        id: req.params.stageId
      });
      res.status(req.params.stageId ? 200 : 201).json(stage);
    } catch (err) {
      logger.error('Failed to upsert pipeline stage', err);
      res.status(500).json({ error: 'Failed to upsert pipeline stage' });
    }
  };

  assignCustomerStage = async (req: Request, res: Response) => {
    const { error, value } = assignSchema.validate(req.body, { abortEarly: false });
    if (error) {
      return res.status(400).json({ error: 'Invalid payload', details: error.details });
    }

    try {
      const customer = await pipelineService.assignCustomerToStage(req.params.customerId, value.stageId);
      if (!customer) {
        return res.status(404).json({ error: 'Customer not found' });
      }
      res.json(customer);
    } catch (err) {
      logger.error('Failed to assign stage to customer', err);
      res.status(500).json({ error: 'Failed to assign stage to customer' });
    }
  };
}

export const pipelineController = new PipelineController();
