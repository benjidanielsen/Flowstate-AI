import { AuthService } from '../services/authService';
import DatabaseManager from '../database';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';

const JWT_SECRET = process.env.JWT_SECRET || 'supersecretjwtkey';

describe('AuthService', () => {
  let authService: AuthService;
  let dbManager: DatabaseManager;

  beforeAll(async () => {
    dbManager = DatabaseManager.getInstance();
    // Use an in-memory database for testing
    process.env.DATABASE_URL = ':memory:';
    await dbManager.connect();
    // Run migrations to create the users table
    await dbManager.getDb().exec(`
      CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
      );
    `);
    authService = new AuthService();
  });

  afterEach(async () => {
    // Clear users table after each test
    await dbManager.getDb().run('DELETE FROM users');
  });

  afterAll(async () => {
    await dbManager.close();
  });

  it('should register a new user', async () => {
    const user = await authService.registerUser('testuser', 'password123');
    expect(user).toBeDefined();
    expect(user.username).toBe('testuser');
    expect(user.id).toBeDefined();
    const foundUser = await authService.findUserByUsername('testuser');
    expect(foundUser).toBeDefined();
    expect(foundUser?.username).toBe('testuser');
  });

  it('should not register a user with an existing username', async () => {
    await authService.registerUser('testuser', 'password123');
    await expect(authService.registerUser('testuser', 'anotherpassword')).rejects.toThrow();
  });

  it('should validate a user with correct credentials', async () => {
    await authService.registerUser('testuser', 'password123');
    const user = await authService.validateUser('testuser', 'password123');
    expect(user).toBeDefined();
    expect(user?.username).toBe('testuser');
    expect((user as any).password).toBeUndefined(); // Password hash should not be returned
  });

  it('should not validate a user with incorrect password', async () => {
    await authService.registerUser('testuser', 'password123');
    const user = await authService.validateUser('testuser', 'wrongpassword');
    expect(user).toBeNull();
  });

  it('should not validate a non-existent user', async () => {
    const user = await authService.validateUser('nonexistent', 'password123');
    expect(user).toBeNull();
  });

  it('should generate a valid JWT token', async () => {
    const user = await authService.registerUser('testuser', 'password123');
    const token = authService.generateToken(user);
    expect(token).toBeDefined();
    const decoded = jwt.verify(token, JWT_SECRET) as any;
    expect(decoded.id).toBe(user.id);
    expect(decoded.username).toBe(user.username);
  });

  it('should verify a valid JWT token', async () => {
    const user = await authService.registerUser('testuser', 'password123');
    const token = authService.generateToken(user);
    const decoded = authService.verifyToken(token);
    expect(decoded).toBeDefined();
    expect(decoded.id).toBe(user.id);
    expect(decoded.username).toBe(user.username);
  });

  it('should not verify an invalid JWT token', () => {
    const invalidToken = 'invalid.token.here';
    const decoded = authService.verifyToken(invalidToken);
    expect(decoded).toBeNull();
  });

  it('should not verify an expired JWT token', async () => {
    const user = await authService.registerUser('testuser', 'password123');
    // Generate a token that expires immediately
    const expiredToken = jwt.sign({ id: user.id, username: user.username }, JWT_SECRET, { expiresIn: '0s' });
    
    // Wait for a short moment to ensure token expires
    await new Promise(resolve => setTimeout(resolve, 100));

    const decoded = authService.verifyToken(expiredToken);
    expect(decoded).toBeNull();
  });
});

