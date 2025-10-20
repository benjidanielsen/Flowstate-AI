import { v4 as uuidv4 } from 'uuid';
import DatabaseManager from '../database';
import { Interaction, InteractionType } from '../types';

export type InteractionCreateInput = {
  customer_id: string;
  type: InteractionType;
  summary?: string;
  content?: string;
  notes?: string;
  interaction_date?: Date;
  scheduled_for?: Date | null;
  completed?: boolean;
};

export type InteractionUpdateInput = Partial<InteractionCreateInput> & {
  interaction_date?: Date;
};

const EMAIL_REGEX = /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b/g;
const PHONE_REGEX = /\b\d{3}[-.]?\d{3}[-.]?\d{4}\b/g;
const GENERIC_ID_REGEX = /\b(user_id|customer_id|agent_id):\s*\S+/gi;

function redact(value: string): string {
  return value
    .replace(EMAIL_REGEX, '[REDACTED_EMAIL]')
    .replace(PHONE_REGEX, '[REDACTED_PHONE]')
    .replace(GENERIC_ID_REGEX, '$1: [REDACTED_ID]');
}

function sanitizeSummary(summary?: string, content?: string): string {
  const base = (summary ?? content ?? '').trim();
  if (!base) {
    throw new Error('Interaction summary is required');
  }
  return redact(base);
}

function sanitizeContent(summary: string, content?: string): string {
  const base = (content ?? summary).trim();
  return base ? redact(base) : summary;
}

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

export class InteractionService {
  private getDb() {
    return DatabaseManager.getInstance().getDb();
  }

  async create(interaction: InteractionCreateInput): Promise<Interaction> {
    const db = this.getDb();
    const id = uuidv4();
    const now = new Date();
    const interactionDate = interaction.interaction_date ?? now;
    const scheduledFor = interaction.scheduled_for ?? null;

    const summary = sanitizeSummary(interaction.summary, interaction.content);
    const content = sanitizeContent(summary, interaction.content);
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
  }

  async createInteraction(interaction: InteractionCreateInput): Promise<Interaction> {
    return this.create(interaction);
  }

  async getByCustomerId(customerId: string): Promise<Interaction[]> {
    const db = this.getDb();

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
  }

  async getInteractionsByCustomer(customerId: string): Promise<Interaction[]> {
    return this.getByCustomerId(customerId);
  }

  async getById(id: string): Promise<Interaction | undefined> {
    const db = this.getDb();

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
  }

  async getInteractionById(id: string): Promise<Interaction | null> {
    const interaction = await this.getById(id);
    return interaction ?? null;
  }

  async update(id: string, updates: InteractionUpdateInput): Promise<Interaction | undefined> {
    const db = this.getDb();
    const now = new Date().toISOString();

    const fields: string[] = [];
    const values: any[] = [];

    if (updates.customer_id) { fields.push('customer_id = ?'); values.push(updates.customer_id); }
    if (updates.type) { fields.push('type = ?'); values.push(updates.type); }
    if (updates.summary !== undefined) { fields.push('summary = ?'); values.push(redact(updates.summary)); }
    if (updates.content !== undefined) { fields.push('content = ?'); values.push(updates.content ? redact(updates.content) : null); }
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

          db.get(`SELECT * FROM interactions WHERE id = ?`, [id], (innerErr, row: any) => {
            if (innerErr) return reject(innerErr);
            if (!row) return resolve(undefined);
            resolve(mapRowToInteraction(row));
          });
        }
      );
    });
  }

  async updateInteraction(id: string, updates: InteractionUpdateInput): Promise<Interaction | undefined> {
    return this.update(id, updates);
  }

  async markCompleted(id: string): Promise<Interaction | null> {
    const db = this.getDb();
    const now = new Date().toISOString();

    return new Promise((resolve, reject) => {
      db.run(
        `UPDATE interactions SET completed = 1, updated_at = ? WHERE id = ?`,
        [now, id],
        function(err) {
          if (err) return reject(err);
          if (this.changes === 0) return resolve(null);

          db.get(`SELECT * FROM interactions WHERE id = ?`, [id], (innerErr, row: any) => {
            if (innerErr) return reject(innerErr);
            if (!row) return resolve(null);
            resolve(mapRowToInteraction(row));
          });
        }
      );
    });
  }

  async markInteractionCompleted(id: string): Promise<Interaction | null> {
    return this.markCompleted(id);
  }

  async getUpcoming(limit = 5): Promise<Interaction[]> {
    const db = this.getDb();
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
  }

  async getUpcomingInteractions(limit = 5): Promise<Interaction[]> {
    return this.getUpcoming(limit);
  }

  async delete(id: string): Promise<void> {
    const db = this.getDb();

    return new Promise((resolve, reject) => {
      db.run(`DELETE FROM interactions WHERE id = ?`, [id], function(err) {
        if (err) return reject(err);
        resolve();
      });
    });
  }

  async deleteInteraction(id: string): Promise<void> {
    await this.delete(id);
  }
}

export const interactionService = new InteractionService();

