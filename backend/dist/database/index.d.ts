import { SupabaseClient } from '@supabase/supabase-js';
import { Pool } from 'pg';
declare class DatabaseManager {
    private static instance;
    private pool;
    private supabaseClient;
    private constructor();
    static getInstance(): DatabaseManager;
    private initialiseSupabaseClient;
    getClient(): SupabaseClient;
    connect(): Promise<Pool>;
    close(): Promise<void>;
    getPool(): Pool;
}
export default DatabaseManager;
//# sourceMappingURL=index.d.ts.map