import React, { useState, useEffect } from 'react';
import './CrmDashboard.css';

const PIPELINE_STAGES = [
  'New',
  'Contacted',
  'Qualified',
  'Proposal Sent',
  'Negotiation',
  'Won',
  'Lost'
];

const sampleLeads = [
  { id: 1, name: 'Acme Corp', contact: 'alice@acme.com', stage: 'New' },
  { id: 2, name: 'Beta LLC', contact: 'bob@beta.com', stage: 'Contacted' },
  { id: 3, name: 'Gamma Inc', contact: 'carol@gamma.com', stage: 'Qualified' },
  { id: 4, name: 'Delta Co', contact: 'dave@delta.com', stage: 'Proposal Sent' },
  { id: 5, name: 'Epsilon Ltd', contact: 'ellen@epsilon.com', stage: 'Negotiation' }
];

function CrmDashboard() {
  const [leads, setLeads] = useState([]);
  const [draggedLead, setDraggedLead] = useState(null);

  useEffect(() => {
    // In real app, fetch leads from API
    setLeads(sampleLeads);
  }, []);

  const onDragStart = (e, lead) => {
    setDraggedLead(lead);
  };

  const onDragOver = (e) => {
    e.preventDefault();
  };

  const onDrop = (e, newStage) => {
    e.preventDefault();
    if (draggedLead) {
      setLeads(prevLeads => 
        prevLeads.map(lead => {
          if (lead.id === draggedLead.id) {
            return { ...lead, stage: newStage };
          }
          return lead;
        })
      );
      setDraggedLead(null);
    }
  };

  const onLeadClick = (lead) => {
    alert(`Lead Details:\nName: ${lead.name}\nContact: ${lead.contact}\nStage: ${lead.stage}`);
  };

  return (
    <div className="crm-dashboard">
      <h1>CRM Leads Pipeline</h1>
      <div className="pipeline-container">
        {PIPELINE_STAGES.map(stage => (
          <div
            key={stage}
            className="pipeline-stage"
            onDragOver={onDragOver}
            onDrop={(e) => onDrop(e, stage)}
          >
            <h3>{stage}</h3>
            <div className="leads-list">
              {leads.filter(lead => lead.stage === stage).map(lead => (
                <div
                  key={lead.id}
                  className="lead-card"
                  draggable
                  onDragStart={(e) => onDragStart(e, lead)}
                  onClick={() => onLeadClick(lead)}
                  title={`Contact: ${lead.contact}`}
                >
                  {lead.name}
                </div>
              ))}
              {leads.filter(lead => lead.stage === stage).length === 0 && (
                <p className="empty-text">No leads</p>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default CrmDashboard;
