import logger from '../utils/logger';
import DatabaseManager from '../database';
import getDbInstance from '../database/supabase';
import { documents } from '../database/schema';
import embeddingService from '../services/embeddingService';
import vectorSearchService from '../services/vectorSearchService';
import { sql } from 'drizzle-orm';
import { hasOpenAIKey } from '../config/environment';

async function reindexDocuments() {
  if (!hasOpenAIKey()) {
    logger.error('OPENAI_API_KEY must be configured to reindex documents.');
    process.exitCode = 1;
    return;
  }

  const dbManager = DatabaseManager.getInstance();

  try {
    await dbManager.connect();
    const db = getDbInstance();

    logger.info('Fetching documents for reindexing...');
    const docs = await db.select().from(documents);

    let updatedCount = 0;
    for (const doc of docs) {
      if (!doc.content) {
        continue;
      }

      const embedding = await embeddingService.generateEmbedding(doc.content);
      const embeddingStr = embeddingService.formatEmbeddingForPostgres(embedding);
      await db.execute(sql`UPDATE documents SET embedding = ${embeddingStr} WHERE id = ${doc.id}`);
      updatedCount += 1;
    }

    logger.info(`Reindexed ${updatedCount} document(s).`);

    if (updatedCount === 0) {
      logger.warn('No documents contained content to index; skipping search smoke test.');
      return;
    }

    const sampleQuery = 'sample customer';
    logger.info(`Running semantic search smoke test for query: "${sampleQuery}"`);
    const results = await vectorSearchService.semanticSearch(sampleQuery, { limit: 3 });
    logger.info(`Semantic search returned ${results.length} result(s).`);
  } catch (error) {
    logger.error('Failed to reindex documents or run semantic search:', error);
    process.exitCode = 1;
  } finally {
    await dbManager.close();
  }
}

reindexDocuments().catch((error) => {
  logger.error('Unexpected error during reindexing:', error);
  process.exitCode = 1;
});

