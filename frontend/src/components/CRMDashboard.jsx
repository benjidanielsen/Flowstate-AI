import React, { useState } from 'react';
import './CRMDashboard.css';

const pipelineStages = [
  'New',
  'Contacted',
  'Qualified',
  'Proposal Sent',
  'Negotiation',
  'Won',
  'Lost'
];

// Sample data for demonstration; in real app this would come from API
const initialLeads = [
  { id: 1, name: 'Alice Johnson', company: 'Acme Corp', email: 'alice@acme.com', stage: 'New' },
  { id: 2, name: 'Bob Smith', company: 'Beta LLC', email: 'bob@beta.com', stage: 'Contacted' },
  { id: 3, name: 'Charlie Davis', company: 'Gamma Inc', email: 'charlie@gamma.com', stage: 'Qualified' },
  { id: 4, name: 'Dana Lee', company: 'Delta Co', email: 'dana@delta.co', stage: 'Proposal Sent' }
];

export default function CRMDashboard() {
  const [leads, setLeads] = useState(initialLeads);
  const [selectedLead, setSelectedLead] = useState(null);
  const [isEditing, setIsEditing] = useState(false);

  function moveLead(leadId, direction) {
    setLeads(current => {
      return current.map(lead => {
        if (lead.id === leadId) {
          const currentIndex = pipelineStages.indexOf(lead.stage);
          let newIndex = currentIndex + direction;
          if (newIndex < 0) newIndex = 0;
          if (newIndex >= pipelineStages.length) newIndex = pipelineStages.length - 1;
          return { ...lead, stage: pipelineStages[newIndex] };
        }
        return lead;
      });
    });
  }

  function selectLead(lead) {
    setSelectedLead(lead);
    setIsEditing(false);
  }

  function handleFieldChange(e) {
    const { name, value } = e.target;
    setSelectedLead(prev => ({ ...prev, [name]: value }));
  }

  function saveLead() {
    setLeads(current => current.map(lead => (lead.id === selectedLead.id ? selectedLead : lead)));
    setIsEditing(false);
  }

  function addNewLead() {
    const newLead = {
      id: Date.now(),
      name: '',
      company: '',
      email: '',
      stage: 'New'
    };
    setLeads(current => [newLead, ...current]);
    setSelectedLead(newLead);
    setIsEditing(true);
  }

  function deleteLead(leadId) {
    setLeads(current => current.filter(lead => lead.id !== leadId));
    if (selectedLead && selectedLead.id === leadId) {
      setSelectedLead(null);
      setIsEditing(false);
    }
  }

  return (
    <div className="crm-dashboard">
      <header>
        <h1>Flowstate-AI CRM Dashboard</h1>
        <button onClick={addNewLead} className="add-lead-btn">+ Add Lead</button>
      </header>
      <div className="pipeline-container">
        {pipelineStages.map(stage => (
          <div key={stage} className="pipeline-stage">
            <h2>{stage}</h2>
            <div className="leads-list">
              {leads.filter(lead => lead.stage === stage).map(lead => (
                <div
                  key={lead.id}
                  className={`lead-card ${selectedLead && selectedLead.id === lead.id ? 'selected' : ''}`}
                  onClick={() => selectLead(lead)}
                >
                  <strong>{lead.name || <em>Unnamed</em>}</strong>
                  <small>{lead.company}</small>
                </div>
              ))}
              {leads.filter(lead => lead.stage === stage).length === 0 && <p className="empty-text">No leads</p>}
            </div>
          </div>
        ))}
      </div>

      <aside className="lead-detail-panel">
        {selectedLead ? (
          <>
            <h2>Lead Details</h2>
            {!isEditing ? (
              <div className="lead-info">
                <p><strong>Name:</strong> {selectedLead.name || '—'}</p>
                <p><strong>Company:</strong> {selectedLead.company || '—'}</p>
                <p><strong>Email:</strong> {selectedLead.email || '—'}</p>
                <p><strong>Stage:</strong> {selectedLead.stage}</p>
                <div className="buttons">
                  <button onClick={() => setIsEditing(true)}>Edit</button>
                  <button onClick={() => deleteLead(selectedLead.id)} className="delete-btn">Delete</button>
                </div>
                <div className="move-buttons">
                  <button
                    disabled={pipelineStages.indexOf(selectedLead.stage) === 0}
                    onClick={() => moveLead(selectedLead.id, -1)}
                  >
                    &larr; Prev Stage
                  </button>
                  <button
                    disabled={pipelineStages.indexOf(selectedLead.stage) === pipelineStages.length - 1}
                    onClick={() => moveLead(selectedLead.id, 1)}
                  >
                    Next Stage &rarr;
                  </button>
                </div>
              </div>
            ) : (
              <div className="lead-edit-form">
                <label>
                  Name
                  <input type="text" name="name" value={selectedLead.name} onChange={handleFieldChange} />
                </label>
                <label>
                  Company
                  <input type="text" name="company" value={selectedLead.company} onChange={handleFieldChange} />
                </label>
                <label>
                  Email
                  <input type="email" name="email" value={selectedLead.email} onChange={handleFieldChange} />
                </label>
                <label>
                  Stage
                  <select name="stage" value={selectedLead.stage} onChange={handleFieldChange}>
                    {pipelineStages.map(stage => (
                      <option key={stage} value={stage}>{stage}</option>
                    ))}
                  </select>
                </label>
                <div className="buttons">
                  <button onClick={saveLead}>Save</button>
                  <button onClick={() => setIsEditing(false)} className="cancel-btn">Cancel</button>
                </div>
              </div>
            )}
          </>
        ) : (
          <p>Select a lead to view details</p>
        )}
      </aside>
    </div>
  );
}
