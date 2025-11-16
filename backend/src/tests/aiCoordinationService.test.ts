import axios from 'axios';
import { AICoordinationService } from '../services/aiCoordinationService';

jest.mock('axios');

const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('AICoordinationService', () => {
  const service = new AICoordinationService();
  const payload = { task: 'demo' };

  beforeEach(() => {
    mockedAxios.post.mockReset();
    mockedAxios.get.mockReset();
  });

  it('sends tasks with correlation headers', async () => {
    mockedAxios.post.mockResolvedValue({ data: { status: 'ok' } } as any);

    const result = await service.sendTaskToAIWorker('demo', payload, 'corr-123');

    expect(result).toEqual({ status: 'ok' });
    expect(mockedAxios.post).toHaveBeenCalledWith(
      expect.stringContaining('/ai-task/demo'),
      payload,
      expect.objectContaining({ headers: expect.objectContaining({ 'X-Correlation-ID': 'corr-123' }) })
    );
  });

  it('throws when the worker is unavailable', async () => {
    mockedAxios.post.mockRejectedValue(new Error('boom'));
    await expect(service.sendTaskToAIWorker('demo', payload)).rejects.toThrow('Failed to communicate');
  });

  it('checks worker status with correlation headers', async () => {
    mockedAxios.get.mockResolvedValue({ data: { status: 'healthy' } } as any);
    const status = await service.getAIWorkerStatus('corr-999');
    expect(status).toEqual({ status: 'healthy' });
    expect(mockedAxios.get).toHaveBeenCalledWith(
      expect.stringContaining('/health'),
      expect.objectContaining({ headers: expect.objectContaining({ 'X-Correlation-ID': 'corr-999' }) })
    );
  });
});
