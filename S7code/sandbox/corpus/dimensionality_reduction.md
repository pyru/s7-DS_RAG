# Dimensionality Reduction: PCA, t-SNE, and UMAP

High-dimensional data is difficult to visualize and computationally expensive to process. Dimensionality reduction maps data from high-dimensional space to lower dimensions while preserving important structure.

## Principal Component Analysis (PCA)

PCA finds orthogonal directions (principal components) that maximize variance. It is a linear transformation.

**Algorithm**:
1. Center data: X ← X - mean(X)
2. Compute covariance matrix: C = (1/n)XᵀX
3. Eigendecompose: C = QΛQᵀ
4. Sort eigenvectors by eigenvalue (descending)
5. Project: X_reduced = X · Q[:, :k]

```python
from sklearn.decomposition import PCA
import numpy as np

X = np.random.randn(1000, 50)  # 1000 samples, 50 features

pca = PCA(n_components=2)
X_2d = pca.fit_transform(X)

# Variance explained by each component
print(pca.explained_variance_ratio_)  # e.g., [0.12, 0.09]
print(pca.explained_variance_ratio_.sum())  # Total variance retained

# Using SVD directly (more numerically stable)
U, S, Vt = np.linalg.svd(X - X.mean(axis=0), full_matrices=False)
X_2d = U[:, :2] * S[:2]  # Equivalent to PCA projection
```

**When to use PCA**:
- Feature preprocessing before ML algorithms
- Visualization (reduce to 2-3D)
- Noise reduction (discard low-variance components)
- Compressed representations of embeddings

**Limitations**: Linear only — misses non-linear structure (concentric rings, swiss roll manifold).

## t-SNE: t-Distributed Stochastic Neighbor Embedding

t-SNE (van der Maaten & Hinton, 2008) is a non-linear method optimized for visualization:

1. Compute pairwise similarities in high-dimensional space (Gaussian kernel)
2. Initialize low-dimensional embedding (often with PCA)
3. Optimize embedding to minimize KL divergence between high-D and low-D similarity distributions
4. Use Student-t distribution in low-D to combat "crowding problem"

```python
from sklearn.manifold import TSNE

tsne = TSNE(n_components=2, perplexity=30, learning_rate='auto', 
            init='pca', random_state=42, n_iter=1000)
X_2d = tsne.fit_transform(X)
```

**Key hyperparameter — perplexity**: Roughly the number of effective neighbors (5-50 typical). Low perplexity → local structure; high perplexity → global structure.

**Critical limitations**:
- No transform method (must re-run for new data)
- Global structure may be distorted (cluster distances not meaningful)
- Not suitable for distances or nearest-neighbor retrieval
- Slow: O(n log n) with Barnes-Hut approximation

## UMAP: Uniform Manifold Approximation and Projection

UMAP (McInnes et al., 2018) addresses t-SNE's limitations:
- Preserves both local AND global structure better
- Orders of magnitude faster than t-SNE
- Supports out-of-sample transform (transform new data after fitting)
- Theoretically grounded in Riemannian geometry

```python
import umap

reducer = umap.UMAP(n_components=2, n_neighbors=15, min_dist=0.1, 
                    metric='cosine', random_state=42)
reducer.fit(X_train)
X_2d = reducer.transform(X_test)  # Works on new data!
```

**Key hyperparameters**:
- `n_neighbors`: Local neighborhood size (5-50 typical). Small → local; large → global
- `min_dist`: Minimum distance in embedded space. Small → tight clusters; large → spread out
- `metric`: Distance metric; 'cosine' works well for text embeddings

## Comparison Summary

| Method | Non-linear | Speed | New Points | Preserves Global | Use Case |
|--------|-----------|-------|------------|-----------------|----------|
| PCA | No | Fastest | Yes | Yes | Feature reduction, noise removal |
| t-SNE | Yes | Slow | No | Partially | Publication-quality visualization |
| UMAP | Yes | Fast | Yes | Yes | Interactive visualization, preprocessing |

## Applications in RAG

For large vector stores (100K+ embeddings):
1. Visualize document embeddings with UMAP to verify clustering
2. Use PCA to reduce from 768D to 128D before FAISS (2-3% recall loss, 6× faster)
3. Identify outlier documents that are far from all clusters (potential noise)
