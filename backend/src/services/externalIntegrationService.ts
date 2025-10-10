import { ExternalIntegration } from '../types';
import logger from '../utils/logger';
import DatabaseManager from '../database';
import { v4 as uuidv4 } from 'uuid';

export class ExternalIntegrationService {
  async createIntegration(integration: Omit<ExternalIntegration, 'id' | 'created_at' | 'updated_at'>): Promise<ExternalIntegration> {
    const db = DatabaseManager.getInstance().getDb();
    const id = uuidv4();
    const now = new Date().toISOString();
    
    logger.info('Creating new external integration', { type: integration.type, customerId: integration.customer_id });
    
    return new Promise((resolve, reject) => {
      db.run(
        `INSERT INTO external_integrations (id, customer_id, type, config, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)`,
        [id, integration.customer_id, integration.type, integration.config, now, now],
        function(err) {
          if (err) return reject(err);
          resolve({
            id,
            ...integration,
            created_at: new Date(now),
            updated_at: new Date(now)
          });
        }
      );
    });
  }

  async getIntegrationsByCustomer(customerId: string): Promise<ExternalIntegration[]> {
    const db = DatabaseManager.getInstance().getDb();
    logger.info('Fetching external integrations for customer', { customerId });
    
    return new Promise((resolve, reject) => {
      db.all(
        `SELECT * FROM external_integrations WHERE customer_id = ?`,
        [customerId],
        (err, rows: any[]) => {
          if (err) return reject(err);
          const integrations = rows.map(row => ({
            id: row.id,
            customer_id: row.customer_id,
            type: row.type,
            config: row.config,
            created_at: new Date(row.created_at),
            updated_at: new Date(row.updated_at)
          }));
          resolve(integrations);
        }
      );
    });
  }

  async updateIntegration(id: string, updates: Partial<Omit<ExternalIntegration, 'id' | 'customer_id' | 'created_at'>>): Promise<ExternalIntegration> {
    const db = DatabaseManager.getInstance().getDb();
    const now = new Date().toISOString();
    
    logger.info('Updating external integration', { id });
    
    const fields: string[] = [];
    const values: any[] = [];
    
    if (updates.type) { fields.push('type = ?'); values.push(updates.type); }
    if (updates.config) { fields.push('config = ?'); values.push(updates.config); }
    
    fields.push('updated_at = ?');
    values.push(now);
    values.push(id);
    
    return new Promise((resolve, reject) => {
      db.run(
        `UPDATE external_integrations SET ${fields.join(', ')} WHERE id = ?`,
        values,
        function(err) {
          if (err) return reject(err);
          db.get(`SELECT * FROM external_integrations WHERE id = ?`, [id], (err, row: any) => {
            if (err) return reject(err);
            if (row) {
              resolve({
                id: row.id,
                customer_id: row.customer_id,
                type: row.type,
                config: row.config,
                created_at: new Date(row.created_at),
                updated_at: new Date(row.updated_at)
              });
            } else {
              reject(new Error('Integration not found after update'));
            }
          });
        }
      );
    });
  }

  async deleteIntegration(id: string): Promise<void> {
    const db = DatabaseManager.getInstance().getDb();
    logger.info('Deleting external integration', { id });
    
    return new Promise((resolve, reject) => {
      db.run(`DELETE FROM external_integrations WHERE id = ?`, [id], function(err) {
        if (err) return reject(err);
        resolve();
      });
    });
  }
}

