import { Request, Response } from 'express';
import { AICoordinationService } from '../services/aiCoordinationService';

import logger from '../utils/logger';

const aiCoordinationService = new AICoordinationService();

export const sendTask = async (req: Request, res: Response) => {
  try {
    const { taskType, payload } = req.body;
    const result = await aiCoordinationService.sendTaskToAIWorker(taskType, payload);
    res.status(200).json(result);
  } catch (error: any) {
    logger.error('Error sending task to AI worker:', error);
    res.status(500).json({ message: 'Failed to send task to AI worker', error: error.message });
  }
};

export const getStatus = async (req: Request, res: Response) => {
  try {
    const status = await aiCoordinationService.getAIWorkerStatus();
    res.status(200).json(status);
  } catch (error: any) {
    logger.error('Error getting AI worker status:', error);
    res.status(500).json({ message: 'Failed to get AI worker status', error: error.message });
  }
};

