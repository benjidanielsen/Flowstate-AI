import DatabaseManager from '../database';

beforeAll(async () => {
  // Setup test database
  process.env.DATABASE_URL = ':memory:';
  process.env.BYPASS_AUTH_TOKEN = 'test-bypass-token';
});

afterAll(async () => {
  // Close database connections
  await DatabaseManager.getInstance().close();
});

beforeEach(() => {
  // Reset any mocks or test state
});