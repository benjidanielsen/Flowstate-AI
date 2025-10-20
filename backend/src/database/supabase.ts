import { drizzle } from 'drizzle-orm/node-postgres';
import { Pool } from 'pg';
import { SupabaseClient } from '@supabase/supabase-js';
import * as schema from './schema';
import logger from '../utils/logger';
import DatabaseManager from './index';

let _dbInstance: ReturnType<typeof drizzle> | null = null;
let _supabaseClient: SupabaseClient | null = null;

export function getDbInstance(): ReturnType<typeof drizzle> {
  if (!_dbInstance) {
    let pool: Pool;
    try {
      pool = DatabaseManager.getInstance().getPool();
      _dbInstance = drizzle(pool, { schema });
    } catch (error) {
      logger.error('Failed to get database pool from DatabaseManager:', error);
      throw error; // Re-throw to indicate a critical error
    }
  }
  return _dbInstance;
}

export function getSupabaseClient(): SupabaseClient {
  if (!_supabaseClient) {
    _supabaseClient = DatabaseManager.getInstance().getClient();
  }
  return _supabaseClient;
}

// Test connection function (now uses the pool from DatabaseManager)
export async function testConnection(): Promise<boolean> {
  try {
    const pool = DatabaseManager.getInstance().getPool(); // Get pool when needed
    await pool.query('SELECT 1');
    logger.info('Successfully connected to Supabase database via DatabaseManager pool');
    return true;
  } catch (error) {
    logger.error('Failed to connect to Supabase database via DatabaseManager pool:', error);
    return false;
  }
}

// Export getDbInstance as the default export for convenience
export default getDbInstance;

