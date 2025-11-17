import { v4 as uuidv4 } from 'uuid';
import DatabaseManager from '../database';
import { Interaction, InteractionType } from '../types';

type InteractionInput = Omit<Interaction, 'id' | 'created_at' | 'updated_at'> & {
  interaction_date?: Date;
};

type LegacyInteractionInput = {
  customer_id: string;
  type: InteractionType;
  content: string;
  notes?: string;
  scheduled_for?: Date;
  completed?: boolean;
};

export type InteractionRecord = Interaction & {
  /**
   * Legacy alias fields that some tests (and potentially older code paths)
   * still rely on. They map directly to the canonical columns so we simply
   * expose friendly getters without duplicating state.
   */
  content: string;
  scheduled_for: Date;
  completed: boolean;
};

class InteractionService {
  private mapToRecord(row: any): InteractionRecord {
    const interaction: Interaction = {
      id: row.id,
      customer_id: row.customer_id,
      type: row.type,
      summary: row.summary,
      notes: row.notes || undefined,
      interaction_date: new Date(row.interaction_date),
      created_at: new Date(row.created_at),
      updated_at: new Date(row.updated_at)
    };

    return this.withLegacyFields(interaction);
  }

  private withLegacyFields(interaction: Interaction): InteractionRecord {
    return {
      ...interaction,
      content: interaction.summary,
      scheduled_for: interaction.interaction_date,
      completed: false,
    };
  }

  private getDb() {
    return DatabaseManager.getInstance().getDb();
  }

  async create(interaction: InteractionInput): Promise<InteractionRecord> {
    const db = this.getDb();
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
        (err) => {
          if (err) return reject(err);
          resolve(this.withLegacyFields({
            id,
            ...interaction,
            interaction_date: interactionDate,
            created_at: now,
            updated_at: now
          }));
        }
      );
    });
  }

  async createInteraction(interaction: LegacyInteractionInput): Promise<InteractionRecord> {
    return this.create({
      customer_id: interaction.customer_id,
      type: interaction.type,
      summary: interaction.content,
      notes: interaction.notes,
      interaction_date: interaction.scheduled_for ?? new Date(),
    });
  }

  async getByCustomerId(customerId: string): Promise<InteractionRecord[]> {
    const db = this.getDb();

    return new Promise((resolve, reject) => {
      db.all(
        `SELECT * FROM interactions WHERE customer_id = ? ORDER BY interaction_date DESC`,
        [customerId],
        (err, rows: any[]) => {
          if (err) return reject(err);
          resolve(rows.map(row => this.mapToRecord(row)));
        }
      );
    });
  }

  async getInteractionsByCustomer(customerId: string): Promise<InteractionRecord[]> {
    return this.getByCustomerId(customerId);
  }

  async getById(id: string): Promise<InteractionRecord | null> {
    const db = this.getDb();

    return new Promise((resolve, reject) => {
      db.get(
        `SELECT * FROM interactions WHERE id = ?`,
        [id],
        (err, row: any) => {
          if (err) return reject(err);
          if (!row) return resolve(null);
          resolve(this.mapToRecord(row));
        }
      );
    });
  }

  async getInteractionById(id: string): Promise<InteractionRecord | null> {
    return this.getById(id);
  }

  async update(id: string, updates: Partial<Omit<Interaction, 'id' | 'created_at'>> & { interaction_date?: Date }): Promise<InteractionRecord | null> {
    const db = this.getDb();
    const now = new Date().toISOString();
    const mapToRecord = this.mapToRecord.bind(this);

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
          if (this.changes === 0) return resolve(null);

          db.get(`SELECT * FROM interactions WHERE id = ?`, [id], (err, row: any) => {
            if (err) return reject(err);
            if (!row) return resolve(null);
            resolve(mapToRecord(row));
          });
        }
      );
    });
  }

  async updateInteraction(id: string, updates: Partial<LegacyInteractionInput>): Promise<InteractionRecord | null> {
    const mappedUpdates: Partial<Omit<Interaction, 'id' | 'created_at' | 'updated_at'>> & { interaction_date?: Date } = {};
    if (updates.customer_id) mappedUpdates.customer_id = updates.customer_id;
    if (updates.type) mappedUpdates.type = updates.type;
    if (updates.content) mappedUpdates.summary = updates.content;
    if (updates.notes !== undefined) mappedUpdates.notes = updates.notes;
    if (updates.scheduled_for) mappedUpdates.interaction_date = updates.scheduled_for;

    return this.update(id, mappedUpdates);
  }

  async delete(id: string): Promise<void> {
    const db = this.getDb();

    return new Promise((resolve, reject) => {
      db.run(`DELETE FROM interactions WHERE id = ?`, [id], (err) => {
        if (err) return reject(err);
        resolve();
      });
    });
  }

  async deleteInteraction(id: string): Promise<void> {
    return this.delete(id);
  }
}

export const interactionService = new InteractionService();
export { InteractionService };

