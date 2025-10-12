# Deployment Runbook

## Overview

This runbook provides step-by-step procedures for deploying Flowstate-AI to staging and production environments. It covers both automated and manual deployment processes, health checks, rollback procedures, and troubleshooting.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Deployment Environments](#deployment-environments)
3. [Automated Deployments](#automated-deployments)
4. [Manual Deployments](#manual-deployments)
5. [Health Checks](#health-checks)
6. [Rollback Procedures](#rollback-procedures)
7. [Troubleshooting](#troubleshooting)
8. [Post-Deployment Tasks](#post-deployment-tasks)

## Prerequisites

### Required Secrets

Ensure the following GitHub secrets are configured:

**Staging:**
- `STAGING_SSH_KEY`: SSH private key for staging server
- `STAGING_HOST`: Staging server hostname/IP
- `STAGING_USER`: SSH username for staging
- `STAGING_PORT`: SSH port (default: 22)
- `STAGING_URL`: Staging application URL

**Production:**
- `PRODUCTION_SSH_KEY`: SSH private key for production server
- `PRODUCTION_HOST`: Production server hostname/IP
- `PRODUCTION_USER`: SSH username for production
- `PRODUCTION_PORT`: SSH port (default: 22)
- `PRODUCTION_URL`: Production application URL

### Server Requirements

**Staging:**
- 1x VM (2 vCPU, 4GB RAM)
- PostgreSQL database
- Docker and Docker Compose installed
- SSH access configured

**Production:**
- 2x VMs (4 vCPU, 8GB RAM each) for blue-green deployment
- PostgreSQL HA cluster
- Docker and Docker Compose installed
- Load balancer configured
- SSH access configured

### Local Requirements

- GitHub CLI (`gh`) installed and authenticated
- SSH client configured
- Docker installed (for building images)
- `jq` installed (for JSON parsing)

## Deployment Environments

### Staging Environment

- **Purpose**: Testing and validation before production
- **URL**: https://staging.flowstate-ai.com
- **Branch**: `develop`
- **Deployment Trigger**: Automatic on push to `develop` branch
- **Deployment Strategy**: Rolling update
- **Downtime**: Minimal (< 30 seconds)

### Production Environment

- **Purpose**: Live customer-facing environment
- **URL**: https://flowstate-ai.com
- **Branch**: `main` (tagged releases)
- **Deployment Trigger**: Manual via release or workflow dispatch
- **Deployment Strategy**: Blue-green deployment
- **Downtime**: Zero downtime

## Automated Deployments

### Staging Deployment

Staging deployments are triggered automatically when code is pushed to the `develop` branch.

**Workflow**: `.github/workflows/deploy-staging.yml`

**Process**:
1. Code is pushed to `develop` branch
2. GitHub Actions workflow is triggered
3. Docker images are built and pushed to GHCR
4. Images are deployed to staging server via SSH
5. Health checks are performed
6. Smoke tests are executed
7. Deployment status is reported

**Monitoring**:
```bash
# View workflow runs
gh run list --workflow=deploy-staging.yml

# View specific run details
gh run view <run-id>

# Watch run in real-time
gh run watch <run-id>
```

**Manual Trigger**:
```bash
# Deploy specific version to staging
gh workflow run deploy-staging.yml -f version=<commit-sha>
```

### Production Deployment

Production deployments are triggered by creating a release or manually via workflow dispatch.

**Workflow**: `.github/workflows/deploy-production.yml`

**Process**:
1. Release is created with semantic version tag (e.g., v1.2.3)
2. Pre-deployment checks are performed
3. Docker images are built and pushed to GHCR
4. Database backup is created
5. Green environment is deployed
6. Health checks validate green environment
7. Traffic is switched to green environment
8. Blue environment is stopped
9. Post-deployment tasks are executed
10. Deployment status is reported

**Creating a Release**:
```bash
# Create and push a version tag
git tag -a v1.2.3 -m "Release v1.2.3"
git push origin v1.2.3

# Create GitHub release
gh release create v1.2.3 --title "v1.2.3" --notes "Release notes here"
```

**Manual Trigger**:
```bash
# Deploy specific version to production
gh workflow run deploy-production.yml -f version=v1.2.3

# Deploy with skipped tests (not recommended)
gh workflow run deploy-production.yml -f version=v1.2.3 -f skip_tests=true
```

## 2. Initial Setup (First-Time Deployment)

This section covers the initial setup and deployment of the Flowstate-AI system.

### 2.1. Clone the Repository

Clone the project repository to the deployment server:

```bash
git clone https://github.com/benjidanielsen/Flowstate-AI.git
cd Flowstate-AI
```

### 2.2. Configure Secrets

Use the provided script to generate secure secrets and create the `.env.production` file:

```bash
./scripts/setup-secrets.sh
```

Follow the prompts to configure domain names, ports, and other settings. The script will generate a `.env.production` file with secure defaults. **Review this file and ensure all settings are correct for your environment.**

**IMPORTANT:** Securely back up the `.env.production` file. It contains sensitive credentials and is critical for system operation.

### 2.3. Run the Deployment

Execute the deployment script to build and start all services:

```bash
./scripts/deploy-production.sh
```

This script will:

1.  Check for prerequisites.
2.  Validate the `.env.production` file.
3.  Pull the latest Docker images.
4.  Build the application images.
5.  Start the PostgreSQL and Redis services.
6.  Run database migrations using `dbmate`.
7.  Start all application services (backend, frontend, worker).
8.  Perform a health check on all services.

## 3. Routine Operations

This section describes common operational tasks.

### 3.1. Updating the System

To update the system to the latest version:

1.  **Pull the latest code:**

    ```bash
    git pull origin main
    ```

2.  **Run the deployment script:**

    ```bash
    ./scripts/deploy-production.sh
    ```

    The script will automatically rebuild images and restart services.

### 3.2. Checking System Status

To check the health of all services, run the health check script:

```bash
./scripts/health-check.sh
```

To view the status of running containers:

```bash
docker-compose -f docker-compose.production.yml ps
```

### 3.3. Viewing Logs

To view the logs for all services in real-time:

```bash
docker-compose -f docker-compose.production.yml logs -f
```

To view the logs for a specific service:

```bash
docker-compose -f docker-compose.production.yml logs -f <service_name>
```

(e.g., `backend`, `frontend`, `postgres`)

### 3.4. Stopping and Starting Services

-   **To stop all services:**

    ```bash
    docker-compose -f docker-compose.production.yml down
    ```

-   **To start all services:**

    ```bash
    docker-compose -f docker-compose.production.yml up -d
    ```

## 4. Database Management

Database migrations are managed using `dbmate`.

### 4.1. Creating a New Migration

To create a new migration file:

```bash
dbmate new <migration_name>
```

This will create a new SQL file in the `db/migrations` directory. Edit this file to define your schema changes.

### 4.2. Running Migrations

To apply all pending migrations:

```bash
dbmate up
```

The deployment script automatically runs this command.

### 4.3. Rolling Back Migrations

To roll back the last migration:

```bash
dbmate down
```

## 5. Troubleshooting

-   **Service Not Starting:** Check the service logs (`docker-compose logs -f <service_name>`) for errors. Common issues include incorrect environment variables or port conflicts.
-   **Database Connection Issues:** Ensure the `DATABASE_URL` in `.env.production` is correct and that the PostgreSQL container is running and healthy.
-   **Permission Errors:** Ensure all scripts in the `scripts/` directory are executable (`chmod +x scripts/*.sh`).

## 6. Security Best Practices

-   **Rotate Secrets:** Regularly run `./scripts/setup-secrets.sh` to generate new secrets and update your `.env.production` file.
-   **Restrict Access:** Limit access to the deployment server and the `.env.production` file.
-   **Enable HTTPS:** For production deployments, configure Nginx with SSL/TLS certificates to enable HTTPS. The `docker/nginx/nginx.conf` file includes a template for this.
-   **Regularly Update:** Keep the system and its dependencies up-to-date by pulling the latest code and re-deploying.



### Prerequisites

1. Ensure you have SSH access to the target server
2. Verify Docker images are available in GHCR
3. Backup database before production deployments

### Staging Manual Deployment

```bash
# 1. SSH into staging server
ssh -i ~/.ssh/staging_key user@staging-host

# 2. Navigate to application directory
cd /opt/flowstate-ai

# 3. Pull latest images
docker pull ghcr.io/benjidanielsen/flowstate-ai/backend:staging-latest
docker pull ghcr.io/benjidanielsen/flowstate-ai/frontend:staging-latest
docker pull ghcr.io/benjidanielsen/flowstate-ai/python-worker:staging-latest

# 4. Stop current containers
docker-compose -f docker/compose.yml down

# 5. Start new containers
docker-compose -f docker/compose.yml up -d

# 6. Verify health
docker-compose -f docker/compose.yml ps
curl -f https://staging.flowstate-ai.com/health
```

### Production Manual Deployment

```bash
# 1. SSH into production server
ssh -i ~/.ssh/production_key user@production-host

# 2. Navigate to application directory
cd /opt/flowstate-ai

# 3. Create backup
BACKUP_DIR="/opt/flowstate-ai/backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
docker exec flowstate-db pg_dump -U flowstate flowstate > "$BACKUP_DIR/database.sql"

# 4. Pull versioned images
VERSION="v1.2.3"
docker pull ghcr.io/benjidanielsen/flowstate-ai/backend:$VERSION
docker pull ghcr.io/benjidanielsen/flowstate-ai/frontend:$VERSION
docker pull ghcr.io/benjidanielsen/flowstate-ai/python-worker:$VERSION

# 5. Deploy to green environment
docker-compose -f docker/compose.green.yml up -d

# 6. Wait for green environment
sleep 30

# 7. Health check green environment
curl -f http://localhost:8081/health

# 8. Switch traffic (update load balancer)
# This step depends on your load balancer configuration

# 9. Stop blue environment
docker-compose -f docker/compose.yml down

# 10. Promote green to blue
docker-compose -f docker/compose.green.yml down
docker-compose -f docker/compose.yml up -d

# 11. Verify production health
curl -f https://flowstate-ai.com/health
```

## Health Checks

### Backend Health Check

```bash
# Basic health check
curl -f https://flowstate-ai.com/health

# Expected response:
# {"status":"healthy","timestamp":"2025-10-10T12:00:00Z"}

# Detailed health check with components
curl -s https://flowstate-ai.com/health | jq '.'

# Check database connectivity
curl -s https://flowstate-ai.com/health/db | jq '.'
```

### Frontend Health Check

```bash
# Check frontend is accessible
curl -f https://flowstate-ai.com

# Check specific routes
curl -f https://flowstate-ai.com/dashboard
curl -f https://flowstate-ai.com/login
```

### Service-Specific Health Checks

```bash
# Backend API
curl -f https://flowstate-ai.com/api/v1/health

# Authentication service
curl -f https://flowstate-ai.com/api/v1/auth/status

# Stats service
curl -f https://flowstate-ai.com/api/v1/stats

# Python worker (internal)
docker exec flowstate-python-worker curl -f http://localhost:8000/health
```

### Docker Container Health

```bash
# Check container status
docker-compose ps

# Check container logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs python-worker

# Check container resource usage
docker stats --no-stream
```

## Rollback Procedures

### Staging Rollback

Staging rollbacks are automatic on deployment failure. For manual rollback:

```bash
# 1. SSH into staging server
ssh -i ~/.ssh/staging_key user@staging-host

# 2. Navigate to application directory
cd /opt/flowstate-ai

# 3. Stop current containers
docker-compose -f docker/compose.yml down

# 4. Pull previous version images
docker pull ghcr.io/benjidanielsen/flowstate-ai/backend:staging-<previous-sha>
docker pull ghcr.io/benjidanielsen/flowstate-ai/frontend:staging-<previous-sha>
docker pull ghcr.io/benjidanielsen/flowstate-ai/python-worker:staging-<previous-sha>

# 5. Start containers
docker-compose -f docker/compose.yml up -d

# 6. Verify health
curl -f https://staging.flowstate-ai.com/health
```

### Production Rollback

Production rollbacks are automatic on deployment failure. For manual rollback:

```bash
# 1. SSH into production server
ssh -i ~/.ssh/production_key user@production-host

# 2. Navigate to application directory
cd /opt/flowstate-ai

# 3. Stop failed green environment
docker-compose -f docker/compose.green.yml down

# 4. Identify latest backup
LATEST_BACKUP=$(ls -t /opt/flowstate-ai/backups/ | head -1)
echo "Rolling back to: $LATEST_BACKUP"

# 5. Restore database if needed
docker exec -i flowstate-db psql -U flowstate flowstate < "/opt/flowstate-ai/backups/$LATEST_BACKUP/database.sql"

# 6. Ensure blue environment is running
docker-compose -f docker/compose.yml up -d

# 7. Verify health
curl -f https://flowstate-ai.com/health

# 8. Monitor for errors
for i in {1..10}; do
  curl -s https://flowstate-ai.com/health/errors | jq '.count'
  sleep 10
done
```

### Emergency Rollback (Critical)

If the system is completely down:

```bash
# 1. SSH into production server
ssh -i ~/.ssh/production_key user@production-host

# 2. Stop all containers
cd /opt/flowstate-ai
docker-compose -f docker/compose.yml down
docker-compose -f docker/compose.green.yml down

# 3. Restore from latest backup
LATEST_BACKUP=$(ls -t /opt/flowstate-ai/backups/ | head -1)
docker exec -i flowstate-db psql -U flowstate flowstate < "/opt/flowstate-ai/backups/$LATEST_BACKUP/database.sql"

# 4. Start with last known good version
docker pull ghcr.io/benjidanielsen/flowstate-ai/backend:v<last-good-version>
docker pull ghcr.io/benjidanielsen/flowstate-ai/frontend:v<last-good-version>
docker pull ghcr.io/benjidanielsen/flowstate-ai/python-worker:v<last-good-version>

docker-compose -f docker/compose.yml up -d

# 5. Verify and monitor
curl -f https://flowstate-ai.com/health
docker-compose logs -f
```

## Troubleshooting

### Common Issues

#### 1. Health Check Failures

**Symptom**: Health check endpoint returns 500 or times out

**Diagnosis**:
```bash
# Check container logs
docker-compose logs backend

# Check database connectivity
docker exec flowstate-db psql -U flowstate -c "SELECT 1"

# Check container status
docker-compose ps
```

**Resolution**:
- Restart affected service: `docker-compose restart backend`
- Check database connection string
- Verify environment variables are set correctly

#### 2. Database Connection Issues

**Symptom**: "Connection refused" or "Too many connections"

**Diagnosis**:
```bash
# Check database status
docker exec flowstate-db pg_isready

# Check active connections
docker exec flowstate-db psql -U flowstate -c "SELECT count(*) FROM pg_stat_activity"

# Check database logs
docker-compose logs db
```

**Resolution**:
- Increase max_connections in PostgreSQL config
- Check for connection leaks in application code
- Restart database: `docker-compose restart db`

#### 3. Image Pull Failures

**Symptom**: "manifest unknown" or "unauthorized"

**Diagnosis**:
```bash
# Verify image exists
docker manifest inspect ghcr.io/benjidanielsen/flowstate-ai/backend:v1.2.3

# Check authentication
docker login ghcr.io
```

**Resolution**:
- Verify image tag is correct
- Ensure GitHub token has package read permissions
- Re-authenticate: `echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin`

#### 4. SSH Connection Failures

**Symptom**: "Permission denied" or "Connection timed out"

**Diagnosis**:
```bash
# Test SSH connection
ssh -v -i ~/.ssh/deploy_key user@host

# Check SSH key permissions
ls -l ~/.ssh/deploy_key
```

**Resolution**:
- Verify SSH key has correct permissions: `chmod 600 ~/.ssh/deploy_key`
- Check server firewall rules
- Verify SSH key is added to server's authorized_keys

#### 5. High Error Rates After Deployment

**Symptom**: Increased error count in monitoring

**Diagnosis**:
```bash
# Check error logs
docker-compose logs backend | grep ERROR

# Check error endpoint
curl -s https://flowstate-ai.com/health/errors | jq '.'

# Check application metrics
curl -s https://flowstate-ai.com/metrics
```

**Resolution**:
- Identify root cause from logs
- Consider immediate rollback if critical
- Apply hotfix if issue is minor

### Debug Commands

```bash
# View all running containers
docker ps

# View container resource usage
docker stats

# Execute command in container
docker exec -it flowstate-backend sh

# View container logs (last 100 lines)
docker logs --tail 100 flowstate-backend

# Follow container logs in real-time
docker logs -f flowstate-backend

# Inspect container configuration
docker inspect flowstate-backend

# Check Docker network
docker network inspect flowstate-network

# Check Docker volumes
docker volume ls
docker volume inspect flowstate_data
```

## Post-Deployment Tasks

### Immediate (Within 1 hour)

1. **Monitor Health Metrics**
   ```bash
   # Check health every 5 minutes for 1 hour
   for i in {1..12}; do
     curl -s https://flowstate-ai.com/health | jq '.'
     sleep 300
   done
   ```

2. **Review Error Logs**
   ```bash
   # Check for errors in last hour
   docker-compose logs --since 1h backend | grep ERROR
   ```

3. **Verify Critical Functionality**
   - Test user login
   - Test lead creation
   - Test reminder generation
   - Test NBA recommendations

### Short-term (Within 24 hours)

1. **Clear CDN Cache** (if applicable)
   ```bash
   # Example for Cloudflare
   curl -X POST "https://api.cloudflare.com/client/v4/zones/<zone-id>/purge_cache" \
     -H "Authorization: Bearer <api-token>" \
     -H "Content-Type: application/json" \
     --data '{"purge_everything":true}'
   ```

2. **Update Status Page**
   - Update deployment status
   - Note any known issues
   - Provide ETA for fixes

3. **Notify Stakeholders**
   - Send deployment notification
   - Include version number
   - Highlight new features or fixes

4. **Update Documentation**
   - Update CHANGELOG.md
   - Update version in README.md
   - Update API documentation if needed

### Long-term (Within 1 week)

1. **Performance Analysis**
   - Review response times
   - Check resource utilization
   - Identify optimization opportunities

2. **User Feedback Collection**
   - Monitor support tickets
   - Review user feedback
   - Track feature adoption

3. **Security Review**
   - Review security scan results
   - Address any new vulnerabilities
   - Update dependencies if needed

4. **Backup Verification**
   - Verify backups are being created
   - Test backup restoration
   - Update backup retention policy

## Deployment Checklist

### Pre-Deployment

- [ ] Code reviewed and approved
- [ ] All tests passing
- [ ] Security scans completed
- [ ] Database migrations tested
- [ ] Staging deployment successful
- [ ] Backup created (production only)
- [ ] Stakeholders notified
- [ ] Rollback plan prepared

### During Deployment

- [ ] Deployment workflow triggered
- [ ] Docker images built successfully
- [ ] Images pushed to registry
- [ ] Deployment to server completed
- [ ] Health checks passed
- [ ] Smoke tests passed
- [ ] Traffic switched (production only)

### Post-Deployment

- [ ] Health metrics monitored
- [ ] Error logs reviewed
- [ ] Critical functionality verified
- [ ] CDN cache cleared
- [ ] Status page updated
- [ ] Stakeholders notified
- [ ] Documentation updated
- [ ] Backup verified

## Emergency Contacts

- **DevOps Lead**: [Contact Information]
- **Backend Lead**: [Contact Information]
- **Database Admin**: [Contact Information]
- **Security Team**: [Contact Information]
- **On-Call Engineer**: [Contact Information]

## Additional Resources

- [System Architecture Documentation](./SYSTEM_ARCHITECTURE.md)
- [Operations Runbook](./OPS_RUNBOOK.md)
- [Disaster Recovery Runbook](./DR_RUNBOOK.md)
- [Security Policy](SECURITY.md)
- [API Documentation](api/index.md)

