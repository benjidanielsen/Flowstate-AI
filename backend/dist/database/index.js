"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const pg_1 = require("pg");
const logger_1 = __importDefault(require("../utils/logger"));
class DatabaseManager {
    constructor() {
        this.pool = null;
    }
    static getInstance() {
        if (!DatabaseManager.instance) {
            DatabaseManager.instance = new DatabaseManager();
        }
        return DatabaseManager.instance;
    }
    async connect() {
        if (this.pool) {
            return this.pool;
        }
        const connectionString = process.env.DATABASE_URL;
        if (!connectionString) {
            logger_1.default.error('DATABASE_URL is not defined in environment variables.');
            throw new Error('DATABASE_URL is not defined.');
        }
        try {
            this.pool = new pg_1.Pool({
                connectionString,
                // You might want to add more pool options here, e.g., max, idleTimeoutMillis
            });
            await this.pool.query('SELECT 1'); // Test connection
            logger_1.default.info('Connected to Supabase PostgreSQL database');
            return this.pool;
        }
        catch (error) {
            logger_1.default.error('Error connecting to Supabase database:', error);
            throw error;
        }
    }
    async close() {
        if (this.pool) {
            try {
                await this.pool.end();
                this.pool = null;
                logger_1.default.info('Supabase PostgreSQL database connection pool closed.');
            }
            catch (error) {
                logger_1.default.error('Error closing Supabase database connection pool:', error);
                throw error;
            }
        }
    }
    getPool() {
        if (!this.pool) {
            throw new Error('Database not connected. Call connect() first.');
        }
        return this.pool;
    }
}
exports.default = DatabaseManager;
//# sourceMappingURL=index.js.map