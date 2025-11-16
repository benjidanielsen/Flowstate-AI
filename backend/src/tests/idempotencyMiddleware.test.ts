import express, { Request, Response } from 'express';
import request from 'supertest';
import { idempotencyMiddleware } from '../middleware/idempotency';
import { cacheManager } from '../utils/cacheManager';

describe('idempotency middleware', () => {
  let app: express.Express;

  beforeEach(async () => {
    app = express();
    app.use(express.json());
    app.use(idempotencyMiddleware);

    app.post('/test-resource', (_req: Request, res: Response) => {
      res.status(201).json({
        method: 'POST',
        payloadId: `${Date.now()}-${Math.random()}`,
      });
    });

    app.put('/test-resource', (_req: Request, res: Response) => {
      res.status(200).json({
        method: 'PUT',
        payloadId: `${Date.now()}-${Math.random()}`,
      });
    });

    await cacheManager.clear();
  });

  it('replays cached POST response when the same idempotency key is reused', async () => {
    const key = 'post-key';

    const firstResponse = await request(app)
      .post('/test-resource')
      .set('X-Idempotency-Key', key)
      .send({ value: 'alpha' })
      .expect(201);

    const secondResponse = await request(app)
      .post('/test-resource')
      .set('X-Idempotency-Key', key)
      .send({ value: 'alpha' })
      .expect(201);

    expect(secondResponse.body).toEqual(firstResponse.body);
    expect(secondResponse.headers['content-type']).toEqual(firstResponse.headers['content-type']);
  });

  it('replays cached PUT response when the same idempotency key is reused', async () => {
    const key = 'put-key';

    const firstResponse = await request(app)
      .put('/test-resource')
      .set('X-Idempotency-Key', key)
      .send({ value: 'beta' })
      .expect(200);

    const secondResponse = await request(app)
      .put('/test-resource')
      .set('X-Idempotency-Key', key)
      .send({ value: 'beta' })
      .expect(200);

    expect(secondResponse.body).toEqual(firstResponse.body);
    expect(secondResponse.headers['content-type']).toEqual(firstResponse.headers['content-type']);
  });
});
