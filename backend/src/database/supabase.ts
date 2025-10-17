import { drizzle } from 'drizzle-orm/postgres-js';
import postgres from 'postgres';
import * as schema from './schema';
import logger from '../utils/logger';

// Supabase connection configuration
const connectionString = process.env.DATABASE_URL || '';

if (!connectionString) {
  throw new Error('DATABASE_URL environment variable is not set');
}

// Create postgres client
const client = postgres(connectionString, {
  prepare: false,
  max: 10,
  idle_timeout: 20,
  connect_timeout: 10,
});

// Create drizzle instance
export const db = drizzle(client, { schema });

// Test connection
export async function testConnection(): Promise<boolean> {
  try {
    await client`SELECT 1`;
    logger.info('Successfully connected to Supabase database');
    return true;
  } catch (error) {
    logger.error('Failed to connect to Supabase database:', error);
    return false;
  }
}

export default db;

