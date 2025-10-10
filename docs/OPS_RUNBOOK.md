# Operations Runbook

**Version:** 1.0  
**Last Updated:** 2025-10-10

## Purpose

This runbook provides operational procedures for managing Flowstate-AI in production environments.

## Daily Operations

### Health Checks

Monitor system health via GODMODE dashboard and verify all services are running, check database connectivity, review error logs for anomalies, and confirm backup completion.

### Monitoring

Key metrics to monitor include API response times (target: <200ms p95), database query performance (target: <100ms p95), reminder processing queue depth (target: <100 pending), NBA calculation latency (target: <500ms), and active user sessions.

## Common Procedures

### Service Restart

```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart backend
docker-compose restart python-worker
docker-compose restart godmode-dashboard
```

### Log Access

```bash
# View backend logs
docker-compose logs -f backend

# View Python worker logs
docker-compose logs -f python-worker

# View all logs
docker-compose logs -f
```

### Database Backup

```bash
# Manual backup
docker-compose exec db pg_dump -U flowstate flowstate_db > backup_$(date +%Y%m%d_%H%M%S).sql
```

## Incident Response

For incidents, follow these steps: assess severity using the incident severity matrix, activate appropriate response team, follow incident-specific procedures below, document in incident log, and conduct post-incident review.

## Contact Information

- **On-Call Engineer:** [Contact]
- **System Owner:** [Contact]
- **Database Administrator:** [Contact]

---

**Maintained By:** Operations Team
