# Event-Driven Architecture and Non-Blocking I/O

Event-driven architecture (EDA) is a software design paradigm where program flow is determined by events — signals from users, sensors, messages, or other programs. Rather than sequentially executing blocking operations, an event-driven program registers callbacks and yields control until events arrive. This pattern is fundamental to modern high-performance networked applications.

## The Reactor Pattern

The **reactor pattern** is the canonical design for single-threaded event-driven systems. A central **event dispatcher** (or reactor) monitors a set of I/O handles (file descriptors, sockets) for readiness events. When a handle becomes readable or writable, the reactor invokes the registered callback.

Key components:
- **Event dispatcher**: polls I/O handles via `select()`, `epoll()`, or `kqueue()`
- **Event handler**: a callback invoked when its registered event fires
- **Resource handle**: a socket, file, or timer that generates events

Node.js is built entirely on this pattern using libuv. Nginx processes thousands of simultaneous connections using a small number of event loops, far outperforming thread-per-connection servers at high concurrency.

## Non-Blocking I/O

Traditionally, I/O operations block the calling thread until completion. A `read()` call on a socket may wait hundreds of milliseconds for data. In a non-blocking model, I/O calls return immediately with `EAGAIN` if data is not available, allowing the calling code to perform other work.

The non-blocking paradigm transforms sequential code:
```
# Blocking (thread sleeps waiting for network)
data = socket.recv(1024)  # Thread blocked for 200ms

# Non-blocking (returns to event loop immediately)
def on_data_ready(data):   # Called when data arrives
    process(data)
register_callback(socket, on_data_ready)
```

## Callback Chains and Callback Hell

Non-blocking code traditionally uses nested callbacks, which creates deeply nested, hard-to-follow code often called "callback hell":

```javascript
fetch(url1, function(result1) {
    fetch(url2(result1), function(result2) {
        fetch(url3(result2), function(result3) {
            // deeply nested...
        });
    });
});
```

This pattern makes error handling and composition difficult. Promises (and later async/await) were invented specifically to flatten callback chains into sequential-looking code.

## Proactor Pattern

The **proactor pattern** extends reactor for asynchronous I/O operations that initiate in the background and notify completion rather than readiness. Windows IOCP (I/O Completion Ports) uses this model. Rust's `tokio` runtime implements proactor-style async I/O.

## Message Queues and Event Streaming

In distributed systems, event-driven architecture scales via **message brokers**:
- **Apache Kafka**: durable log-structured event streaming, millions of events/second
- **RabbitMQ**: AMQP-based message queuing with flexible routing
- **Redis Streams**: lightweight ordered event log with consumer groups

Publishers emit events without knowing subscribers. Subscribers consume events independently, enabling decoupled, scalable microservice architectures.

## Back-Pressure

In pipelines where consumers are slower than producers, **back-pressure** mechanisms prevent memory exhaustion by signaling producers to slow down. Reactive Streams (RxJava, Akka Streams) formalize back-pressure as a first-class concept.

## Connection Between EDA and Concurrent Execution

Event-driven execution enables high concurrency without multiple operating system threads. A single execution context handles thousands of simultaneous I/O operations by interleaving their execution around natural suspension points. This approach reduces context-switching overhead, thread synchronization costs, and memory usage compared to one-thread-per-connection models. The trade-off is that CPU-intensive operations must be explicitly delegated to worker threads or processes to avoid blocking the event dispatcher.
