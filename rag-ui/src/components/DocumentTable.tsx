import type { RagDocument, IndexedStatus } from '../types';

// ── Icon helpers ──────────────────────────────────────────────────
function IconFile() {
  return (
    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
      <polyline points="14 2 14 8 20 8" />
    </svg>
  );
}

function IconEye() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
      <circle cx="12" cy="12" r="3" />
    </svg>
  );
}

// ── Status badge ──────────────────────────────────────────────────
const STATUS_LABELS: Record<IndexedStatus, string> = {
  indexed: 'Indexed',
  not_indexed: 'Not Indexed',
  stale: 'Stale',
};

function IndexedBadge({ status }: { status: IndexedStatus }) {
  return (
    <span className={`status-badge status-${status}`}>
      {STATUS_LABELS[status]}
    </span>
  );
}

// ── Props ─────────────────────────────────────────────────────────
interface DocumentTableProps {
  documents: RagDocument[];
  // Backend integration point: replace with GET /api/documents/:id
  onView?: (doc: RagDocument) => void;
}

export default function DocumentTable({ documents, onView }: DocumentTableProps) {
  if (documents.length === 0) {
    return (
      <div className="doc-table-wrapper">
        <div className="empty-state">
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="11" cy="11" r="8" /><line x1="21" y1="21" x2="16.65" y2="16.65" />
          </svg>
          <p>No documents match your filters.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="doc-table-wrapper">
      <table className="doc-table" aria-label="RAG documents">
        <thead>
          <tr>
            <th>ID</th>
            <th>File</th>
            <th>Title</th>
            <th>Category</th>
            <th style={{ textAlign: 'right' }}>Chunks</th>
            <th>Status</th>
            <th>Last Indexed</th>
            <th style={{ textAlign: 'center' }}>Action</th>
          </tr>
        </thead>
        <tbody>
          {documents.map((doc) => (
            <tr key={doc.id}>
              <td><span className="doc-id">{doc.id}</span></td>

              <td>
                <span className="doc-filename">
                  <IconFile />
                  {doc.fileName}
                </span>
              </td>

              <td>
                <span className="doc-title" title={doc.title}>{doc.title}</span>
              </td>

              <td>
                <span className="doc-category">{doc.category}</span>
              </td>

              <td>
                <span className="doc-chunks">{doc.chunkCount}</span>
              </td>

              <td>
                <IndexedBadge status={doc.indexed} />
              </td>

              <td>
                <span className="doc-date">
                  {doc.lastIndexed ?? '—'}
                </span>
              </td>

              <td style={{ textAlign: 'center' }}>
                <button
                  className="btn-icon"
                  title={`View ${doc.fileName}`}
                  aria-label={`View ${doc.title}`}
                  onClick={() => onView?.(doc)}
                >
                  <IconEye />
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
