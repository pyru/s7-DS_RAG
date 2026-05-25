# Sentence Transformers: Dense Text Embeddings

Sentence Transformers is a Python library that produces semantically meaningful dense vector representations of text. Built on top of HuggingFace Transformers, it provides pre-trained models optimized for semantic similarity tasks — the foundation of modern RAG systems.

## What Are Sentence Embeddings?

Unlike word embeddings (Word2Vec, GloVe) that represent individual tokens, sentence embeddings map entire sentences or paragraphs to fixed-length vectors where **semantic similarity corresponds to geometric proximity**. Two sentences with similar meaning map to nearby points in the embedding space, even if they share no words.

Example:
- "The dog ran across the park" → [0.23, -0.45, 0.81, ...]
- "A canine sprinted through the garden" → [0.21, -0.43, 0.79, ...]  ← nearby
- "The stock market fell sharply" → [-0.67, 0.12, -0.33, ...]  ← distant

## Architecture: Siamese Networks

Sentence Transformers uses a **Siamese or triplet network** structure during training. Two BERT-like encoders (with shared weights) process sentence pairs simultaneously. The network is trained to minimize distance between semantically similar pairs and maximize distance between dissimilar pairs.

The final sentence embedding is computed by **mean pooling** over all token representations:
```
embedding = mean(token_representations[1:-1])  # Exclude [CLS] and [SEP]
```

## Key Pre-trained Models

| Model | Dim | Speed | Quality | Use Case |
|-------|-----|-------|---------|----------|
| all-MiniLM-L6-v2 | 384 | Fast | Good | Default RAG |
| all-mpnet-base-v2 | 768 | Medium | Great | Quality-sensitive |
| multi-qa-mpnet-base-dot-v1 | 768 | Medium | Great | Q&A retrieval |
| paraphrase-multilingual-MiniLM-L12-v2 | 384 | Fast | Good | Multilingual |
| BAAI/bge-large-en-v1.5 | 1024 | Slow | Excellent | MTEB SOTA |

## Usage

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

# Single encoding
embedding = model.encode("What is information theory?")

# Batch encoding (more efficient)
sentences = ["First sentence", "Second sentence", "Third sentence"]
embeddings = model.encode(sentences, batch_size=32, show_progress_bar=True)

# Semantic search
from sentence_transformers import util
query_emb = model.encode("Who invented information theory?")
scores = util.cos_sim(query_emb, embeddings)
```

## Asymmetric Retrieval

For retrieval tasks, queries and documents have different characteristics. **Bi-encoder** models encode them independently; **cross-encoders** encode the query+document jointly for higher accuracy.

Production systems use bi-encoders for retrieval (fast, can precompute document embeddings) and cross-encoders for re-ranking (slow but accurate):

1. Bi-encoder: retrieve top-100 candidates from FAISS
2. Cross-encoder: re-rank top-100 to find true top-10

## Task-Specific Encoding

Many embedding APIs accept a `task_type` parameter:
- `retrieval_document`: optimized for encoding corpus documents
- `retrieval_query`: optimized for encoding user queries
- `semantic_similarity`: for comparing sentence pairs
- `classification`: for downstream classification tasks

Using the correct task type improves retrieval quality, especially for asymmetric retrieval where queries are shorter than documents.

## Training Your Own Model

For domain-specific retrieval, fine-tune on domain data using:
```python
from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader

model = SentenceTransformer('all-MiniLM-L6-v2')
train_examples = [
    InputExample(texts=['Query', 'Relevant passage'], label=1.0),
    InputExample(texts=['Query', 'Irrelevant passage'], label=0.0),
]
train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=16)
train_loss = losses.CosineSimilarityLoss(model)
model.fit(train_objectives=[(train_dataloader, train_loss)], epochs=3)
```
