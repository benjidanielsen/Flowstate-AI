import { v4 as uuidv4 } from 'uuid';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import DatabaseManager from '../database';
import { User } from '../types';
import { getActiveJwtSecret } from '../middleware/authMiddleware';

export class AuthService {
  private db = DatabaseManager.getInstance().getDb();

  async registerUser(username: string, password_plain: string, role: string = process.env.DEFAULT_USER_ROLE || 'agent'): Promise<User> {
    const hashedPassword = await bcrypt.hash(password_plain, 10);
    const id = uuidv4();
    const now = new Date().toISOString();

    return new Promise((resolve, reject) => {
      this.db.run(
        'INSERT INTO users (id, username, password, role, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)',
        [id, username, hashedPassword, role, now, now],
        function (err) {
          if (err) {
            reject(err);
          } else {
            resolve({ id, username, role, created_at: new Date(now), updated_at: new Date(now) });
          }
        }
      );
    });
  }

  async findUserByUsername(username: string): Promise<User | null> {
    return new Promise((resolve, reject) => {
      this.db.get('SELECT * FROM users WHERE username = ?', [username], (err, row: any) => {
        if (err) {
          reject(err);
        } else if (!row) {
          resolve(null);
        } else {
          resolve({ ...row, created_at: new Date(row.created_at), updated_at: new Date(row.updated_at) });
        }
      });
    });
  }

  async validateUser(username: string, password_plain: string): Promise<User | null> {
    const user = await this.findUserByUsername(username);
    if (!user) {
      return null;
    }

    // Assuming password field is named 'password' in the database
    const isMatch = await bcrypt.compare(password_plain, (user as any).password);
    if (isMatch) {
      const { password: _password, ...userWithoutPassword } = user as any; // eslint-disable-line @typescript-eslint/no-unused-vars
      return userWithoutPassword as User;
    }
    return null;
  }

  generateToken(user: User): string {
    const roles = (user as any).roles || (user.role ? [user.role] : ['agent']);
    return jwt.sign(
      { id: user.id, username: user.username, roles, provider: 'internal' },
      getActiveJwtSecret(),
      {
        expiresIn: process.env.JWT_TTL || '1h',
        issuer: process.env.JWT_ISSUER || 'flowstate-backend',
        audience: process.env.JWT_AUDIENCE || 'flowstate-clients',
      }
    );
  }

  verifyToken(token: string): any {
    try {
      return jwt.verify(token, getActiveJwtSecret());
    } catch (error) {
      return null;
    }
  }
}

