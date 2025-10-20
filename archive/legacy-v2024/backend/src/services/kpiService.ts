import DatabaseManager from '../database';
import { PoolClient } from 'pg';
import { v4 as uuidv4 } from 'uuid';
import { KPI } from '../types';

export class KpiService {
  async createKpi(data: {
    name: string;
    value: number;
    unit: string;
    change: number;
    changeType: 'increase' | 'decrease' | 'neutral';
    description: string;
    status: 'success' | 'warning' | 'danger';
    category: string;
  }): Promise<KPI> {
    let client: PoolClient | null = null;
    try {
      const pool = DatabaseManager.getInstance().getPool();
      client = await pool.connect();
      const id = uuidv4();
      const now = new Date().toISOString();
      const result = await client.query(
        `INSERT INTO kpis (id, name, value, unit, change, change_type, description, status, category, created_at, updated_at)
         VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11) RETURNING *`,
        [
          id,
          data.name,
          data.value,
          data.unit,
          data.change,
          data.changeType,
          data.description,
          data.status,
          data.category,
          now,
          now,
        ]
      );
      return result.rows[0];
    } finally {
      if (client) client.release();
    }
  }

  async getKpiById(id: string): Promise<KPI | null> {
    let client: PoolClient | null = null;
    try {
      const pool = DatabaseManager.getInstance().getPool();
      client = await pool.connect();
      const result = await client.query(
        `SELECT * FROM kpis WHERE id = $1`,
        [id]
      );
      return result.rows[0] || null;
    } finally {
      if (client) client.release();
    }
  }

  async getAllKpis(category?: string): Promise<KPI[]> {
    let client: PoolClient | null = null;
    try {
      const pool = DatabaseManager.getInstance().getPool();
      client = await pool.connect();
      let query = `SELECT * FROM kpis`;
      const params: any[] = [];
      if (category) {
        query += ` WHERE category = $1`;
        params.push(category);
      }
      query += ` ORDER BY created_at DESC`;
      const result = await client.query(query, params);
      return result.rows;
    } finally {
      if (client) client.release();
    }
  }

  async updateKpi(id: string, data: Partial<KPI>): Promise<KPI | null> {
    let client: PoolClient | null = null;
    try {
      const pool = DatabaseManager.getInstance().getPool();
      client = await pool.connect();
      const now = new Date().toISOString();
      const fields = Object.keys(data).map((key, index) => `
        ${key} = $${index + 2}
      `).join(', ');
      const values = Object.values(data);

      if (values.length === 0) {
        return this.getKpiById(id);
      }

      const result = await client.query(
        `UPDATE kpis SET ${fields}, updated_at = $${values.length + 2} WHERE id = $1 RETURNING *`,
        [id, ...values, now]
      );
      return result.rows[0] || null;
    } finally {
      if (client) client.release();
    }
  }

  async deleteKpi(id: string): Promise<boolean> {
    let client: PoolClient | null = null;
    try {
      const pool = DatabaseManager.getInstance().getPool();
      client = await pool.connect();
      const result = await client.query(
        `DELETE FROM kpis WHERE id = $1 RETURNING id`,
        [id]
      );
      return result.rowCount !== null && result.rowCount > 0;
    } finally {
      if (client) client.release();
    }
  }
}

export const kpiService = new KpiService();

