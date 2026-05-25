# Neural Network Fundamentals

Neural networks are computational models loosely inspired by biological neurons. They learn to approximate complex functions from training examples through a process of forward propagation, loss computation, and gradient-based optimization.

## The Perceptron

A single neuron computes:
```
output = activation(w·x + b)
```
Where w is the weight vector, x is input, b is bias, and activation introduces non-linearity.

Common activation functions:
- **ReLU**: max(0, x) — fast, sparse activations, avoids vanishing gradient
- **Sigmoid**: 1/(1+e⁻ˣ) — maps to (0,1), used in binary classification outputs
- **Tanh**: (eˣ-e⁻ˣ)/(eˣ+e⁻ˣ) — maps to (-1,1), zero-centered
- **SoftMax**: exp(xᵢ)/Σ exp(xⱼ) — converts logits to probabilities
- **GELU**: Gaussian Error Linear Unit — used in BERT, GPT

## Multilayer Perceptron (MLP)

Stacked layers of neurons enable learning non-linear decision boundaries:

```python
import torch.nn as nn

model = nn.Sequential(
    nn.Linear(784, 256),   # Input layer: 784 pixels → 256 hidden
    nn.ReLU(),
    nn.Dropout(0.2),
    nn.Linear(256, 128),   # Hidden layer
    nn.ReLU(),
    nn.Linear(128, 10),    # Output: 10 classes
)
```

Universal approximation theorem: A network with one hidden layer and sufficient neurons can approximate any continuous function.

## Forward Propagation

```
Layer 1: h₁ = ReLU(W₁x + b₁)
Layer 2: h₂ = ReLU(W₂h₁ + b₂)
Output:  ŷ = SoftMax(W₃h₂ + b₃)
```

## Backpropagation

Backpropagation efficiently computes gradients via the chain rule, propagating error signal from output to input:

```
∂L/∂W₁ = ∂L/∂ŷ · ∂ŷ/∂h₂ · ∂h₂/∂h₁ · ∂h₁/∂W₁
```

PyTorch tracks operations and automatically computes gradients:
```python
loss = criterion(output, target)
loss.backward()  # Computes all gradients
optimizer.step() # Updates weights
optimizer.zero_grad()  # Clear gradients for next step
```

## Loss Functions

**Cross-entropy** (classification):
```
L = -Σᵢ yᵢ log(ŷᵢ)
```

**Mean Squared Error** (regression):
```
L = (1/n) Σ(y - ŷ)²
```

**Binary Cross-Entropy** (binary classification or multi-label):
```
L = -(y log(ŷ) + (1-y) log(1-ŷ))
```

## Optimization Algorithms

**Gradient Descent variants**:
- **SGD**: Update after each example; noisy but fast
- **Mini-batch SGD**: Update after k examples (k=32–256 typically)
- **Momentum**: Add fraction of previous update to reduce oscillation

**Adaptive methods**:
- **Adam**: Maintains per-parameter adaptive learning rates (m₁=0.9, m₂=0.999)
- **AdamW**: Adam with correct weight decay (decoupled from gradient updates)
- **Adafactor**: Memory-efficient for large models

## Regularization

**Dropout**: Randomly zero out neurons during training (p=0.1–0.5). Forces redundant learning; prevents co-adaptation.

**Weight decay** (L2): Add λ‖W‖² to loss; shrinks weights toward zero.

**Batch normalization**: Normalize layer inputs to unit mean/variance; accelerates training, allows higher learning rates.

**Layer normalization**: Normalize across features (not batch); standard in transformers.

## Training Tricks

- **Learning rate scheduling**: Cosine annealing, warm-up + linear decay
- **Gradient clipping**: cap gradient norm to prevent exploding gradients
- **Mixed precision** (fp16/bf16): 2× memory reduction, 2-3× training speedup
- **Gradient checkpointing**: Recompute activations during backward pass to save memory
