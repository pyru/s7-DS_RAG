# DS_RAG — Agentic RAG with FAISS Vector Memory

**EAGV3 Session 7** · Python + React · FAISS · MCP · LLM Gateway

An agentic Retrieval-Augmented Generation system that proves semantic retrieval outperforms keyword search. The agent runs a 4-layer cognitive loop — Memory → Perception → Decision → Action — over a **56-document corpus** across 8 technical domains.

---

## Architecture

```
User Query
    │
    ▼
┌──────────────────────────────────────────────────────────┐
│  agent7.py  (MAX_ITERATIONS = 20)                        │
│                                                          │
│  ① Memory.read(query)     ← FAISS vector first          │
│  ② Perception.observe()   ← LLM goal decomposition      │
│  ③ Decision.next_step()   ← LLM + 11 MCP tool schemas   │
│  ④ Action.execute()       ← MCP stdio dispatcher        │
│  ⑤ Memory.record_outcome()← embed + FAISS persist       │
└──────────────────────────────────────────────────────────┘
         │                        │
         ▼                        ▼
  state/index.faiss         mcp_server.py
  state/memory.json          11 tools over stdio
```

**Architectural rule**: Perception's SYSTEM prompt contains **zero MCP tool names** — only intent verbs. Tool awareness belongs exclusively in Decision.

---

## Quick Start

### Python Backend

```bash
cd S7code
uv sync
cp .env.example .env        # add your API keys

# Index the 56-document corpus
uv run scripts/index_corpus.py

# Run all 8 required queries
uv run scripts/run_queries.py --save-traces

# Run a single query
uv run agent7.py "What is Shannon entropy?"
```

### React Dashboard

```bash
# Node 18+ required — run from the clean sibling path (# in parent breaks Rollup)
cd ../rag-ui
npm install
npm run dev
# → http://localhost:5173
```

---

## Required Queries (A–H)

| ID | Use Case | Query |
|----|----------|-------|
| A | Artifact fetch + Wikipedia carryover | Who was Claude Shannon and what is his most important contribution? |
| B | Multi-goal planning, memory carryover | Trip to Tokyo in April — activities and weather? |
| C | Durable memory across process restarts | Remember my birthday is 15 July (verified in new process) |
| D | Multi-source synthesis | Python asyncio — event loop, tasks vs coroutines, best patterns |
| E | Single-document on-demand indexing | Index `faiss_vector_store.md`, then query FAISS index types |
| F | Cross-run FAISS persistence | BM25 vs dense retrieval + RRF — zero re-indexing |
| G | **Semantic recall** — zero token overlap | Proximity-based lookup for similar items (retrieves: k-NN, ANN, HNSW) |
| H | Cross-document synthesis | FAISS + sentence transformers + RAG pipeline tradeoffs |

Traces saved in `S7code/traces/`. Each JSON contains: `trace_id`, `query`, iterations with `tool`, `arguments`, `result`, and `memory_new_items`.

---

## Custom Queries (C1–C5)

Each custom trace includes a `no_corpus_comparison` block proving the answer degrades without the index.

| ID | Label | Semantic? | Target Documents |
|----|-------|-----------|-----------------|
| C1 | Shannon entropy definition | No | `claude_shannon_information_theory.md`, `information_theory_basics.md` |
| C2 | Tokyo food recommendations | No | `tokyo_activities_guide.md`, `japan_culture_etiquette.md` |
| C3 | Non-blocking execution patterns | **Yes** | `event_driven_architecture.md` (uses "reactor pattern", "callback chains" — not "asyncio") |
| C4 | LoRA vs full fine-tuning tradeoffs | No | `fine_tuning_llms.md`, `knowledge_distillation.md` |
| C5 | Similarity computation algorithms | **Yes** | `nearest_neighbor_search.md` (uses "proximity queries", "distance computation" — not "vector") |

**Semantic proof — C3**: Query "how do programs handle many tasks simultaneously without blocking" retrieves `event_driven_architecture.md`. That document uses "reactor pattern", "non-blocking I/O", "callback chains" — **zero overlap** with "asyncio", "coroutine", or "async/await".

**Semantic proof — C5**: Query "algorithms that efficiently find similar items in large high-dimensional collections" retrieves `nearest_neighbor_search.md`. No query word appears verbatim in the document.

---

## Corpus Manifest

56 markdown documents in `S7code/sandbox/corpus/` · ~283 chunks after indexing.

| Domain | Count | Key Files |
|--------|-------|-----------|
| Information Theory | 3 | `claude_shannon_information_theory.md`, `information_theory_basics.md`, `data_compression_coding.md` |
| Vector Search & RAG | 6 | `faiss_vector_store.md`, `nearest_neighbor_search.md`, `retrieval_augmented_generation.md`, `hybrid_search_rrf.md`, `semantic_search_techniques.md`, `vector_databases_comparison.md` |
| LLM & ML | 12 | `transformer_architecture.md`, `bert_model_explained.md`, `gpt_evolution.md`, `sentence_transformers_guide.md`, `fine_tuning_llms.md`, `llm_agent_architectures.md`, … |
| Tokyo & Japan | 5 | `tokyo_activities_guide.md`, `tokyo_weather_patterns.md`, `tokyo_neighborhoods.md`, `tokyo_transportation.md`, `japan_culture_etiquette.md` |
| Python & Async | 6 | `python_asyncio_fundamentals.md`, `asyncio_advanced_patterns.md`, `event_driven_architecture.md`, … |
| Systems & Infra | 8 | `distributed_systems_fundamentals.md`, `docker_kubernetes_guide.md`, `api_design_rest.md`, … |
| ML Foundations | 8 | `neural_network_fundamentals.md`, `clustering_algorithms.md`, `linear_algebra_for_ml.md`, … |
| Other | 8 | `model_context_protocol.md`, `knowledge_graphs.md`, `pydantic_guide.md`, `fastapi_tutorial.md`, … |

Full manifest: `S7code/sandbox/corpus/corpus_index.md`

---

## PDF Reference Library

49 reference books in `S7code/sandbox/RAG/` — gitignored due to file size, available locally. These are the source material from which the 56 corpus markdown documents were distilled.

### Python & Data Science (8)
| Title | Author | Year |
|-------|--------|------|
| Python Data Science Handbook | Jake VanderPlas | 2016 |
| Python for Data Analysis | Wes McKinney | 2022 |
| Python Crash Course | Eric Matthes | 2023 |
| Python for Data Science | Yuli Vasiliev | 2022 |
| Python All-in-One For Dummies | Shovic & Simpson | 2021 |
| Python Machine Learning By Example | Yuxi Liu | 2020 |
| Python Programming (Complete Guide) | Nicholas Ayden | 2019 |
| Data Science at the Command Line | Jeroen Janssens | 2014 |

### Machine Learning — Core (7)
| Title | Author | Year |
|-------|--------|------|
| Hands-On Machine Learning with Scikit-Learn, Keras & TensorFlow | Aurélien Géron | 2023 |
| The Hundred-Page Machine Learning Book | Andriy Burkov | 2019 |
| Machine Learning for Absolute Beginners | Oliver Theobald | 2020 |
| Machine Learning Yearning | Andrew Ng | draft |
| Introduction to Machine Learning with Python | Müller & Guido | 2016 |
| Machine Learning Design Patterns | Lakshmanan et al. | 2020 |
| The StatQuest Illustrated Guide to Machine Learning | Josh Starmer | — |

### Deep Learning (3)
| Title | Author | Year |
|-------|--------|------|
| Deep Learning | Goodfellow, Bengio, Courville | 2016 |
| Deep Learning Pipeline with TensorFlow | El-Amir & Hamdy | 2020 |
| Deep Learning with Python | Jason Brownlee | — |

### Statistics & Mathematics (6)
| Title | Author | Year |
|-------|--------|------|
| Think Stats | Allen B. Downey | 2011 |
| Mathematics for Machine Learning | Deisenroth, Faisal, Ong | 2021 |
| Introductory Business Statistics | OpenStax | — |
| Foundations of Probabilistic Programming | Barthe, Katoen, Silva | 2021 |
| Introduction to Statistical Relational Learning | Getoor & Taskar | 2007 |
| Modeling and Simulation in Python | Allen B. Downey | 2023 |

### Systems & Engineering (5)
| Title | Author | Year |
|-------|--------|------|
| Designing Machine Learning Systems | Chip Huyen | 2022 |
| Designing Data-Intensive Applications | Martin Kleppmann | 2018 |
| Fundamentals of Data Engineering | Reis & Housley | 2022 |
| System Design Interview | Alex Xu | 2020 |
| Machine Learning Design Interview | Khang Pham | 2022 |

### Algorithms & Coding (6)
| Title | Author | Year |
|-------|--------|------|
| Grokking Algorithms | Aditya Bhargava | 2016 |
| Data Structures and Algorithm Analysis in Java | Mark Allen Weiss | 2012 |
| Cracking the Coding Interview | Gayle Laakmann McDowell | 2015 |
| The Recursive Book of Recursion | Al Sweigart | 2022 |
| Programming Interview Problems: Dynamic Programming | Leonardo Rossi | 2020 |
| Machine Learning Algorithms From Scratch | Jason Brownlee | 2018 |

### Interview Preparation (5)
| Title | Author | Year |
|-------|--------|------|
| DSI ACE PREP — Data Science Interview Handbook | Data Science Interview Books | — |
| Data Science & ML Interview Questions Using Python | Vishwanathan Narayanan | — |
| 500 Most Important Data Science Interview Q&A | Vamsee Puligadda | 2018 |
| 120 Real Data Science Interview Questions | Shan, Song, Wang, Chen | 2015 |
| Data Science from Scratch | Steven Cooper | — |

### Visualization & BI (5)
| Title | Author | Year |
|-------|--------|------|
| Data Storytelling and Visualization with Tableau | Joshi & Mahalle | 2022 |
| The Tableau Workshop | Gupta, Pinto et al. | — |
| Microsoft Power BI For Dummies | Jack A. Hyman | 2022 |
| Excel Data Analysis For Dummies | Paul McFedries | 2022 |
| Excel All-in-One | McFedries & Harvey | 2022 |

### Other (4)
| Title | Author | Year |
|-------|--------|------|
| Imbalanced Classification with Python | Jason Brownlee | 2020 |
| Chaos: Making a New Science | James Gleick | — |
| Introduction to Statistical Relational Learning | Getoor & Taskar | 2007 |
| Linux For Dummies | Richard Blum | 2020 |

> **Note:** PDFs are excluded from git (`sandbox/RAG/` is in `.gitignore`). The 56 indexed markdown documents in `sandbox/corpus/` are distilled summaries that fit within the embedding model's 512-token chunk limit.

---

## MCP Tools (11 total)

| Tool | Purpose |
|------|---------|
| `web_search` | Tavily / DDGS web search |
| `fetch_url` | Crawl4AI page fetch → artifact if >4 KB |
| `get_time` | Current UTC datetime |
| `currency_convert` | FX rate lookup |
| `read_file` | Sandbox file read |
| `list_dir` | Sandbox directory listing |
| `create_file` | Create file in sandbox |
| `update_file` | Overwrite file in sandbox |
| `edit_file` | Patch file (old→new string) |
| `index_document` | Chunk + embed + FAISS-store a document |
| `search_knowledge` | FAISS vector search over indexed corpus |

`index_document` and `search_knowledge` are the Session 7 additions. Their docstrings teach Decision when to use them versus re-fetching.

---

## Dashboard (`rag-ui/`)

React + TypeScript + Vite SPA with two pages:

| Page | Route | What it shows |
|------|-------|---------------|
| **Queries** | `/queries` | 8 evaluation query cards with live trace streaming (380 ms/event) and stat tiles |
| **RAG Documents** | `/documents` | RAG Query Playground (category-aware prompts, Ctrl+Enter) + 56-document corpus browser |

---

## Project Structure

```
S7#DS_RAG/
├── README.md                       ← this file
├── .gitignore
│
├── S7code/                         Python agent backend
│   ├── agent7.py                   main async agent loop (MAX_ITERATIONS=20)
│   ├── perception.py               LLM goal decomposer — zero tool names in SYSTEM
│   ├── decision.py                 LLM tool selector + answer writer
│   ├── action.py                   MCP stdio dispatcher + artifact routing
│   ├── memory.py                   FAISS + keyword memory service
│   ├── vector_index.py             IndexFlatIP wrapper (exact cosine via L2-norm)
│   ├── mcp_server.py               FastMCP — 11 tools over stdio
│   ├── sandbox/corpus/             56 markdown documents (gitignored: state/)
│   ├── scripts/                    index_corpus.py, run_queries.py
│   ├── tests/                      75 unit tests (vector_index, memory, tools)
│   └── traces/                     13 JSON traces (A–H base + C1–C5 custom)
│
├── llm_gatewayV7/                  FastAPI LLM gateway (chat + embed endpoints)
│
└── rag-ui/                         React dashboard (Vite + TypeScript)
    └── src/
        ├── components/             QueriesPage, DocumentsPage, QueryCard, Navbar
        ├── context/RunsContext.tsx global state + localStorage persistence
        └── data/                   queries.ts, traces.ts, documents.ts
```

---

## Submission Checklist

- [x] 8 base query traces (A–H) in `S7code/traces/`
- [x] 5 custom traces (C1–C5) with `no_corpus_comparison` blocks
- [x] 2 semantic queries with zero token overlap proof (C3, G)
- [x] 56-document corpus in `S7code/sandbox/corpus/`
- [x] Perception SYSTEM grep test: zero MCP tool names
- [x] FAISS cross-run persistence (`IndexFlatIP`, `state/index.faiss`)
- [x] React evaluation dashboard (`rag-ui/`)
- [ ] Short demo video (record locally)
