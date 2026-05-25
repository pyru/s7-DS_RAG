# Linear Algebra for Machine Learning

Linear algebra is the mathematical foundation of machine learning. Every neural network forward pass, every PCA decomposition, every embedding similarity computation relies on matrix and vector operations.

## Vectors and Spaces

A vector v ∈ ℝⁿ is an n-dimensional point. Key properties:
- **Norm**: ‖v‖₂ = √(Σ vᵢ²) — vector magnitude
- **Unit vector**: ‖v‖ = 1 — normalize by v / ‖v‖
- **Dot product**: v·w = Σ vᵢwᵢ = ‖v‖‖w‖cos(θ)

The dot product is the basis of all similarity computation in ML. When vectors are L2-normalized, dot product equals cosine similarity — the measure FAISS uses in inner product indices.

## Matrix Operations

```python
import numpy as np

A = np.array([[1, 2], [3, 4]])
B = np.array([[5, 6], [7, 8]])

# Matrix multiplication (not element-wise)
C = A @ B  # = np.matmul(A, B)
# [[19, 22], [43, 50]]

# Element-wise
D = A * B  # [[5, 12], [21, 32]]

# Transpose
A_T = A.T  # [[1, 3], [2, 4]]

# Inverse (when exists)
A_inv = np.linalg.inv(A)  # A @ A_inv = Identity
```

## Eigendecomposition

For a square matrix A, eigenvalues λ and eigenvectors v satisfy:
```
Av = λv
```

Eigendecomposition: A = QΛQ⁻¹ where Q contains eigenvectors and Λ is diagonal with eigenvalues.

**Applications**:
- PCA: Eigenvectors of the covariance matrix are principal components
- PageRank: Largest eigenvector of the link matrix gives page importance scores
- Graph Laplacian: Eigenvectors reveal community structure

```python
eigenvalues, eigenvectors = np.linalg.eig(A)
```

## Singular Value Decomposition (SVD)

Every matrix M ∈ ℝ^(m×n) can be decomposed as:
```
M = UΣVᵀ
```
Where U (m×m) and V (n×n) are orthogonal matrices, Σ is diagonal with singular values.

**Applications**:
- **PCA**: SVD of centered data matrix gives principal components
- **Recommendation systems** (collaborative filtering): Factorize user-item matrix
- **Low-rank approximation**: Keep top-k singular values to compress matrix
- **Pseudoinverse**: M⁺ = VΣ⁺Uᵀ — enables least-squares solutions to overdetermined systems

```python
U, S, Vt = np.linalg.svd(M, full_matrices=False)
# Low-rank approximation keeping k components
k = 50
M_approx = U[:, :k] @ np.diag(S[:k]) @ Vt[:k, :]
```

## Gradient as a Vector

In optimization, the gradient ∇f(x) is the vector of partial derivatives — points in the direction of steepest ascent. Gradient descent follows -∇f:

```
x ← x - η∇f(x)
```

The Hessian H = ∇²f (matrix of second derivatives) describes the curvature of the loss landscape. Newton's method uses the Hessian for faster convergence: x ← x - H⁻¹∇f(x).

## Attention as Matrix Operations

The transformer's attention mechanism is a matrix operation:

```python
def attention(Q, K, V, mask=None):
    d_k = Q.shape[-1]
    scores = Q @ K.transpose(-2, -1) / np.sqrt(d_k)  # [batch, heads, seq, seq]
    if mask is not None:
        scores = scores.masked_fill(mask == 0, -1e9)
    weights = softmax(scores, dim=-1)
    return weights @ V  # [batch, heads, seq, d_v]
```

This is: scaled dot-product attention = softmax(QKᵀ/√dₖ)V — pure matrix multiplication.

## Batch Processing Efficiency

GPUs excel at large matrix multiplications due to SIMD parallelism:
- 1000 sequential matrix multiplications: slow
- One batched matmul [1000, m, n] × [1000, n, k]: 100-1000× faster

Always prefer batched operations over loops in NumPy/PyTorch/JAX.
