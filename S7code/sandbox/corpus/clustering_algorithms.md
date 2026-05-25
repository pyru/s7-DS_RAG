# Clustering Algorithms: Unsupervised Pattern Discovery

Clustering groups similar data points without labeled data, revealing hidden structure in datasets. Applications include customer segmentation, anomaly detection, document organization, and gene expression analysis.

## K-Means Clustering

K-means partitions n points into k clusters by minimizing within-cluster sum of squares:

**Algorithm**:
1. Initialize k centroids (random or k-means++ for better initialization)
2. Assign each point to nearest centroid
3. Update each centroid to mean of its assigned points
4. Repeat 2-3 until convergence

```python
from sklearn.cluster import KMeans
import numpy as np

X = np.random.randn(1000, 2)
kmeans = KMeans(n_clusters=5, init='k-means++', n_init=10, random_state=42)
labels = kmeans.fit_predict(X)
centroids = kmeans.cluster_centers_
inertia = kmeans.inertia_  # Within-cluster sum of squares
```

**Choosing k**: Elbow method (plot inertia vs k), Silhouette score, Gap statistic.

**Limitations**:
- Assumes spherical clusters of similar size
- Sensitive to outliers (centroids pulled toward them)
- Must specify k in advance

## DBSCAN: Density-Based Clustering

DBSCAN discovers arbitrarily shaped clusters without specifying k:

**Core concepts**:
- **Core point**: Has at least min_samples points within radius epsilon
- **Border point**: Within epsilon of a core point but not core itself
- **Noise point**: Neither core nor border — treated as outlier

```python
from sklearn.cluster import DBSCAN

dbscan = DBSCAN(eps=0.5, min_samples=5)
labels = dbscan.fit_predict(X)
# labels == -1 → noise points (outliers)
n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
```

**Strengths**: Handles arbitrary shapes, identifies outliers, no need to specify k
**Weaknesses**: Struggles with varying density; eps and min_samples are sensitive

## Hierarchical Clustering

Agglomerative hierarchical clustering builds a dendrogram (tree) of merges:

1. Start: Each point is its own cluster
2. Merge: Combine the two most similar clusters
3. Repeat until all points in one cluster

Linkage criteria:
- **Single linkage**: Distance between nearest points (chaining tendency)
- **Complete linkage**: Distance between farthest points (compact clusters)
- **Average linkage**: Average of all pairwise distances (balanced)
- **Ward's linkage**: Minimize increase in total within-cluster variance

```python
from sklearn.cluster import AgglomerativeClustering
from scipy.cluster.hierarchy import dendrogram, linkage

Z = linkage(X, method='ward')
# Plot dendrogram to choose cut point
labels = AgglomerativeClustering(n_clusters=5, linkage='ward').fit_predict(X)
```

## Gaussian Mixture Models (GMM)

GMM models data as a mixture of k Gaussian distributions, estimated via Expectation-Maximization:

```python
from sklearn.mixture import GaussianMixture

gmm = GaussianMixture(n_components=5, covariance_type='full', random_state=42)
gmm.fit(X)
labels = gmm.predict(X)
probs = gmm.predict_proba(X)  # Soft assignments — point belongs to cluster 3 with probability 0.85
```

GMM is more flexible than k-means: clusters can have different sizes, shapes, and orientations. Enables soft cluster assignments.

## Evaluation Metrics

**When ground truth is available**:
- Adjusted Rand Index (ARI): 1.0 = perfect match, 0 = random
- Normalized Mutual Information (NMI)
- Adjusted Mutual Information (AMI)

**When ground truth is unavailable**:
- **Silhouette score**: Mean (within-cluster cohesion - nearest-cluster separation) / max. Range [-1, 1]; higher is better
- **Davies-Bouldin index**: Lower is better (avg similarity of each cluster to its most similar other)
- **Calinski-Harabasz index**: Higher is better (ratio of between-cluster to within-cluster dispersion)

## Clustering for RAG: Document Organization

In retrieval systems, clustering is used to:
1. Group similar documents for efficient navigation
2. Create hierarchical topic indices
3. Initialize IVF centroids in FAISS
4. Discover latent topics without labeled data (similar to LDA topic modeling)
