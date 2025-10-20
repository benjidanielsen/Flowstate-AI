CREATE EXTENSION IF NOT EXISTS vector; CREATE TABLE public.documents (id SERIAL PRIMARY KEY, content TEXT, metadata JSONB, embedding TEXT);
