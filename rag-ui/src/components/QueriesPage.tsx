import QueryCard from './QueryCard';
import { QUERIES } from '../data/queries';
import { useRuns } from '../context/RunsContext';
import type { QueryStatus } from '../types';

// ── Live stats wired to RunsContext ───────────────────────────────
function QueriesStats() {
  const { statusMap } = useRuns();

  const counts: Record<QueryStatus, number> = { not_started: 0, running: 0, completed: 0, failed: 0 };
  for (const q of QUERIES) {
    const s = statusMap[q.id] ?? 'not_started';
    counts[s]++;
  }

  return (
    <div className="stats-row">
      <div className="stat-card">
        <span className="stat-value">{QUERIES.length}</span>
        <span className="stat-label">Total Queries</span>
      </div>
      <div className="stat-card">
        <span className="stat-value" style={{ color: 'var(--text-muted)' }}>{counts.not_started}</span>
        <span className="stat-label">Not Started</span>
      </div>
      <div className="stat-card">
        <span className="stat-value" style={{ color: 'var(--blue)' }}>{counts.running}</span>
        <span className="stat-label">Running</span>
      </div>
      <div className="stat-card">
        <span className="stat-value" style={{ color: 'var(--green)' }}>{counts.completed}</span>
        <span className="stat-label">Completed</span>
      </div>
      <div className="stat-card">
        <span className="stat-value" style={{ color: 'var(--red)' }}>{counts.failed}</span>
        <span className="stat-label">Failed</span>
      </div>
    </div>
  );
}

// ── Page ──────────────────────────────────────────────────────────
export default function QueriesPage() {
  return (
    <main className="page-wrapper">
      <div className="page-header">
        <h1>Evaluation Queries</h1>
        <p>
          8 predefined queries covering artifact fetch, multi-goal reasoning,
          durable memory, RAG indexing, vector recall, and cross-document synthesis.
        </p>
      </div>

      <QueriesStats />

      <div className="queries-grid">
        {QUERIES.map((query) => (
          <QueryCard key={query.id} query={query} />
        ))}
      </div>
    </main>
  );
}
