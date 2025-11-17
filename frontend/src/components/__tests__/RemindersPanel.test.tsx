import { describe, it, expect, vi, beforeEach } from 'vitest';
import type { Mock } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import RemindersPanel from '../RemindersPanel';

type FetchArgs = Parameters<typeof fetch>;
type MockFetchResponse = { ok: boolean; json?: () => Promise<unknown>; status?: number };
type FetchMock = Mock<FetchArgs, Promise<MockFetchResponse>>;

const fetchMock: FetchMock = vi.fn<FetchArgs, Promise<MockFetchResponse>>();

global.fetch = fetchMock as unknown as typeof fetch;

describe('RemindersPanel', () => {
  const mockReminders = [
    {
      id: '1',
      customer_id: 'c1',
      customer_name: 'John Doe',
      type: 'Follow-up',
      description: 'Call to discuss proposal',
      due_date: new Date(Date.now() + 86400000).toISOString(), // Tomorrow
      completed: false,
      created_at: new Date().toISOString(),
    },
    {
      id: '2',
      customer_id: 'c2',
      customer_name: 'Jane Smith',
      type: 'Meeting',
      description: 'Quarterly review meeting',
      due_date: new Date(Date.now() - 86400000).toISOString(), // Yesterday (overdue)
      completed: false,
      created_at: new Date().toISOString(),
    },
    {
      id: '3',
      customer_id: 'c3',
      customer_name: 'Bob Johnson',
      type: 'Email',
      description: 'Send presentation',
      due_date: new Date(Date.now() + (86400000 * 5)).toISOString(), // In 5 days
      completed: true,
      created_at: new Date().toISOString(),
    },
  ];

  beforeEach(() => {
    vi.clearAllMocks();
    fetchMock.mockReset();
  });

  it('renders loading state initially', () => {
    fetchMock.mockImplementation(
      () => new Promise(() => {}) // Never resolves
    );

    const { container } = render(<RemindersPanel />);

    const spinner = container.querySelector('.animate-spin');
    expect(spinner).toBeInTheDocument();
  });

  it('fetches and displays reminders', async () => {
    fetchMock.mockResolvedValue({
      ok: true,
      json: async () => mockReminders,
    });

    render(<RemindersPanel />);

    await waitFor(() => {
      expect(screen.getByText('Upcoming Reminders')).toBeInTheDocument();
    });

    expect(screen.getByText('Call to discuss proposal')).toBeInTheDocument();
    expect(screen.getByText('Quarterly review meeting')).toBeInTheDocument();
    expect(screen.getByText('Send presentation')).toBeInTheDocument();
  });

  it('displays customer names', async () => {
    fetchMock.mockResolvedValue({
      ok: true,
      json: async () => mockReminders,
    });

    render(<RemindersPanel />);

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });

    expect(screen.getByText('Jane Smith')).toBeInTheDocument();
    expect(screen.getByText('Bob Johnson')).toBeInTheDocument();
  });

  it('shows active reminder count', async () => {
    fetchMock.mockResolvedValue({
      ok: true,
      json: async () => mockReminders,
    });

    render(<RemindersPanel />);

    await waitFor(() => {
      expect(screen.getByText('2 active')).toBeInTheDocument();
    });
  });

  it('displays urgency indicators correctly', async () => {
    fetchMock.mockResolvedValue({
      ok: true,
      json: async () => mockReminders,
    });

    const { container } = render(<RemindersPanel />);

    await waitFor(() => {
      expect(screen.getByText('Overdue')).toBeInTheDocument();
    });

    // Check for urgency color classes - overdue should have red border
    const overdueReminder = container.querySelector('.border-red-500');
    expect(overdueReminder).toBeInTheDocument();
    
    // Check that blue border exists for future reminders
    const futureReminder = container.querySelector('.border-blue-500');
    expect(futureReminder).toBeInTheDocument();
  });

  it('handles empty reminders list', async () => {
    fetchMock.mockResolvedValue({
      ok: true,
      json: async () => [],
    });

    render(<RemindersPanel />);

    await waitFor(() => {
      expect(screen.getByText('No reminders found')).toBeInTheDocument();
    });
  });

  it('handles fetch errors', async () => {
    fetchMock.mockRejectedValue(new Error('Network error'));

    render(<RemindersPanel />);

    await waitFor(() => {
      expect(screen.getByText('Network error')).toBeInTheDocument();
    });
  });

  it('handles API errors', async () => {
    fetchMock.mockResolvedValue({
      ok: false,
    });

    render(<RemindersPanel />);

    await waitFor(() => {
      expect(screen.getByText('Failed to fetch reminders')).toBeInTheDocument();
    });
  });

  it('marks reminder as complete', async () => {
    const user = userEvent.setup();
    fetchMock
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockReminders,
      })
      .mockResolvedValueOnce({
        ok: true,
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockReminders.map(r => 
          r.id === '1' ? { ...r, completed: true } : r
        ),
      });

    render(<RemindersPanel />);

    await waitFor(() => {
      expect(screen.getByText('Call to discuss proposal')).toBeInTheDocument();
    });

    const completeButtons = screen.getAllByTitle('Mark as complete');
    await user.click(completeButtons[0]);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:3001/api/reminders/1/complete',
        { method: 'POST' }
      );
    });
  });

  it('fetches reminders for specific customer', async () => {
    fetchMock.mockResolvedValue({
      ok: true,
      json: async () => [mockReminders[0]],
    });

    render(<RemindersPanel customerId="c1" />);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:3001/api/reminders/customer/c1'
      );
    });
  });

  it('applies limit parameter', async () => {
    fetchMock.mockResolvedValue({
      ok: true,
      json: async () => mockReminders,
    });

    render(<RemindersPanel limit={5} />);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:3001/api/reminders?limit=5'
      );
    });
  });

  it('styles completed reminders with opacity', async () => {
    fetchMock.mockResolvedValue({
      ok: true,
      json: async () => mockReminders,
    });

    const { container } = render(<RemindersPanel />);

    await waitFor(() => {
      expect(screen.getByText('Send presentation')).toBeInTheDocument();
    });

    const completedReminder = container.querySelector('.opacity-50');
    expect(completedReminder).toBeInTheDocument();
  });

  it('does not show complete button for completed reminders', async () => {
    fetchMock.mockResolvedValue({
      ok: true,
      json: async () => mockReminders,
    });

    render(<RemindersPanel />);

    await waitFor(() => {
      expect(screen.getByText('Send presentation')).toBeInTheDocument();
    });

    // Should have 2 complete buttons (for 2 incomplete reminders)
    const completeButtons = screen.getAllByTitle('Mark as complete');
    expect(completeButtons).toHaveLength(2);
  });
});
