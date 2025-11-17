import { useMemo } from 'react';
import { ArrowRightCircle, CheckCircle2, Clock4, RefreshCw, ShieldCheck, Users } from 'lucide-react';
import ErrorState from '../components/ErrorState';
import Skeleton from '../components/Skeleton';
import { useAdminActivity, useAdminRoster, useAdminTasks } from '../services/api';
import { ActivityLog, AdminTask, AgentProfile } from '../types';

const statusStyles: Record<AgentProfile['status'], string> = {
  online: 'bg-emerald-100 text-emerald-700',
  busy: 'bg-amber-100 text-amber-700',
  offline: 'bg-slate-100 text-slate-600',
};

const taskColumns: { id: AdminTask['status']; title: string; accent: string }[] = [
  { id: 'todo', title: 'Backlog', accent: 'border-slate-200' },
  { id: 'in_progress', title: 'In Progress', accent: 'border-amber-200' },
  { id: 'blocked', title: 'Blocked', accent: 'border-rose-200' },
  { id: 'done', title: 'Completed', accent: 'border-emerald-200' },
];

const AdminDashboard = () => {
  const rosterQuery = useAdminRoster();
  const activityQuery = useAdminActivity();
  const tasksQuery = useAdminTasks();

  const roster = rosterQuery.data ?? [];
  const activity = activityQuery.data ?? [];
  const tasks = tasksQuery.data ?? [];

  const groupedTasks = useMemo(() => {
    return taskColumns.reduce<Record<string, AdminTask[]>>((acc, column) => {
      acc[column.id] = tasks.filter((task) => task.status === column.id);
      return acc;
    }, {});
  }, [tasks]);

  const onlineCount = roster.filter((agent) => agent.status === 'online').length;
  const busyCount = roster.filter((agent) => agent.status === 'busy').length;
  const activeTasks = tasks.filter((task) => task.status !== 'done').length;

  const isRefreshing =
    rosterQuery.isRefetching || activityQuery.isRefetching || tasksQuery.isRefetching;

  const renderRosterContent = () => {
    if (rosterQuery.isError) {
      return (
        <ErrorState
          message={rosterQuery.error?.message ?? 'Unable to load agent roster'}
          onRetry={rosterQuery.refetch}
        />
      );
    }

    if (rosterQuery.isLoading) {
      return (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {Array.from({ length: 6 }).map((_, index) => (
            <Skeleton key={index} className="h-40 w-full" />
          ))}
        </div>
      );
    }

    return (
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3" aria-live="polite">
        {roster.map((agent) => (
          <article
            key={agent.id}
            className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm"
          >
            <div className="flex items-start justify-between">
              <div>
                <p className="text-base font-semibold text-slate-900">{agent.name}</p>
                <p className="text-sm text-slate-500">{agent.role}</p>
              </div>
              <span
                className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold ${statusStyles[agent.status]}`}
              >
                {agent.status.replace('_', ' ')}
              </span>
            </div>
            <dl className="mt-4 space-y-1 text-sm text-slate-600">
              <div className="flex items-center justify-between">
                <dt>Specialty</dt>
                <dd className="font-medium text-slate-900">{agent.specialty ?? '—'}</dd>
              </div>
              <div className="flex items-center justify-between">
                <dt>Tasks in flight</dt>
                <dd className="font-semibold text-slate-900">{agent.tasksInFlight}</dd>
              </div>
              <div className="flex items-center justify-between">
                <dt>Last active</dt>
                <dd>{new Date(agent.lastActive).toLocaleTimeString()}</dd>
              </div>
            </dl>
          </article>
        ))}
      </div>
    );
  };

  const renderActivity = () => {
    if (activityQuery.isError) {
      return (
        <ErrorState
          message={activityQuery.error?.message ?? 'Unable to load activity feed'}
          onRetry={activityQuery.refetch}
        />
      );
    }

    if (activityQuery.isLoading) {
      return (
        <div className="space-y-3">
          {Array.from({ length: 4 }).map((_, index) => (
            <Skeleton key={index} className="h-16 w-full" />
          ))}
        </div>
      );
    }

    if (!activity.length) {
      return <p className="text-sm text-slate-500">No recent events.</p>;
    }

    return (
      <ul className="space-y-3" aria-live="polite">
        {activity.map((entry: ActivityLog) => (
          <li
            key={entry.id}
            className="rounded-lg border border-slate-200 bg-white p-4 text-sm text-slate-700 shadow-sm"
          >
            <p className="font-medium text-slate-900">{entry.agentName}</p>
            <p className="mt-1">{entry.action}</p>
            {entry.details && <p className="mt-1 text-slate-500">{entry.details}</p>}
            <p className="mt-2 text-xs text-slate-400">
              {new Date(entry.createdAt).toLocaleString()}
            </p>
          </li>
        ))}
      </ul>
    );
  };

  const renderTasks = () => {
    if (tasksQuery.isError) {
      return (
        <ErrorState
          message={tasksQuery.error?.message ?? 'Unable to load tasks'}
          onRetry={tasksQuery.refetch}
        />
      );
    }

    if (tasksQuery.isLoading) {
      return (
        <div className="grid gap-4 md:grid-cols-2">
          {Array.from({ length: 4 }).map((_, index) => (
            <Skeleton key={index} className="h-48 w-full" />
          ))}
        </div>
      );
    }

    return (
      <div className="grid gap-4 md:grid-cols-2" aria-live="polite">
        {taskColumns.map((column) => (
          <section key={column.id} className={`rounded-xl border ${column.accent} bg-white p-4 shadow-sm`}>
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold text-slate-900">{column.title}</h3>
              <span className="text-xs text-slate-500">{groupedTasks[column.id]?.length ?? 0} tasks</span>
            </div>
            <ul className="mt-4 space-y-3">
              {(groupedTasks[column.id] ?? []).map((task) => (
                <li key={task.id} className="rounded-lg border border-slate-100 p-3 text-sm">
                  <p className="font-medium text-slate-900">{task.title}</p>
                  <p className="text-xs text-slate-500">Owner: {task.owner}</p>
                  {task.relatedCustomer && (
                    <p className="text-xs text-slate-500">Customer: {task.relatedCustomer}</p>
                  )}
                  <div className="mt-2 flex items-center justify-between text-xs">
                    <span className="flex items-center gap-1 text-slate-500">
                      <Clock4 className="h-3.5 w-3.5" />
                      Due {new Date(task.dueDate).toLocaleDateString()}
                    </span>
                    <span className="font-semibold text-slate-700">{task.priority.toUpperCase()}</span>
                  </div>
                </li>
              ))}
              {(!groupedTasks[column.id] || groupedTasks[column.id].length === 0) && (
                <li className="text-xs text-slate-400">No tasks in this column.</li>
              )}
            </ul>
          </section>
        ))}
      </div>
    );
  };

  return (
    <main className="min-h-screen bg-slate-50 p-6">
      <div className="mx-auto max-w-6xl space-y-8">
        <header className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-wide text-slate-500">
              Control tower
            </p>
            <h1 className="text-3xl font-bold text-slate-900">Admin dashboard</h1>
            <p className="text-sm text-slate-600">
              Oversee agent orchestration, live activity, and operational tasks in one view.
            </p>
          </div>
          <button
            type="button"
            onClick={() => {
              rosterQuery.refetch();
              activityQuery.refetch();
              tasksQuery.refetch();
            }}
            className="inline-flex items-center justify-center rounded-md border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700 shadow-sm transition hover:bg-slate-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-700"
            disabled={isRefreshing}
          >
            <RefreshCw className={`mr-2 h-4 w-4 ${isRefreshing ? 'animate-spin' : ''}`} aria-hidden="true" />
            {isRefreshing ? 'Refreshing…' : 'Refresh data'}
          </button>
        </header>

        <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4" aria-live="polite">
          <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
            <div className="flex items-center justify-between">
              <p className="text-sm font-medium text-slate-500">Total agents</p>
              <Users className="h-4 w-4 text-slate-400" aria-hidden="true" />
            </div>
            <p className="mt-2 text-3xl font-bold text-slate-900">{roster.length}</p>
            <p className="text-xs text-slate-500">Across all pods</p>
          </div>
          <div className="rounded-xl border border-emerald-200 bg-white p-4 shadow-sm">
            <div className="flex items-center justify-between">
              <p className="text-sm font-medium text-slate-500">Online now</p>
              <ShieldCheck className="h-4 w-4 text-emerald-500" aria-hidden="true" />
            </div>
            <p className="mt-2 text-3xl font-bold text-emerald-700">{onlineCount}</p>
            <p className="text-xs text-emerald-600">{busyCount} assisting or pairing</p>
          </div>
          <div className="rounded-xl border border-amber-200 bg-white p-4 shadow-sm">
            <div className="flex items-center justify-between">
              <p className="text-sm font-medium text-slate-500">Work in flight</p>
              <ArrowRightCircle className="h-4 w-4 text-amber-500" aria-hidden="true" />
            </div>
            <p className="mt-2 text-3xl font-bold text-amber-600">{activeTasks}</p>
            <p className="text-xs text-amber-600">Open tasks across pods</p>
          </div>
          <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
            <div className="flex items-center justify-between">
              <p className="text-sm font-medium text-slate-500">Escalations</p>
              <CheckCircle2 className="h-4 w-4 text-slate-400" aria-hidden="true" />
            </div>
            <p className="mt-2 text-3xl font-bold text-slate-900">{activity.length}</p>
            <p className="text-xs text-slate-500">Events logged today</p>
          </div>
        </section>

        <section className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-slate-900">Agent roster</h2>
            <p className="text-sm text-slate-500">Live presence from the Flowstate AI mesh.</p>
          </div>
          {renderRosterContent()}
        </section>

        <section className="grid gap-6 lg:grid-cols-2">
          <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-slate-900">Activity feed</h2>
              <Clock4 className="h-4 w-4 text-slate-400" aria-hidden="true" />
            </div>
            <div className="mt-4 max-h-[28rem] overflow-y-auto pr-1">
              {renderActivity()}
            </div>
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-slate-900">Task management</h2>
              <ShieldCheck className="h-4 w-4 text-slate-400" aria-hidden="true" />
            </div>
            <div className="mt-4 max-h-[28rem] overflow-y-auto pr-1">
              {renderTasks()}
            </div>
          </div>
        </section>
      </div>
    </main>
  );
};

export default AdminDashboard;
