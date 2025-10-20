import dotenv from 'dotenv';
import Joi from 'joi';

dotenv.config();

const envSchema = Joi.object({
  NODE_ENV: Joi.string()
    .valid('development', 'test', 'production', 'staging')
    .default('development'),
  OPENAI_API_KEY: Joi.string().allow('').optional(),
  EMBEDDING_MODEL: Joi.string().default('text-embedding-3-small'),
  OPENAI_API_URL: Joi.string()
    .uri()
    .default('https://api.openai.com/v1/embeddings'),
}).unknown();

const { value, error } = envSchema.validate(process.env, {
  abortEarly: false,
  stripUnknown: false,
});

if (error) {
  throw new Error(`Environment validation error: ${error.message}`);
}

export const environment = {
  nodeEnv: value.NODE_ENV as string,
  openAI: {
    apiKey: (value.OPENAI_API_KEY as string | undefined) ?? '',
    model: value.EMBEDDING_MODEL as string,
    apiUrl: value.OPENAI_API_URL as string,
  },
};

export const hasOpenAIKey = (): boolean => Boolean(environment.openAI.apiKey);

export const getOpenAIApiKey = (): string => {
  if (!environment.openAI.apiKey) {
    throw new Error('OPENAI_API_KEY not configured');
  }
  return environment.openAI.apiKey;
};

