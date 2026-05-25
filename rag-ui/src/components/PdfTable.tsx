import { useMemo, useState } from 'react';
import { PDFS } from '../data/pdfs';

const ALL_PDF_CATEGORIES = Array.from(new Set(PDFS.map((p) => p.category))).sort();

function IconBook() {
  return (
    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
      <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
    </svg>
  );
}

function IconSearch() {
  return (
    <svg className="search-box-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="11" cy="11" r="8" /><line x1="21" y1="21" x2="16.65" y2="16.65" />
    </svg>
  );
}

export default function PdfTable() {
  const [search, setSearch]           = useState('');
  const [categoryFilter, setCategory] = useState('');

  const filtered = useMemo(() => {
    const q = search.toLowerCase().trim();
    return PDFS.filter((p) => {
      const matchSearch =
        !q ||
        p.title.toLowerCase().includes(q) ||
        p.author.toLowerCase().includes(q) ||
        p.category.toLowerCase().includes(q);
      const matchCategory = !categoryFilter || p.category === categoryFilter;
      return matchSearch && matchCategory;
    });
  }, [search, categoryFilter]);

  return (
    <div style={{ marginTop: 24 }}>
      {/* Toolbar */}
      <div className="toolbar">
        <div className="search-box">
          <IconSearch />
          <input
            className="search-input"
            type="search"
            placeholder="Search by title or author…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            aria-label="Search PDF library"
          />
        </div>

        <select
          className="filter-select"
          value={categoryFilter}
          onChange={(e) => setCategory(e.target.value)}
          aria-label="Filter by category"
        >
          <option value="">All Categories</option>
          {ALL_PDF_CATEGORIES.map((c) => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>

        {(search || categoryFilter) && (
          <button className="btn btn-ghost btn-sm" onClick={() => { setSearch(''); setCategory(''); }}>
            Clear filters
          </button>
        )}

        <span className="result-count">{filtered.length} of {PDFS.length} books</span>
      </div>

      {/* Table */}
      <div className="doc-table-wrapper" style={{ marginTop: 12 }}>
        {filtered.length === 0 ? (
          <div className="empty-state">
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="11" cy="11" r="8" /><line x1="21" y1="21" x2="16.65" y2="16.65" />
            </svg>
            <p>No books match your filters.</p>
          </div>
        ) : (
          <table className="doc-table" aria-label="PDF reference library">
            <thead>
              <tr>
                <th style={{ width: 60 }}>#</th>
                <th>Title</th>
                <th>Author</th>
                <th style={{ width: 60 }}>Year</th>
                <th>Category</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((book, idx) => (
                <tr key={book.id}>
                  <td><span className="doc-id">{String(idx + 1).padStart(2, '0')}</span></td>
                  <td>
                    <span className="doc-filename">
                      <IconBook />
                      <span className="doc-title" title={book.title}>{book.title}</span>
                    </span>
                  </td>
                  <td><span className="doc-date">{book.author}</span></td>
                  <td><span className="doc-date">{book.year}</span></td>
                  <td><span className="doc-category">{book.category}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
