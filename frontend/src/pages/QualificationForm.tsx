import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';

interface QualificationData {
  goals: string;
  timeline: string;
  budget: string;
  decision_maker: string;
  pain_points: string;
  current_situation: string;
}

export const QualificationForm: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [customerName, setCustomerName] = useState('');
  const [prospectWhy, setProspectWhy] = useState('');
  const [qualificationData, setQualificationData] = useState<QualificationData>({
    goals: '',
    timeline: '',
    budget: '',
    decision_maker: '',
    pain_points: '',
    current_situation: ''
  });

  useEffect(() => {
    const loadCustomer = async () => {
      try {
        const response = await fetch(`http://localhost:3001/api/qualification/${id}`);
        if (response.ok) {
          const data = await response.json();
          setCustomerName(data.name || '');
          setProspectWhy(data.prospect_why || '');
          if (data.qualification_data) {
            setQualificationData((prev) => ({ ...prev, ...data.qualification_data }));
        }
      }
    } catch (error) {
      console.error('Error loading customer:', error);
    }
    };
    
    loadCustomer();
  }, [id]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const response = await fetch('http://localhost:3001/api/qualification', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          customer_id: id,
          prospect_why: prospectWhy,
          qualification_data: qualificationData
        })
      });
      
      if (response.ok) {
        alert('Qualification saved successfully!');
        navigate(`/customers/${id}`);
      } else {
        alert('Error saving qualification');
      }
    } catch (error) {
      console.error('Error saving qualification:', error);
      alert('Error saving qualification');
    } finally {
      setLoading(false);
    }
  };

  const updateField = (field: keyof QualificationData, value: string) => {
    setQualificationData({...qualificationData, [field]: value});
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-md p-6">
        <h1 className="text-2xl font-bold mb-6">
          Frazer Method Qualification: {customerName}
        </h1>
        
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Prospect's WHY - Most Important */}
          <div className="bg-blue-50 p-4 rounded-lg border-2 border-blue-200">
            <label className="block text-lg font-bold text-blue-900 mb-2">
              🎯 Prospect&apos;s WHY (Required for Qualification)
            </label>
            <textarea
              value={prospectWhy}
              onChange={(e) => setProspectWhy(e.target.value)}
              className="w-full px-3 py-2 border border-blue-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows={4}
              placeholder="Why do they want to join? What's their core motivation? This is the foundation of the Frazer Method."
              required
            />
            <p className="text-sm text-blue-700 mt-2">
              💡 This is the most important question. Understanding their WHY helps you serve them better.
            </p>
          </div>

          {/* Current Situation */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Current Situation
            </label>
            <textarea
              value={qualificationData.current_situation}
              onChange={(e) => updateField('current_situation', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows={3}
              placeholder="Where are they now? What's their current work/life situation?"
            />
          </div>

          {/* Goals */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Goals & Dreams
            </label>
            <textarea
              value={qualificationData.goals}
              onChange={(e) => updateField('goals', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows={3}
              placeholder="What do they want to achieve? Where do they see themselves in 1-3 years?"
            />
          </div>

          {/* Pain Points */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Pain Points & Challenges
            </label>
            <textarea
              value={qualificationData.pain_points}
              onChange={(e) => updateField('pain_points', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows={3}
              placeholder="What problems are they facing? What keeps them up at night?"
            />
          </div>

          {/* Timeline */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Timeline & Urgency
            </label>
            <input
              type="text"
              value={qualificationData.timeline}
              onChange={(e) => updateField('timeline', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="When do they want to start? How urgent is this for them?"
            />
          </div>

          {/* Budget/Investment Mindset */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Investment Mindset
            </label>
            <input
              type="text"
              value={qualificationData.budget}
              onChange={(e) => updateField('budget', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Are they ready to invest in themselves? What's their mindset about opportunity cost?"
            />
          </div>

          {/* Decision Maker */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Decision Making
            </label>
            <input
              type="text"
              value={qualificationData.decision_maker}
              onChange={(e) => updateField('decision_maker', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Do they make their own decisions? Any partners/family to consult?"
            />
          </div>

          {/* Action Buttons */}
          <div className="flex gap-4 pt-4">
            <button
              type="submit"
              disabled={loading || !prospectWhy}
              className="flex-1 bg-blue-600 text-white px-6 py-3 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-medium"
            >
              {loading ? 'Saving...' : 'Save Qualification'}
            </button>
            <button
              type="button"
              onClick={() => navigate(`/customers/${id}`)}
              className="px-6 py-3 border border-gray-300 rounded-md hover:bg-gray-50"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
