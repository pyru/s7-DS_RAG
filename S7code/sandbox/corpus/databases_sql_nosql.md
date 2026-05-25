# Databases: SQL vs NoSQL Design Tradeoffs

Choosing the right database technology is one of the most consequential architectural decisions. SQL and NoSQL databases each excel in different contexts.

## Relational Databases (SQL)

Relational databases organize data into tables with predefined schemas. They guarantee ACID properties:

- **Atomicity**: Transactions succeed completely or fail completely
- **Consistency**: Database moves from one valid state to another
- **Isolation**: Concurrent transactions don't interfere
- **Durability**: Committed transactions survive failures

**When to choose SQL**:
- Complex queries with joins across multiple tables
- Data integrity and referential constraints are critical
- Reporting and analytics workloads (OLAP)
- Financial transactions requiring strict consistency

**Major SQL databases**:
- **PostgreSQL**: Full-featured, extensible (JSONB, PostGIS, pgvector), excellent for most workloads
- **MySQL/MariaDB**: Widely deployed, simpler replication, strong ecosystem
- **SQLite**: Embedded, serverless, perfect for development and edge deployments

### Indexing

Indexes dramatically speed up read queries at the cost of write overhead:

```sql
-- B-tree index (default): range queries, equality
CREATE INDEX idx_users_email ON users(email);

-- GIN index: full-text search, JSONB queries
CREATE INDEX idx_articles_fts ON articles USING GIN(to_tsvector('english', content));

-- Partial index: only index relevant rows
CREATE INDEX idx_active_users ON users(last_login) WHERE active = true;

-- Covering index: include extra columns to avoid table lookup
CREATE INDEX idx_orders_customer ON orders(customer_id) INCLUDE (total, status);
```

### Query Optimization

```sql
-- EXPLAIN ANALYZE shows actual execution plan with timing
EXPLAIN ANALYZE
SELECT u.name, COUNT(o.id) as order_count
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
WHERE u.created_at > '2024-01-01'
GROUP BY u.id
ORDER BY order_count DESC
LIMIT 10;
```

Look for: Seq Scan (may need index), Hash Join vs Nested Loop, actual vs estimated rows.

## NoSQL Databases

NoSQL databases sacrifice some ACID guarantees for flexibility, scalability, or specialized access patterns.

### Document Stores (MongoDB, Firestore)

Store JSON-like documents; flexible schema:
```json
{
  "_id": "user123",
  "name": "Alice",
  "preferences": {"theme": "dark", "notifications": true},
  "addresses": [
    {"type": "home", "city": "New York"},
    {"type": "work", "city": "Boston"}
  ]
}
```

**When to choose**: Hierarchical data, varying schemas, rapid prototyping, content management.

### Key-Value Stores (Redis, DynamoDB)

Simple: key → value. Extremely fast for direct lookups:
- Redis: In-memory, sub-millisecond latency; pub/sub, sorted sets, streams
- DynamoDB: Managed AWS service; unlimited scale with predictable performance

**When to choose**: Caching, session storage, leaderboards, simple lookups.

### Wide-Column Stores (Cassandra, HBase)

Row keys + sorted column families; optimized for time-series and IoT data:

**When to choose**: Write-heavy workloads, time-series data, multi-datacenter replication.

### Time-Series Databases (InfluxDB, TimescaleDB)

Optimized for timestamped metrics; automatic downsampling, retention policies.

## Choosing Your Database

| Factor | SQL | Document | Key-Value | Wide-Column |
|--------|-----|----------|-----------|-------------|
| Complex queries | ✓ | Limited | No | Limited |
| Flexible schema | Limited | ✓ | ✓ | ✓ |
| ACID guarantees | ✓ | Partial | Partial | Eventual |
| Horizontal scale | Hard | ✓ | ✓ | ✓ |
| Write throughput | Medium | High | Very High | Very High |
