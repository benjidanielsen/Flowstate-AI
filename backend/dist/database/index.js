"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const sqlite3_1 = __importDefault(require("sqlite3"));
const path_1 = __importDefault(require("path"));
const fs_1 = __importDefault(require("fs"));
class DatabaseManager {
    constructor() {
        this.db = null;
    }
    static getInstance() {
        if (!DatabaseManager.instance) {
            DatabaseManager.instance = new DatabaseManager();
        }
        return DatabaseManager.instance;
    }
    async connect() {
        if (this.db) {
            return this.db;
        }
        const dbPath = process.env.DATABASE_URL || './data/flowstate.db';
        const dataDir = path_1.default.dirname(dbPath);
        // Ensure data directory exists
        if (!fs_1.default.existsSync(dataDir)) {
            fs_1.default.mkdirSync(dataDir, { recursive: true });
        }
        return new Promise((resolve, reject) => {
            this.db = new sqlite3_1.default.Database(dbPath, (err) => {
                if (err) {
                    console.error('Error connecting to database:', err);
                    reject(err);
                }
                else {
                    console.log('Connected to SQLite database');
                    resolve(this.db);
                }
            });
        });
    }
    async close() {
        if (this.db) {
            return new Promise((resolve, reject) => {
                this.db.close((err) => {
                    if (err) {
                        reject(err);
                    }
                    else {
                        this.db = null;
                        resolve();
                    }
                });
            });
        }
    }
    getDb() {
        if (!this.db) {
            throw new Error('Database not connected. Call connect() first.');
        }
        return this.db;
    }
}
exports.default = DatabaseManager;
//# sourceMappingURL=index.js.map