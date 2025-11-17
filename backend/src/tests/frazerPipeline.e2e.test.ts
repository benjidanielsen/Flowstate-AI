import request from 'supertest';
import jwt from 'jsonwebtoken';
import express from 'express';
import customerRoutes from '../routes/customers';
import statsRoutes from '../routes/stats';
import DatabaseManager from '../database';
import { runMigrations } from '../database/migrate';
import { PipelineStatus } from '../types';
import { authenticateToken } from '../middleware/authMiddleware';

const JWT_SECRET = process.env.JWT_SECRET || 'supersecretjwtkey';

describe('Frazer pipeline end-to-end API', () => {
  const dbManager = DatabaseManager.getInstance();
  let token: string;
  let app: express.Express;

  beforeAll(async () => {
    await dbManager.connect();
    await resetDatabase();
    await runMigrations();
    app = buildTestApp();
    token = jwt.sign({ sub: 'frazer-e2e', roles: ['admin'] }, JWT_SECRET);
  });

  afterAll(async () => {
    await dbManager.close();
  });

  it('walks a lead through Frazer stages and emits telemetry', async () => {
    const agent = request(app);
    const headers = { Authorization: `Bearer ${token}` };

    const createResponse = await agent
      .post('/api/customers')
      .set(headers)
      .send({
        name: 'Frazer API Test',
        email: `frazer-${Date.now()}@example.com`,
        status: PipelineStatus.NEW_LEAD,
        notes: 'Stage-walk test'
      })
      .expect(201);

    const customerId = createResponse.body.id;
    expect(createResponse.body.status).toBe(PipelineStatus.NEW_LEAD);

    const progressionTargets = [
      PipelineStatus.WARMING_UP,
      PipelineStatus.INVITED,
      PipelineStatus.QUALIFIED,
      PipelineStatus.PRESENTATION_SENT
    ];

    for (const expectedStage of progressionTargets) {
      const response = await agent
        .post(`/api/customers/${customerId}/next-stage`)
        .set(headers)
        .expect(200);

      expect(response.body.status).toBe(expectedStage);
    }

    const stageTransitionCount = await countRows(
      'SELECT COUNT(*) as c FROM event_logs WHERE customer_id = ? AND event_type = ?',
      [customerId, 'frazer_stage_transition']
    );
    expect(stageTransitionCount).toBe(progressionTargets.length);

    const reminderCount = await countRows(
      'SELECT COUNT(*) as c FROM reminders WHERE customer_id = ? AND completed = 0',
      [customerId]
    );
    expect(reminderCount).toBeGreaterThanOrEqual(1);

    const statsResponse = await agent
      .get('/api/customers/stats')
      .set(headers)
      .expect(200);

    expect(statsResponse.body.counts_by_status[PipelineStatus.PRESENTATION_SENT]).toBeGreaterThanOrEqual(1);
    expect(statsResponse.body.dmo_today).toBeDefined();
    expect(statsResponse.body.overdue_followups).toBeDefined();
  });
});

async function resetDatabase() {
  const db = DatabaseManager.getInstance().getDb();
  await new Promise<void>((resolve, reject) => {
    db.exec(
      'DROP TABLE IF EXISTS reminders; DROP TABLE IF EXISTS interactions; DROP TABLE IF EXISTS event_logs; DROP TABLE IF EXISTS customers;',
      (err) => {
        if (err) reject(err);
        else resolve();
      }
    );
  });
}

async function countRows(query: string, params: any[]): Promise<number> {
  const db = DatabaseManager.getInstance().getDb();
  return new Promise((resolve, reject) => {
    db.get(query, params, (err, row: any) => {
      if (err) return reject(err);
      resolve(row?.c || row?.count || 0);
    });
  });
}

function buildTestApp() {
  const app = express();
  app.use(express.json());

  const apiRouter = express.Router();
  apiRouter.use(authenticateToken);
  apiRouter.use('/customers', customerRoutes);
  apiRouter.use('/stats', statsRoutes);

  app.use('/api', apiRouter);
  return app;
}
