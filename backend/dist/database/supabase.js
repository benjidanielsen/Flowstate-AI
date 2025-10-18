"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.getDbInstance = getDbInstance;
exports.testConnection = testConnection;
const node_postgres_1 = require("drizzle-orm/node-postgres");
const schema = __importStar(require("./schema"));
const logger_1 = __importDefault(require("../utils/logger"));
const index_1 = __importDefault(require("./index"));
let _dbInstance = null;
function getDbInstance() {
    if (!_dbInstance) {
        let pool;
        try {
            pool = index_1.default.getInstance().getPool();
            _dbInstance = (0, node_postgres_1.drizzle)(pool, { schema });
        }
        catch (error) {
            logger_1.default.error('Failed to get database pool from DatabaseManager:', error);
            throw error; // Re-throw to indicate a critical error
        }
    }
    return _dbInstance;
}
// Test connection function (now uses the pool from DatabaseManager)
async function testConnection() {
    try {
        const pool = index_1.default.getInstance().getPool(); // Get pool when needed
        await pool.query('SELECT 1');
        logger_1.default.info('Successfully connected to Supabase database via DatabaseManager pool');
        return true;
    }
    catch (error) {
        logger_1.default.error('Failed to connect to Supabase database via DatabaseManager pool:', error);
        return false;
    }
}
// Export getDbInstance as the default export for convenience
exports.default = getDbInstance;
//# sourceMappingURL=supabase.js.map