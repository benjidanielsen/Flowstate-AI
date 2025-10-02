import request from 'supertest';
import express, { Express } from 'express';
import customerRoutes from '../../routes/customers';
import { pool } from '../../database/db';

describe('Customers API Integration Tests', () => {
  let app: Express;

  beforeAll(() => {
    app = express();
    app.use(express.json());
    app.use('/api/customers', customerRoutes);
  });

  afterAll(async () => {
    await pool.end();
  });

  describe('GET /api/customers', () => {
    it('should return all customers', async () => {
      const response = await request(app)
        .get('/api/customers')
        .expect(200);

      expect(Array.isArray(response.body)).toBe(true);
      if (response.body.length > 0) {
        expect(response.body[0]).toHaveProperty('id');
        expect(response.body[0]).toHaveProperty('name');
        expect(response.body[0]).toHaveProperty('email');
        expect(response.body[0]).toHaveProperty('status');
      }
    });
  });

  describe('GET /api/customers/stats', () => {
    it('should return pipeline statistics', async () => {
      const response = await request(app)
        .get('/api/customers/stats')
        .expect(200);

      expect(response.body).toHaveProperty('total');
      expect(typeof response.body.total).toBe('number');
    });
  });

  describe('POST /api/customers', () => {
    let createdCustomerId: string;

    it('should create a new customer', async () => {
      const newCustomer = {
        name: 'Test Customer',
        email: `test${Date.now()}@example.com`,
        phone: '555-0123',
      };

      const response = await request(app)
        .post('/api/customers')
        .send(newCustomer)
        .expect(201);

      expect(response.body).toHaveProperty('id');
      expect(response.body.name).toBe(newCustomer.name);
      expect(response.body.email).toBe(newCustomer.email);
      expect(response.body.phone).toBe(newCustomer.phone);
      expect(response.body.status).toBe('Invited');

      createdCustomerId = response.body.id;
    });

    it('should return 400 for invalid customer data', async () => {
      const invalidCustomer = {
        name: '',
        email: 'invalid-email',
      };

      await request(app)
        .post('/api/customers')
        .send(invalidCustomer)
        .expect(400);
    });

    afterAll(async () => {
      if (createdCustomerId) {
        await pool.query('DELETE FROM customers WHERE id = $1', [createdCustomerId]);
      }
    });
  });

  describe('GET /api/customers/:id', () => {
    let testCustomerId: string;

    beforeAll(async () => {
      const result = await pool.query(
        'INSERT INTO customers (name, email, status) VALUES ($1, $2, $3) RETURNING id',
        ['Get Test Customer', `gettest${Date.now()}@example.com`, 'Invited']
      );
      testCustomerId = result.rows[0].id;
    });

    it('should return a customer by ID', async () => {
      const response = await request(app)
        .get(`/api/customers/${testCustomerId}`)
        .expect(200);

      expect(response.body.id).toBe(testCustomerId);
      expect(response.body.name).toBe('Get Test Customer');
    });

    it('should return 404 for non-existent customer', async () => {
      await request(app)
        .get('/api/customers/00000000-0000-0000-0000-000000000000')
        .expect(404);
    });

    afterAll(async () => {
      await pool.query('DELETE FROM customers WHERE id = $1', [testCustomerId]);
    });
  });

  describe('PUT /api/customers/:id', () => {
    let testCustomerId: string;

    beforeAll(async () => {
      const result = await pool.query(
        'INSERT INTO customers (name, email, status) VALUES ($1, $2, $3) RETURNING id',
        ['Update Test Customer', `updatetest${Date.now()}@example.com`, 'Invited']
      );
      testCustomerId = result.rows[0].id;
    });

    it('should update a customer', async () => {
      const updates = {
        name: 'Updated Customer Name',
        phone: '555-9999',
      };

      const response = await request(app)
        .put(`/api/customers/${testCustomerId}`)
        .send(updates)
        .expect(200);

      expect(response.body.name).toBe(updates.name);
      expect(response.body.phone).toBe(updates.phone);
    });

    it('should return 404 for non-existent customer', async () => {
      await request(app)
        .put('/api/customers/00000000-0000-0000-0000-000000000000')
        .send({ name: 'Test' })
        .expect(404);
    });

    afterAll(async () => {
      await pool.query('DELETE FROM customers WHERE id = $1', [testCustomerId]);
    });
  });

  describe('POST /api/customers/:id/next-stage', () => {
    let testCustomerId: string;

    beforeAll(async () => {
      const result = await pool.query(
        'INSERT INTO customers (name, email, status) VALUES ($1, $2, $3) RETURNING id',
        ['Pipeline Test Customer', `pipelinetest${Date.now()}@example.com`, 'Invited']
      );
      testCustomerId = result.rows[0].id;
    });

    it('should move customer to next pipeline stage', async () => {
      const response = await request(app)
        .post(`/api/customers/${testCustomerId}/next-stage`)
        .expect(200);

      expect(response.body.status).toBe('Qualified');
    });

    it('should return 404 for non-existent customer', async () => {
      await request(app)
        .post('/api/customers/00000000-0000-0000-0000-000000000000/next-stage')
        .expect(404);
    });

    afterAll(async () => {
      await pool.query('DELETE FROM customers WHERE id = $1', [testCustomerId]);
    });
  });

  describe('DELETE /api/customers/:id', () => {
    let testCustomerId: string;

    beforeEach(async () => {
      const result = await pool.query(
        'INSERT INTO customers (name, email, status) VALUES ($1, $2, $3) RETURNING id',
        ['Delete Test Customer', `deletetest${Date.now()}@example.com`, 'Invited']
      );
      testCustomerId = result.rows[0].id;
    });

    it('should delete a customer', async () => {
      await request(app)
        .delete(`/api/customers/${testCustomerId}`)
        .expect(204);

      // Verify customer is deleted
      const result = await pool.query('SELECT * FROM customers WHERE id = $1', [testCustomerId]);
      expect(result.rows.length).toBe(0);
    });

    it('should return 404 for non-existent customer', async () => {
      await request(app)
        .delete('/api/customers/00000000-0000-0000-0000-000000000000')
        .expect(404);
    });
  });
});
