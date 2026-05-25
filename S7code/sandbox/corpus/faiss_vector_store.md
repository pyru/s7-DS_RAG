# FAISS: Facebook AI Similarity Search

FAISS (Facebook AI Similarity Search) is an open-source library developed by Meta AI Research for efficient similarity search and clustering of dense vectors. It is the most widely deployed library for large-scale approximate nearest neighbor (ANN) search, supporting billion-scale databases.

## Core Design

FAISS is written in C++ with Python bindings. It optimizes for:
- **Throughput**: millions of queries per second using SIMD vectorization and GPU acceleration
- **Memory efficiency**: compressed indices that fit massive vector databases in RAM
- **Flexibility**: dozens of index types covering exact, approximate, compressed, and GPU-based search

## Index Types

### Flat Indices (Exact Search)
- `IndexFlatL2`: Brute-force L2 (Euclidean) distance
- `IndexFlatIP`: Brute-force inner product (cosine on normalized vectors)

These produce exact results but scale linearly with database size. Suitable for databases up to ~1M vectors.

### IVF (Inverted File Index)
IVF partitions vectors into `nlist` Voronoi cells via k-means. Queries search only `nprobe` cells:

```python
quantizer = faiss.IndexFlatL2(d)
index = faiss.IndexIVFFlat(quantizer, d, nlist=100)
index.train(xb)   # Required for IVF
index.add(xb)
D, I = index.search(xq, k=10, nprobe=10)
```

Typical settings: nlist = 4√n, nprobe = nlist/10.

### HNSW (Hierarchical Navigable Small World)
HNSW builds a multi-layer proximity graph. Excellent recall-speed tradeoff:

```python
index = faiss.IndexHNSWFlat(d, M=32)  # M: connections per node
```

HNSW does not require training and supports incremental insertion. It achieves state-of-the-art performance at recall@1 > 0.99 with ~1ms latency on million-scale databases.

### PQ (Product Quantization)
PQ compresses vectors by splitting into m subspaces and quantizing each:

```python
index = faiss.IndexPQ(d, m=8, nbits=8)  # 8 subspaces, 256 centroids each
```

Reduces memory by 8-32× at the cost of ~2–5% recall loss.

### IVF + PQ (Combined)
The most common production configuration:

```python
index = faiss.index_factory(d, "IVF1024,PQ16")
```

## Persistence

FAISS indices are serialized to disk:

```python
faiss.write_index(index, "index.faiss")
index = faiss.read_index("index.faiss")
```

The loaded index is immediately queryable without retraining. Memory-mapped mode (`read_index(..., mmap=True)`) loads only accessed pages, enabling indices larger than RAM.

## GPU Acceleration

A single GPU can achieve 100× speedup over CPU for flat indices:

```python
res = faiss.StandardGpuResources()
gpu_index = faiss.index_cpu_to_gpu(res, 0, cpu_index)
```

## Cosine Similarity vs L2

For cosine similarity, L2-normalize vectors before adding to an `IndexFlatIP`:

```python
faiss.normalize_L2(vectors)  # In-place normalization
index = faiss.IndexFlatIP(d)
index.add(vectors)
```

After normalization, inner product = cosine similarity.

## Integration with RAG

In a RAG system, FAISS stores dense embeddings of document chunks:
1. Encode chunks with a sentence transformer model
2. Add embeddings to FAISS index with `index.add(embeddings)`
3. At query time, encode the query and search: `D, I = index.search(query_embedding, k=5)`
4. Map result indices back to original chunks via a parallel list

The state directory in agent7 contains `index.faiss` and `index_ids.json` for this mapping.
