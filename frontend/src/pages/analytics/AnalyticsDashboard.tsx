import React, { useEffect, useMemo, useState } from 'react';
import { analyticsApi, featureFlagApi } from '../../services/api';
import { AnalyticsEventRecord, AnalyticsSummary } from '../../types';

const LoadingState: React.FC = () => (
  <div className="flex items-center justify-center min-h-96">
    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600" />
  </div>
);

const AnalyticsDashboard: React.FC = () => {
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [recentEvents, setRecentEvents] = useState<AnalyticsEventRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [flagEnabled, setFlagEnabled] = useState<boolean>(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const flag = await featureFlagApi.evaluate('analytics_dashboards');
        if (!flag.enabledForContext) {
          setFlagEnabled(false);
          setLoading(false);
          return;
        }
        setFlagEnabled(true);
        const [summaryData, recentEventData] = await Promise.all([
          analyticsApi.getSummary(),
          analyticsApi.getRecentEvents({ limit: 10 }),
        ]);
        setSummary(summaryData);
        setRecentEvents(recentEventData);
      } catch (err) {
        console.error('Failed to load analytics dashboard', err);
        setError('Unable to load analytics insights right now.');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const maxEventCount = useMemo(() => {
    if (!summary) return 1;
    return summary.events.byType.reduce((max, item) => Math.max(max, item.count), 1);
  }, [summary]);

  const maxPipelineCount = useMemo(() => {
    if (!summary) return 1;
    return summary.pipeline.byStatus.reduce((max, item) => Math.max(max, item.count), 1);
  }, [summary]);

  if (loading) {
    return <LoadingState />;
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 p-6 rounded-md">
        <h2 className="text-lg font-semibold mb-2">Analytics temporarily unavailable</h2>
        <p className="text-sm">{error}</p>
      </div>
    );
  }

  if (!flagEnabled) {
    return (
      <div className="bg-white border border-dashed border-gray-300 p-8 rounded-lg text-center">
        <h2 className="text-2xl font-semibold text-gray-800 mb-2">Analytics dashboards in phased rollout</h2>
        <p className="text-gray-600">
          This workspace is not yet enrolled in the analytics dashboard preview. Enable the
          <span className="font-medium"> analytics_dashboards</span> feature flag to explore pipeline metrics
          and agent insights before general availability.
        </p>
      </div>
    );
  }

  if (!summary) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 text-yellow-800 p-6 rounded-md">
        <h2 className="text-lg font-semibold mb-2">No analytics data yet</h2>
        <p className="text-sm">Start logging customer events and agent recommendations to populate this view.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Analytics Overview</h1>
          <p className="text-gray-600">Tracking event ingestion, agent output, and pipeline health.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <SummaryCard title="Events captured" value={summary.events.total} description="30-day window" />
        <SummaryCard title="Recommendations logged" value={summary.recommendations.total} description="Vector + heuristic" />
        <SummaryCard
          title="Active pipeline stages"
          value={summary.pipeline.byStatus.length}
          description="Across all customers"
        />
      </div>

      <section className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Event volume by type</h2>
          <div className="space-y-3">
            {summary.events.byType.map((eventType) => (
              <div key={eventType.eventType}>
                <div className="flex justify-between text-sm text-gray-700 mb-1">
                  <span>{eventType.eventType}</span>
                  <span>{eventType.count}</span>
                </div>
                <div className="h-2 bg-gray-100 rounded">
                  <div
                    className="h-2 rounded bg-primary-500"
                    style={{ width: `${(eventType.count / maxEventCount) * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Pipeline distribution</h2>
          <div className="space-y-3">
            {summary.pipeline.byStatus.map((status) => (
              <div key={status.status}>
                <div className="flex justify-between text-sm text-gray-700 mb-1">
                  <span>{status.status}</span>
                  <span>{status.count}</span>
                </div>
                <div className="h-2 bg-gray-100 rounded">
                  <div
                    className="h-2 rounded bg-indigo-500"
                    style={{ width: `${(status.count / maxPipelineCount) * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow col-span-1 lg:col-span-2">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Event trend (14 days)</h2>
          <TrendChart points={summary.events.trend} />
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Top recommendation types</h2>
          <ul className="space-y-3">
            {summary.recommendations.topTypes.map((item) => (
              <li key={item.recommendationType} className="border-b border-gray-100 pb-2">
                <div className="flex justify-between text-sm text-gray-800">
                  <span>{item.recommendationType}</span>
                  <span className="font-medium">{item.count}</span>
                </div>
                <p className="text-xs text-gray-500">
                  Avg. priority: {item.averagePriority !== null ? item.averagePriority.toFixed(1) : '—'}
                </p>
              </li>
            ))}
          </ul>
        </div>
      </section>

      <section className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Agent contribution</h2>
          <ul className="space-y-3">
            {summary.recommendations.byAgent.map((agent) => {
              const avgScore = summary.recommendations.averageScoreByAgent.find(
                (score) => score.agentName === agent.agentName
              );
              return (
                <li key={agent.agentName} className="flex justify-between text-sm text-gray-700">
                  <span className="font-medium">{agent.agentName || 'unknown agent'}</span>
                  <span>
                    {agent.count} recs
                    {avgScore && avgScore.averageScore !== null
                      ? ` • avg score ${(avgScore.averageScore * 100).toFixed(0)}%`
                      : ''}
                  </span>
                </li>
              );
            })}
          </ul>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Latest analytics events</h2>
          <ul className="space-y-3">
            {recentEvents.map((event) => (
              <li key={event.id} className="border-b border-gray-100 pb-2">
                <div className="flex justify-between text-sm text-gray-800">
                  <span>{event.event_type}</span>
                  <span className="text-gray-500">
                    {new Date(event.occurred_at || event.ingested_at).toLocaleString()}
                  </span>
                </div>
                {event.customer_id && (
                  <p className="text-xs text-gray-500">Customer: {event.customer_id}</p>
                )}
                {event.source && <p className="text-xs text-gray-500">Source: {event.source}</p>}
              </li>
            ))}
            {recentEvents.length === 0 && (
              <li className="text-sm text-gray-500">No analytics events ingested yet.</li>
            )}
          </ul>
        </div>
      </section>
    </div>
  );
};

interface SummaryCardProps {
  title: string;
  value: number;
  description: string;
}

const SummaryCard: React.FC<SummaryCardProps> = ({ title, value, description }) => (
  <div className="bg-white p-6 rounded-lg shadow">
    <p className="text-sm text-gray-500">{description}</p>
    <p className="text-3xl font-bold text-gray-900">{value}</p>
    <p className="text-sm font-medium text-gray-700 mt-2">{title}</p>
  </div>
);

interface TrendChartProps {
  points: { date: string; count: number }[];
}

const TrendChart: React.FC<TrendChartProps> = ({ points }) => {
  if (!points.length) {
    return <p className="text-sm text-gray-500">No trend data available.</p>;
  }

  const max = points.reduce((acc, point) => Math.max(acc, point.count), 0) || 1;
  const width = 400;
  const height = 160;
  const step = width / Math.max(points.length - 1, 1);

  const coordinates = points
    .map((point, index) => {
      const x = index * step;
      const y = height - (point.count / max) * (height - 20);
      return `${x},${y}`;
    })
    .join(' ');

  return (
    <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-40">
      <polyline
        fill="none"
        stroke="#6366F1"
        strokeWidth="3"
        strokeLinejoin="round"
        points={coordinates}
      />
      {points.map((point, index) => {
        const x = index * step;
        const y = height - (point.count / max) * (height - 20);
        return <circle key={point.date} cx={x} cy={y} r={3} fill="#4F46E5" />;
      })}
    </svg>
  );
};

export default AnalyticsDashboard;
