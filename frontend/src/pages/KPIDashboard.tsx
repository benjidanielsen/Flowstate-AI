import React, { useState, useEffect } from 'react';
import axiosInstance from '../api/axiosInstance';

interface KPI {
  name: string;
  value: number | string;
  unit?: string;
  change?: number;
  changeType?: 'increase' | 'decrease' | 'neutral';
  description?: string;
  status?: 'success' | 'warning' | 'error' | 'info';
}

const TAB_CONFIG: Array<{ key: string; label: string; description: string }> = [
  { key: 'executive', label: 'Executive Summary', description: 'High-level metrics that describe company performance.' },
  { key: 'operational', label: 'Operational', description: 'System health, responsiveness, and uptime.' },
  { key: 'business', label: 'Business Impact', description: 'Revenue, acquisition, and other commercial metrics.' },
  { key: 'quality', label: 'Quality', description: 'Product quality and delivery metrics.' },
  { key: 'learning', label: 'Learning & Evolution', description: 'Automation learning and continuous improvement signals.' },
];

const KPIDashboard: React.FC = () => {
  const [kpis, setKpis] = useState<KPI[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedTab, setSelectedTab] = useState<string>('executive');

  useEffect(() => {
    fetchKPIs();
  }, [selectedTab]);

  const fetchKPIs = async () => {
    setLoading(true);
    setError(null);
    try {
      // Simulate API call based on selectedTab
      const response = await axiosInstance.get(`/kpis`, { params: { category: selectedTab } });
      setKpis(response.data);
    } catch (err) {
      console.error('Failed to fetch KPIs', err);
      setError('Failed to load KPIs. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  const renderKPIs = () => {
    if (loading) return <p className="text-gray-600">Loading KPIs...</p>;
    if (error) return <p className="text-red-500">Error: {error}</p>;
    if (kpis.length === 0) return <p>No KPIs available for this category.</p>;

    return (
      <ul className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        {kpis.map((kpi, index) => (
          <li key={index} className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">{kpi.name}</p>
                <p className="mt-2 text-2xl font-semibold text-gray-900">
                  {typeof kpi.value === 'number' ? kpi.value.toLocaleString() : kpi.value}
                  {kpi.unit && <span className="ml-1 text-sm text-gray-500">{kpi.unit}</span>}
                </p>
              </div>
              {kpi.status && (
                <span
                  className={`rounded-full px-2 py-1 text-xs font-semibold ${
                    kpi.status === 'success'
                      ? 'bg-emerald-100 text-emerald-700'
                      : kpi.status === 'warning'
                        ? 'bg-amber-100 text-amber-700'
                        : kpi.status === 'error'
                          ? 'bg-rose-100 text-rose-700'
                          : 'bg-blue-100 text-blue-700'
                  }`}
                >
                  {kpi.status.toUpperCase()}
                </span>
              )}
            </div>
            {kpi.change !== undefined && (
              <p className="mt-3 text-sm text-gray-600">
                <span
                  className={
                    kpi.changeType === 'increase'
                      ? 'text-emerald-600'
                      : kpi.changeType === 'decrease'
                        ? 'text-rose-600'
                        : 'text-gray-700'
                  }
                >
                  {kpi.change > 0 ? '+' : ''}{kpi.change.toLocaleString()}
                  {kpi.unit && <span className="ml-1 text-xs text-gray-500">{kpi.unit}</span>}
                </span>
                <span className="ml-2 text-xs text-gray-500">vs. previous period</span>
              </p>
            )}
            {kpi.description && <p className="mt-4 text-sm text-gray-500">{kpi.description}</p>}
          </li>
        ))}
      </ul>
    );
  };

  return (
    <main className="space-y-6 p-6">
      <header className="space-y-2">
        <h1 className="text-3xl font-semibold text-gray-900">Flowstate-AI KPI Dashboard</h1>
        <p className="text-gray-600">Key Performance Indicators for Flowstate-AI operations and business impact.</p>
      </header>

      <nav className="flex flex-wrap gap-2" aria-label="KPI categories">
        {TAB_CONFIG.map(tab => (
          <button
            key={tab.key}
            type="button"
            onClick={() => setSelectedTab(tab.key)}
            className={`rounded-full border px-4 py-2 text-sm font-medium transition ${
              selectedTab === tab.key
                ? 'border-blue-500 bg-blue-50 text-blue-700'
                : 'border-gray-200 bg-white text-gray-600 hover:border-blue-300 hover:text-blue-600'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </nav>

      <section className="space-y-4" aria-live="polite">
        <div>
          <h2 className="text-xl font-semibold text-gray-900">
            {TAB_CONFIG.find(tab => tab.key === selectedTab)?.label ?? 'KPIs'}
          </h2>
          <p className="text-sm text-gray-500">
            {TAB_CONFIG.find(tab => tab.key === selectedTab)?.description ?? ''}
          </p>
        </div>
        {renderKPIs()}
      </section>
    </main>
  );
};

export default KPIDashboard;

