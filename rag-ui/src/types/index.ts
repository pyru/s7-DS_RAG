export type QueryStatus = 'not_started' | 'running' | 'completed' | 'failed';

export type TraceComponent = 'memory.read' | 'perception' | 'decision' | 'action' | 'system';

export interface TraceEvent {
  iter: number;
  component: TraceComponent;
  status: string | null;
  message: string;
}

export interface TraceRun {
  runId: string;
  queryId: string;
  queryLabel: string;
  queryTitle: string;
  queryText: string;
  startedAt: string;
  finishedAt?: string;
  status: QueryStatus;
  iters: number;
  events: TraceEvent[];
  result?: string;
}

export interface Query {
  id: string;
  label: string;
  title: string;
  text: string;
  tags: string[];
  useCase: string;
  status: QueryStatus;
  samplePrompts?: string[];
  runs?: QueryRun[];
}

export interface QueryRun {
  runId: string;
  startedAt: string;
  finishedAt?: string;
  status: QueryStatus;
  result?: string;
}

export type IndexedStatus = 'indexed' | 'not_indexed' | 'stale';

export interface PdfBook {
  id: string;
  title: string;
  author: string;
  year: string;
  category: string;
}

export interface RagDocument {
  id: string;
  fileName: string;
  title: string;
  category: string;
  chunkCount: number;
  indexed: IndexedStatus;
  lastIndexed: string | null;
  fileSizeKb: number;
  description: string;
}
