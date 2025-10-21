import { describe, it, expect, beforeAll, afterEach, vi } from 'vitest';
import { render, waitFor } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
import QualificationQuestionnaire from '../components/QualificationQuestionnaire';
import RemindersPanel from '../components/RemindersPanel';
import { Customer, PipelineStatus } from '../types';
import type { Mock } from 'vitest';

// Extend expect with jest-axe matchers
expect.extend(toHaveNoViolations);

type FetchArgs = Parameters<typeof fetch>;
type MockFetchResponse = { ok: boolean; json: () => Promise<unknown> };
type FetchMock = Mock<FetchArgs, Promise<MockFetchResponse>>;

const fetchMock: FetchMock = vi.fn<FetchArgs, Promise<MockFetchResponse>>();

describe('Accessibility Tests', () => {
  describe('QualificationQuestionnaire', () => {
    const mockCustomer: Customer = {
      id: '1',
      name: 'John Doe',
      email: 'john@example.com',
      status: PipelineStatus.INVITED,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    it('should not have accessibility violations', async () => {
      const { container } = render(
        <QualificationQuestionnaire
          customer={mockCustomer}
          onComplete={() => {}}
          onCancel={() => {}}
        />
      );

      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });
  });

  describe('RemindersPanel', () => {
    // Mock fetch for RemindersPanel
    beforeAll(() => {
      fetchMock.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve([]),
      });
      global.fetch = fetchMock as unknown as typeof fetch;
    });

    afterEach(() => {
      fetchMock.mockClear();
    });

    it('should not have accessibility violations', async () => {
      const { container } = render(<RemindersPanel />);

      // Wait for component to load
      await waitFor(() => {
        expect(fetchMock).toHaveBeenCalled();
      });

      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });
  });
});
