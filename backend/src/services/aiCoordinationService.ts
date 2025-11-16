
import logger from '../utils/logger';
import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';

export class AICoordinationService {
  private pythonWorkerUrl: string;

  constructor() {
    this.pythonWorkerUrl = process.env.PYTHON_WORKER_URL || 'http://localhost:8000'; // Default to local FastAPI
  }

  async sendTaskToAIWorker(taskType: string, payload: any, correlationId?: string): Promise<any> {
    const traceCorrelation = correlationId || uuidv4();
    logger.info(`Sending task '${taskType}' to AI worker`, { payload, correlationId: traceCorrelation });
    try {
      const response = await axios.post(`${this.pythonWorkerUrl}/ai-task/${taskType}`, payload, {
        headers: { 'X-Correlation-ID': traceCorrelation },
      });
      logger.info(`AI worker responded to task '${taskType}'`, { responseData: response.data, correlationId: traceCorrelation });
      return response.data;
    } catch (error: any) {
      logger.error(`Error sending task '${taskType}' to AI worker: ${error.message}`, { error, correlationId: traceCorrelation });
      throw new Error(`Failed to communicate with AI worker: ${error.message}`);
    }
  }

  async getAIWorkerStatus(correlationId?: string): Promise<any> {
    const traceCorrelation = correlationId || uuidv4();
    logger.info('Checking AI worker status', { correlationId: traceCorrelation });
    try {
      const response = await axios.get(`${this.pythonWorkerUrl}/health`, {
        headers: { 'X-Correlation-ID': traceCorrelation },
      });
      logger.info('AI worker status check successful', { status: response.data.status, correlationId: traceCorrelation });
      return response.data;
    } catch (error: any) {
      logger.error(`Error checking AI worker status: ${error.message}`, { error, correlationId: traceCorrelation });
      throw new Error(`Failed to get AI worker status: ${error.message}`);
    }
  }
}

