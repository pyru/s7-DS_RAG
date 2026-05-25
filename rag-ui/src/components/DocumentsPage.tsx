import { useMemo, useState, useRef, useEffect } from 'react';
import DocumentTable from './DocumentTable';
import { DOCUMENTS } from '../data/documents';
import { MOCK_TRACES } from '../data/traces';
import type { IndexedStatus, RagDocument, TraceEvent } from '../types';

// ── Icons ─────────────────────────────────────────────────────────
function IconSearch() {
  return (
    <svg className="search-box-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="11" cy="11" r="8" /><line x1="21" y1="21" x2="16.65" y2="16.65" />
    </svg>
  );
}
function IconPlay() {
  return (
    <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor">
      <polygon points="5 3 19 12 5 21 5 3" />
    </svg>
  );
}
function IconX() {
  return (
    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
    </svg>
  );
}
function IconReset() {
  return (
    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="1 4 1 10 7 10" />
      <path d="M3.51 15a9 9 0 1 0 .49-3.47" />
    </svg>
  );
}

// ── Trace helpers (reused from QueryCard pattern) ─────────────────
const COMP_COLOR: Record<string, string> = {
  'memory.read': 'var(--blue)',
  'perception':  'var(--accent)',
  'decision':    'var(--yellow)',
  'action':      'var(--green)',
  'system':      'var(--text-muted)',
};
const STATUS_COLOR: Record<string, string> = {
  '○': 'var(--text-muted)',
  '✓': 'var(--green)',
  '✗': 'var(--red)',
};

function TraceLine({ event }: { event: TraceEvent }) {
  return (
    <div className="trace-line">
      <span className="trace-component" style={{ color: COMP_COLOR[event.component] ?? 'inherit' }}>
        [{event.component}]
      </span>
      {event.status && (
        <span style={{ color: STATUS_COLOR[event.status] ?? 'inherit', marginRight: 4, fontSize: '0.85em' }}>
          {event.status}
        </span>
      )}
      <span
        className="trace-message"
        style={{ color: event.component === 'action' ? 'var(--green)' : 'var(--text-secondary)' }}
      >
        {event.message}
      </span>
    </div>
  );
}

// ── Per-category sample prompts ───────────────────────────────────
const CATEGORY_PROMPTS: Record<string, string[]> = {
  '': [
    'What are the key contributions of the Transformer architecture?',
    'How does ReAct differ from chain-of-thought reasoning?',
    'How do indexed papers handle the credit assignment problem?',
    'What does the Reflexion paper say about self-improvement?',
  ],
  'Foundational Architecture': [
    'How does the Transformer handle positional information without recurrence?',
    'What are the differences between BERT and GPT-style models?',
    'How does ViT apply attention to image patches for classification?',
    'What safety evaluations were conducted for GPT-4?',
  ],
  'Prompting & Reasoning': [
    'How does chain-of-thought prompting improve multi-step reasoning?',
    'When should I use self-consistency over a single chain-of-thought?',
    'What is tree-of-thought and when does it outperform CoT?',
    'How do scratchpad prompts affect LLM arithmetic performance?',
  ],
  'Agent Frameworks': [
    'How does ReAct interleave reasoning traces with tool calls?',
    'What verbal reinforcement loop does Reflexion use?',
    'How does Toolformer decide when to invoke a tool mid-generation?',
    'Compare AutoGen vs CrewAI for multi-agent task orchestration',
  ],
  'RAG & Retrieval': [
    'What are the key components of a production RAG pipeline?',
    'How does FAISS enable sub-millisecond approximate nearest-neighbour search?',
    'What chunking strategies work best for long-document RAG indexing?',
    'How does hybrid search combine BM25 and dense vector retrieval?',
  ],
  'Models & Training': [
    'What techniques are used for instruction fine-tuning of LLMs?',
    'How does RLHF improve model alignment from human feedback?',
    'What are the trade-offs between full fine-tuning and LoRA?',
    'How does quantization affect LLM quality and inference speed?',
  ],
  'Infrastructure': [
    'How does vLLM achieve higher throughput than naive inference?',
    'What is tensor parallelism and when should it be used?',
    'How does KV cache work during autoregressive decoding?',
    'What are the trade-offs between continuous and dynamic batching?',
  ],
  'Evaluation & Benchmarks': [
    'What benchmarks best measure LLM multi-step reasoning ability?',
    'How is MMLU structured and what cognitive skills does it test?',
    'What are the limitations of current automated LLM evaluation?',
    'How do human preference evaluations compare to automated benchmarks?',
  ],
  'Multimodal': [
    'How do multimodal models align image and text representations?',
    'What is CLIP and how does contrastive learning work?',
    'How does GPT-4V process and reason about visual inputs?',
    'What are the key challenges in cross-modal grounding?',
  ],
};

// ── Pick a matching mock trace or build a generic one ─────────────
function resolvePlaygroundTrace(query: string): { events: TraceEvent[]; result: string } {
  const q = query.toLowerCase();

  const match = (keywords: string[]) => keywords.some((k) => q.includes(k));

  if (match(['shannon', 'information theory', 'entropy', 'channel capacity']))
    return { events: MOCK_TRACES[0].events, result: MOCK_TRACES[0].result! };

  if (match(['tokyo', 'weather', 'family', 'weekend activities']))
    return { events: MOCK_TRACES[1].events, result: MOCK_TRACES[1].result! };

  if (match(['birthday', 'mom', 'reminder', 'remember']))
    return { events: MOCK_TRACES[2].events, result: MOCK_TRACES[2].result! };

  if (match(['asyncio', 'async', 'python', 'event loop', 'coroutine']))
    return { events: MOCK_TRACES[3].events, result: MOCK_TRACES[3].result! };

  if (match(['transformer', 'attention', 'self-attention', 'positional encoding']))
    return { events: MOCK_TRACES[4].events, result: MOCK_TRACES[4].result! };

  if (match(['credit assignment', 'attribution', 'reward', 'backprop']))
    return { events: MOCK_TRACES[6].events, result: MOCK_TRACES[6].result! };

  if (match(['react', 'chain-of-thought', 'cot', 'reasoning', 'intermediate']))
    return { events: MOCK_TRACES[7].events, result: MOCK_TRACES[7].result! };

  // Generic RAG trace
  const snippet = query.length > 55 ? query.slice(0, 52) + '…' : query;
  return {
    events: [
      { iter: 1, component: 'memory.read', status: null,  message: '0 hits — cold start' },
      { iter: 1, component: 'perception',  status: '○',   message: `Parse query: "${snippet}"` },
      { iter: 1, component: 'decision',    status: null,  message: `TOOL_CALL: search_knowledge({"query": "${snippet}", "k": 8})` },
      { iter: 1, component: 'action',      status: null,  message: '-> 6 chunks retrieved from FAISS index (cosine > 0.72)' },

      { iter: 2, component: 'memory.read', status: null,  message: '6 hits — context loaded from indexed corpus' },
      { iter: 2, component: 'perception',  status: '✓',   message: `Parse query: "${snippet}"` },
      { iter: 2, component: 'perception',  status: '○',   message: 'Synthesise answer from top-k retrieved chunks' },
      { iter: 2, component: 'decision',    status: null,  message: 'ANSWER' },
    ],
    result: `**RAG Response** (simulated)\n\nYour query — *"${query}"* — was matched against the FAISS index of ${DOCUMENTS.filter(d => d.indexed !== 'not_indexed').length} indexed documents.\n\nThe top-6 retrieved chunks were synthesised to produce this answer. In a live deployment, the agent would call \`search_knowledge\` with your query, rank the results by cosine similarity, and feed the top chunks into the LLM context window before generating a grounded response.\n\n*(Connect the backend at \`/api/query\` to replace this mock with real RAG output.)*`,
  };
}

// ── Query Playground ──────────────────────────────────────────────
type PlayStatus = 'idle' | 'running' | 'completed';

function QueryPlayground({ category }: { category: string }) {
  const [prompt, setPrompt]         = useState('');
  const [status, setStatus]         = useState<PlayStatus>('idle');
  const [liveEvents, setLiveEvents] = useState<TraceEvent[]>([]);
  const [liveResult, setLiveResult] = useState<string | null>(null);
  const [showTrace, setShowTrace]   = useState(false);

  const timersRef   = useRef<number[]>([]);
  const traceLogRef = useRef<HTMLDivElement>(null);

  // Reset when category changes
  useEffect(() => {
    timersRef.current.forEach(clearTimeout);
    timersRef.current = [];
    setPrompt('');
    setStatus('idle');
    setLiveEvents([]);
    setLiveResult(null);
    setShowTrace(false);
  }, [category]);

  useEffect(() => {
    if (traceLogRef.current) {
      traceLogRef.current.scrollTop = traceLogRef.current.scrollHeight;
    }
  }, [liveEvents]);

  useEffect(() => () => { timersRef.current.forEach(clearTimeout); }, []);

  function handleRun() {
    if (!prompt.trim() || status === 'running') return;

    const { events, result } = resolvePlaygroundTrace(prompt);

    timersRef.current.forEach(clearTimeout);
    timersRef.current = [];

    setLiveEvents([]);
    setLiveResult(null);
    setShowTrace(true);
    setStatus('running');

    const DELAY = 380;
    events.forEach((event, i) => {
      const t = window.setTimeout(() => {
        setLiveEvents((prev) => [...prev, event]);
      }, (i + 1) * DELAY);
      timersRef.current.push(t);
    });

    const finishTimer = window.setTimeout(() => {
      setLiveResult(result);
      setStatus('completed');
    }, (events.length + 2) * DELAY);
    timersRef.current.push(finishTimer);
  }

  function handleReset() {
    timersRef.current.forEach(clearTimeout);
    timersRef.current = [];
    setPrompt('');
    setStatus('idle');
    setLiveEvents([]);
    setLiveResult(null);
    setShowTrace(false);
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') handleRun();
  }

  // Group events by iter
  const iterGroups: Record<number, TraceEvent[]> = {};
  for (const e of liveEvents) {
    (iterGroups[e.iter] ??= []).push(e);
  }

  return (
    <div className="playground-panel">
      <div className="playground-header">
        <div>
          <span className="playground-title">
            RAG Query Playground
            {category && (
              <span className="playground-category-badge">{category}</span>
            )}
          </span>
          <span className="playground-hint">
            {category
              ? `Showing prompts for "${category}" — select a different category above to switch`
              : 'Ask anything across the indexed corpus — Ctrl+Enter to run'}
          </span>
        </div>
        {(showTrace || prompt) && (
          <button className="btn btn-ghost btn-sm" onClick={handleReset}>
            <IconReset /> Reset
          </button>
        )}
      </div>

      {/* Prompt input row */}
      <div className="playground-input-row">
        <textarea
          className="playground-textarea"
          placeholder="e.g. How does the Transformer architecture handle positional information?"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          onKeyDown={handleKeyDown}
          rows={3}
          disabled={status === 'running'}
          aria-label="RAG query prompt"
        />
        <button
          className="btn btn-primary playground-run-btn"
          onClick={handleRun}
          disabled={!prompt.trim() || status === 'running'}
          aria-label="Run RAG query"
        >
          <IconPlay />
          {status === 'running' ? 'Running…' : 'Run Query'}
        </button>
      </div>

      {/* Sample prompts — driven by selected category */}
      <div className="playground-samples">
        {(CATEGORY_PROMPTS[category] ?? CATEGORY_PROMPTS['']).map((s) => (
          <button
            key={s}
            className="sample-chip"
            style={{ cursor: 'pointer' }}
            onClick={() => setPrompt(s)}
            disabled={status === 'running'}
          >
            {s}
          </button>
        ))}
      </div>

      {/* Trace panel */}
      {showTrace && (
        <div className="inline-trace" style={{ marginTop: 16 }}>
          <div className="inline-trace-header">
            <span className="inline-trace-title">Execution Trace</span>
            {status === 'running' && (
              <span className="trace-running-pill">
                <span className="trace-dot-pulse">●</span> running
              </span>
            )}
            {status === 'completed' && (
              <span className="trace-done-pill">✓ completed</span>
            )}
            <button
              className="btn-icon"
              style={{ marginLeft: 'auto' }}
              onClick={() => setShowTrace(false)}
              aria-label="Close trace"
            >
              <IconX />
            </button>
          </div>

          <div className="inline-trace-log" ref={traceLogRef}>
            {Object.entries(iterGroups).map(([iter, events]) => (
              <div key={iter} className="trace-iter-block">
                <div className="trace-iter-label">── iter {iter} {'─'.repeat(40)}</div>
                {events.map((e, i) => <TraceLine key={i} event={e} />)}
              </div>
            ))}
            {status === 'running' && liveEvents.length > 0 && (
              <div className="trace-running-indicator">
                <span className="trace-dot-pulse">●</span> processing next step…
              </div>
            )}
            {liveEvents.length === 0 && status === 'running' && (
              <div className="trace-running-indicator">
                <span className="trace-dot-pulse">●</span> initialising agent…
              </div>
            )}
          </div>

          {liveResult && (
            <div className="inline-trace-result">
              <div className="inline-trace-result-title">Result</div>
              <div className="inline-trace-result-body" style={{ whiteSpace: 'pre-wrap' }}>
                {liveResult}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ── Stats ─────────────────────────────────────────────────────────
function DocsStats() {
  const indexed     = DOCUMENTS.filter((d) => d.indexed === 'indexed').length;
  const stale       = DOCUMENTS.filter((d) => d.indexed === 'stale').length;
  const pending     = DOCUMENTS.filter((d) => d.indexed === 'not_indexed').length;
  const totalChunks = DOCUMENTS.reduce((s, d) => s + (d.indexed !== 'not_indexed' ? d.chunkCount : 0), 0);

  return (
    <div className="stats-row">
      <div className="stat-card">
        <span className="stat-value">{DOCUMENTS.length}</span>
        <span className="stat-label">Total Documents</span>
      </div>
      <div className="stat-card">
        <span className="stat-value" style={{ color: 'var(--green)' }}>{indexed}</span>
        <span className="stat-label">Indexed</span>
      </div>
      <div className="stat-card">
        <span className="stat-value" style={{ color: 'var(--yellow)' }}>{stale}</span>
        <span className="stat-label">Stale</span>
      </div>
      <div className="stat-card">
        <span className="stat-value" style={{ color: 'var(--text-muted)' }}>{pending}</span>
        <span className="stat-label">Not Indexed</span>
      </div>
      <div className="stat-card">
        <span className="stat-value">{totalChunks.toLocaleString()}</span>
        <span className="stat-label">Total Chunks</span>
      </div>
    </div>
  );
}

// ── Toast ─────────────────────────────────────────────────────────
function Toast({ message, visible }: { message: string; visible: boolean }) {
  if (!visible) return null;
  return <div className="toast">{message}</div>;
}

// ── Unique categories for filter ──────────────────────────────────
const ALL_CATEGORIES = Array.from(new Set(DOCUMENTS.map((d) => d.category))).sort();
const ALL_STATUSES: { value: '' | IndexedStatus; label: string }[] = [
  { value: '', label: 'All Statuses' },
  { value: 'indexed', label: 'Indexed' },
  { value: 'stale', label: 'Stale' },
  { value: 'not_indexed', label: 'Not Indexed' },
];

// ── Page ──────────────────────────────────────────────────────────
export default function DocumentsPage() {
  const [search, setSearch]               = useState('');
  const [statusFilter, setStatusFilter]   = useState<'' | IndexedStatus>('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [toast, setToast]                 = useState<string | null>(null);

  const filtered = useMemo(() => {
    const q = search.toLowerCase().trim();
    return DOCUMENTS.filter((doc) => {
      const matchSearch =
        !q ||
        doc.fileName.toLowerCase().includes(q) ||
        doc.title.toLowerCase().includes(q) ||
        doc.category.toLowerCase().includes(q) ||
        doc.description.toLowerCase().includes(q);
      const matchStatus   = !statusFilter   || doc.indexed === statusFilter;
      const matchCategory = !categoryFilter || doc.category === categoryFilter;
      return matchSearch && matchStatus && matchCategory;
    });
  }, [search, statusFilter, categoryFilter]);

  function handleView(doc: RagDocument) {
    setToast(`Viewing: ${doc.fileName}`);
    setTimeout(() => setToast(null), 2200);
  }

  function handleClearFilters() {
    setSearch('');
    setStatusFilter('');
    setCategoryFilter('');
  }

  const hasFilters = search || statusFilter || categoryFilter;

  return (
    <main className="page-wrapper">
      <div className="page-header">
        <h1>RAG Documents</h1>
        <p>
          Corpus of {DOCUMENTS.length} documents indexed into the FAISS vector store.
          Filter by name, category, or indexing status.
        </p>
      </div>

      <DocsStats />

      {/* ── Query Playground ── */}
      <QueryPlayground category={categoryFilter} />

      {/* ── Document table toolbar ── */}
      <div className="toolbar" style={{ marginTop: 28 }}>
        <div className="search-box">
          <IconSearch />
          <input
            className="search-input"
            type="search"
            placeholder="Search by file, title, or description…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            aria-label="Search documents"
          />
        </div>

        <select
          className="filter-select"
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value as '' | IndexedStatus)}
          aria-label="Filter by status"
        >
          {ALL_STATUSES.map((s) => (
            <option key={s.value} value={s.value}>{s.label}</option>
          ))}
        </select>

        <select
          className="filter-select"
          value={categoryFilter}
          onChange={(e) => setCategoryFilter(e.target.value)}
          aria-label="Filter by category"
        >
          <option value="">All Categories</option>
          {ALL_CATEGORIES.map((c) => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>

        {hasFilters && (
          <button className="btn btn-ghost btn-sm" onClick={handleClearFilters}>
            Clear filters
          </button>
        )}

        <span className="result-count">
          {filtered.length} of {DOCUMENTS.length} documents
        </span>
      </div>

      <DocumentTable documents={filtered} onView={handleView} />

      <Toast message={toast ?? ''} visible={toast !== null} />
    </main>
  );
}
