# Database Migrations Guide

## Overview

This guide provides comprehensive documentation for managing database migrations in the Flowstate-AI project using dbmate. It covers migration creation, testing, deployment, rollback procedures, and best practices.

## Table of Contents

1. [Introduction](#introduction)
2. [Migration Framework](#migration-framework)
3. [Creating Migrations](#creating-migrations)
4. [Testing Migrations](#testing-migrations)
5. [Deploying Migrations](#deploying-migrations)
6. [Rollback Procedures](#rollback-procedures)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)
9. [Common Patterns](#common-patterns)

## Introduction

Database migrations are version-controlled changes to the database schema. They allow teams to evolve the database structure safely and consistently across all environments (development, staging, production).

### Why dbmate?

We chose dbmate for database migrations because it provides a simple, language-agnostic approach to database schema management with strong support for PostgreSQL, MySQL, and SQLite. It uses plain SQL migrations, making it easy to understand and review changes.

### Key Features

- **Version Control**: All migrations are tracked in Git
- **Reversible**: Each migration includes both `up` and `down` SQL
- **Idempotent**: Safe to run multiple times
- **Environment-Specific**: Separate configurations for dev, staging, production
- **Automated**: Integrated with CI/CD workflows
- **Auditable**: Complete history of schema changes

## Migration Framework

### Directory Structure

```
db/
├── migrations/
│   ├── 0001_init.sql
│   ├── 0002_add_user_preferences.sql
│   └── 0003_add_customer_tags.sql
└── schema.sql (auto-generated)
```

### Migration File Format

Each migration file follows this structure:

```sql
-- migrate:up
-- Description of what this migration does

CREATE TABLE example (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- migrate:down
-- Rollback instructions

DROP TABLE IF EXISTS example;
```

### Configuration Files

**`.env.dbmate`**: Environment-specific database URLs

```bash
DEV_DATABASE_URL="postgresql://user:pass@localhost:5432/flowstate_dev"
STAGING_DATABASE_URL="postgresql://user:pass@staging-db:5432/flowstate_staging"
PRODUCTION_DATABASE_URL="postgresql://user:pass@prod-db:5432/flowstate_production"
```

## Creating Migrations

### Prerequisites

1. **Install dbmate**:
   ```bash
   # macOS
   brew install dbmate
   
   # Linux
   sudo curl -fsSL -o /usr/local/bin/dbmate \
     https://github.com/amacneil/dbmate/releases/latest/download/dbmate-linux-amd64
   sudo chmod +x /usr/local/bin/dbmate
   
   # Windows
   scoop install dbmate
   ```

2. **Set database URL**:
   ```bash
   export DATABASE_URL="postgresql://flowstate:password@localhost:5432/flowstate_dev"
   ```

### Creating a New Migration

```bash
# Create a new migration file
dbmate new add_customer_tags

# This creates: db/migrations/YYYYMMDDHHMMSS_add_customer_tags.sql
```

### Writing Migration SQL

**Example: Adding a new table**

```sql
-- migrate:up
-- Add customer tags table for categorizing customers

CREATE TABLE customer_tags (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    tag VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(customer_id, tag)
);

CREATE INDEX idx_customer_tags_customer_id ON customer_tags(customer_id);
CREATE INDEX idx_customer_tags_tag ON customer_tags(tag);

-- migrate:down
-- Remove customer tags table

DROP TABLE IF EXISTS customer_tags;
```

**Example: Adding a column**

```sql
-- migrate:up
-- Add timezone preference to users table

ALTER TABLE users 
ADD COLUMN timezone VARCHAR(50) DEFAULT 'UTC';

-- migrate:down
-- Remove timezone column from users table

ALTER TABLE users 
DROP COLUMN IF EXISTS timezone;
```

**Example: Data migration**

```sql
-- migrate:up
-- Migrate old status values to new format

UPDATE customers 
SET pipeline_stage = 'qualified' 
WHERE pipeline_stage = 'interested';

UPDATE customers 
SET pipeline_stage = 'closed_won' 
WHERE pipeline_stage = 'customer';

-- migrate:down
-- Revert status values to old format

UPDATE customers 
SET pipeline_stage = 'interested' 
WHERE pipeline_stage = 'qualified';

UPDATE customers 
SET pipeline_stage = 'customer' 
WHERE pipeline_stage = 'closed_won';
```

## Testing Migrations

### Local Testing

1. **Check current status**:
   ```bash
   dbmate status
   ```

2. **Apply migrations (up)**:
   ```bash
   dbmate up
   ```

3. **Test rollback (down)**:
   ```bash
   dbmate rollback
   ```

4. **Re-apply to verify idempotency**:
   ```bash
   dbmate up
   ```

5. **Verify schema**:
   ```bash
   # Connect to database
   psql $DATABASE_URL
   
   # Check tables
   \dt
   
   # Check specific table
   \d customers
   
   # Verify data
   SELECT * FROM customers LIMIT 5;
   ```

### Dry Run Testing

```bash
# Show SQL without executing
dbmate up --dry-run

# Show rollback SQL
dbmate rollback --dry-run
```

### Automated Testing

Migrations are automatically tested in CI/CD:

1. **On Pull Request**: Migrations are applied to a test database
2. **Schema validation**: Ensures migrations don't break existing queries
3. **Rollback testing**: Verifies down migrations work correctly
4. **Performance testing**: Checks for slow migrations (> 30s)

## Deploying Migrations

### Development Environment

Migrations are applied automatically when starting the development environment:

```bash
# Using Docker Compose
docker-compose up -d db
docker-compose exec backend npm run db:migrate

# Or manually
export DATABASE_URL="postgresql://flowstate:password@localhost:5432/flowstate_dev"
dbmate up
```

### Staging Environment

Migrations are applied automatically on deployment to staging:

```bash
# Via GitHub Actions (automatic on develop push)
# Or manually:
gh workflow run db-migrate.yml \
  -f environment=staging \
  -f action=up \
  -f dry_run=false
```

### Production Environment

Production migrations require manual approval:

```bash
# 1. Dry run first to review SQL
gh workflow run db-migrate.yml \
  -f environment=production \
  -f action=up \
  -f dry_run=true

# 2. Review the SQL output in workflow logs

# 3. Create database backup (automatic in workflow)

# 4. Apply migration
gh workflow run db-migrate.yml \
  -f environment=production \
  -f action=up \
  -f dry_run=false

# 5. Verify application health
curl https://flowstate-ai.com/health/db
```

### Migration Workflow

```
┌─────────────────────────────────────────────────────┐
│           Production Migration Process               │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
            ┌───────────────────────┐
            │  1. Dry Run Review    │
            │  (Show SQL)           │
            └───────────┬───────────┘
                        │
                        ▼
            ┌───────────────────────┐
            │  2. Create Backup     │
            │  (Automatic)          │
            └───────────┬───────────┘
                        │
                        ▼
            ┌───────────────────────┐
            │  3. Apply Migration   │
            │  (dbmate up)          │
            └───────────┬───────────┘
                        │
                        ▼
            ┌───────────────────────┐
            │  4. Health Check      │
            │  (Verify DB)          │
            └───────────┬───────────┘
                        │
                   ┌────┴────┐
                   │         │
                Success   Failure
                   │         │
                   ▼         ▼
          ┌────────────┐  ┌──────────────┐
          │  Complete  │  │  Auto        │
          │  & Record  │  │  Rollback    │
          └────────────┘  └──────────────┘
```

## Rollback Procedures

### When to Rollback

Rollback a migration if:
- Application errors occur after deployment
- Performance degradation is observed
- Data integrity issues are detected
- Migration was applied to wrong environment

### Automatic Rollback

The deployment workflow automatically rolls back if:
- Health checks fail after migration
- Application fails to start
- Database connectivity is lost

### Manual Rollback

```bash
# 1. Check current migration status
gh workflow run db-migrate.yml \
  -f environment=production \
  -f action=status

# 2. Dry run rollback to review SQL
gh workflow run db-migrate.yml \
  -f environment=production \
  -f action=rollback \
  -f dry_run=true

# 3. Execute rollback
gh workflow run db-migrate.yml \
  -f environment=production \
  -f action=rollback \
  -f dry_run=false

# 4. Verify application health
curl https://flowstate-ai.com/health/db
```

### Emergency Rollback

If the automated workflow is unavailable:

```bash
# 1. SSH into production server
ssh production-server

# 2. Set database URL
export DATABASE_URL="postgresql://flowstate:password@prod-db:5432/flowstate_production"

# 3. Check status
dbmate status

# 4. Rollback last migration
dbmate rollback

# 5. Verify database
psql $DATABASE_URL -c "SELECT version FROM schema_migrations ORDER BY version DESC LIMIT 5;"

# 6. Restart application
docker-compose restart backend
```

### Rollback Best Practices

1. **Always test rollback locally first**
2. **Review rollback SQL in dry run**
3. **Have database backup before rollback**
4. **Verify application works after rollback**
5. **Document reason for rollback**
6. **Fix migration before re-applying**

## Best Practices

### Migration Design

1. **One logical change per migration**
   - ✅ Good: `add_customer_tags_table.sql`
   - ❌ Bad: `add_tags_and_fix_users_and_update_indexes.sql`

2. **Always include rollback SQL**
   - Every `migrate:up` must have a corresponding `migrate:down`
   - Test rollback before deploying

3. **Make migrations idempotent**
   ```sql
   -- Good: Safe to run multiple times
   CREATE TABLE IF NOT EXISTS customers (...);
   ALTER TABLE users ADD COLUMN IF NOT EXISTS timezone VARCHAR(50);
   
   -- Bad: Will fail on second run
   CREATE TABLE customers (...);
   ALTER TABLE users ADD COLUMN timezone VARCHAR(50);
   ```

4. **Use transactions for data migrations**
   ```sql
   -- migrate:up
   BEGIN;
   UPDATE customers SET status = 'active' WHERE status IS NULL;
   COMMIT;
   
   -- migrate:down
   BEGIN;
   UPDATE customers SET status = NULL WHERE status = 'active';
   COMMIT;
   ```

5. **Add indexes for foreign keys**
   ```sql
   CREATE TABLE interactions (
       customer_id UUID REFERENCES customers(id)
   );
   CREATE INDEX idx_interactions_customer_id ON interactions(customer_id);
   ```

### Performance Considerations

1. **Avoid long-running migrations**
   - Break large data migrations into batches
   - Consider background jobs for massive updates
   - Target: < 30 seconds for production migrations

2. **Create indexes concurrently** (PostgreSQL)
   ```sql
   CREATE INDEX CONCURRENTLY idx_customers_email ON customers(email);
   ```

3. **Add columns with defaults carefully**
   ```sql
   -- Slow: Rewrites entire table
   ALTER TABLE customers ADD COLUMN status VARCHAR(50) DEFAULT 'active';
   
   -- Fast: Add column without default, then update
   ALTER TABLE customers ADD COLUMN status VARCHAR(50);
   UPDATE customers SET status = 'active' WHERE status IS NULL;
   ALTER TABLE customers ALTER COLUMN status SET DEFAULT 'active';
   ```

### Security Considerations

1. **Never include sensitive data in migrations**
   - No passwords, API keys, or PII in SQL
   - Use environment variables or secrets management

2. **Review permissions**
   ```sql
   -- Grant only necessary permissions
   GRANT SELECT, INSERT, UPDATE ON customers TO flowstate_app;
   ```

3. **Validate input data**
   ```sql
   ALTER TABLE users ADD CONSTRAINT email_format 
   CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$');
   ```

### Documentation

1. **Write clear migration descriptions**
   ```sql
   -- migrate:up
   -- Add customer tags table to support categorization and filtering
   -- This enables users to organize customers by custom tags
   -- Related to feature: Customer Segmentation (FLOW-123)
   ```

2. **Document breaking changes**
   ```sql
   -- migrate:up
   -- ⚠️ BREAKING CHANGE: Renames 'status' column to 'pipeline_stage'
   -- Applications must be updated to use new column name before this migration
   ```

3. **Link to issues/PRs**
   ```sql
   -- migrate:up
   -- Implements feature request: https://github.com/org/repo/issues/123
   ```

## Troubleshooting

### Common Issues

#### 1. Migration Already Applied

**Symptom**: `Error: migration already applied`

**Cause**: Attempting to apply a migration that's already in the database

**Solution**:
```bash
# Check migration status
dbmate status

# If migration should be re-applied, rollback first
dbmate rollback
dbmate up
```

#### 2. Syntax Error in Migration

**Symptom**: `ERROR: syntax error at or near "..."`

**Cause**: Invalid SQL in migration file

**Solution**:
1. Test SQL in psql first
2. Check for typos and missing semicolons
3. Validate SQL with linter
4. Fix and re-run

#### 3. Foreign Key Constraint Violation

**Symptom**: `ERROR: insert or update on table violates foreign key constraint`

**Cause**: Data exists that violates new constraint

**Solution**:
```sql
-- migrate:up
-- Clean up orphaned records first
DELETE FROM interactions WHERE customer_id NOT IN (SELECT id FROM customers);

-- Then add constraint
ALTER TABLE interactions 
ADD CONSTRAINT fk_customer 
FOREIGN KEY (customer_id) REFERENCES customers(id);
```

#### 4. Migration Timeout

**Symptom**: Migration runs for > 30 seconds and times out

**Cause**: Large data migration or missing indexes

**Solution**:
1. Break into smaller batches
2. Add indexes before data migration
3. Consider background job for large updates

#### 5. Rollback Fails

**Symptom**: `Error: rollback failed`

**Cause**: Rollback SQL is invalid or data has changed

**Solution**:
1. Review rollback SQL
2. Manually fix database state
3. Update migration with correct rollback
4. Test thoroughly before production

### Debug Commands

```bash
# Check migration status
dbmate status

# Show applied migrations
psql $DATABASE_URL -c "SELECT * FROM schema_migrations ORDER BY version;"

# Show table structure
psql $DATABASE_URL -c "\d customers"

# Check for locks
psql $DATABASE_URL -c "SELECT * FROM pg_locks WHERE NOT granted;"

# Verify database connectivity
dbmate status

# Show migration history
git log --oneline db/migrations/
```

## Common Patterns

### Adding a Table

```sql
-- migrate:up
CREATE TABLE customer_notes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    note TEXT NOT NULL,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_customer_notes_customer_id ON customer_notes(customer_id);
CREATE INDEX idx_customer_notes_created_at ON customer_notes(created_at);

CREATE TRIGGER update_customer_notes_updated_at 
BEFORE UPDATE ON customer_notes
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- migrate:down
DROP TABLE IF EXISTS customer_notes;
```

### Adding a Column

```sql
-- migrate:up
ALTER TABLE customers 
ADD COLUMN last_purchase_date TIMESTAMP;

CREATE INDEX idx_customers_last_purchase_date 
ON customers(last_purchase_date) 
WHERE last_purchase_date IS NOT NULL;

-- migrate:down
ALTER TABLE customers 
DROP COLUMN IF EXISTS last_purchase_date;
```

### Renaming a Column

```sql
-- migrate:up
ALTER TABLE customers 
RENAME COLUMN status TO pipeline_stage;

-- migrate:down
ALTER TABLE customers 
RENAME COLUMN pipeline_stage TO status;
```

### Adding an Enum Type

```sql
-- migrate:up
CREATE TYPE customer_status AS ENUM ('new', 'qualified', 'customer', 'churned');

ALTER TABLE customers 
ADD COLUMN status_enum customer_status DEFAULT 'new';

-- Migrate existing data
UPDATE customers SET status_enum = status::customer_status;

-- migrate:down
ALTER TABLE customers 
DROP COLUMN IF EXISTS status_enum;

DROP TYPE IF EXISTS customer_status;
```

### Adding Constraints

```sql
-- migrate:up
-- Add NOT NULL constraint
ALTER TABLE customers 
ALTER COLUMN email SET NOT NULL;

-- Add UNIQUE constraint
ALTER TABLE customers 
ADD CONSTRAINT unique_customer_email UNIQUE (email);

-- Add CHECK constraint
ALTER TABLE customers 
ADD CONSTRAINT valid_relationship_score 
CHECK (relationship_score >= 0 AND relationship_score <= 100);

-- migrate:down
ALTER TABLE customers 
DROP CONSTRAINT IF EXISTS valid_relationship_score;

ALTER TABLE customers 
DROP CONSTRAINT IF EXISTS unique_customer_email;

ALTER TABLE customers 
ALTER COLUMN email DROP NOT NULL;
```

### Data Migration with Batching

```sql
-- migrate:up
-- Update customers in batches to avoid long locks
DO $$
DECLARE
    batch_size INTEGER := 1000;
    offset_val INTEGER := 0;
    rows_updated INTEGER;
BEGIN
    LOOP
        UPDATE customers 
        SET normalized_email = LOWER(email)
        WHERE id IN (
            SELECT id FROM customers 
            WHERE normalized_email IS NULL 
            LIMIT batch_size
        );
        
        GET DIAGNOSTICS rows_updated = ROW_COUNT;
        EXIT WHEN rows_updated = 0;
        
        -- Small delay between batches
        PERFORM pg_sleep(0.1);
    END LOOP;
END $$;

-- migrate:down
UPDATE customers SET normalized_email = NULL;
```

## Migration Checklist

### Before Creating Migration

- [ ] Understand the schema change required
- [ ] Review existing schema and constraints
- [ ] Plan rollback strategy
- [ ] Consider performance impact
- [ ] Identify affected queries and code

### Creating Migration

- [ ] Create migration file with descriptive name
- [ ] Write clear migration description
- [ ] Implement `migrate:up` SQL
- [ ] Implement `migrate:down` SQL
- [ ] Make migration idempotent
- [ ] Add necessary indexes
- [ ] Include constraints and validations

### Testing Migration

- [ ] Test migration locally (up)
- [ ] Test rollback locally (down)
- [ ] Verify data integrity
- [ ] Check application functionality
- [ ] Test with production-like data volume
- [ ] Measure migration duration
- [ ] Review SQL with team

### Deploying Migration

- [ ] Merge migration PR
- [ ] Deploy to staging first
- [ ] Verify staging application
- [ ] Run dry run on production
- [ ] Create production backup
- [ ] Apply to production
- [ ] Monitor application health
- [ ] Verify production functionality

### Post-Deployment

- [ ] Document migration completion
- [ ] Update schema documentation
- [ ] Monitor for errors
- [ ] Communicate to team
- [ ] Archive backup after 30 days

## Additional Resources

- [dbmate Documentation](https://github.com/amacneil/dbmate)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Database Migration Best Practices](https://www.postgresql.org/docs/current/ddl.html)
- [Deployment Runbook](./DEPLOYMENT_RUNBOOK.md)
- [Operations Runbook](./OPS_RUNBOOK.md)
- [ADR 0007: Database Migrations](./adr/0007-database-migrations.md)

