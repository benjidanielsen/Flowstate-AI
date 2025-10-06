import http from 'http';
import request from 'supertest';
import { shutdown, startServer } from '../index';

describe('server lifecycle', () => {
  let server: http.Server;
  // let app: Express.Application;
  let port: number;



  beforeAll(async () => {
    // Assign a unique port for the test suite
    port = Math.floor(Math.random() * (40000 - 30000 + 1)) + 30000;
    process.env.PORT = port.toString();

    // app = createApp(); // Create the app once for the test suite
    // Start the server once for the entire test suite
    server = await startServer();
  });

  afterAll(async () => {
    // Shut down the server once after all tests
    try {
      await shutdown();
    } catch (e) {
      // Ignore errors if server was not running
    }
  });

  it('should start and shutdown without open handles', async () => {

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

    expect(server).toBeDefined();

    await shutdown();
    await shutdown(); // Second call should be harmless

    await expect(request(`http://localhost:${port}`).get('/api/health')).rejects.toThrow();
  });
});

