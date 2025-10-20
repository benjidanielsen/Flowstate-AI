import { useEffect, useMemo, useState } from 'react';
import { pipelineApi } from '../../services/api';
import type { Pipeline, PipelineStage } from '../../types';

interface StageGroupProps {
  stage: PipelineStage;
  onSelectStage(stage: PipelineStage): void;
  isSelected: boolean;
}

const StageGroup = ({ stage, onSelectStage, isSelected }: StageGroupProps) => (
  <button
    className={`rounded-md border px-4 py-2 text-left transition hover:border-blue-400 ${
      isSelected ? 'border-blue-500 bg-blue-50 text-blue-900' : 'border-slate-200 bg-white'
    }`}
    onClick={() => onSelectStage(stage)}
  >
    <div className="flex items-center justify-between">
      <h3 className="text-sm font-semibold">{stage.name}</h3>
      <span className="text-xs text-slate-500">#{stage.position + 1}</span>
    </div>
    {stage.description && (
      <p className="mt-1 text-xs text-slate-600">{stage.description}</p>
    )}
  </button>
);

export default function PipelineDashboard() {
  const [pipelines, setPipelines] = useState<Pipeline[]>([]);
  const [selectedPipelineId, setSelectedPipelineId] = useState<string | null>(null);
  const [selectedStage, setSelectedStage] = useState<PipelineStage | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const response = await pipelineApi.list();
        setPipelines(response);
        if (!selectedPipelineId && response.length) {
          setSelectedPipelineId(response[0].id);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load pipelines');
      } finally {
        setIsLoading(false);
      }
    };

    load();
  }, [selectedPipelineId]);

  const selectedPipeline = useMemo(
    () => pipelines.find((pipeline) => pipeline.id === selectedPipelineId) ?? null,
    [pipelines, selectedPipelineId]
  );

  const onSelectStage = (stage: PipelineStage) => setSelectedStage(stage);

  return (
    <section className="space-y-4 rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
      <header className="flex flex-wrap items-center justify-between gap-2">
        <div>
          <h2 className="text-lg font-semibold text-slate-900">Pipeline Dashboard</h2>
          <p className="text-sm text-slate-500">Monitor pipeline structure and stage readiness.</p>
        </div>
        <select
          className="rounded-md border border-slate-200 px-3 py-2 text-sm"
          value={selectedPipelineId ?? ''}
          onChange={(event) => setSelectedPipelineId(event.target.value || null)}
        >
          <option value="">Select pipeline…</option>
          {pipelines.map((pipeline) => (
            <option key={pipeline.id} value={pipeline.id}>
              {pipeline.name}
            </option>
          ))}
        </select>
      </header>

      {isLoading && <p className="text-sm text-slate-500">Loading pipelines…</p>}
      {error && <p className="text-sm text-red-500">{error}</p>}

      {selectedPipeline && (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {selectedPipeline.stages.map((stage) => (
            <StageGroup
              key={stage.id}
              stage={stage}
              onSelectStage={onSelectStage}
              isSelected={selectedStage?.id === stage.id}
            />
          ))}
        </div>
      )}

      {selectedStage && (
        <aside className="rounded-md border border-blue-200 bg-blue-50 p-3 text-sm text-blue-900">
          <h3 className="font-semibold">{selectedStage.name}</h3>
          {selectedStage.description && <p className="mt-1 text-blue-800">{selectedStage.description}</p>}
          {selectedStage.metadata && Object.keys(selectedStage.metadata).length > 0 && (
            <pre className="mt-2 whitespace-pre-wrap text-xs text-blue-700">
              {JSON.stringify(selectedStage.metadata, null, 2)}
            </pre>
          )}
        </aside>
      )}
    </section>
  );
}
