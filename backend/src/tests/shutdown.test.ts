import { startServer, shutdown, createApp } from '../index';
import request from 'supertest';
import http from 'http';

describe('server lifecycle', () => {
  let server: http.Server;
  let app: Express.Application;
  let port: number;

  beforeAll(() => {
    app = createApp(); // Create the app once for the test suite
  });

  beforeEach(async () => {
    // Assign a unique port for each test
    port = Math.floor(Math.random() * (40000 - 30000 + 1)) + 30000;
    process.env.PORT = port.toString();

    // Ensure server is not running before each test
    try {
      await shutdown();
    } catch (e) {
      // Ignore errors if server was not running
    }
  });

  afterEach(async () => {
    // Ensure server is shut down after each test
    try {
      await shutdown();
    } catch (e) {
      // Ignore errors if server was not running
    }
  });

  it('should start and shutdown without open handles', async () => {
    server = await startServer();
    expect(server).toBeDefined();

    // Make a request to ensure server is responsive
    const res = await request(`http://localhost:${port}`).get('/api/health');
    expect(res.statusCode).toEqual(200);
    expect(res.body.status).toEqual('OK');

    await shutdown();
    // Verify server is closed (e.g., by trying to connect again, which should fail)
    // Note: supertest will throw if the server is not listening, so we expect a rejection.
    await expect(request(`http://localhost:${port}`).get('/api/health')).rejects.toThrow();
  });

  it('should handle multiple shutdown calls gracefully', async () => {
    server = await startServer();
    expect(server).toBeDefined();

    await shutdown();
    await shutdown(); // Second call should be harmless

    await expect(request(`http://localhost:${port}`).get('/api/health')).rejects.toThrow();
  });
});

