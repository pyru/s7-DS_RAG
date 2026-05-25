import { useState, useRef, useEffect } from 'react';
import type { Query, QueryStatus, TraceEvent } from '../types';
import { useRuns } from '../context/RunsContext';
import { MOCK_TRACES } from '../data/traces';

// ── Component colour map ──────────────────────────────────────────
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

// ── Icons ─────────────────────────────────────────────────────────
function IconPlay() {
  return (
    <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor">
      <polygon points="5 3 19 12 5 21 5 3" />
    </svg>
  );
}
function IconCopy() {
  return (
    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
      <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
    </svg>
  );
}
function IconCheck() {
  return (
    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="20 6 9 17 4 12" />
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

// ── Status badge ──────────────────────────────────────────────────
const STATUS_LABELS: Record<QueryStatus, string> = {
  not_started: 'Not Started',
  running: 'Running',
  completed: 'Completed',
  failed: 'Failed',
};

function StatusBadge({ status }: { status: QueryStatus }) {
  return <span className={`status-badge status-${status}`}>{STATUS_LABELS[status]}</span>;
}

// ── Single trace event line ───────────────────────────────────────
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

// ── Query card ────────────────────────────────────────────────────
export default function QueryCard({ query }: { query: Query }) {
  const { statusMap, updateQueryStatus, addRun, updateRun } = useRuns();
  const status = statusMap[query.id] ?? query.status;

  const [copied, setCopied]           = useState(false);
  const [showTrace, setShowTrace]     = useState(false);
  const [liveEvents, setLiveEvents]   = useState<TraceEvent[]>([]);
  const [liveResult, setLiveResult]   = useState<string | null>(null);

  const timersRef   = useRef<number[]>([]);
  const traceLogRef = useRef<HTMLDivElement>(null);

  // Auto-scroll trace log whenever new events arrive
  useEffect(() => {
    if (traceLogRef.current) {
      traceLogRef.current.scrollTop = traceLogRef.current.scrollHeight;
    }
  }, [liveEvents]);

  // Cancel timers on unmount
  useEffect(() => {
    return () => { timersRef.current.forEach(clearTimeout); };
  }, []);

  function handleCopy() {
    navigator.clipboard.writeText(query.text).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 1800);
    });
  }

  function handleRun() {
    if (status === 'running') return;

    const mockRun = MOCK_TRACES.find((t) => t.queryId === query.id);
    if (!mockRun) return;

    timersRef.current.forEach(clearTimeout);
    timersRef.current = [];

    const runId     = `run-${query.id}-${Date.now()}`;
    const startedAt = new Date().toISOString();

    setLiveEvents([]);
    setLiveResult(null);
    setShowTrace(true);
    updateQueryStatus(query.id, 'running');

    addRun({
      runId,
      queryId:    query.id,
      queryLabel: query.label,
      queryTitle: query.title,
      queryText:  query.text,
      startedAt,
      status:     'running',
      iters:      mockRun.iters,
      events:     [],
    });

    const DELAY = 380; // ms between events

    mockRun.events.forEach((event, i) => {
      const t = window.setTimeout(() => {
        setLiveEvents((prev) => [...prev, event]);
      }, (i + 1) * DELAY);
      timersRef.current.push(t);
    });

    const finishDelay = (mockRun.events.length + 2) * DELAY;
    const finishTimer = window.setTimeout(() => {
      const finishedAt = new Date().toISOString();
      setLiveResult(mockRun.result ?? null);
      updateQueryStatus(query.id, 'completed');
      updateRun(runId, {
        status:     'completed',
        finishedAt,
        events:     mockRun.events,
        result:     mockRun.result,
      });
    }, finishDelay);
    timersRef.current.push(finishTimer);
  }

  // Group live events by iter for display
  const iterGroups: Record<number, TraceEvent[]> = {};
  for (const e of liveEvents) {
    (iterGroups[e.iter] ??= []).push(e);
  }

  return (
    <article className="query-card">
      {/* ── Header ── */}
      <div className="query-card-header">
        <div className="query-label-group">
          <span className="query-label">{query.label}</span>
          <div>
            <div className="query-title">{query.title}</div>
            <div className="query-use-case">Use case: {query.useCase}</div>
          </div>
        </div>
        <StatusBadge status={status} />
      </div>

      {/* ── Query text ── */}
      <pre className="query-text">{query.text}</pre>

      {/* ── Sample prompts ── */}
      {query.samplePrompts && query.samplePrompts.length > 0 && (
        <div className="sample-prompts">
          <span className="sample-prompts-label">Sample prompts</span>
          <div className="sample-chips">
            {query.samplePrompts.map((p, i) => (
              <span key={i} className="sample-chip">{p}</span>
            ))}
          </div>
        </div>
      )}

      {/* ── Tags ── */}
      <div className="query-tags">
        {query.tags.map((tag) => (
          <span key={tag} className="tag">{tag}</span>
        ))}
      </div>

      {/* ── Footer actions ── */}
      <div className="query-footer">
        <div className="query-actions">
          <button
            className="btn btn-primary"
            onClick={handleRun}
            disabled={status === 'running'}
            aria-label={`Run ${query.label}`}
          >
            <IconPlay />
            {status === 'running' ? 'Running…' : 'Run Query'}
          </button>
          <button className="btn btn-ghost" onClick={handleCopy} aria-label="Copy query text">
            {copied ? <IconCheck /> : <IconCopy />}
            {copied ? 'Copied!' : 'Copy'}
          </button>
        </div>
        {query.runs && query.runs.length > 0 && (
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            {query.runs.length} previous run{query.runs.length !== 1 ? 's' : ''}
          </span>
        )}
      </div>

      {/* ── Inline real-time trace panel ── */}
      {showTrace && (
        <div className="inline-trace">
          {/* Trace header */}
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

          {/* Event log */}
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

          {/* Result */}
          {liveResult && (
            <div className="inline-trace-result">
              <div className="inline-trace-result-title">Result</div>
              <div className="inline-trace-result-body">{liveResult}</div>
            </div>
          )}
        </div>
      )}
    </article>
  );
}
