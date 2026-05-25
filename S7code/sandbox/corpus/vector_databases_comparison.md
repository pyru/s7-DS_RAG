# Vector Databases: A Comparison

Vector databases are purpose-built for storing, indexing, and querying high-dimensional embeddings. Unlike traditional relational or document databases, they optimize for semantic similarity search rather than exact match retrieval. This guide compares the major players in the vector database ecosystem.

## What Makes a Vector Database?

A vector database must provide:
1. **Efficient ANN indexing**: HNSW, IVF, or similar indices for fast similarity search
2. **Metadata filtering**: Combine vector search with traditional field filters
3. **CRUD operations**: Add, update, delete vectors with associated metadata
4. **Persistence and replication**: Durable storage with high availability
5. **Scalability**: Handle billions of vectors with horizontal scaling

## Pinecone

**Type**: Fully managed cloud service  
**Strengths**: Zero infrastructure management, automatic scaling, production-ready from day one  
**Weaknesses**: Vendor lock-in, cost at scale, latency variability  
**Best for**: Teams that want to ship quickly without managing infrastructure

```python
import pinecone
pinecone.init(api_key="...", environment="us-east-1-aws")
index = pinecone.Index("my-index")
index.upsert(vectors=[("id1", [0.1, 0.2, ...], {"text": "..."})]) 
results = index.query(vector=[0.1, 0.2, ...], top_k=10, include_metadata=True)
```

## Weaviate

**Type**: Open-source, self-hosted or cloud  
**Strengths**: Native GraphQL API, multi-modal support, hybrid search built-in, module ecosystem  
**Weaknesses**: Higher resource requirements, complex configuration  
**Best for**: Complex data models with rich metadata and multi-modal search

## Qdrant

**Type**: Open-source, self-hosted or cloud  
**Strengths**: Written in Rust (excellent performance), rich filtering, sparse vector support, payload indexing  
**Weaknesses**: Smaller ecosystem than competitors  
**Best for**: Performance-critical applications with complex filtering requirements

```python
from qdrant_client import QdrantClient
client = QdrantClient(":memory:")
client.create_collection("docs", vectors_config=VectorParams(size=384, distance=Distance.COSINE))
client.upsert("docs", points=[PointStruct(id=1, vector=[...], payload={"text": "..."})])
results = client.search("docs", query_vector=[...], limit=10)
```

## Chroma

**Type**: Open-source, embedded or server  
**Strengths**: Python-native, dead-simple API, perfect for prototyping and development  
**Weaknesses**: Limited production features, early scalability ceiling  
**Best for**: Prototyping RAG applications, small-to-medium datasets

```python
import chromadb
client = chromadb.Client()
collection = client.create_collection("docs")
collection.add(documents=["text..."], ids=["id1"])
results = collection.query(query_texts=["search query"], n_results=5)
```

## pgvector

**Type**: PostgreSQL extension  
**Strengths**: Leverages existing PostgreSQL infrastructure, SQL joins with vector search, ACID compliance  
**Weaknesses**: Not optimized for very large scales (>100M vectors), sequential scan fallback  
**Best for**: Teams already using PostgreSQL who want to add vector search without a new service

## FAISS (Library, not a database)

FAISS is a library, not a database — it has no server, persistence layer, or metadata. But it is the underlying algorithm inside many vector databases and the go-to choice for:
- Research and experimentation
- Applications with custom persistence requirements
- Maximum control over the index type and parameters

## Selection Guide

| Requirement | Recommendation |
|-------------|----------------|
| Prototype quickly | Chroma |
| Production managed | Pinecone |
| Self-hosted, complex filtering | Qdrant |
| Multi-modal, GraphQL | Weaviate |
| PostgreSQL integration | pgvector |
| Maximum control | FAISS directly |
