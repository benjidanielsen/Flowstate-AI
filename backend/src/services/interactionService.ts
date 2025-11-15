import { v4 as uuidv4 } from 'uuid';
import DatabaseManager from '../database';
import { Interaction, PaginatedResult } from '../types';

interface InteractionFilters {
  page?: number;
  pageSize?: number;
  type?: string;
  search?: string;
  from?: Date;
  to?: Date;
}

export const interactionService = {
  async create(interaction: Omit<Interaction, 'id' | 'created_at' | 'updated_at'>): Promise<Interaction> {
    const db = DatabaseManager.getInstance().getDb();
    const id = uuidv4();
    const now = new Date();
    const interactionDate = interaction.interaction_date || now;
    
    return new Promise((resolve, reject) => {
      db.run(
        `INSERT INTO interactions (id, customer_id, type, summary, notes, interaction_date, created_at, updated_at) 
         VALUES (?, ?, ?, ?, ?, ?, ?, ?)`,
        [
          id,
          interaction.customer_id,
          interaction.type,
          interaction.summary,
          interaction.notes || null,
          interactionDate.toISOString(),
          now.toISOString(),
          now.toISOString()
        ],
        function(err) {
          if (err) return reject(err);
          resolve({
            id,
            ...interaction,
            interaction_date: interactionDate,
            created_at: now,
            updated_at: now
          });
        }
      );
    });
  },

  async getByCustomerId(customerId: string, filters: InteractionFilters = {}): Promise<PaginatedResult<Interaction>> {
    const manager = DatabaseManager.getInstance();
    const pool = await manager.connect();
    const clauses = ['customer_id = $1'];
    const params: any[] = [customerId];
    let idx = 2;

    if (filters.type) {
      clauses.push(`type = $${idx++}`);
      params.push(filters.type);
    }
    if (filters.from) {
      clauses.push(`interaction_date >= $${idx++}`);
      params.push(filters.from.toISOString());
    }
    if (filters.to) {
      clauses.push(`interaction_date <= $${idx++}`);
      params.push(filters.to.toISOString());
    }
    if (filters.search) {
      const search = `%${filters.search.toLowerCase()}%`;
      clauses.push(`(LOWER(summary) LIKE $${idx} OR LOWER(notes) LIKE $${idx + 1})`);
      params.push(search, search);
      idx += 2;
    }

    const whereClause = `WHERE ${clauses.join(' AND ')}`;
    const page = Math.max(filters.page || 1, 1);
    const rawPageSize = filters.pageSize || 25;
    const pageSize = Math.min(Math.max(rawPageSize, 1), 100);
    const offset = (page - 1) * pageSize;

    const totalResult = await pool.query<{ count: number }>(
      `SELECT COUNT(*)::BIGINT AS count FROM interactions ${whereClause}`,
      params
    );
    const total = Number(totalResult.rows[0]?.count || 0);

    const dataResult = await pool.query(
      `SELECT * FROM interactions ${whereClause} ORDER BY interaction_date DESC LIMIT $${idx} OFFSET $${idx + 1}`,
      [...params, pageSize, offset]
    );
    const interactions = dataResult.rows.map(row => this.mapInteractionRow(row));

    return {
      data: interactions,
      meta: {
        page,
        pageSize,
        total,
        hasMore: offset + interactions.length < total,
      },
    };
  },

  async getById(id: string): Promise<Interaction | undefined> {
    const db = DatabaseManager.getInstance().getDb();
    
    return new Promise((resolve, reject) => {
      db.get(
        `SELECT * FROM interactions WHERE id = ?`,
        [id],
        (err, row: any) => {
          if (err) return reject(err);
          if (!row) return resolve(undefined);
          resolve(this.mapInteractionRow(row));
        }
      );
    });
  },

  async update(id: string, updates: Partial<Omit<Interaction, 'id' | 'created_at'>>): Promise<Interaction | undefined> {
    const db = DatabaseManager.getInstance().getDb();
    const now = new Date().toISOString();
    
    const fields: string[] = [];
    const values: any[] = [];
    
    if (updates.customer_id) { fields.push('customer_id = ?'); values.push(updates.customer_id); }
    if (updates.type) { fields.push('type = ?'); values.push(updates.type); }
    if (updates.summary) { fields.push('summary = ?'); values.push(updates.summary); }
    if (updates.notes !== undefined) { fields.push('notes = ?'); values.push(updates.notes); }
    if (updates.interaction_date) { fields.push('interaction_date = ?'); values.push(updates.interaction_date.toISOString()); }
    
    fields.push('updated_at = ?');
    values.push(now);
    values.push(id);
    
    if (fields.length === 1) { // Only updated_at
      return this.getById(id);
    }
    
    return new Promise((resolve, reject) => {
      db.run(
        `UPDATE interactions SET ${fields.join(', ')} WHERE id = ?`,
        values,
        function(err) {
          if (err) return reject(err);
          if (this.changes === 0) return resolve(undefined);
          
          db.get(`SELECT * FROM interactions WHERE id = ?`, [id], (err, row: any) => {
            if (err) return reject(err);
            if (!row) return resolve(undefined);
            resolve(this.mapInteractionRow(row));
          });
        }
      );
    });
  },

  async delete(id: string): Promise<void> {
    const db = DatabaseManager.getInstance().getDb();

    return new Promise((resolve, reject) => {
      db.run(`DELETE FROM interactions WHERE id = ?`, [id], function(err) {
        if (err) return reject(err);
        resolve();
      });
    });
  },

  mapInteractionRow(row: any): Interaction {
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
  }
};

