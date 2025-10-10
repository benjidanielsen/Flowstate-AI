-- migrate:up
CREATE TABLE IF NOT EXISTS healthcheck (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- migrate:down
DROP TABLE IF EXISTS healthcheck;
