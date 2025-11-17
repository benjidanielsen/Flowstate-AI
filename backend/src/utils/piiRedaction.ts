import logger from './logger';
import { correlationContext } from './correlationContext';

type Primitive = string | number | boolean | null | undefined;

type LogMeta = unknown;

type LogLevel = 'info' | 'warn' | 'error' | 'debug';

const PII_PATTERNS: Array<{ pattern: RegExp; replacement: string | ((match: string) => string) }> = [
  { pattern: /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b/g, replacement: '[REDACTED_EMAIL]' },
  { pattern: /\b\+?\d{1,2}?[-.\s]?\(?(?:\d{3})\)?[-.\s]?\d{3}[-.\s]?\d{4}\b/g, replacement: '[REDACTED_PHONE]' },
  { pattern: /\b(?:customer|user|agent|prospect)_?id\s*[:=]\s*[^\s,]+/gi, replacement: (match) => {
    const [key] = match.split(/[:=]/);
    return `${key.trim()}: [REDACTED_ID]`;
  } },
  { pattern: /\b\d{3}-\d{2}-\d{4}\b/g, replacement: '[REDACTED_SSN]' },
];

const redactString = (input: string): string => {
  return PII_PATTERNS.reduce<string>((acc, { pattern, replacement }) => {
    if (typeof replacement === 'function') {
      return acc.replace(pattern, (match: string) => replacement(match));
    }
    return acc.replace(pattern, replacement);
  }, input);
};

const sanitizePrimitive = (value: Primitive): Primitive | string => {
  if (typeof value === 'string') {
    return redactString(value);
  }
  return value;
};

const sanitizeUnknown = (value: unknown): unknown => {
  if (value === null || value === undefined) {
    return value;
  }

  if (typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean') {
    return sanitizePrimitive(value);
  }

  if (value instanceof Error) {
    return {
      name: value.name,
      message: redactString(value.message),
      stack: value.stack ? redactString(value.stack) : undefined,
    };
  }

  if (Array.isArray(value)) {
    return value.map((item) => sanitizeUnknown(item));
  }

  if (typeof value === 'object') {
    const sanitizedEntries = Object.entries(value as Record<string, unknown>).map(([key, val]) => [key, sanitizeUnknown(val)] as const);
    return Object.fromEntries(sanitizedEntries);
  }

  try {
    return redactString(String(value));
  } catch {
    return value;
  }
};

const buildLogPayload = (message: unknown): string => {
  if (typeof message === 'string') {
    return redactString(message);
  }

  if (message instanceof Error) {
    return redactString(`${message.name}: ${message.message}`);
  }

  try {
    return redactString(JSON.stringify(sanitizeUnknown(message)));
  } catch {
    return '[UNSERIALIZABLE_LOG_MESSAGE]';
  }
};

const sanitizeMeta = (meta?: LogMeta): unknown => {
  if (meta === undefined) {
    return undefined;
  }
  return sanitizeUnknown(meta);
};

const appendCorrelationId = (meta: unknown): unknown => {
  const correlationId = correlationContext.getCorrelationId();

  if (!correlationId) {
    return meta;
  }

  if (meta === undefined) {
    return { correlationId };
  }

  if (meta && typeof meta === 'object' && !Array.isArray(meta)) {
    return { correlationId, ...(meta as Record<string, unknown>) };
  }

  return { correlationId, value: meta };
};

const log = (level: LogLevel, message: unknown, meta?: LogMeta) => {
  const sanitizedMessage = buildLogPayload(message);
  const sanitizedMeta = appendCorrelationId(sanitizeMeta(meta));

  if (sanitizedMeta !== undefined) {
    logger.log(level, sanitizedMessage, sanitizedMeta);
  } else {
    logger.log(level, sanitizedMessage);
  }
};

export const safeLogger: {
  info: (message: unknown, meta?: LogMeta) => void;
  warn: (message: unknown, meta?: LogMeta) => void;
  error: (message: unknown, meta?: LogMeta) => void;
  debug: (message: unknown, meta?: LogMeta) => void;
} = {
  info: (message, meta) => log('info', message, meta),
  warn: (message, meta) => log('warn', message, meta),
  error: (message, meta) => log('error', message, meta),
  debug: (message, meta) => log('debug', message, meta),
};

export default safeLogger;
