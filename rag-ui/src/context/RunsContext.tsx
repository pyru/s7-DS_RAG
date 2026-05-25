import { createContext, useContext, useState, type ReactNode } from 'react';
import type { TraceRun, QueryStatus } from '../types';
import { MOCK_TRACES } from '../data/traces';
import { QUERIES } from '../data/queries';

interface RunsCtx {
  runs: TraceRun[];
  activeRunId: string | null;
  setActiveRunId: (id: string | null) => void;
  addRun: (run: TraceRun) => void;
  updateRun: (runId: string, patch: Partial<TraceRun>) => void;
  statusMap: Record<string, QueryStatus>;
  updateQueryStatus: (id: string, status: QueryStatus) => void;
}

const Ctx = createContext<RunsCtx | null>(null);

// ── localStorage helpers ──────────────────────────────────────────
function lsGet<T>(key: string): T | null {
  try { const v = localStorage.getItem(key); return v ? (JSON.parse(v) as T) : null; } catch { return null; }
}
function lsSet(key: string, value: unknown) {
  try { localStorage.setItem(key, JSON.stringify(value)); } catch { /* quota exceeded — ignore */ }
}

// Heal stale 'running' runs left over from before updateRun existed.
// A run with a result → completed; without → failed.
function healRuns(runs: TraceRun[]): TraceRun[] {
  return runs.map((r) => {
    if (r.status !== 'running') return r;
    return {
      ...r,
      status: r.result ? 'completed' : 'failed',
      finishedAt: r.finishedAt ?? new Date().toISOString(),
    };
  });
}

export function RunsProvider({ children }: { children: ReactNode }) {
  // Runs — persisted so history survives browser refresh
  const [runs, setRuns] = useState<TraceRun[]>(() => {
    const loaded = lsGet<TraceRun[]>('dsrag:runs') ?? MOCK_TRACES;
    const healed = healRuns(loaded);
    // Write back only if something changed
    if (healed.some((r, i) => r !== loaded[i])) lsSet('dsrag:runs', healed);
    return healed;
  });

  // Active run selection — persisted
  const [activeRunId, setActiveRunIdState] = useState<string | null>(
    () => lsGet<string>('dsrag:activeRunId') ?? (MOCK_TRACES[0]?.runId ?? null)
  );

  // Query status map — persisted
  const [statusMap, setStatusMap] = useState<Record<string, QueryStatus>>(
    () => lsGet<Record<string, QueryStatus>>('dsrag:statusMap')
      ?? Object.fromEntries(QUERIES.map((q) => [q.id, q.status]))
  );

  function setActiveRunId(id: string | null) {
    setActiveRunIdState(id);
    lsSet('dsrag:activeRunId', id);
  }

  function addRun(run: TraceRun) {
    setRuns((prev) => {
      const next = [run, ...prev];
      lsSet('dsrag:runs', next);
      return next;
    });
    setActiveRunId(run.runId);
  }

  function updateRun(runId: string, patch: Partial<TraceRun>) {
    setRuns((prev) => {
      const next = prev.map((r) => r.runId === runId ? { ...r, ...patch } : r);
      lsSet('dsrag:runs', next);
      return next;
    });
  }

  function updateQueryStatus(id: string, status: QueryStatus) {
    setStatusMap((prev) => {
      const next = { ...prev, [id]: status };
      lsSet('dsrag:statusMap', next);
      return next;
    });
  }

  return (
    <Ctx.Provider value={{ runs, activeRunId, setActiveRunId, addRun, updateRun, statusMap, updateQueryStatus }}>
      {children}
    </Ctx.Provider>
  );
}

export function useRuns() {
  const ctx = useContext(Ctx);
  if (!ctx) throw new Error('useRuns must be used inside RunsProvider');
  return ctx;
}
