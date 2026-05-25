# Architecture — DS_RAG Dashboard

---

## Component Tree

```
App
├── RunsProvider          (global state + localStorage)
├── Navbar                (tab bar — Queries | RAG Documents)
└── Routes
    ├── /queries          QueriesPage
    │   ├── QueriesStats  (live tile counters from RunsContext)
    │   └── QueryCard × 8
    │       ├── StatusBadge
    │       ├── Sample prompts (chips)
    │       ├── Run / Copy buttons
    │       └── InlineTrace panel (streams on run)
    │
    └── /documents        DocumentsPage
        ├── DocsStats     (total / indexed / stale / not-indexed / chunks)
        ├── QueryPlayground
        │   ├── Textarea + Run button
        │   ├── Category-aware sample chips
        │   └── InlineTrace panel (streams on run)
        ├── Toolbar       (search input + status filter + category dropdown)
        └── DocumentTable
```

---

## State Management

One context (`RunsContext`) holds all mutable state. It wraps the whole app so every component can read or write without prop drilling.

```
RunsContext
├── runs: TraceRun[]              full history of executed runs
├── activeRunId: string | null    selected run (used by trace viewer)
└── statusMap: Record<id, status> live status for each of the 8 eval queries
```

**Mutations available to components:**

| Function | What it does |
|----------|-------------|
| `addRun(run)` | Prepends a new run, sets it as active |
| `updateRun(id, patch)` | Patches an existing run (e.g. status → completed, adds result) |
| `updateQueryStatus(id, status)` | Updates a single query's live status badge |
| `setActiveRunId(id)` | Changes which run is highlighted |

Every mutation immediately writes to `localStorage` so state survives page refresh.

---

## Trace Streaming — How it Works

Both `QueryCard` and `QueryPlayground` use the same pattern:

```
1. User clicks Run
2. Find matching mock trace (MOCK_TRACES or resolvePlaygroundTrace)
3. Clear previous timers + state
4. Mark status = 'running', open trace panel
5. Schedule one setTimeout per event at (index + 1) × 380 ms
   → each fires setLiveEvents(prev => [...prev, event])
6. Final timer at (events.length + 2) × 380 ms:
   → setLiveResult(result)
   → mark status = 'completed'
   → call updateRun() to persist the finished run
7. Timer IDs stored in timersRef — cleared on reset or unmount
```

Event colours in the trace log:

| Component | Colour |
|-----------|--------|
| `memory.read` | Blue |
| `perception` | Purple (accent) |
| `decision` | Yellow |
| `action` | Green |
| `system` | Muted grey |

---

## QueryPlayground — Category-Aware Prompts

The playground on the Documents page derives its sample prompts from the category dropdown selection.

```
categoryFilter (state in DocumentsPage)
    │
    ├── passed as prop to → QueryPlayground
    │       └── CATEGORY_PROMPTS[category] → renders sample chips
    │
    └── passed to → DocumentTable filter
```

When `categoryFilter` changes:
- Sample chips swap to the new category's 4 prompts
- Any in-progress trace is cancelled and the panel resets
- The document table filters to show only that category's documents

Categories and their prompts are defined in `CATEGORY_PROMPTS` inside `DocumentsPage.tsx`.

---

## Mock Trace Resolution

`resolvePlaygroundTrace(query)` matches the typed query to the best available mock trace:

```
query text
    │
    ├── contains "transformer" / "attention"   → trace-e (attention.md RAG)
    ├── contains "react" / "reasoning"         → trace-h (cross-doc synthesis)
    ├── contains "credit assignment"           → trace-g (synonym recall)
    ├── contains "asyncio" / "python"          → trace-d (multi-source)
    ├── contains "shannon" / "entropy"         → trace-a (Wikipedia fetch)
    ├── contains "tokyo" / "weather"           → trace-b (multi-goal)
    ├── contains "birthday" / "reminder"       → trace-c (durable memory)
    └── no match                               → generic 2-iter RAG trace
```

The 8 mock traces in `src/data/traces.ts` each contain:
- `events[]` — per-iteration trace events with component, status symbol, message
- `result` — the final synthesised answer (markdown)

---

## Data Flow Diagram

```
User clicks Run Query
        │
        ▼
QueryCard.handleRun()
  │  ├─ updateQueryStatus(id, 'running')    ──► RunsContext ──► localStorage
  │  ├─ addRun(newRun)                       ──► RunsContext ──► localStorage
  │  └─ scheduleEvents(MOCK_TRACES[id])
        │
        │  380ms per event
        ▼
setLiveEvents([...prev, event])
        │
        ▼
  trace panel re-renders with new row (fadeInLine animation)
        │
  (final timer fires)
        ▼
updateRun(id, { status:'completed', result, finishedAt })
        │
        ▼
RunsContext ──► localStorage
```

---

## File Map

```
rag-ui/
├── src/
│   ├── App.tsx                   router + RunsProvider
│   ├── main.tsx                  ReactDOM entry
│   ├── index.css                 design tokens + all component styles
│   ├── context/
│   │   └── RunsContext.tsx       global state, localStorage persistence
│   ├── components/
│   │   ├── Navbar.tsx
│   │   ├── QueriesPage.tsx       live stat tiles + query grid
│   │   ├── QueryCard.tsx         card + inline trace streaming
│   │   ├── DocumentsPage.tsx     playground + document table
│   │   └── DocumentTable.tsx     filterable corpus table
│   ├── data/
│   │   ├── queries.ts            8 evaluation queries
│   │   ├── traces.ts             pre-built mock traces (A–H)
│   │   └── documents.ts          50 corpus document records
│   └── types/
│       └── index.ts              Query, TraceRun, TraceEvent, RagDocument, …
├── README.md
└── Architecture.md
```
