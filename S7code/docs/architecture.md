# DS_RAG Architecture

Session 7 of the EAGV3 (Evolving Agentic Generation V3) project. Adds FAISS-backed vector memory and on-demand document indexing to the S6 cognitive architecture. Paired with a React evaluation dashboard (`rag-ui/`) for live query execution and trace inspection.

---

## High-Level Overview

```
User Query
    │
    ▼
┌──────────────────────────────────────────────────────┐
│                     agent7.py                        │
│                                                      │
│  Memory.read() ──► Perception ──► Decision ──► Action│
│       ▲                │              │         │    │
│       │                ▼              │         │    │
│       └──── Memory.record_outcome ◄──┘         │    │
│                        │                        │    │
│                        └──── Answer ────────────┘    │
└──────────────────────────────────────────────────────┘
         │                                    │
         ▼                                    ▼
  state/memory.json                    MCP Server (stdio)
  state/index.faiss                    11 tools
  state/index_ids.json
  state/artifacts/
```

---

## Layer Descriptions

### 1. Perception (`perception.py`)

Receives: user query + prior memory hits + prior iteration history  
Produces: `Observation` with a typed `Goal` list

- Calls one LLM (routed `auto_route="perception"`)
- Decomposes the query into atomic goals on iteration 1
- Marks goals done as they are satisfied
- **Never mentions MCP tool names** (tool awareness belongs in Decision)
- Tracks an `attach_artifact_id` per goal when raw bytes are needed downstream

### 2. Decision (`decision.py`)

Receives: current goal + memory context + MCP tool schemas + conversation history  
Produces: `DecisionOutput` — either `answer` or `tool_call`

- Single LLM call per iteration (routed `auto_route="decision"`)
- Injects full MCP tool schemas so the model can choose the right tool
- Embeds artifact content at `[HEAD:20000]…[TAIL:10000]` so the model sees large pages
- Emits a JSON-structured tool call or a final answer text

### 3. Action (`action.py`)

Receives: `ToolCall` from Decision  
Produces: `(descriptor, artifact_id | None)`

- Dispatches the tool call to the MCP server over stdio
- If the result exceeds 4096 bytes → stores it in the artifact store (content-addressable SHA-256) and returns an `art:` handle
- Blocks artifact handles from being naively passed back to file/URL tools

### 4. Memory (`memory.py`)

Two read paths, one write path:

```
read(query)
    │
    ├─► vector_search()   — FAISS IndexFlatIP over embedded descriptors
    │       │ hit → return
    │       │ miss ↓
    └─► keyword_search()  — token-overlap fallback (S6 path)

write:
    add_fact()          — direct fact write (document indexing tools use this)
    record_outcome()    — tool outcome write (Action calls this)
    remember()          — LLM-classified write (agent loop uses for user input)
```

Embeddable kinds: `fact`, `preference`, `tool_outcome`  
Non-embeddable: `scratchpad` (run-scoped)

---

## Vector Memory Design

### FAISS Index (`vector_index.py`)

```
┌─────────────────────────────────────────────┐
│  VectorIndex                                │
│                                             │
│  _index:  faiss.IndexFlatIP  (inner prod)   │
│  _ids:    list[str]          (parallel ids) │
│  _dim:    int | None                        │
│                                             │
│  add(id, embedding)  → L2-normalize → add  │
│  search(query_emb, k) → [(id, score), ...]  │
│  persist() → state/index.faiss              │
│                          state/index_ids.json│
│  clear()  → delete both files               │
└─────────────────────────────────────────────┘
```

**Why IndexFlatIP on L2-normalized vectors?**  
For unit-norm vectors, inner product equals cosine similarity:

```
cosine(a, b) = (a · b) / (|a| |b|) = a · b  [when |a|=|b|=1]
```

This gives exact cosine nearest-neighbor search with no approximation. At S7 scale (thousands of chunks), brute-force is fast enough. HNSW or IVF would replace this in Session 8 for million-scale.

### Embedding Pipeline

```
text descriptor
      │
      ▼
gateway.embed(text, task_type)
      │
      ▼ POST /v1/embed → llm_gatewayV7
      │
      ▼
{embedding: [float × 384], model: "...", latency_ms: ...}
      │
      ▼
VectorIndex.add(item_id, embedding)
```

`task_type` is set to `"retrieval_document"` at write time and `"retrieval_query"` at read time, matching asymmetric embedding models (e.g., `all-MiniLM-L6-v2`).

---

## MCP Tool Registry

The server exposes 11 tools via stdio transport (FastMCP):

| Tool | Category | Description |
|------|----------|-------------|
| `web_search` | Web | Tavily primary, DuckDuckGo fallback; capped at 5 results |
| `fetch_url` | Web | crawl4ai headless Chromium → clean markdown |
| `get_time` | Utility | IANA timezone → ISO-8601 + human-readable |
| `currency_convert` | Utility | frankfurter.dev exchange rates |
| `read_file` | Filesystem | UTF-8 read from sandbox |
| `list_dir` | Filesystem | Directory listing with type/size |
| `create_file` | Filesystem | Create (errors if exists) |
| `update_file` | Filesystem | Overwrite existing file |
| `edit_file` | Filesystem | Find-and-replace (single or replace_all) |
| `index_document` | RAG | Chunk file → embed → write facts to FAISS |
| `search_knowledge` | RAG | Vector search over indexed fact chunks |

**Sandboxing**: All filesystem tools call `_safe(path)` which resolves and verifies the path is under `./sandbox/`. Any `../` traversal raises `ValueError("escapes the sandbox")`.

---

## Artifact Store (`artifacts.py`)

Large tool results (>4 KB) are stored content-addressably:

```
result bytes
     │
     ▼
SHA-256 hash → art:{hex8}
     │
     ▼
state/artifacts/{hex8}.bytes   (raw content)
state/artifacts/{hex8}.meta    (JSON: size, content_type, source, descriptor)
```

Decision sees the `art:` handle and retrieves `[HEAD:20000][TAIL:10000]` slices for context-window-safe grounding.

---

## Data Flow: Full Iteration

```
Iteration N
────────────────────────────────────────────────────────
1. Perception.observe(query, memory_hits, history)
        → Observation(goals=[Goal(...), ...])

2. obs.next_unfinished() → current_goal

3. Decision.next_step(goal, tools, history)
        → DecisionOutput(tool_call=ToolCall(name, args))
   OR   → DecisionOutput(answer="...")

4. Action.execute(tool_call)
        → (descriptor, artifact_id)
           stores >4KB results in artifact store

5. Memory.record_outcome(tool_call, result, artifact_id)
        → MemoryItem(kind="tool_outcome", embedding=...)
           persisted to memory.json + FAISS index

6. Perception re-evaluates: mark goal done if satisfied

→ repeat until obs.all_done or MAX_ITERATIONS=20
```

---

## Cross-Run Persistence

```
Run 1 (index_corpus.py):                Run 2 (agent7.py Q: "What is RRF?"):
─────────────────────────               ────────────────────────────────────
hybrid_search_rrf.md                    agent7 starts
    → chunk(400w/80w overlap)           memory.read("RRF fusion") called
    → embed each chunk                  → _index() loads index.faiss
    → VectorIndex.add(id, vec)          → FAISS finds chunk from Run 1
    → VectorIndex.persist()             → returns result WITHOUT re-fetching
    → state/index.faiss written         ↑ cross-run persistence demonstrated
```

State files written to `state/` directory:
- `state/memory.json` — all `MemoryItem` records
- `state/index.faiss` — binary FAISS index
- `state/index_ids.json` — parallel string id list
- `state/artifacts/` — content-addressable byte store

---

## Semantic Retrieval Demonstration

Queries G and C3 prove semantic-only retrieval (no keyword overlap):

**Query G**: "Explain how proximity-based lookup works for finding similar items in large collections."

Retrieves `nearest_neighbor_search.md` which contains:
- "k-NN", "approximate nearest neighbor", "proximity queries", "distance computation"
- Does **NOT** contain: "vector similarity", "FAISS", "cosine similarity"

The retrieval succeeds purely via embedding similarity — the embedded query vector is close to the embedded document vectors despite zero token overlap.

**Why this works**: Both "proximity-based lookup" and "k-nearest-neighbor" map to similar regions in the embedding space because they describe the same mathematical concept. The sentence transformer model captures this conceptual equivalence.

---

## Document Chunking

```python
def _chunk_text(text, size=400, overlap=80):
    words = text.split()
    stride = size - overlap   # 320 words
    for i in range(0, len(words), stride):
        yield " ".join(words[i:i+size])
        if i + size >= len(words): break
```

- **Size 400 words** ≈ 2,000–2,500 characters: fits within embedding model context (512 tokens for MiniLM)
- **Overlap 80 words**: ensures sentences spanning chunk boundaries are captured by both chunks
- **Sliding window**: simple, deterministic, reproducible across runs

Each chunk descriptor includes provenance: `[corpus:filename.md chunk 3/7] first 120 chars...`

---

## Corpus Summary

56 markdown documents in `sandbox/corpus/`, covering:

| Domain | Count | Key Files |
|--------|-------|-----------|
| Information Theory | 3 | claude_shannon_information_theory.md, information_theory_basics.md, data_compression_coding.md |
| Vector Search / RAG | 5 | faiss_vector_store.md, nearest_neighbor_search.md, retrieval_augmented_generation.md, hybrid_search_rrf.md, semantic_search_techniques.md |
| Python / Async | 5 | python_asyncio_fundamentals.md, asyncio_advanced_patterns.md, event_driven_architecture.md, python_concurrency.py, python_type_hints.md |
| Tokyo / Japan | 5 | tokyo_activities_guide.md, tokyo_weather_patterns.md, tokyo_neighborhoods.md, tokyo_transportation.md, japan_culture_etiquette.md |
| LLM / ML | 12 | transformer_architecture.md, bert_model_explained.md, gpt_evolution.md, fine_tuning_llms.md, llm_scaling_laws.md, ... |
| Systems / Infra | 8 | distributed_systems_fundamentals.md, docker_kubernetes_guide.md, microservices_patterns.md, ... |
| Other CS | 18 | data_structures_algorithms.md, git_version_control.md, network_security_basics.md, ... |

---

---

## Frontend Architecture (rag-ui)

The `rag-ui/` React dashboard is a read-only evaluation interface. It does not call the Python backend directly; instead it ships with mock traces and a simulated query runner to demonstrate the agent behaviour without requiring the backend to be running.

### Component Tree

```
App (BrowserRouter + RunsProvider)
│
├── Navbar                          tab navigation, run-count badge
│
├── Routes
│   ├── /           DocumentsPage   document browser + inline QueryRunner
│   ├── /queries    QueriesPage     8 evaluation queries + live status counters
│   └── /traces     TracesPage      run history sidebar + trace detail panel
```

### Global State — RunsContext

All mutable UI state lives in a single React context that wraps the whole app. Three slices, all persisted to `localStorage`:

```
RunsContext
├── runs           TraceRun[]          — full history of executed runs
├── activeRunId    string | null       — which run is shown in TracesPage
└── statusMap      Record<id, status>  — per-query status for QueriesPage
```

State is initialised from `localStorage` on first mount (lazy `useState` initialiser) and written on every mutation. This makes it survive navigation (React Router unmounts pages on route change) and browser refresh (`F5`).

```
localStorage keys
  dsrag:runs         JSON array of TraceRun objects
  dsrag:activeRunId  active run ID string
  dsrag:statusMap    { "query-a": "completed", "query-b": "not_started", ... }
```

### Page Breakdown

#### DocumentsPage — `/`

```
DocumentsPage
├── DocsStats              summary counters (total / indexed / stale / pending / chunks)
├── Toolbar                search box + status dropdown + category dropdown
├── DocumentTable          sortable, filterable table of 4 Indian Tax documents
└── QueryRunner            self-contained inline query runner (no backend)
    ├── suggestion chips   5 pre-written Indian tax question prompts
    ├── <textarea>         free-form query input (Ctrl+Enter to run)
    ├── Live trace log     event-by-event simulation (memory → perception → decision → action)
    └── Result panel       keyword-matched statutory answer with chunk citations
```

**QueryRunner simulation**: `buildScript(query)` returns a timed sequence of `{ delay, event }` objects fired via `setTimeout`. `buildResult(query)` pattern-matches on keywords (`slab`, `tds`, `80c`, `budget`, `advance tax`) to return a realistic statutory answer. `timersRef` stores all timer IDs so `handleClear` can cancel mid-run.

#### QueriesPage — `/queries`

```
QueriesPage (reads statusMap from RunsContext)
├── QueriesStats           4 counter cards: not_started / running / completed / failed
└── <QueryCard × 8>        one card per evaluation query (A–H)
    ├── status badge        controlled by statusMap[query.id]
    ├── Run Query button    fires: onStatusChange('running') → addRun() → setTimeout 2s → onStatusChange('completed')
    └── "View trace →"     Link (clickable when running/completed) or plain span (not started)
```

Status propagation:
1. `QueriesPage` passes `onStatusChange` down to each `QueryCard`
2. `QueryCard` calls `onStatusChange('running')`, then 2 s later `onStatusChange('completed')`
3. `QueriesPage` calls `updateQueryStatus(id, s)` which writes to `RunsContext`
4. `RunsContext` persists to `localStorage` — survives navigation + refresh

#### TracesPage — `/traces`

```
TracesPage (reads runs, activeRunId from RunsContext)
├── Sidebar (trace-sidebar)
│   └── RunItem × N        query label + status dot + date/time/elapsed
└── Detail panel (trace-main)
    └── TraceDetail
        ├── Run header      label, runId, date, elapsed, iteration count
        ├── Query text      full query text in <pre>
        ├── Execution log   per-iter grouped trace events
        │   └── TraceLine   [component] ○/✓/✗ message
        └── Result panel    final synthesised answer
```

### Data Flow: Running a Query from QueriesPage

```
1. User clicks "Run Query" on QueryCard
       │
       ▼
2. handleRun() in QueryCard
   ├── onStatusChange('running')          → RunsContext.updateQueryStatus → localStorage
   ├── builds TraceRun from MOCK_TRACES template (or creates empty shell)
   └── addRun(newRun)                     → RunsContext.addRun → localStorage
       │
       ▼
3. RunsContext.activeRunId = newRun.runId → localStorage

4. After 2s:  onStatusChange('completed') → RunsContext.updateQueryStatus → localStorage

5. User navigates to /traces
   → TracesPage reads runs from RunsContext (not re-fetched, already in memory + localStorage)
   → Shows the new run at top of sidebar, auto-selected
```

### CSS Design System

All styles live in `src/index.css`. A set of CSS custom properties forms the design token layer:

```css
:root {
  --bg-primary, --bg-surface-1, --bg-surface-2   /* dark backgrounds */
  --text-primary, --text-secondary, --text-muted
  --accent                                        /* purple #7c6fe0 */
  --green, --blue, --yellow, --red                /* status colours */
  --border, --border-accent
  --mono                                          /* JetBrains Mono / monospace */
  --radius-sm, --radius-md, --radius-lg
}
```

Component classes: `.query-runner`, `.suggested-queries`, `.suggestion-chip`, `.runner-trace`, `.runner-result`, `.trace-sidebar`, `.trace-detail`, `.stats-row`, `.stat-card`, `.query-card`, `.status-badge`.

---

## Directory Structure

```
S7code/
├── agent7.py                   ← main agent loop
├── perception.py               ← goal decomposition / tracking
├── decision.py                 ← tool selection / answer synthesis
├── action.py                   ← MCP dispatcher + artifact store
├── memory.py                   ← vector + keyword memory service
├── vector_index.py             ← FAISS wrapper (IndexFlatIP)
├── artifacts.py                ← content-addressable byte store
├── schemas.py                  ← Pydantic contracts
├── gateway.py                  ← llm_gatewayV7 bridge + embed()
├── mcp_server.py               ← FastMCP server (11 tools)
├── pyproject.toml
├── requirements.txt
│
├── sandbox/corpus/             ← 56 markdown documents
├── state/                      ← persistent state (gitignored)
│   ├── memory.json
│   ├── index.faiss
│   ├── index_ids.json
│   └── artifacts/
│
├── scripts/
│   ├── index_corpus.py         ← bulk-index all corpus docs
│   ├── run_queries.py          ← run A–H + custom queries
│   └── generate_traces.py      ← write representative trace files
│
├── tests/
│   ├── test_vector_index.py    ← FAISS wrapper unit tests
│   ├── test_memory.py          ← memory service unit tests
│   └── test_tools.py           ← MCP tools unit tests
│
├── traces/                     ← pre-generated JSON trace files
│   ├── query_A_*.json
│   ├── query_G_*_SEMANTIC_*.json
│   └── ...
│
└── docs/
    └── architecture.md         ← this file
```
