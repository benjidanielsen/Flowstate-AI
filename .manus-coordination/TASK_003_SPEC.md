# TASK-003: Build Frontend Qualification Form

## Objective
Create UI for Frazer Method qualification questions

## File to Create
frontend/src/pages/QualificationForm.tsx

## Implementation
```typescript
import React, { useState } from 'react';
import { customerApi } from '../services/api';

export const QualificationForm: React.FC<{ customerId: string }> = ({ customerId }) => {
  const [prospectWhy, setProspectWhy] = useState('');
  const [qualificationData, setQualificationData] = useState({
    goals: '',
    timeline: '',
    budget: '',
    decision_maker: ''
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      await customerApi.update(customerId, {
        prospect_why: prospectWhy,
        qualification_data: JSON.stringify(qualificationData)
      });
      alert('Qualification saved!');
    } catch (error) {
      alert('Error saving qualification');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium">Prospect's WHY</label>
        <textarea
          value={prospectWhy}
          onChange={(e) => setProspectWhy(e.target.value)}
          className="mt-1 block w-full rounded-md border-gray-300"
          rows={3}
          placeholder="Why do they want to join?"
        />
      </div>
      
      <div>
        <label className="block text-sm font-medium">Goals</label>
        <input
          type="text"
          value={qualificationData.goals}
          onChange={(e) => setQualificationData({...qualificationData, goals: e.target.value})}
          className="mt-1 block w-full rounded-md border-gray-300"
        />
      </div>
      
      <div>
        <label className="block text-sm font-medium">Timeline</label>
        <input
          type="text"
          value={qualificationData.timeline}
          onChange={(e) => setQualificationData({...qualificationData, timeline: e.target.value})}
          className="mt-1 block w-full rounded-md border-gray-300"
        />
      </div>
      
      <button type="submit" className="bg-blue-500 text-white px-4 py-2 rounded">
        Save Qualification
      </button>
    </form>
  );
};
```

## Add Route
In frontend/src/App.tsx or router:
```typescript
<Route path="/customers/:id/qualify" element={<QualificationForm />} />
```

## Done When
- Form renders correctly
- Saves to backend API
- Shows success/error messages
- Looks good visually

GRAB IT!
