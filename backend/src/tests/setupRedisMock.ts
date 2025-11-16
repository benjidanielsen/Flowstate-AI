// Ensure Redis operations use an in-memory mock during tests
jest.mock('ioredis', () => require('ioredis-mock'));

export {};
