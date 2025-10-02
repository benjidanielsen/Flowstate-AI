# End-to-End Testing for FlowState-AI

This directory contains comprehensive end-to-end (E2E) tests for the FlowState-AI CRM system using Playwright.

## Overview

The E2E test suite covers all critical user workflows in the FlowState-AI system:

1. **Customer Creation Flow** - Creating new customers with validation
2. **Pipeline Progression** - Moving customers through Frazer Method stages
3. **Qualification Process** - Completing the "Prospect's WHY" questionnaire
4. **Follow-up Automation** - Creating and managing automated reminders

## Test Structure

```
e2e/
├── tests/
│   ├── 01-customer-creation.spec.ts      # Customer creation and validation
│   ├── 02-pipeline-progression.spec.ts   # Frazer Method pipeline stages
│   ├── 03-qualification-process.spec.ts  # Qualification questionnaire
│   └── 04-follow-up-automation.spec.ts   # Reminder system
├── fixtures/                              # Test data and fixtures
└── README.md                              # This file
```

## Prerequisites

- Node.js 18+ installed
- FlowState-AI backend and frontend dependencies installed
- Playwright installed (`npm install -D @playwright/test`)
- Chromium browser installed (`npx playwright install chromium`)

## Running Tests

### Run all E2E tests

```bash
npm run test:e2e
```

### Run specific test file

```bash
npx playwright test e2e/tests/01-customer-creation.spec.ts
```

### Run tests in headed mode (with browser UI)

```bash
npx playwright test --headed
```

### Run tests in debug mode

```bash
npx playwright test --debug
```

### View test report

```bash
npx playwright show-report
```

## Test Configuration

The Playwright configuration is defined in `playwright.config.ts` at the project root.

Key configuration options:

- **Base URL**: `http://localhost:3000`
- **Timeout**: 30 seconds per test
- **Retries**: 2 retries on CI, 0 locally
- **Browsers**: Chromium (Desktop Chrome)
- **Web Servers**: Automatically starts backend (port 3001) and frontend (port 3000)

## Writing New Tests

When adding new E2E tests:

1. Create a new `.spec.ts` file in `e2e/tests/`
2. Use descriptive test names that explain the user workflow
3. Follow the existing test structure and patterns
4. Use `test.beforeEach()` for common setup
5. Use `test.describe()` to group related tests
6. Add appropriate assertions with `expect()`
7. Handle async operations with `await`
8. Use `page.waitForTimeout()` sparingly; prefer `waitForSelector()` or `waitForLoadState()`

### Example Test Structure

```typescript
import { test, expect } from '@playwright/test';

test.describe('Feature Name', () => {
  test.beforeEach(async ({ page }) => {
    // Common setup for all tests in this describe block
    await page.goto('/');
  });

  test('should perform specific action', async ({ page }) => {
    // Test implementation
    await page.getByRole('button', { name: /action/i }).click();
    await expect(page.getByText(/success/i)).toBeVisible();
  });
});
```

## Best Practices

1. **Use semantic selectors**: Prefer `getByRole()`, `getByLabel()`, `getByText()` over CSS selectors
2. **Wait for elements**: Use `waitForSelector()` or `waitForLoadState()` instead of fixed timeouts
3. **Unique test data**: Use timestamps or UUIDs to create unique test data
4. **Clean up**: Tests should be independent and not rely on previous test state
5. **Assertions**: Always verify the expected outcome with `expect()`
6. **Error handling**: Tests should handle both success and failure scenarios
7. **Documentation**: Add comments explaining complex test logic

## Continuous Integration

The E2E tests are configured to run automatically on CI/CD pipelines:

- Tests run on every pull request
- Tests run on every push to main branch
- Failed tests block merges
- Test reports are generated and archived

## Troubleshooting

### Tests fail locally but pass on CI

- Ensure your local environment matches CI (Node.js version, dependencies)
- Check if backend/frontend servers are running
- Clear browser cache and cookies

### Tests are flaky

- Increase timeout values in `playwright.config.ts`
- Add explicit waits for dynamic content
- Use `waitForLoadState('networkidle')` for AJAX-heavy pages

### Browser not found

```bash
npx playwright install chromium
```

### Port already in use

- Stop any running backend/frontend servers
- Change ports in `playwright.config.ts` if needed

## Test Coverage

Current test coverage:

- ✅ Customer creation and validation
- ✅ Pipeline progression (all Frazer Method stages)
- ✅ Qualification questionnaire
- ✅ Follow-up reminder system
- ⏳ Interaction logging (planned)
- ⏳ Analytics dashboard (planned)
- ⏳ Export functionality (planned)

## Author

**Manus 7** - Quality-focused AI Agent  
Task: TASK-110 (End-to-End Testing)  
Date: October 2, 2025

## License

MIT License - See project root for details
