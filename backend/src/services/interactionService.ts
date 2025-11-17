import { v4 as uuidv4 } from 'uuid';
import DatabaseManager from '../database';
import { Interaction, InteractionType } from '../types';

type InteractionCreateInput = {
  customer_id: string;
  type: InteractionType;
  summary?: string;
  content?: string;
  notes?: string;
  interaction_date?: Date;
  scheduled_for?: Date | null;
  completed?: boolean;
};

type InteractionUpdateInput = Partial<InteractionCreateInput> & {
  interaction_date?: Date;
};

function mapRowToInteraction(row: any): Interaction {
  return {
    id: row.id,
    customer_id: row.customer_id,
    type: row.type,
    summary: row.summary,
    content: row.content ?? undefined,
    notes: row.notes ?? undefined,
    interaction_date: new Date(row.interaction_date),
    scheduled_for: row.scheduled_for ? new Date(row.scheduled_for) : null,
    completed: Boolean(row.completed),
    created_at: new Date(row.created_at),
    updated_at: new Date(row.updated_at),
  };
}

export const interactionService = {
  async create(interaction: InteractionCreateInput): Promise<Interaction> {
    const db = DatabaseManager.getInstance().getDb();
    const id = uuidv4();
    const now = new Date();
    const interactionDate = interaction.interaction_date ?? now;
    const scheduledFor = interaction.scheduled_for ?? null;

    const summary = (interaction.summary ?? interaction.content ?? '').trim();
    if (!summary) {
      throw new Error('Interaction summary is required');
    }

    const content = interaction.content ?? summary;
    const completed = interaction.completed ?? false;

    return new Promise((resolve, reject) => {
      db.run(
        `INSERT INTO interactions (
          id, customer_id, type, summary, notes, interaction_date, created_at, updated_at, content, scheduled_for, completed
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
        [
          id,
          interaction.customer_id,
          interaction.type,
          summary,
          interaction.notes ?? null,
          interactionDate.toISOString(),
          now.toISOString(),
          now.toISOString(),
          content,
          scheduledFor ? scheduledFor.toISOString() : null,
          completed ? 1 : 0,
        ],
        function(err) {
          if (err) return reject(err);
          resolve({
            id,
            customer_id: interaction.customer_id,
            type: interaction.type,
            summary,
            content,
            notes: interaction.notes,
            interaction_date: interactionDate,
            scheduled_for: scheduledFor,
            completed,
            created_at: now,
            updated_at: now,
          });
        }
      );
    });
  },

  async getByCustomerId(customerId: string): Promise<Interaction[]> {
    const db = DatabaseManager.getInstance().getDb();

    return new Promise((resolve, reject) => {
      db.all(
        `SELECT * FROM interactions WHERE customer_id = ? ORDER BY interaction_date DESC`,
        [customerId],
        (err, rows: any[]) => {
          if (err) return reject(err);
          const interactions = rows.map(mapRowToInteraction);
          resolve(interactions);
        }
      );
    });
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
          resolve(mapRowToInteraction(row));
        }
      );
    });
  },

  async update(id: string, updates: InteractionUpdateInput): Promise<Interaction | undefined> {
    const db = DatabaseManager.getInstance().getDb();
    const now = new Date().toISOString();

    const fields: string[] = [];
    const values: any[] = [];

    if (updates.customer_id) { fields.push('customer_id = ?'); values.push(updates.customer_id); }
    if (updates.type) { fields.push('type = ?'); values.push(updates.type); }
    if (updates.summary !== undefined) { fields.push('summary = ?'); values.push(updates.summary); }
    if (updates.content !== undefined) { fields.push('content = ?'); values.push(updates.content); }
    if (updates.notes !== undefined) { fields.push('notes = ?'); values.push(updates.notes); }
    if (updates.interaction_date) { fields.push('interaction_date = ?'); values.push(updates.interaction_date.toISOString()); }
    if (updates.scheduled_for !== undefined) {
      fields.push('scheduled_for = ?');
      values.push(updates.scheduled_for ? updates.scheduled_for.toISOString() : null);
    }
    if (updates.completed !== undefined) {
      fields.push('completed = ?');
      values.push(updates.completed ? 1 : 0);
    }

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
            resolve(mapRowToInteraction(row));
          });
        }
      );
    });
  },

  async markCompleted(id: string): Promise<Interaction | null> {
    const db = DatabaseManager.getInstance().getDb();
    const now = new Date().toISOString();

    return new Promise((resolve, reject) => {
      db.run(
        `UPDATE interactions SET completed = 1, updated_at = ? WHERE id = ?`,
        [now, id],
        function(err) {
          if (err) return reject(err);
          if (this.changes === 0) return resolve(null);

          db.get(`SELECT * FROM interactions WHERE id = ?`, [id], (err, row: any) => {
            if (err) return reject(err);
            if (!row) return resolve(null);
            resolve(mapRowToInteraction(row));
          });
        }
      );
    });
  },

  async getUpcoming(limit: number = 5): Promise<Interaction[]> {
    const db = DatabaseManager.getInstance().getDb();
    const nowIso = new Date().toISOString();

    return new Promise((resolve, reject) => {
      db.all(
        `SELECT * FROM interactions
         WHERE completed = 0
           AND scheduled_for IS NOT NULL
           AND scheduled_for >= ?
         ORDER BY scheduled_for ASC
         LIMIT ?`,
        [nowIso, limit],
        (err, rows: any[]) => {
          if (err) return reject(err);
          resolve(rows.map(mapRowToInteraction));
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

  async createInteraction(interaction: InteractionCreateInput): Promise<Interaction> {
    return this.create(interaction);
  },

  async getInteractionsByCustomer(customerId: string): Promise<Interaction[]> {
    return this.getByCustomerId(customerId);
  },

  async getInteractionById(id: string): Promise<Interaction | null> {
    const interaction = await this.getById(id);
    return interaction ?? null;
  },

  async updateInteraction(id: string, updates: InteractionUpdateInput): Promise<Interaction | undefined> {
    return this.update(id, updates);
  },

  async deleteInteraction(id: string): Promise<void> {
    await this.delete(id);
  },
};

export class InteractionService {
  async createInteraction(interaction: InteractionCreateInput): Promise<Interaction> {
    return interactionService.createInteraction(interaction);
  }

  async getInteractionsByCustomer(customerId: string): Promise<Interaction[]> {
    return interactionService.getInteractionsByCustomer(customerId);
  }

  async getInteractionById(id: string): Promise<Interaction | null> {
    return interactionService.getInteractionById(id);
  }

  async updateInteraction(id: string, updates: InteractionUpdateInput): Promise<Interaction | undefined> {
    return interactionService.updateInteraction(id, updates);
  }

  async deleteInteraction(id: string): Promise<void> {
    await interactionService.deleteInteraction(id);
  }
}

