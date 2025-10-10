# Disaster Recovery Runbook

## Executive Summary

This document defines the disaster recovery (DR) procedures for Flowstate-AI, ensuring business continuity and data protection in the event of system failures, data loss, or catastrophic events.

**Recovery Time Objective (RTO)**: 4 hours  
**Recovery Point Objective (RPO)**: 1 hour  
**Last Updated**: 2025-01-10  
**Version**: 2.0

## Disaster Scenarios

### Scenario 1: Database Failure

**Impact**: Complete loss of database service  
**Probability**: Low  
**RTO**: 2 hours  
**RPO**: 15 minutes

**Recovery Procedure**:

1. **Assess the Situation** (5 minutes)
   - Verify database is truly down (not network issue)
   - Check monitoring dashboards (Grafana)
   - Review error logs in Loki
   - Determine root cause if possible

2. **Activate Standby Database** (15 minutes)
   - If using PostgreSQL replication, promote standby to primary
   - Update application configuration to point to new primary
   - Restart application services
   - Verify connectivity

3. **Restore from Backup** (if no standby, 1-2 hours)
   - Identify latest valid backup
   - Provision new database instance
   - Restore backup using automated scripts
   - Verify data integrity
   - Update application configuration
   - Restart services

4. **Verify Recovery** (30 minutes)
   - Run health checks
   - Test critical user workflows
   - Verify data consistency
   - Monitor for errors

5. **Post-Recovery** (ongoing)
   - Document incident
   - Analyze root cause
   - Update procedures if needed
   - Schedule post-mortem

**Commands**:
```bash
# Check database status
pg_isready -h $DB_HOST -p 5432

# Restore from latest backup
./scripts/restore-database.sh --backup latest --target production

# Verify restoration
psql $DATABASE_URL -c "SELECT COUNT(*) FROM users;"

# Restart services
systemctl restart flowstate-backend
```

### Scenario 2: Application Server Failure

**Impact**: Service unavailable for users  
**Probability**: Medium  
**RTO**: 30 minutes  
**RPO**: 0 (no data loss)

**Recovery Procedure**:

1. **Detect Failure** (immediate)
   - Monitoring alerts trigger
   - Health checks fail
   - Users report issues

2. **Failover to Backup Server** (5 minutes)
   - Load balancer automatically routes to healthy servers
   - If manual: update DNS or load balancer configuration
   - Verify failover successful

3. **Investigate Primary Server** (15 minutes)
   - Check system logs
   - Review resource usage
   - Identify root cause

4. **Restore Primary Server** (10 minutes)
   - Fix identified issue
   - Restart services
   - Run health checks
   - Return to load balancer pool

**Commands**:
```bash
# Check server health
curl -f https://api.flowstate-ai.com/health || echo "Server down"

# Restart application
systemctl restart flowstate-backend

# Check logs
journalctl -u flowstate-backend -n 100 --no-pager

# Verify recovery
curl https://api.flowstate-ai.com/health
```

### Scenario 3: Complete Data Center Outage

**Impact**: All services unavailable  
**Probability**: Very Low  
**RTO**: 4 hours  
**RPO**: 1 hour

**Recovery Procedure**:

1. **Activate DR Site** (30 minutes)
   - Spin up infrastructure in secondary region
   - Deploy application from container registry
   - Restore database from off-site backup
   - Configure networking and DNS

2. **Restore Data** (2 hours)
   - Identify latest off-site backup
   - Restore database
   - Restore file storage
   - Verify data integrity

3. **Update DNS** (15 minutes, plus propagation)
   - Update DNS records to point to DR site
   - Wait for propagation (up to 1 hour)
   - Monitor traffic shift

4. **Verify Services** (1 hour)
   - Test all critical workflows
   - Verify integrations
   - Monitor for errors
   - Communicate status to users

5. **Maintain DR Site** (ongoing)
   - Monitor performance
   - Plan primary site recovery
   - Document lessons learned

**Commands**:
```bash
# Deploy to DR region
./scripts/deploy-dr-site.sh --region us-west-2

# Restore database
./scripts/restore-database.sh --backup latest --target dr-site

# Update DNS
./scripts/update-dns.sh --target dr-site

# Verify deployment
./scripts/health-check.sh --environment dr
```

### Scenario 4: Data Corruption

**Impact**: Incorrect or corrupted data  
**Probability**: Low  
**RTO**: 2 hours  
**RPO**: Up to 24 hours (depending on detection)

**Recovery Procedure**:

1. **Identify Corruption** (varies)
   - User reports
   - Data validation checks
   - Monitoring alerts

2. **Assess Scope** (30 minutes)
   - Determine affected tables/records
   - Identify time of corruption
   - Estimate impact on users

3. **Isolate System** (15 minutes)
   - Enable maintenance mode
   - Prevent further writes
   - Communicate to users

4. **Restore Clean Data** (1 hour)
   - Identify last known good backup
   - Restore affected tables
   - Verify data integrity
   - Replay transactions if possible

5. **Resume Operations** (15 minutes)
   - Disable maintenance mode
   - Monitor for issues
   - Communicate resolution

**Commands**:
```bash
# Enable maintenance mode
./scripts/maintenance-mode.sh --enable

# Restore specific table
./scripts/restore-table.sh --table users --timestamp "2025-01-10 10:00:00"

# Verify restoration
psql $DATABASE_URL -c "SELECT COUNT(*) FROM users WHERE updated_at > '2025-01-10 10:00:00';"

# Disable maintenance mode
./scripts/maintenance-mode.sh --disable
```

### Scenario 5: Security Breach

**Impact**: Unauthorized access, data exposure  
**Probability**: Low  
**RTO**: Immediate containment, 8 hours full recovery  
**RPO**: Varies

**Recovery Procedure**:

1. **Contain Breach** (immediate)
   - Isolate affected systems
   - Revoke compromised credentials
   - Block malicious IPs
   - Enable enhanced monitoring

2. **Assess Damage** (2 hours)
   - Review access logs
   - Identify compromised data
   - Determine attack vector
   - Notify security team

3. **Eradicate Threat** (2 hours)
   - Patch vulnerabilities
   - Remove malware/backdoors
   - Reset all credentials
   - Update security rules

4. **Recover Systems** (3 hours)
   - Restore from clean backups
   - Rebuild compromised servers
   - Verify no persistence mechanisms
   - Restore services gradually

5. **Post-Incident** (ongoing)
   - Notify affected users
   - Report to authorities if required
   - Conduct forensic analysis
   - Implement additional security measures

**Commands**:
```bash
# Block malicious IP
iptables -A INPUT -s <malicious-ip> -j DROP

# Revoke all sessions
./scripts/revoke-all-sessions.sh

# Audit access logs
./scripts/audit-logs.sh --since "2025-01-10" --suspicious

# Restore from clean backup
./scripts/restore-clean-state.sh --date "2025-01-09"
```

## Backup Strategy

### Database Backups

**Frequency**: 
- Full backup: Daily at 2 AM UTC
- Incremental backup: Every 6 hours
- Transaction logs: Continuous

**Retention**:
- Daily backups: 30 days
- Weekly backups: 90 days
- Monthly backups: 1 year

**Storage**:
- Primary: AWS S3 or GitHub Actions artifacts
- Secondary: Cross-region replication
- Tertiary: Long-term archival storage

**Verification**:
- Automated restore test: Weekly
- Manual verification: Monthly
- Integrity checks: Daily

### Application Backups

**Configuration Files**:
- Stored in Git repository
- Tagged with each release
- Backed up daily

**User-Uploaded Files**:
- Stored with versioning enabled
- Cross-region replication
- Lifecycle policies applied

**Container Images**:
- Stored in GitHub Container Registry
- Tagged with version and commit SHA
- Retained for all production releases

## Recovery Procedures

### Database Restoration

```bash
#!/bin/bash
# Restore database from backup

BACKUP_FILE=$1
TARGET_DB=$2

# Download backup
# Restore to target database
# Verify restoration
# Clean up

echo "Database restored to $TARGET_DB"
```

### Application Restoration

```bash
#!/bin/bash
# Deploy application from backup version

VERSION=$1

# Pull container image
# Deploy to production
# Wait for rollout
# Verify deployment

echo "Application restored to version $VERSION"
```

## Testing and Validation

### DR Testing Schedule

**Monthly**: Backup restoration test  
**Quarterly**: Failover to standby database  
**Annually**: Full DR site activation

### Test Procedures

**Backup Restoration Test** (Monthly):
1. Select random backup from past week
2. Restore to test environment
3. Verify data integrity
4. Run automated tests
5. Document results

**Failover Test** (Quarterly):
1. Schedule maintenance window
2. Promote standby to primary
3. Update application configuration
4. Verify functionality
5. Failback to original primary
6. Document results

**Full DR Test** (Annually):
1. Schedule extended maintenance window
2. Activate DR site
3. Restore all data
4. Update DNS
5. Test all functionality
6. Maintain DR site for 24 hours
7. Failback to primary site
8. Document results and lessons learned

## Communication Plan

### Internal Communication

**Incident Detection**:
- Automated alerts to on-call engineer
- Team notification via Slack/email
- Leadership briefing

**During Recovery**:
- Status updates every 30 minutes
- Stakeholder briefing every hour
- Executive summary for leadership

**Post-Recovery**:
- Incident report within 24 hours
- Post-mortem meeting within 1 week
- Updated procedures within 2 weeks

### External Communication

**User Notification**:
- Status page update
- Email to affected users
- Social media updates
- In-app notifications

**Message Templates**:

**Initial Notification**:
```
We are currently experiencing technical difficulties with Flowstate-AI. 
Our team is actively working to resolve the issue. We will provide 
updates every hour until service is restored.
```

**Progress Update**:
```
Update: We have identified the issue and are implementing a fix. 
We expect service to be restored within [X] hours. Thank you for 
your patience.
```

**Resolution**:
```
Service has been restored. All systems are operating normally. 
We apologize for the inconvenience. A detailed incident report 
will be published within 24 hours.
```

## Roles and Responsibilities

### Incident Commander
- Overall responsibility for recovery
- Coordinates all recovery activities
- Makes final decisions
- Communicates with stakeholders

### Technical Lead
- Executes recovery procedures
- Troubleshoots technical issues
- Coordinates with infrastructure team
- Provides technical updates

### Communications Lead
- Manages internal communications
- Drafts user notifications
- Updates status page
- Coordinates with PR team

### On-Call Engineer
- First responder
- Initial assessment
- Escalates if needed
- Documents incident

## Contact Information

**On-Call Rotation**: See on-call schedule  
**Incident Commander**: [Primary], [Backup]  
**Technical Lead**: [Primary], [Backup]  
**Communications Lead**: [Primary], [Backup]

**Escalation**:
- Level 1: On-call engineer
- Level 2: Technical lead
- Level 3: Engineering manager
- Level 4: CTO

**External Contacts**:
- Cloud Provider Support
- Database Vendor Support
- Security Team: security@flowstate-ai.com

## Post-Incident Procedures

### Incident Report

Document within 24 hours:
- Timeline of events
- Root cause analysis
- Impact assessment
- Recovery actions taken
- Lessons learned

### Post-Mortem Meeting

Schedule within 1 week:
- Review incident report
- Discuss what went well
- Identify improvements
- Assign action items
- Update procedures

### Follow-Up Actions

Complete within 2 weeks:
- Implement preventive measures
- Update documentation
- Improve monitoring
- Enhance automation
- Train team on new procedures

## Appendix

### Checklist: Database Failure Recovery

- [ ] Verify database is down
- [ ] Check monitoring dashboards
- [ ] Review error logs
- [ ] Activate standby or restore from backup
- [ ] Update application configuration
- [ ] Restart services
- [ ] Run health checks
- [ ] Test critical workflows
- [ ] Verify data consistency
- [ ] Document incident
- [ ] Schedule post-mortem

### Checklist: Full DR Site Activation

- [ ] Declare disaster
- [ ] Notify team and stakeholders
- [ ] Provision infrastructure in DR region
- [ ] Deploy applications
- [ ] Restore database
- [ ] Restore file storage
- [ ] Configure networking
- [ ] Update DNS records
- [ ] Wait for DNS propagation
- [ ] Test all services
- [ ] Monitor traffic shift
- [ ] Communicate to users
- [ ] Document recovery process

---

**Document Owner**: Engineering Team  
**Review Frequency**: Quarterly  
**Next Review**: 2025-04-10  
**Test Schedule**: Quarterly DR drills

