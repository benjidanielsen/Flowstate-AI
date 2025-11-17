import request from 'supertest';
import { createApp } from '../src/index';

describe('Customers API', () => {
  it('GET /customers returns 200 and array', async () => {
    const app = createApp();
    const res = await request(app).get('/customers');
    expect(res.status).toBe(200);
    expect(Array.isArray(res.body)).toBe(true);
  });

  it('POST /customers creates a customer', async () => {
    const app = createApp();
    const res = await request(app).post('/customers').send({ name: 'Test' });
    expect(res.status).toBe(201);
    expect(res.body.name).toBe('Test');
    expect(res.body.id).toBeDefined();
  });
});
