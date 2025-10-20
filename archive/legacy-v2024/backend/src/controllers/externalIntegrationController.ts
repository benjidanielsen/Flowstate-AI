import { Request, Response } from 'express';
import { ExternalIntegrationService } from '../services/externalIntegrationService';

import logger from '../utils/logger';

const externalIntegrationService = new ExternalIntegrationService();

export const createIntegration = async (req: Request, res: Response) => {
  try {
    const { customer_id, type, config } = req.body;
    const newIntegration = await externalIntegrationService.createIntegration({ customer_id, type, config });
    res.status(201).json(newIntegration);
  } catch (error) {
    logger.error('Error creating external integration:', error);
    res.status(500).json({ message: 'Failed to create integration' });
  }
};

export const getIntegrationsByCustomer = async (req: Request, res: Response) => {
  try {
    const { customerId } = req.params;
    const integrations = await externalIntegrationService.getIntegrationsByCustomer(customerId);
    res.status(200).json(integrations);
  } catch (error) {
    logger.error('Error fetching external integrations:', error);
    res.status(500).json({ message: 'Failed to fetch integrations' });
  }
};

export const updateIntegration = async (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    const updates = req.body;
    const updatedIntegration = await externalIntegrationService.updateIntegration(id, updates);
    res.status(200).json(updatedIntegration);
  } catch (error) {
    logger.error('Error updating external integration:', error);
    res.status(500).json({ message: 'Failed to update integration' });
  }
};

export const deleteIntegration = async (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    await externalIntegrationService.deleteIntegration(id);
    res.status(204).send();
  } catch (error) {
    logger.error('Error deleting external integration:', error);
    res.status(500).json({ message: 'Failed to delete integration' });
  }
};

