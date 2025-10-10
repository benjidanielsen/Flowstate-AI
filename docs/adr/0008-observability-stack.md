# ADR 0008: Observability Stack

## Status

Accepted

## Context

A production system requires comprehensive observability to understand system behavior, diagnose issues, optimize performance, and ensure reliability. Without proper observability, teams operate blind, unable to detect problems before they impact users or diagnose issues quickly when they occur.

### Current Situation

- Limited visibility into system performance and health
- No centralized metrics collection
- No distributed tracing capabilities
- Logs scattered across containers
- Difficult to correlate events across services
- Reactive rather than proactive problem detection

### Requirements

1. **Metrics**: Collect and visualize system and application metrics
2. **Logs**: Aggregate and search logs from all services
3. **Traces**: Track requests across distributed services
4. **Dashboards**: Visualize system health and performance
5. **Alerting**: Proactive notification of issues
6. **Correlation**: Link metrics, logs, and traces
7. **Retention**: Store data for analysis and compliance
8. **Performance**: Minimal overhead on application performance

## Decision

We will implement a comprehensive observability stack using the **Prometheus + Grafana + Loki + Jaeger** combination, commonly known as the PLG stack with tracing.

### Components

#### 1. Prometheus - Metrics Collection

**Purpose**: Time-series metrics collection and alerting

**Why Prometheus**:
- Industry standard for metrics in cloud-native applications
- Pull-based model reduces application complexity
- Powerful query language (PromQL)
- Built-in alerting capabilities
- Excellent Kubernetes integration
- Large ecosystem of exporters
- Efficient storage format

**Alternatives Considered**:
- **InfluxDB**: Push-based, more complex setup, less ecosystem
- **Datadog**: SaaS, expensive, vendor lock-in
- **New Relic**: SaaS, expensive, less flexibility
- **CloudWatch**: AWS-specific, limited query capabilities

**Configuration**:
- 15-second scrape interval
- Alert rules for common issues
- Exporters for system, container, and database metrics
- 31-day retention period

#### 2. Grafana - Visualization

**Purpose**: Dashboards and visualization for all observability data

**Why Grafana**:
- Best-in-class visualization capabilities
- Supports multiple data sources (Prometheus, Loki, Jaeger)
- Rich dashboard ecosystem
- Alerting capabilities
- Free and open-source
- Active community and development

**Alternatives Considered**:
- **Kibana**: Elasticsearch-focused, less flexible
- **Chronograf**: InfluxDB-specific
- **Datadog**: SaaS, expensive
- **Prometheus UI**: Limited visualization capabilities

**Configuration**:
- Pre-configured dashboards for system and application metrics
- Datasource provisioning for Prometheus, Loki, and Jaeger
- Alert rules and notification channels
- Role-based access control

#### 3. Loki - Log Aggregation

**Purpose**: Centralized log collection and querying

**Why Loki**:
- Designed to work seamlessly with Grafana
- Cost-effective (indexes only metadata, not full text)
- LogQL query language similar to PromQL
- Efficient storage
- Easy to operate
- Native Grafana integration

**Alternatives Considered**:
- **Elasticsearch**: More powerful but complex and resource-intensive
- **Splunk**: Expensive, enterprise-focused
- **CloudWatch Logs**: AWS-specific, limited query capabilities
- **Fluentd + Elasticsearch**: More complex setup

**Configuration**:
- Promtail for log shipping from containers and system
- 31-day retention period
- Automatic log parsing and labeling
- Integration with Jaeger for trace correlation

#### 4. Jaeger - Distributed Tracing

**Purpose**: Track requests across microservices

**Why Jaeger**:
- CNCF graduated project
- OpenTelemetry compatible
- Excellent performance
- Easy to deploy (all-in-one mode)
- Native Grafana integration
- Supports multiple storage backends

**Alternatives Considered**:
- **Zipkin**: Older, less active development
- **Datadog APM**: SaaS, expensive
- **New Relic**: SaaS, expensive
- **AWS X-Ray**: AWS-specific

**Configuration**:
- All-in-one deployment for simplicity
- OpenTelemetry protocol support
- Zipkin compatibility for legacy clients
- Integration with Loki for log correlation

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Observability Stack                     │
└─────────────────────────────────────────────────────────┘

Application Services
    │
    ├─ Metrics ──────────► Prometheus ──┐
    ├─ Logs ─────────────► Promtail ────► Loki ──┐
    └─ Traces ───────────► Jaeger ──────────────┐│
                                                  ││
System & Infrastructure                           ││
    │                                             ││
    ├─ Node Exporter ────► Prometheus ──────────┐││
    ├─ cAdvisor ─────────► Prometheus ──────────┤││
    └─ Postgres Exporter ► Prometheus ──────────┤││
                                                  │││
                                                  ▼▼▼
                                               Grafana
                                                  │
                                                  ▼
                                            Dashboards
                                            Alerts
                                            Queries
```

### Deployment Strategy

**Development**:
- Docker Compose for local development
- All services in single compose file
- Persistent volumes for data retention
- Default credentials for easy access

**Staging**:
- Separate observability stack
- Connected to staging application services
- Same configuration as production
- Used for testing alerts and dashboards

**Production**:
- Dedicated observability infrastructure
- High availability for critical components
- Secure credentials and access control
- Backup and disaster recovery
- Separate network for security

### Integration Points

**Application Instrumentation**:
- Backend: prom-client for Node.js metrics
- Python Worker: prometheus_client for Python metrics
- Frontend: nginx metrics via stub_status
- Custom business metrics for key operations

**Log Format**:
- Structured JSON logging
- Standard fields: timestamp, level, message, trace_id
- Correlation IDs for request tracking
- Sensitive data redaction

**Tracing**:
- OpenTelemetry SDK in all services
- Automatic trace propagation
- Custom spans for key operations
- Trace sampling for high-volume endpoints

## Consequences

### Positive

1. **Comprehensive Visibility**: Full observability across metrics, logs, and traces
2. **Proactive Monitoring**: Alerts catch issues before users are impacted
3. **Fast Diagnosis**: Correlated data enables quick root cause analysis
4. **Performance Insights**: Identify bottlenecks and optimization opportunities
5. **Cost Effective**: Open-source stack with no licensing costs
6. **Scalable**: Can grow with the application
7. **Standard Tools**: Industry-standard tools with large communities
8. **Unified Interface**: Single Grafana interface for all observability data

### Negative

1. **Operational Overhead**: Additional services to maintain and monitor
2. **Learning Curve**: Team must learn PromQL, LogQL, and tracing concepts
3. **Storage Costs**: Metrics, logs, and traces require storage
4. **Resource Usage**: Observability stack consumes CPU, memory, and disk
5. **Configuration Complexity**: Proper setup requires careful configuration

### Neutral

1. **Tool Commitment**: Committed to this observability stack
2. **Instrumentation Required**: Applications must be instrumented
3. **Network Traffic**: Metrics and logs generate network traffic

## Implementation

### Phase 1: Foundation (Complete)
- [x] Docker Compose configuration for all services
- [x] Prometheus configuration with scrape targets
- [x] Loki and Promtail configuration
- [x] Jaeger all-in-one deployment
- [x] Grafana with datasource provisioning

### Phase 2: Instrumentation (Next)
- [ ] Add metrics endpoints to backend
- [ ] Add metrics endpoints to python-worker
- [ ] Implement structured logging
- [ ] Add OpenTelemetry tracing
- [ ] Configure log shipping

### Phase 3: Dashboards (Next)
- [ ] System metrics dashboard
- [ ] Application metrics dashboard
- [ ] Business metrics dashboard
- [ ] Log exploration dashboard
- [ ] Trace analysis dashboard

### Phase 4: Alerting (Next)
- [ ] Define alert rules
- [ ] Configure notification channels
- [ ] Create runbooks for alerts
- [ ] Test alert delivery
- [ ] Establish on-call rotation

### Phase 5: Production Deployment (Next)
- [ ] Deploy observability stack to production
- [ ] Configure high availability
- [ ] Set up backup and retention
- [ ] Implement access control
- [ ] Document operational procedures

## Monitoring and Metrics

Track the following metrics for the observability stack itself:

1. **Prometheus**: Scrape duration, sample ingestion rate, storage usage
2. **Loki**: Ingestion rate, query performance, storage usage
3. **Jaeger**: Trace ingestion rate, storage usage, query performance
4. **Grafana**: Dashboard load time, query performance, user activity

## Retention and Storage

**Metrics (Prometheus)**:
- Retention: 31 days
- Storage: ~1GB per day (estimated)
- Downsampling: Not implemented initially

**Logs (Loki)**:
- Retention: 31 days
- Storage: ~2GB per day (estimated)
- Compression: Enabled

**Traces (Jaeger)**:
- Retention: 7 days
- Storage: ~500MB per day (estimated)
- Sampling: 10% of requests

**Total Estimated Storage**: ~100GB per month

## Security Considerations

1. **Access Control**: Grafana authentication and RBAC
2. **Network Security**: Observability network isolated from public
3. **Data Sensitivity**: PII redaction in logs
4. **Credentials**: Secure storage of database and service credentials
5. **API Security**: Prometheus and Loki APIs protected

## Review and Evolution

This decision will be reviewed:
- After 3 months of production operation
- Quarterly as part of technical review
- When performance or cost issues arise
- When new observability requirements emerge

## References

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Loki Documentation](https://grafana.com/docs/loki/)
- [Jaeger Documentation](https://www.jaegertracing.io/docs/)
- [OpenTelemetry Documentation](https://opentelemetry.io/docs/)

## Related ADRs

- ADR 0001: Phase 0 Baseline Establishment
- ADR 0003: Container Optimization
- ADR 0006: Automated Deployments
- ADR 0007: Database Migrations

## Date

2025-01-10

## Authors

- Manus AI (Implementation)
- Benji Danielsen (Review and Approval)

