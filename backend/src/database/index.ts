import { createClient, SupabaseClient } from '@supabase/supabase-js';
import { Pool } from 'pg';
import logger from '../utils/logger';

class DatabaseManager {
  private static instance: DatabaseManager;
  private pool: Pool | null = null;
  private supabaseClient: SupabaseClient | null = null;

  private constructor() {}

  public static getInstance(): DatabaseManager {
    if (!DatabaseManager.instance) {
      DatabaseManager.instance = new DatabaseManager();
    }
    return DatabaseManager.instance;
  }

  private initialiseSupabaseClient(): SupabaseClient {
    if (this.supabaseClient) {
      return this.supabaseClient;
    }

    const supabaseUrl = process.env.SUPABASE_URL;
    const serviceRoleKey = process.env.SUPABASE_SERVICE_ROLE_KEY ?? process.env.SUPABASE_ANON_KEY;

    if (!supabaseUrl || !serviceRoleKey) {
      logger.error('Supabase credentials are not configured.');
      throw new Error('SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY (or SUPABASE_ANON_KEY) must be defined.');
    }

    this.supabaseClient = createClient(supabaseUrl, serviceRoleKey, {
      auth: {
        autoRefreshToken: false,
        persistSession: false,
      },
    });

    logger.info('Supabase client initialised.');

    return this.supabaseClient;
  }

  public getClient(): SupabaseClient {
    return this.initialiseSupabaseClient();
  }

  public async connect(): Promise<Pool> {
    if (this.pool) {
      return this.pool;
    }

    // Ensure Supabase client is created so credentials are validated early.
    this.initialiseSupabaseClient();

    const connectionString = process.env.SUPABASE_DB_URL ?? process.env.DATABASE_URL;

    if (!connectionString) {
      logger.error('No database connection string configured for Supabase.');
      throw new Error('SUPABASE_DB_URL or DATABASE_URL must be defined.');
    }

    try {
      this.pool = new Pool({
        connectionString,
        ssl: connectionString.includes('supabase.co')
          ? { rejectUnauthorized: false }
          : undefined,
      });
      await this.pool.query('SELECT 1');
      logger.info('Connected to Supabase PostgreSQL database.');
      return this.pool;
    } catch (error) {
      logger.error('Error connecting to Supabase database:', error);
      throw error;
    }
  }

  public async close(): Promise<void> {
    if (this.pool) {
      try {
        await this.pool.end();
        this.pool = null;
        logger.info('Supabase PostgreSQL database connection pool closed.');
      } catch (error) {
        logger.error('Error closing Supabase database connection pool:', error);
        throw error;
      }
    }
  }

  public getPool(): Pool {
    if (!this.pool) {
      throw new Error('Database not connected. Call connect() first.');
    }
    return this.pool;
  }
}

export default DatabaseManager;
