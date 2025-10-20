"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const supabase_js_1 = require("@supabase/supabase-js");
const pg_1 = require("pg");
const logger_1 = __importDefault(require("../utils/logger"));
class DatabaseManager {
    constructor() {
        this.pool = null;
        this.supabaseClient = null;
    }
    static getInstance() {
        if (!DatabaseManager.instance) {
            DatabaseManager.instance = new DatabaseManager();
        }
        return DatabaseManager.instance;
    }
    initialiseSupabaseClient() {
        if (this.supabaseClient) {
            return this.supabaseClient;
        }
        const supabaseUrl = process.env.SUPABASE_URL;
        const serviceRoleKey = process.env.SUPABASE_SERVICE_ROLE_KEY ?? process.env.SUPABASE_ANON_KEY;
        if (!supabaseUrl || !serviceRoleKey) {
            logger_1.default.error('Supabase credentials are not configured.');
            throw new Error('SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY (or SUPABASE_ANON_KEY) must be defined.');
        }
        this.supabaseClient = (0, supabase_js_1.createClient)(supabaseUrl, serviceRoleKey, {
            auth: {
                autoRefreshToken: false,
                persistSession: false,
            },
        });
        logger_1.default.info('Supabase client initialised.');
        return this.supabaseClient;
    }
    getClient() {
        return this.initialiseSupabaseClient();
    }
    async connect() {
        if (this.pool) {
            return this.pool;
        }
        // Ensure Supabase client is created so credentials are validated early.
        this.initialiseSupabaseClient();
        const connectionString = process.env.SUPABASE_DB_URL ?? process.env.DATABASE_URL;
        if (!connectionString) {
            logger_1.default.error('No database connection string configured for Supabase.');
            throw new Error('SUPABASE_DB_URL or DATABASE_URL must be defined.');
        }
        try {
            this.pool = new pg_1.Pool({
                connectionString,
                ssl: connectionString.includes('supabase.co')
                    ? { rejectUnauthorized: false }
                    : undefined,
            });
            await this.pool.query('SELECT 1');
            logger_1.default.info('Connected to Supabase PostgreSQL database.');
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