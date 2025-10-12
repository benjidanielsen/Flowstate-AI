# Flowstate-AI Operator Guide

**Version:** 1.0
**Last Updated:** 2025-10-12

This guide is intended for system operators and administrators responsible for the day-to-day management and monitoring of the Flowstate-AI system.

## 1. System Overview

The Flowstate-AI system consists of the following core components:

- **Frontend:** The user-facing web application (React).
- **Backend:** The main API and business logic (Node.js).
- **Python Worker:** The AI/ML processing service (Python/FastAPI).
- **PostgreSQL:** The primary database for application data.
- **Redis:** The cache and session storage.
- **Nginx:** The reverse proxy for routing traffic to services.

These components are orchestrated using Docker Compose, as defined in the `docker-compose.production.yml` file.

## 2. Daily Operations

### 2.1. Daily Health Check

At the start of each day, perform a full system health check:

```bash
./scripts/health-check.sh
```

This script will verify the status of all services and their dependencies. Investigate any reported failures immediately.

### 2.2. Monitoring Key Metrics

Monitor the following key metrics to ensure system stability:

- **API Error Rates:** Check the backend logs for an increase in HTTP 5xx errors.
- **CPU and Memory Usage:** Use `docker stats` to monitor resource consumption of all containers.
- **Database Performance:** Monitor for slow queries and high connection counts.
- **AI Worker Queue Length:** (If applicable) Monitor the length of the AI processing queue in Redis.

## 3. User Management

User management is currently handled directly in the database. Future versions will include an admin UI.

### 3.1. Creating a New User

To create a new user, connect to the PostgreSQL database and run:

```sql
INSERT INTO users (email, name, role) VALUES (
  'new.user@example.com',
  'New User',
  'user'
);
```

### 3.2. Changing a User's Role

To change a user's role (e.g., to `admin`):

```sql
UPDATE users SET role = 'admin' WHERE email = 'user@example.com';
```

## 4. Backup and Restore

Database backups are critical for disaster recovery.

### 4.1. Manual Backup

To create a manual backup of the PostgreSQL database:

```bash
docker-compose -f docker-compose.production.yml exec -T postgres pg_dump -U flowstate -d flowstate_ai > backup_$(date +%Y%m%d_%H%M%S).sql
```

Securely store this backup file in a separate location.

### 4.2. Restoring from Backup

To restore the database from a backup file:

1.  **Stop the application services:**

    ```bash
    docker-compose -f docker-compose.production.yml stop backend frontend python-worker
    ```

2.  **Restore the database:**

    ```bash
    cat backup.sql | docker-compose -f docker-compose.production.yml exec -T postgres psql -U flowstate -d flowstate_ai
    ```

3.  **Restart the services:**

    ```bash
    docker-compose -f docker-compose.production.yml start backend frontend python-worker
    ```

## 5. Common Troubleshooting Scenarios

-   **High CPU Usage:** Identify the container with high CPU usage using `docker stats`. Check the logs for that container to identify the cause (e.g., infinite loop, inefficient query).
-   **Slow API Response Times:** Check the backend and database logs. This could be due to slow database queries, high server load, or issues with external services.
-   **AI Worker Not Processing Tasks:** Check the worker logs for errors. Ensure it is connected to Redis and the database.

## 6. Emergency Procedures

In the event of a critical system failure, follow these steps:

1.  **Attempt a full system restart:**

    ```bash
    ./scripts/deploy-production.sh
    ```

2.  **If the restart fails, check the logs for each service** to identify the point of failure.
3.  **If the database is corrupted, restore from the latest backup** as described in section 4.2.
4.  **If the issue is with a recent code change, consider rolling back to a previous version.** This is a manual process that involves checking out a previous Git commit and re-deploying.

For all critical incidents, document the timeline, impact, and resolution steps in a post-mortem report.

