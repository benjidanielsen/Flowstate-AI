import { Database } from 'sqlite3';
declare class DatabaseManager {
    private static instance;
    private db;
    private constructor();
    static getInstance(): DatabaseManager;
    connect(): Promise<Database>;
    close(): Promise<void>;
    getDb(): Database;
}
export default DatabaseManager;
//# sourceMappingURL=index.d.ts.map