import Navbar from '../components/Navbar';

const contactCardStyle = {
  display: 'inline-flex',
  alignItems: 'center',
  gap: '8px',
  padding: '10px 18px',
  borderRadius: '8px',
  border: '1.5px solid var(--color-border)',
  background: 'var(--color-bg-card)',
  color: 'var(--color-text)',
  textDecoration: 'none',
  fontWeight: '600',
  fontSize: '0.9rem',
  transition: 'all 0.15s ease',
  cursor: 'pointer',
};

export default function ApiDocs() {
  return (
    <>
      <Navbar />
      <style>{`.contact-card:hover{background:var(--color-primary-bg)!important;border-color:var(--color-primary-light)!important;color:var(--color-primary)!important}`}</style>
      <div className="page-container" style={{ padding: '60px 24px', maxWidth: '800px', margin: '0 auto' }}>
        <div style={{
          background: 'var(--color-surface)',
          border: '1px solid var(--color-border)',
          borderRadius: '12px',
          padding: '48px',
          textAlign: 'center'
        }}>
          <h1 style={{
            fontSize: '2rem',
            fontWeight: '600',
            marginBottom: '16px',
            color: 'var(--color-text-primary)'
          }}>
            API Coming Soon
          </h1>

          <p style={{
            color: 'var(--color-text-secondary)',
            fontSize: '1.1rem',
            lineHeight: '1.7',
            marginBottom: '24px'
          }}>
            We currently do not have a public API available. We are actively working on improving the DevScore tool accessibility
            and plan to release a REST API soon.
          </p>

          <div style={{
            background: 'var(--color-background)',
            border: '1px solid var(--color-border)',
            borderRadius: '8px',
            padding: '24px',
            marginBottom: '24px',
            textAlign: 'left'
          }}>
            <h2 style={{
              fontSize: '1.1rem',
              fontWeight: '600',
              marginBottom: '12px',
              color: 'var(--color-text-primary)'
            }}>
              What we're working on:
            </h2>
            <ul style={{
              color: 'var(--color-text-secondary)',
              lineHeight: '1.8',
              paddingLeft: '20px'
            }}>
              <li>1. Designing a clean, developer-friendly REST API for DevScore</li>
              <li>2. Implementing authentication and rate limiting</li>
              <li>3. Adding comprehensive API documentation with examples</li>
              <li>4. Setting up a generous free tier for academic and research use</li>
            </ul>
          </div>

          <p style={{
            color: 'var(--color-text-secondary)',
            fontSize: '1rem',
            lineHeight: '1.7',
            marginBottom: '28px'
          }}>
            We welcome <strong>technical and/or scientific contributions</strong> to this project.
            If you're interested in helping shape the API, contributing code, or providing feedback on
            what features would be most useful for your research, please reach out.
          </p>

          <div style={{
            display: 'flex',
            gap: '12px',
            justifyContent: 'center',
            flexWrap: 'wrap',
            marginBottom: '28px'
          }}>
            <a href="https://www.linkedin.com/in/ghrieb-abdelkarim-hani/" target="_blank" rel="noopener noreferrer"
              className="contact-card" style={contactCardStyle}>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
              LinkedIn
            </a>
            <a href="https://github.com/Ghrieb" target="_blank" rel="noopener noreferrer"
              className="contact-card" style={contactCardStyle}>
              <svg width="18" height="18" viewBox="0 0 16 16" fill="currentColor"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/></svg>
              @Ghrieb
            </a>
            <a href="mailto:ghriebabdelkarimhani@gmail.com"
              className="contact-card" style={contactCardStyle}>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="M22 7l-10 7L2 7"/></svg>
              Email
            </a>
          </div>

          <p style={{
            color: 'var(--color-text-tertiary)',
            fontSize: '0.85rem',
            fontFamily: 'var(--font-mono)'
          }}>
            In the meantime, use the web interface at <span style={{color: 'var(--color-text-secondary)'}}>DevMutDB</span>
            {' '}to calculate DevScores interactively.
          </p>
        </div>
      </div>
    </>
  );
}