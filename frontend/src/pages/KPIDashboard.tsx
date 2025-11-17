import { useMemo, useState } from 'react';
import { ArrowDownRight, ArrowUpRight, BarChart3, RefreshCw, Shield, TrendingUp } from 'lucide-react';
import ErrorState from '../components/ErrorState';
import Skeleton from '../components/Skeleton';
import { useKpiDashboard } from '../services/api';
import { KPIMetric, TrendPoint } from '../types';

const tabs = [
  { id: 'executive', label: 'Executive', description: 'Top-line performance' },
  { id: 'operational', label: 'Operational', description: 'Agent & infra health' },
  { id: 'crm', label: 'CRM', description: 'Pipeline and customers' },
  { id: 'quality', label: 'Quality', description: 'AI + human QA' },
  { id: 'learning', label: 'Evolution', description: 'Self-improving signals' },
];

const TrendSparkline = ({ data }: { data: TrendPoint[] }) => {
  if (!data.length) {
    return <p className="text-xs text-slate-500">No trend data yet.</p>;
  }

  const values = data.map((point) => point.value);
  const max = Math.max(...values);
  const min = Math.min(...values);

  const points = data
    .map((point, index) => {
      const x = (index / Math.max(data.length - 1, 1)) * 100;
      const y = max === min ? 50 : 100 - ((point.value - min) / (max - min)) * 100;
      return `${x},${y}`;
    })
    .join(' ');

  return (
    <svg viewBox="0 0 100 100" className="h-20 w-full text-slate-500" role="img" aria-label="Trend sparkline">
      <polyline
        points={points}
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
};

const MetricCard = ({ metric }: { metric: KPIMetric }) => {
  const DirectionIcon = metric.direction === 'down' ? ArrowDownRight : ArrowUpRight;
  const isPositive = metric.direction !== 'down';

  return (
    <article className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm" aria-label={`${metric.name} metric`}>
      <p className="text-sm font-medium text-slate-500">{metric.name}</p>
      <p className="mt-2 text-3xl font-bold text-slate-900">
        {metric.value.toLocaleString()} {metric.unit && <span className="text-base text-slate-500">{metric.unit}</span>}
      </p>
      {typeof metric.change === 'number' && (
        <div className="mt-3 inline-flex items-center rounded-full bg-slate-100 px-2 py-1 text-xs font-semibold">
          <DirectionIcon className={`mr-1 h-3 w-3 ${isPositive ? 'text-emerald-600' : 'text-rose-600'}`} aria-hidden="true" />
          <span className={isPositive ? 'text-emerald-700' : 'text-rose-600'}>
            {metric.change.toFixed(1)}%
          </span>
          <span className="ml-1 text-slate-500">vs last period</span>
        </div>
      )}
      {metric.description && <p className="mt-3 text-sm text-slate-600">{metric.description}</p>}
    </article>
  );
};

const KPIDashboard = () => {
  const [activeTab, setActiveTab] = useState<string>('executive');
  const { data, isLoading, isError, isFetching, error, refetch } = useKpiDashboard(activeTab);

  const metrics = data?.metrics ?? [];
  const trend = data?.trend ?? [];
  const summary = data?.summary;

  const focusTotal = summary?.total ?? null;
  const totalDelta = useMemo(() => summary?.delta ?? 0, [summary]);

  return (
    <main className="min-h-screen bg-slate-50 p-6">
      <div className="mx-auto max-w-6xl space-y-8">
        <header className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-wide text-slate-500">Performance</p>
            <h1 className="text-3xl font-bold text-slate-900">KPI overview</h1>
            <p className="text-sm text-slate-600">
              Cached via React Query with shared skeleton and error handling.
            </p>
          </div>
          <button
            type="button"
            onClick={() => refetch()}
            className="inline-flex items-center justify-center rounded-md border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700 shadow-sm transition hover:bg-slate-100"
            disabled={isFetching}
          >
            <RefreshCw className={`mr-2 h-4 w-4 ${isFetching ? 'animate-spin' : ''}`} aria-hidden="true" />
            {isFetching ? 'Refreshing…' : 'Refresh data'}
          </button>
        </header>

        <div className="flex flex-wrap gap-2" role="tablist" aria-label="KPI categories">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              role="tab"
              aria-selected={activeTab === tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`rounded-full px-4 py-2 text-sm font-semibold transition ${
                activeTab === tab.id
                  ? 'bg-slate-900 text-white shadow'
                  : 'bg-white text-slate-600 shadow-sm hover:text-slate-900'
              }`}
            >
              <span className="block text-left">
                {tab.label}
                <span className="block text-xs font-normal text-slate-400">{tab.description}</span>
              </span>
            </button>
          ))}
        </div>

        <section className="grid gap-4 md:grid-cols-3" aria-live="polite">
          <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
            <p className="text-sm font-medium text-slate-500">Focus metric</p>
            <p className="mt-2 text-3xl font-bold text-slate-900">
              {focusTotal !== null ? focusTotal.toLocaleString() : '—'}
            </p>
            <p className="text-xs text-slate-500">{tabs.find((tab) => tab.id === activeTab)?.label}</p>
          </div>
          <div className="rounded-xl border border-emerald-200 bg-white p-4 shadow-sm">
            <p className="text-sm font-medium text-slate-500">Delta</p>
            <div className="mt-2 flex items-baseline gap-2">
              <TrendingUp className="h-5 w-5 text-emerald-600" aria-hidden="true" />
              <p className="text-3xl font-bold text-emerald-600">{totalDelta.toFixed(1)}%</p>
            </div>
            <p className="text-xs text-emerald-600">vs previous period</p>
          </div>
          <div className="rounded-xl border border-amber-200 bg-white p-4 shadow-sm">
            <p className="text-sm font-medium text-slate-500">Cache status</p>
            <div className="mt-2 flex items-center gap-2">
              <Shield className="h-5 w-5 text-amber-500" aria-hidden="true" />
              <span className="text-3xl font-bold text-amber-600">{isFetching ? 'Warm' : 'Fresh'}</span>
            </div>
            <p className="text-xs text-amber-600">Shared query cache</p>
          </div>
        </section>

        {isError && (
          <ErrorState
            message={error?.message ?? 'Unable to load KPI data'}
            onRetry={refetch}
          />
        )}

        {(isLoading || (isFetching && !metrics.length)) && (
          <div className="grid gap-4 md:grid-cols-2" role="status" aria-live="polite">
            {Array.from({ length: 4 }).map((_, index) => (
              <Skeleton key={index} className="h-44 w-full" />
            ))}
          </div>
        )}

        {!isLoading && !isError && (
          <>
            <section className="grid gap-4 md:grid-cols-2">
              {metrics.map((metric) => (
                <MetricCard key={metric.id} metric={metric} />
              ))}
              {!metrics.length && (
                <p className="text-sm text-slate-500">No KPI metrics available for this category.</p>
              )}
            </section>

            <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold text-slate-900">Trend insight</h2>
                <BarChart3 className="h-5 w-5 text-slate-400" aria-hidden="true" />
              </div>
              <TrendSparkline data={trend} />
            </section>
          </>
        )}
      </div>
    </main>
  );
};

export default KPIDashboard;
