# Flowstate-AI System Architecture

**Version**: 1.1.0  
**Last Updated**: 2025-10-10  
**Status**: Production

## Overview

Flowstate-AI is an AI-first, self-improving CRM-OS designed for network marketers and solo founders. The system architecture follows a microservices pattern with containerized components, comprehensive observability, and production-ready security practices.

## Architecture Principles

The Flowstate-AI architecture is guided by several core principles that ensure scalability, maintainability, and reliability. The system embraces a **modular design** where each component has a single, well-defined responsibility and communicates through standard interfaces. This modularity enables independent development, testing, and deployment of services.

**Security by design** is fundamental to the architecture. All services run as non-root users in containers, communication between services is encrypted, secrets are managed through secure vaults, and the principle of least privilege is enforced throughout. Regular security scanning and vulnerability management ensure ongoing protection.

The architecture is designed for **scalability**, with stateless services that can scale horizontally, database connection pooling and query optimization, caching strategies to reduce database load, and asynchronous processing for long-running tasks. This enables the system to grow with user demand.

**Observability** is built into every layer, providing comprehensive metrics collection with Prometheus, distributed tracing with Jaeger, centralized logging with Loki, and health checks for all services. This visibility enables rapid problem diagnosis and resolution.

## System Components

### Frontend (React/Vite)

The frontend is a modern single-page application built with React and Vite, served through nginx in production. The architecture provides a responsive user interface with real-time updates, state management using React Context and hooks, and API communication through Axios with interceptors for authentication and error handling.

The frontend implements **progressive enhancement** to ensure core functionality works even with JavaScript disabled or on slower connections. The build process uses Vite for fast development and optimized production builds with code splitting and lazy loading.

**Security features** include Content Security Policy headers, XSS protection, CSRF token validation, and secure cookie handling. The nginx configuration provides gzip compression, static asset caching, and security headers.

### Backend (Node.js/TypeScript)

The backend is built with Node.js and TypeScript, providing a robust API layer with type safety and modern JavaScript features. The architecture follows a **layered pattern** with clear separation between routes, controllers, services, and data access layers.

**Key features** include RESTful API design with consistent endpoint structure, JWT-based authentication and authorization, input validation and sanitization, comprehensive error handling with proper HTTP status codes, and rate limiting to prevent abuse.

The backend uses **dependency injection** for better testability and maintainability. Services are loosely coupled and can be easily mocked for testing. The TypeScript compiler provides compile-time type checking to catch errors early.

**Database access** is managed through a data access layer that provides connection pooling, query optimization, and transaction management. The backend supports both PostgreSQL for relational data and Redis for caching and session management.

### Python Worker (FastAPI)

The Python worker handles AI processing and machine learning tasks using FastAPI for high-performance async operations. This component provides **AI capabilities** including natural language processing, sentiment analysis, recommendation engines, and predictive analytics.

The worker architecture uses **asynchronous processing** with Celery for task queuing, Redis as a message broker, and worker processes that can scale independently. This enables long-running AI tasks to execute without blocking the main application.

**Model management** includes versioned model storage, A/B testing capabilities, model performance monitoring, and automatic fallback to previous versions if performance degrades. Models are loaded on worker startup and cached in memory for fast inference.

### Database Layer

#### PostgreSQL

PostgreSQL serves as the primary relational database, storing user data, CRM records, and transactional information. The database architecture includes **normalized schemas** for data integrity, **indexes** for query performance, **foreign key constraints** for referential integrity, and **triggers** for audit logging.

**High availability** is achieved through streaming replication with a primary and standby server, automatic failover with pg_auto_failover or Patroni, and regular backups with point-in-time recovery capability.

**Performance optimization** includes connection pooling through PgBouncer, query optimization with EXPLAIN ANALYZE, partitioning for large tables, and vacuum and analyze scheduling for maintenance.

#### Redis

Redis provides caching and session management with **in-memory storage** for fast access. The architecture uses Redis for session storage, API response caching, rate limiting counters, and pub/sub for real-time features.

**Data persistence** is configured with AOF (Append-Only File) for durability and RDB snapshots for backup. The maxmemory policy is set to allkeys-lru to automatically evict least recently used keys when memory is full.

## Communication Patterns

### Synchronous Communication

Synchronous communication between services uses **HTTP/REST** with JSON payloads. The backend exposes RESTful endpoints that the frontend consumes, while the python-worker provides API endpoints for AI processing.

**API versioning** is implemented through URL paths (e.g., /api/index.mdv1/) to enable backward compatibility. Each API response includes standard fields for status, data, and error messages.

**Authentication** uses JWT tokens passed in Authorization headers. Tokens are short-lived (15 minutes) with refresh tokens for extended sessions. The backend validates tokens on every request and enforces role-based access control.

### Asynchronous Communication

Asynchronous communication uses **message queues** for decoupling services and handling long-running tasks. Celery workers consume tasks from Redis queues and execute them asynchronously.

**Task patterns** include fire-and-forget for non-critical tasks, request-reply for tasks that need results, and pub-sub for event broadcasting. Tasks are idempotent to handle retries safely.

**Error handling** includes automatic retries with exponential backoff, dead letter queues for failed tasks, and alerting for critical failures. Task status is tracked in the database for monitoring.

## Data Flow

### User Request Flow

A typical user request follows this path through the system. The user interacts with the React frontend, which sends an HTTP request to the backend API. The backend validates the JWT token and checks permissions before processing the request through the appropriate service layer. Services interact with the database or cache as needed, and the response is returned through the same path with appropriate status codes and data.

For AI-powered features, the backend may queue a task to the python-worker and return immediately with a task ID. The frontend can poll for task completion or receive updates through WebSocket connections.

### Data Persistence Flow

Data persistence follows a structured pattern to ensure consistency and durability. User actions trigger API calls to the backend, which validates input and enforces business rules. The service layer transforms data into database models and executes transactions with proper error handling. Database triggers log changes to audit tables for compliance and debugging.

**Caching strategy** includes cache-aside pattern where the application checks cache first, reads from database on cache miss, and updates cache with the result. Cache invalidation occurs on data updates to prevent stale data.

## Security Architecture

### Authentication and Authorization

The system implements **multi-layered security** starting with authentication. Users authenticate with email and password, receiving a JWT access token and refresh token. The access token is short-lived (15 minutes) and contains user ID and roles. The refresh token is long-lived (7 days) and stored securely in HTTP-only cookies.

**Authorization** uses role-based access control (RBAC) with roles defined in the database. Each API endpoint specifies required roles, and the backend middleware validates tokens and checks permissions before allowing access.

### Network Security

Network security is enforced at multiple levels. All external communication uses HTTPS with TLS 1.3, internal service communication occurs on a private Docker network, and the database is not exposed to the public internet. Firewall rules restrict access to only necessary ports.

**API security** includes rate limiting to prevent abuse, input validation to prevent injection attacks, output encoding to prevent XSS, and CORS configuration to restrict allowed origins.

### Data Security

Data security protects sensitive information at rest and in transit. Passwords are hashed with bcrypt (cost factor 12), sensitive data is encrypted in the database using application-level encryption, and database backups are encrypted before storage. API keys and secrets are stored in environment variables or secret management systems, never in code.

## Observability Stack

### Metrics (Prometheus)

Prometheus collects metrics from all services through /metrics endpoints. **System metrics** include CPU usage, memory usage, disk I/O, and network traffic. **Application metrics** track request rates, error rates, response times, and active connections. **Business metrics** monitor user signups, API usage, and feature adoption.

Metrics are stored in Prometheus with configurable retention periods. Grafana provides visualization through dashboards for different audiences including operations, development, and business stakeholders.

### Logging (Loki)

Loki provides centralized logging with efficient storage and querying. All services send structured logs in JSON format with standard fields including timestamp, level, service, and message. **Log levels** follow standard conventions: ERROR for failures, WARN for potential issues, INFO for significant events, and DEBUG for detailed troubleshooting.

Logs are retained for 30 days in Loki and archived to object storage for compliance. Log aggregation enables correlation across services using request IDs.

### Tracing (Jaeger)

Jaeger provides distributed tracing to understand request flow across services. Each request generates a trace with spans for each service interaction. **Trace data** includes service name, operation name, start time and duration, tags for metadata, and logs for events within spans.

Sampling is configured to balance observability with performance impact. Critical paths are always traced while routine operations are sampled at lower rates.

## Deployment Architecture

### Container Orchestration

Services are containerized using Docker with multi-stage builds for optimization. **Container features** include non-root user execution, health checks for automatic recovery, resource limits to prevent resource exhaustion, and security scanning in CI/CD pipelines.

The docker-compose configuration defines service dependencies, networking, and volumes. For production, Kubernetes can be used for advanced orchestration with features like auto-scaling, rolling updates, and self-healing.

### CI/CD Pipeline

The CI/CD pipeline automates testing and deployment with multiple stages. **Build stage** checks out code, runs linters and type checkers, executes unit tests, and builds Docker images. **Security stage** scans for vulnerabilities, checks for secrets in code, and validates dependencies. **Deploy stage** pushes images to registry, updates deployment configuration, and performs health checks.

Deployments follow blue-green or canary patterns to minimize downtime and risk. Rollback procedures are automated and tested regularly.

### Infrastructure

Infrastructure is managed as code using tools like Terraform or CloudFormation. **Production environment** includes load balancers for traffic distribution, auto-scaling groups for compute resources, managed databases with automatic backups, and CDN for static asset delivery.

**Disaster recovery** capabilities include regular database backups with point-in-time recovery, infrastructure as code for rapid rebuilding, documented runbooks for common scenarios, and tested recovery procedures with defined RTO and RPO.

## Scalability Considerations

### Horizontal Scaling

Services are designed for horizontal scaling with stateless application servers that can be added or removed dynamically. **Load balancing** distributes traffic across instances using round-robin or least-connections algorithms. Session data is stored in Redis rather than application memory to enable any server to handle any request.

**Database scaling** uses read replicas for query load distribution, connection pooling to maximize connection reuse, and query optimization to reduce database load. For extreme scale, sharding can partition data across multiple database instances.

### Vertical Scaling

Vertical scaling provides additional resources to existing instances. **Resource tuning** includes adjusting Node.js heap size, configuring database memory buffers, optimizing Redis maxmemory, and tuning worker process counts.

**Performance monitoring** identifies bottlenecks and guides scaling decisions. Metrics track resource utilization and application performance to determine whether horizontal or vertical scaling is more appropriate.

### Caching Strategy

Caching reduces load on backend systems and improves response times. **Multi-level caching** includes browser caching for static assets, CDN caching for public content, Redis caching for API responses, and database query result caching.

**Cache invalidation** uses time-to-live (TTL) for automatic expiration and event-based invalidation for immediate updates. Cache warming preloads frequently accessed data during deployment.

## Future Architecture Evolution

The architecture is designed to evolve with the system's needs. **Planned enhancements** include migrating to Kubernetes for advanced orchestration, implementing service mesh for advanced networking, adding GraphQL for flexible API queries, and introducing event sourcing for audit and replay capabilities.

**AI evolution** will expand machine learning capabilities, add real-time model training, implement federated learning for privacy, and develop self-improving algorithms that learn from system behavior.

## References

- [Deployment Guide](DEPLOYMENT_GUIDE.md)
- [Operations Runbook](OPS_RUNBOOK.md)
- [Architecture Decision Records](adr/index.md)
- [API Documentation](api/index.md)

---

**Document Owner**: Architecture Team  
**Review Cycle**: Quarterly  
**Next Review**: 2026-01-10

