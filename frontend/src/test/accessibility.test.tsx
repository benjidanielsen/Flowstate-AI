import { describe, it, expect, beforeAll, vi } from 'vitest';
import { render, waitFor } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
import QualificationQuestionnaire from '../components/QualificationQuestionnaire';
import RemindersPanel from '../components/RemindersPanel';
import { Customer, PipelineStatus } from '../types';

// Extend expect with jest-axe matchers
expect.extend(toHaveNoViolations);

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
      global.fetch = vi.fn(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve([]),
        })
      ) as any;
    });

    it('should not have accessibility violations', async () => {
      const { container } = render(<RemindersPanel />);

      // Wait for component to load and state updates to complete
      await waitFor(() => {
        expect(container.querySelector('[role="status"]') || container.querySelector('div')).toBeTruthy();
      }, { timeout: 1000 });

      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });
  });
});
