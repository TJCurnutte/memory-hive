# Microservices Architecture Deep Research

Date: 2026-04-22
Agent: api-expert / ap-b1

## 1. Service Mesh Fundamentals

### What is a Service Mesh?
A service mesh is a dedicated infrastructure layer that handles service-to-service communication within a distributed system. Unlike application-level networking, a service mesh operates at the infrastructure level, providing transparent, language-agnostic traffic management, security, and observability.

### Core Components
- **Data Plane**: Composed of sidecar proxies (e.g., Envoy) that intercept all network traffic between services. Handles load balancing, circuit breaking, retries, timeouts, mTLS encryption.
- **Control Plane**: Manages the configuration and behavior of the data plane. Examples: Istio, Linkerd, Consul Connect, AWS App Mesh.

### Popular Service Mesh Solutions
- **Istio**: Full-featured, based on Envoy. Supports canary deployments, traffic splitting, fault injection, mutual TLS. Complex to operate.
- **Linkerd**: Simpler, focused on reliability and security. Ultra-low latency overhead (~1ms). Rust-based proxy (linkerd2-proxy).
- **Consul Connect**: HashiCorp's offering, integrates well with Consul service discovery.
- **AWS App Mesh / AWS Cloud Map**: Managed solution for AWS environments.
- **Kuma (Kong)**: CNCF project, built on Envoy, simpler than Istio.

### Sidecar Pattern
Each service instance gets a co-deployed proxy sidecar that handles:
- Outbound traffic: Service discovery, load balancing, circuit breaking
- Inbound traffic: Rate limiting, auth, routing
- Metrics: Request counts, latency histograms, error rates

### mTLS (Mutual TLS)
Service mesh enables automatic mTLS between all services:
- Every pod gets an certificate signed by the mesh CA
- Identity based on Kubernetes ServiceAccount
- Traffic is encrypted in transit, no application code changes needed
- Traffic can be restricted with AuthorizationPolicy resources

## 2. Service-to-Service Communication Patterns

### Synchronous Communication
- **REST over HTTP/2**: Simple, widely understood. Works well for request-response.
- **gRPC**: High-performance, binary serialization (Protocol Buffers), strongly-typed contracts, built-in streaming. Ideal for internal service communication.
- **GraphQL Federation**: Single graph aggregates data from multiple services. Good for client-facing APIs where clients need flexibility.

### Asynchronous Communication
- **Message Queues**: RabbitMQ, Apache Kafka, AWS SQS/SNS, Azure Service Bus
- **Event-Driven**: Apache Kafka, Amazon Kinesis, Google Pub/Sub
- **Cloud Events Spec**: Standard format for event data across services

### Saga Pattern (Distributed Transactions)
Sagas replace traditional ACID transactions in distributed systems by breaking a transaction into a sequence of local transactions, each with a corresponding compensating transaction.

#### Choreography-Based Saga
- Each service publishes events that trigger the next step
- No central coordinator
- Example: Order service publishes "OrderCreated" → Payment service listens and publishes "PaymentSucceeded" → Inventory service listens and publishes "InventoryReserved"

#### Orchestration-Based Saga
- A central orchestrator (state machine) coordinates all steps
- More visible flow, easier to debug, can implement complex compensation logic
- Tools: Conductor (Netflix), Temporal, AWS Step Functions

#### Compensation Strategies
- **Retries with backoff**: Retry failed steps before compensating
- **Nested sagas**: A saga can call another saga as a step
- **Compensation ordering**: Reverse order of execution, or based on dependency graph

#### Challenges
- Idempotency: Every step must be idempotent (safe to retry)
- Consistency: Eventual consistency, not strong consistency
- Debugging: Hard to trace the full transaction flow
- Partial failures: Must handle cases where compensation also fails

### CQRS (Command Query Responsibility Segregation)
Separate read and write models for a service or domain.

#### Write Side (Command Model)
- Optimized for consistency and business rule enforcement
- Uses normalized data models
- Handles complex validation
- Event sourcing: Store all state changes as events

#### Read Side (Query Model)
- Optimized for query performance
- Denormalized, projected views
- Multiple read models for different query patterns
- Populated via events (projections)

#### Benefits
- Independent scaling of read/write
- Different storage for different access patterns (PostgreSQL for writes, Elasticsearch for search, Redis for caching)
- Better performance for complex query use cases
- Clear separation between write intent and read intent

#### Event Sourcing
- Store events, not just current state
- Enables: full audit trail, temporal queries, replaying state, projections
- Challenges: eventual consistency in read models, event schema evolution (upcasting), snapshotting for performance

## 3. API Composition and Aggregation

### Backend for Frontend (BFF) Pattern
- Separate API layer per frontend client (mobile, web, third-party)
- Each BFF aggregates the specific data the client needs
- Reduces client complexity and network calls
- Owned by the frontend team, not a shared backend team

### API Gateway Patterns
- **Single gateway**: One entry point for all clients. Examples: Kong, AWS API Gateway, Apigee, Tyk, Ambassador
- **GraphQL Gateway**: Apollo Federation, GraphQL Mesh, GraphQL Hive
- **Aggregating gateway**: Fan out requests to multiple services, merge responses

### GraphQL Federation
GraphQL Federation allows building a supergraph that combines multiple subgraph schemas:
- Each service owns its subgraph schema
- The router (federation gateway) stitches them together
- Services can independently evolve their schemas
- Entities allow services to reference each other's types

#### Example Supergraph
```graphql
# Subgraph: Users
type User @key(fields: "id") {
  id: ID!
  name: String!
  email: String!
}

# Subgraph: Orders
type Order @key(fields: "id") {
  id: ID!
  user: User!
  total: Float!
}

# Router automatically resolves user reference in Order
```

### RESTful Aggregation
- API Composer pattern: orchestration layer that fans out to multiple services
- Use async parallel calls (Promise.all) where possible
- Handle partial failures gracefully (islands of data may be missing)
- Cache responses to reduce downstream load

### Data Graph Patterns
- Stitching data from multiple sources
- Real-time: GraphQL subscriptions, Server-Sent Events
- Materialized views: Pre-computed aggregations updated via events

## 4. Distributed Systems Patterns

### Circuit Breaker (Resilience4j, Envoy)
States: CLOSED (normal) → OPEN (failing) → HALF_OPEN (test recovery)
- CLOSED: Requests flow through normally. Failures counted.
- OPEN: Requests fail immediately with circuit open exception. No calls to failing service.
- HALF_OPEN: Limited requests allowed to test if service recovered.
- Thresholds: failure rate %, volume threshold, sleep window

### Bulkhead Pattern
- Isolate workloads so failure in one doesn't cascade
- Thread pool isolation in Java (Resilience4j Bulkhead)
- Connection pool isolation in network contexts
- Separate namespaces/pools per consumer in message queues

### Retry Patterns
- **Exponential backoff**: Wait times double with each retry (1s, 2s, 4s, 8s...)
- **Jitter**: Add randomness to prevent thundering herd
- **Budget**: Maximum retries, maximum total time
- **Retry on**: 5xx errors, timeouts, connection failures (NOT 4xx client errors)
- **Idempotency key**: Include in retry requests so duplicate processing is safe

### Rate Limiting and Throttling
- Token bucket algorithm (most common)
- Leaky bucket (smooths output rate)
- Fixed window vs sliding window counters
- Distributed rate limiting: Redis-based, per-API-key or per-customer-tier
- Global vs per-instance rate limits

### Load Shedding
- Reject requests before they consume resources
- Priority queues: critical traffic vs best-effort
- Load shedder at API gateway level
- Proportional shedding under extreme load

## 5. Service Discovery

### DNS-Based
- CoreDNS for Kubernetes
- Consul DNS interface
- Challenge: doesn't handle health checks,负载分配不均

### Service Registry
- **Eureka/Netflix**: Client-side discovery, with built-in health checks and load balancing
- **Consul**: Agent-based, HTTP API, DNS interface
- **etcd / ZooKeeper**: Key-value store for service endpoints

### Kubernetes Service Discovery
- Cluster DNS (kube-dns / CoreDNS)
- Service type: ClusterIP, NodePort, LoadBalancer, ExternalName
- EndpointSlices for scalable endpoint tracking
- Ingress for HTTP routing

### Service Mesh Discovery
- Automatic: sidecar proxies maintain service catalog from control plane
- DNS: Virtual hosts resolve to sidecar, not directly to pods
- Health checking: proxies test upstream services

## 6. Deployment Patterns

### Blue-Green Deployment
- Two identical environments: one live (blue), one idle (green)
- Deploy to green, smoke test, switch traffic
- Instant rollback: switch back to blue
- Cost: double the infrastructure during deployment

### Canary Deployment
- Gradually shift traffic from old to new (e.g., 5% → 20% → 100%)
- Monitor error rates, latency, business metrics
- Automated rollback if anomaly detected
- Tools: Flagger (Flux), Argo Rollouts, Spinnaker

### Rolling Deployment
- Gradually replace pods: terminate old, spin up new
- No double infrastructure cost
- Slower than blue-green
- Partial failure risk during rollout

### Feature Flags
- Decouple deployment from release
- Toggle features per user, percentage, region
- Tools: LaunchDarkly, Split.io, Flagsmith, Unleash
- Risk: flag debt, complexity in code paths

### Container Image Patterns
- Minimal base images (distroless, alpine)
- Multi-stage builds for small final image
- Distroless: no shell, minimal attack surface
- SBOM generation for security scanning

## 7. Communication Protocols

### HTTP/2 and gRPC
- Multiplexing: single TCP connection for many concurrent streams
- Binary framing (more efficient than HTTP/1.1 text)
- Header compression (HPACK)
- Built-in streaming (client, server, bidirectional)
- Protocol Buffers: strongly-typed, schema validation, backwards compatible

### WebSocket
- Full-duplex communication over a single TCP connection
- Good for real-time: dashboards, live updates, collaborative editing
- Challenge: stateful, harder to scale horizontally
- Connection management: heartbeat, reconnect logic

### Server-Sent Events (SSE)
- One-way server-to-client push over HTTP
- Simpler than WebSocket
- Auto-reconnect, event IDs for resume
- Good for: notifications, live feeds, progress updates

### Message Queue Protocols
- **AMQP**: RabbitMQ, advanced routing (exchanges, queues, bindings)
- **MQTT**: IoT, lightweight, publish-subscribe, low bandwidth
- **STOMP**: Simple text-based protocol, widely supported
- **Apache Kafka**: Distributed log, high throughput, configurable retention

## 8. Schema Registry and Contract Testing

### Contract Testing
- **Consumer-driven contracts**: Consumers define what they need, providers ensure compatibility
- Tools: Pact (broker-based, multi-language), Spring Cloud Contract
- Prevents breaking changes from going to production

### Schema Registry
- **Confluent Schema Registry**: Avro, JSON Schema, Protobuf
- **AWS Glue Schema Registry**: For Kinesis, MSK, Lambda
- **Apache Apicurio**: Open source, supports OpenAPI, AsyncAPI
- Enforce compatibility rules: BACKWARD, FORWARD, FULL, NONE

### API Versioning Strategies
- **URL path**: /v1/users, /v2/users — most explicit, good for REST
- **Header**: API-Version: 2 — cleaner URLs, but discovery harder
- **Content negotiation**: Accept: application/vnd.api.v2+json — semantically correct
- **Deprecation**: Sunset headers, documentation, client notifications

## 9. Scaling Patterns

### Horizontal vs Vertical Scaling
- Horizontal: more instances, stateless services, load balancing
- Vertical: bigger machines, simpler operations, limits to growth

### Stateless Services
- No local session state
- Session stored in distributed cache (Redis) or JWT
- Enables: scale out/in freely, rolling deployments, failure isolation

### Database Per Service
- Each microservice owns its data store
- Prevents tight coupling via shared databases
- Challenges: joins across services (use API composition), transactions, data duplication
- Pattern: Database per Service + Read replicas for heavy query loads

### Sharding Strategies
- Hash-based sharding: consistent hashing for even distribution
- Range-based: shard by date, region, alphabetical range
- Directory-based: lookup table for shard routing
- Trade-offs: rebalancing cost, cross-shard queries

### Caching Strategies
- **Cache-aside**: application checks cache first, populates on miss
- **Write-through**: write to cache and DB simultaneously
- **Write-behind**: write to cache, async write to DB
- **Refresh-ahead**: proactively refresh expiring entries
- Cache invalidation: TTL, event-driven invalidation, versioned keys

## 10. Best Practices

1. **Design for failure**: Every service call can fail. Timeouts, retries, circuit breakers.
2. **Observability first**: Distributed tracing, structured logging, metrics. You can't debug what you can't see.
3. **Health endpoints**: /health, /ready, /live for orchestration systems
4. **Graceful shutdown**: Handle SIGTERM, drain connections, finish in-flight requests
5. **Async by default**: Not everything needs to be synchronous request-response
6. **Domain-driven boundaries**: Services aligned with business domains, not technical layers
7. **API contracts are first-class**: Document, version, test, protect
8. **Security at every layer**: mTLS, API keys, OAuth2, rate limiting, input validation
9. **Feature flags for gradual rollouts**: Decouple deployment from release
10. **Containerization and orchestration**: Kubernetes, Helm, Kustomize

## 11. Key Technologies and Tools

| Category | Tools |
|----------|-------|
| Service Mesh | Istio, Linkerd, Consul Connect, Kuma |
| API Gateway | Kong, Tyk, AWS API Gateway, Ambassador |
| gRPC | grpc-go, grpc-java, grpc-node |
| Message Queue | RabbitMQ, Kafka, SQS/SNS, Azure Service Bus |
| Saga Orchestration | Temporal, Conductor, AWS Step Functions |
| Contract Testing | Pact, Spring Cloud Contract |
| Schema Registry | Confluent Schema Registry, Apicurio, AWS Glue |
| Feature Flags | LaunchDarkly, Split, Unleash |
| Deployment | ArgoCD, Flux, Flagger, Spinnaker |
| Kubernetes | K3s, Kube-batch, Knative, KEDA |
| API Docs | OpenAPI, AsyncAPI, Slate, Redoc |

---
Sources: Web research — Istio docs, Linkerd docs, Martin Fowler (CQRS, Saga), Netflix Conductor docs, Temporal.io, CNCF landscape, Kubernetes documentation, gRPC official site, AWS well-architected framework.
