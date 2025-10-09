import { v4 as uuidv4 } from 'uuid';
import DatabaseManager from '../database';
import { Interaction } from '../types';

export const interactionService = {
  async create(interaction: Omit<Interaction, 'id' | 'created_at' | 'updated_at'>): Promise<Interaction> {
    const db = await DatabaseManager.getInstance().connect();
    const newInteraction: Interaction = {
      id: uuidv4(),
      ...interaction,
      interaction_date: interaction.interaction_date || new Date(),
      created_at: new Date(),
      updated_at: new Date(),
    };
    await db.insertInto("interactions").values({
      id: newInteraction.id,
      customer_id: newInteraction.customer_id,
      type: newInteraction.type,
      summary: newInteraction.summary,
      notes: newInteraction.notes,
      interaction_date: newInteraction.interaction_date.toISOString(),
      created_at: newInteraction.created_at.toISOString(),
      updated_at: newInteraction.updated_at.toISOString(),
    }).execute();
    return newInteraction;
  },

  async getByCustomerId(customerId: string): Promise<Interaction[]> {
    const db = await DatabaseManager.getInstance().connect();
    const rows = await db.selectFrom("interactions").selectAll().where("customer_id", "=", customerId).execute();
    return rows.map(row => ({
      ...row,
      interaction_date: new Date(row.interaction_date),
      created_at: new Date(row.created_at),
      updated_at: new Date(row.updated_at),
    }));
  },

  async getById(id: string): Promise<Interaction | undefined> {
    const db = await DatabaseManager.getInstance().connect();
    const row = await db.selectFrom("interactions").selectAll().where("id", "=", id).executeTakeFirst();
    if (!row) return undefined;
    return {
      ...row,
      interaction_date: new Date(row.interaction_date),
      created_at: new Date(row.created_at),
      updated_at: new Date(row.updated_at),
    };
  },

  async update(id: string, updates: Partial<Omit<Interaction, 'id' | 'created_at'>>): Promise<Interaction | undefined> {
    const db = await DatabaseManager.getInstance().connect();
    const updated = await db.updateTable("interactions").set({
      ...updates,
      interaction_date: updates.interaction_date ? updates.interaction_date.toISOString() : undefined,
      updated_at: new Date().toISOString(),
    }).where("id", "=", id).returningAll().executeTakeFirst();
    if (!updated) return undefined;
    return {
      ...updated,
      interaction_date: new Date(updated.interaction_date),
      created_at: new Date(updated.created_at),
      updated_at: new Date(updated.updated_at),
    };
  },

  async delete(id: string): Promise<void> {
    const db = await DatabaseManager.getInstance().connect();
    await db.deleteFrom("interactions").where("id", "=", id).execute();
  },
};
