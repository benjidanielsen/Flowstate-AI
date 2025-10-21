import { v4 as uuidv4 } from 'uuid';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import { Database } from 'sqlite3';
import DatabaseManager from '../database';
import { User } from '../types';

const JWT_SECRET = process.env.JWT_SECRET || 'supersecretjwtkey';

type UserRecord = User & { password: string };

export class AuthService {
  private dbManager = DatabaseManager.getInstance();

  private async resolveDb(): Promise<Database> {
    try {
      return this.dbManager.getDb();
    } catch (error) {
      // If the connection hasn't been established yet, create it lazily.
      return this.dbManager.connect();
    }
  }

  async registerUser(username: string, password_plain: string): Promise<User> {
    const hashedPassword = await bcrypt.hash(password_plain, 10);
    const id = uuidv4();
    const now = new Date().toISOString();
    const db = await this.resolveDb();

    return new Promise((resolve, reject) => {
      db.run(
        'INSERT INTO users (id, username, password, created_at, updated_at) VALUES (?, ?, ?, ?, ?)',
        [id, username, hashedPassword, now, now],
        function (err) {
          if (err) {
            reject(err);
          } else {
            resolve({ id, username, created_at: new Date(now), updated_at: new Date(now) });
          }
        }
      );
    });
  }

  async findUserByUsername(username: string): Promise<UserRecord | null> {
    const db = await this.resolveDb();

    return new Promise((resolve, reject) => {
      db.get('SELECT * FROM users WHERE username = ?', [username], (err, row: any) => {
        if (err) {
          reject(err);
        } else if (!row) {
          resolve(null);
        } else {
          resolve({
            id: row.id,
            username: row.username,
            password: row.password,
            created_at: new Date(row.created_at),
            updated_at: new Date(row.updated_at)
          });
        }
      });
    });
  }

  async validateUser(username: string, password_plain: string): Promise<User | null> {
    const user = await this.findUserByUsername(username);
    if (!user) {
      return null;
    }

    const isMatch = await bcrypt.compare(password_plain, user.password);
    if (isMatch) {
      const { password: _password, ...userWithoutPassword } = user; // eslint-disable-line @typescript-eslint/no-unused-vars
      return userWithoutPassword;
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

