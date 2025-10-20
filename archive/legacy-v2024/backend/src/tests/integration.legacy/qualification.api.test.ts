import request from 'supertest';
import express, { Express } from 'express';
import qualificationRoutes from '../../routes/qualification';
import DatabaseManager from '../../database';
import { v4 as uuidv4 } from 'uuid';

describe('Qualification API Integration Tests', () => {
  let app: Express;
  let testCustomerId: string;

  beforeAll(async () => {
    app = express();
    app.use(express.json());
    app.use('/api/qualification', qualificationRoutes);

    // Create a test customer for qualification
    const db = DatabaseManager.getInstance().getDb();
    testCustomerId = uuidv4();
    await new Promise((resolve, reject) => {
      db.run(
        'INSERT INTO customers (id, name, email, status, created_at, updated_at) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)',
        [testCustomerId, 'Qualification Test Customer', `qualtest${Date.now()}@example.com`, 'invited'],
        (err) => {
          if (err) reject(err);
          else resolve(null);
        }
      );
    });
  });

  afterAll(async () => {
    // Clean up test customer
    const db = DatabaseManager.getInstance().getDb();
    await new Promise((resolve, reject) => {
      db.run('DELETE FROM customers WHERE id = ?', [testCustomerId], (err) => {
        if (err) reject(err);
        else resolve(null);
      });
    });
    db.close();
  });

  describe('POST /api/qualification', () => {
    it('should save qualification data for a customer', async () => {
      const qualificationData = {
        customer_id: testCustomerId,
        prospect_why: 'Wants financial freedom to spend more time with family',
      };

      const response = await request(app)
        .post('/api/qualification')
        .send(qualificationData)
        .expect(200);

      expect(response.body).toHaveProperty('id');
      expect(response.body.prospect_why).toBe(qualificationData.prospect_why);
      expect(response.body.status).toBe('Qualified');
    });

    it('should update existing qualification data', async () => {
      const updatedQualification = {
        customer_id: testCustomerId,
        prospect_why: 'Updated: Seeking entrepreneurship and personal growth',
      };

      const response = await request(app)
        .post('/api/qualification')
        .send(updatedQualification)
        .expect(200);

      expect(response.body.prospect_why).toBe(updatedQualification.prospect_why);
    });

    it('should return 400 for invalid qualification data', async () => {
      const invalidQualification = {
        customer_id: testCustomerId,
        // Missing prospect_why
      };

      await request(app)
        .post('/api/qualification')
        .send(invalidQualification)
        .expect(400);
    });

    it('should return 404 for non-existent customer', async () => {
      const qualificationData = {
        customer_id: '00000000-0000-0000-0000-000000000000',
        prospect_why: 'Test',
      };

      await request(app)
        .post('/api/qualification')
        .send(qualificationData)
        .expect(404);
    });
  });

  describe('GET /api/qualification/:id', () => {
    beforeAll(async () => {
      // Ensure qualification data exists
      await pool.query(
        'UPDATE customers SET prospect_why = $1, status = $2 WHERE id = $3',
        ['Wants to achieve work-life balance', 'Qualified', testCustomerId]
      );
    });

    it('should retrieve qualification data for a customer', async () => {
      const response = await request(app)
        .get(`/api/qualification/${testCustomerId}`)
        .expect(200);

      expect(response.body.id).toBe(testCustomerId);
      expect(response.body.prospect_why).toBe('Wants to achieve work-life balance');
      expect(response.body.status).toBe('Qualified');
    });

    it('should return 404 for non-existent customer', async () => {
      await request(app)
        .get('/api/qualification/00000000-0000-0000-0000-000000000000')
        .expect(404);
    });

    it('should return 404 for customer without qualification data', async () => {
      // Create a customer without qualification
      const result = await pool.query(
        'INSERT INTO customers (name, email, status) VALUES ($1, $2, $3) RETURNING id',
        ['No Qual Customer', `noqual${Date.now()}@example.com`, 'Invited']
      );
      const noQualCustomerId = result.rows[0].id;

      await request(app)
        .get(`/api/qualification/${noQualCustomerId}`)
        .expect(404);

      // Clean up
      await pool.query('DELETE FROM customers WHERE id = $1', [noQualCustomerId]);
    });
  });
});
