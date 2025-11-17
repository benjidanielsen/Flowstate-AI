
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

  async getAgentStatuses(): Promise<any> {
    try {
      const response = await axios.get(`${this.pythonWorkerUrl}/evolution/agents`);
      return response.data;
    } catch (error: any) {
      logger.error('Failed to fetch agent statuses from worker', { error: error.message });
      throw new Error(`Failed to fetch agent statuses: ${error.message}`);
    }
  }

  async getApprovalQueue(): Promise<any> {
    try {
      const response = await axios.get(`${this.pythonWorkerUrl}/evolution/approvals`);
      return response.data;
    } catch (error: any) {
      logger.error('Failed to fetch approval queue from worker', { error: error.message });
      throw new Error(`Failed to fetch approval queue: ${error.message}`);
    }
  }

  async submitApprovalDecision(eventId: string, payload: { decision: 'approve' | 'reject'; rationale: string; decision_maker: string; }): Promise<any> {
    try {
      const response = await axios.post(`${this.pythonWorkerUrl}/evolution/approvals/${eventId}`, payload);
      return response.data;
    } catch (error: any) {
      logger.error(`Failed to submit approval decision for ${eventId}`, { error: error.message });
      throw new Error(`Failed to submit approval decision: ${error.message}`);
    }
  }

  async sendEvolutionSignal(signal: any): Promise<any> {
    try {
      const response = await axios.post(`${this.pythonWorkerUrl}/evolution/signals`, signal);
      return response.data;
    } catch (error: any) {
      logger.error('Failed to send evolution signal to worker', { error: error.message, signal });
      throw new Error(`Failed to send evolution signal: ${error.message}`);
    }
  }
}

