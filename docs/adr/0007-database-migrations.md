# ADR 0007: Database Migrations Framework

## Status

Accepted

## Context

As the Flowstate-AI project evolves, the database schema must change to support new features, optimize performance, and fix issues. Without a robust migration framework, these changes are error-prone, difficult to track, and challenging to roll back if problems occur.

### Current Situation

- Database schema changes are manual and undocumented
- No version control for database structure
- Difficult to synchronize schema across environments (dev, staging, production)
- No standardized rollback procedures
- Risk of data loss during schema changes
- Inconsistent database state across team members' local environments

### Requirements

1. **Version Control**: All schema changes must be tracked in Git
2. **Reversibility**: Every change must be reversible with a rollback procedure
3. **Environment Consistency**: Same schema across all environments
4. **Automation**: Migrations should be automated in CI/CD
5. **Safety**: Minimize risk of data loss or corruption
6. **Auditability**: Complete history of all schema changes
7. **Performance**: Migrations should complete quickly (< 30s for production)
8. **Simplicity**: Easy for developers to create and test migrations

## Decision

We will implement a database migration framework using **dbmate** with the following components:

### 1. Migration Tool: dbmate

**Rationale for dbmate**:
- Simple, language-agnostic approach
- Uses plain SQL (no DSL to learn)
- Strong PostgreSQL support
- Built-in rollback support
- Fast and reliable
- Active maintenance and community
- Easy to integrate with CI/CD

**Alternatives Considered**:
- **Flyway**: More enterprise-focused, Java-based, heavier
- **Liquibase**: XML/YAML-based, more complex, steeper learning curve
- **Alembic**: Python-specific, not language-agnostic
- **Knex.js**: JavaScript-specific, tied to Node.js ecosystem
- **Sequelize Migrations**: ORM-specific, less flexible

### 2. Migration Structure

```
db/
├── migrations/
│   ├── YYYYMMDDHHMMSS_description.sql
│   └── ...
├── schema.sql (auto-generated)
└── .env.dbmate (environment configs)
```

Each migration file contains:
```sql
-- migrate:up
-- SQL for applying the migration

-- migrate:down
-- SQL for rolling back the migration
```

### 3. Automated Workflows

**GitHub Actions Workflow** (`db-migrate.yml`):
- Manual trigger with environment selection (dev, staging, production)
- Actions: up (apply), status (check), rollback
- Dry run mode for reviewing SQL before execution
- Automatic backup before production migrations
- Health checks after migration
- Automatic rollback on failure
- Issue creation on failure

### 4. Environment Configuration

Separate database URLs for each environment:
- Development: Local PostgreSQL or SQLite
- Staging: Staging database server
- Production: Production database cluster

Configuration stored in `.env.dbmate` (not committed to Git):
```bash
DEV_DATABASE_URL="postgresql://..."
STAGING_DATABASE_URL="postgresql://..."
PRODUCTION_DATABASE_URL="postgresql://..."
```

### 5. Migration Best Practices

**Design Principles**:
1. One logical change per migration
2. Always include rollback SQL
3. Make migrations idempotent (safe to run multiple times)
4. Use transactions for data migrations
5. Add indexes for foreign keys
6. Test rollback before deploying

**Performance Guidelines**:
1. Target < 30 seconds for production migrations
2. Create indexes concurrently (PostgreSQL)
3. Add columns without defaults, then update
4. Batch large data migrations

**Security Guidelines**:
1. Never include sensitive data in migrations
2. Review permissions and grants
3. Validate input data with constraints
4. Use parameterized queries for data migrations

### 6. Deployment Process

**Development**:
```bash
# Create migration
dbmate new add_feature

# Apply locally
dbmate up

# Test rollback
dbmate rollback

# Re-apply
dbmate up
```

**Staging** (automatic on develop push):
- Migrations applied automatically via deployment workflow
- Health checks verify application functionality

**Production** (manual with approval):
1. Dry run to review SQL
2. Create automatic backup
3. Apply migration
4. Health checks
5. Automatic rollback on failure

### 7. Documentation

Comprehensive documentation in `docs/DATABASE_MIGRATIONS.md` covering:
- Creating migrations
- Testing procedures
- Deployment process
- Rollback procedures
- Best practices
- Common patterns
- Troubleshooting guide

## Consequences

### Positive

1. **Version Control**: All schema changes tracked in Git with full history
2. **Consistency**: Identical schema across all environments
3. **Safety**: Automatic backups and rollback on failure
4. **Automation**: Integrated with CI/CD for seamless deployments
5. **Auditability**: Complete audit trail of all schema changes
6. **Developer Experience**: Simple SQL-based migrations, easy to learn
7. **Reversibility**: Every migration has a tested rollback procedure
8. **Performance**: Fast migrations with optimization guidelines
9. **Documentation**: Comprehensive guides for all scenarios

### Negative

1. **Learning Curve**: Team must learn dbmate and migration best practices
2. **Discipline Required**: Developers must write good rollback SQL
3. **Testing Overhead**: Migrations must be tested locally before deployment
4. **Coordination Needed**: Large migrations require coordination across team
5. **Manual Production**: Production migrations require manual trigger (by design for safety)

### Neutral

1. **Tool Dependency**: Committed to dbmate as migration tool
2. **SQL Knowledge**: Developers need SQL proficiency (already required)
3. **Process Change**: New workflow for schema changes

## Implementation

### Phase 1: Foundation (Complete)
- [x] Install and configure dbmate
- [x] Create initial migration (0001_init.sql)
- [x] Set up directory structure
- [x] Create environment configuration template

### Phase 2: Automation (Complete)
- [x] Create GitHub Actions workflow (db-migrate.yml)
- [x] Implement dry run capability
- [x] Add automatic backup for production
- [x] Implement health checks
- [x] Add automatic rollback on failure
- [x] Create issue on failure

### Phase 3: Documentation (Complete)
- [x] Create comprehensive migration guide (DATABASE_MIGRATIONS.md)
- [x] Document best practices
- [x] Provide common patterns and examples
- [x] Create troubleshooting guide
- [x] Document rollback procedures

### Phase 4: Integration (Next Steps)
- [ ] Integrate with deployment workflows
- [ ] Add migration status to health checks
- [ ] Create migration dashboard in Godmode
- [ ] Set up migration notifications
- [ ] Train team on migration process

## Monitoring and Metrics

Track the following metrics:
1. **Migration Success Rate**: Percentage of successful migrations
2. **Migration Duration**: Time to complete migrations
3. **Rollback Frequency**: How often rollbacks are needed
4. **Migration Coverage**: Percentage of schema changes using migrations
5. **Time to Recovery**: Time to recover from failed migration

## Review and Evolution

This decision will be reviewed:
- After first 10 production migrations
- Quarterly as part of technical review
- When significant issues arise
- When new migration patterns emerge

## References

- [dbmate Documentation](https://github.com/amacneil/dbmate)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Database Migration Best Practices](https://www.postgresql.org/docs/current/ddl.html)
- [Deployment Runbook](../DEPLOYMENT_RUNBOOK.md)
- [Database Migrations Guide](../DATABASE_MIGRATIONS.md)

## Related ADRs

- ADR 0001: Phase 0 Baseline Establishment
- ADR 0002: Supply Chain Security
- ADR 0003: Container Optimization
- ADR 0004: Documentation Portal
- ADR 0006: Automated Deployments

## Date

2025-01-10

## Authors

- Manus AI (Implementation)
- Benji Danielsen (Review and Approval)

