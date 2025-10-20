CREATE TABLE public.agent_states (id SERIAL PRIMARY KEY, agent_name TEXT NOT NULL, state JSONB, created_at TIMESTAMPTZ DEFAULT NOW(), updated_at TIMESTAMPTZ DEFAULT NOW());
