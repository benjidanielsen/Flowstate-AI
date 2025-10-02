import React, { useState } from 'react';
import { Customer } from '../types';
import { customerApi } from '../services/api';

interface QualificationQuestionnaireProps {
  customer: Customer;
  onComplete: (updatedCustomer: Customer) => void;
  onCancel: () => void;
}

const QualificationQuestionnaire: React.FC<QualificationQuestionnaireProps> = ({
  customer,
  onComplete,
  onCancel,
}) => {
  const [prospectWhy, setProspectWhy] = useState(customer.prospect_why || '');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!prospectWhy.trim()) {
      setError('Please answer the Prospect WHY question');
      return;
    }

    try {
      setLoading(true);
      setError('');
      const updated = await customerApi.update(customer.id, {
        prospect_why: prospectWhy,
        status: 'QUALIFIED' as any,
      });
      onComplete(updated);
    } catch (err: unknown) {
      const error = err as { response?: { data?: { error?: string } } };
      setError(error.response?.data?.error || 'Failed to save qualification');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <h2 className="text-2xl font-bold mb-4">Prospect Qualification - Frazer Method</h2>
        
        <div className="mb-6 p-4 bg-blue-50 rounded-lg">
          <h3 className="font-semibold text-blue-900 mb-2">The Frazer Method: Prospect&apos;s WHY</h3>
          <p className="text-sm text-blue-800">
            Understanding the prospect&apos;s core motivation is essential. Ask: &quot;What is driving you to consider this opportunity?&quot;
            Listen for their deeper reasons - financial freedom, time with family, personal growth, etc.
          </p>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Customer: {customer.name}
            </label>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              What is {customer.name.split(' ')[0]}&apos;s WHY? *
            </label>
            <textarea
              value={prospectWhy}
              onChange={(e) => setProspectWhy(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              rows={6}
              placeholder="Describe their core motivation, goals, and reasons for considering this opportunity..."
              required
            />
            <p className="mt-2 text-sm text-gray-600">
              Examples: &quot;Wants financial freedom to spend more time with kids&quot;, &quot;Seeking additional income to pay off debt&quot;, 
              &quot;Looking for personal growth and entrepreneurship&quot;
            </p>
          </div>

          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
              {error}
            </div>
          )}

          <div className="flex justify-end space-x-3">
            <button
              type="button"
              onClick={onCancel}
              className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
              disabled={loading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
              disabled={loading}
            >
              {loading ? 'Saving...' : 'Qualify Prospect'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default QualificationQuestionnaire;
