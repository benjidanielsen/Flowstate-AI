import React, { useState } from 'react';

const initialStages = [
  { id: 'stage-1', title: 'New Leads', leads: [
    { id: 'lead-1', name: 'Alice Johnson' },
    { id: 'lead-2', name: 'Bob Smith' }
  ]},
  { id: 'stage-2', title: 'Contacted', leads: [
    { id: 'lead-3', name: 'Charlie Brown' }
  ]},
  { id: 'stage-3', title: 'Qualified', leads: []},
  { id: 'stage-4', title: 'Proposal Sent', leads: []},
  { id: 'stage-5', title: 'Closed', leads: []}
];

function Pipeline() {
  const [stages, setStages] = useState(initialStages);
  const [draggedLead, setDraggedLead] = useState(null);

  function onDragStart(e, lead, sourceStageId) {
    e.dataTransfer.effectAllowed = 'move';
    setDraggedLead({ lead, sourceStageId });
  }

  function onDragOver(e) {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
  }

  function onDrop(e, targetStageId) {
    e.preventDefault();
    if (!draggedLead) return;

    const { lead, sourceStageId } = draggedLead;

    if (sourceStageId === targetStageId) {
      setDraggedLead(null);
      return; // no change
    }

    setStages(prevStages => {
      // Remove lead from source stage
      const newStages = prevStages.map(stage => {
        if (stage.id === sourceStageId) {
          return { ...stage, leads: stage.leads.filter(l => l.id !== lead.id) };
        }
        return stage;
      });

      // Add lead to target stage
      return newStages.map(stage => {
        if (stage.id === targetStageId) {
          return { ...stage, leads: [...stage.leads, lead] };
        }
        return stage;
      });
    });

    setDraggedLead(null);
  }

  return (
    <div style={{ display: 'flex', gap: '16px', padding: '16px', overflowX: 'auto' }}>
      {stages.map(stage => (
        <div
          key={stage.id}
          onDragOver={onDragOver}
          onDrop={e => onDrop(e, stage.id)}
          style={{
            backgroundColor: '#f4f6f8',
            borderRadius: '6px',
            width: '220px',
            minHeight: '300px',
            padding: '12px',
            display: 'flex',
            flexDirection: 'column'
          }}
        >
          <h3 style={{ textAlign: 'center' }}>{stage.title}</h3>
          <div style={{ flexGrow: 1 }}>
            {stage.leads.map(lead => (
              <div
                key={lead.id}
                draggable
                onDragStart={e => onDragStart(e, lead, stage.id)}
                style={{
                  padding: '8px',
                  margin: '6px 0',
                  backgroundColor: 'white',
                  borderRadius: '4px',
                  boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
                  cursor: 'grab'
                }}
              >
                {lead.name}
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

export default Pipeline;
