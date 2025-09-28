import DatabaseManager from '../database';
import { Interaction, InteractionType } from '../types';
import { v4 as uuidv4 } from 'uuid';
import { EventLogService } from './eventLogService';

export class InteractionService {
  private eventLogService: EventLogService;

  constructor() {
    this.eventLogService = new EventLogService();
  }

  async getInteractionsByCustomer(customerId: string): Promise<Interaction[]> {
    const db = DatabaseManager.getInstance().getDb();
    
    return new Promise((resolve, reject) => {
      db.all(`
        SELECT * FROM interactions 
        WHERE customer_id = ? 
        ORDER BY created_at DESC
      `, [customerId], (err, rows: any[]) => {
        if (err) {
          reject(err);
        } else {
          const interactions = rows.map(row => ({
            ...row,
            created_at: new Date(row.created_at),
            scheduled_for: row.scheduled_for ? new Date(row.scheduled_for) : undefined,
            completed: Boolean(row.completed)
          }));
          resolve(interactions);
        }
      });
    });
  }

  async createInteraction(interactionData: Omit<Interaction, 'id' | 'created_at'>): Promise<Interaction> {
    const db = DatabaseManager.getInstance().getDb();
    const id = uuidv4();
    const now = new Date();

    const interaction: Interaction = {
      id,
      ...interactionData,
      created_at: now
    };

    return new Promise((resolve, reject) => {
      const stmt = db.prepare(`
        INSERT INTO interactions (id, customer_id, type, content, created_at, scheduled_for, completed)
        VALUES (?, ?, ?, ?, ?, ?, ?)
      `);

      stmt.run([
        interaction.id,
        interaction.customer_id,
        interaction.type,
        interaction.content,
        interaction.created_at.toISOString(),
        interaction.scheduled_for?.toISOString(),
        interaction.completed ? 1 : 0
      ], function(err) {
        if (err) {
          reject(err);
        } else {
          // Log event
          this.eventLogService.logEvent('interaction_created', {
            interaction_id: interaction.id,
            customer_id: interaction.customer_id,
            type: interaction.type
          }, interaction.customer_id);

          resolve(interaction);
        }
      });

      stmt.finalize();
    });
  }

  async updateInteraction(id: string, updates: Partial<Interaction>): Promise<Interaction | null> {
    const db = DatabaseManager.getInstance().getDb();
    
    // First get the existing interaction
    const existing = await this.getInteractionById(id);
    if (!existing) {
      return null;
    }

    const updated = { ...existing, ...updates };

    return new Promise((resolve, reject) => {
      const stmt = db.prepare(`
        UPDATE interactions 
        SET type = ?, content = ?, scheduled_for = ?, completed = ?
        WHERE id = ?
      `);

      stmt.run([
        updated.type,
        updated.content,
        updated.scheduled_for?.toISOString(),
        updated.completed ? 1 : 0,
        id
      ], function(err) {
        if (err) {
          reject(err);
        } else {
          resolve(updated);
        }
      });

      stmt.finalize();
    });
  }

  async getInteractionById(id: string): Promise<Interaction | null> {
    const db = DatabaseManager.getInstance().getDb();
    
    return new Promise((resolve, reject) => {
      db.get('SELECT * FROM interactions WHERE id = ?', [id], (err, row: any) => {
        if (err) {
          reject(err);
        } else if (!row) {
          resolve(null);
        } else {
          const interaction = {
            ...row,
            created_at: new Date(row.created_at),
            scheduled_for: row.scheduled_for ? new Date(row.scheduled_for) : undefined,
            completed: Boolean(row.completed)
          };
          resolve(interaction);
        }
      });
    });
  }

  async deleteInteraction(id: string): Promise<boolean> {
    const db = DatabaseManager.getInstance().getDb();
    
    return new Promise((resolve, reject) => {
      db.run('DELETE FROM interactions WHERE id = ?', [id], function(err) {
        if (err) {
          reject(err);
        } else {
          resolve(this.changes > 0);
        }
      });
    });
  }

  async getUpcomingInteractions(limit: number = 20): Promise<Interaction[]> {
    const db = DatabaseManager.getInstance().getDb();
    const now = new Date().toISOString();
    
    return new Promise((resolve, reject) => {
      db.all(`
        SELECT * FROM interactions 
        WHERE scheduled_for > ? AND completed = 0
        ORDER BY scheduled_for ASC 
        LIMIT ?
      `, [now, limit], (err, rows: any[]) => {
        if (err) {
          reject(err);
        } else {
          const interactions = rows.map(row => ({
            ...row,
            created_at: new Date(row.created_at),
            scheduled_for: row.scheduled_for ? new Date(row.scheduled_for) : undefined,
            completed: Boolean(row.completed)
          }));
          resolve(interactions);
        }
      });
    });
  }
}