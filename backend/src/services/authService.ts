import { v4 as uuidv4 } from 'uuid';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import DatabaseManager from '../database';
import { User } from '../types';
import { PoolClient } from 'pg';

const JWT_SECRET = process.env.JWT_SECRET || 'supersecretjwtkey';

export class AuthService {
  async registerUser(username: string, password_plain: string): Promise<User> {
    let client: PoolClient | null = null;
    try {
      const pool = DatabaseManager.getInstance().getPool();
      client = await pool.connect();
      const hashedPassword = await bcrypt.hash(password_plain, 10);
      const id = uuidv4();
      const now = new Date().toISOString();

      const result = await client.query(
        `INSERT INTO users (id, username, password, created_at, updated_at) VALUES ($1, $2, $3, $4, $5) RETURNING id, username, created_at, updated_at`,
        [id, username, hashedPassword, now, now]
      );
      return result.rows[0];
    } finally {
      if (client) client.release();
    }
  }

  async findUserByUsername(username: string): Promise<User | null> {
    let client: PoolClient | null = null;
    try {
      const pool = DatabaseManager.getInstance().getPool();
      client = await pool.connect();
      const result = await client.query(
        `SELECT id, username, password, created_at, updated_at FROM users WHERE username = $1`,
        [username]
      );
      return result.rows[0] || null;
    } finally {
      if (client) client.release();
    }
  }

  async validateUser(username: string, password_plain: string): Promise<User | null> {
    const user = await this.findUserByUsername(username);
    if (!user) {
      return null;
    }

    const isMatch = await bcrypt.compare(password_plain, (user as any).password);
    if (isMatch) {
      // Remove password hash before returning user object
      const { password: _password, ...userWithoutPassword } = user as any; // eslint-disable-line @typescript-eslint/no-unused-vars
      return userWithoutPassword as User;
    }
    return null;
  }

  generateToken(user: User): string {
    return jwt.sign({ id: user.id, username: user.username }, JWT_SECRET, { expiresIn: '1h' });
  }

  verifyToken(token: string): any {
    try {
      return jwt.verify(token, JWT_SECRET);
    } catch (error) {
      return null;
    }
  }
}

export const authService = new AuthService();

