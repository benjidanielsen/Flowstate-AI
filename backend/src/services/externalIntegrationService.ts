import { Kysely, sql } from 'kysely';
import { Database, ExternalIntegration } from '../types';
import logger from '../utils/logger';

export class ExternalIntegrationService {
  constructor(private db: Kysely<Database>) {}

  async createIntegration(integration: Omit<ExternalIntegration, 'id' | 'created_at' | 'updated_at'>): Promise<ExternalIntegration> {
    logger.info('Creating new external integration', { type: integration.type, customerId: integration.customer_id });
    const result = await this.db.insertInto('external_integrations')
      .values({
        ...integration,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      })
      .returningAll()
      .executeTakeFirstOrThrow();
    return result;
  }

  async getIntegrationsByCustomer(customerId: string): Promise<ExternalIntegration[]> {
    logger.info('Fetching external integrations for customer', { customerId });
    return this.db.selectFrom('external_integrations')
      .selectAll()
      .where('customer_id', '=', customerId)
      .execute();
  }

  async updateIntegration(id: string, updates: Partial<Omit<ExternalIntegration, 'id' | 'customer_id' | 'created_at'>>): Promise<ExternalIntegration> {
    logger.info('Updating external integration', { id });
    const result = await this.db.updateTable('external_integrations')
      .set({
        ...updates,
        updated_at: new Date().toISOString(),
      })
      .where('id', '=', id)
      .returningAll()
      .executeTakeFirstOrThrow();
    return result;
  }

  async deleteIntegration(id: string): Promise<void> {
    logger.info('Deleting external integration', { id });
    await this.db.deleteFrom('external_integrations')
      .where('id', '=', id)
      .execute();
  }
}

