import { Database } from '../types';
import logger from '../utils/logger';
import axios from 'axios';

export class AICoordinationService {
  private pythonWorkerUrl: string;

  constructor() {
    this.pythonWorkerUrl = process.env.PYTHON_WORKER_URL || 'http://localhost:8000'; // Default to local FastAPI
  }

  async sendTaskToAIWorker(taskType: string, payload: any): Promise<any> {
    logger.info(`Sending task '${taskType}' to AI worker`, { payload });
    try {
      const response = await axios.post(`${this.pythonWorkerUrl}/ai-task/${taskType}`, payload);
      logger.info(`AI worker responded to task '${taskType}'`, { responseData: response.data });
      return response.data;
    } catch (error: any) {
      logger.error(`Error sending task '${taskType}' to AI worker: ${error.message}`, { error });
      throw new Error(`Failed to communicate with AI worker: ${error.message}`);
    }
  }

  async getAIWorkerStatus(): Promise<any> {
    logger.info('Checking AI worker status');
    try {
      const response = await axios.get(`${this.pythonWorkerUrl}/health`);
      logger.info('AI worker status check successful', { status: response.data.status });
      return response.data;
    } catch (error: any) {
      logger.error(`Error checking AI worker status: ${error.message}`, { error });
      throw new Error(`Failed to get AI worker status: ${error.message}`);
    }
  }
}

