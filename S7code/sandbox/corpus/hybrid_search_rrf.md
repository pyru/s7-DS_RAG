# Hybrid Search and Reciprocal Rank Fusion

Hybrid search combines dense vector retrieval with sparse keyword-based retrieval to achieve better results than either approach alone. Reciprocal Rank Fusion (RRF) is the most widely used algorithm for merging ranked lists from multiple retrieval systems.

## Why Hybrid Search Works

Dense retrieval and sparse retrieval have complementary strengths:

**Dense retrieval (vector search) excels at**:
- Synonym matching ("heart attack" ↔ "myocardial infarction")
- Paraphrase matching ("how do I reset my password?" ↔ "password recovery procedure")
- Conceptual queries without specific terminology
- Cross-lingual retrieval

**Sparse retrieval (BM25) excels at**:
- Exact technical terms (product codes, error messages, command names)
- Rare proper nouns not seen in embedding training
- Numerical and date queries
- Short queries with distinctive keywords

The combination consistently outperforms either component in BEIR benchmark studies, often by 3-8% in NDCG@10.

## BM25: The Sparse Baseline

BM25 (Best Match 25) scores documents by term frequency, inverse document frequency, and document length normalization:

```
BM25(D,Q) = Σ_q IDF(q) · (TF(q,D) · (k₁+1)) / (TF(q,D) + k₁·(1-b+b·|D|/avgdl))
```

Where k₁=1.5, b=0.75 are typical constants; |D| is document length; avgdl is average document length.

BM25 is implemented efficiently with inverted indexes. Tools: Elasticsearch, Lucene, rank_bm25 (Python).

## Reciprocal Rank Fusion (RRF)

RRF (Cormack et al., 2009) merges ranked lists without requiring score normalization:

```
RRF(d) = Σ_i  1 / (k + rank_i(d))
```

Where k=60 (smoothing constant preventing high weights for rank 1) and rank_i(d) is document d's position in retrieval system i.

**Example**:
```
Dense results: doc_A (rank 1), doc_B (rank 2), doc_C (rank 3)
Sparse results: doc_C (rank 1), doc_A (rank 2), doc_D (rank 3)

RRF(doc_A) = 1/(60+1) + 1/(60+2) = 0.0164 + 0.0161 = 0.0325
RRF(doc_B) = 1/(60+2) + 0         = 0.0161
RRF(doc_C) = 1/(60+3) + 1/(60+1) = 0.0159 + 0.0164 = 0.0323
RRF(doc_D) = 0        + 1/(60+3) = 0.0159

Final ranking: doc_A > doc_C > doc_B > doc_D
```

## Implementation

```python
from collections import defaultdict

def reciprocal_rank_fusion(ranked_lists: list[list[str]], k: int = 60) -> list[str]:
    """Merge multiple ranked lists using RRF."""
    scores = defaultdict(float)
    for ranked in ranked_lists:
        for rank, doc_id in enumerate(ranked, 1):
            scores[doc_id] += 1.0 / (k + rank)
    return sorted(scores.keys(), key=lambda d: -scores[d])

# Usage
dense_results = ["doc_A", "doc_B", "doc_C", "doc_E"]
sparse_results = ["doc_C", "doc_A", "doc_D", "doc_F"]

final_ranking = reciprocal_rank_fusion([dense_results, sparse_results])
```

## Alternatives to RRF

**Linear interpolation**: Requires normalized scores (not always available):
```
score(d) = α · dense_score(d) + (1-α) · sparse_score(d)
```

**CombSUM/CombMNZ**: Older fusion methods; generally inferior to RRF.

**Learn-to-Rank**: Train a model to optimally weight multiple retrieval signals (LightGBM, neural rankers). Requires labeled data but achieves best results.

## Sparse Vectors: SPLADE

SPLADE (SParse Lexical and Expansion) uses a masked language model to produce sparse expansions — semantically related terms added to the sparse representation:

Query: "AI ethics" → {AI: 2.3, ethics: 1.8, fairness: 1.4, bias: 1.2, responsibility: 0.9}

SPLADE bridges dense and sparse retrieval, often matching hybrid search quality with a single index.

## Production Deployment

In production RAG systems, hybrid search typically:
1. Dense retrieval retrieves top-100 candidates from FAISS
2. Sparse retrieval retrieves top-100 from Elasticsearch
3. RRF merges lists into final top-20
4. Cross-encoder reranker produces final top-5
5. LLM generates answer grounded in top-5 passages
