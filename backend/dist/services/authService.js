"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.AuthService = void 0;
const uuid_1 = require("uuid");
const bcryptjs_1 = __importDefault(require("bcryptjs"));
const jsonwebtoken_1 = __importDefault(require("jsonwebtoken"));
const database_1 = __importDefault(require("../database"));
const JWT_SECRET = process.env.JWT_SECRET || 'supersecretjwtkey';
class AuthService {
    constructor() {
        this.db = database_1.default.getInstance().getDb();
    }
    async registerUser(username, password_plain) {
        const hashedPassword = await bcryptjs_1.default.hash(password_plain, 10);
        const id = (0, uuid_1.v4)();
        const now = new Date().toISOString();
        return new Promise((resolve, reject) => {
            this.db.run('INSERT INTO users (id, username, password, created_at, updated_at) VALUES (?, ?, ?, ?, ?)', [id, username, hashedPassword, now, now], function (err) {
                if (err) {
                    reject(err);
                }
                else {
                    resolve({ id, username, created_at: new Date(now), updated_at: new Date(now) });
                }
            });
        });
    }
    async findUserByUsername(username) {
        return new Promise((resolve, reject) => {
            this.db.get('SELECT * FROM users WHERE username = ?', [username], (err, row) => {
                if (err) {
                    reject(err);
                }
                else if (!row) {
                    resolve(null);
                }
                else {
                    resolve({ ...row, created_at: new Date(row.created_at), updated_at: new Date(row.updated_at) });
                }
            });
        });
    }
    async validateUser(username, password_plain) {
        const user = await this.findUserByUsername(username);
        if (!user) {
            return null;
        }
        // Assuming password field is named 'password' in the database
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
//# sourceMappingURL=authService.js.map