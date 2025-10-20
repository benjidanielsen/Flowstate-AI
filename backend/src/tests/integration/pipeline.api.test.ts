import express, { Express } from 'express';
import request from 'supertest';
import pipelineRoutes from '../../routes/pipelines';
import { pipelineService } from '../../services/pipelineService';

jest.mock('../../services/pipelineService', () => ({
  pipelineService: {
    listPipelines: jest.fn(),
    getPipelineById: jest.fn(),
    createPipeline: jest.fn(),
    upsertStage: jest.fn(),
    assignCustomerToStage: jest.fn(),
  }
}));

const mockedPipelineService = pipelineService as jest.Mocked<typeof pipelineService>;

describe('Pipeline API integration', () => {
  let app: Express;

  beforeEach(() => {
    jest.resetAllMocks();
    app = express();
    app.use(express.json());
    app.use('/pipelines', pipelineRoutes);
  });

  it('returns a list of pipelines', async () => {
    mockedPipelineService.listPipelines.mockResolvedValueOnce([
      {
        id: 'pipe-1',
        name: 'Demo Pipeline',
        description: 'Test pipeline',
        created_at: new Date(),
        updated_at: new Date(),
        stages: [
          {
            id: 'stage-1',
            pipeline_id: 'pipe-1',
            name: 'Lead',
            description: null,
            position: 0,
            metadata: {},
            created_at: new Date(),
            updated_at: new Date()
          }
        ]
      }
    ]);

    const response = await request(app).get('/pipelines');

    expect(response.status).toBe(200);
    expect(response.body).toHaveLength(1);
    expect(mockedPipelineService.listPipelines).toHaveBeenCalled();
  });

  it('assigns a customer to a stage', async () => {
    const stageId = '3b8f9027-1fa5-4f9c-8a5b-90527bba7a01';
    mockedPipelineService.assignCustomerToStage.mockResolvedValueOnce({
      id: 'cust-1',
      name: 'Test Customer',
      status: 'Lead',
      created_at: new Date(),
      updated_at: new Date()
    } as any);

    const response = await request(app)
      .post('/pipelines/customers/cust-1/stage')
      .send({ stageId });

    expect(response.status).toBe(200);
    expect(mockedPipelineService.assignCustomerToStage).toHaveBeenCalledWith('cust-1', stageId);
  });
});
