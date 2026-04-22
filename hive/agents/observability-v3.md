# Observability Deep Research

Date: 2026-04-22
Agent: api-expert / ap-b3

## 1. Distributed Tracing

### What is Distributed Tracing?
A method of tracking requests as they flow through a distributed system — across services, processes, and network boundaries. Each unit of work gets a trace ID that propagates through every component.

### Core Concepts
- **Trace**: The complete journey of a request from start to end across all services
- **Span**: A single unit of work within a trace (one function call, one HTTP request)
- **Span Context**: Metadata that links spans together (trace ID, span ID, baggage)
- **Parent-child relationships**: Each span knows its parent, enabling a tree structure

### Trace Anatomy
```
Trace: [abc123]
  Span: [api-gateway] duration=45ms
    Span: [auth-service] duration=12ms
    Span: [user-service] duration=8ms
    Span: [order-service] duration=30ms
      Span: [payment-service] duration=20ms
      Span: [inventory-service] duration=15ms
      Span: [notification-service] duration=5ms
    Span: [response-formatter] duration=3ms
```

### Propagation Standards
- **W3C Trace Context**: Industry standard for trace propagation
  - `traceparent: 00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01`
  - `tracestate: congo=t61rcWkgMzE,P@ro=54n5j1D2`
- **B3 (Zipkin format)**: `X-B3-TraceId`, `X-B3-SpanId`, `X-B3-ParentSpanId`
- **Jaeger/Baryon**: Custom propagation headers

### Sampling Strategies
- **Head-based**: Decision made at trace start (in the SDK/agent)
  - Constant rate: sample N% of all traces
  - Rate limiting: N traces per second
  - Probabilistic: random sample based on probability
- **Tail-based**: Decision made at trace end (collector side)
  - Capture all spans cheaply, fully store interesting traces
  - More complex but ensures rare/slow traces are captured
  - Tools: Jaeger collector tail sampling, OpenTelemetry tail sampling processor

### Instrumentation Approaches
- **Automatic instrumentation**: Agents/libraries auto-inject spans
  - OpenTelemetry auto-instrumentation (Java, Python, Node.js, Go)
  - Envoy proxy: spans generated for every HTTP/gRPC call
  - Database drivers: span for every SQL query
- **Manual instrumentation**: Add spans in application code
  ```go
  ctx, span := tracer.Start(ctx, "process-order")
  defer span.End()
  span.SetAttributes("order.id", orderID)
  span.RecordError(err)
  ```

## 2. OpenTelemetry

### Architecture Overview
```
[Application] --> [OTel SDK] --> [Collector] --> [Backend]
                        |
                   [Auto-instrumentation]
                   [Manual spans/traces/metrics/logs]
```

### Signal Types (The Three Pillars)
1. **Traces**: Distributed tracing, spans with timing
2. **Metrics**: Aggregated measurements (counters, gauges, histograms)
3. **Logs**: Individual log events with correlation data

### Collector (OTel Collector)
- Receives telemetry from applications (OTLP, Jaeger, Zipkin, Prometheus)
- Processes and enriches: sampling, filtering, transforming
- Exports to backends: Jaeger, Tempo, Prometheus, Datadog, Honeycomb, etc.
- Deployment modes: Agent (sidecar/daemonset), Gateway (centralized), Hybrid

### Key Components

#### Resource
Metadata about the service producing telemetry:
```yaml
resource:
  attributes:
    service.name: user-service
    service.version: 2.1.0
    deployment.environment: production
    cloud.zone: us-east-1a
```

#### Attributes
Key-value pairs attached to spans, metrics, logs:
- Use consistent naming conventions (snake_case)
- Record relevant business context: user_id, tenant_id, order_id
- Limit cardinality on high-volume attributes

#### Context Propagation
- Baggage: cross-service key-value pairs that flow with trace context
- Used for: request-scoped data, tenant ID, user role, experiment flags
- Propagated via W3C Trace Context headers (or baggage header)

### Semantic Conventions
Standard attribute names for common operations:
- `http.method`, `http.url`, `http.status_code`, `http.host`
- `db.system`, `db.name`, `db.statement`, `db.operation`
- `rpc.system`, `rpc.method`, `rpc.grpc.status_code`
- `messaging.system`, `messaging.destination`, `messaging.operation`

### OpenTelemetry SDKs
- **Go**: go.opentelemetry.io/otel
- **Node.js**: @opentelemetry/sdk-node
- **Python**: opentelemetry-api, opentelemetry-sdk
- **Java**: io.opentelemetry:opentelemetry-sdk
- **Rust**: opentelemetry-rust

### Collector Configuration Example
```yaml
receivers:
  otlp:
    protocols:
      grpc:
      http:
  jaeger:
    protocols:
      thrift_http:
  prometheus:
    config:
      scrape_configs:
        - job_name: 'services'

processors:
  batch:
    timeout: 10s
  memory_limiter:
    check_interval: 1s
    limit_mib: 1000

exporters:
  otlp/tempo:
    endpoint: tempo:4317
  prometheus:
    endpoint: 0.0.0.0:8889

service:
  pipelines:
    traces:
      receivers: [otlp, jaeger]
      processors: [memory_limiter, batch]
      exporters: [otlp/tempo]
    metrics:
      receivers: [prometheus]
      processors: [memory_limiter, batch]
      exporters: [prometheus]
```

## 3. Structured Logging

### Why Structured Logs?
- **Searchable**: Query by field (level, service, user_id, status_code)
- **Aggregatable**: Count errors by service, p95 latency by endpoint
- **Correlatable**: Join logs with traces via trace_id
- **Parseable**: Machine-readable, no fragile regex parsing

### Log Schema Design
```json
{
  "timestamp": "2026-04-22T14:32:15.123Z",
  "level": "error",
  "service": "order-service",
  "version": "3.2.1",
  "trace_id": "0af7651916cd43dd8448eb211c80319c",
  "span_id": "b7ad6b7169203331",
  "message": "Payment processing failed",
  "user_id": "usr_8x9k2m",
  "tenant_id": "acme-corp",
  "order_id": "ord_12345",
  "error_code": "PAYMENT_DECLINED",
  "error_details": {
    "processor": "stripe",
    "code": "card_declined",
    "decline_code": "insufficient_funds"
  },
  "duration_ms": 1247,
  "environment": "production"
}
```

### Log Levels
- **FATAL**: Unrecoverable, process will exit (use sparingly — alerts trigger)
- **ERROR**: Something failed, request couldn't complete
- **WARN**: Unexpected but recoverable (retry succeeded, degraded mode)
- **INFO**: Significant business events (order placed, payment successful, user logged in)
- **DEBUG**: Detailed debugging info (not in production log volume)
- **TRACE**: Even more verbose than debug

### Correlation
Always include in every log entry:
- `trace_id`: Link to distributed trace
- `span_id`: Link to specific span
- `request_id`: For non-traced requests
- `user_id`, `tenant_id`, `session_id`: Business context

### Log Sampling
- DEBUG and TRACE logs: sample in production (10-50% or rate-limited)
- High-cardinality fields: sample to prevent log explosion
- Error logs: always log (or log 100% with higher detail)

### JSON vs Structured Text
- **JSON**: Best for machine processing, log aggregation systems (ELK, Loki, Splunk)
- **Structured text (key=value)**: Human-readable + machine-parseable
- Example: `level=error msg="payment failed" order_id=12345 duration_ms=500`

### Log Tools and Systems

| Tool | Type | Notes |
|------|------|-------|
| Elasticsearch | Search engine | Core of ELK stack, expensive at scale |
| Loki (Grafana) | Log aggregation | Label-based, works with Prometheus |
| Splunk | Commercial SIEM | Powerful query language, expensive |
| Datadog Logs | SaaS | Excellent APM integration |
| Grafana Explore | Viewer | Works with Loki, Tempo, Prometheus |
| OpenTelemetry Collector | Collection | Export to any backend |

## 4. API Metrics

### RED Method (Requests, Errors, Duration)
For every API endpoint or service:
- **Rate**: Requests per second (throughput)
- **Errors**: Error rate (4xx + 5xx or just 5xx as "errors")
- **Duration**: Latency distribution (p50, p95, p99)

### USE Method (Utilization, Saturation, Errors)
For every resource:
- **Utilization**: % busy (CPU %, memory %)
- **Saturation**: Queue depth, load average, buffer levels
- **Errors**: Error rate for the resource

### Key Metrics for APIs

#### Latency Metrics
- **p50 (median)**: Half of requests are faster
- **p90 (90th percentile)**: 10% of requests are slower
- **p95**: SLA threshold for many companies
- **p99 (or p99.9)**: Where outliers live, critical for tail latency
- **p99.99 (4 nines)**: <3.65 seconds of downtime/year target
- **Mean/Average**: Can be skewed by outliers, use alongside percentiles
- **Histogram buckets**: Full distribution, not just aggregates

#### Request Metrics
- Total requests (rate)
- Requests by endpoint, method, status code
- Unique clients (by API key, user ID)
- Payload size (request and response bytes)

#### Error Metrics
- Error rate: errors/total requests (often per minute)
- Error types: 4xx client errors, 5xx server errors
- Error breakdown by endpoint, client, region
- Critical errors: specific error codes that trigger alerts

#### Saturation / Capacity Metrics
- Request queue depth
- Connection pool utilization
- Thread pool utilization
- Memory pressure
- CPU utilization
- Goroutines / threads in flight

### Histograms and Buckets
```yaml
# Prometheus histogram for API latency
histogram:
  buckets: [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10]
  labels: [method, endpoint, status_code]
  # Buckets tuned for API latency (most API calls <100ms)
```

### SLI / SLO / SLA

#### SLI (Service Level Indicator)
What you measure:
- Request latency: p95 < 200ms
- Error rate: < 0.1%
- Availability: > 99.9% of requests successful

#### SLO (Service Level Objective)
Target values for SLIs:
- 99.9% availability (8.76 hours downtime/year)
- p95 latency < 200ms for 95% of requests

#### Error Budget
```
SLO: 99.9% → Allowed downtime: 43.83 min/month or 8.76 hours/year
"Error budget" = 100% - SLO

If error budget consumed in 15 days:
- Alert: Budget burn rate too fast
- Action: Freeze deployments, investigate
```

#### Real User Monitoring (RUM)
- Page load timing: TTFB, LCP, FID, CLS
- API call timing from browser
- User-facing errors
- Geographic and device breakdowns

## 5. Alerting and On-Call

### Alert Design Principles
- **Actionable**: Every alert requires human action, not just notification
- **No alert fatigue**: Fewer, more meaningful alerts
- **Severity levels**: P1 critical, P2 high, P3 medium, P4 low
- **Runbooks**: Every alert has a documented response procedure

### Alerting Rules (Prometheus/Grafana)
```yaml
groups:
  - name: api-alerts
    rules:
      - alert: HighErrorRate
        expr: |
          sum(rate(http_requests_total{status_code=~"5.."}[5m]))
          / sum(rate(http_requests_total[5m])) > 0.01
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "High API error rate"
          description: "Error rate is {{ $value | humanizePercentage }} (threshold: 1%)"
          runbook: "https://wiki.example.com/runbooks/high-error-rate"

      - alert: HighLatency
        expr: |
          histogram_quantile(0.95, 
            sum(rate(http_request_duration_seconds_bucket[5m])) by (le, service)
          ) > 0.5
        for: 5m
        labels:
          severity: warning

      - alert: SLOBudgetBurn
        expr: |
          sum(rate(errors_total[1h])) / 100 > 2 * (1 - 0.999)
        for: 5m
        labels:
          severity: warning
```

### On-Call Best Practices
- Rotation schedule with fair distribution
- Escalation policies: P1 → engineer → lead → director
- Acknowledgment timeout: auto-escalate if not acknowledged
- Noisy hours: reduce alert volume at night (use wake-up appropriately)
- Incident management: define severity, create incident channel, assign IC

### Post-Incident Review (PIR) / Postmortem
- Blameless review: focus on systems, not individuals
- Timeline reconstruction from traces, logs, metrics
- Root cause analysis (5 whys, fishbone)
- Action items: specific, assigned, time-bound
- Follow-up: verify fixes worked

## 6. Service Level Objectives (SLO) Framework

### Defining Good SLOs
1. **Pick the right SLIs**: User-facing, measurable, represents user experience
2. **Set aspirational targets**: Not what you're currently hitting, what you want
3. **Involve stakeholders**: Business, product, engineering agree on targets
4. **Iterate**: SLOs change as understanding grows

### SLO Examples by Service Type
- **Public API**: Availability 99.95%, Latency p99 < 500ms, Error rate < 0.1%
- **Internal service**: Availability 99.9%, Latency p99 < 200ms
- **Critical payment service**: Availability 99.99%, Latency p99 < 100ms
- **Batch job**: Throughput > 1000 records/min, completion within SLA

### Multi-layered SLOs
```
User experience SLO (end-to-end):
  → API Gateway SLO
    → Auth Service SLO
    → User Service SLO
    → Order Service SLO
      → Database SLO
      → Payment Service SLO
```

### SLO Burn Rate Alerts
```yaml
# 30-day window, 1-hour burn rate
- alert: SLOSlowBurn
  expr: |
    sum(rate(http_requests_total{status_code=~"5.."}[1h])) 
    / sum(rate(http_requests_total[1h])) > 0.001
  for: 3h
  labels:
    severity: warning

- alert: SLOFastBurn
  expr: |
    sum(rate(http_requests_total{status_code=~"5.."}[5m]))
    / sum(rate(http_request_total[5m])) > 0.005
  for: 10m
  labels:
    severity: critical
```

## 7. Visualization and Dashboards

### Golden Signals Dashboard
For every service, at minimum:
1. **Latency**: Distribution histogram, p50/p95/p99 over time
2. **Traffic**: Requests per second, broken down by endpoint/status
3. **Errors**: Error rate (%) and count over time, by error type
4. **Saturation**: CPU, memory, connection pool, queue depth

### Distributed Trace Visualization
- **Service graph**: Directed graph of service dependencies (how services connect)
- **Trace waterfall**: Timeline of spans for one request
- **Span detail**: All attributes, logs, events attached to a span
- **Error trace**: Traces that ended in error, highlighted
- **Flame graph**: Stack trace visualization for profiling (Grafana Pyroscope)

### Trace-Log-Metric Correlation
- **Grafana**: Unified dashboard with traces (Tempo), logs (Loki), metrics (Prometheus)
- **Jaeger + Elasticsearch**: Trace visualization with linked logs
- **Datadog/Honeycomb**: Native correlation, click trace → see logs

### Dashboard Hierarchy
```
Organization Dashboard
  → Team Dashboard
    → Service Dashboard
      → Endpoint Dashboard
        → Instance/Host Dashboard
```

## 8. Infrastructure Observability

### Kubernetes Observability
- **kube-state-metrics**: Cluster state (deployments, pods, services)
- **cAdvisor**: Container metrics (CPU, memory, filesystem)
- **Node Exporter**: Host-level metrics
- **Prometheus Operator**: Auto-discovery of services/pods
- **kubectl top**: Quick cluster resource check

### Container Metrics
- CPU throttling: throttling_cpu_seconds_total (throttling = resource limit)
- Memory working set: memory_working_set_bytes
- Restart count: restart count, restarts in last hour
- OOMKilled: container memory limit exceeded

### Network Observability
- **eBPF-based**: Cilium, Pixie — zero-code-injection network tracing
- Service mesh metrics: connection counts, mTLS status, circuit breaker state
- DNS resolution latency
- Packet loss, retransmits

## 9. Tracing Backend Comparison

| Backend | Strengths | Best For |
|---------|-----------|---------|
| **Jaeger** | CNCF, open source, self-hosted, low cost | Self-hosted, Kubernetes |
| **Grafana Tempo** | Very low storage cost (object storage), Grafana integration | Cost-sensitive, high volume |
| **AWS X-Ray** | AWS-native integration, Lambda tracing | AWS-hosted services |
| **Datadog APM** | Best-in-class UI, RUM, profiling, AI suggestions | Enterprise, multiple tech stacks |
| **Honeycomb** | Event-based, flexible schema, Retriever query language | Debugging complex interactions |
| **New Relic** | Broad APM coverage, legacy support | Enterprises with existing NR |
| **Lightstep** | Satellites for low overhead, enterprise | High-scale, low-latency services |

### Cost Optimization
- Tail sampling: store all spans cheaply, fully record interesting ones
- Span deduplication: merge duplicate spans from multiple exporters
- Retention: hot storage (30 days), cold storage (longer term, compressed)
- Backend choice: object storage (Tempo) >> Elasticsearch << commercial SaaS

## 10. Profiling

### Continuous Profiling
- Captures CPU, memory, and wall-time profiles continuously
- Attach to traces: click trace span → flame graph of that request
- Compare profiles between time periods: "what changed in the last week?"

### Tools
- **Grafana Pyroscope**: Open source, low overhead, continuous profiling
- **Datadog Profiler**: Paid, deep integration
- **Google Cloud Profiler**: GCP-native
- **Async Profiler**: JVM, CPU + memory + lock profiling

### Flame Graph
- X-axis: stack depth (alphabetical or by frequency)
- Y-axis: call stack depth
- Width: proportion of time spent in that function
- Color: CPU (red), memory (blue), alloc (orange)

## 11. Chaos Engineering

### Principles
- Start with hypothesis: "If we kill one instance, latency stays < 200ms"
- Test in staging first, then production with careful controls
- Measure impact on SLOs
- Automate experiments with steady state validation

### Tools
- **Chaos Mesh**: Kubernetes-native, supports many fault types
- **Gremlin**: Managed chaos, good for multi-cloud
- **AWS Fault Injection Simulator (FIS)**: AWS-native, latency, throttling, shutdown
- **LitmusChaos**: Cloud-native, CNCF project

### Common Experiments
- Kill pod: validate resilience, auto-restart
- Network partition: validate timeout and retry behavior
- CPU/memory stress: validate autoscaling, rate limiting
- Database slow queries: validate timeout handling
- Clock skew: validate timestamp handling, JWT expiration

---
Sources: Web research — OpenTelemetry official docs, W3C Trace Context spec, Prometheus docs, Grafana Loki/Tempo/Pyroscope docs, Google SRE book (SLO chapter), AWS Observability Best Practices, CNCF Observability White Paper, Datadog APM docs, Honeycomb docs, Jaeger docs, Kubernetes observability patterns.
