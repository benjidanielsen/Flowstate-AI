import React, { useEffect, useState } from 'react';
import { AIDecisionLog } from '../types';
import { aiCoordinationApi } from '../services/api';
import { toast } from 'react-toastify';

const AIDecisionLogs: React.FC = () => {
  const [logs, setLogs] = useState<AIDecisionLog[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDecisionLogs();
  }, []);

  const fetchDecisionLogs = async () => {
    try {
      setLoading(true);
      const response = await aiCoordinationApi.getDecisionLogs();
      setLogs(response.data);
    } catch (err: any) {
      setError(err.response?.data?.message || err.message);
      toast.error("Failed to fetch AI decision logs.");
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateStatus = async (logId: number, newStatus: 'approved' | 'rejected' | 'executed') => {
    try {
      await aiCoordinationApi.updateDecisionStatus(logId, newStatus, 'Human Reviewer'); // Placeholder for actual reviewer
      toast.success(`Decision log ${logId} ${newStatus} successfully.`);
      fetchDecisionLogs(); // Refresh logs
    } catch (err: any) {
      toast.error(`Failed to update status for log ${logId}: ${err.response?.data?.message || err.message}`);
    }
  };

  if (loading) return <div className="text-center py-4">Loading AI Decision Logs...</div>;
  if (error) return <div className="text-center py-4 text-red-500">Error: {error}</div>;

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">AI Decision Logs</h1>
      <button
        onClick={fetchDecisionLogs}
        className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded mb-4"
      >
        Refresh Logs
      </button>
      <div className="overflow-x-auto">
        <table className="min-w-full bg-white border border-gray-200">
          <thead>
            <tr>
              <th className="py-2 px-4 border-b">ID</th>
              <th className="py-2 px-4 border-b">Agent</th>
              <th className="py-2 px-4 border-b">Decision</th>
              <th className="py-2 px-4 border-b">Action</th>
              <th className="py-2 px-4 border-b">Status</th>
              <th className="py-2 px-4 border-b">Metadata</th>
              <th className="py-2 px-4 border-b">Created At</th>
              <th className="py-2 px-4 border-b">Actions</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((log) => (
              <tr key={log.id} className="hover:bg-gray-50">
                <td className="py-2 px-4 border-b">{log.id}</td>
                <td className="py-2 px-4 border-b">{log.agent_name} ({log.agent_id})</td>
                <td className="py-2 px-4 border-b">{log.decision_description}</td>
                <td className="py-2 px-4 border-b">{log.action_taken}</td>
                <td className="py-2 px-4 border-b">
                  <span
                    className={`px-2 py-1 rounded-full text-xs font-semibold
                      ${log.status === 'approved' ? 'bg-green-100 text-green-800'
                      : log.status === 'rejected' ? 'bg-red-100 text-red-800'
                      : log.status === 'executed' ? 'bg-blue-100 text-blue-800'
                      : 'bg-yellow-100 text-yellow-800'}`}
                  >
                    {log.status}
                  </span>
                </td>
                <td className="py-2 px-4 border-b text-sm">
                  <pre className="whitespace-pre-wrap text-xs">{JSON.stringify(log.metadata, null, 2)}</pre>
                </td>
                <td className="py-2 px-4 border-b">{new Date(log.created_at).toLocaleString()}</td>
                <td className="py-2 px-4 border-b">
                  {log.status === 'pending' && (
                    <div className="flex space-x-2">
                      <button
                        onClick={() => handleUpdateStatus(log.id, 'approved')}
                        className="bg-green-500 hover:bg-green-700 text-white text-xs py-1 px-2 rounded"
                      >
                        Approve
                      </button>
                      <button
                        onClick={() => handleUpdateStatus(log.id, 'rejected')}
                        className="bg-red-500 hover:bg-red-700 text-white text-xs py-1 px-2 rounded"
                      >
                        Reject
                      </button>
                    </div>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default AIDecisionLogs;

