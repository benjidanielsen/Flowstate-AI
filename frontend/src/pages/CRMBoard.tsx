import { useMemo, useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { FixedSizeList, ListChildComponentProps } from 'react-window';
import {
  ArrowRight,
  Loader2,
  Mail,
  MapPin,
  Phone,
  RefreshCw,
  Users,
} from 'lucide-react';
import ErrorState from '../components/ErrorState';
import Skeleton from '../components/Skeleton';
import { customerApi, useCustomerPipeline } from '../services/api';
import { Customer, PipelineStatus } from '../types';

const pipelineStages = [
  { id: PipelineStatus.LEAD, label: 'Frazer leads', hint: 'Inbound records synced nightly' },
  { id: PipelineStatus.RELATIONSHIP, label: 'Relationship', hint: 'Actively nurtured prospects' },
  { id: PipelineStatus.INVITED, label: 'Invited', hint: 'Booked for a Frazer call' },
  { id: PipelineStatus.QUALIFIED, label: 'Qualified', hint: 'Validated needs and fit' },
  { id: PipelineStatus.PRESENTATION_SENT, label: 'Deck sent', hint: 'Waiting on signal' },
  { id: PipelineStatus.FOLLOW_UP, label: 'Follow-up', hint: 'Scheduled reminders and nudges' },
  { id: PipelineStatus.SIGNED_UP, label: 'Won', hint: 'Closed via Frazer automation' },
];

const CARD_HEIGHT = 180;

type PipelineListData = {
  items: Customer[];
  pendingId: string | null;
  onAdvance: (id: string) => void;
};

const PipelineRow = ({ index, style, data }: ListChildComponentProps<PipelineListData>) => {
  const lead = data.items[index];
  const isPending = data.pendingId === lead.id;

  return (
    <div style={style} className="px-1 pb-3">
      <article className="flex h-full flex-col justify-between rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <div>
          <p className="text-base font-semibold text-slate-900">{lead.name}</p>
          <p className="text-xs uppercase tracking-wide text-slate-500">
            {lead.source ?? 'Unknown source'}
          </p>
          {lead.notes && <p className="mt-2 text-sm text-slate-600">{lead.notes}</p>}
        </div>
        <dl className="mt-3 space-y-1 text-xs text-slate-500">
          {lead.email && (
            <div className="flex items-center gap-2">
              <Mail className="h-3.5 w-3.5" aria-hidden="true" />
              <span>{lead.email}</span>
            </div>
          )}
          {lead.phone && (
            <div className="flex items-center gap-2">
              <Phone className="h-3.5 w-3.5" aria-hidden="true" />
              <span>{lead.phone}</span>
            </div>
          )}
          {lead.country && (
            <div className="flex items-center gap-2">
              <MapPin className="h-3.5 w-3.5" aria-hidden="true" />
              <span>{lead.country}</span>
            </div>
          )}
        </dl>
        <div className="mt-4 flex items-center justify-between">
          <div>
            <p className="text-xs text-slate-500">Next action</p>
            <p className="text-sm font-medium text-slate-900">
              {lead.next_action ?? 'Align talking points'}
            </p>
          </div>
          <button
            type="button"
            onClick={() => data.onAdvance(lead.id)}
            disabled={isPending}
            className="inline-flex items-center gap-1 rounded-full border border-slate-200 px-3 py-1 text-xs font-semibold text-slate-700 transition hover:bg-slate-100 disabled:opacity-60"
          >
            {isPending ? (
              <Loader2 className="h-3.5 w-3.5 animate-spin" aria-hidden="true" />
            ) : (
              <ArrowRight className="h-3.5 w-3.5" aria-hidden="true" />
            )}
            Advance
          </button>
        </div>
      </article>
    </div>
  );
};

const CRMBoard = () => {
  const queryClient = useQueryClient();
  const [sourceView, setSourceView] = useState<'frazer' | 'all'>('frazer');
  const [pendingCustomer, setPendingCustomer] = useState<string | null>(null);

  const { data: customers = [], isLoading, isFetching, isError, error, refetch } = useCustomerPipeline();

  const filteredCustomers = useMemo(() => {
    if (sourceView === 'frazer') {
      return customers.filter((customer) => (customer.source ?? '').toLowerCase().includes('frazer'));
    }
    return customers;
  }, [customers, sourceView]);

  const pipeline = useMemo(() => {
    return pipelineStages.map((stage) => ({
      ...stage,
      customers: filteredCustomers.filter((customer) => customer.status === stage.id),
    }));
  }, [filteredCustomers]);

  const conversionRate = useMemo(() => {
    if (!filteredCustomers.length) return 0;
    const won = filteredCustomers.filter((customer) => customer.status === PipelineStatus.SIGNED_UP).length;
    return Math.round((won / filteredCustomers.length) * 100);
  }, [filteredCustomers]);

  const moveMutation = useMutation({
    mutationFn: (id: string) => customerApi.moveToNextStage(id),
    onMutate: (id) => {
      setPendingCustomer(id);
    },
    onSettled: () => {
      setPendingCustomer(null);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['customers'] });
    },
  });

  const renderSkeleton = () => (
    <div className="grid gap-4 lg:grid-cols-2 xl:grid-cols-3">
      {pipelineStages.slice(0, 3).map((stage) => (
        <div key={stage.id} className="rounded-2xl border border-slate-100 bg-white p-4 shadow-sm">
          <div className="flex items-center justify-between">
            <p className="text-sm font-semibold text-slate-500">{stage.label}</p>
            <Skeleton className="h-4 w-10" />
          </div>
          <div className="mt-4 space-y-3">
            {Array.from({ length: 3 }).map((_, index) => (
              <Skeleton key={index} className="h-32 w-full" />
            ))}
          </div>
        </div>
      ))}
    </div>
  );

  return (
    <main className="min-h-screen bg-slate-50 p-6">
      <div className="mx-auto max-w-7xl space-y-8">
        <header className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-wide text-slate-500">
              CRM operations
            </p>
            <h1 className="text-3xl font-bold text-slate-900">Frazer pipeline</h1>
            <p className="text-sm text-slate-600">
              Real-time pipeline health with virtualization for high-volume lead queues.
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <div className="inline-flex rounded-full bg-white p-1 shadow-sm" role="tablist" aria-label="Source filter">
              {['frazer', 'all'].map((option) => (
                <button
                  key={option}
                  type="button"
                  role="tab"
                  aria-selected={sourceView === option}
                  onClick={() => setSourceView(option as 'frazer' | 'all')}
                  className={`rounded-full px-4 py-1.5 text-sm font-semibold transition ${
                    sourceView === option
                      ? 'bg-slate-900 text-white shadow'
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  {option === 'frazer' ? 'Frazer only' : 'All customers'}
                </button>
              ))}
            </div>
            <button
              type="button"
              onClick={() => refetch()}
              className="inline-flex items-center justify-center rounded-md border border-slate-200 bg-white px-3 py-2 text-sm font-semibold text-slate-700 shadow-sm transition hover:bg-slate-100"
              disabled={isFetching}
            >
              <RefreshCw className={`mr-2 h-4 w-4 ${isFetching ? 'animate-spin' : ''}`} aria-hidden="true" />
              {isFetching ? 'Refreshing…' : 'Refresh'}
            </button>
          </div>
        </header>

        <section className="grid gap-4 md:grid-cols-3" aria-live="polite">
          <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
            <div className="flex items-center justify-between">
              <p className="text-sm font-medium text-slate-500">Active leads</p>
              <Users className="h-4 w-4 text-slate-400" aria-hidden="true" />
            </div>
            <p className="mt-2 text-3xl font-bold text-slate-900">{filteredCustomers.length}</p>
            <p className="text-xs text-slate-500">{sourceView === 'frazer' ? 'Synced from Frazer CRM' : 'All CRM contacts'}</p>
          </div>
          <div className="rounded-xl border border-emerald-200 bg-white p-4 shadow-sm">
            <p className="text-sm font-medium text-slate-500">Conversion rate</p>
            <p className="mt-2 text-3xl font-bold text-emerald-600">{conversionRate}%</p>
            <p className="text-xs text-emerald-600">Won vs. total visible leads</p>
          </div>
          <div className="rounded-xl border border-amber-200 bg-white p-4 shadow-sm">
            <p className="text-sm font-medium text-slate-500">Virtualized rows</p>
            <p className="mt-2 text-3xl font-bold text-amber-600">{filteredCustomers.length || 0}</p>
            <p className="text-xs text-amber-600">Rendering capped via react-window</p>
          </div>
        </section>

        {isError && (
          <ErrorState message={error?.message ?? 'Unable to load CRM board'} onRetry={refetch} />
        )}

        {(isLoading || isFetching) && !filteredCustomers.length ? renderSkeleton() : null}

        {!isLoading && !isError && (
          <div className="grid gap-4 lg:grid-cols-2 xl:grid-cols-3" aria-live="polite">
            {pipeline.map((stage) => (
              <section
                key={stage.id}
                className="rounded-2xl border border-slate-100 bg-white p-4 shadow-sm"
                aria-label={`${stage.label} column`}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-sm font-semibold text-slate-900">{stage.label}</h2>
                    <p className="text-xs text-slate-500">{stage.hint}</p>
                  </div>
                  <span className="text-xs font-semibold text-slate-500">
                    {stage.customers.length} leads
                  </span>
                </div>
                <div className="mt-4">
                  {stage.customers.length === 0 ? (
                    <p className="text-sm text-slate-500">No leads in this stage.</p>
                  ) : (
                    <FixedSizeList
                      height={Math.max(Math.min(stage.customers.length, 4), 1) * CARD_HEIGHT}
                      itemCount={stage.customers.length}
                      itemSize={CARD_HEIGHT}
                      width="100%"
                      itemData={{
                        items: stage.customers,
                        pendingId: pendingCustomer,
                        onAdvance: (id: string) => moveMutation.mutate(id),
                      }}
                    >
                      {PipelineRow}
                    </FixedSizeList>
                  )}
                </div>
              </section>
            ))}
          </div>
        )}
      </div>
    </main>
  );
};

export default CRMBoard;
