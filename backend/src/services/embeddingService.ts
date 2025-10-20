import logger from '../utils/logger';
import axios from 'axios';
import { environment, getOpenAIApiKey, hasOpenAIKey } from '../config/environment';

export interface EmbeddingResult {
  embedding: number[];
  model: string;
  usage: {
    prompt_tokens: number;
    total_tokens: number;
  };
}

export class EmbeddingService {
  private apiKey: string;
  private model: string;
  private apiUrl: string;

  constructor() {
    this.apiKey = environment.openAI.apiKey || '';
    this.model = environment.openAI.model;
    this.apiUrl = environment.openAI.apiUrl;

    if (!hasOpenAIKey()) {
      logger.warn('OPENAI_API_KEY not set. Embedding service will not work.');
    }
  }

  private ensureApiKey(): string {
    if (!this.apiKey) {
      this.apiKey = getOpenAIApiKey();
    }
    return this.apiKey;
  }

  /**
   * Generate an embedding for a given text
   */
  async generateEmbedding(text: string): Promise<number[]> {
    try {
      const apiKey = this.ensureApiKey();

      logger.debug(`Generating embedding for text: ${text.substring(0, 100)}...`);

      const response = await axios.post(
        this.apiUrl,
        {
          input: text,
          model: this.model,
        },
        {
          headers: {
            'Authorization': `Bearer ${apiKey}`,
            'Content-Type': 'application/json',
          },
        }
      );

      const embedding = response.data.data[0].embedding;
      logger.debug(`Generated embedding with ${embedding.length} dimensions`);

      return embedding;
    } catch (error: any) {
      logger.error('Error generating embedding:', error.response?.data || error.message);
      throw new Error(`Failed to generate embedding: ${error.message}`);
    }
  }

  /**
   * Generate embeddings for multiple texts in batch
   */
  async generateEmbeddings(texts: string[]): Promise<number[][]> {
    try {
      const apiKey = this.ensureApiKey();

      logger.debug(`Generating embeddings for ${texts.length} texts`);

      const response = await axios.post(
        this.apiUrl,
        {
          input: texts,
          model: this.model,
        },
        {
          headers: {
            'Authorization': `Bearer ${apiKey}`,
            'Content-Type': 'application/json',
          },
        }
      );

      const embeddings = response.data.data.map((item: any) => item.embedding);
      logger.debug(`Generated ${embeddings.length} embeddings`);

      return embeddings;
    } catch (error: any) {
      logger.error('Error generating embeddings:', error.response?.data || error.message);
      throw new Error(`Failed to generate embeddings: ${error.message}`);
    }
  }

  /**
   * Calculate cosine similarity between two embeddings
   */
  cosineSimilarity(embedding1: number[], embedding2: number[]): number {
    if (embedding1.length !== embedding2.length) {
      throw new Error('Embeddings must have the same dimension');
    }

    let dotProduct = 0;
    let norm1 = 0;
    let norm2 = 0;

    for (let i = 0; i < embedding1.length; i++) {
      dotProduct += embedding1[i] * embedding2[i];
      norm1 += embedding1[i] * embedding1[i];
      norm2 += embedding2[i] * embedding2[i];
    }

    return dotProduct / (Math.sqrt(norm1) * Math.sqrt(norm2));
  }

  /**
   * Format embedding for PostgreSQL vector type
   */
  formatEmbeddingForPostgres(embedding: number[]): string {
    return `[${embedding.join(',')}]`;
  }

  /**
   * Parse embedding from PostgreSQL vector type
   */
  parseEmbeddingFromPostgres(embeddingStr: string): number[] {
    // Remove brackets and split by comma
    const cleaned = embeddingStr.replace(/^\[|\]$/g, '');
    return cleaned.split(',').map(Number);
  }

  /**
   * Get the embedding model being used
   */
  getModel(): string {
    return this.model;
  }

  /**
   * Get the expected embedding dimension for the current model
   */
  getEmbeddingDimension(): number {
    // text-embedding-3-small: 1536 dimensions
    // text-embedding-3-large: 3072 dimensions
    // text-embedding-ada-002: 1536 dimensions
    
    if (this.model.includes('large')) {
      return 3072;
    }
    return 1536;
  }
}

export default new EmbeddingService();

