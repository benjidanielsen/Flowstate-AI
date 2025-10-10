# Disaster Recovery Runbook

**Version:** 1.0  
**Last Updated:** 2025-10-10

## Purpose

This runbook defines disaster recovery procedures for Flowstate-AI.

## Recovery Time Objectives

- **RTO (Recovery Time Objective):** 4 hours
- **RPO (Recovery Point Objective):** 24 hours

## Disaster Scenarios

### Database Failure

1. Identify most recent backup
2. Provision new database instance
3. Restore from backup
4. Update connection strings
5. Verify data integrity
6. Resume operations

### Complete System Failure

1. Provision new infrastructure
2. Deploy from last known good release
3. Restore database from backup
4. Verify all services operational
5. Resume operations

## Backup Locations

- **Database Backups:** GitHub Actions artifacts (30-day retention)
- **Configuration:** Git repository
- **Docker Images:** GitHub Container Registry

## Contact

- **Emergency Contact:** [24/7 Contact]
- **System Owner:** [Contact]

---

**Test Schedule:** Quarterly DR drills
