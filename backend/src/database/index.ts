import { Pool } from 'pg';
import logger from '../utils/logger';

class DatabaseManager {
  private static instance: DatabaseManager;
  private pool: Pool | null = null;

  private constructor() {}

  public static getInstance(): DatabaseManager {
    if (!DatabaseManager.instance) {
      DatabaseManager.instance = new DatabaseManager();
    }
    return DatabaseManager.instance;
  }

  public async connect(): Promise<Pool> {
    if (this.pool) {
      return this.pool;
    }

    const connectionString = process.env.DATABASE_URL;

    if (!connectionString) {
      logger.error('DATABASE_URL is not defined in environment variables.');
      throw new Error('DATABASE_URL is not defined.');
    }

    try {
      this.pool = new Pool({
        connectionString,
        // Supabase instances require TLS; allow self-signed certificates when running locally.
        ssl: { rejectUnauthorized: false },
        // You might want to add more pool options here, e.g., max, idleTimeoutMillis
      });
      await this.pool.query('SELECT 1'); // Test connection
      logger.info('Connected to Supabase PostgreSQL database');
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
