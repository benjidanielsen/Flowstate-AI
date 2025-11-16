import request from 'supertest';
import express from 'express';
import kpiRoutes from '../routes/kpis';
import { register } from '../utils/metrics';

const AUTH_HEADER = 'Bearer test-bypass-token';

describe('KPI Routes', () => {
  const app = express();
  app.use(express.json());
  app.use('/kpis', kpiRoutes);

  beforeAll(() => {
    process.env.BYPASS_AUTH_TOKEN = AUTH_HEADER.replace('Bearer ', '');
  });

  afterEach(() => {
    register.resetMetrics();
  });

  it('returns KPI data for a valid category and records metrics', async () => {
    const response = await request(app)
      .get('/kpis?category=executive')
      .set('Authorization', AUTH_HEADER);

    expect(response.status).toBe(200);
    expect(Array.isArray(response.body)).toBe(true);
    expect(response.body.length).toBeGreaterThan(0);

    const metrics = await register.getSingleMetricAsString('flowstate_kpi_value');
    expect(metrics).toContain('executive');
    expect(metrics).toContain('Monthly Active Users');
  });

  it('rejects invalid categories', async () => {
    const response = await request(app)
      .get('/kpis?category=unknown')
      .set('Authorization', AUTH_HEADER);

    expect(response.status).toBe(400);
    expect(response.body.error).toContain('Invalid');
  });
});
