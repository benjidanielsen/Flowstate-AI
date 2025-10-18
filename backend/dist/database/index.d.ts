import { Pool } from 'pg';
declare class DatabaseManager {
    private static instance;
    private pool;
    private constructor();
    static getInstance(): DatabaseManager;
    connect(): Promise<Pool>;
    close(): Promise<void>;
    getPool(): Pool;
}
export default DatabaseManager;
//# sourceMappingURL=index.d.ts.map