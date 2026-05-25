# Semantic Search: Beyond Keyword Matching

Semantic search retrieves documents based on meaning rather than exact keyword overlap. A semantic search for "autonomous vehicles" returns documents about "self-driving cars" and "driverless transportation," even if those exact words appear nowhere in the query.

## Limitations of Keyword Search

Traditional information retrieval relies on lexical matching (BM25, TF-IDF):
- **Vocabulary mismatch**: "heart attack" vs "myocardial infarction" — same concept, no overlap
- **Polysemy**: "bank" (financial institution vs riverbank) — same word, different meanings
- **Synonymy**: "rapid" vs "fast" vs "swift" — different words, same meaning
- **Paraphrase**: "How do I reset my password?" vs "Password recovery procedure" — different phrasing

These limitations motivated the development of dense vector representations that encode meaning.

## Dense Retrieval Architecture

Dense retrieval encodes queries and documents as continuous vectors using dual encoders:

**Bi-encoder** (retrieval): Encodes query and document independently
```
q_emb = encoder(query)   # [768-dim vector]
d_emb = encoder(document)  # [768-dim vector]
score = cosine_similarity(q_emb, d_emb)
```

Pre-computed document embeddings enable sub-millisecond retrieval via FAISS even at billion scale.

**Cross-encoder** (re-ranking): Concatenates query+document for joint encoding
```
score = classifier(concat(query, document))
```
Much more accurate but ~100× slower — used to re-rank top-k bi-encoder results.

## Training Dense Retrievers

**Contrastive learning**: Train bi-encoders using triplets (query, positive doc, negative doc)

**In-batch negatives**: Treat other queries' positives in a mini-batch as negatives — efficient and effective

**Hard negative mining**: Retrieve documents that are similar but not relevant to create challenging training examples — dramatically improves retrieval quality

**Knowledge distillation**: Use cross-encoder scores to supervise bi-encoder training

## Hybrid Search: Best of Both Worlds

Combining dense and sparse retrieval almost always outperforms either alone:

**Reciprocal Rank Fusion (RRF)**:
```
score(doc) = Σ 1/(k + rank_in_system_i(doc))
```
With k=60 (smoothing constant). Simply average ranks from multiple retrieval systems.

**Linear interpolation**:
```
score = α · dense_score + (1-α) · sparse_score
```
Optimal α varies by dataset (typically 0.3–0.7 for dense component).

## Query Understanding and Expansion

Enhance queries before retrieval:

**Query rewriting**: LLM generates alternative query formulations
**Hypothetical Document Embeddings (HyDE)**: Generate a hypothetical answer, embed it, use that embedding for retrieval. The generated answer lives in document space, bridging the query-document gap.

```python
hypothetical_answer = llm.generate("Answer this question in detail: " + query)
embedding = encoder.encode(hypothetical_answer)
results = faiss_index.search(embedding, k=10)
```

**Query expansion with synonyms**: Add synonyms from WordNet or model-generated paraphrases

## Evaluation and Failure Analysis

Semantic retrieval quality degrades for:
- Highly technical jargon not in pre-training data
- Proper nouns and entity-specific queries
- Very long documents where the relevant passage is surrounded by noise
- Multi-hop questions requiring reasoning across documents

Mitigation: domain-specific fine-tuning, smaller chunks, reranking, and query decomposition.
