import DatabaseManager from '../database';

beforeAll(async () => {
  // Setup test database
  process.env.DATABASE_URL = ':memory:';
});

afterAll(async () => {
  // Close database connections
  await DatabaseManager.getInstance().close();
});

beforeEach(() => {
  // Reset any mocks or test state
});