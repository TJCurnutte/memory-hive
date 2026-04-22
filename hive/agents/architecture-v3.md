# Software Architecture Patterns & Patterns 2026 — Deep Research
## Coder Agent — Architecture Deep Dive (v3)

> Research date: 2026-04-22 | Focus: Modern architecture for AI-era systems

---

## Table of Contents
1. [Architecture Patterns in 2026](#1-architecture-patterns-in-2026)
2. [Microservices vs Monolith for AI Agents](#2-microservices-vs-monolith-for-ai-agents)
3. [Event-Driven Architecture](#3-event-driven-architecture)
4. [Domain-Driven Design in Practice](#4-domain-driven-design-in-practice)
5. [CQRS — Command Query Responsibility Segregation](#5-cqrs)
6. [Event Sourcing](#6-event-sourcing)
7. [AI Agent Architecture Patterns](#7-ai-agent-architecture-patterns)
8. [Key Insights & Recommendations](#8-key-insights--recommendations)
9. [References & Further Reading](#9-references--further-reading)

---


<a name="1-architecture-patterns-in-2026"></a>
## 1. Architecture Patterns in 2026

The software architecture landscape in 2026 is defined by three converging forces: the proliferation of AI agents requiring new coordination primitives, edge computing becoming mainstream, and sustainability/energy efficiency becoming first-class concerns alongside performance.

### 1.1 The Macro Trends

**AI-First Architecture**: Systems are being designed with AI agents as first-class citizens. This means:
- Agents need well-defined interfaces (tools/functions they can call)
- Orchestration layers for multi-agent workflows
- Memory and state management for persistent agents
- Planning and reasoning infrastructure

**Edge-Native Design**: Rather than treating edge as an optimization, architects are designing edge-first systems. This aligns with:
- Latency requirements for real-time AI inference
- Data sovereignty and privacy regulations
- Bandwidth efficiency for AI workloads
- Resilience and offline-first requirements

**Sustainable Architecture**: Energy consumption of software systems is becoming a design consideration. Techniques include:
- Right-sizing compute based on actual SLAs
- Batching workloads to maximize CPU utilization
- Choosing energy-efficient languages for specific workloads
- Carbon-aware computing (scheduling heavy workloads when renewable energy is available)

### 1.2 The Patterns That Survived and Evolved

**Hexagonal Architecture (Ports & Adapters)**: Still highly relevant. The core business logic is isolated from external concerns through ports. Adapters (driven/secondary adapters) translate between the outside world and the core. In 2026, this pattern is often combined with AI capabilities.

Key benefits:
- Testability: Core domain logic has no dependencies on infrastructure
- Flexibility: Swap adapters (e.g., switch from PostgreSQL to DynamoDB) without changing business logic
- Clarity: Explicit ports make the boundaries very clear

```python
# Hexagonal architecture in Python — example structure
# 
# src/
#   domain/           # Pure business logic, no external dependencies
#     model.py        # Entities, Value Objects
#     service.py      # Domain Services
#     events.py       # Domain Events
#   application/      # Use cases, orchestration
#     commands.py     # Command handlers
#     queries.py      # Query handlers
#     ports.py        # Interface definitions (abstract)
#   adapters/         # Implementations of ports
#     primary/        # Driven (API endpoints, CLI)
#     secondary/      # Driving (databases, external APIs)
```

**Clean Architecture**: Evolved from Hexagonal, popularized by Robert Martin. Layers: Entities → Use Cases → Interface Adapters → Frameworks & Drivers. In 2026, this pattern is often implemented with dependency injection frameworks that make the architecture explicit in the code structure.

**Onion Architecture**: Similar to Hexagonal, emphasizing dependency direction pointing inward toward the core. Often used when the domain is complex and needs to be isolated from many different types of external concerns.

### 1.3 New Patterns for the AI Era

**Agent-Oriented Architecture (AOSA)**: Emerging pattern where software is decomposed into autonomous agents with defined responsibilities. Each agent:
- Has its own state and can make decisions
- Communicates via well-defined protocols (often message-based)
- Can be composed into hierarchies
- Can be deployed and scaled independently

Key differences from microservices:
- Agents are stateful and persistent (vs stateless services)
- Agents have goals and can plan (vs services that just respond to requests)
- Agent communication is often goal-oriented (vs REST/GraphQL)

**Semantic Kernel / AI Orchestration Patterns**: Microsoft's Semantic Kernel and similar frameworks introduced patterns for connecting AI models to traditional software. These patterns include:
- **Planner agents**: AI agents that decompose tasks into steps
- **Memory tiers**: Short-term (conversation), long-term (learned facts), semantic (vector store)
- **Skill loading**: Dynamically loading capabilities based on context

**Multi-Agent Coordination Patterns**: When multiple AI agents work together, several patterns emerge:
- **Hierarchical**: One agent coordinates others (boss → workers pattern)
- **Debate**: Agents argue different positions, a judge agent decides
- **Marketplace**: Agents offer services, others buy them (price-based coordination)
- **Voting/Consensus**: Agents vote on outcomes
- **Blackboard**: Shared state that agents read/write to coordinate

---

<a name="2-microservices-vs-monolith-for-ai-agents"></a>
## 2. Microservices vs Monolith for AI Agents

This is one of the most important architectural decisions in AI-era systems. The answer has nuances.

### 2.1 When Monoliths Still Win

**For AI agents specifically**, monoliths often win when:
1. **The agent needs to reason across many domains** — having everything in one process makes this faster and more coherent
2. **State is complex and relational** — SQL databases with ACID transactions are easier to reason about
3. **The team is small** — the operational overhead of microservices is real
4. **Latency is critical** — in-process calls are faster than network calls
5. **The agent is a single, cohesive entity** — splitting it creates unnecessary complexity

**Practical guidance**: If your AI agent is a single product (e.g., a customer support bot), a well-structured monolith (using clean/hexagonal architecture internally) is usually the right choice. You get:
- Faster development cycles
- Easier debugging
- Simpler deployment
- ACID transactions for complex workflows

**The Modular Monolith**: An increasingly popular approach. Structure the monolith with clear module boundaries (as if it were microservices) but deploy as a single unit. You get:
- Clear separation of concerns
- Ability to extract modules as true microservices later if needed
- No network overhead
- Simpler operations

```python
# Modular monolith structure
# app/
#   modules/
#     order_management/    # Treated as a module with clear boundaries
#       domain/            # Entities, services, events
#       application/       # Commands, queries, use cases
#       infrastructure/    # DB repositories, external API clients
#       api/               # Controllers (often minimal)
#     inventory/
#       domain/
#       application/
#       infrastructure/
#       api/
#     ai_agent/            # The AI component as a module
#       domain/            # Agent state, goals, contexts
#       application/       # Reasoning, planning, tool execution
#       infrastructure/    # LLM API adapters, vector DB
#       api/
#   shared/               # Cross-cutting concerns
#     events/              # Shared event bus
#     logging/
#     monitoring/
```

### 2.2 When to Choose Microservices for AI Systems

Microservices make sense when:
1. **Different components have very different scaling characteristics** — e.g., the vector DB needs 10x more memory than the web server
2. **Different teams own different parts** — clear ownership boundaries
3. **You need different technology stacks** — some parts need Python (for ML), others need Go (for high performance)
4. **Fault isolation is critical** — if the AI inference component fails, the rest of the system should keep working
5. **You need independent deployability** — different parts change at different rates

**AI-specific microservices considerations**:
- **LLM Gateway service**: Centralized management of LLM calls, rate limiting, caching, fallback
- **Vector store service**: Dedicated service for embeddings and similarity search
- **Memory service**: Long-term memory and context management
- **Tool execution service**: Sandboxed execution of agent tools
- **Orchestration service**: Workflow and multi-agent coordination

### 2.3 The Hybrid Approach (Most Common in 2026)

The most successful architectures in 2026 are **hybrid**:
- Core agent logic in a modular monolith
- Heavy lifting (LLM inference, vector search) as separate services
- Event-driven communication for loose coupling
- Shared event bus for cross-cutting concerns

This gives you the best of both worlds: the operational simplicity of a monolith with the scaling flexibility of microservices.

### 2.4 Key Decision Framework

```
Ask: Does this component need to scale independently?
  └── No → Modular monolith
  └── Yes → Ask: Is it AI-specific infrastructure?
      └── Yes → Extract as microservice (LLM gateway, vector store)
      └── No → Ask: Does it have different team ownership?
          └── Yes → Microservice
          └── No → Ask: Will network latency hurt user experience?
              └── Yes → Keep in monolith (co-locate)
              └── No → Could be microservice
```

---

<a name="3-event-driven-architecture"></a>
## 3. Event-Driven Architecture

Event-driven architecture has become the backbone of modern AI systems, enabling loose coupling, scalability, and the reactive patterns that AI workflows require.

### 3.1 Core Concepts

**Events vs Commands**: Understanding the distinction is critical.

- **Event**: "Something happened" — the system did something and is informing others. Emitted by the aggregate that owns the state. The emitter doesn't know who will handle it.
  - Example: `OrderPlaced`, `UserPreferencesUpdated`, `AgentTaskCompleted`
  - Past tense naming convention
  - Fire and forget (though you can have event sourcing for recovery)

- **Command**: "Do this" — a directive to a specific recipient. The sender knows who should handle it and expects a response.
  - Example: `PlaceOrder`, `UpdateUserPreferences`, `ExecuteAgentTask`
  - Imperative naming convention
  - Expects acknowledgment/response

**Event Carried State Transfer (ECST)**: A pattern where an event carries enough state that the consumer can update its local copy without needing to query the source system again. Reduces coupling and improves performance.

```python
# Event example with ECST
@ dataclass
class OrderPlacedEvent:
    event_id: str          # UUID for deduplication
    aggregate_id: str      # Order ID
    occurred_at: datetime  # Timestamp
    payload: OrderPayload  # Full order data (state transfer)
    
@dataclass
class OrderPayload:
    customer_id: str
    items: List[OrderItem]
    total: Decimal
    shipping_address: Address
    # Full payload so consumers don't need to call back
```

### 3.2 Event Processing Patterns

**Simple Event Processing**: Event triggers an action. One event → one handler → one action. Suitable for simple integrations.

**Event Streaming**: Events are written to an append-only log (Kafka, AWS Kinesis, etc.). Multiple consumers can read and process independently. The log is the source of truth.

**Complex Event Processing (CEP)**: Multiple events are correlated to detect patterns. Example: detecting fraud by correlating login events, purchase events, and shipping address changes.

**Event Sourcing**: The log IS the database. Instead of storing current state, you store all events that led to current state. Enables powerful features like time-travel debugging, replay, and audit trails. Covered in detail in Section 6.

### 3.3 Event Bus Implementations

**In-Process Event Bus** (for monoliths):
- Python: `events`, `dispatch`
- Node.js: `EventEmitter` from Node's events module
- Go: Channels or libraries like `go-event`/`eventbus`

**Message Broker Solutions**:
- **Apache Kafka**: The heavyweight choice. Excellent for high-throughput, exactly-once semantics, log retention, and replay. Best for event sourcing and event streaming at scale.
  - Good for: High-volume event streams, event sourcing, audit logs
  - Considerations: Operational complexity, requires Kafka expertise
  
- **Redis Streams**: Lightweight, Redis-based. Good for medium-throughput scenarios. Simpler than Kafka but less powerful.
  
- **Amazon EventBridge / SNS**: Cloud-native, serverless. Good for AWS-centric architectures.
  
- **Google Cloud Pub/Sub**: GCP-native, excellent for Google Cloud deployments.
  
- **Azure Event Grid / Service Bus**: Microsoft ecosystem equivalent.

### 3.4 Event Schema Design

A critical and often overlooked aspect. Events should be:
1. **Self-describing**: Include event type, version, timestamp
2. **Backward compatible**: New fields should be optional or have defaults
3. **Forward compatible**: Old consumers should ignore unknown fields
4. **Well-documented**: Schema registry (Confluent Schema Registry, AWS Glue, etc.)

```python
# Good event schema design
@dataclass
class BaseEvent:
    event_type: str        # "agent.task.completed"
    event_version: str     # "1.0" — for schema evolution
    event_id: str          # UUID
    occurred_at: datetime  # ISO 8601
    correlation_id: str    # For tracing related events
    causation_id: str      # What caused this event
    
@dataclass
class AgentTaskCompletedEvent(BaseEvent):
    task_id: str
    agent_id: str
    result: Dict[str, Any]  # Structured result
    duration_ms: int
    tokens_used: int        # AI cost tracking
    # New fields added in v2:
    # metadata: Dict[str, Any]  # Optional, v2+ producers
```

### 3.5 Idempotency

Events can be delivered more than once (network issues, retries, at-least-once delivery). Handlers MUST be idempotent.

```python
# Idempotent event handler
class OrderPlacedHandler:
    def __init__(self, db: Database):
        self.db = db
    
    def handle(self, event: OrderPlacedEvent):
        # Check if already processed (idempotency key)
        existing = self.db.query(
            "SELECT id FROM processed_events WHERE event_id = ?",
            [event.event_id]
        )
        if existing:
            logger.info(f"Event {event.event_id} already processed, skipping")
            return
        
        # Process the event
        self._process_order(event)
        
        # Record that we processed it
        self.db.execute(
            "INSERT INTO processed_events (event_id, processed_at) VALUES (?, ?)",
            [event.event_id, datetime.now()]
        )
        self.db.commit()
```

### 3.6 Event-Driven Architecture for AI Agents

AI agents benefit enormously from event-driven patterns:

1. **Decoupled tool execution**: Tool calls become events. The agent emits a `ToolCallRequested` event; a separate service handles execution and emits `ToolCallCompleted` or `ToolCallFailed`.

2. **Observability**: Agent reasoning steps can be emitted as events, enabling debugging, compliance, and improvement.

3. **Multi-agent coordination**: Events are the natural medium for agent communication. An agent doesn't know or care which other agents are listening.

```python
# AI agent event-driven architecture
class AIAgent:
    def __init__(self, event_bus: EventBus, llm: LLMAdapter, tool_registry: ToolRegistry):
        self.event_bus = event_bus
        self.llm = llm
        self.tool_registry = tool_registry
    
    async def process_goal(self, goal: Goal):
        # Emit planning started event
        self.event_bus.publish(AgentPlanningStartedEvent(
            agent_id=self.agent_id,
            goal_id=goal.id
        ))
        
        # LLM generates plan
        plan = await self.llm.plan(goal)
        
        # Emit plan created event (for observability/debugging)
        self.event_bus.publish(AgentPlanCreatedEvent(
            agent_id=self.agent_id,
            goal_id=goal.id,
            plan_steps=[s.dict() for s in plan.steps]
        ))
        
        # Execute plan steps
        for step in plan.steps:
            result = await self._execute_step(step)
            self.event_bus.publish(AgentStepCompletedEvent(
                agent_id=self.agent_id,
                goal_id=goal.id,
                step=step.name,
                result=result
            ))
        
        self.event_bus.publish(AgentGoalCompletedEvent(
            agent_id=self.agent_id,
            goal_id=goal.id,
            final_result=result
        ))
```

---

<a name="4-domain-driven-design-in-practice"></a>
## 4. Domain-Driven Design in Practice

DDD remains one of the most powerful approaches to structuring complex software, especially for AI systems where the domain logic is often intricate and evolving.

### 4.1 The Strategic Patterns (Big Picture)

**Bounded Contexts**: The most important strategic pattern. A bounded context is a linguistic and organizational boundary where a particular domain model is valid and consistent.

Key insight: Different parts of your organization may use the same words to mean different things. In a `CustomerSupport` context, a "Ticket" is a support issue. In an `Analytics` context, a "Ticket" is a data point about support volume. These are different bounded contexts with different models.

**Identifying Bounded Contexts**:
- Look for different vocabulary (same words, different meanings)
- Look for different update frequencies (what changes together stays together)
- Look for different teams (Conway's Law applies)
- Look for different SLAs (different quality attributes)
- Look for different regulatory environments

**Context Mapping**: How do bounded contexts relate to each other?

- **Partnership**: Two contexts cooperate; changes in one require coordination with the other
- **Shared Kernel**: Two contexts share a subset of the domain model (careful — can become a source of coupling)
- **Customer-Supplier (Anti-Corruption Layer)**: One context provides for another; the upstream context is independent
- **Conformist**: You conform to the model of the upstream context (no translation)
- **Open Host Service**: Your context publishes a well-defined protocol that others can use
- **Published Language**: The communication happens through a well-defined shared language (often a schema)
- **Separate Ways**: Integration is not worth the cost; contexts are truly independent

### 4.2 The Tactical Patterns (Building Blocks)

**Aggregates**: A cluster of related entities and value objects that are treated as a unit for data changes. One entity within the aggregate is the **Aggregate Root**. External objects only interact with the aggregate through the root.

```python
# DDD Aggregate in Python
class Order:  # This is the Aggregate Root
    def __init__(self, order_id: OrderId, customer_id: CustomerId):
        self._id = order_id
        self._customer_id = customer_id
        self._items: List[OrderItem] = []
        self._status = OrderStatus.DRAFT
    
    @property
    def id(self) -> OrderId:
        return self._id
    
    def add_item(self, product: Product, quantity: int):
        if self._status != OrderStatus.DRAFT:
            raise InvalidOperationError("Cannot add items to non-draft order")
        
        existing_item = next(
            (item for item in self._items if item.product_id == product.id),
            None
        )
        if existing_item:
            existing_item.add_quantity(quantity)
        else:
            self._items.append(OrderItem(product.id, product.price, quantity))
    
    def place(self):
        if not self._items:
            raise DomainRuleViolation("Cannot place empty order")
        self._status = OrderStatus.PLACED
        # Domain event - immutable fact
        self._domain_events.append(OrderPlaced(self.id, self.total))
    
    def start_shipping(self):
        if self._status != OrderStatus.PLACED:
            raise InvalidOperationError("Cannot ship non-placed order")
        self._status = OrderStatus.SHIPPING
        self._domain_events.append(OrderShippingStarted(self.id))
    
    def clear_domain_events(self):
        events = self._domain_events[:]
        self._domain_events.clear()
        return events
    
    @property
    def total(self) -> Money:
        return sum(item.subtotal for item in self._items)
```

**Value Objects**: Immutable objects defined by their attributes rather than a unique identity. They are compared by their attribute values.

```python
# Value Object - Money
@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str
    
    def add(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise CurrencyMismatchError(f"Cannot add {self.currency} and {other.currency}")
        return Money(self.amount + other.amount, self.currency)
    
    def multiply(self, factor: Decimal) -> 'Money':
        return Money(self.amount * factor, self.currency)
    
    def __eq__(self, other):
        if not isinstance(other, Money):
            return False
        return self.amount == other.amount and self.currency == other.currency
```

**Domain Events**: The immutable facts that have happened in the domain. They are named in past tense because they represent things that have already happened. See Section 3.1 for implementation details.

**Domain Services**: When an operation doesn't belong naturally to any entity or value object, a domain service encapsulates it.

**Repositories**: Interfaces for accessing aggregates. The domain layer defines the interface; the infrastructure layer implements it.

**Factories**: Methods for creating complex objects and aggregates. They encapsulate the knowledge needed to correctly instantiate complex domain objects.

### 4.3 DDD with AI Agents

AI systems benefit from DDD in several specific ways:

1. **Clear boundaries around the AI capability**: The AI agent is a bounded context. It has its own language (prompts, responses, tools, goals). Other parts of the system (order management, billing) don't need to understand the internal workings of the agent.

2. **Anti-Corruption Layer between AI and business logic**: The agent's outputs (often natural language) need to be translated into structured domain events. The ACL protects the domain model from AI "hallucinations" or format changes.

3. **Context mapping for AI integration**: When integrating AI into an existing system, carefully map the AI context to other bounded contexts. For example:
   - `AIPlanningContext` ↔ `ProjectManagementContext` via a published language
   - `AIReasoningContext` ↔ `KnowledgeBaseContext` via conformist mapping (AI conforms to the KB schema)

```python
# Anti-Corruption Layer for AI output
class AIAgentOutputTranslator:
    """Translates natural language AI outputs into domain events.
    Protects the domain model from AI quirks."""
    
    def __init__(self, event_factory: DomainEventFactory):
        self.event_factory = event_factory
    
    def translate_task_completion(self, ai_output: str, context: ExecutionContext) -> List[DomainEvent]:
        # Parse AI output - be defensive, AI can hallucinate
        try:
            parsed = self._parse_json_or_structured(ai_output)
            
            # Map AI concepts to domain concepts
            domain_events = []
            
            if "status" in parsed:
                if parsed["status"] == "completed":
                    domain_events.append(self.event_factory.task_completed(
                        task_id=context.task_id,
                        result=parsed.get("result", {}),
                        completed_at=context.timestamp
                    ))
                elif parsed["status"] == "failed":
                    domain_events.append(self.event_factory.task_failed(
                        task_id=context.task_id,
                        reason=parsed.get("error", "Unknown"),
                        failed_at=context.timestamp
                    ))
            
            # Validate mapped events conform to domain rules
            for event in domain_events:
                self._validate_domain_compliance(event)
            
            return domain_events
            
        except (ParseError, ValidationError) as e:
            # Log the failure, emit a domain event about AI translation failure
            logger.warning(f"AI output translation failed: {e}, raw output: {ai_output[:200]}")
            return [self.event_factory.ai_output_translation_failed(
                task_id=context.task_id,
                raw_output=ai_output[:1000],  # Truncate for safety
                error=str(e)
            )]
    
    def _parse_json_or_structured(self, output: str) -> Dict:
        # Robust parsing with multiple fallback strategies
        # ...
        pass
    
    def _validate_domain_compliance(self, event: DomainEvent):
        # Ensure the event conforms to domain invariants
        # ...
        pass
```

### 4.4 DDD in Practice: Common Mistakes

1. **Over-engineering**: DDD is for complex domains. For simple CRUD apps, it's overkill. Use it where you have genuine complexity.

2. **Anemic domain models**: Objects that are just data bags with getters/setters. This is the most common DDD anti-pattern. The domain model should have behavior.

3. **Ignoring bounded contexts**: Trying to create one unified model for the entire organization. This leads to a "big ball of mud" domain model.

4. **Leaking infrastructure concerns into domain**: If your domain objects know about databases, ORMs, or network calls, you've violated the architecture.

5. **Using DDD terminology without understanding it**: Calling everything an "aggregate" without the right boundaries.

6. **Event-driven everything**: Not every system needs event sourcing. It's a powerful tool with significant complexity costs.

---

<a name="5-cqrs"></a>
## 5. CQRS — Command Query Responsibility Segregation

CQRS is the pattern of separating read and write operations into different models, allowing them to be optimized independently.

### 5.1 The Core Idea

In most systems, reads and writes have very different characteristics:

| Aspect | Write (Command) | Read (Query) |
|--------|-----------------|--------------|
| Data shape | Optimized for modification | Optimized for display |
| Latency requirements | Usually higher (user waits) | Can be more relaxed |
| Consistency | Must be exactly right | Can be slightly stale |
| Complexity | Business rules, validation | Aggregation, filtering |
| Scale | Often lower volume | Often much higher volume |
| Caching | Hard to cache writes | Easy to cache reads |

CQRS acknowledges this and allows you to treat them as separate concerns.

### 5.2 CQRS in Practice

**Simple CQRS (Single Database)**:
The same database, but separate command and query models (different classes/services).

```python
# Command side - optimized for writes
class CreateOrderCommand:
    def __init__(self, db: Database):
        self.db = db
    
    async def execute(self, cmd: CreateOrderCommandDTO) -> OrderId:
        # Validate business rules
        customer = await self._validate_customer(cmd.customer_id)
        if not customer.is_active:
            raise CustomerNotActiveError()
        
        # Create order
        order = Order.create(
            customer_id=cmd.customer_id,
            items=cmd.items,
            shipping_address=cmd.shipping_address
        )
        
        # Save (normalized, optimized for writes)
        await self.db.execute(
            "INSERT INTO orders (id, customer_id, status, created_at) VALUES (?, ?, ?, ?)",
            [order.id, order.customer_id, order.status.value, order.created_at]
        )
        
        for item in order.items:
            await self.db.execute(
                "INSERT INTO order_items (order_id, product_id, qty, price) VALUES (?, ?, ?, ?)",
                [order.id, item.product_id, item.quantity, item.price]
            )
        
        return order.id

# Query side - optimized for reads
class GetOrderQuery:
    def __init__(self, db: Database):
        self.db = db
    
    async def execute(self, order_id: OrderId) -> OrderDetailDTO:
        # Return a denormalized view with all related data
        row = await self.db.query_one(
            """
            SELECT o.*, c.name as customer_name, c.email as customer_email,
                   json_group_array(json_object(
                       'product_id', oi.product_id,
                       'product_name', p.name,
                       'quantity', oi.quantity,
                       'price', oi.price
                   )) as items
            FROM orders o
            JOIN customers c ON o.customer_id = c.id
            LEFT JOIN order_items oi ON o.id = oi.order_id
            LEFT JOIN products p ON oi.product_id = p.id
            WHERE o.id = ?
            GROUP BY o.id
            """,
            [order_id]
        )
        return OrderDetailDTO.from_db_row(row)
```

**CQRS with Separate Read Database**:
The command side writes to the main database; the query side reads from a read replica or read-optimized store.

This is common in high-scale systems:
- Write to PostgreSQL (normalized, transactional)
- Replicate to Elasticsearch or read replica (denormalized, query-optimized)
- Asynchronous synchronization (eventual consistency)

```python
# Event-driven CQRS synchronization
class OrderProjectionSynchronizer:
    """Syncs command-side data to query-side read model."""
    
    async def on_order_placed(self, event: OrderPlacedEvent):
        # Read from command database (or use event payload via ECST)
        order = await self.command_db.get_order(event.order_id)
        
        # Transform to read model
        read_model = OrderReadModel(
            id=order.id,
            customer_name=order.customer.name,
            customer_email=order.customer.email,
            total=order.total,
            item_count=len(order.items),
            placed_at=event.occurred_at,
            status="placed"
        )
        
        # Write to read database (or Elasticsearch, etc.)
        await self.read_db.upsert("orders", read_model.to_document())
```

### 5.3 CQRS with Event Sourcing

CQRS naturally combines with Event Sourcing (see Section 6). The write model is the event store; the read model is built by replaying events.

This combination is particularly powerful for AI systems because:
1. You get a complete audit trail of everything that happened
2. You can replay the history to understand agent behavior
3. Read models can be rebuilt from scratch if requirements change
4. The event store is the source of truth — if the read model is wrong, replay

### 5.4 When to Use CQRS

**Use CQRS when**:
- Reads and writes have very different performance requirements
- Different teams own reads and writes
- The domain naturally separates into command and query parts
- You need to scale reads and writes independently
- You want to optimize read models for specific use cases (dashboards, analytics, etc.)
- You're using event sourcing (CQRS + ES is a natural fit)

**Don't use CQRS when**:
- Your domain is simple CRUD
- You don't need the complexity of maintaining two models
- Eventual consistency between read and write is unacceptable
- The team doesn't understand the pattern (it adds complexity)

### 5.5 CQRS in AI Systems

For AI agents, CQRS is particularly useful:

**Command side**: The agent's decision-making, tool execution, planning
**Query side**: The agent's memory, context retrieval, conversation history

This mirrors how the human brain works — we don't store and retrieve memories in the same format as we make decisions.

```python
# AI Agent with CQRS
class AIAgent:
    def __init__(self, command_store: AgentCommandStore, query_store: AgentQueryStore):
        self.command_store = command_store  # Event store, decision logs
        self.query_store = query_store      # Vector DB, memory index
    
    async def think(self, context: GoalContext):
        # Query side: retrieve relevant memories, context
        memories = await self.query_store.retrieve_similar(context.goal, k=10)
        history = await self.query_store.get_conversation_history(context.conversation_id)
        
        # Use retrieved context to inform reasoning
        reasoning = await self.llm.reason(goal=context.goal, memories=memories, history=history)
        
        # Command side: record the decision/reasoning
        await self.command_store.record_reasoning(
            agent_id=self.agent_id,
            context=context,
            reasoning=reasoning,
            decision=reasoning.decision
        )
        
        return reasoning
```

---

<a name="6-event-sourcing"></a>
## 6. Event Sourcing

Event sourcing is the practice of storing state changes as a sequence of events, rather than storing the current state directly. The current state is derived by replaying all events.

### 6.1 Core Concepts

**Event Store**: An append-only log of events. This is the source of truth — there is no "current state" stored; it's always derived.

**Aggregate reconstruction**: To get the current state of an aggregate, load all events for that aggregate ID and apply them in order to reconstruct the state.

```python
class EventStore:
    def __init__(self, db: Database):
        self.db = db
    
    async def append(self, aggregate_id: str, events: List[DomainEvent], expected_version: int):
        # Optimistic concurrency check
        current_version = await self._get_version(aggregate_id)
        if current_version != expected_version:
            raise ConcurrencyConflict(expected_version, current_version)
        
        for event in events:
            await self.db.execute(
                """
                INSERT INTO events (aggregate_id, event_type, event_data, version, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                [aggregate_id, event.type, event.to_json(), expected_version + 1, datetime.now()]
            )
    
    async def get_events(self, aggregate_id: str) -> List[DomainEvent]:
        rows = await self.db.query(
            "SELECT * FROM events WHERE aggregate_id = ? ORDER BY version",
            [aggregate_id]
        )
        return [self._deserialize_event(row) for row in rows]
    
    async def get_events_from(self, aggregate_id: str, from_version: int) -> List[DomainEvent]:
        rows = await self.db.query(
            "SELECT * FROM events WHERE aggregate_id = ? AND version > ? ORDER BY version",
            [aggregate_id, from_version]
        )
        return [self._deserialize_event(row) for row in rows]

class OrderAggregate:
    """Reconstructs state from events."""
    
    @staticmethod
    def reconstruct(order_id: str, event_store: EventStore) -> 'OrderAggregate':
        events = await event_store.get_events(order_id)
        
        order = OrderAggregate.__new__(OrderAggregate)  # Create without __init__
        order._id = order_id
        order._status = OrderStatus.DRAFT
        order._items = []
        
        # Replay events
        for event in events:
            order._apply(event)
        
        return order
    
    def _apply(self, event: DomainEvent):
        if isinstance(event, OrderPlaced):
            self._status = OrderStatus.PLACED
            self._items = event.items
        elif isinstance(event, ItemAddedToOrder):
            self._items.append(event.item)
        elif isinstance(event, OrderShipped):
            self._status = OrderStatus.SHIPPING
            self._shipped_at = event.shipped_at
        # ... handle all event types
```

### 6.2 Projections (Building Read Models from Events)

Projections rebuild read models by consuming events and updating denormalized views.

```python
class OrderProjection:
    """Builds a read model for orders."""
    
    def __init__(self, read_db: ReadDatabase):
        self.read_db = read_db
    
    async def project(self, events: List[DomainEvent]):
        for event in events:
            await self._project_single(event)
    
    async def _project_single(self, event: DomainEvent):
        if isinstance(event, OrderPlaced):
            await self.read_db.execute(
                "INSERT INTO order_summaries (order_id, customer_id, total, status, created_at) VALUES (?, ?, ?, ?, ?)",
                [event.order_id, event.customer_id, event.total, "placed", event.occurred_at]
            )
        elif isinstance(event, OrderShipped):
            await self.read_db.execute(
                "UPDATE order_summaries SET status = 'shipped', shipped_at = ? WHERE order_id = ?",
                [event.shipped_at, event.order_id]
            )
        elif isinstance(event, ItemAddedToOrder):
            # Recalculate total — could also just add the delta
            current = await self.read_db.query_one(
                "SELECT total FROM order_summaries WHERE order_id = ?",
                [event.order_id]
            )
            new_total = Decimal(current.total) + event.item.price * event.item.quantity
            await self.read_db.execute(
                "UPDATE order_summaries SET total = ? WHERE order_id = ?",
                [new_total, event.order_id]
            )
```

### 6.3 Snapshots (Optimization)

Replay all events every time is expensive for aggregates with long histories. Snapshots store periodic state.

```python
class SnapshottingEventStore(EventStore):
    def __init__(self, db: Database, snapshot_interval: int = 100):
        super().__init__(db)
        self.snapshot_interval = snapshot_interval
    
    async def get_aggregate(self, aggregate_id: str) -> Aggregate:
        # Check for recent snapshot
        snapshot = await self._get_latest_snapshot(aggregate_id)
        
        if snapshot:
            # Reconstruct from snapshot
            aggregate = snapshot.to_aggregate()
            # Replay only events after snapshot
            events = await self.get_events_from(aggregate_id, snapshot.version)
            for event in events:
                aggregate._apply(event)
        else:
            # No snapshot, replay all events
            aggregate = await OrderAggregate.reconstruct(aggregate_id, self)
        
        return aggregate
    
    async def save_aggregate(self, aggregate: Aggregate):
        events = aggregate.clear_domain_events()
        if events:
            await self.append(aggregate.id, events, aggregate.version)
            
            # Create snapshot if needed
            if aggregate.version % self.snapshot_interval == 0:
                snapshot = Snapshot(
                    aggregate_id=aggregate.id,
                    version=aggregate.version,
                    state=aggregate.to_snapshot_state(),
                    created_at=datetime.now()
                )
                await self._save_snapshot(snapshot)
```

### 6.4 Event Sourcing in AI Systems

Event sourcing is exceptionally well-suited for AI agent systems:

1. **Complete audit trail**: Every decision, tool call, and reasoning step is recorded. You can replay any moment in the agent's "life."

2. **Debugging**: When an agent makes a bad decision, replay the events to understand what context led to that decision.

3. **Compliance**: Many AI systems need to explain their decisions. Event sourcing provides the evidence.

4. **Learning**: Historical events can be used to train improved models, understand failure patterns, and measure improvement.

5. **Temporal queries**: "What did the agent think 5 minutes ago?" — trivial with event sourcing, impossible with current-state storage.

```python
# AI Agent with Event Sourcing
class EventSourcedAIAgent:
    """An AI agent where every action is an event."""
    
    async def execute_goal(self, goal: Goal) -> GoalResult:
        agent_id = self._get_or_create_agent_id()
        
        # Load agent's history
        events = await self.event_store.get_events(agent_id)
        agent_state = self._reconstruct_state(events)
        
        # Update state with new goal
        agent_state.pending_goals.append(goal)
        
        # Reasoning becomes a command that creates events
        reasoning_result = await self._reason(agent_state, goal)
        
        # Record reasoning as events
        new_events = [
            ReasoningStarted(agent_id, goal.id, reasoning_result.context_snapshot),
            ReasoningStep(step_number=1, thought=reasoning_result.thought_1, tools_considered=...),
            ReasoningStep(step_number=2, thought=reasoning_result.thought_2, ...),
            ToolSelected(agent_id, goal.id, tool_id, reason),
            ToolExecuted(agent_id, goal.id, tool_id, result),
            GoalCompleted(agent_id, goal.id, final_result)
        ]
        
        await self.event_store.append(agent_id, new_events, agent_state.version)
        
        return GoalResult(final_result, events=new_events)
    
    async def diagnose_failure(self, goal_id: str):
        """Debug a failed goal by replaying events."""
        events = await self.event_store.get_events_by_type(
            event_type=GoalCompleted,
            metadata={"goal_id": goal_id, "status": "failed"}
        )
        
        # Replay from the beginning to see what happened
        agent_state = self._reconstruct_state(events)
        
        # Analyze failure patterns
        return FailureAnalysis(
            goal_id=goal_id,
            reasoning_trace=agent_state.reasoning_history,
            tool_calls=agent_state.tool_execution_history,
            failure_point=self._identify_failure_point(agent_state)
        )
```

### 6.5 Challenges and Mitigations

**Schema evolution**: Events from years ago need to be processed by current code. Solutions:
- Version events with a schema version number
- Upcasters: functions that transform old event versions to new versions
- Keep all versions processable (don't delete old code)

**Eventual consistency**: If you're using CQRS with separate read/write stores, there's a window where reads are stale.

**Storage size**: Over time, the event store grows. Solutions:
- Snapshots (covered above)
- Archival: move old events to cold storage
- Compaction: replace series of events with a single "state at time X" event

**Concurrent modifications**: Two processes trying to append to the same aggregate simultaneously. Solutions:
- Optimistic concurrency control (version checking)
- Conflict resolution (last writer wins, merge, or human resolution)

---

<a name="7-ai-agent-architecture-patterns"></a>
## 7. AI Agent Architecture Patterns

With AI agents becoming first-class software components, several architectural patterns have emerged.

### 7.1 Agent Loop Pattern

The foundational pattern — the agent's main loop:

```
while goal not completed:
    1. Observe (get context, check memory, read environment)
    2. Think (reason about what to do next)
    3. Plan (decide on next action)
    4. Act (execute the action)
    5. Reflect (update memory, check if goal is met)
```

This is the "ReAct" (Reasoning + Acting) pattern, popularized by papers like "ReAct: Synergizing Reasoning and Acting in Language Models."

```python
class AgentLoop:
    def __init__(self, llm: LLM, tools: List[Tool], memory: AgentMemory, max_iterations: int = 50):
        self.llm = llm
        self.tools = tools
        self.memory = memory
        self.max_iterations = max_iterations
    
    async def run(self, goal: Goal) -> GoalResult:
        observations = await self._observe(goal)
        
        for iteration in range(self.max_iterations):
            # Think
            thought = await self._think(goal, observations)
            
            # Decide next action
            action = await self._plan(goal, thought, observations)
            
            if action is None:
                # No more actions needed, goal likely complete
                break
            
            # Act
            result = await self._act(action)
            
            # Reflect
            observations = await self._reflect(goal, action, result, observations)
            
            # Check if goal is complete
            if self._is_goal_complete(goal, observations):
                break
        
        return GoalResult(
            success=True,
            iterations=iteration + 1,
            final_observations=observations
        )
    
    async def _think(self, goal: Goal, observations: List[Observation]) -> Thought:
        prompt = self._build_thinking_prompt(goal, observations)
        response = await self.llm.complete(prompt)
        return Thought.from_llm_response(response)
    
    async def _plan(self, goal: Goal, thought: Thought, observations: List[Observation]) -> Optional[Action]:
        # Decide if more action is needed, and what action
        # ...
        pass
    
    async def _act(self, action: Action) -> ActionResult:
        if action.tool_id in [t.id for t in self.tools]:
            tool = self._get_tool(action.tool_id)
            return await tool.execute(**action.parameters)
        else:
            return ActionResult(error=f"Unknown tool: {action.tool_id}")
    
    async def _reflect(self, goal: Goal, action: Action, result: ActionResult, 
                       observations: List[Observation]) -> List[Observation]:
        # Update memory with what happened
        memory_entry = MemoryEntry(
            agent_id=self.agent_id,
            goal_id=goal.id,
            action=action,
            result=result,
            timestamp=datetime.now()
        )
        await self.memory.add(memory_entry)
        
        # Add result to observations
        return observations + [Observation(result=result, source=action.tool_id)]
```

### 7.2 Tool-Using Agent Pattern

The agent can use external tools to gather information or perform actions. Tools are first-class citizens.

```python
@dataclass
class Tool:
    id: str
    name: str
    description: str
    parameters: List[ToolParameter]
    handler: Callable
    
    async def execute(self, **kwargs) -> ToolResult:
        # Validate parameters
        self._validate_parameters(kwargs)
        # Execute
        result = await self.handler(**kwargs)
        # Wrap result
        return ToolResult(
            tool_id=self.id,
            success=True,
            output=result,
            execution_time_ms=0  # track this
        )

class ToolUsingAgent:
    """Agent that selects and uses tools to accomplish goals."""
    
    async def select_tool(self, goal: Goal, context: ReasoningContext) -> Tool:
        # Use LLM to select tool based on goal and available tools
        tool_descriptions = "\n".join([f"- {t.name}: {t.description}" for t in self.tools])
        
        prompt = f"""
Goal: {goal.description}
Available tools:
{tool_descriptions}

Which tool is most appropriate for this goal? Return the tool name and parameters.
"""
        
        response = await self.llm.complete(prompt, tools=self.tools)
        return self._parse_tool_selection(response)
```

### 7.3 Hierarchical Agent Pattern

Multiple agents in a hierarchy, where higher-level agents coordinate lower-level ones.

```
Planning Agent (high-level)
  ├── Research Agent (mid-level)
  │     ├── Web Search Agent
  │     └── Document Analysis Agent
  ├── Writing Agent (mid-level)
  │     ├── Draft Agent
  │     └── Edit Agent
  └── Verification Agent (mid-level)
        └── Fact Check Agent
```

```python
class HierarchicalAgent:
    def __init__(self, agents: Dict[str, Agent], planner: LLM):
        self.agents = agents
        self.planner = planner
    
    async def execute(self, goal: Goal) -> GoalResult:
        # Top-level planning
        plan = await self.planner.decompose(goal)
        
        results = []
        for step in plan.steps:
            agent = self.agents.get(step.agent_type)
            if not agent:
                return GoalResult(success=False, error=f"No agent for step: {step.agent_type}")
            
            # Execute step with the appropriate agent
            step_result = await agent.execute(step.sub_goal)
            results.append(step_result)
            
            # Check if step failed
            if not step_result.success:
                # Try recovery or abort
                recovery = await self._attempt_recovery(step, step_result)
                if not recovery.success:
                    return GoalResult(success=False, failed_at=step.name, partial_results=results)
        
        # Aggregate results
        return self._aggregate_results(results)
```

### 7.4 Memory-Augmented Agent Pattern

Agents with different types of memory:
- **Short-term (working memory)**: Current context, recent observations
- **Long-term**: Historical interactions, learned facts
- **Semantic**: Vector-based similarity search

```python
class MemoryAugmentedAgent:
    def __init__(self, llm: LLM, short_term: WorkingMemory, 
                 long_term: EpisodicMemory, semantic: SemanticMemory):
        self.llm = llm
        self.short_term = short_term
        self.long_term = long_term
        self.semantic = semantic
    
    async def think(self, goal: Goal) -> Thought:
        # Gather context from all memory tiers
        short_term_context = await self.short_term.get_recent(goal.conversation_id)
        long_term_context = await self.long_term.get_episodes(goal.agent_id, limit=5)
        semantic_context = await self.semantic.search(goal.query, k=5)
        
        # Combine and reason
        combined_context = self._combine_contexts(
            short_term_context,
            long_term_context,
            semantic_context
        )
        
        # LLM reasons over combined context
        thought = await self.llm.reason(goal=goal, context=combined_context)
        
        # Update memory
        await self.short_term.add(goal, thought)  # Short-term
        if thought.is_significant:
            await self.long_term.add_episode(goal, thought)  # Long-term
            await self.semantic.index(goal, thought)  # Semantic
        
        return thought

class SemanticMemory:
    """Vector-based memory for similarity search."""
    
    def __init__(self, vector_store: VectorStore, embedder: Embedder):
        self.vector_store = vector_store
        self.embedder = embedder
    
    async def search(self, query: str, k: int = 5) -> List[MemoryEntry]:
        query_embedding = await self.embedder.embed(query)
        results = await self.vector_store.search(query_embedding, k=k)
        return results
    
    async def index(self, goal: Goal, thought: Thought):
        embedding = await self.embedder.embed(str(thought))
        await self.vector_store.insert(
            vector=embedding,
            metadata={
                "goal_id": goal.id,
                "agent_id": goal.agent_id,
                "content": str(thought),
                "timestamp": datetime.now().isoformat()
            }
        )
```

### 7.5 Planning Agent Pattern

Agents that do explicit planning before execution. Different from reactive agents.

```python
class PlanningAgent:
    """Agent that builds an explicit plan before acting."""
    
    async def plan(self, goal: Goal) -> Plan:
        # Generate initial plan
        plan_steps = await self._generate_plan_steps(goal)
        
        # Validate plan
        validated_steps = await self._validate_plan(plan_steps, goal)
        
        # Optimize plan
        optimized_steps = await self._optimize_plan(validated_steps)
        
        return Plan(steps=optimized_steps, goal=goal)
    
    async def _generate_plan_steps(self, goal: Goal) -> List[PlanStep]:
        prompt = f"""
Goal: {goal.description}
Context: {goal.context}

Break down this goal into a sequence of steps. For each step, specify:
1. What to do
2. What tools/resources are needed
3. What the expected outcome is
4. Any dependencies on other steps
"""
        response = await self.llm.complete(prompt)
        return self._parse_plan_steps(response)
    
    async def _validate_plan(self, steps: List[PlanStep], goal: Goal) -> List[PlanStep]:
        """Ensure plan is feasible and complete."""
        validated = []
        for step in steps:
            # Check if step's required tools are available
            for tool_id in step.required_tools:
                if not self._is_tool_available(tool_id):
                    # Try to find alternative
                    alternative = self._find_alternative_tool(tool_id)
                    if alternative:
                        step = step.with_replacement(tool_id, alternative)
                    else:
                        raise PlanValidationError(f"Tool {tool_id} not available and no alternative")
            
            validated.append(step)
        
        return validated
```

### 7.6 Self-Correcting Agent Pattern

Agents that can identify and recover from their own errors.

```python
class SelfCorrectingAgent:
    """Agent that detects errors and adjusts behavior."""
    
    async def execute_goal(self, goal: Goal) -> GoalResult:
        step_count = 0
        corrections = 0
        
        while not self._goal_complete(goal):
            step = await self._get_next_step(goal)
            
            result = await self._execute_step(step)
            
            if self._is_step_failed(result):
                correction = await self._analyze_failure(result)
                if correction:
                    corrections += 1
                    goal = self._apply_correction(goal, correction)
                    continue
            
            step_count += 1
            
            if step_count > self.max_steps:
                return GoalResult(success=False, error="Max steps exceeded")
        
        return GoalResult(success=True, steps=step_count, corrections=corrections)
    
    async def _analyze_failure(self, result: StepResult) -> Optional[Correction]:
        prompt = f"""
Step failed: {result.action}
Error: {result.error}
Output: {result.output}

Analyze why this step failed and propose a correction.
"""
        analysis = await self.llm.complete(prompt)
        return Correction.from_llm_analysis(analysis)
```

---

<a name="8-key-insights--recommendations"></a>
## 8. Key Insights & Recommendations

### Architecture Principles for AI-Era Systems

1. **Start with the domain, not the AI**: Understand your business domain first. AI is a tool, not the architecture. DDD helps you understand where AI adds value.

2. **Treat AI outputs as untrusted input**: The anti-corruption layer pattern is essential. AI outputs need validation and translation before entering your domain model.

3. **Design for agent observability**: Since AI agents are complex and opaque, design your system to capture rich traces of agent reasoning. Event sourcing is excellent for this.

4. **Prefer event-driven for AI coordination**: AI agents work best when loosely coupled via events. This makes them easier to test, debug, and evolve.

5. **Use CQRS for AI memory**: AI systems naturally benefit from CQRS — the write side (reasoning/learning) is very different from the read side (context retrieval/memory).

6. **Start modular, extract microservices selectively**: Most AI systems benefit from starting as a modular monolith and extracting services as scale/independence requirements emerge.

7. **Plan for AI failure modes**: Unlike traditional software, AI can fail in strange ways (hallucination, prompt injection, alignment failures). Design your architecture to contain and recover from these failures.

### Specific Recommendations

- **For small teams**: Use a modular monolith with hexagonal architecture internally. Add AI as a bounded context with a clean anti-corruption layer.

- **For scaling teams**: Use bounded contexts with event-driven communication between them. Extract the AI agent as its own context with clear interfaces.

- **For complex AI systems**: Use hierarchical agents with event sourcing for observability and CQRS for memory management.

- **For research/prototyping**: Keep it simple. Use the agent loop pattern. Add complexity as requirements solidify.

---

<a name="9-references--further-reading"></a>
## 9. References & Further Reading

### Architecture Patterns
- "Fundamentals of Software Architecture" by Mark Richards & Neal Ford
- "Building Evolutionary Architectures" by Ford et al.
- "Software Architecture: The Hard Parts" by Richards et al.

### Domain-Driven Design
- "Domain-Driven Design" by Eric Evans (the blue book)
- "Implementing Domain-Driven Design" by Vaughn Vernon (the red book)
- "Domain-Driven Design Distilled" by Vaughn Vernon

### Event-Driven & Event Sourcing
- "Event-Driven Architecture in Golang" by Michael Buyd
- "Playing with Patterns" series by Martin Fowler
- "Event Sourcing" Martin Fowler's article (martinfowler.com)

### CQRS
- "CQRS" by Martin Fowler (article)
- "CQRS Journey" by Microsoft (free e-book)

### AI Agent Patterns
- "ReAct: Synergizing Reasoning and Acting in Language Models" (Yao et al.)
- "Language Agent Tree Search" (LATS) papers
- "AutoGen" documentation (Microsoft)
- "LangChain" architecture patterns
- "Semantic Kernel" documentation (Microsoft)

### 2026 Specific
- Review patterns from "Fundamentals of AI Architecture" (emerging as a field)
- AWS re:Invent and Google Next talks on AI infrastructure patterns
- Research papers on multi-agent systems (2024-2026)

---

*Document generated by Coder Agent — Architecture Deep Dive subagent*
*Research completed: 2026-04-22*
