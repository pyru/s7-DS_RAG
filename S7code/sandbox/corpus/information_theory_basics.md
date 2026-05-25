# Information Theory Fundamentals

Information theory, founded by Claude Shannon in 1948, provides the mathematical foundation for understanding communication, compression, and uncertainty. Its core concepts permeate machine learning, cryptography, statistics, and coding theory.

## Entropy: Measuring Uncertainty

The **Shannon entropy** H(X) of a discrete random variable X measures the average uncertainty (or information content) of its outcomes:

H(X) = -∑ᵢ p(xᵢ) log₂ p(xᵢ)

Properties:
- H(X) ≥ 0 always
- H(X) = 0 when one outcome has probability 1 (no uncertainty)
- H(X) is maximized when all outcomes are equally likely (uniform distribution)
- For a fair coin: H = -(0.5 log₂ 0.5 + 0.5 log₂ 0.5) = 1 bit
- For a fair die: H = -6(1/6 · log₂ 1/6) ≈ 2.585 bits

## Joint Entropy and Conditional Entropy

**Joint entropy**: uncertainty of two variables together
H(X,Y) = -∑ p(x,y) log₂ p(x,y)

**Conditional entropy**: uncertainty of Y given X is known
H(Y|X) = H(X,Y) - H(X)

Chain rule: H(X,Y) = H(X) + H(Y|X)

If X and Y are independent: H(Y|X) = H(Y) — knowing X tells us nothing about Y.

## Mutual Information

Mutual information I(X;Y) quantifies how much knowing one variable reduces uncertainty about another:

I(X;Y) = H(X) - H(X|Y) = H(Y) - H(Y|X) = H(X) + H(Y) - H(X,Y)

Properties:
- I(X;Y) ≥ 0
- I(X;Y) = 0 iff X and Y are independent
- I(X;Y) = H(X) iff X is fully determined by Y

Mutual information is widely used in feature selection (select features maximally informative about the label), neuroscience (measure stimulus-response relationships), and network analysis.

## KL Divergence

The Kullback-Leibler divergence measures how much probability distribution P differs from reference distribution Q:

D_KL(P||Q) = ∑ P(x) log(P(x)/Q(x))

Properties:
- D_KL(P||Q) ≥ 0 (Gibbs' inequality)
- D_KL(P||Q) = 0 iff P = Q
- Asymmetric: D_KL(P||Q) ≠ D_KL(Q||P)

KL divergence appears in variational inference, VAE loss functions, and reinforcement learning (as a penalty in RLHF/PPO).

## Cross-Entropy

Cross-entropy H(P,Q) is the average number of bits needed to encode samples from P using a code optimized for Q:

H(P,Q) = -∑ P(x) log₂ Q(x) = H(P) + D_KL(P||Q)

In machine learning, cross-entropy loss is the standard classification loss where P is the true distribution (one-hot labels) and Q is the model's predicted distribution.

## Channel Capacity

A noisy channel with input X and output Y has capacity:
C = max_{P(X)} I(X;Y) bits/channel use

Shannon's coding theorem: reliable communication is possible at any rate R < C, and impossible for R > C.

## Data Compression

The **source coding theorem** states that the minimum expected code length for a source with entropy H is H bits per symbol. Practical compression algorithms approach this limit:
- Huffman coding: optimal prefix-free code, within 1 bit of entropy
- Arithmetic coding: approaches entropy limit arbitrarily closely
- LZ77/DEFLATE (used in gzip/PNG): achieves near-theoretical rates on real data
- Neural compressors (HiFiC, MS-ILLM): approach or exceed traditional limits for images

## Applications in Machine Learning

- **Training**: cross-entropy loss for classification
- **Variational autoencoders**: ELBO = reconstruction - KL term
- **Information bottleneck**: optimal representation compresses X while preserving information about Y
- **Mutual information neural estimation (MINE)**: estimate MI via neural networks
- **Data augmentation**: preserve task-relevant information while varying task-irrelevant factors
