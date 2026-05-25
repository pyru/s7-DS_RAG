import { NavLink } from 'react-router-dom';
import { QUERIES } from '../data/queries';
import { DOCUMENTS } from '../data/documents';

// Icons as inline SVG to avoid extra dependencies
function IconBolt() {
  return (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
    </svg>
  );
}

function IconDatabase() {
  return (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <ellipse cx="12" cy="5" rx="9" ry="3" />
      <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3" />
      <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5" />
    </svg>
  );
}

export default function Navbar() {
  return (
    <nav className="navbar">
      <div className="navbar-inner">
        <div className="navbar-brand">
          <span className="navbar-brand-dot" />
          DS_RAG
        </div>

        <ul className="navbar-nav">
          <li>
            <NavLink
              to="/queries"
              className={({ isActive }) => (isActive ? 'active' : '')}
            >
              <IconBolt />
              Queries
              <span className="navbar-badge">{QUERIES.length}</span>
            </NavLink>
          </li>
          <li>
            <NavLink
              to="/documents"
              className={({ isActive }) => (isActive ? 'active' : '')}
            >
              <IconDatabase />
              RAG Documents
              <span className="navbar-badge">{DOCUMENTS.length}</span>
            </NavLink>
          </li>
        </ul>
      </div>
    </nav>
  );
}
