import React, { useEffect, useState } from 'react';
import { Bell, Check, Clock, User } from 'lucide-react';

interface Reminder {
  id: string;
  customer_id: string;
  customer_name?: string;
  type: string;
  description: string;
  due_date: string;
  completed: boolean;
  created_at: string;
}

interface RemindersPanelProps {
  customerId?: string;
  limit?: number;
}

const RemindersPanel: React.FC<RemindersPanelProps> = ({ customerId, limit = 10 }) => {
  const [reminders, setReminders] = useState<Reminder[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchReminders();
  }, [customerId]);

  const fetchReminders = async () => {
    try {
      setLoading(true);
      const url = customerId 
        ? `http://localhost:3001/api/reminders/customer/${customerId}`
        : `http://localhost:3001/api/reminders?limit=${limit}`;
      
      const response = await fetch(url);
      if (!response.ok) throw new Error('Failed to fetch reminders');
      
      const data = await response.json();
      setReminders(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleComplete = async (reminderId: string) => {
    try {
      const response = await fetch(`http://localhost:3001/api/reminders/${reminderId}/complete`, {
        method: 'POST',
      });
      
      if (!response.ok) throw new Error('Failed to complete reminder');
      
      // Refresh reminders
      fetchReminders();
    } catch (err: any) {
      setError(err.message);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = date.getTime() - now.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    
    if (diffDays < 0) return 'Overdue';
    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Tomorrow';
    if (diffDays < 7) return `In ${diffDays} days`;
    
    return date.toLocaleDateString();
  };

  const getUrgencyColor = (dueDate: string) => {
    const date = new Date(dueDate);
    const now = new Date();
    const diffDays = Math.floor((date.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
    
    if (diffDays < 0) return 'border-l-4 border-red-500 bg-red-50';
    if (diffDays === 0) return 'border-l-4 border-orange-500 bg-orange-50';
    if (diffDays <= 2) return 'border-l-4 border-yellow-500 bg-yellow-50';
    return 'border-l-4 border-blue-500 bg-white';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
        {error}
      </div>
    );
  }

  if (reminders.length === 0) {
    return (
      <div className="text-center p-8 text-gray-500">
        <Bell className="mx-auto mb-2" size={48} />
        <p>No reminders found</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold flex items-center">
          <Bell className="mr-2" size={20} />
          Upcoming Reminders
        </h3>
        <span className="text-sm text-gray-600">
          {reminders.filter(r => !r.completed).length} active
        </span>
      </div>

      {reminders.map((reminder) => (
        <div
          key={reminder.id}
          className={`p-4 rounded-lg ${getUrgencyColor(reminder.due_date)} ${
            reminder.completed ? 'opacity-50' : ''
          }`}
        >
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center space-x-2 mb-1">
                {reminder.customer_name && (
                  <span className="flex items-center text-sm text-gray-600">
                    <User size={14} className="mr-1" />
                    {reminder.customer_name}
                  </span>
                )}
                <span className="text-xs px-2 py-1 bg-gray-100 rounded">
                  {reminder.type}
                </span>
              </div>
              
              <p className={`text-sm ${reminder.completed ? 'line-through' : 'font-medium'}`}>
                {reminder.description}
              </p>
              
              <div className="flex items-center mt-2 text-xs text-gray-600">
                <Clock size={12} className="mr-1" />
                {formatDate(reminder.due_date)}
              </div>
            </div>

            {!reminder.completed && (
              <button
                onClick={() => handleComplete(reminder.id)}
                className="ml-4 p-2 text-green-600 hover:bg-green-100 rounded-lg transition-colors"
                title="Mark as complete"
              >
                <Check size={20} />
              </button>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};

export default RemindersPanel;
