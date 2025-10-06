-- Migration: Optimize database schema and indexes for Flowstate-AI

-- 1. Add indexes to frequently queried columns
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_projects_owner_id ON projects(owner_id);
CREATE INDEX IF NOT EXISTS idx_documents_project_id ON documents(project_id);

-- 2. Alter columns for better performance and storage
-- Assuming some text columns can be shortened or converted to more efficient types
ALTER TABLE users ALTER COLUMN status TYPE VARCHAR(20);
ALTER TABLE sessions ALTER COLUMN session_token TYPE VARCHAR(128);

-- 3. Add foreign keys with ON DELETE CASCADE where appropriate
ALTER TABLE sessions
  DROP CONSTRAINT IF EXISTS fk_sessions_user_id,
  ADD CONSTRAINT fk_sessions_user_id FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE projects
  DROP CONSTRAINT IF EXISTS fk_projects_owner_id,
  ADD CONSTRAINT fk_projects_owner_id FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE documents
  DROP CONSTRAINT IF EXISTS fk_documents_project_id,
  ADD CONSTRAINT fk_documents_project_id FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE;

-- 4. Vacuum analyze for updated statistics
VACUUM ANALYZE;
