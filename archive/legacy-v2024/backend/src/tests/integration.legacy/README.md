# Backend API Integration Tests

## Overview

This directory contains integration tests for the FlowState-AI backend API endpoints using **Jest** and **Supertest**.

## Test Structure

```
backend/src/tests/
├── integration/
│   ├── customers.api.test.ts      # Customer CRUD and pipeline operations
│   ├── reminders.api.test.ts      # Reminder management
│   ├── qualification.api.test.ts  # Qualification process
│   └── README.md (this file)
└── *.test.ts                      # Unit tests for services
```

## Running Tests

```bash
# Run all tests (unit + integration)
npm test

# Run tests in watch mode
npm run test:watch

# Run only integration tests
npm test -- integration

# Run specific test file
npm test -- customers.api.test
```

## Test Coverage

### Customers API (customers.api.test.ts)
- ✅ GET /api/customers - List all customers
- ✅ GET /api/customers/stats - Pipeline statistics
- ✅ POST /api/customers - Create new customer
- ✅ GET /api/customers/:id - Get customer by ID
- ✅ PUT /api/customers/:id - Update customer
- ✅ POST /api/customers/:id/next-stage - Move to next pipeline stage
- ✅ DELETE /api/customers/:id - Delete customer
- ✅ Error handling (404, 400 responses)

### Reminders API (reminders.api.test.ts)
- ✅ POST /api/reminders - Create new reminder
- ✅ GET /api/reminders/due - List due reminders
- ✅ POST /api/reminders/:id/complete - Mark reminder as complete
- ✅ Validation of reminder data
- ✅ Error handling (404, 400 responses)

### Qualification API (qualification.api.test.ts)
- ✅ POST /api/qualification - Save qualification data
- ✅ POST /api/qualification - Update existing qualification
- ✅ GET /api/qualification/:id - Retrieve qualification data
- ✅ Validation of qualification data
- ✅ Error handling (404, 400 responses)

## Test Database

Integration tests use the same database as the development environment. Each test:
1. Creates test data before running
2. Performs API operations
3. Cleans up test data after completion

**Important:** Ensure your database is running before executing integration tests.

## Writing New Integration Tests

### Basic Structure

```typescript
import request from 'supertest';
import express, { Express } from 'express';
import yourRoutes from '../../routes/yourRoutes';
import { pool } from '../../database/db';

describe('Your API Integration Tests', () => {
  let app: Express;

  beforeAll(() => {
    app = express();
    app.use(express.json());
    app.use('/api/your-endpoint', yourRoutes);
  });

  afterAll(async () => {
    await pool.end();
  });

  it('should perform an operation', async () => {
    const response = await request(app)
      .get('/api/your-endpoint')
      .expect(200);

    expect(response.body).toHaveProperty('expectedField');
  });
});
```

### Best Practices

1. **Isolation**: Each test should be independent and not rely on other tests
2. **Cleanup**: Always clean up test data in `afterAll` or `afterEach` hooks
3. **Unique Data**: Use timestamps or UUIDs to create unique test data
4. **Error Cases**: Test both success and error scenarios
5. **Status Codes**: Always verify HTTP status codes with `.expect()`
6. **Response Structure**: Validate response body structure and content
7. **Database State**: Verify database state changes when necessary

### Common Assertions

```typescript
// Status codes
.expect(200)  // Success
.expect(201)  // Created
.expect(204)  // No Content
.expect(400)  // Bad Request
.expect(404)  // Not Found

// Response body
expect(response.body).toHaveProperty('id');
expect(response.body.name).toBe('Expected Name');
expect(Array.isArray(response.body)).toBe(true);

// Database verification
const result = await pool.query('SELECT * FROM table WHERE id = $1', [id]);
expect(result.rows.length).toBe(1);
```

## Troubleshooting

### Tests failing with database errors
- Ensure PostgreSQL is running
- Check database connection settings in `.env`
- Verify database schema is up to date

### Tests timing out
- Increase Jest timeout in `jest.config.js`
- Check for hanging database connections
- Ensure `pool.end()` is called in `afterAll`

### Cleanup issues
- Use unique identifiers (timestamps, UUIDs) for test data
- Always use `afterAll` or `afterEach` for cleanup
- Consider using transactions for test isolation

## Resources

- [Jest Documentation](https://jestjs.io/)
- [Supertest Documentation](https://github.com/visionmedia/supertest)
- [Testing Best Practices](https://testingjavascript.com/)
