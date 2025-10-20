# Frontend Testing Guide

## Overview

This project uses **Vitest** and **React Testing Library** for unit and integration testing of React components.

## Test Structure

```
frontend/src/
├── components/
│   ├── __tests__/
│   │   ├── QualificationQuestionnaire.test.tsx
│   │   └── RemindersPanel.test.tsx
│   ├── QualificationQuestionnaire.tsx
│   └── RemindersPanel.tsx
└── test/
    ├── setup.ts
    └── README.md (this file)
```

## Running Tests

```bash
# Run tests in watch mode (interactive)
npm test

# Run tests once
npm run test:run

# Run tests with coverage report
npm run test:coverage

# Run tests with UI
npm run test:ui
```

## Test Coverage

### QualificationQuestionnaire Component (9 tests)
- ✅ Component rendering
- ✅ Customer name display
- ✅ Required field validation
- ✅ Successful form submission
- ✅ Loading states
- ✅ API error handling
- ✅ Cancel functionality
- ✅ Pre-filled data
- ✅ Button states during loading

### RemindersPanel Component (13 tests)
- ✅ Loading state
- ✅ Fetching and displaying reminders
- ✅ Customer name display
- ✅ Active reminder count
- ✅ Urgency indicators (color coding)
- ✅ Empty state handling
- ✅ Network error handling
- ✅ API error handling
- ✅ Marking reminders as complete
- ✅ Customer-specific filtering
- ✅ Limit parameter
- ✅ Completed reminder styling
- ✅ Complete button visibility

## Writing Tests

### Basic Test Structure

```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import YourComponent from '../YourComponent';

describe('YourComponent', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders correctly', () => {
    render(<YourComponent />);
    expect(screen.getByText('Expected Text')).toBeInTheDocument();
  });
});
```

### Mocking APIs

```typescript
import * as api from '../../services/api';

vi.mock('../../services/api', () => ({
  customerApi: {
    update: vi.fn(),
  },
}));

// In your test
(api.customerApi.update as any).mockResolvedValue(mockData);
```

### User Interactions

```typescript
const user = userEvent.setup();

// Type in input
await user.type(screen.getByRole('textbox'), 'Hello');

// Click button
await user.click(screen.getByRole('button', { name: /Submit/i }));

// Clear input
await user.clear(screen.getByRole('textbox'));
```

### Async Testing

```typescript
await waitFor(() => {
  expect(screen.getByText('Success')).toBeInTheDocument();
}, { timeout: 3000 });
```

## Best Practices

1. **Use semantic queries**: Prefer `getByRole`, `getByLabelText` over `getByTestId`
2. **Test user behavior**: Focus on what users see and do, not implementation details
3. **Mock external dependencies**: APIs, timers, etc.
4. **Clean up**: Use `beforeEach` to reset mocks
5. **Async handling**: Always use `waitFor` for async operations
6. **Accessibility**: Testing with semantic queries improves accessibility

## Configuration

### vitest.config.ts
- Environment: jsdom (browser-like environment)
- Setup file: `src/test/setup.ts`
- Coverage provider: v8
- Coverage reporters: text, json, html

### src/test/setup.ts
- Imports `@testing-library/jest-dom` for custom matchers
- Configures cleanup after each test

## Troubleshooting

### Tests timing out
- Increase timeout in `waitFor`: `waitFor(() => {...}, { timeout: 5000 })`
- Check if async operations are properly mocked

### Element not found
- Use `screen.debug()` to see current DOM
- Check if element is rendered conditionally
- Ensure proper async handling with `waitFor`

### Mock not working
- Verify mock is set up before component render
- Clear mocks in `beforeEach`
- Check mock implementation matches actual API

## Resources

- [Vitest Documentation](https://vitest.dev/)
- [React Testing Library](https://testing-library.com/react)
- [Testing Library Queries](https://testing-library.com/docs/queries/about)
- [User Event](https://testing-library.com/docs/user-event/intro)
