import { NavLink } from 'react-router-dom';

/**
 * Shared navigation bar matching the DevMutDB platform design.
 * Displays on every page. Accepts optional `actions` prop for
 * page-specific buttons (e.g., "Share" and "Export PDF" on results).
 */
export default function Navbar({ actions }) {
  const linkClass = ({ isActive }) =>
    `navbar-link${isActive ? ' active' : ''}`;

  return (
    <nav className="navbar" role="navigation" aria-label="Main navigation">
      <div className="navbar-inner">
        <div className="navbar-left">
          <NavLink to="/" className="navbar-brand" id="nav-brand" style={{ display: 'inline-flex', alignItems: 'center' }}>
            <span 
              className="brand-circle" 
              style={{ 
                display: 'inline-block', 
                width: '10px', 
                height: '10px', 
                borderRadius: '50%', 
                backgroundColor: '#5546c8', 
                marginRight: '8px' 
              }} 
            />
            DevMutDB
          </NavLink>
          <NavLink to="/" className={linkClass} end id="nav-search">
            Search
          </NavLink>
          <NavLink to="/get-started" className={linkClass} id="nav-get-started">
            Get Started
          </NavLink>
          <NavLink to="/methodology" className={linkClass} id="nav-methodology">
            Methodology
          </NavLink>
          <NavLink to="/api" className={linkClass} id="nav-api">
            API
          </NavLink>
          <a
            href="https://doi.org/10.1101/2025.xx.xx"
            className="navbar-link"
            target="_blank"
            rel="noopener noreferrer"
            id="nav-preprint"
          >
            Preprint
          </a>
        </div>
        <div className="navbar-right">
          {actions || (
            <a
              href="https://github.com/DevMutDB/DevMutDB"
              className="btn btn-outline btn-sm"
              target="_blank"
              rel="noopener noreferrer"
              id="nav-github"
              style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}
            >
              <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/>
              </svg>
              View on GitHub
            </a>
          )}
        </div>
      </div>
    </nav>
  );
}
