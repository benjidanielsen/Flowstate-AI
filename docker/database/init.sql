-- Flowstate-AI Database Initialization Script
-- This script runs when the PostgreSQL container first starts

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm"; -- For text search optimization

-- Create application database (if not exists)
SELECT 'CREATE DATABASE flowstate_ai'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'flowstate_ai')\gexec

-- Connect to the application database
\c flowstate_ai

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Grant necessary permissions
GRANT ALL PRIVILEGES ON DATABASE flowstate_ai TO flowstate;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO flowstate;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO flowstate;

-- Set default privileges for future objects
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO flowstate;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO flowstate;

-- Log successful initialization
DO $$
BEGIN
    RAISE NOTICE 'Flowstate-AI database initialized successfully at %', NOW();
END $$;
