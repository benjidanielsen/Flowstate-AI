import request from 'supertest';
import express, { Express } from 'express';
import reminderRoutes from '../../routes/reminders';
import DatabaseManager from '../../database';
import { v4 as uuidv4 } from 'uuid';

describe('Reminders API Integration Tests', () => {
  let app: Express;
  let testCustomerId: string;

  beforeAll(async () => {
    app = express();
    app.use(express.json());
    app.use('/api/reminders', reminderRoutes);

    // Create a test customer for reminders
    const db = DatabaseManager.getInstance().getDb();
    testCustomerId = uuidv4();
    await new Promise((resolve, reject) => {
      db.run(
        'INSERT INTO customers (id, name, email, status, created_at, updated_at) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)',
        [testCustomerId, 'Reminder Test Customer', `remindertest${Date.now()}@example.com`, 'invited'],
        (err) => {
          if (err) reject(err);
          else resolve(null);
        }
      );
    });
  });

  afterAll(async () => {
    // Clean up test customer and related reminders
    await pool.query('DELETE FROM reminders WHERE customer_id = $1', [testCustomerId]);
    await pool.query('DELETE FROM customers WHERE id = $1', [testCustomerId]);
    await pool.end();
  });

  describe('POST /api/reminders', () => {
    let createdReminderId: string;

    it('should create a new reminder', async () => {
      const newReminder = {
        customer_id: testCustomerId,
        type: 'Follow-up',
        description: 'Call to discuss proposal',
        due_date: new Date(Date.now() + 86400000).toISOString(), // Tomorrow
      };

      const response = await request(app)
        .post('/api/reminders')
        .send(newReminder)
        .expect(201);

      expect(response.body).toHaveProperty('id');
      expect(response.body.customer_id).toBe(testCustomerId);
      expect(response.body.type).toBe(newReminder.type);
      expect(response.body.description).toBe(newReminder.description);
      expect(response.body.completed).toBe(false);

      createdReminderId = response.body.id;
    });

    it('should return 400 for invalid reminder data', async () => {
      const invalidReminder = {
        customer_id: testCustomerId,
        // Missing required fields
      };

      await request(app)
        .post('/api/reminders')
        .send(invalidReminder)
        .expect(400);
    });

    afterAll(async () => {
      if (createdReminderId) {
        await pool.query('DELETE FROM reminders WHERE id = $1', [createdReminderId]);
      }
    });
  });

  describe('GET /api/reminders/due', () => {
    let dueReminderId: string;
    let futureReminderId: string;

    beforeAll(async () => {
      // Create a due reminder (yesterday)
      const dueResult = await pool.query(
        `INSERT INTO reminders (customer_id, type, description, due_date, completed)
         VALUES ($1, $2, $3, $4, $5) RETURNING id`,
        [testCustomerId, 'Follow-up', 'Overdue reminder', new Date(Date.now() - 86400000).toISOString(), false]
      );
      dueReminderId = dueResult.rows[0].id;

      // Create a future reminder (next week)
      const futureResult = await pool.query(
        `INSERT INTO reminders (customer_id, type, description, due_date, completed)
         VALUES ($1, $2, $3, $4, $5) RETURNING id`,
        [testCustomerId, 'Meeting', 'Future reminder', new Date(Date.now() + 604800000).toISOString(), false]
      );
      futureReminderId = futureResult.rows[0].id;
    });

    it('should return only due reminders', async () => {
      const response = await request(app)
        .get('/api/reminders/due')
        .expect(200);

      expect(Array.isArray(response.body)).toBe(true);
      
      // Check that the due reminder is in the response
      const dueReminder = response.body.find((r: any) => r.id === dueReminderId);
      expect(dueReminder).toBeDefined();
      expect(dueReminder.description).toBe('Overdue reminder');

      // Check that the future reminder is NOT in the response
      const futureReminder = response.body.find((r: any) => r.id === futureReminderId);
      expect(futureReminder).toBeUndefined();
    });

    afterAll(async () => {
      await pool.query('DELETE FROM reminders WHERE id IN ($1, $2)', [dueReminderId, futureReminderId]);
    });
  });

  describe('POST /api/reminders/:id/complete', () => {
    let testReminderId: string;

    beforeAll(async () => {
      const result = await pool.query(
        `INSERT INTO reminders (customer_id, type, description, due_date, completed)
         VALUES ($1, $2, $3, $4, $5) RETURNING id`,
        [testCustomerId, 'Task', 'Test reminder to complete', new Date().toISOString(), false]
      );
      testReminderId = result.rows[0].id;
    });

    it('should mark a reminder as complete', async () => {
      const response = await request(app)
        .post(`/api/reminders/${testReminderId}/complete`)
        .expect(200);

      expect(response.body.completed).toBe(true);

      // Verify in database
      const result = await pool.query('SELECT completed FROM reminders WHERE id = $1', [testReminderId]);
      expect(result.rows[0].completed).toBe(true);
    });

    it('should return 404 for non-existent reminder', async () => {
      await request(app)
        .post('/api/reminders/00000000-0000-0000-0000-000000000000/complete')
        .expect(404);
    });

    afterAll(async () => {
      await pool.query('DELETE FROM reminders WHERE id = $1', [testReminderId]);
    });
  });
});
