import { Database, open } from 'sqlite';
import sqlite3 from 'sqlite3';

export async function openDb(filename: string = './data/dev.db'): Promise<Database> {
  const db = await open({ filename, driver: sqlite3.Database });
  await db.exec(`CREATE TABLE IF NOT EXISTS customers (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, stage TEXT, createdAt TEXT)`);
  return db;
}
