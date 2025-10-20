import { v4 as uuidv4 } from 'uuid';
import DatabaseManager from '../database';
import { Interaction, InteractionType } from '../types';
import { PoolClient } from 'pg';
import { EventLogService } from './eventLogService';

export class InteractionService {
  private eventLogService: EventLogService;

  constructor() {
    this.eventLogService = new EventLogService();
  }

  async create(interaction: Omit<Interaction, 'id' | 'created_at' | 'updated_at'>): Promise<Interaction> {
    let client: PoolClient | null = null;
    try {
      const pool = DatabaseManager.getInstance().getPool();
      client = await pool.connect();
      const id = uuidv4();
      const now = new Date();
      const interactionDate = interaction.interaction_date || now;

      const result = await client.query(
        `INSERT INTO interactions (id, customer_id, type, summary, notes, interaction_date, created_at, updated_at)
         VALUES ($1, $2, $3, $4, $5, $6, $7, $8) RETURNING *`,
        [
          id,
          interaction.customer_id,
          interaction.type,
          interaction.summary,
          interaction.notes || null,
          interactionDate.toISOString(),
          now.toISOString(),
          now.toISOString()
        ]
      );
      this.eventLogService.logEvent('interaction_created', { interaction_id: id, customer_id: interaction.customer_id, type: interaction.type }, interaction.customer_id);
      return result.rows[0];
    } finally {
      if (client) client.release();
    }
  }

  async getByCustomerId(customerId: string): Promise<Interaction[]> {
    let client: PoolClient | null = null;
    try {
      const pool = DatabaseManager.getInstance().getPool();
      client = await pool.connect();

      const result = await client.query(
        `SELECT * FROM interactions WHERE customer_id = $1 ORDER BY interaction_date DESC`,
        [customerId]
      );
      return result.rows.map(row => ({
        id: row.id,
        customer_id: row.customer_id,
        type: row.type,
        summary: row.summary,
        notes: row.notes,
        interaction_date: new Date(row.interaction_date),
        created_at: new Date(row.created_at),
        updated_at: new Date(row.updated_at)
      }));
    } finally {
      if (client) client.release();
    }
  }

  async getById(id: string): Promise<Interaction | undefined> {
    let client: PoolClient | null = null;
    try {
      const pool = DatabaseManager.getInstance().getPool();
      client = await pool.connect();

      const result = await client.query(
        `SELECT * FROM interactions WHERE id = $1`,
        [id]
      );
      const row = result.rows[0];
      if (!row) return undefined;
      return {
        id: row.id,
        customer_id: row.customer_id,
        type: row.type,
        summary: row.summary,
        notes: row.notes,
        interaction_date: new Date(row.interaction_date),
        created_at: new Date(row.created_at),
        updated_at: new Date(row.updated_at)
      };
    } finally {
      if (client) client.release();
    }
  }

  async update(id: string, updates: Partial<Omit<Interaction, 'id' | 'created_at'>>): Promise<Interaction | undefined> {
    let client: PoolClient | null = null;
    try {
      const pool = DatabaseManager.getInstance().getPool();
      client = await pool.connect();
      const now = new Date().toISOString();

      const fields: string[] = [];
      const values: any[] = [];

      if (updates.customer_id) { fields.push('customer_id = $' + (fields.length + 1)); values.push(updates.customer_id); }
      if (updates.type) { fields.push('type = $' + (fields.length + 1)); values.push(updates.type); }
      if (updates.summary) { fields.push('summary = $' + (fields.length + 1)); values.push(updates.summary); }
      if (updates.notes !== undefined) { fields.push('notes = $' + (fields.length + 1)); values.push(updates.notes); }
      if (updates.interaction_date) { fields.push('interaction_date = $' + (fields.length + 1)); values.push(updates.interaction_date.toISOString()); }

      if (fields.length === 0) { // Only updated_at
        return this.getById(id);
      }

      fields.push('updated_at = $' + (fields.length + 1));
      values.push(now);
      values.push(id);

      const result = await client.query(
        `UPDATE interactions SET ${fields.join(', ')} WHERE id = $${values.length} RETURNING *`,
        values
      );
      this.eventLogService.logEvent('interaction_updated', { interaction_id: id, updated_fields: Object.keys(updates) }, result.rows[0]?.customer_id);
      return result.rows[0] || undefined;
    } finally {
      if (client) client.release();
    }
  }

  async delete(id: string): Promise<boolean> {
    let client: PoolClient | null = null;
    try {
      const pool = DatabaseManager.getInstance().getPool();
      client = await pool.connect();
      const result = await client.query(
        `DELETE FROM interactions WHERE id = $1 RETURNING customer_id`,
        [id]
      );
      if (result.rowCount !== null && result.rowCount > 0) {
        this.eventLogService.logEvent('interaction_deleted', { interaction_id: id }, result.rows[0].customer_id);
        return true;
      }
      return false;
    } finally {
      if (client) client.release();
    }
  }

  async getAllInteractions(): Promise<Interaction[]> {
    let client: PoolClient | null = null;
    try {
      const pool = DatabaseManager.getInstance().getPool();
      client = await pool.connect();
      const result = await client.query(
        `SELECT * FROM interactions ORDER BY timestamp DESC`
      );
      return result.rows.map(row => ({
        id: row.id,
        customer_id: row.customer_id,
        type: row.type,
        summary: row.summary,
        notes: row.notes,
        interaction_date: new Date(row.interaction_date),
        created_at: new Date(row.created_at),
        updated_at: new Date(row.updated_at)
      }));
    } finally {
      if (client) client.release();
    }
  }

  async getInteractionSummaryByType(): Promise<Record<InteractionType, number>> {
    let client: PoolClient | null = null;
    try {
      const pool = DatabaseManager.getInstance().getPool();
      client = await pool.connect();
      const result = await client.query(
        `SELECT type, COUNT(*) as count FROM interactions GROUP BY type`
      );
      return result.rows.reduce((acc, row) => ({
        ...acc,
        [row.type]: parseInt(row.count, 10),
      }), {} as Record<InteractionType, number>);
    } finally {
      if (client) client.release();
    }
  }
}

export const interactionService = new InteractionService();

