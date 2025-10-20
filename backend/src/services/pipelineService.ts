import { v4 as uuidv4 } from 'uuid';
import { PoolClient } from 'pg';
import DatabaseManager from '../database';
import logger from '../utils/logger';
import { Customer, Pipeline, PipelineStage } from '../types';

export interface PipelineWithStages extends Pipeline {
  stages: PipelineStage[];
}

const pipelineStageSelect = `
  SELECT id, pipeline_id, name, description, position, metadata, created_at, updated_at
  FROM pipeline_stages
  WHERE pipeline_id = $1
  ORDER BY position ASC
`;

export class PipelineService {
  async listPipelines(): Promise<PipelineWithStages[]> {
    let client: PoolClient | null = null;
    try {
      const pool = DatabaseManager.getInstance().getPool();
      client = await pool.connect();
      const pipelinesResult = await client.query<Pipeline>(
        `SELECT id, name, description, created_at, updated_at FROM pipelines ORDER BY created_at ASC`
      );

      const pipelines = await Promise.all(
        pipelinesResult.rows.map(async (pipeline) => {
          const stages = await client!.query<PipelineStage>(pipelineStageSelect, [pipeline.id]);
          return {
            ...pipeline,
            stages: stages.rows.map((stage) => ({
              ...stage,
              metadata: stage.metadata ?? {},
              created_at: new Date(stage.created_at),
              updated_at: new Date(stage.updated_at)
            })),
            created_at: new Date(pipeline.created_at),
            updated_at: new Date(pipeline.updated_at)
          };
        })
      );
      return pipelines;
    } finally {
      if (client) client.release();
    }
  }

  async getPipelineById(id: string): Promise<PipelineWithStages | null> {
    let client: PoolClient | null = null;
    try {
      const pool = DatabaseManager.getInstance().getPool();
      client = await pool.connect();
      const pipelineResult = await client.query<Pipeline>(
        `SELECT id, name, description, created_at, updated_at FROM pipelines WHERE id = $1`,
        [id]
      );
      const pipeline = pipelineResult.rows[0];
      if (!pipeline) return null;
      const stages = await client.query<PipelineStage>(pipelineStageSelect, [pipeline.id]);
      return {
        ...pipeline,
        stages: stages.rows.map((stage) => ({
          ...stage,
          metadata: stage.metadata ?? {},
          created_at: new Date(stage.created_at),
          updated_at: new Date(stage.updated_at)
        })),
        created_at: new Date(pipeline.created_at),
        updated_at: new Date(pipeline.updated_at)
      };
    } finally {
      if (client) client.release();
    }
  }

  async createPipeline(data: Pick<Pipeline, 'name' | 'description'> & { stages?: Array<Pick<PipelineStage, 'name' | 'description' | 'position' | 'metadata'>> }): Promise<PipelineWithStages> {
    let client: PoolClient | null = null;
    try {
      const pool = DatabaseManager.getInstance().getPool();
      client = await pool.connect();
      await client.query('BEGIN');

      const pipelineId = uuidv4();
      const pipelineResult = await client.query<Pipeline>(
        `INSERT INTO pipelines (id, name, description)
         VALUES ($1, $2, $3)
         RETURNING id, name, description, created_at, updated_at`,
        [pipelineId, data.name, data.description || null]
      );
      const pipeline = pipelineResult.rows[0];

      const stageRecords: PipelineStage[] = [];
      if (data.stages?.length) {
        for (const stage of data.stages.sort((a, b) => a.position - b.position)) {
          const stageId = uuidv4();
          const stageResult = await client.query<PipelineStage>(
            `INSERT INTO pipeline_stages (id, pipeline_id, name, description, position, metadata)
             VALUES ($1, $2, $3, $4, $5, $6)
             RETURNING id, pipeline_id, name, description, position, metadata, created_at, updated_at`,
            [stageId, pipelineId, stage.name, stage.description || null, stage.position, stage.metadata || {}]
          );
          stageRecords.push({
            ...stageResult.rows[0],
            metadata: stageResult.rows[0].metadata ?? {},
            created_at: new Date(stageResult.rows[0].created_at),
            updated_at: new Date(stageResult.rows[0].updated_at)
          } as PipelineStage);
        }
      }

      await client.query('COMMIT');
      return {
        ...pipeline,
        created_at: new Date(pipeline.created_at),
        updated_at: new Date(pipeline.updated_at),
        stages: stageRecords
      };
    } catch (error) {
      if (client) await client.query('ROLLBACK');
      logger.error('Failed to create pipeline', error);
      throw error;
    } finally {
      if (client) client.release();
    }
  }

  async upsertStage(pipelineId: string, stage: Partial<PipelineStage> & { name: string; position: number; id?: string }): Promise<PipelineStage> {
    let client: PoolClient | null = null;
    try {
      const pool = DatabaseManager.getInstance().getPool();
      client = await pool.connect();
      const stageId = stage.id ?? uuidv4();
      const query = stage.id
        ? `UPDATE pipeline_stages
             SET name = $1, description = $2, position = $3, metadata = $4, updated_at = NOW()
           WHERE id = $5 AND pipeline_id = $6
           RETURNING id, pipeline_id, name, description, position, metadata, created_at, updated_at`
        : `INSERT INTO pipeline_stages (id, pipeline_id, name, description, position, metadata)
           VALUES ($1, $2, $3, $4, $5, $6)
           RETURNING id, pipeline_id, name, description, position, metadata, created_at, updated_at`;
      const params = stage.id
        ? [stage.name, stage.description || null, stage.position, stage.metadata || {}, stageId, pipelineId]
        : [stageId, pipelineId, stage.name, stage.description || null, stage.position, stage.metadata || {}];

      const result = await client.query<PipelineStage>(query, params);
      const record = result.rows[0];
      return {
        ...record,
        metadata: record.metadata ?? {},
        created_at: new Date(record.created_at),
        updated_at: new Date(record.updated_at)
      };
    } finally {
      if (client) client.release();
    }
  }

  async deleteStage(stageId: string): Promise<boolean> {
    let client: PoolClient | null = null;
    try {
      const pool = DatabaseManager.getInstance().getPool();
      client = await pool.connect();
      const result = await client.query(`DELETE FROM pipeline_stages WHERE id = $1`, [stageId]);
      return (result.rowCount ?? 0) > 0;
    } finally {
      if (client) client.release();
    }
  }

  async assignCustomerToStage(customerId: string, stageId: string): Promise<Customer | null> {
    let client: PoolClient | null = null;
    try {
      const pool = DatabaseManager.getInstance().getPool();
      client = await pool.connect();
      const result = await client.query<Customer>(
        `UPDATE customers
           SET pipeline_stage_id = $1,
               pipeline_id = (SELECT pipeline_id FROM pipeline_stages WHERE id = $1),
               updated_at = NOW()
         WHERE id = $2
         RETURNING *`,
        [stageId, customerId]
      );
      const row = result.rows[0];
      if (!row) return null;
      return {
        ...row,
        created_at: new Date(row.created_at),
        updated_at: new Date(row.updated_at),
        next_action_date: row.next_action_date ? new Date(row.next_action_date) : undefined,
        last_interacted_at: row.last_interacted_at ? new Date(row.last_interacted_at) : undefined,
        consent_json: row.consent_json,
        utm_json: row.utm_json
      };
    } finally {
      if (client) client.release();
    }
  }
}

export const pipelineService = new PipelineService();
