-- Migration: create pipeline-related tables and extend CRM entities

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS public.pipelines (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.pipeline_stages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pipeline_id UUID NOT NULL REFERENCES public.pipelines(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    position INTEGER NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (pipeline_id, position)
);

ALTER TABLE public.customers
    ADD COLUMN IF NOT EXISTS pipeline_id UUID REFERENCES public.pipelines(id),
    ADD COLUMN IF NOT EXISTS pipeline_stage_id UUID REFERENCES public.pipeline_stages(id),
    ADD COLUMN IF NOT EXISTS last_interacted_at TIMESTAMPTZ;

ALTER TABLE public.interactions
    ADD COLUMN IF NOT EXISTS pipeline_stage_id UUID REFERENCES public.pipeline_stages(id);

ALTER TABLE public.reminders
    ADD COLUMN IF NOT EXISTS pipeline_stage_id UUID REFERENCES public.pipeline_stages(id);

CREATE INDEX IF NOT EXISTS idx_pipeline_stages_pipeline_id ON public.pipeline_stages(pipeline_id);
CREATE INDEX IF NOT EXISTS idx_customers_pipeline_stage ON public.customers(pipeline_stage_id);
CREATE INDEX IF NOT EXISTS idx_interactions_stage ON public.interactions(pipeline_stage_id);
CREATE INDEX IF NOT EXISTS idx_reminders_stage ON public.reminders(pipeline_stage_id);
