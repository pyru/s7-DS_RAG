# Microservices Architecture Patterns

Microservices decompose a monolithic application into small, independently deployable services. Each service owns its data, exposes an API, and can be developed, deployed, and scaled independently.

## Core Characteristics

A microservice should:
- Be responsible for a **single business capability** (e.g., user management, order processing)
- Own its own **database** (no shared database schema between services)
- Communicate via **APIs** (REST, gRPC) or **events** (message queues)
- Be deployable independently without coordinating with other services
- Be small enough that one team can understand and own it completely

## Inter-Service Communication

### Synchronous (REST/gRPC)

Direct request-response communication — simple but creates coupling:

```python
# API Gateway calls Order Service
import httpx

async def create_order(user_id: int, items: list) -> dict:
    # Validate user exists (synchronous call)
    user_resp = await httpx.get(f"http://user-service/users/{user_id}")
    if user_resp.status_code != 200:
        raise UserNotFound(user_id)
    
    # Create order
    order_resp = await httpx.post("http://order-service/orders", json={
        "user_id": user_id, "items": items
    })
    return order_resp.json()
```

**gRPC** provides type-safe, binary-protocol communication with streaming support. Ideal for high-throughput internal service calls.

### Asynchronous (Event-Driven)

Publish events to a message broker; services react independently:

```python
# Order Service publishes event
await kafka_producer.send("order.created", {
    "order_id": order.id,
    "user_id": order.user_id,
    "amount": order.total,
})

# Notification Service consumes event
async for message in kafka_consumer:
    event = json.loads(message.value)
    await send_confirmation_email(event["user_id"], event["order_id"])

# Inventory Service consumes same event
async for message in kafka_consumer:
    event = json.loads(message.value)
    await reserve_inventory(event["items"])
```

## Service Mesh

A service mesh (Istio, Linkerd) handles cross-cutting concerns at the infrastructure level:
- **mTLS**: Mutual TLS between all services
- **Circuit breaker**: Automatically stop calling failing services
- **Retry and timeout**: Configurable without code changes
- **Observability**: Automatic distributed tracing and metrics

## API Gateway Pattern

A single entry point for all client requests:

```
Client → API Gateway → [User Service]
                     → [Order Service]
                     → [Product Service]
```

API Gateway handles: authentication, rate limiting, request routing, response aggregation, SSL termination.

## Circuit Breaker

Prevents cascade failures when a service is down:

```python
from circuitbreaker import circuit

@circuit(failure_threshold=5, recovery_timeout=30, expected_exception=httpx.HTTPError)
async def call_user_service(user_id: int):
    response = await httpx.get(f"http://user-service/users/{user_id}", timeout=2.0)
    response.raise_for_status()
    return response.json()
```

States: CLOSED (normal) → OPEN (failing, return fallback) → HALF-OPEN (test recovery)

## Saga Pattern for Distributed Transactions

When a business transaction spans multiple services:

**Choreography**: Services publish events and react to other services' events
**Orchestration**: A central saga coordinator sends commands to services

```
Order Saga Orchestrator:
1. → Reserve inventory (Inventory Service)
   ← Inventory reserved
2. → Charge payment (Payment Service)
   ← Payment processed
3. → Update order status (Order Service)
   ← Order confirmed

If step 2 fails:
3. → Release inventory (Inventory Service) [compensating transaction]
```

## Observability

Three pillars essential for microservices:

**Structured Logging** (JSON):
```python
import structlog
log = structlog.get_logger()
log.info("order.created", order_id=order.id, user_id=user.id, amount=order.total)
```

**Metrics** (Prometheus):
```python
from prometheus_client import Counter, Histogram
order_count = Counter('orders_total', 'Total orders', ['status'])
order_duration = Histogram('order_processing_seconds', 'Order processing time')
```

**Distributed Tracing** (OpenTelemetry):
```python
from opentelemetry import trace
tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("create_order") as span:
    span.set_attribute("user.id", user_id)
    result = await process_order(order)
```
