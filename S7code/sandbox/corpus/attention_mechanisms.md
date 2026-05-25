# Attention Mechanisms: From Bahdanau to Flash Attention

Attention mechanisms allow neural networks to focus on relevant parts of the input when producing each output element, rather than compressing the entire input into a fixed-size vector. This breakthrough enabled long-document understanding and is the core innovation in transformers.

## The Problem: Fixed-Size Bottleneck

Early sequence-to-sequence models (Sutskever et al., 2014) compressed an entire input sequence into a single fixed-size context vector, losing information for long sequences. Translation quality degraded for sentences longer than ~30 words.

## Bahdanau Attention (2015)

Bahdanau et al. introduced **additive attention** that computes a context vector as a weighted sum of all encoder hidden states:

```
e_ij = v^T tanh(W_s s_{i-1} + W_h h_j)    # Alignment score
α_ij = softmax(e_ij)                          # Attention weights
c_i = Σ_j α_ij h_j                          # Context vector
```

The decoder can attend to any encoder position at each decoding step — enabling alignment learning without explicit supervision.

## Luong Attention (2015)

Luong et al. proposed simpler **multiplicative (dot-product) attention**:

```
score(s_i, h_j) = s_i^T h_j    # Dot product
score(s_i, h_j) = s_i^T W h_j  # General
```

More computationally efficient and works well in practice.

## Scaled Dot-Product Attention (Transformer, 2017)

The transformer scales dot products by √d_k to prevent vanishing gradients from large dot products:

```
Attention(Q, K, V) = softmax(QK^T / √d_k) V
```

**Why scaling?**: For large d_k, dot products can become very large, pushing softmax into regions with tiny gradients. Dividing by √d_k keeps variance approximately 1.

## Multi-Head Attention

Running h parallel attention heads captures different relationship types:

```python
def multi_head_attention(Q, K, V, num_heads=8):
    d_k = Q.shape[-1] // num_heads
    
    # Project to h subspaces
    Q_heads = Q.reshape(-1, num_heads, d_k)
    K_heads = K.reshape(-1, num_heads, d_k)
    V_heads = V.reshape(-1, num_heads, d_k)
    
    # Compute attention per head
    attn = scaled_dot_product_attention(Q_heads, K_heads, V_heads)
    
    # Concatenate and project
    return linear(attn.reshape(-1, num_heads * d_k))
```

## Self-Attention vs Cross-Attention

**Self-attention**: Q, K, V all come from the same sequence. Enables each position to attend to all others in the sequence.

**Cross-attention**: Q comes from the decoder; K, V come from the encoder. Enables decoder to attend to encoder representations (used in seq2seq tasks).

## Positional Attention

Standard attention is permutation-invariant (order doesn't matter). Positional information is added via:

- **Absolute PE** (original transformer): sin/cos functions of position
- **Relative PE**: Attend to distances, not absolute positions
- **RoPE (Rotary PE)**: Rotate Q, K vectors by angle proportional to position — used in LLaMA, Mistral
- **ALiBi**: Add linear bias to attention scores — enables length extrapolation

## Efficient Attention

Standard attention is O(n²) in sequence length — problematic for long contexts.

**Flash Attention** (Dao et al., 2022): IO-aware exact attention that tiles computation to minimize HBM reads/writes. Same result as standard attention but 2-4× faster and 5-20× less memory — enables training on longer sequences.

**Sliding Window Attention** (Mistral): Each token attends to the nearest W tokens, not all tokens. O(n·W) complexity. Combined with sparse global attention for long-range dependencies.

**Linear Attention**: Replace softmax with kernel functions to get O(n) attention — but accuracy trade-off remains an active research area.

## Attention Patterns

Visualizing attention weights reveals what models learn:
- **Syntactic heads**: Track grammatical dependencies (subjects of verbs)
- **Positional heads**: Attend to fixed relative positions
- **Rare word heads**: Attend to contextually unusual tokens
- **Coreference heads**: Track pronouns to their referents
