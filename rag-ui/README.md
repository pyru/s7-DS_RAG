# DS_RAG Dashboard

Evaluation UI for the DS_RAG agentic RAG system (EAGV3 Session 7).  
Built with React + TypeScript + Vite. Runs fully standalone — no Python backend required.

---

## Quick Start

```bash
# Node 18+ required
cd rag-ui
npm install
npm run dev
# → http://localhost:5173
```

> **Windows note:** The `#` in `S7#DS_RAG/` conflicts with Rollup's URL parser.  
> Run the dev server from the clean sibling copy at `../rag-ui/` instead.

---

## Pages

### Queries — `/queries`

Eight predefined evaluation queries (A–H) covering the main agent capabilities.

| Query | Use Case | Topic |
|-------|----------|-------|
| A | Artifact fetch + carryover | Claude Shannon / Wikipedia |
| B | Multi-goal, memory carryover | Tokyo activities + weather |
| C | Durable memory across runs | Mom's birthday reminders |
| D | Multi-source synthesis | Python asyncio best practices |
| E | RAG indexing | Index a single paper then query it |
| F | FAISS persistence | Cross-run document recall |
| G | Vector beats keyword | Synonym / semantic recall |
| H | RAG synthesis | Cross-document comparison |

**What you can do:**
- Click **Run Query** on any card to see a real-time streaming execution trace
- Watch each iteration unfold — `memory.read → perception → decision → action` — at 380 ms per step
- Read the final synthesised result when the run completes
- Four stat tiles (Not Started / Running / Completed / Failed) update live as queries run
- Each card shows 3 sample prompts for that use case

### RAG Documents — `/documents`

Corpus browser for all 50 indexed documents across 8 categories.

**Stats row** — total documents, indexed count, stale count, not-indexed count, total chunks.

**RAG Query Playground** — type any prompt and watch the full RAG pipeline trace:
1. Pick a category from the dropdown (or leave at All Categories)
2. Sample prompts update automatically to match the selected category
3. Click a chip or type your own question — Ctrl+Enter to run
4. Watch the live trace stream, then read the synthesised result

**Document table** — searchable, filterable by status and category.  
Columns: ID, file name, title, category, chunk count, status badge, last indexed date, view action.

---

## Categories

| Category | Documents |
|----------|-----------|
| Foundational Architecture | 6 |
| Prompting & Reasoning | 7 |
| Agent Frameworks | 9 |
| RAG & Retrieval | 10 |
| Models & Training | 6 |
| Infrastructure | 5 |
| Evaluation & Benchmarks | 5 |
| Multimodal | 2 |

---

## Tech Stack

| Concern | Choice |
|---------|--------|
| Framework | React 18 |
| Language | TypeScript 5 |
| Build tool | Vite 5 |
| Routing | React Router v6 |
| State | React Context + localStorage |
| Styling | Plain CSS custom properties |
| Icons | Inline SVG (no icon library) |

---

## Key Files

| File | What it does |
|------|-------------|
| `src/App.tsx` | Router + `RunsProvider` wrapper |
| `src/index.css` | All styles — design tokens, components, animations |
| `src/context/RunsContext.tsx` | Global state: runs, status map, active run — persisted to localStorage |
| `src/components/QueriesPage.tsx` | Queries page — live stat tiles + 8 query cards |
| `src/components/QueryCard.tsx` | Individual card — run button, sample prompts, inline trace panel |
| `src/components/DocumentsPage.tsx` | Documents page — RAG Query Playground + document table |
| `src/components/Navbar.tsx` | Top nav bar |
| `src/data/queries.ts` | 8 evaluation query definitions (text, tags, sample prompts) |
| `src/data/traces.ts` | Pre-built mock traces for all 8 queries |
| `src/data/documents.ts` | 50 document records for the corpus table |
| `src/types/index.ts` | Shared TypeScript types |

---

## State Persistence

All state lives in `RunsContext` and survives browser refresh via `localStorage`:

| Key | Contents |
|-----|----------|
| `dsrag:runs` | Full history of executed runs |
| `dsrag:activeRunId` | Currently selected run |
| `dsrag:statusMap` | Per-query status (`not_started` / `running` / `completed` / `failed`) |
