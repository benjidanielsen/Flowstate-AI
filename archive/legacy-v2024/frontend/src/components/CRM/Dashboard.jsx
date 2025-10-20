import React, { useState, useEffect } from 'react';
import './Dashboard.css';

const PIPELINE_STAGES = [
  'New',
  'Contacted',
  'Qualified',
  'Proposal Sent',
  'Negotiation',
  'Closed Won',
  'Closed Lost'
];

// Sample lead data structure for demo purposes
const sampleLeads = [
  { id: 1, name: 'Acme Corp', contact: 'alice@acme.com', stage: 'New' },
  { id: 2, name: 'Beta LLC', contact: 'bob@beta.com', stage: 'Contacted' },
  { id: 3, name: 'Gamma Inc', contact: 'carol@gamma.com', stage: 'Qualified' },
  { id: 4, name: 'Delta Ltd.', contact: 'dave@delta.com', stage: 'Proposal Sent' },
  { id: 5, name: 'Epsilon Co.', contact: 'eve@epsilon.com', stage: 'Negotiation' }
];

function Dashboard() {
  const [leads, setLeads] = useState([]);
  const [draggedLeadId, setDraggedLeadId] = useState(null);

  useEffect(() => {
    // In real app, fetch leads from backend here
    setLeads(sampleLeads);
  }, []);

  function onDragStart(e, leadId) {
    setDraggedLeadId(leadId);
    e.dataTransfer.effectAllowed = 'move';
  }

  function onDragOver(e) {
    e.preventDefault();
  }

  function onDrop(e, stage) {
    e.preventDefault();
    if (draggedLeadId == null) return;

    setLeads(currentLeads =>
      currentLeads.map(lead => {
        if (lead.id === draggedLeadId) {
          return { ...lead, stage };
        }
        return lead;
      })
    );
    setDraggedLeadId(null);
  }

  function onDragEnd() {
    setDraggedLeadId(null);
  }

  return (
    <div className="dashboard-container">
      <h1>CRM Pipeline Dashboard</h1>
      <div className="pipeline">
        {PIPELINE_STAGES.map(stage => (
          <div
            key={stage}
            className="pipeline-stage"
            onDragOver={onDragOver}
            onDrop={e => onDrop(e, stage)}
          >
            <h2>{stage}</h2>
            <div className="leads-list">
              {leads
                .filter(lead => lead.stage === stage)
                .map(lead => (
                  <div
                    key={lead.id}
                    className="lead-card"
                    draggable
                    onDragStart={e => onDragStart(e, lead.id)}
                    onDragEnd={onDragEnd}
                    title={`${lead.name} - ${lead.contact}`}
                  >
                    <strong>{lead.name}</strong>
                    <p>{lead.contact}</p>
                  </div>
                ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Dashboard;
