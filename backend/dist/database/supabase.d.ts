import { drizzle } from 'drizzle-orm/node-postgres';
export declare function getDbInstance(): ReturnType<typeof drizzle>;
export declare function testConnection(): Promise<boolean>;
export default getDbInstance;
//# sourceMappingURL=supabase.d.ts.map