import { v4 as uuidv4 } from 'uuid';
import DatabaseManager from '../database';
import { Interaction, InteractionType } from '../types';
import { safeLogger } from '../utils/piiRedaction';

export interface CreateInteractionInput {
  customer_id: string;
  type: InteractionType;
  content: string;
  notes?: string;
  scheduled_for?: Date;
  completed?: boolean;
}

export type UpdateInteractionInput = Partial<Pick<Interaction, 'type' | 'content' | 'notes' | 'scheduled_for' | 'completed'>>;

const toBoolean = (value: unknown): boolean => {
  if (typeof value === 'boolean') {
    return value;
  }
  if (typeof value === 'number') {
    return value === 1;
  }
  if (typeof value === 'string') {
    return value === '1' || value.toLowerCase() === 'true';
  }
  return false;
};

const mapRowToInteraction = (row: any): Interaction => {
  const scheduledRaw = row.scheduled_for || row.interaction_date || row.created_at;
  return {
    id: row.id,
    customer_id: row.customer_id,
    type: row.type as InteractionType,
    content: row.summary ?? row.content ?? '',
    notes: row.notes ?? undefined,
    scheduled_for: scheduledRaw ? new Date(scheduledRaw) : new Date(row.created_at),
    completed: toBoolean(row.completed),
    created_at: new Date(row.created_at),
    updated_at: new Date(row.updated_at),
    summary: row.summary ?? undefined,
  };
};

export class InteractionService {
  async createInteraction(input: CreateInteractionInput): Promise<Interaction> {
    const db = DatabaseManager.getInstance().getDb();
    const id = uuidv4();
    const now = new Date();
    const scheduledFor = input.scheduled_for ?? now;
    const completed = input.completed ?? false;

    return new Promise((resolve, reject) => {
      db.run(
        `INSERT INTO interactions (id, customer_id, type, summary, notes, interaction_date, completed, created_at, updated_at)
         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`,
        [
          id,
          input.customer_id,
          input.type,
          input.content,
          input.notes ?? null,
          scheduledFor.toISOString(),
          completed ? 1 : 0,
          now.toISOString(),
          now.toISOString(),
        ],
        (err) => {
          if (err) {
            safeLogger.error('Failed to create interaction', { err, customerId: input.customer_id });
            reject(err);
            return;
          }

          resolve({
            id,
            customer_id: input.customer_id,
            type: input.type,
            content: input.content,
            notes: input.notes,
            scheduled_for: scheduledFor,
            completed,
            created_at: now,
            updated_at: now,
            summary: input.content,
          });
        }
      );
    });
  }

  async getInteractionsByCustomer(customerId: string): Promise<Interaction[]> {
    const db = DatabaseManager.getInstance().getDb();

    return new Promise((resolve, reject) => {
      db.all(
        `SELECT * FROM interactions WHERE customer_id = ? ORDER BY interaction_date DESC`,
        [customerId],
        (err, rows: any[]) => {
          if (err) {
            safeLogger.error('Failed to load interactions for customer', { err, customerId });
            reject(err);
            return;
          }

          const interactions = rows.map(mapRowToInteraction);
          resolve(interactions);
        }
      );
    });
  }

  async getInteractionById(id: string): Promise<Interaction | null> {
    const db = DatabaseManager.getInstance().getDb();

    return new Promise((resolve, reject) => {
      db.get(`SELECT * FROM interactions WHERE id = ?`, [id], (err, row: any) => {
        if (err) {
          safeLogger.error('Failed to load interaction by id', { err, id });
          reject(err);
          return;
        }

        if (!row) {
          resolve(null);
          return;
        }

        resolve(mapRowToInteraction(row));
      });
    });
  }

  async updateInteraction(id: string, updates: UpdateInteractionInput): Promise<Interaction | null> {
    const db = DatabaseManager.getInstance().getDb();
    const fields: string[] = [];
    const values: any[] = [];

    if (updates.type) {
      fields.push('type = ?');
      values.push(updates.type);
    }
    if (typeof updates.content === 'string') {
      fields.push('summary = ?');
      values.push(updates.content);
    }
    if (updates.notes !== undefined) {
      fields.push('notes = ?');
      values.push(updates.notes);
    }
    if (updates.scheduled_for) {
      fields.push('interaction_date = ?');
      values.push(updates.scheduled_for.toISOString());
    }
    if (typeof updates.completed === 'boolean') {
      fields.push('completed = ?');
      values.push(updates.completed ? 1 : 0);
    }

    if (fields.length === 0) {
      return this.getInteractionById(id);
    }

    fields.push('updated_at = ?');
    values.push(new Date().toISOString());
    values.push(id);

    return new Promise((resolve, reject) => {
      db.run(
        `UPDATE interactions SET ${fields.join(', ')} WHERE id = ?`,
        values,
        function (this: { changes: number }, err: Error | null) {
          if (err) {
            safeLogger.error('Failed to update interaction', { err, id });
            reject(err);
            return;
          }

          if (this.changes === 0) {
            resolve(null);
            return;
          }

          db.get(`SELECT * FROM interactions WHERE id = ?`, [id], (selectErr, row: any) => {
            if (selectErr) {
              safeLogger.error('Failed to load interaction after update', { err: selectErr, id });
              reject(selectErr);
              return;
            }

            if (!row) {
              resolve(null);
              return;
            }

            resolve(mapRowToInteraction(row));
          });
        }
      );
    });
  }

  async deleteInteraction(id: string): Promise<void> {
    const db = DatabaseManager.getInstance().getDb();

    return new Promise((resolve, reject) => {
      db.run(`DELETE FROM interactions WHERE id = ?`, [id], (err) => {
        if (err) {
          safeLogger.error('Failed to delete interaction', { err, id });
          reject(err);
          return;
        }

        resolve();
      });
    });
  }
}

export const interactionService = new InteractionService();
export type InteractionServiceInstance = InteractionService;
