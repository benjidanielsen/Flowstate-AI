import { jest } from '@jest/globals';

const swaggerUi = {
  serve: jest.fn((_req?: unknown, _res?: unknown, next?: () => void) => {
    if (typeof next === 'function') {
      next();
    }
  }),
  setup: jest.fn(() => (_req?: unknown, _res?: unknown, next?: () => void) => {
    if (typeof next === 'function') {
      next();
    }
  }),
};

export default swaggerUi;
