import request from 'supertest';
import { startServer, shutdown } from '../index';
import DatabaseManager from '../database';

describe('server lifecycle', () => {
  afterAll(async () => {
    // Ensure server is shutdown in case of test failures
    try {
      await shutdown();
    } catch (err) {
      // ignore
    }
  });

  test('start and shutdown without open handles', async () => {
    await startServer();

    // Hit health endpoint
    const res = await request('http://localhost:3001').get('/api/health');
    expect(res.status).toBe(200);
    expect(res.body).toHaveProperty('status');

    // Shutdown
    await shutdown();

    // After shutdown, server should not respond
    await expect(request('http://localhost:3001').get('/api/health')).rejects.toBeDefined();

    // Database should be closed and getDb() should throw
    expect(() => DatabaseManager.getInstance().getDb()).toThrow();
  }, 20000);
});

