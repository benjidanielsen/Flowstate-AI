import express from 'express';
import request from 'supertest';
import jwt from 'jsonwebtoken';

import kpiRoutes from '../routes/kpis';

const JWT_SECRET = process.env.JWT_SECRET || 'supersecretjwtkey';

describe('KPI Routes Authentication', () => {
  const app = express();
  app.use(express.json());
  app.use('/api/kpis', kpiRoutes);

  it('should return 401 when no token is provided', async () => {
    const response = await request(app).get('/api/kpis?category=executive');
    expect(response.status).toBe(401);
  });

  it('should return 403 for invalid tokens', async () => {
    const response = await request(app)
      .get('/api/kpis?category=executive')
      .set('Authorization', 'Bearer invalid-token');
    expect(response.status).toBe(403);
  });

  it('should return KPI data when provided a valid JWT', async () => {
    const token = jwt.sign({ userId: 'test-user' }, JWT_SECRET);
    const response = await request(app)
      .get('/api/kpis?category=executive')
      .set('Authorization', `Bearer ${token}`);

    expect(response.status).toBe(200);
    expect(Array.isArray(response.body)).toBe(true);
    expect(response.body.length).toBeGreaterThan(0);
  });
});
