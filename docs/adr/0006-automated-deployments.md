# ADR 0006: Automated Deployment Workflows

**Date**: 2025-10-10  
**Status**: Accepted  
**Context**: Phase E - Deployments  
**Decision Makers**: MAIN MANUS, ARCHITECT, DevOps Team

## Context and Problem Statement

Flowstate-AI requires reliable, repeatable, and safe deployment processes for both staging and production environments. Manual deployments are error-prone, time-consuming, and lack consistency. We need automated deployment workflows that ensure zero-downtime deployments, comprehensive health checks, automatic rollback capabilities, and clear audit trails.

## Decision Drivers

* **Reliability**: Deployments must be consistent and predictable
* **Safety**: Zero-downtime deployments with automatic rollback on failure
* **Speed**: Reduce deployment time from hours to minutes
* **Auditability**: Clear records of what was deployed, when, and by whom
* **Scalability**: Support multiple environments (staging, production)
* **Security**: Secure handling of credentials and sensitive data
* **Observability**: Comprehensive monitoring and health checks

## Considered Options

### 1. GitHub Actions with SSH Deployment
**Pros:**
- Native GitHub integration
- Free for public repositories
- Mature ecosystem of actions
- Built-in secrets management
- Easy to version control workflows

**Cons:**
- Requires SSH access to servers
- Limited to GitHub ecosystem
- Potential vendor lock-in

### 2. GitLab CI/CD
**Pros:**
- Integrated with GitLab
- Built-in container registry
- Kubernetes integration
- Self-hosted option available

**Cons:**
- Requires migration from GitHub
- Additional infrastructure for self-hosted
- Learning curve for team

### 3. Jenkins
**Pros:**
- Highly customizable
- Large plugin ecosystem
- Self-hosted control

**Cons:**
- Requires dedicated infrastructure
- Complex setup and maintenance
- Steeper learning curve

### 4. ArgoCD / Flux (GitOps)
**Pros:**
- Declarative deployments
- Automatic sync from Git
- Kubernetes-native

**Cons:**
- Requires Kubernetes
- More complex infrastructure
- Overkill for current scale

## Decision Outcome

**Chosen option**: **GitHub Actions with SSH Deployment**

We chose GitHub Actions because:
1. **Native Integration**: Already using GitHub for source control
2. **Cost-Effective**: Free for public repositories, minimal cost for private
3. **Simplicity**: Straightforward workflow definition and execution
4. **Ecosystem**: Rich marketplace of pre-built actions
5. **Security**: Built-in secrets management and OIDC support
6. **Flexibility**: Can evolve to more complex solutions as needed

## Implementation Details

### Deployment Strategy

**Staging Environment:**
- **Strategy**: Rolling update
- **Trigger**: Automatic on push to `develop` branch
- **Downtime**: Minimal (< 30 seconds)
- **Rollback**: Automatic on failure

**Production Environment:**
- **Strategy**: Blue-green deployment
- **Trigger**: Manual via release or workflow dispatch
- **Downtime**: Zero downtime
- **Rollback**: Automatic on failure with database backup restoration

### Workflow Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   GitHub Actions                         │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐      ┌──────────────┐                │
│  │   Staging    │      │  Production  │                │
│  │  Deployment  │      │  Deployment  │                │
│  └──────────────┘      └──────────────┘                │
│         │                      │                         │
│         ├──────────────────────┤                         │
│         │                      │                         │
│    ┌────▼────┐            ┌───▼────┐                   │
│    │  Build  │            │ Pre-   │                   │
│    │ Images  │            │ checks │                   │
│    └────┬────┘            └───┬────┘                   │
│         │                      │                         │
│    ┌────▼────┐            ┌───▼────┐                   │
│    │  Push   │            │ Backup │                   │
│    │  GHCR   │            │  DB    │                   │
│    └────┬────┘            └───┬────┘                   │
│         │                      │                         │
│    ┌────▼────┐            ┌───▼────┐                   │
│    │ Deploy  │            │ Deploy │                   │
│    │   SSH   │            │ Green  │                   │
│    └────┬────┘            └───┬────┘                   │
│         │                      │                         │
│    ┌────▼────┐            ┌───▼────┐                   │
│    │ Health  │            │ Health │                   │
│    │ Checks  │            │ Checks │                   │
│    └────┬────┘            └───┬────┘                   │
│         │                      │                         │
│    ┌────▼────┐            ┌───▼────┐                   │
│    │  Smoke  │            │ Switch │                   │
│    │  Tests  │            │Traffic │                   │
│    └─────────┘            └───┬────┘                   │
│                                │                         │
│                           ┌────▼────┐                   │
│                           │  Post-  │                   │
│                           │  Tasks  │                   │
│                           └─────────┘                   │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Health Check Strategy

**Multi-Level Health Checks:**
1. **Container Level**: Docker health checks
2. **Application Level**: HTTP health endpoints
3. **Database Level**: Database connectivity checks
4. **Integration Level**: Critical API endpoint tests
5. **Business Logic Level**: Smoke tests for key workflows

**Health Check Endpoints:**
- `/health` - Basic health status
- `/health/db` - Database connectivity
- `/health/errors` - Error rate monitoring
- `/api/v1/health` - API health
- `/api/v1/auth/status` - Authentication service
- `/api/v1/stats` - Database query functionality

### Rollback Mechanisms

**Automatic Rollback Triggers:**
- Health check failures
- Smoke test failures
- High error rates (> 10 errors in 5 minutes)
- Database connectivity issues
- Critical service unavailability

**Rollback Process:**
1. Stop failed deployment
2. Restore database from backup (production only)
3. Revert to previous container versions
4. Verify health of rolled-back system
5. Notify team of rollback
6. Create incident report

### Security Measures

**Secrets Management:**
- SSH keys stored in GitHub Secrets
- Database credentials in environment variables
- API keys rotated regularly
- No secrets in code or logs

**Access Control:**
- SSH key-based authentication only
- Principle of least privilege
- Separate keys for staging and production
- Regular key rotation

**Audit Trail:**
- All deployments logged in GitHub Actions
- Deployment records in AUDIT_TRAIL.md
- Who deployed, what version, when
- Success/failure status

### Monitoring and Observability

**Deployment Metrics:**
- Deployment frequency
- Deployment success rate
- Mean time to deploy (MTTD)
- Mean time to recovery (MTTR)
- Rollback frequency

**Health Monitoring:**
- Continuous health checks post-deployment
- Error rate monitoring
- Response time tracking
- Resource utilization monitoring

**Alerting:**
- Deployment failures
- Health check failures
- High error rates
- Resource exhaustion
- Security incidents

## Consequences

### Positive

* **Increased Deployment Frequency**: From weekly to daily (or on-demand)
* **Reduced Deployment Time**: From 2-3 hours to 10-15 minutes
* **Improved Reliability**: Automated processes reduce human error
* **Zero Downtime**: Blue-green deployment eliminates production downtime
* **Faster Rollback**: Automatic rollback in < 5 minutes
* **Better Auditability**: Complete deployment history in GitHub
* **Enhanced Security**: Centralized secrets management
* **Improved Confidence**: Comprehensive health checks and smoke tests

### Negative

* **Initial Setup Complexity**: Requires SSH configuration and secret management
* **GitHub Dependency**: Tied to GitHub Actions availability
* **SSH Overhead**: Requires maintaining SSH access to servers
* **Learning Curve**: Team needs to understand GitHub Actions workflows
* **Monitoring Overhead**: Requires active monitoring of deployments

### Neutral

* **Infrastructure Requirements**: Servers must support Docker and SSH
* **Maintenance**: Workflows need occasional updates
* **Cost**: Minimal for public repos, scales with usage for private repos

## Compliance and Standards

* **CI/CD Best Practices**: Follows industry-standard CI/CD patterns
* **Security Standards**: Implements secure deployment practices
* **GitOps Principles**: Infrastructure and deployments as code
* **Observability**: Comprehensive monitoring and logging
* **Disaster Recovery**: Backup and rollback procedures

## Implementation Plan

### Phase 1: Staging Deployment (Week 1)
1. Create staging deployment workflow
2. Configure staging server
3. Set up SSH access and secrets
4. Test deployment process
5. Document procedures

### Phase 2: Production Deployment (Week 2)
1. Create production deployment workflow
2. Configure production servers (blue-green)
3. Set up SSH access and secrets
4. Implement backup procedures
5. Test deployment and rollback
6. Document procedures

### Phase 3: Monitoring and Optimization (Week 3)
1. Set up deployment monitoring
2. Configure alerting
3. Optimize deployment speed
4. Refine health checks
5. Train team on procedures

## Alternatives Considered But Rejected

### Kubernetes with Helm
**Reason for Rejection**: Overkill for current scale. Adds significant complexity without proportional benefits at this stage. Can be revisited when scaling requirements increase.

### Manual Deployments with Scripts
**Reason for Rejection**: Error-prone, not auditable, lacks rollback automation, and doesn't scale with team growth.

### Continuous Deployment (CD) to Production
**Reason for Rejection**: Too risky for production without extensive testing. Prefer manual trigger with automated execution for production deployments.

## Related Decisions

* **ADR 0002**: Supply Chain Security - Integrates with image signing and SBOM generation
* **ADR 0003**: Container Optimization - Leverages optimized container images
* **ADR 0004**: Documentation Portal - Deployment procedures documented
* **ADR 0005**: Security Scanning - Pre-deployment security validation

## References

* [GitHub Actions Documentation](https://docs.github.com/en/actions)
* [Blue-Green Deployment Pattern](https://martinfowler.com/bliki/BlueGreenDeployment.html)
* [Deployment Runbook](../DEPLOYMENT_RUNBOOK.md)
* [Operations Runbook](../OPS_RUNBOOK.md)
* [Disaster Recovery Runbook](../DR_RUNBOOK.md)

## Review and Update

* **Next Review Date**: 2026-01-10 (3 months)
* **Review Triggers**: 
  - Deployment failures > 10%
  - Rollback frequency > 5% of deployments
  - Team feedback on process pain points
  - Infrastructure changes (e.g., Kubernetes adoption)
  - Security incidents related to deployments

## Approval

* **Proposed by**: MAIN MANUS
* **Reviewed by**: ARCHITECT, DevOps Team
* **Approved by**: Project Lead
* **Date**: 2025-10-10

