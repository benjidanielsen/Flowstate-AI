import type winston from 'winston';
import logger from './logger';

const SENSITIVE_FIELDS = [
  'password',
  'token',
  'accessToken',
  'refreshToken',
  'secret',
  'apiKey',
  'apikey',
  'authorization',
  'auth',
  'email',
  'phone',
  'ssn',
  'socialSecurityNumber',
  'creditCard',
  'cardNumber',
];

const REDACTED_VALUE = '[REDACTED]';
const SENSITIVE_FIELD_SET = new Set(SENSITIVE_FIELDS.map(field => field.toLowerCase()));

type LogFunction = (message: string, meta?: unknown) => winston.Logger | void;

const maskValue = (value: unknown): unknown => {
  if (Array.isArray(value)) {
    return value.map(() => REDACTED_VALUE);
  }

  if (value && typeof value === 'object') {
    return REDACTED_VALUE;
  }

  return REDACTED_VALUE;
};

const isPlainObject = (value: unknown): value is Record<string, unknown> => {
  if (value === null) {
    return false;
  }

  if (Array.isArray(value)) {
    return false;
  }

  return typeof value === 'object' && Object.getPrototypeOf(value) === Object.prototype;
};

const sanitizeValue = (value: unknown, parentKey?: string): unknown => {
  if (parentKey && SENSITIVE_FIELD_SET.has(parentKey.toLowerCase())) {
    return maskValue(value);
  }

  if (Array.isArray(value)) {
    return value.map(entry => sanitizeValue(entry));
  }

  if (isPlainObject(value)) {
    return Object.entries(value).reduce<Record<string, unknown>>((acc, [key, entry]) => {
      acc[key] = sanitizeValue(entry, key);
      return acc;
    }, {});
  }

  return value;
};

const sanitizeMeta = (meta?: unknown): unknown => {
  if (meta === undefined || meta === null) {
    return meta;
  }

  if (Array.isArray(meta) || isPlainObject(meta)) {
    return sanitizeValue(meta);
  }

  return meta;
};

const wrapLogFunction = (fn: LogFunction): LogFunction => {
  return (message: string, meta?: unknown) => fn(message, sanitizeMeta(meta));
};

export const safeLogger = {
  info: wrapLogFunction(logger.info.bind(logger)),
  warn: wrapLogFunction(logger.warn.bind(logger)),
  error: wrapLogFunction(logger.error.bind(logger)),
  debug: wrapLogFunction(logger.debug.bind(logger)),
};

export default safeLogger;
