import { useEffect, useState } from 'react';
import { customerApi, pipelineApi, reminderApi } from '../../services/api';
import type { Customer, PipelineStage, Reminder } from '../../types';

interface CustomerDetailViewProps {
  customerId: string;
}

export default function CustomerDetailView({ customerId }: CustomerDetailViewProps) {
  const [customer, setCustomer] = useState<Customer | null>(null);
  const [reminders, setReminders] = useState<Reminder[]>([]);
  const [availableStages, setAvailableStages] = useState<PipelineStage[]>([]);
  const [selectedStage, setSelectedStage] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      try {
        const [customerResponse, reminderResponse, pipelines] = await Promise.all([
          customerApi.getById(customerId),
          reminderApi.getAll(customerId),
          pipelineApi.list(),
        ]);
        setCustomer(customerResponse);
        setReminders(reminderResponse);
        const stages = pipelines.flatMap((pipeline) => pipeline.stages);
        setAvailableStages(stages);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load customer');
      }
    };

    load();
  }, [customerId]);

  const handleAssignStage = async () => {
    if (!selectedStage) return;
    try {
      const updatedCustomer = await pipelineApi.assignCustomerStage(customerId, selectedStage);
      setCustomer(updatedCustomer);
      setStatusMessage('Pipeline stage updated successfully.');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to assign stage');
    }
  };

  return (
    <section className="space-y-4 rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
      <header>
        <h2 className="text-lg font-semibold text-slate-900">Customer Details</h2>
        {customer && <p className="text-sm text-slate-500">{customer.email ?? 'No email on file'}</p>}
      </header>

      {error && <p className="text-sm text-red-500">{error}</p>}
      {statusMessage && <p className="text-sm text-emerald-600">{statusMessage}</p>}

      {customer ? (
        <div className="grid gap-4 md:grid-cols-2">
          <article className="space-y-2">
            <h3 className="text-sm font-semibold text-slate-700">Profile</h3>
            <dl className="space-y-1 text-sm text-slate-600">
              <div>
                <dt className="font-medium">Name</dt>
                <dd>{customer.name}</dd>
              </div>
              <div>
                <dt className="font-medium">Status</dt>
                <dd>{customer.status}</dd>
              </div>
              {customer.pipeline_stage_id && (
                <div>
                  <dt className="font-medium">Pipeline Stage</dt>
                  <dd>{availableStages.find((stage) => stage.id === customer.pipeline_stage_id)?.name ?? 'Unknown'}</dd>
                </div>
              )}
              {customer.notes && (
                <div>
                  <dt className="font-medium">Notes</dt>
                  <dd className="whitespace-pre-wrap">{customer.notes}</dd>
                </div>
              )}
            </dl>
          </article>

          <article className="space-y-2">
            <h3 className="text-sm font-semibold text-slate-700">Assign Pipeline Stage</h3>
            <div className="flex flex-wrap items-center gap-2">
              <select
                value={selectedStage}
                onChange={(event) => setSelectedStage(event.target.value)}
                className="flex-1 rounded-md border border-slate-200 px-3 py-2 text-sm"
              >
                <option value="">Select stage…</option>
                {availableStages.map((stage) => (
                  <option key={stage.id} value={stage.id}>
                    {stage.name}
                  </option>
                ))}
              </select>
              <button
                onClick={handleAssignStage}
                className="rounded-md bg-blue-600 px-3 py-2 text-sm font-medium text-white transition hover:bg-blue-700"
              >
                Assign
              </button>
            </div>
          </article>
        </div>
      ) : (
        <p className="text-sm text-slate-500">Loading customer…</p>
      )}

      <section>
        <h3 className="text-sm font-semibold text-slate-700">Upcoming Reminders</h3>
        {reminders.length ? (
          <ul className="mt-2 space-y-2">
            {reminders.map((reminder) => (
              <li key={reminder.id} className="rounded-md border border-slate-200 p-3 text-sm text-slate-600">
                <p className="font-medium text-slate-700">{reminder.message ?? reminder.title ?? 'Reminder'}</p>
                <p className="text-xs text-slate-500">
                  Due {reminder.scheduled_for ? new Date(reminder.scheduled_for).toLocaleString() : 'N/A'}
                </p>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-slate-500">No reminders scheduled.</p>
        )}
      </section>
    </section>
  );
}
