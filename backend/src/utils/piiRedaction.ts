import logger from './logger';

// Common PII patterns we want to sanitize from both messages and metadata
const PII_PATTERNS: Array<{ regex: RegExp; replacement: string }> = [
  { regex: /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b/g, replacement: '[REDACTED_EMAIL]' },
  { regex: /\b\d{3}[-.]?\d{3}[-.]?\d{4}\b/g, replacement: '[REDACTED_PHONE]' },
  { regex: /\b(ssn|social security number)[:\s]*\d{3}-?\d{2}-?\d{4}\b/gi, replacement: '$1: [REDACTED_SSN]' },
  { regex: /\b(?:\d[ -]*?){13,19}\b/g, replacement: '[REDACTED_CARD]' },
  { regex: /\b(user_id|customer_id|agent_id|id)[:=]\s*[^\s,}]+/gi, replacement: '$1: [REDACTED_ID]' },
];

const redactString = (input: string): string => {
  return PII_PATTERNS.reduce((acc, pattern) => acc.replace(pattern.regex, pattern.replacement), input);
};

const scrubMeta = (meta: unknown): unknown => {
  if (meta == null) return meta;

  if (typeof meta === 'string') {
    return redactString(meta);
  }

  if (typeof meta === 'number' || typeof meta === 'boolean') {
    return meta;
  }

  if (Array.isArray(meta)) {
    return meta.map((item) => scrubMeta(item));
  }

  if (meta instanceof Error) {
    return {
      name: meta.name,
      message: redactString(meta.message),
      stack: meta.stack ? redactString(meta.stack) : undefined,
    };
  }

  if (typeof meta === 'object') {
    return Object.entries(meta as Record<string, unknown>).reduce<Record<string, unknown>>((acc, [key, value]) => {
      acc[key] = scrubMeta(value);
      return acc;
    }, {});
  }

  return meta;
};

type LogMethod = (message: string, meta?: unknown) => void;

const createSafeLogMethod = (level: 'info' | 'warn' | 'error' | 'debug'): LogMethod => {
  return (message: string, meta?: unknown) => {
    const sanitizedMessage = redactString(message);
    const sanitizedMeta = scrubMeta(meta);
    (logger as unknown as Record<string, LogMethod>)[level](sanitizedMessage, sanitizedMeta);
  };
};

export const safeLogger = {
  info: createSafeLogMethod('info'),
  warn: createSafeLogMethod('warn'),
  error: createSafeLogMethod('error'),
  debug: createSafeLogMethod('debug'),
};

export default safeLogger;
