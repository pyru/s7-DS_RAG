# Transformer Architecture: Attention Is All You Need

The Transformer architecture, introduced by Vaswani et al. in 2017, revolutionized natural language processing and became the foundation for all large language models. It replaced recurrent and convolutional networks with a purely attention-based architecture that processes sequences in parallel.

## Core Innovation: Self-Attention

The **scaled dot-product attention** mechanism computes relationships between all positions in a sequence simultaneously:

```
Attention(Q, K, V) = softmax(QKᵀ / √dₖ) · V
```

Where:
- Q (queries), K (keys), V (values) are linear projections of the input
- dₖ is the key dimension (scaling prevents vanishing gradients in softmax)
- The output is a weighted sum of values, where weights reflect relevance of each key to each query

This allows any two tokens to attend to each other regardless of distance — solving the long-range dependency problem that plagued RNNs.

## Multi-Head Attention

Rather than computing a single attention function, the Transformer runs h attention heads in parallel, each learning different relationship patterns:

```
MultiHead(Q, K, V) = Concat(head₁, ..., headₕ) · Wᴼ
headᵢ = Attention(QWᵢᴼ, KWᵢᴷ, VWᵢᵛ)
```

With 8 or 16 heads, the model jointly attends to information from different representation subspaces — one head might track coreference, another syntactic dependencies, another semantic similarity.

## Positional Encoding

Since attention is permutation-invariant, positional information is injected via **positional encodings** added to the input embeddings:

```
PE(pos, 2i)   = sin(pos / 10000^(2i/dmodel))
PE(pos, 2i+1) = cos(pos / 10000^(2i/dmodel))
```

Modern models (GPT-3, LLaMA) use **rotary positional embeddings (RoPE)** or **ALiBi** instead, which extrapolate better to longer sequences.

## Encoder-Decoder Structure

The original Transformer uses an **encoder-decoder** architecture:

**Encoder** (N=6 identical layers, each with):
1. Multi-head self-attention
2. Feed-forward network (FFN): two linear layers with ReLU
3. Residual connections + layer normalization around each sublayer

**Decoder** adds:
1. Masked self-attention (prevents attending to future tokens)
2. Cross-attention over encoder output
3. FFN with residual + layer norm

## Variants

- **Encoder-only** (BERT, RoBERTa): best for understanding tasks (classification, NER)
- **Decoder-only** (GPT, LLaMA, Claude): best for generation tasks
- **Encoder-decoder** (T5, BART): best for seq2seq tasks (translation, summarization)

## Feed-Forward Network

Each layer contains a position-wise FFN:
```
FFN(x) = max(0, xW₁ + b₁)W₂ + b₂
```
The inner dimension is typically 4× the model dimension (512 → 2048 in the base model). Modern variants use SwiGLU or GeGLU activations for improved performance.

## Layer Normalization

**Pre-LN** (normalize before attention) is now standard over original post-LN, as it produces more stable training with large learning rates and enables training without warmup.

## Scaling Laws

Kaplan et al. (2020) established that Transformer performance scales predictably as a power law with compute, data, and parameters. This insight drove the race to GPT-3 (175B), PaLM (540B), and beyond — larger models reliably perform better across nearly all tasks.
