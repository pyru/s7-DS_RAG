# Distributed Systems Fundamentals

Distributed systems are collections of independent computers that appear to users as a single coherent system. They enable horizontal scaling, fault tolerance, and geographic distribution — but introduce fundamental challenges around consistency, availability, and coordination.

## The CAP Theorem

The CAP theorem (Brewer, 2000; proven by Gilbert and Lynch, 2002) states that a distributed data store can guarantee at most two of three properties simultaneously:

- **Consistency (C)**: Every read receives the most recent write or an error
- **Availability (A)**: Every request receives a response (not necessarily the most recent)
- **Partition Tolerance (P)**: The system continues operating despite network partitions

In practice, network partitions are unavoidable, so the real tradeoff is **CP vs AP**:
- CP systems (HBase, Zookeeper, MongoDB in strong mode): Return errors during partitions rather than stale data
- AP systems (Cassandra, CouchDB, DynamoDB): Return potentially stale data during partitions

## Consistency Models

From strongest to weakest:

**Linearizability**: Operations appear to take effect instantaneously at some point between their invocation and response. The strongest and most expensive guarantee.

**Sequential consistency**: All nodes see operations in the same order, but not necessarily real-time order.

**Causal consistency**: Operations that are causally related are seen in the correct order; concurrent operations may be seen in different orders.

**Eventual consistency**: Given no new updates, all replicas will eventually converge to the same value. Amazon Dynamo popularized this model.

## Consensus Algorithms

Distributed consensus — getting multiple nodes to agree on a value — is the fundamental problem of distributed computing.

**Paxos**: The canonical consensus algorithm. Complex but provably correct. Used in Google Chubby lock service.

**Raft**: Designed for understandability. Separates consensus into leader election, log replication, and safety. Used in etcd (Kubernetes), CockroachDB, TiKV.

**ZAB (Zookeeper Atomic Broadcast)**: Used in Apache Zookeeper for leader election and state machine replication.

## Replication Strategies

**Single-leader replication**: One leader handles writes; followers replicate asynchronously. Simple but leader is a bottleneck and single point of failure.

**Multi-leader replication**: Multiple leaders accept writes; useful for multi-datacenter deployments. Requires conflict resolution.

**Leaderless replication** (Dynamo-style): Clients write to multiple nodes (quorum writes) and read from multiple nodes (quorum reads). W + R > N guarantees overlap with at least one up-to-date node.

## Distributed Transactions

**Two-Phase Commit (2PC)**: Coordinator sends "prepare" to all participants; if all agree, sends "commit." Blocking: coordinator failure leaves participants locked.

**Saga pattern**: Long-running transactions as sequences of local transactions with compensating transactions for rollback. Used in microservices.

**CRDT (Conflict-free Replicated Data Types)**: Data structures that can be merged without conflicts — counters, sets, sequences, maps. Enable strong eventual consistency without coordination.

## Observability

Distributed systems require three pillars of observability:
- **Logs**: Structured event records (ELK stack, Loki)
- **Metrics**: Time-series numerical data (Prometheus, Datadog)
- **Traces**: Request flow across services (Jaeger, Zipkin, OpenTelemetry)

Distributed tracing propagates trace IDs across service boundaries to reconstruct the full call graph for a single request.
