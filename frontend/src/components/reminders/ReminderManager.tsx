import { FormEvent, useEffect, useState } from 'react';
import { reminderApi } from '../../services/api';
import type { Reminder } from '../../types';

interface ReminderManagerProps {
  customerId: string;
}

const initialFormState = {
  message: '',
  scheduled_for: '',
  type: 'follow_up',
};

export default function ReminderManager({ customerId }: ReminderManagerProps) {
  const [reminders, setReminders] = useState<Reminder[]>([]);
  const [formState, setFormState] = useState(initialFormState);
  const [error, setError] = useState<string | null>(null);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      try {
        const reminderList = await reminderApi.getAll(customerId);
        setReminders(reminderList);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load reminders');
      }
    };
    load();
  }, [customerId]);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!formState.scheduled_for) {
      setError('Please choose a reminder time.');
      return;
    }

    try {
      const payload = {
        customer_id: customerId,
        type: formState.type,
        message: formState.message,
        scheduled_for: new Date(formState.scheduled_for).toISOString(),
      };
      const reminder = await reminderApi.create(customerId, payload as any);
      setReminders((prev) => [reminder, ...prev]);
      setFormState(initialFormState);
      setStatusMessage('Reminder created successfully.');
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create reminder');
    }
  };

  return (
    <section className="space-y-3 rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
      <header>
        <h2 className="text-lg font-semibold text-slate-900">Reminder Management</h2>
        <p className="text-sm text-slate-500">Schedule follow-ups to keep prospects engaged.</p>
      </header>

      {error && <p className="text-sm text-red-500">{error}</p>}
      {statusMessage && <p className="text-sm text-emerald-600">{statusMessage}</p>}

      <form className="grid gap-3 md:grid-cols-3" onSubmit={handleSubmit}>
        <label className="flex flex-col text-sm text-slate-600">
          Message
          <input
            value={formState.message}
            onChange={(event) => setFormState({ ...formState, message: event.target.value })}
            className="mt-1 rounded-md border border-slate-200 px-3 py-2"
            placeholder="Reminder message"
          />
        </label>
        <label className="flex flex-col text-sm text-slate-600">
          Schedule for
          <input
            type="datetime-local"
            value={formState.scheduled_for}
            onChange={(event) => setFormState({ ...formState, scheduled_for: event.target.value })}
            className="mt-1 rounded-md border border-slate-200 px-3 py-2"
          />
        </label>
        <label className="flex flex-col text-sm text-slate-600">
          Type
          <select
            value={formState.type}
            onChange={(event) => setFormState({ ...formState, type: event.target.value })}
            className="mt-1 rounded-md border border-slate-200 px-3 py-2"
          >
            <option value="follow_up">Follow-up</option>
            <option value="call">Call</option>
            <option value="email">Email</option>
            <option value="meeting">Meeting</option>
          </select>
        </label>
        <div className="md:col-span-3">
          <button
            type="submit"
            className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-blue-700"
          >
            Create Reminder
          </button>
        </div>
      </form>

      <ul className="space-y-2">
        {reminders.map((reminder) => (
          <li key={reminder.id} className="rounded-md border border-slate-200 p-3 text-sm text-slate-600">
            <div className="flex items-center justify-between">
              <span className="font-medium text-slate-700">{reminder.message ?? 'Reminder'}</span>
              <span className="text-xs text-slate-500">
                {reminder.scheduled_for ? new Date(reminder.scheduled_for).toLocaleString() : 'N/A'}
              </span>
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
}
