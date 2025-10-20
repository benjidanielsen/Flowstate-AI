import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './LeadDetailView.css';

const LeadDetailView = ({ leadId }) => {
  const [lead, setLead] = useState(null);
  const [notes, setNotes] = useState([]);
  const [history, setHistory] = useState([]);
  const [newNote, setNewNote] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchLeadDetails = async () => {
      setLoading(true);
      try {
        const [leadRes, notesRes, historyRes] = await Promise.all([
          axios.get(`/api/leads/${leadId}`),
          axios.get(`/api/leads/${leadId}/notes`),
          axios.get(`/api/leads/${leadId}/history`),
        ]);
        setLead(leadRes.data);
        setNotes(notesRes.data);
        setHistory(historyRes.data);
        setError(null);
      } catch (e) {
        setError('Failed to load lead details.');
      } finally {
        setLoading(false);
      }
    };

    if (leadId) {
      fetchLeadDetails();
    }
  }, [leadId]);

  const handleAddNote = async () => {
    if (!newNote.trim()) return;
    try {
      const res = await axios.post(`/api/leads/${leadId}/notes`, { content: newNote });
      setNotes(prev => [res.data, ...prev]);
      setNewNote('');
    } catch (e) {
      alert('Failed to add note.');
    }
  };

  const handleAction = async (actionType) => {
    try {
      await axios.post(`/api/leads/${leadId}/actions`, { action: actionType });
      alert(`Action '${actionType}' performed.`);
      // Optionally refresh history
      const historyRes = await axios.get(`/api/leads/${leadId}/history`);
      setHistory(historyRes.data);
    } catch (e) {
      alert(`Failed to perform action '${actionType}'.`);
    }
  };

  if (loading) {
    return <div className="lead-detail-view">Loading...</div>;
  }

  if (error) {
    return <div className="lead-detail-view error">{error}</div>;
  }

  if (!lead) {
    return <div className="lead-detail-view">No Lead Selected</div>;
  }

  return (
    <div className="lead-detail-view">
      <h2>Lead Detail</h2>
      <section className="lead-info">
        <h3>{lead.name}</h3>
        <p><strong>Email:</strong> {lead.email}</p>
        <p><strong>Phone:</strong> {lead.phone}</p>
        <p><strong>Status:</strong> {lead.status}</p>
        <p><strong>Company:</strong> {lead.company}</p>
      </section>

      <section className="lead-actions">
        <h3>Actions</h3>
        <button onClick={() => handleAction('contact')}>Contact Lead</button>
        <button onClick={() => handleAction('qualify')}>Qualify Lead</button>
        <button onClick={() => handleAction('disqualify')}>Disqualify Lead</button>
      </section>

      <section className="lead-notes">
        <h3>Notes</h3>
        <div className="add-note">
          <textarea
            value={newNote}
            onChange={(e) => setNewNote(e.target.value)}
            placeholder="Add a note..."
          />
          <button onClick={handleAddNote}>Add Note</button>
        </div>
        <ul className="notes-list">
          {notes.length === 0 && <li>No notes available.</li>}
          {notes.map(note => (
            <li key={note.id} className="note-item">
              <div className="note-content">{note.content}</div>
              <div className="note-meta">{new Date(note.created_at).toLocaleString()}</div>
            </li>
          ))}
        </ul>
      </section>

      <section className="lead-history">
        <h3>History</h3>
        <ul className="history-list">
          {history.length === 0 && <li>No history available.</li>}
          {history.map(event => (
            <li key={event.id} className="history-item">
              <div className="history-action">{event.action}</div>
              <div className="history-meta">{new Date(event.timestamp).toLocaleString()}</div>
              {event.details && <div className="history-details">{event.details}</div>}
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
};

export default LeadDetailView;