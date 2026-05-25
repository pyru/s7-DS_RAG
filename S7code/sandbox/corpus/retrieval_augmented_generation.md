# Retrieval-Augmented Generation (RAG)

Retrieval-Augmented Generation (RAG) combines a parametric language model with a non-parametric retrieval system to produce factual, up-to-date responses grounded in external knowledge. Introduced by Lewis et al. (2020) at Facebook AI Research, RAG has become the dominant approach for knowledge-intensive NLP tasks.

## The RAG Pipeline

A standard RAG system consists of three components:

1. **Indexing**: Documents are chunked, embedded into dense vectors, and stored in a vector database
2. **Retrieval**: Given a user query, the nearest chunks are found via approximate nearest neighbor search
3. **Generation**: The retrieved chunks are prepended to the prompt as context for the language model

```
User Query → Embedding → ANN Search → Top-k Chunks → LLM + Chunks → Answer
```

## Why RAG?

Large language models have several limitations that RAG addresses:

- **Knowledge cutoff**: LLMs are trained on data up to a cutoff date; RAG enables retrieval from current documents
- **Hallucination**: Grounding generation in retrieved evidence reduces fabricated facts
- **Auditability**: Retrieved sources can be cited, enabling verification
- **Cost efficiency**: Fine-tuning is expensive; updating a vector index is cheap

## Retrieval Methods

### Dense Retrieval
Dense retrieval encodes both queries and documents into continuous vector spaces using neural encoders. Similarity is measured by inner product or cosine distance. Models like DPR (Dense Passage Retrieval), Contriever, and the sentence-transformers family are commonly used encoders.

### Sparse Retrieval (BM25)
BM25 is a bag-of-words retrieval function based on term frequency and inverse document frequency. While it cannot match synonyms or paraphrases, it handles rare terms and exact matches robustly.

### Hybrid Retrieval with Reciprocal Rank Fusion (RRF)
Combining dense and sparse signals via RRF typically outperforms either method alone:
```
RRF(d) = Σ 1/(k + rank(d))
```
where k=60 is a smoothing constant and rank(d) is a document's position in each ranked list.

## Chunking Strategies

Document chunking critically affects retrieval quality:

- **Fixed-size chunking**: Split by token count (256–512 tokens) with overlap (50–100 tokens). Simple and widely used.
- **Sentence-level chunking**: Split at sentence boundaries to preserve semantic units.
- **Recursive chunking**: Try paragraph → sentence → word boundaries in sequence.
- **Semantic chunking**: Use embedding similarity to split at topic boundaries. Most effective but computationally expensive.

## Agentic RAG

Agentic RAG extends the static pipeline with iterative reasoning:

1. Agent analyzes query and decides whether retrieval is needed
2. Formulates search queries (potentially different from original query)
3. Retrieves and evaluates relevance of results
4. Reformulates if needed (query rewriting, hypothetical document embedding)
5. Synthesizes answer across multiple retrieved passages

This multi-step approach handles complex questions requiring multi-hop reasoning or iterative refinement.

## Evaluation

Key metrics for RAG systems:
- **Retrieval recall@k**: Fraction of relevant passages in top-k results
- **Faithfulness**: Whether the generated answer is supported by retrieved context
- **Answer relevance**: Whether the answer addresses the question
- **Context precision**: Whether retrieved chunks are actually relevant

Frameworks like RAGAS, TruLens, and LangSmith provide automated RAG evaluation pipelines.
