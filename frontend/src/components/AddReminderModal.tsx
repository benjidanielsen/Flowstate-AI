import React, { useState } from 'react';
import { X } from 'lucide-react';
import { Reminder, ReminderType } from '../types';
import { reminderApi } from '../services/api';
import { useToast } from '../contexts/ToastContext';

interface AddReminderModalProps {
  customerId: string;
  onClose: () => void;
  onSuccess: () => void;
  existingReminder?: Reminder;
}

const AddReminderModal: React.FC<AddReminderModalProps> = ({
  customerId,
  onClose,
  onSuccess,
  existingReminder,
}) => {
  const { push } = useToast();
  const [message, setMessage] = useState(existingReminder?.message || '');
  const [scheduledFor, setScheduledFor] = useState(
    existingReminder?.scheduled_for
      ? new Date(existingReminder.scheduled_for).toISOString().slice(0, 16)
      : ''
  );
  const [type, setType] = useState<ReminderType>((existingReminder?.type as ReminderType) || ReminderType.FOLLOW_UP);
  const [repeatInterval, setRepeatInterval] = useState(existingReminder?.repeat_interval || '');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!message || !scheduledFor) {
      push('Message and Scheduled For date are required.', 'error');
      return;
    }

    setLoading(true);
    try {
      const reminderData = {
        customer_id: customerId,
        type,
        message,
        scheduled_for: new Date(scheduledFor),
        repeat_interval: repeatInterval || undefined,
        completed: false,
        updated_at: new Date().toISOString(),
      };

      if (existingReminder) {
        await reminderApi.update(customerId, existingReminder.id, reminderData);
        push('Reminder updated successfully!', 'success');
      } else {
        await reminderApi.create(customerId, reminderData);
        push('Reminder created successfully!', 'success');
      }
      onSuccess();
    } catch (error) {
      console.error('Error saving reminder:', error);
      push('Failed to save reminder.', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full flex justify-center items-center z-50">
      <div className="relative bg-white rounded-lg shadow-xl p-6 w-full max-w-md mx-auto">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-gray-900">
            {existingReminder ? 'Edit Reminder' : 'Add New Reminder'}
          </h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="message" className="block text-sm font-medium text-gray-700">Message</label>
            <textarea
              id="message"
              rows={3}
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2 focus:ring-primary-500 focus:border-primary-500"
              required
            ></textarea>
          </div>

          <div>
            <label htmlFor="scheduledFor" className="block text-sm font-medium text-gray-700">Scheduled For</label>
            <input
              type="datetime-local"
              id="scheduledFor"
              value={scheduledFor}
              onChange={(e) => setScheduledFor(e.target.value)}
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2 focus:ring-primary-500 focus:border-primary-500"
              required
            />
          </div>

          <div>
            <label htmlFor="type" className="block text-sm font-medium text-gray-700">Reminder Type</label>
            <select
              id="type"
              value={type}
              onChange={(e) => setType(e.target.value as ReminderType)}
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2 focus:ring-primary-500 focus:border-primary-500"
            >
              {Object.values(ReminderType).map((rt) => (
                <option key={rt} value={rt}>
                  {rt.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase())}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label htmlFor="repeatInterval" className="block text-sm font-medium text-gray-700">Repeat Interval (e.g., “daily”, “weekly”, “monthly”)</label>
            <input
              type="text"
              id="repeatInterval"
              value={repeatInterval}
              onChange={(e) => setRepeatInterval(e.target.value)}
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2 focus:ring-primary-500 focus:border-primary-500"
              placeholder="e.g., daily, weekly, monthly"
            />
          </div>

          <div className="flex justify-end space-x-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 text-sm font-medium text-white bg-primary-600 rounded-md hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Saving...' : (existingReminder ? 'Save Changes' : 'Add Reminder')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AddReminderModal;

