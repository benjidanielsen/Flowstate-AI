import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import QualificationQuestionnaire from '../QualificationQuestionnaire';
import { Customer, PipelineStatus } from '../../types';
import * as api from '../../services/api';

// Mock the API
vi.mock('../../services/api', () => ({
  customerApi: {
    update: vi.fn(),
  },
}));

describe('QualificationQuestionnaire', () => {
  const mockCustomer: Customer = {
    id: '1',
    name: 'John Doe',
    email: 'john@example.com',
    status: PipelineStatus.INVITED,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  };

  const mockOnComplete = vi.fn();
  const mockOnCancel = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders the qualification form correctly', () => {
    render(
      <QualificationQuestionnaire
        customer={mockCustomer}
        onComplete={mockOnComplete}
        onCancel={mockOnCancel}
      />
    );

    expect(screen.getByText(/Prospect Qualification - Frazer Method/i)).toBeInTheDocument();
    expect(screen.getByText(/The Frazer Method: Prospect's WHY/i)).toBeInTheDocument();
    expect(screen.getByText(/Customer: John Doe/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Qualify Prospect/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Cancel/i })).toBeInTheDocument();
  });

  it('displays customer name in the question', () => {
    render(
      <QualificationQuestionnaire
        customer={mockCustomer}
        onComplete={mockOnComplete}
        onCancel={mockOnCancel}
      />
    );

    expect(screen.getByText(/What is John's WHY/i)).toBeInTheDocument();
  });

  it('validates required field', () => {
    render(
      <QualificationQuestionnaire
        customer={mockCustomer}
        onComplete={mockOnComplete}
        onCancel={mockOnCancel}
      />
    );

    const textarea = screen.getByPlaceholderText(/Describe their core motivation/i);
    expect(textarea).toBeRequired();
    expect(textarea).toHaveValue('');
  });

  it('submits form successfully with valid data', async () => {
    const user = userEvent.setup();
    const updatedCustomer: Customer = {
      ...mockCustomer,
      prospect_why: 'Wants financial freedom',
      status: PipelineStatus.QUALIFIED,
    };

    (api.customerApi.update as any).mockResolvedValue(updatedCustomer);

    render(
      <QualificationQuestionnaire
        customer={mockCustomer}
        onComplete={mockOnComplete}
        onCancel={mockOnCancel}
      />
    );

    const textarea = screen.getByPlaceholderText(/Describe their core motivation/i);
    await user.type(textarea, 'Wants financial freedom to spend more time with kids');

    const submitButton = screen.getByRole('button', { name: /Qualify Prospect/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(api.customerApi.update).toHaveBeenCalledWith('1', {
        prospect_why: 'Wants financial freedom to spend more time with kids',
        status: 'Qualified',
      });
    });

    expect(mockOnComplete).toHaveBeenCalledWith(updatedCustomer);
    expect(mockOnCancel).not.toHaveBeenCalled();
  });

  it('displays loading state during submission', async () => {
    const user = userEvent.setup();
    (api.customerApi.update as any).mockImplementation(
      () => new Promise((resolve) => setTimeout(resolve, 100))
    );

    render(
      <QualificationQuestionnaire
        customer={mockCustomer}
        onComplete={mockOnComplete}
        onCancel={mockOnCancel}
      />
    );

    const textarea = screen.getByPlaceholderText(/Describe their core motivation/i);
    await user.type(textarea, 'Test motivation');

    const submitButton = screen.getByRole('button', { name: /Qualify Prospect/i });
    await user.click(submitButton);

    expect(screen.getByText(/Saving.../i)).toBeInTheDocument();
    expect(submitButton).toBeDisabled();
  });

  it('handles API errors gracefully', async () => {
    const user = userEvent.setup();
    const errorMessage = 'Failed to save qualification';
    (api.customerApi.update as any).mockRejectedValue({
      response: { data: { error: errorMessage } },
    });

    render(
      <QualificationQuestionnaire
        customer={mockCustomer}
        onComplete={mockOnComplete}
        onCancel={mockOnCancel}
      />
    );

    const textarea = screen.getByPlaceholderText(/Describe their core motivation/i);
    await user.type(textarea, 'Test motivation');

    const submitButton = screen.getByRole('button', { name: /Qualify Prospect/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(errorMessage)).toBeInTheDocument();
    }, { timeout: 3000 });

    // Verify API was called but failed
    expect(api.customerApi.update).toHaveBeenCalled();
  });

  it('calls onCancel when cancel button is clicked', async () => {
    const user = userEvent.setup();

    render(
      <QualificationQuestionnaire
        customer={mockCustomer}
        onComplete={mockOnComplete}
        onCancel={mockOnCancel}
      />
    );

    const cancelButton = screen.getByRole('button', { name: /Cancel/i });
    await user.click(cancelButton);

    expect(mockOnCancel).toHaveBeenCalled();
    expect(mockOnComplete).not.toHaveBeenCalled();
  });

  it('pre-fills textarea if customer already has prospect_why', () => {
    const customerWithWhy: Customer = {
      ...mockCustomer,
      prospect_why: 'Existing motivation',
    };

    render(
      <QualificationQuestionnaire
        customer={customerWithWhy}
        onComplete={mockOnComplete}
        onCancel={mockOnCancel}
      />
    );

    const textarea = screen.getByPlaceholderText(/Describe their core motivation/i) as HTMLTextAreaElement;
    expect(textarea.value).toBe('Existing motivation');
  });

  it('disables buttons during loading', async () => {
    const user = userEvent.setup();
    (api.customerApi.update as any).mockImplementation(
      () => new Promise((resolve) => setTimeout(resolve, 100))
    );

    render(
      <QualificationQuestionnaire
        customer={mockCustomer}
        onComplete={mockOnComplete}
        onCancel={mockOnCancel}
      />
    );

    const textarea = screen.getByPlaceholderText(/Describe their core motivation/i);
    await user.type(textarea, 'Test');

    const submitButton = screen.getByRole('button', { name: /Qualify Prospect/i });
    await user.click(submitButton);

    const cancelButton = screen.getByRole('button', { name: /Cancel/i });
    expect(submitButton).toBeDisabled();
    expect(cancelButton).toBeDisabled();
  });
});
