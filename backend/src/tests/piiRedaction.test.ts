import EventEmitter from 'events';
import type { Request, Response, NextFunction } from 'express';

jest.mock('../utils/logger', () => {
  const info = jest.fn();
  const warn = jest.fn();
  const error = jest.fn();
  const debug = jest.fn();

  return {
    __esModule: true,
    default: {
      info,
      warn,
      error,
      debug,
    },
  };
});

import logger from '../utils/logger';
import { safeLogger } from '../utils/piiRedaction';
import { correlationIdMiddleware } from '../middleware/correlationId';

describe('safeLogger PII redaction', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('masks sensitive fields before delegating to the base logger', () => {
    const meta = {
      email: 'user@example.com',
      nested: {
        password: 'super-secret',
        profile: {
          token: 'abc123',
          safe: 'value',
        },
      },
      auditTrail: [
        { refreshToken: 'def456', action: 'login' },
      ],
    };

    safeLogger.info('user login', meta);

    expect(logger.info).toHaveBeenCalledWith('user login', {
      email: '[REDACTED]',
      nested: {
        password: '[REDACTED]',
        profile: {
          token: '[REDACTED]',
          safe: 'value',
        },
      },
      auditTrail: [
        { refreshToken: '[REDACTED]', action: 'login' },
      ],
    });
  });
});

class MockResponse extends EventEmitter {
  public setHeader = jest.fn();
}

describe('correlationId middleware', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('adds the correlation ID to all log metadata', () => {
    const req = {
      headers: {},
    } as Request;
    const res = new MockResponse() as unknown as Response;
    const next = jest.fn() as NextFunction;

    correlationIdMiddleware(req, res, next);

    safeLogger.info('processing request', { action: 'ping' });

    expect(logger.info).toHaveBeenCalledWith(
      'processing request',
      expect.objectContaining({
        action: 'ping',
        correlationId: req.correlationId,
      }),
    );
    expect(next).toHaveBeenCalled();
  });
});
