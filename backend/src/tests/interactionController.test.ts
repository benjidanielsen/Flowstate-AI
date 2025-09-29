import request from 'supertest';
import app from '../index';
import DatabaseManager from '../database';
import { v4 as uuidv4 } from 'uuid';

describe('Interaction completion API', () => {
  beforeAll(async () => {
    await DatabaseManager.getInstance().connect();
    // run migrations to ensure schema
    const { runMigrations } = await import('../database/migrate');
    await runMigrations();
  });

  afterAll(async () => {
    await DatabaseManager.getInstance().close();
  });

  it('marks an interaction as completed', async () => {
    const db = DatabaseManager.getInstance().getDb();
    const id = uuidv4();
    const customerId = uuidv4();
    const now = new Date().toISOString();

    // Insert an interaction directly
    await new Promise<void>((resolve, reject) => {
      const stmt = db.prepare(`INSERT INTO interactions (id, customer_id, type, content, created_at, completed) VALUES (?, ?, ?, ?, ?, ?)`);
      stmt.run([id, customerId, 'note', 'test content', now, 0], (err) => {
        if (err) return reject(err);
        resolve();
      });
      stmt.finalize();
    });

    const res = await request(app).post(`/api/interactions/${id}/complete`).send();
    expect(res.status).toBe(200);
    expect(res.body).toBeDefined();
    expect(res.body.completed).toBeTruthy();

    // Verify from DB
    const row = await new Promise<any>((resolve, reject) => {
      db.get('SELECT completed FROM interactions WHERE id = ?', [id], (err, row) => {
        if (err) return reject(err);
        resolve(row);
      });
    });

    expect(row.completed).toBe(1);
  }, 20000);
});
