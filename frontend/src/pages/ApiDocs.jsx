import Navbar from '../components/Navbar';

export default function ApiDocs() {
  return (
    <>
      <Navbar />
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
            marginBottom: '24px'
          }}>
            We welcome <strong>technical and/or scientific contributions</strong> to this project.
            If you're interested in helping shape the API, contributing code, or providing feedback on
            what features would be most useful for your research, please reach out to us.
          </p>

          <a
            href="mailto:contact@devmutdb.org"
            style={{
              display: 'inline-block',
              background: 'var(--color-primary)',
              color: 'white',
              padding: '12px 24px',
              borderRadius: '8px',
              textDecoration: 'none',
              fontWeight: '500',
              fontSize: '1rem',
              transition: 'opacity 0.2s'
            }}
            onMouseOver={(e) => e.target.style.opacity = '0.9'}
            onMouseOut={(e) => e.target.style.opacity = '1'}
          >
            Contact Us
          </a>

          <p style={{
            color: 'var(--color-text-tertiary)',
            fontSize: '0.85rem',
            marginTop: '32px',
            fontFamily: 'var(--font-mono)'
          }}>
            In the meantime, you can use the web interface at <span style={{color: 'var(--color-text-secondary)'}}>DevMutDB </span>
            to calculate DevScores interactively.
          </p>
        </div>
      </div>
    </>
  );
}