# Word Embeddings: From One-Hot to Contextual Representations

Word embeddings map words to dense real-valued vectors where semantic relationships are encoded geometrically. The evolution from sparse one-hot vectors to contextual embeddings tracks the progress of NLP over the past decade.

## One-Hot Encoding: The Baseline

One-hot encoding represents each word as a V-dimensional binary vector (V = vocabulary size, typically 50K-100K):

```
"cat" → [0, 0, 1, 0, 0, ..., 0]   # 1 at index 3
"dog" → [0, 0, 0, 1, 0, ..., 0]   # 1 at index 4
```

**Problems**:
- V-dimensional vectors (50K+ features) are extremely sparse
- No semantic relationship: dot product of any two different words is 0
- Cannot generalize: seen "cat" but not "kitten" → model treats them as completely unrelated

## Word2Vec (2013)

Mikolov et al. discovered that shallow neural networks trained on local context windows learn semantically meaningful representations:

**Skip-gram**: Predict surrounding words from center word
**CBOW (Continuous Bag of Words)**: Predict center word from surrounding words

Remarkable property: linear relationships in vector space encode semantic relationships:
```
vec("king") - vec("man") + vec("woman") ≈ vec("queen")
vec("Paris") - vec("France") + vec("Germany") ≈ vec("Berlin")
vec("walked") - vec("walk") ≈ vec("ran") - vec("run")
```

These analogies emerge from the distributional structure of text, not explicit linguistic knowledge.

## GloVe: Global Vectors (2014)

GloVe (Pennington et al.) trains embeddings by factorizing the global word-word co-occurrence matrix, weighting by co-occurrence frequency:

```
J = Σ f(X_ij)(w_i^T w̃_j + b_i + b̃_j - log X_ij)²
```

GloVe captures both local context (like Word2Vec) and global statistics (unlike Word2Vec). On many benchmarks, quality is similar; practitioners often try both.

## FastText (2016)

Facebook AI Research extended Word2Vec with character n-grams:
- "playing" → {pla, lay, ayi, yin, ing, <pl, la>, ..., <playing>}
- Word embedding = sum of n-gram embeddings

**Advantages**:
- Handles morphological variation: "running", "runner", "runs" share subword structure
- Generates embeddings for OOV (out-of-vocabulary) words from their subwords
- Better for morphologically rich languages (German, Turkish, Finnish)

## ELMo: Contextual Representations (2018)

ELMo (Embeddings from Language Models, Peters et al.) introduced contextual embeddings: the same word gets different representations depending on context:

- "The river **bank** flooded" → bank ≈ [0.2, -0.8, ...]
- "I deposited money at the **bank**" → bank ≈ [-0.5, 0.3, ...]

ELMo uses a bidirectional 2-layer LSTM language model. Word representations combine all layers (weighted by learned parameters).

## BERT and Beyond: Transformers as Contextual Embedders

BERT (2018) and its successors produce the richest contextual representations by attending to all positions simultaneously. When used for sentence-level tasks, the `[CLS]` token representation aggregates contextual meaning.

For sentence embeddings (as opposed to word embeddings), sentence-transformers models based on BERT produce high-quality fixed-size representations optimized for semantic similarity through contrastive training.

## Practical Guidance

| Use Case | Recommended Embedding |
|----------|----------------------|
| Static word features | FastText (handles OOV) |
| Semantic sentence similarity | sentence-transformers |
| Named Entity Recognition | BERT contextual embeddings |
| Multilingual | multilingual-MiniLM or mBERT |
| Speed-critical | all-MiniLM-L6-v2 (fast + good) |
| Quality-critical | BAAI/bge-large or OpenAI embeddings |
