import { Activity, AlertTriangle, BarChart3, CheckCircle2, Shield } from 'lucide-react';
import ErrorState from '../components/ErrorState';
import Skeleton from '../components/Skeleton';
import { useEvolutionDashboard, useToggleSafeMode } from '../services/api';

const EvolutionDashboard = () => {
  const { data, isLoading, isError, error, refetch, isFetching } = useEvolutionDashboard();
  const toggleSafeMode = useToggleSafeMode();

  const metrics = data?.metrics;
  const anomalies = data?.anomalies ?? [];
  const performance = data?.performance;
  const activity = data?.activity ?? [];

  const safeModeActive = metrics?.safeModeActive ?? false;
  const optimisticSafeMode = toggleSafeMode.isPending ? !safeModeActive : safeModeActive;

  if (isError) {
    return (
      <main className="min-h-screen bg-slate-50 p-6">
        <div className="mx-auto max-w-6xl">
          <ErrorState message={error?.message ?? 'Unable to load evolution data'} onRetry={refetch} />
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-slate-50 p-6">
      <div className="mx-auto max-w-6xl space-y-8">
        <header className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-wide text-slate-500">Evolution</p>
            <h1 className="text-3xl font-bold text-slate-900">Self-evolution dashboard</h1>
            <p className="text-sm text-slate-600">Shared query cache ensures consistent skeletons across KPI + CRM.</p>
          </div>
          <button
            type="button"
            onClick={() => toggleSafeMode.mutate(!safeModeActive)}
            disabled={toggleSafeMode.isPending}
            className={`inline-flex items-center gap-2 rounded-md px-4 py-2 text-sm font-semibold text-white shadow-sm transition ${
              optimisticSafeMode
                ? 'bg-rose-600 hover:bg-rose-700'
                : 'bg-emerald-600 hover:bg-emerald-700'
            }`}
          >
            <Shield className="h-4 w-4" aria-hidden="true" />
            {optimisticSafeMode ? 'Safe mode enabled' : 'Safe mode disabled'}
          </button>
        </header>

        {(isLoading || isFetching) && (
          <div className="grid gap-4 md:grid-cols-2" role="status" aria-live="polite">
            {Array.from({ length: 4 }).map((_, index) => (
              <Skeleton key={index} className="h-32 w-full" />
            ))}
          </div>
        )}

        {!isLoading && metrics && (
          <section className="grid gap-4 md:grid-cols-2 lg:grid-cols-4" aria-live="polite">
            <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
              <p className="text-sm font-medium text-slate-500">Evolution events</p>
              <p className="mt-2 text-3xl font-bold text-slate-900">{metrics.totalEvents}</p>
              <p className="text-xs text-slate-500">Since last deployment</p>
            </div>
            <div className="rounded-xl border border-emerald-200 bg-white p-4 shadow-sm">
              <p className="text-sm font-medium text-slate-500">Success rate</p>
              <p className="mt-2 text-3xl font-bold text-emerald-600">{(metrics.successRate * 100).toFixed(1)}%</p>
              <p className="text-xs text-emerald-600">Validated improvements</p>
            </div>
            <div className="rounded-xl border border-amber-200 bg-white p-4 shadow-sm">
              <p className="text-sm font-medium text-slate-500">Pending improvements</p>
              <p className="mt-2 text-3xl font-bold text-amber-600">{metrics.pendingImprovements}</p>
              <p className="text-xs text-amber-600">Awaiting human review</p>
            </div>
            <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
              <p className="text-sm font-medium text-slate-500">Avg confidence</p>
              <p className="mt-2 text-3xl font-bold text-slate-900">{(metrics.averageConfidence * 100).toFixed(0)}%</p>
              <p className="text-xs text-slate-500">Across suggestions</p>
            </div>
          </section>
        )}

        {!isLoading && (
          <section className="grid gap-6 lg:grid-cols-2">
            <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold text-slate-900">Anomaly detection</h2>
                <AlertTriangle className="h-5 w-5 text-amber-500" aria-hidden="true" />
              </div>
              {anomalies.length === 0 ? (
                <p className="mt-3 text-sm text-emerald-600">No anomalies detected.</p>
              ) : (
                <ul className="mt-4 space-y-3" aria-live="polite">
                  {anomalies.map((anomaly) => (
                    <li
                      key={anomaly.metricName}
                      className="rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900"
                    >
                      <p className="font-semibold">{anomaly.metricName}</p>
                      <p className="text-xs text-amber-700">
                        Latest {anomaly.latestValue.toFixed(2)} • μ {anomaly.mean.toFixed(2)} • z-score{' '}
                        {anomaly.zScore.toFixed(2)}
                      </p>
                      <p className="text-xs text-amber-600">{new Date(anomaly.timestamp).toLocaleString()}</p>
                    </li>
                  ))}
                </ul>
              )}
            </div>

            <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold text-slate-900">System performance</h2>
                <Activity className="h-5 w-5 text-slate-400" aria-hidden="true" />
              </div>
              {performance ? (
                <dl className="mt-4 space-y-4 text-sm text-slate-600">
                  <div>
                    <dt className="flex items-center justify-between">
                      <span>NBA success</span>
                      <span className="font-semibold text-slate-900">
                        {(performance.nbaSuccessRate * 100).toFixed(1)}%
                      </span>
                    </dt>
                    <div className="mt-2 h-2 rounded-full bg-slate-100">
                      <div
                        className="h-full rounded-full bg-emerald-500"
                        style={{ width: `${performance.nbaSuccessRate * 100}%` }}
                      />
                    </div>
                  </div>
                  <div>
                    <dt className="flex items-center justify-between">
                      <span>Reminder success</span>
                      <span className="font-semibold text-slate-900">
                        {(performance.reminderSuccessRate * 100).toFixed(1)}%
                      </span>
                    </dt>
                    <div className="mt-2 h-2 rounded-full bg-slate-100">
                      <div
                        className="h-full rounded-full bg-blue-500"
                        style={{ width: `${performance.reminderSuccessRate * 100}%` }}
                      />
                    </div>
                  </div>
                  <div>
                    <dt className="flex items-center justify-between">
                      <span>Avg response time</span>
                      <span className="font-semibold text-slate-900">{performance.avgResponseTime} ms</span>
                    </dt>
                    <div className="mt-2 h-2 rounded-full bg-slate-100">
                      <div
                        className="h-full rounded-full bg-amber-500"
                        style={{ width: `${Math.min(performance.avgResponseTime / 10, 100)}%` }}
                      />
                    </div>
                  </div>
                </dl>
              ) : (
                <p className="mt-3 text-sm text-slate-500">No performance data.</p>
              )}
            </div>
          </section>
        )}

        {!isLoading && (
          <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-slate-900">Recent evolution activity</h2>
              <BarChart3 className="h-5 w-5 text-slate-400" aria-hidden="true" />
            </div>
            {activity.length === 0 ? (
              <p className="mt-3 text-sm text-slate-500">No logged events.</p>
            ) : (
              <ul className="mt-4 space-y-3" aria-live="polite">
                {activity.map((item) => (
                  <li
                    key={item.id}
                    className="flex items-start justify-between rounded-lg border border-slate-100 p-4 text-sm text-slate-700"
                  >
                    <div>
                      <p className="font-semibold text-slate-900">{item.agentName}</p>
                      <p>{item.action}</p>
                      {item.details && <p className="text-xs text-slate-500">{item.details}</p>}
                    </div>
                    <div className="text-right text-xs text-slate-500">
                      <p>{new Date(item.createdAt).toLocaleTimeString()}</p>
                      <CheckCircle2 className="mt-1 h-4 w-4 text-emerald-500" aria-hidden="true" />
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </section>
        )}
      </div>
    </main>
  );
};

export default EvolutionDashboard;
