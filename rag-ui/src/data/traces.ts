import type { TraceRun } from '../types';
import { QUERIES } from './queries';

// ------------------------------------------------------------------
// Pre-built mock execution traces for each query.
// For live backend: replace with SSE stream from
//   GET /api/runs/:runId/stream  →  TraceEvent[]
// ------------------------------------------------------------------

function q(id: string) {
  return QUERIES.find((x) => x.id === id)!;
}

export const MOCK_TRACES: TraceRun[] = [
  // ── Query A: Shannon Wikipedia ───────────────────────────────────
  {
    runId: 'run-a-001',
    queryId: 'query-a',
    queryLabel: q('query-a').label,
    queryTitle: q('query-a').title,
    queryText: q('query-a').text,
    startedAt: '2026-05-24T08:14:02Z',
    finishedAt: '2026-05-24T08:14:19Z',
    status: 'completed',
    iters: 2,
    result: `Claude Shannon (April 30, 1916 – February 24, 2001) was an American mathematician, electrical engineer, and cryptographer.

**Birth date:** April 30, 1916 (Petoskey, Michigan, USA)
**Death date:** February 24, 2001 (Medford, Massachusetts, USA)

**Three key contributions to information theory:**

1. **A Mathematical Theory of Communication (1948)** — Shannon's landmark paper defined *information entropy* as the fundamental measure of information content and uncertainty, establishing the mathematical foundations of modern communication systems.

2. **Source Coding Theorem (Shannon's First Theorem)** — Proved that the entropy of a source is the theoretical lower bound on the average number of bits needed to encode its output, formalizing lossless data compression limits.

3. **Channel Capacity Theorem (Shannon's Second Theorem / Noisy Channel Coding Theorem)** — Demonstrated that error-free digital communication is achievable at any rate below the channel capacity \`C = B log₂(1 + S/N)\`, where B is bandwidth and S/N is the signal-to-noise ratio.`,
    events: [
      { iter: 1, component: 'memory.read',  status: null, message: '0 hits' },
      { iter: 1, component: 'perception',   status: '○',  message: 'Fetch the Claude Shannon Wikipedia page' },
      { iter: 1, component: 'perception',   status: '○',  message: 'Extract birth date, death date, and 3 key contributions' },
      { iter: 1, component: 'decision',     status: null, message: 'TOOL_CALL: fetch_url({"url": "https://en.wikipedia.org/wiki/Claude_Shannon"})' },
      { iter: 1, component: 'action',       status: null, message: '→ Status 200 · 44,821 bytes · text/markdown' },

      { iter: 2, component: 'memory.read',  status: null, message: '4 hits' },
      { iter: 2, component: 'perception',   status: '✓',  message: 'Fetch the Claude Shannon Wikipedia page' },
      { iter: 2, component: 'perception',   status: '○',  message: 'Extract birth date, death date, and 3 key contributions' },
      { iter: 2, component: 'decision',     status: null, message: 'ANSWER' },
    ],
  },

  // ── Query B: Tokyo activities + weather ──────────────────────────
  {
    runId: 'run-b-001',
    queryId: 'query-b',
    queryLabel: q('query-b').label,
    queryTitle: q('query-b').title,
    queryText: q('query-b').text,
    startedAt: '2026-05-24T08:22:10Z',
    finishedAt: '2026-05-24T08:22:41Z',
    status: 'completed',
    iters: 3,
    result: `**Top 3 family-friendly activities in Tokyo this weekend:**

1. **Ueno Zoo & Ueno Park** — Japan's oldest zoo with 3,000+ animals. Free admission to the park; zoo ¥600/adult. Great for kids of all ages.
2. **teamLab Borderless (Odaiba)** — Immersive digital art museum; children love the interactive light installations. Book in advance (¥3,200/adult, ¥1,000/child).
3. **Senso-ji Temple (Asakusa)** — Tokyo's most visited temple with a lively Nakamise shopping street. Free entry; street food for the whole family.

**Saturday weather forecast (Tokyo):** 26°C, partly cloudy, 10% rain chance, light southerly breeze.

**Best choice given the weather:** **Ueno Zoo & Park** — The mild partly-cloudy conditions make it ideal for an outdoor half-day. teamLab is indoors and better saved for a rainy day. Senso-ji is also viable but gets very crowded on fair-weather weekends.`,
    events: [
      { iter: 1, component: 'memory.read',  status: null, message: '0 hits' },
      { iter: 1, component: 'perception',   status: '○',  message: 'Search for 3 family-friendly Tokyo activities' },
      { iter: 1, component: 'perception',   status: '○',  message: 'Check Saturday weather in Tokyo' },
      { iter: 1, component: 'decision',     status: null, message: 'TOOL_CALL: web_search({"query": "family friendly things to do Tokyo this weekend 2026", "max_results": 5})' },
      { iter: 1, component: 'action',       status: null, message: '→ 5 results returned (Tavily)' },

      { iter: 2, component: 'memory.read',  status: null, message: '3 hits' },
      { iter: 2, component: 'perception',   status: '✓',  message: 'Search for 3 family-friendly Tokyo activities' },
      { iter: 2, component: 'perception',   status: '○',  message: 'Check Saturday weather in Tokyo' },
      { iter: 2, component: 'decision',     status: null, message: 'TOOL_CALL: web_search({"query": "Tokyo weather forecast Saturday May 2026"})' },
      { iter: 2, component: 'action',       status: null, message: '→ 5 results returned (Tavily)' },

      { iter: 3, component: 'memory.read',  status: null, message: '6 hits' },
      { iter: 3, component: 'perception',   status: '✓',  message: 'Check Saturday weather in Tokyo' },
      { iter: 3, component: 'perception',   status: '○',  message: 'Recommend best activity given the forecast' },
      { iter: 3, component: 'decision',     status: null, message: 'ANSWER' },
    ],
  },

  // ── Query C: Mom's birthday – Run 1 ─────────────────────────────
  {
    runId: 'run-c-001',
    queryId: 'query-c',
    queryLabel: q('query-c').label,
    queryTitle: q('query-c').title + ' (Run 1)',
    queryText: "My mom's birthday is 15 May 2026. Remember that and create reminders for two weeks before and on the day.",
    startedAt: '2026-05-01T10:00:04Z',
    finishedAt: '2026-05-01T10:00:38Z',
    status: 'completed',
    iters: 3,
    result: `Stored in memory: **Mom's birthday is 15 May 2026**.

Two reminders created and saved to \`sandbox/reminders.md\`:

- **🗓 1 May 2026** — "Two weeks to Mom's birthday! Start planning a gift."
- **🎂 15 May 2026** — "Today is Mom's birthday! Don't forget to call / celebrate."

You can retrieve this with: *"When is mom's birthday?"*`,
    events: [
      { iter: 1, component: 'memory.read',  status: null, message: '0 hits' },
      { iter: 1, component: 'perception',   status: '○',  message: "Remember mom's birthday is 15 May 2026" },
      { iter: 1, component: 'perception',   status: '○',  message: 'Create reminders for 1 May and 15 May 2026' },
      { iter: 1, component: 'decision',     status: null, message: "TOOL_CALL: remember({\"fact\": \"Mom's birthday is 15 May 2026\"})" },
      { iter: 1, component: 'action',       status: null, message: '→ mem:4f2e19a3 stored (kind=fact, embedding=768-dim)' },

      { iter: 2, component: 'memory.read',  status: null, message: '2 hits — birthday fact retrieved' },
      { iter: 2, component: 'perception',   status: '✓',  message: "Remember mom's birthday is 15 May 2026" },
      { iter: 2, component: 'perception',   status: '○',  message: 'Create reminders for 1 May and 15 May 2026' },
      { iter: 2, component: 'decision',     status: null, message: 'TOOL_CALL: create_file({"path": "reminders.md", "content": "..."})' },
      { iter: 2, component: 'action',       status: null, message: '→ File created: sandbox/reminders.md (312 bytes)' },

      { iter: 3, component: 'memory.read',  status: null, message: '3 hits' },
      { iter: 3, component: 'perception',   status: '✓',  message: 'Create reminders for 1 May and 15 May 2026' },
      { iter: 3, component: 'decision',     status: null, message: 'ANSWER' },
    ],
  },

  // ── Query C: Mom's birthday – Run 2 (cross-run recall) ──────────
  {
    runId: 'run-c-002',
    queryId: 'query-c',
    queryLabel: q('query-c').label,
    queryTitle: q('query-c').title + ' (Run 2)',
    queryText: "When is mom's birthday?",
    startedAt: '2026-05-10T08:00:07Z',
    finishedAt: '2026-05-10T08:00:18Z',
    status: 'completed',
    iters: 1,
    result: `**Mom's birthday is 15 May 2026.**

*(Retrieved from durable memory written in a previous run on 1 May 2026.)*`,
    events: [
      { iter: 1, component: 'memory.read',  status: null, message: "8 hits — top hit: \"Mom's birthday is 15 May 2026\" (score 0.94)" },
      { iter: 1, component: 'perception',   status: '○',  message: "Recall mom's birthday from memory" },
      { iter: 1, component: 'decision',     status: null, message: 'ANSWER  ← memory hit sufficient, no tool call needed' },
    ],
  },

  // ── Query D: Asyncio research ────────────────────────────────────
  {
    runId: 'run-d-001',
    queryId: 'query-d',
    queryLabel: q('query-d').label,
    queryTitle: q('query-d').title,
    queryText: q('query-d').text,
    startedAt: '2026-05-24T09:05:22Z',
    finishedAt: '2026-05-24T09:06:14Z',
    status: 'completed',
    iters: 5,
    result: `**Agreed best practices across top 3 sources:**

1. **Avoid blocking calls inside coroutines** — Never call \`time.sleep()\`, synchronous file I/O, or CPU-bound code directly inside \`async def\` functions. Use \`asyncio.sleep()\`, \`aiofiles\`, or \`loop.run_in_executor()\` instead.

2. **Use \`asyncio.gather()\` for concurrent tasks** — When multiple independent coroutines must run together, \`asyncio.gather(*coros)\` is more efficient and readable than manually managing tasks with \`asyncio.create_task()\`.

3. **Prefer \`async with\` and \`async for\`** — Use async context managers for resources (HTTP sessions, DB connections) and async iterators for streaming data. This ensures proper cleanup even on exceptions.

4. **Set timeouts explicitly** — Wrap long-running awaits with \`asyncio.wait_for(coro, timeout=N)\` to avoid silent hangs in production.

*(Sources: Real Python asyncio guide, Python docs official tutorial, FastAPI advanced async patterns)*`,
    events: [
      { iter: 1, component: 'memory.read',  status: null, message: '0 hits' },
      { iter: 1, component: 'perception',   status: '○',  message: 'Search for "Python asyncio best practices"' },
      { iter: 1, component: 'decision',     status: null, message: 'TOOL_CALL: web_search({"query": "Python asyncio best practices 2026"})' },
      { iter: 1, component: 'action',       status: null, message: '→ 5 results (Tavily)' },

      { iter: 2, component: 'memory.read',  status: null, message: '2 hits' },
      { iter: 2, component: 'perception',   status: '✓',  message: 'Search for "Python asyncio best practices"' },
      { iter: 2, component: 'perception',   status: '○',  message: 'Read result #1 (Real Python)' },
      { iter: 2, component: 'decision',     status: null, message: 'TOOL_CALL: fetch_url({"url": "https://realpython.com/async-io-python/"})' },
      { iter: 2, component: 'action',       status: null, message: '→ Status 200 · 38,140 bytes' },

      { iter: 3, component: 'memory.read',  status: null, message: '4 hits' },
      { iter: 3, component: 'perception',   status: '✓',  message: 'Read result #1' },
      { iter: 3, component: 'perception',   status: '○',  message: 'Read result #2 (Python docs)' },
      { iter: 3, component: 'decision',     status: null, message: 'TOOL_CALL: fetch_url({"url": "https://docs.python.org/3/library/asyncio-task.html"})' },
      { iter: 3, component: 'action',       status: null, message: '→ Status 200 · 29,845 bytes' },

      { iter: 4, component: 'memory.read',  status: null, message: '6 hits' },
      { iter: 4, component: 'perception',   status: '✓',  message: 'Read result #2' },
      { iter: 4, component: 'perception',   status: '○',  message: 'Read result #3 (FastAPI patterns)' },
      { iter: 4, component: 'decision',     status: null, message: 'TOOL_CALL: fetch_url({"url": "https://fastapi.tiangolo.com/async/"})' },
      { iter: 4, component: 'action',       status: null, message: '→ Status 200 · 14,212 bytes' },

      { iter: 5, component: 'memory.read',  status: null, message: '8 hits' },
      { iter: 5, component: 'perception',   status: '✓',  message: 'Read result #3' },
      { iter: 5, component: 'perception',   status: '○',  message: 'Synthesise agreed advice across all 3 sources' },
      { iter: 5, component: 'decision',     status: null, message: 'ANSWER' },
    ],
  },

  // ── Query E: Index + extract attention.md ────────────────────────
  {
    runId: 'run-e-001',
    queryId: 'query-e',
    queryLabel: q('query-e').label,
    queryTitle: q('query-e').title,
    queryText: q('query-e').text,
    startedAt: '2026-05-24T09:30:01Z',
    finishedAt: '2026-05-24T09:30:28Z',
    status: 'completed',
    iters: 3,
    result: `**Indexed:** \`sandbox/papers/attention.md\` → **42 chunks** (400 words / 80-word overlap).

**Three key contributions of the Transformer architecture** (from the paper):

1. **Multi-Head Self-Attention** — The model attends to all positions simultaneously with multiple independent attention heads, each learning different relational patterns. This replaces recurrence entirely, eliminating the sequential dependency that made RNNs slow to parallelise.

2. **Positional Encoding** — Since attention has no inherent sense of order, sinusoidal positional encodings inject sequence position information into the input embeddings, allowing the model to reason about token order without recurrence or convolution.

3. **Encoder-Decoder with Masked Attention** — The architecture pairs a fully-parallel encoder (bidirectional self-attention) with a decoder that uses *masked* self-attention to prevent positions from attending to future tokens during autoregressive generation, enabling efficient training with teacher forcing.`,
    events: [
      { iter: 1, component: 'memory.read',  status: null, message: '0 hits' },
      { iter: 1, component: 'perception',   status: '○',  message: 'Index papers/attention.md into memory' },
      { iter: 1, component: 'perception',   status: '○',  message: 'Extract 3 key Transformer contributions' },
      { iter: 1, component: 'decision',     status: null, message: 'TOOL_CALL: index_document({"path": "papers/attention.md"})' },
      { iter: 1, component: 'action',       status: null, message: '→ Indexed 42 chunks from sandbox:papers/attention.md' },

      { iter: 2, component: 'memory.read',  status: null, message: '8 hits — attention.md chunks retrieved' },
      { iter: 2, component: 'perception',   status: '✓',  message: 'Index papers/attention.md into memory' },
      { iter: 2, component: 'perception',   status: '○',  message: 'Extract 3 key Transformer contributions' },
      { iter: 2, component: 'decision',     status: null, message: 'TOOL_CALL: search_knowledge({"query": "key contributions Transformer architecture attention"})' },
      { iter: 2, component: 'action',       status: null, message: '→ 5 chunks returned (cosine similarity > 0.81)' },

      { iter: 3, component: 'memory.read',  status: null, message: '8 hits' },
      { iter: 3, component: 'perception',   status: '✓',  message: 'Extract 3 key Transformer contributions' },
      { iter: 3, component: 'decision',     status: null, message: 'ANSWER' },
    ],
  },

  // ── Query F: Cross-run document recall ───────────────────────────
  {
    runId: 'run-f-001',
    queryId: 'query-f',
    queryLabel: q('query-f').label,
    queryTitle: q('query-f').title + ' (Run 1 — index)',
    queryText: 'Index every .md file under papers/. Confirm how many chunks were indexed in total.',
    startedAt: '2026-05-24T10:00:05Z',
    finishedAt: '2026-05-24T10:01:58Z',
    status: 'completed',
    iters: 4,
    result: `**All .md files under \`sandbox/papers/\` indexed successfully.**

| File | Chunks |
|---|---|
| attention.md | 42 |
| react.md | 36 |
| chain-of-thought.md | 35 |
| self-consistency.md | 29 |
| rag.md | 40 |
| toolformer.md | 32 |
| reflexion.md | 34 |
| tree-of-thought.md | 33 |

**Total: 281 chunks** written to FAISS index (\`state/index.faiss\`). Chunks are now searchable via \`search_knowledge\`.`,
    events: [
      { iter: 1, component: 'memory.read',  status: null, message: '0 hits' },
      { iter: 1, component: 'perception',   status: '○',  message: 'List all .md files under papers/' },
      { iter: 1, component: 'decision',     status: null, message: 'TOOL_CALL: list_dir({"path": "papers"})' },
      { iter: 1, component: 'action',       status: null, message: '→ count=8, names=[attention.md, react.md, chain-of-thought.md, …]' },

      { iter: 2, component: 'memory.read',  status: null, message: '1 hit' },
      { iter: 2, component: 'perception',   status: '✓',  message: 'List all .md files under papers/' },
      { iter: 2, component: 'perception',   status: '○',  message: 'Index each .md file (8 files)' },
      { iter: 2, component: 'decision',     status: null, message: 'TOOL_CALL: index_document({"path": "papers/attention.md"})' },
      { iter: 2, component: 'action',       status: null, message: '→ 42 chunks indexed' },

      { iter: 3, component: 'memory.read',  status: null, message: '4 hits' },
      { iter: 3, component: 'perception',   status: '○',  message: 'Index each .md file (continuing…)' },
      { iter: 3, component: 'decision',     status: null, message: 'TOOL_CALL: index_document({"path": "papers/react.md"}) … [repeated for all 8 files]' },
      { iter: 3, component: 'action',       status: null, message: '→ 36 + 35 + 29 + 40 + 32 + 34 + 33 = 239 more chunks indexed' },

      { iter: 4, component: 'memory.read',  status: null, message: '8 hits' },
      { iter: 4, component: 'perception',   status: '✓',  message: 'Index each .md file (8 files)' },
      { iter: 4, component: 'perception',   status: '○',  message: 'Confirm total chunk count' },
      { iter: 4, component: 'decision',     status: null, message: 'ANSWER' },
    ],
  },

  // ── Query G: Synonym recall ──────────────────────────────────────
  {
    runId: 'run-g-001',
    queryId: 'query-g',
    queryLabel: q('query-g').label,
    queryTitle: q('query-g').title,
    queryText: q('query-g').text,
    startedAt: '2026-05-24T10:15:33Z',
    finishedAt: '2026-05-24T10:15:47Z',
    status: 'completed',
    iters: 2,
    result: `The *credit assignment problem* asks how to attribute a reward or error signal back through a sequence of decisions or model layers to determine which actions/weights deserve credit or blame.

**How each indexed paper addresses it:**

- **Attention Is All You Need** — Multi-head attention provides direct gradient paths from every output to every input token, sidestepping the vanishing-gradient credit assignment issue inherent in RNNs.
- **ReAct** — Interleaved reasoning traces make each reasoning step explicit and attributable, so failures can be traced back to a specific thought or action rather than a black-box sequence.
- **Reflexion** — Verbal self-critique creates an explicit feedback loop: the agent's own language describes *which past action* caused failure, solving credit assignment through self-articulated natural language.
- **Chain-of-Thought** — Intermediate reasoning steps serve as checkpoints; evaluation of where reasoning diverges from correct logic is the explicit credit assignment mechanism.

*(Note: none of the papers use the phrase "credit assignment" directly — retrieved by vector similarity over semantically equivalent concepts.)*`,
    events: [
      { iter: 1, component: 'memory.read',  status: null, message: '8 hits — semantic match on "credit assignment ≈ backpropagation / reward attribution"' },
      { iter: 1, component: 'perception',   status: '○',  message: 'Search indexed papers for credit assignment problem' },
      { iter: 1, component: 'decision',     status: null, message: 'TOOL_CALL: search_knowledge({"query": "credit assignment problem reward attribution backpropagation", "k": 8})' },
      { iter: 1, component: 'action',       status: null, message: '→ 8 chunks (attention, react, reflexion, chain-of-thought) — keyword "credit assignment" absent; vector path succeeded' },

      { iter: 2, component: 'memory.read',  status: null, message: '8 hits' },
      { iter: 2, component: 'perception',   status: '✓',  message: 'Search indexed papers for credit assignment problem' },
      { iter: 2, component: 'perception',   status: '○',  message: 'Synthesise how each paper addresses credit assignment' },
      { iter: 2, component: 'decision',     status: null, message: 'ANSWER' },
    ],
  },

  // ── Query H: Cross-document synthesis ───────────────────────────
  {
    runId: 'run-h-001',
    queryId: 'query-h',
    queryLabel: q('query-h').label,
    queryTitle: q('query-h').title,
    queryText: q('query-h').text,
    startedAt: '2026-05-24T10:28:09Z',
    finishedAt: '2026-05-24T10:28:31Z',
    status: 'completed',
    iters: 2,
    result: `**ReAct vs Chain-of-Thought: Treatment of Intermediate Reasoning**

| Dimension | Chain-of-Thought (Wei et al.) | ReAct (Yao et al.) |
|---|---|---|
| **Purpose of reasoning** | Arrive at a better final answer | Decide which action to take next |
| **Reasoning is…** | An internal scratchpad | Interleaved with external actions |
| **Grounding** | Self-contained; model's parametric knowledge only | Grounded in live tool outputs (search, APIs) |
| **Feedback loop** | None — one-shot reasoning chain | Tight loop: observe → reason → act → observe |
| **Failure mode** | Confident but hallucinated chains | Reasoning can diverge if tool returns unexpected data |
| **Best suited for** | Math, logic, closed-book QA | Open-ended tasks needing up-to-date information |

**Key difference:** CoT treats intermediate reasoning as a *monologue* that improves answer quality; ReAct treats it as a *dialogue* with the environment — each reasoning step decides an action, and each action's result shapes the next reasoning step.`,
    events: [
      { iter: 1, component: 'memory.read',  status: null, message: '8 hits — react.md and chain-of-thought.md chunks retrieved' },
      { iter: 1, component: 'perception',   status: '○',  message: 'Retrieve ReAct paper chunks on intermediate reasoning' },
      { iter: 1, component: 'perception',   status: '○',  message: 'Retrieve Chain-of-Thought chunks on intermediate reasoning' },
      { iter: 1, component: 'decision',     status: null, message: 'TOOL_CALL: search_knowledge({"query": "intermediate reasoning treatment chain of thought react", "k": 8})' },
      { iter: 1, component: 'action',       status: null, message: '→ 8 chunks: 4 from react.md, 4 from chain-of-thought.md' },

      { iter: 2, component: 'memory.read',  status: null, message: '8 hits' },
      { iter: 2, component: 'perception',   status: '✓',  message: 'Retrieve ReAct and CoT chunks' },
      { iter: 2, component: 'perception',   status: '○',  message: 'Compare treatment of intermediate reasoning between papers' },
      { iter: 2, component: 'decision',     status: null, message: 'ANSWER' },
    ],
  },
];
