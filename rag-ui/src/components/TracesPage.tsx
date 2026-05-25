import { useRuns } from '../context/RunsContext';
import type { TraceRun, TraceComponent, QueryStatus } from '../types';

// ── Helpers ───────────────────────────────────────────────────────
function fmtTime(iso: string) {
  return new Date(iso).toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}
function fmtDate(iso: string) {
  return new Date(iso).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });
}
function elapsed(start: string, end: string | null) {
  if (!end) return '…';
  const ms = new Date(end).getTime() - new Date(start).getTime();
  return ms < 1000 ? `${ms}ms` : `${(ms / 1000).toFixed(1)}s`;
}

// ── Colour map for trace components ──────────────────────────────
const COMPONENT_COLOR: Record<TraceComponent, string> = {
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

// ── Run history sidebar item ──────────────────────────────────────
function RunItem({ run, active, onClick }: { run: TraceRun; active: boolean; onClick: () => void }) {
  const statusColor: Record<QueryStatus, string> = {
    completed:   'var(--green)',
    running:     'var(--blue)',
    failed:      'var(--red)',
    not_started: 'var(--text-muted)',
  };
  return (
    <button
      className={`trace-run-item ${active ? 'trace-run-item--active' : ''}`}
      onClick={onClick}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
        <span
          className="query-label"
          style={{ fontSize: '0.68rem', padding: '2px 7px' }}
        >
          {run.queryLabel}
        </span>
        <span style={{ fontSize: '0.7rem', color: statusColor[run.status], fontWeight: 600 }}>
          ● {run.status}
        </span>
      </div>
      <div style={{ fontSize: '0.82rem', color: 'var(--text-primary)', fontWeight: 500, lineHeight: 1.3 }}>
        {run.queryTitle}
      </div>
      <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: 4 }}>
        {fmtDate(run.startedAt)} · {fmtTime(run.startedAt)} · {elapsed(run.startedAt, run.finishedAt)}
      </div>
    </button>
  );
}

// ── Trace log line ────────────────────────────────────────────────
function TraceLine({ event }: { event: TraceRun['events'][number] }) {
  const color  = COMPONENT_COLOR[event.component];
  const sColor = event.status ? STATUS_COLOR[event.status] ?? 'inherit' : 'inherit';
  const isAction = event.component === 'action';

  return (
    <div className="trace-line">
      <span className="trace-component" style={{ color }}>
        [{event.component}]
      </span>
      {event.status && (
        <span style={{ color: sColor, marginRight: 4, fontSize: '0.9em' }}>
          {event.status}
        </span>
      )}
      <span
        className="trace-message"
        style={{ color: isAction ? 'var(--green)' : 'var(--text-secondary)' }}
      >
        {event.message}
      </span>
    </div>
  );
}

// ── Trace detail panel ────────────────────────────────────────────
function TraceDetail({ run }: { run: TraceRun }) {
  const iters = Array.from(new Set(run.events.map((e) => e.iter))).sort((a, b) => a - b);

  return (
    <div className="trace-detail">
      {/* Run header */}
      <div className="trace-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap' }}>
          <span className="query-label">{run.queryLabel}</span>
          <span style={{ fontFamily: 'var(--mono)', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            run {run.runId}
          </span>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            {fmtDate(run.startedAt)} at {fmtTime(run.startedAt)}
            {run.finishedAt && ` · ${elapsed(run.startedAt, run.finishedAt)}`}
          </span>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            · {run.iters} iter{run.iters !== 1 ? 's' : ''}
          </span>
        </div>
        <h2 style={{ fontSize: '1rem', fontWeight: 600, marginTop: 6 }}>{run.queryTitle}</h2>
        <pre className="query-text" style={{ marginTop: 8, fontSize: '0.78rem' }}>{run.queryText}</pre>
      </div>

      {/* Execution log */}
      <div className="trace-log">
        <div className="trace-log-title">Execution Trace</div>
        {iters.map((iter) => (
          <div key={iter} className="trace-iter-block">
            <div className="trace-iter-label">── iter {iter} {'─'.repeat(50)}</div>
            {run.events
              .filter((e) => e.iter === iter)
              .map((e, i) => (
                <TraceLine key={i} event={e} />
              ))}
          </div>
        ))}
        {run.status === 'running' && (
          <div className="trace-iter-block">
            <div className="trace-running-indicator">● running…</div>
          </div>
        )}
      </div>

      {/* Result */}
      {run.result && (
        <div className="trace-result">
          <div className="trace-result-title">Result</div>
          <div className="trace-result-body">{run.result}</div>
        </div>
      )}
    </div>
  );
}

// ── Page ──────────────────────────────────────────────────────────
export default function TracesPage() {
  const { runs, activeRunId, setActiveRunId } = useRuns();
  const activeRun = runs.find((r) => r.runId === activeRunId) ?? runs[0];

  if (runs.length === 0) {
    return (
      <main className="page-wrapper">
        <div className="page-header">
          <h1>Traces &amp; Results</h1>
          <p>No runs yet. Click "Run Query" on the Queries page to execute a query.</p>
        </div>
        <div className="empty-state">
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M9 17H7A5 5 0 0 1 7 7h2" /><path d="M15 7h2a5 5 0 0 1 0 10h-2" /><line x1="8" y1="12" x2="16" y2="12" /></svg>
          <p>Traces will appear here after running a query.</p>
        </div>
      </main>
    );
  }

  return (
    <main className="trace-page-layout">
      {/* Sidebar */}
      <aside className="trace-sidebar">
        <div className="trace-sidebar-header">
          <span style={{ fontWeight: 600, fontSize: '0.85rem' }}>Run History</span>
          <span className="navbar-badge">{runs.length}</span>
        </div>
        <div className="trace-sidebar-list">
          {runs.map((run) => (
            <RunItem
              key={run.runId}
              run={run}
              active={run.runId === activeRun?.runId}
              onClick={() => setActiveRunId(run.runId)}
            />
          ))}
        </div>
      </aside>

      {/* Detail panel */}
      <section className="trace-main">
        {activeRun ? (
          <TraceDetail run={activeRun} />
        ) : (
          <div className="empty-state" style={{ paddingTop: 80 }}>
            <p>Select a run from the sidebar.</p>
          </div>
        )}
      </section>
    </main>
  );
}
