import { Pool, PoolConfig, QueryResult, types } from 'pg';
import { safeLogger } from '../utils/piiRedaction';

// Parse BIGINT/NUMERIC as numbers
const parseInteger = (value: string) => (value === null ? null : parseInt(value, 10));
const parseFloatValue = (value: string) => (value === null ? null : parseFloat(value));
types.setTypeParser(20, parseInteger as any); // int8
types.setTypeParser(1700, parseFloatValue as any); // numeric

type Callback<T = void> = (err: Error | null, result?: T) => void;

type QueryOptions = {
  text: string;
  values?: any[];
};

class PreparedStatement {
  constructor(private adapter: DatabaseAdapter, private sql: string) {}

  run(params: any[], callback: Callback = () => undefined) {
    this.adapter.run(this.sql, params, callback);
  }

  all<T = any>(params: any[], callback: Callback<T[]>) {
    this.adapter.all<T>(this.sql, params, callback);
  }

  get<T = any>(params: any[], callback: Callback<T>) {
    this.adapter.get<T>(this.sql, params, callback);
  }

  finalize(callback?: Callback) {
    if (callback) {
      callback(null);
    }
  }
}

class DatabaseAdapter {
  constructor(private manager: DatabaseManager) {}

  private normalizeQuery(sql: string, params: any[] = []): QueryOptions {
    let index = 0;
    const transformed = sql.replace(/\?/g, () => `$${++index}`);
    return { text: transformed, values: params };
  }

  private async execute<T = any>(sql: string, params: any[] = []): Promise<QueryResult<T>> {
    const pool = await this.manager.connect();
    const query = this.normalizeQuery(sql, params);
    return pool.query<T>(query.text, query.values);
  }

  run(sql: string, params?: any[] | Callback, callback?: Callback) {
    const { preparedParams, preparedCallback } = this.extractParamsAndCallback(params, callback);
    this.execute(sql, preparedParams)
      .then(result => {
        preparedCallback.call({ changes: result.rowCount }, null);
      })
      .catch(err => {
        preparedCallback.call({ changes: 0 }, err);
      });
  }

  get<T = any>(sql: string, params?: any[] | Callback<T>, callback?: Callback<T>) {
    const { preparedParams, preparedCallback } = this.extractParamsAndCallback(params, callback);
    this.execute<T>(sql, preparedParams)
      .then(result => {
        preparedCallback(null, result.rows[0] as T);
      })
      .catch(err => preparedCallback(err));
  }

  all<T = any>(sql: string, params?: any[] | Callback<T[]>, callback?: Callback<T[]>) {
    const { preparedParams, preparedCallback } = this.extractParamsAndCallback(params, callback);
    this.execute<T>(sql, preparedParams)
      .then(result => {
        preparedCallback(null, result.rows as T[]);
      })
      .catch(err => preparedCallback(err));
  }

  exec(sql: string, callback: Callback = () => undefined) {
    const statements = sql
      .split(';')
      .map(stmt => stmt.trim())
      .filter(stmt => stmt.length > 0);

    (async () => {
      const pool = await this.manager.connect();
      const client = await pool.connect();
      try {
        await client.query('BEGIN');
        for (const statement of statements) {
          await client.query(statement);
        }
        await client.query('COMMIT');
        callback.call({ changes: 0 }, null);
      } catch (error) {
        await client.query('ROLLBACK');
        callback.call({ changes: 0 }, error as Error);
      } finally {
        client.release();
      }
    })().catch(err => {
      callback.call({ changes: 0 }, err);
    });
  }

  prepare(sql: string): PreparedStatement {
    return new PreparedStatement(this, sql);
  }

  private extractParamsAndCallback<T = any>(
    params?: any[] | Callback<T>,
    callback?: Callback<T>
  ): { preparedParams: any[]; preparedCallback: Callback<T> } {
    if (typeof params === 'function') {
      return { preparedParams: [], preparedCallback: params as Callback<T> };
    }
    return { preparedParams: params || [], preparedCallback: callback || (() => undefined) };
  }
}

class DatabaseManager {
  private static instance: DatabaseManager;
  private pool: Pool | null = null;
  private adapter: DatabaseAdapter | null = null;

  private constructor() {}

  public static getInstance(): DatabaseManager {
    if (!DatabaseManager.instance) {
      DatabaseManager.instance = new DatabaseManager();
    }
    return DatabaseManager.instance;
  }

  public async connect(): Promise<Pool> {
    if (this.pool) {
      return this.pool;
    }

    const connectionString = process.env.DATABASE_URL;
    const poolConfig: PoolConfig = {
      connectionString,
      max: Number(process.env.DB_POOL_SIZE || 10),
      idleTimeoutMillis: 30000,
      ssl: process.env.DB_SSL === 'true' ? { rejectUnauthorized: false } : undefined,
    };

    if (!poolConfig.connectionString) {
      poolConfig.host = process.env.PGHOST || 'localhost';
      poolConfig.user = process.env.PGUSER || 'postgres';
      poolConfig.password = process.env.PGPASSWORD || 'postgres';
      poolConfig.database = process.env.PGDATABASE || 'flowstate';
      poolConfig.port = Number(process.env.PGPORT || 5432);
    }

    this.pool = new Pool(poolConfig);
    this.pool.on('error', (err) => {
      safeLogger.error('Unexpected database error', err);
    });

    await this.pool.query('SELECT 1');
    safeLogger.info('Connected to PostgreSQL database');
    return this.pool;
  }

  public getDb(): DatabaseAdapter {
    if (!this.adapter) {
      this.adapter = new DatabaseAdapter(this);
    }
    return this.adapter;
  }

  public async query<T = any>(text: string, values: any[] = []): Promise<QueryResult<T>> {
    const pool = await this.connect();
    return pool.query<T>(text, values);
  }

  public async close(): Promise<void> {
    if (this.pool) {
      await this.pool.end();
      this.pool = null;
      this.adapter = null;
      safeLogger.info('Database pool closed');
    }
  }
}

export default DatabaseManager;
export { DatabaseManager };
