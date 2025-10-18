"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.authService = exports.AuthService = void 0;
const uuid_1 = require("uuid");
const bcryptjs_1 = __importDefault(require("bcryptjs"));
const jsonwebtoken_1 = __importDefault(require("jsonwebtoken"));
const database_1 = __importDefault(require("../database"));
const JWT_SECRET = process.env.JWT_SECRET || 'supersecretjwtkey';
class AuthService {
    async registerUser(username, password_plain) {
        let client = null;
        try {
            const pool = database_1.default.getInstance().getPool();
            client = await pool.connect();
            const hashedPassword = await bcryptjs_1.default.hash(password_plain, 10);
            const id = (0, uuid_1.v4)();
            const now = new Date().toISOString();
            const result = await client.query(`INSERT INTO users (id, username, password, created_at, updated_at) VALUES ($1, $2, $3, $4, $5) RETURNING id, username, created_at, updated_at`, [id, username, hashedPassword, now, now]);
            return result.rows[0];
        }
        finally {
            if (client)
                client.release();
        }
    }
    async findUserByUsername(username) {
        let client = null;
        try {
            const pool = database_1.default.getInstance().getPool();
            client = await pool.connect();
            const result = await client.query(`SELECT id, username, password, created_at, updated_at FROM users WHERE username = $1`, [username]);
            return result.rows[0] || null;
        }
        finally {
            if (client)
                client.release();
        }
    }
    async validateUser(username, password_plain) {
        const user = await this.findUserByUsername(username);
        if (!user) {
            return null;
        }
        const isMatch = await bcryptjs_1.default.compare(password_plain, user.password);
        if (isMatch) {
            // Remove password hash before returning user object
            const { password: _password, ...userWithoutPassword } = user; // eslint-disable-line @typescript-eslint/no-unused-vars
            return userWithoutPassword;
        }
        return null;
    }
    generateToken(user) {
        return jsonwebtoken_1.default.sign({ id: user.id, username: user.username }, JWT_SECRET, { expiresIn: '1h' });
    }
    verifyToken(token) {
        try {
            return jsonwebtoken_1.default.verify(token, JWT_SECRET);
        }
        catch (error) {
            return null;
        }
    }
}
exports.AuthService = AuthService;
exports.authService = new AuthService();
//# sourceMappingURL=authService.js.map