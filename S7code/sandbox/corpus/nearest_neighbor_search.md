# Approximate Nearest Neighbor Search: Algorithms and Data Structures

Proximity queries in high-dimensional metric spaces are foundational to modern recommendation systems, image retrieval, and machine learning pipelines. Given a query point and a large collection of reference points, the goal is to find the reference points that are closest under some distance measure — the classic **k-NN problem** (k nearest neighbors).

## The Curse of Dimensionality

Exact nearest-neighbor search using brute-force distance computation scales as O(n·d) per query, where n is the database size and d is the dimensionality. In high-dimensional spaces (d > 50), tree-based indices such as KD-trees and ball trees degrade toward brute-force performance because the data increasingly concentrates on the surface of hyperspheres, making partitioning ineffective. This phenomenon is called the **curse of dimensionality**.

## Approximate Nearest Neighbor (ANN) Algorithms

Because exact retrieval is often unnecessary — a slightly suboptimal neighbor is acceptable — **approximate nearest neighbor** algorithms trade a bounded accuracy loss for dramatic speed improvements.

### Locality-Sensitive Hashing (LSH)

LSH projects points onto random hash functions that preserve proximity: nearby points collide in the same hash bucket with high probability. Query processing checks only the candidates in matching buckets. LSH offers provable accuracy guarantees but requires tuning many hyperparameters.

### Hierarchical Navigable Small World (HNSW)

HNSW constructs a multi-layer proximity graph. Each node connects to its k closest neighbors at multiple coarseness levels. During search, traversal starts at the coarsest layer and progressively descends, using greedy best-first search. HNSW achieves state-of-the-art recall-vs-throughput tradeoffs and is the default algorithm in many production systems.

### Inverted File Index (IVF)

IVF partitions the space into Voronoi cells using k-means clustering. A query first identifies the nearest cluster centroids (a coarse search), then exhaustively searches within those cells. The `nprobe` parameter controls how many cells are searched, trading recall for speed.

### Product Quantization (PQ)

PQ compresses high-dimensional vectors by splitting them into subspaces, quantizing each subspace independently. Distance computation operates in compressed space, enabling orders-of-magnitude reduction in memory footprint and faster distance computation.

## FAISS: Facebook AI Similarity Search

FAISS is the industry-standard library for large-scale proximity lookup. It implements IVF, HNSW, PQ, and combinations thereof (IVF-PQ, IVF-HNSW). FAISS supports both CPU and GPU execution, enabling searches over billion-point databases.

Key FAISS index types:
- `IndexFlatL2`: Exact brute-force Euclidean distance — used as a ground-truth baseline
- `IndexFlatIP`: Exact brute-force inner product (equivalent to cosine distance on normalized vectors)
- `IndexIVFFlat`: Inverted file with exact distance computation within cells
- `IndexHNSWFlat`: Hierarchical navigable small world graph
- `IndexIVFPQ`: IVF with product quantization compression

## Evaluation Metrics

The quality of an ANN index is measured by **recall@k**: the fraction of true k nearest neighbors returned in the top-k results. A recall@10 of 0.95 means 95% of true top-10 neighbors appear in the returned set. Production systems typically target recall@10 > 0.90 with query latency under 5ms for million-scale databases.

## Applications

- **Recommendation engines**: finding similar items or users based on latent factor embeddings
- **Semantic document retrieval**: retrieving text passages with similar meaning to a query
- **Image search**: finding visually similar images in large catalogs
- **Deduplication**: identifying near-duplicate records in large datasets
- **Anomaly detection**: identifying points far from their nearest neighbors
