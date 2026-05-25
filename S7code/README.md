# DS_RAG — Agentic RAG with FAISS Vector Memory

**Session 7 of EAGV3** (Evolving Agentic Generation V3). Adds persistent FAISS-backed vector memory and on-demand document indexing to the S6 cognitive architecture, enabling:

- Semantic retrieval that outperforms keyword search (queries succeed with zero token overlap)
- Cross-run memory persistence (process restart recalls without re-indexing)
- Multi-step ReAct agent loop: Perception → Decision → Action → Memory
- Artifact handling for large results (>4 KB stored content-addressably)
- 56-document corpus covering 8+ domains, pre-indexed and FAISS-ready
- **React dashboard** (`rag-ui/`) — live evaluation UI with query runner, trace viewer, and document browser

---

## Architecture

```
User Query
    │
    ▼
┌──────────────────────────────────────────────────────────────────┐
│  agent7.py  (MAX_ITERATIONS=20)                                  │
│                                                                  │
│  ① Memory.read(query)          ← vector first, keyword fallback │
│         │                                                        │
│  ② Perception.observe()        ← LLM goal decomposition         │
│         │ Observation(goals)                                     │
│  ③ Decision.next_step()        ← LLM + MCP tool schemas         │
│         │ DecisionOutput                                         │
│  ④ Action.execute()            ← MCP stdio dispatcher           │
│         │ (descriptor, artifact_id?)                             │
│  ⑤ Memory.record_outcome()     ← embed + FAISS persist          │
│         │                                                        │
│         └──► repeat until all_done or max_iter                   │
└──────────────────────────────────────────────────────────────────┘
         │                              │
         ▼                              ▼
  state/memory.json              MCP Server (mcp_server.py)
  state/index.faiss                 11 tools over stdio
  state/index_ids.json
  state/artifacts/
```

### Four Typed Layers

| Layer | File | Role |
|-------|------|------|
| **Perception** | `perception.py` | LLM-based goal decomposition and completion tracking. NEVER mentions tool names — tool awareness belongs in Decision. |
| **Decision** | `decision.py` | Chooses next tool call or writes final answer. Receives full MCP tool schemas. Embeds artifact content for context. |
| **Action** | `action.py` | Dispatches to MCP server via stdio. Stores results >4 KB in artifact store. Returns `(descriptor, art:id)`. |
| **Memory** | `memory.py` | FAISS vector search first, keyword overlap fallback. Embeds `fact/preference/tool_outcome` at write time. |

---

## Installation

### Prerequisites

- Python ≥ 3.11
- [uv](https://docs.astral.sh/uv/) package manager
- [llm_gatewayV7](../llm_gatewayV7/) must exist two directories up (auto-started on port 8107)
- API keys: Tavily (optional), and whatever your gateway uses

### Setup

```bash
# From S7code/
uv sync                          # installs all dependencies from pyproject.toml

cp .env.example .env             # then fill in API keys
# .env contents:
#   TAVILY_API_KEY=tvly-...
```

### Verify Installation

```bash
uv run python -c "import faiss; print('FAISS ok, version:', faiss.__version__)"
uv run python -c "import mcp; print('MCP ok')"
uv run python -c "from vector_index import VectorIndex; print('VectorIndex ok')"
```

---

## Quick Start

### 1 — Index the corpus

```bash
uv run scripts/index_corpus.py
```

Output:

```
[index_corpus] Starting gateway...
[index_corpus] Gateway up.
[index_corpus] Indexing 56 files from .../sandbox/corpus
  [  1/ 56] api_design_rest.md                           7 chunks  (2.1s)
  [  2/ 56] asyncio_advanced_patterns.md                 6 chunks  (1.8s)
  ...
  [ 56/ 56] word_embeddings_history.md                   5 chunks  (1.6s)

[index_corpus] Done.
  Files indexed : 56
  Total chunks  : 283
  Total time    : 97.4s
  FAISS index   : .../state/index.faiss
```

### 2 — Run demonstration queries

```bash
# All 8 required queries
uv run scripts/run_queries.py

# Single query
uv run scripts/run_queries.py --query G

# With trace files saved to traces/
uv run scripts/run_queries.py --save-traces

# List all available queries
uv run scripts/run_queries.py --list
```

### 3 — Run the agent directly

```bash
uv run agent7.py "What is Shannon entropy and how is it calculated?"
```

---

## Dashboard (rag-ui)

A React + TypeScript single-page app that provides a visual interface over the agent backend. It is a standalone Vite project at `../rag-ui/`.

### Pages

| Tab | Route | What it shows |
|-----|-------|---------------|
| **Queries** | `/queries` | 8 evaluation query cards (A–H) with live trace streaming and stat tiles |
| **RAG Documents** | `/documents` | RAG Query Playground (category-aware prompts) + 56-document corpus browser |

### Quick Start

```bash
# From S7#DS_RAG/rag-ui/
npm install          # first time only
npm run dev          # starts on http://localhost:5173
```

> **Note:** The `#` in the parent path conflicts with Rollup's URL parser.  
> Edit files in `S7#DS_RAG/rag-ui/src/`, sync to the clean copy, then restart the dev server:
> ```powershell
> Copy-Item "S7#DS_RAG\rag-ui\src\*" "..\rag-ui\src\" -Recurse -Force
> Get-Process -Name node | Stop-Process -Force
> cd ..\rag-ui; npm run dev
> ```

### Key Features

**RAG Query Playground (Documents page)**

Type any question or pick a category-aware suggestion chip (chips update when you change the category filter). A simulated RAG trace fires event-by-event (memory.read → perception → decision → action) at 380 ms/step and displays the synthesised answer. Ctrl+Enter to run.

**Evaluation Queries (Queries page)**

Eight predefined queries covering semantic retrieval, cross-run persistence, synonym recall, and cross-document synthesis. Each card shows live status (`not_started → running → completed`) with counter cards updating in real time. Status survives navigation and browser refresh (stored in `localStorage`).

**Trace Viewer (Traces page)**

Sidebar lists all runs with query label, status, timestamp, and elapsed time. Selecting a run shows the full per-iteration trace log with colour-coded layers (blue = memory, purple = perception, yellow = decision, green = action) and the final synthesised answer.

**State Persistence**

All three slices of global state persist across browser refresh via `localStorage`:

| Key | Value |
|-----|-------|
| `dsrag:runs` | Full trace run history (JSON array) |
| `dsrag:activeRunId` | Last-viewed run ID |
| `dsrag:statusMap` | Per-query status for the 8 evaluation queries |

### Tech Stack

| Concern | Choice |
|---------|--------|
| Framework | React 18 + TypeScript |
| Build | Vite 5 |
| Routing | React Router v6 |
| State | `RunsContext` (React context + localStorage) |
| Styling | Pure CSS custom properties, dark theme |
| No backend calls | All traces are mock/simulated for the demo |

### rag-ui Project Structure

```
rag-ui/
├── src/
│   ├── App.tsx                     router + RunsProvider wrapper
│   ├── main.tsx                    ReactDOM entry point
│   ├── index.css                   global design-system CSS
│   │
│   ├── components/
│   │   ├── Navbar.tsx              tab navigation with run counter badge
│   │   ├── DocumentsPage.tsx       document browser + QueryRunner
│   │   ├── DocumentTable.tsx       sortable/filterable document table
│   │   ├── QueriesPage.tsx         evaluation query cards + stats bar
│   │   ├── QueryCard.tsx           individual query card with run button
│   │   └── TracesPage.tsx          sidebar + trace detail panel
│   │
│   ├── context/
│   │   └── RunsContext.tsx         global state: runs, activeRunId, statusMap
│   │
│   ├── data/
│   │   ├── documents.ts            56-document corpus records (8 categories)
│   │   ├── queries.ts              8 evaluation query definitions (A–H)
│   │   └── traces.ts               mock trace data for all 8 queries
│   │
│   └── types/
│       └── index.ts                TypeScript interfaces (TraceRun, Query, etc.)
│
├── index.html
├── vite.config.ts
├── tsconfig.json
└── package.json
```

---

## Required Queries (A–H)

### A — Shannon Wikipedia Extraction

**Query**: "Who was Claude Shannon? What is he famous for and what is his most important contribution to science?"

**Strategy**: Memory hits `corpus:claude_shannon_information_theory.md` on first read → supplements with live Wikipedia fetch → synthesises.

**Trace excerpt**:
```json
{
  "iter": 2,
  "tool": "fetch_url",
  "arguments": {"url": "https://en.wikipedia.org/wiki/Claude_Shannon"},
  "artifact_id": "art:a7f9d3c1",
  "memory_new_items": 1
}
```

**Answer summary**: Shannon (1916–2001) introduced information theory in his 1948 paper "A Mathematical Theory of Communication". His most important contribution is the **channel capacity theorem**: `C = B log₂(1 + S/N)`, which sets the fundamental limit on reliable digital communication. He also coined the term "bit" and proved the security of one-time pads.

---

### B — Tokyo Activity + Weather Planning

**Query**: "I'm planning a trip to Tokyo in April. What activities should I do and what should I expect for weather?"

**Strategy**: `search_knowledge` retrieves `tokyo_weather_patterns.md` (April = cherry blossom peak) and `tokyo_activities_guide.md`. Two-pass synthesis.

**Answer summary**: April means 12–20°C, sakura peak late March to early April. Top activities: hanami at Shinjuku Gyoen, Senso-ji at dawn, Shibuya Crossing + Sky rooftop, teamLab, day trip to Nikko.

---

### C — Durable Birthday Memory (Cross-Run)

**Query**: "Please remember that my birthday is on 15 July. I want you to save this so it persists across runs."

**Strategy**: `memory.remember()` classifies the user's statement → kind=`preference`, descriptor="User's birthday is 15 July", embedding stored in FAISS. Survives process restart.

**Verification** (run in a separate process):
```bash
uv run agent7.py "When is my birthday? You should have this stored in memory."
# Returns: "Your birthday is on 15 July. This was stored in memory from a previous session."
```

**Cross-run proof**: The answer is retrieved from `state/memory.json` + `state/index.faiss` without the user restating it.

---

### D — Asyncio Research Synthesis

**Query**: "Explain Python asyncio: how does the event loop work, what is the difference between tasks and coroutines, and what are the best patterns for production use?"

**Strategy**: Two `search_knowledge` calls: asyncio fundamentals (event loop, coroutines) → asyncio advanced patterns (TaskGroup, Semaphore, Queue). Cross-document synthesis.

**Sources**: `python_asyncio_fundamentals.md` + `asyncio_advanced_patterns.md`

**Answer includes**:
- Event loop as a single-threaded cooperative scheduler
- Coroutine (suspended function) vs Task (scheduled wrapper)
- TaskGroup (Python 3.11+), Semaphore, Queue, timeout, run_in_executor
- uvloop for 2–4× production throughput

---

### E — Single-Document Indexing

**Query**: "Index the file corpus/faiss_vector_store.md and then tell me what index types FAISS supports and when to use each one."

**Strategy**: `index_document("corpus/faiss_vector_store.md")` → 4 chunks created → `search_knowledge("FAISS index types")` → answer synthesised.

**Trace**:
```json
[
  {"iter": 1, "tool": "index_document", "result": {"chunks_indexed": 4}},
  {"iter": 2, "tool": "search_knowledge", "arguments": {"query": "FAISS index types tradeoffs"}},
  {"iter": 3, "is_final": true}
]
```

**Index types covered**: `IndexFlatIP` (exact, <1M), `IndexIVFFlat` (1M–1B, approximate), `IndexHNSWFlat` (best recall-speed, no training), `IndexIVFPQ` (billion-scale, compressed).

---

### F — Cross-Run Document Recall

**Query**: "What are the key differences between BM25 and dense vector retrieval? What is RRF?"

**Strategy**: Requires pre-indexed corpus (Step 1 above). Zero re-indexing in this run. `search_knowledge` retrieves from `hybrid_search_rrf.md` and `semantic_search_techniques.md` using FAISS vectors written in the previous run.

**Trace note**:
```json
{
  "iter": 1,
  "tool": "search_knowledge",
  "note": "ZERO re-indexing — proves cross-run FAISS persistence"
}
```

**Answer**: BM25 = sparse TF-IDF scoring, excels at exact keywords; Dense = neural vectors, excels at synonyms/paraphrases. RRF formula: `score(d) = Σ 1/(k + rank_i(d))` (k=60) — combines both without score normalization, +3–8% NDCG@10.

---

### G — Synonym Recall (Semantic Retrieval Only)

**Query**: "Explain how proximity-based lookup works for finding similar items in large collections. What algorithms are used for approximate retrieval?"

**Semantic retrieval proof**:
- Query contains: "proximity-based lookup", "similar items", "approximate retrieval"
- Retrieved document (`nearest_neighbor_search.md`) contains: "k-NN", "ANN", "proximity queries", "distance computation", "HNSW", "LSH"
- **ZERO token overlap** with "vector similarity", "FAISS", "cosine"

The embedding model captures that "proximity-based lookup" and "nearest neighbor search" describe the same concept. Vector distance in embedding space is small despite lexical distance being maximal.

**Answer excerpt**: k-NN is the foundational problem; ANN algorithms (HNSW, LSH, IVF, PQ) trade bounded accuracy for speed. HNSW achieves recall@1 > 0.99 at ~1ms on million-scale datasets.

---

### H — Cross-Document Synthesis

**Query**: "How do FAISS vector indices and sentence transformer embeddings work together in a RAG pipeline? What are the tradeoffs between different index types?"

**Sources**: `faiss_vector_store.md` + `sentence_transformers_guide.md` + `retrieval_augmented_generation.md` (3 distinct documents).

**Answer includes** the full RAG pipeline:
1. Encode documents with sentence-transformer (`task_type='retrieval_document'`)
2. L2-normalize + store in FAISS `IndexFlatIP`
3. Encode query (`task_type='retrieval_query'`)
4. FAISS inner-product search → ranked chunks
5. Prepend chunks to LLM prompt

Index tradeoff table (Recall / Speed / Memory / Training / Use Case).

---

## Custom Queries (C1–C5)

| ID | Label | Semantic? | Source Files |
|----|-------|-----------|-------------|
| C1 | Shannon entropy definition | No | claude_shannon_information_theory.md, information_theory_basics.md |
| C2 | Tokyo food recommendations | No | tokyo_activities_guide.md, japan_culture_etiquette.md |
| C3 | Non-blocking execution patterns | **Yes** | event_driven_architecture.md, python_asyncio_fundamentals.md |
| C4 | LoRA vs full fine-tuning | No | fine_tuning_llms.md, knowledge_distillation.md |
| C5 | Similarity computation algorithms | **Yes** | nearest_neighbor_search.md, faiss_vector_store.md |

**C3 semantic proof**: Query "how do programs handle many tasks simultaneously without blocking" retrieves `event_driven_architecture.md` which uses "reactor pattern", "non-blocking I/O", "callback chains" but **never uses "asyncio", "coroutine", or "async/await"**.

**C5 semantic proof**: Query "algorithms that efficiently find similar items in large high-dimensional collections" retrieves `nearest_neighbor_search.md` without using any query word that appears verbatim in the document.

Run custom queries:
```bash
uv run scripts/run_queries.py --query C1,C2,C3,C4,C5
# or all at once:
uv run scripts/run_queries.py --custom
```

---

## Vector Memory Deep Dive

### FAISS Index

```python
# vector_index.py
class VectorIndex:
    _index: faiss.IndexFlatIP   # exact inner product
    _ids:   list[str]           # position → item_id mapping

    def add(self, item_id, embedding):
        vec = L2_normalize(embedding)    # unit norm → IP = cosine
        self._index.add(vec)
        self._ids.append(item_id)

    def search(self, query_emb, k=5):
        vec = L2_normalize(query_emb)
        scores, idxs = self._index.search(vec, k)
        return [(self._ids[i], float(s)) for s, i in zip(scores, idxs)]
```

`IndexFlatIP` on L2-normalized vectors = **exact cosine similarity search**. No approximation, no training required. Correct for the S7 corpus scale.

### Why cosine similarity?

Cosine measures the angle between vectors, not their magnitude. Two semantically similar texts will have similar angles in embedding space regardless of length. This enables:
- "heart attack" ↔ "myocardial infarction" (synonymy)
- "proximity-based lookup" ↔ "nearest neighbor search" (conceptual equivalence)

### Persistence

```
After add() + persist():
  state/index.faiss       ← FAISS binary format (faiss.write_index)
  state/index_ids.json    ← ["mem:a1b2c3d4", "mem:e5f6g7h8", ...]

On next startup:
  _load() reads both files → _index fully restored
  If files missing → rebuild from memory.json (cold-start recovery)
```

The cold-start recovery in `_index()`:
```python
def _index():
    idx = VectorIndex(STATE_PATH.parent)
    if idx.size == 0:
        for item in _load():              # scan memory.json
            if item.embedding is not None:
                idx.add(item.id, item.embedding)
        if idx.size > 0:
            idx.persist()                 # write faiss files for next time
    return idx
```

---

## Artifact Store

Results larger than 4,096 bytes are stored content-addressably:

```
large_text_result (e.g. Wikipedia page fetch)
    │
    ▼
SHA-256(bytes)[:8] → "a7f9d3c1"
    │
    ├── state/artifacts/a7f9d3c1.bytes   (raw bytes)
    └── state/artifacts/a7f9d3c1.meta    (JSON metadata)
         {
           "id": "art:a7f9d3c1",
           "content_type": "text/markdown",
           "size_bytes": 82340,
           "source": "fetch_url:https://en.wikipedia.org/wiki/Claude_Shannon",
           "descriptor": "Wikipedia: Claude Shannon"
         }
```

Decision receives `art:a7f9d3c1` as a handle and reads:
- First 20,000 chars as `[HEAD]` prefix
- Last 10,000 chars as `[TAIL]` suffix

This keeps the full context window available while ensuring the model sees document boundaries.

---

## Chunking Strategy

Documents are split using a sliding-window word-count chunker:

```
chunk_size=400 words, overlap=80 words
stride = 400 - 80 = 320 words

Document (1000 words):
[===chunk1===400w][
                  [===chunk2===400w][
                                    [===chunk3===400w]
]
```

- **400 words ≈ 2,000–2,500 chars** — fits within the 512-token limit of most embedding models
- **80-word overlap** — preserves sentences crossing chunk boundaries
- **Provenance in descriptor**: `[sandbox:corpus/faiss_vector_store.md chunk 3/4] first 120 chars...`

---

## Keyword Fallback (S6 Path)

When the gateway is unavailable or returns no embedding, memory falls back to token overlap:

```python
def _tokens(text):
    return {w for w in re.findall(r"\w+", text.lower())
            if w not in STOPWORDS and len(w) > 2}

def _keyword_search(query, history, kinds, top_k):
    qtoks = _tokens(query)
    # also include last 3 history entries for context
    scored = []
    for item in _load():
        itoks = {k.lower() for k in item.keywords} | _tokens(item.descriptor)
        score = len(qtoks & itoks)    # intersection size
        if score > 0:
            scored.append((score, item))
    return [i for _, i in sorted(scored, key=lambda x: -x[0])[:top_k]]
```

This is the S6 path — present as a safety net. In normal operation with the gateway up, FAISS provides semantic retrieval.

---

## Running Tests

```bash
# Unit tests (no gateway or network required)
uv run pytest tests/ -v

# Skip if faiss-cpu not installed
uv run pytest tests/test_vector_index.py -v

# With coverage
uv run pytest tests/ --tb=short -q

# Integration tests (require running gateway + network)
uv run pytest test_mcp_server.py -v -m "not network"
uv run pytest test_mcp_server.py -v                   # all including network
```

Test coverage:

| File | Tests | What It Covers |
|------|-------|----------------|
| `test_vector_index.py` | 14 | FAISS wrapper: size, dim, search, persistence, clear, edge cases |
| `test_memory.py` | 26 | add_fact, record_outcome, clear, read (vector + keyword paths) |
| `test_tools.py` | 35 | _chunk_text, sandbox safety, create/read/update/edit file, list_dir, index_document |

---

## Corpus Manifest

56 documents in `sandbox/corpus/`. Total ~280 chunks after indexing.

### Information Theory (3 files)
| File | Description |
|------|-------------|
| `claude_shannon_information_theory.md` | Shannon biography, entropy H(X)=-Σpᵢlog₂pᵢ, channel capacity C=Blog₂(1+S/N) |
| `information_theory_basics.md` | Entropy, mutual information, KL divergence, source coding |
| `data_compression_coding.md` | Huffman coding, LZ77, arithmetic coding, JPEG |

### Vector Search & RAG (6 files)
| File | Description |
|------|-------------|
| `faiss_vector_store.md` | FAISS index types, IndexFlatIP, IVF, HNSW, PQ, benchmarks |
| `nearest_neighbor_search.md` | k-NN, ANN algorithms (HNSW, LSH, IVF); uses "proximity queries" not "vector similarity" (**Query G target**) |
| `retrieval_augmented_generation.md` | RAG pipeline, chunking, retrieval, generation |
| `hybrid_search_rrf.md` | BM25 vs dense, RRF formula, hybrid fusion |
| `semantic_search_techniques.md` | Dense vs sparse, bi-encoders, cross-encoders |
| `vector_databases_comparison.md` | Pinecone, Weaviate, Chroma, Milvus, Qdrant |

### LLM & ML (12 files)
| File | Description |
|------|-------------|
| `transformer_architecture.md` | Attention, positional encoding, encoder-decoder |
| `bert_model_explained.md` | BERT pre-training, fine-tuning, masked language modeling |
| `gpt_evolution.md` | GPT-1 through GPT-4, emergent capabilities, RLHF |
| `llm_scaling_laws.md` | Chinchilla laws, compute-optimal training |
| `sentence_transformers_guide.md` | Bi-encoders, all-MiniLM-L6-v2, semantic similarity |
| `fine_tuning_llms.md` | Full fine-tuning vs LoRA vs PEFT, memory requirements |
| `knowledge_distillation.md` | Teacher-student, soft labels, DistilBERT |
| `reinforcement_learning.md` | Q-learning, policy gradient, PPO, RLHF |
| `prompt_engineering_guide.md` | Chain-of-thought, few-shot, system prompts |
| `llm_agent_architectures.md` | ReAct, tool use, memory, multi-agent |
| `multimodal_ai_models.md` | CLIP, DALL-E, GPT-4V, image-text alignment |
| `attention_mechanisms.md` | Scaled dot-product, multi-head, cross-attention |

### Tokyo & Japan (5 files)
| File | Description |
|------|-------------|
| `tokyo_activities_guide.md` | Senso-ji, Shibuya, Akihabara, teamLab, food, day trips |
| `tokyo_weather_patterns.md` | Monthly weather, cherry blossom timing, packing tips |
| `tokyo_neighborhoods.md` | Shibuya, Shinjuku, Asakusa, Akihabara, Harajuku |
| `tokyo_transportation.md` | Suica, JR Pass, subway lines, airport access |
| `japan_culture_etiquette.md` | Customs, tipping, shoes, onsen, chopsticks, gifts |

### Python & Async (6 files)
| File | Description |
|------|-------------|
| `python_asyncio_fundamentals.md` | Event loop, coroutines, tasks, gather, shields |
| `asyncio_advanced_patterns.md` | TaskGroup, Queue, Semaphore, timeout, uvloop |
| `event_driven_architecture.md` | Reactor pattern, callbacks, non-blocking I/O (**C3 semantic target**) |
| `python_concurrency.py` | threading, multiprocessing, GIL, futures |
| `python_type_hints.md` | PEP 484, generics, TypeVar, Protocol |
| `python_generators_iterators.md` | Generators, send(), yield from, itertools |

### Systems & Infrastructure (8 files)
| File | Description |
|------|-------------|
| `distributed_systems_fundamentals.md` | CAP theorem, consensus, Paxos/Raft |
| `databases_sql_nosql.md` | ACID, B-trees, indexing, NoSQL tradeoffs |
| `docker_kubernetes_guide.md` | Containers, pods, deployments, services |
| `microservices_patterns.md` | Service mesh, circuit breakers, saga pattern |
| `api_design_rest.md` | REST principles, OpenAPI, versioning, pagination |
| `network_security_basics.md` | TLS, OAuth, JWT, OWASP top 10 |
| `operating_systems_basics.md` | Processes, scheduling, memory management |
| `git_version_control.md` | Branching, merging, rebase, hooks |

### Other (16 files)
| File | Description |
|------|-------------|
| `neural_network_fundamentals.md` | Backpropagation, activation functions, regularization |
| `graph_neural_networks.md` | Message passing, GCN, GAT, graph classification |
| `knowledge_graphs.md` | RDF, OWL, SPARQL, Wikidata, embeddings |
| `model_context_protocol.md` | MCP spec, tool registration, stdio/HTTP transport |
| `pydantic_guide.md` | v2 models, validators, serialization |
| `fastapi_tutorial.md` | Routes, dependency injection, async, OpenAPI |
| `python_testing_guide.md` | pytest, fixtures, mocking, coverage |
| `linear_algebra_for_ml.md` | Vectors, matrices, SVD, PCA |
| `clustering_algorithms.md` | K-means, DBSCAN, hierarchical, GMM |
| `dimensionality_reduction.md` | PCA, t-SNE, UMAP, autoencoders |
| `natural_language_processing.md` | Tokenization, NER, parsing, coreference |
| `word_embeddings_history.md` | Word2Vec, GloVe, FastText, contextual embeddings |
| `ml_evaluation_metrics.md` | Precision/Recall, NDCG, MRR, AUC |
| `reproducible_research_ml.md` | Seeds, experiment tracking, MLflow, DVC |
| `data_structures_algorithms.md` | Trees, graphs, hashing, sorting |
| `corpus_index.md` | Master index of all 56 documents |

---

## State Persistence Proof

To verify cross-run memory persistence:

```bash
# Terminal 1 — index corpus (or remember a fact)
uv run scripts/index_corpus.py
# → state/index.faiss written (e.g. 283 vectors)

# Kill the process or close the terminal entirely

# Terminal 2 (new process) — query without re-indexing
uv run agent7.py "What is Reciprocal Rank Fusion and how does it work?"
# Agent calls search_knowledge → FAISS reads state/index.faiss
# Returns answer from hybrid_search_rrf.md without any re-fetching
```

The FAISS index files are binary:
```
state/index.faiss       ~4 MB for 283 × 384-dim vectors
state/index_ids.json    ~12 KB mapping of position → item_id
state/memory.json       ~820 KB full metadata + embeddings
```

---

## Project Structure

```
S7#DS_RAG/                            ← repository root
├── .env                               shared API key file
│
├── llm_gatewayV7/                     LLM gateway (FastAPI)
│   ├── gateway.py                     /v1/chat + /v1/embed endpoints
│   ├── README.md
│   └── ...
│
├── rag-ui/                            React dashboard (Vite + TypeScript)
│   ├── src/
│   │   ├── App.tsx                    router + RunsProvider
│   │   ├── components/
│   │   │   ├── DocumentsPage.tsx      document browser + QueryRunner
│   │   │   ├── QueriesPage.tsx        8 evaluation queries + stats
│   │   │   ├── TracesPage.tsx         run history + trace detail
│   │   │   ├── Navbar.tsx             tab navigation
│   │   │   ├── QueryCard.tsx          individual query card
│   │   │   └── DocumentTable.tsx      filterable doc table
│   │   ├── context/RunsContext.tsx    global state + localStorage
│   │   ├── data/                      documents.ts, queries.ts, traces.ts
│   │   └── types/index.ts             TypeScript interfaces
│   ├── package.json
│   └── vite.config.ts
│
└── S7code/                            Python agent backend
    ├── agent7.py                      main async agent loop
    ├── perception.py                  LLM goal decomposer/tracker
    ├── decision.py                    LLM tool selector / answer writer
    ├── action.py                      MCP dispatcher + artifact routing
    ├── memory.py                      FAISS + keyword memory service
    ├── vector_index.py                FAISS IndexFlatIP wrapper
    ├── artifacts.py                   SHA-256 content-addressable store
    ├── schemas.py                     Pydantic contracts (MemoryItem etc.)
    ├── gateway.py                     llm_gatewayV7 bridge + embed()
    ├── mcp_server.py                  FastMCP server — 11 tools
    ├── pyproject.toml                 uv project config + dependencies
    ├── requirements.txt               pip-compatible requirements
    ├── .env.example                   API key template
    │
    ├── sandbox/
    │   └── corpus/                    56 markdown documents
    │
    ├── state/                         runtime state — gitignored
    │   ├── memory.json                all MemoryItem records
    │   ├── index.faiss                binary FAISS index
    │   ├── index_ids.json             id mapping
    │   └── artifacts/                 art:* byte blobs
    │
    ├── scripts/
    │   ├── index_corpus.py            bulk-index all corpus files
    │   ├── run_queries.py             run A–H + C1–C5 queries
    │   └── generate_traces.py        write representative trace JSON
    │
    ├── tests/
    │   ├── test_vector_index.py       FAISS wrapper unit tests (14 tests)
    │   ├── test_memory.py             memory service tests (26 tests)
    │   └── test_tools.py              MCP tool tests (35 tests)
    │
    ├── traces/                        pre-generated demonstration traces
    │   ├── query_A_shannon_wikipedia_extraction.json
    │   ├── query_B_tokyo_activity_weather_plannin.json
    │   ├── query_C_durable_birthday_memory.json          [CROSS-RUN]
    │   ├── query_D_asyncio_research_synthesis.json
    │   ├── query_E_single-document_indexing.json
    │   ├── query_F_cross-run_document_recall.json        [CROSS-RUN]
    │   ├── query_G_synonym_recall_semantic_retrie.json   [SEMANTIC]
    │   ├── query_H_cross-document_synthesis.json
    │   ├── query_C1_custom_shannon_entropy_definit.json
    │   ├── query_C2_custom_tokyo_food_recommendati.json
    │   ├── query_C3_custom_semantic_non-blocking_e.json  [SEMANTIC]
    │   ├── query_C4_custom_lora_vs_full_fine-tunin.json
    │   └── query_C5_custom_semantic_similarity_com.json  [SEMANTIC]
    │
    ├── docs/
    │   └── architecture.md            full architecture documentation
    │
    └── test_mcp_server.py             MCP integration tests (via stdio)
```

---

## Design Decisions

### IndexFlatIP over HNSW

`IndexFlatIP` (exact brute-force inner product) was chosen over approximate indices because:
1. At S7 scale (<10,000 chunks), exact search is <50ms — imperceptible
2. Exact search gives 100% recall — no missed results to diagnose
3. Zero hyperparameters (nprobe, efSearch, M) — nothing to tune
4. No training step required

HNSW or IVF would be appropriate at 100K+ chunks.

### Separate State Files vs SQLite

Memory is stored in three separate files (`memory.json`, `index.faiss`, `index_ids.json`) rather than a database because:
- FAISS requires binary format (cannot be inlined)
- JSON is transparent and inspectable without tooling
- `MemoryItem.embedding` in memory.json enables cold-start recovery without the `.faiss` file

### Scratchpad Items Skip Embedding

Only `fact`, `preference`, and `tool_outcome` are embedded. Scratchpad items are run-scoped intermediate notes — they don't benefit from vector retrieval across sessions and embedding them would waste quota.

---

## Limitations and Future Work

| Current (S7) | Future |
|-------------|--------|
| `IndexFlatIP` — exact, O(n) | HNSW / IVF for million-scale |
| Word-count sliding window | Semantic chunking (S8) |
| Single embedding model fixed at gateway | Model-switching + re-index |
| Keyword fallback uses simple token overlap | BM25 with IDF weighting |
| Vector search only | Hybrid RRF (vector + BM25, S8) |
| No result deduplication | Maximal marginal relevance (MMR) |

---

## Tech Stack

| Component | Library | Version |
|-----------|---------|---------|
| Vector index | `faiss-cpu` | ≥1.8.0 |
| Embeddings | llm_gatewayV7 / sentence-transformers | via gateway |
| Agent loop | `mcp[cli]` + FastMCP | ≥1.0 |
| Data contracts | `pydantic` | ≥2.0 |
| Web tools | `crawl4ai`, `tavily-python`, `ddgs` | latest |
| HTTP client | `httpx` | ≥0.27 |
| Numerics | `numpy` | ≥1.26 |
| Testing | `pytest`, `pytest-asyncio` | ≥8.0 |
| Display | `rich` | ≥13.0 |
