import { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';

// ── API base URL (configurable via VITE_API_URL env var) ──────────────────────
const API_BASE = import.meta.env.VITE_API_URL || '/api';

// ── HGVS validation patterns (mirrors backend models.py) ──────────────────────
const HGVS_PATTERNS = [
  /^c\.\d+[ACGT]>[ACGT]$/,            // c.70C>T
  /^c\.\d+_\d+[ACGT]>[ACGT]$/,        // c.70_71CA>TG
  /^c\.\d+del$/,                      // c.112del
  /^c\.\d+_\d+del$/,                  // c.68_69del
  /^c\.\d+dup$/,                      // c.5266dup
  /^c\.\d+_\d+dup$/,                  // c.1274_1277dup
  /^c\.\d+del[ACGTacgt]+$/,           // c.35delG
  /^c\.\d+_\d+del[ACGTacgt]+$/,       // c.301_302delAG
  /^c\.\d+dup[ACGTacgt]+$/,           // c.5266dupC
  /^c\.\d+_\d+ins[ACGTacgt]+$/,       // c.123_124insAGC
  /^c\.\d+_\d+delins[ACGTacgt]+$/,    // c.123_125delinsAGC
  /^c\.\d+[-+]\d+[ACGT]>[ACGT]$/,     // c.1620+1G>A (splice)
  /^c\.\*\d+[ACGT]>[ACGT]$/,          // c.*123A>G (3'UTR)
  /^c\.-\d+[ACGT]>[ACGT]$/,           // c.-123A>G (5'UTR)
  /^p\.\w+\d+\w+$/,                   // p.Gly12Val
  /^p\.\w+\d+\*$/,                    // p.Gly12*
  /^p\.\w+\d+\w+fs\*?\d*$/,           // p.Gly12Valfs*5
  /^n\.\d+[ACGT]>[ACGT]$/,            // n.123A>G
  /^g\.\d+[ACGT]>[ACGT]$/,            // g.123456A>G
  /^g\.\d+_\d+del$/,                  // g.123456_123789del
];

/**
 * Validate a raw HGVS string.
 * Returns { valid: bool, error: string|null, hint: string|null }
 */
function validateHGVS(raw) {
  if (!raw || !raw.trim()) return { valid: false, error: null, hint: null };
  const v = raw.trim();

  // Detect common mistakes with specific guidance
  if (/^\d+[ACGT]>[ACGT]$/.test(v))
    return { valid: false, error: 'Missing "c." prefix', hint: `Did you mean: c.${v}?` };
  if (v.includes('/') && !v.includes('>'))
    return { valid: false, error: 'Use ">" not "/" for substitutions', hint: `e.g. c.70C>T` };
  if (/^[cngp]\.[a-z]/.test(v) && !/^[cngp]\.[A-Z0-9*\-_]/.test(v))
    return { valid: false, error: 'Position must follow "c." with a digit or uppercase letter', hint: `e.g. c.70C>T` };
  if (!/^[cngp]\./.test(v) && v.includes('.'))
    return { valid: false, error: 'Invalid HGVS prefix', hint: 'Use c., p., n., or g. prefix' };
  if (!/^[cngp]\./.test(v))
    return { valid: false, error: 'HGVS notation must start with c., p., n., or g.', hint: `e.g. c.70C>T or p.Gly12Val` };

  if (HGVS_PATTERNS.some(p => p.test(v))) return { valid: true, error: null, hint: null };

  // Suggest corrections for near-misses
  if (/^c\.\d+[ACGT][ACGT]$/.test(v))
    return { valid: false, error: 'Substitution needs ">" between ref and alt', hint: `e.g. ${v.slice(0, -1)}>${v.slice(-1)}` };
  if (/^c\.\d+del[A-Z]$/.test(v))
    return { valid: false, error: null, hint: null }; // let backend decide

  return { valid: false, error: 'Unrecognised HGVS format', hint: 'Expected: c.70C>T, c.112del, c.68_69del, c.5266dupC, p.Gly12Val' };
}

const QUICK_EXAMPLES = [
  { gene: 'SOX2', hgvs: 'c.70C>T' },
  { gene: 'PPARG', hgvs: 'p.Pro12Ala' },
  { gene: 'BRCA1', hgvs: 'c.5266dupC' },
];

export default function Search({ onScoreComplete }) {
  const [geneInput, setGeneInput]         = useState('');
  const [hgvsInput, setHgvsInput]         = useState('');
  const [selectedGene, setSelectedGene]   = useState(null); // confirmed valid gene
  const [geneSuggestions, setGeneSuggestions] = useState([]);
  const [hgvsValidation, setHgvsValidation] = useState({ valid: false, error: null, hint: null });
  const [showVariantModal, setShowVariantModal] = useState(false);
  const [variants, setVariants]           = useState([]);
  const [loadingVariants, setLoadingVariants] = useState(false);
  const [loading, setLoading]             = useState(false);
  const [error, setError]                 = useState('');
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [expressionSource, setExpressionSource] = useState(null);
  const suggestionsRef = useRef(null);
  const navigate = useNavigate();

  // ── Real-time gene autocomplete via backend ────────────────────────────────
  useEffect(() => {
    if (!geneInput.trim() || geneInput.length < 1) {
      setGeneSuggestions([]);
      setShowSuggestions(false);
      return;
    }
    const controller = new AbortController();
    const timer = setTimeout(async () => {
      try {
        const res = await fetch(
          `${API_BASE}/genes/autocomplete?q=${encodeURIComponent(geneInput.trim())}`,
          { signal: controller.signal }
        );
        if (res.ok) {
          const data = await res.json();
          const items = data.suggestions || [];
          setGeneSuggestions(items);
          setShowSuggestions(items.length > 0);
          // Clear expression source when suggestions refresh (gene is being re-typed)
          if (expressionSource) setExpressionSource(null);
        }
      } catch (_) { /* network error or aborted */ }
    }, 180);
    return () => { clearTimeout(timer); controller.abort(); };
  }, [geneInput]);

  // ── Close autocomplete on outside click ───────────────────────────────────
  useEffect(() => {
    const handler = (e) => {
      if (suggestionsRef.current && !suggestionsRef.current.contains(e.target))
        setShowSuggestions(false);
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  // ── Keyboard shortcuts ────────────────────────────────────────────────────
  useEffect(() => {
    const handler = (e) => {
      if (e.key === '/' && e.target.tagName !== 'INPUT' && e.target.tagName !== 'TEXTAREA') {
        e.preventDefault();
        document.getElementById('gene-input')?.focus();
      }
      if (e.key === 'Escape') {
        setShowVariantModal(false);
      }
    };
    document.addEventListener('keydown', handler);
    return () => document.removeEventListener('keydown', handler);
  }, []);

  // ── Real-time HGVS validation ──────────────────────────────────────────────
  useEffect(() => {
    setHgvsValidation(validateHGVS(hgvsInput));
  }, [hgvsInput]);

  // ── Confirm gene selection ────────────────────────────────────────────────
  const confirmGene = useCallback((gene, source) => {
    setGeneInput(gene);
    setSelectedGene(gene);
    setExpressionSource(source || null);
    setShowSuggestions(false);
    setHgvsInput('');  // clear previous variant
    setHgvsValidation({ valid: false, error: null, hint: null });
  }, []);

  const handleGeneChange = (e) => {
    const v = e.target.value;
    setGeneInput(v);
    // Deselect if user edits the gene field after confirming
    if (selectedGene && v.toUpperCase() !== selectedGene) setSelectedGene(null);
  };

  // ── Show variant picker for a confirmed gene ───────────────────────────────
  const openVariantModal = async () => {
    if (!selectedGene) return;
    setLoadingVariants(true);
    setShowVariantModal(true);

    // Fetch curated variants from backend
    try {
      const res = await fetch(`${API_BASE}/genes/${selectedGene}/variants?per_page=10`);
      if (res.ok) {
        const data = await res.json();
        setVariants(data.variants || []);
      } else {
        setVariants([]);
      }
    } catch {
      setVariants([]);
    } finally {
      setLoadingVariants(false);
    }
  };

  // ── Submit scoring ─────────────────────────────────────────────────────────
  const handleScore = async (gene, hgvs) => {
    setError('');
    setLoading(true);
    setShowVariantModal(false);

    try {
      const response = await fetch(`${API_BASE}/score`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ gene, hgvs, position: 0 }),
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        const detail = errData.detail;
        let msg = typeof detail === 'string'
          ? detail
          : (detail?.error || `Server error ${response.status}`);
        // Add a hint if the server sends suggestions
        if (detail?.suggestions?.length) msg += ` — ${detail.suggestions[0]}`;
        throw new Error(msg);
      }

      const result = await response.json();
      onScoreComplete(result);
      navigate('/results');
    } catch (err) {
      if (err.message?.includes('Failed to fetch')) {
        setError(`Cannot reach backend. Ensure the server is running at ${API_BASE}`);
      } else {
        setError(err.message || 'Failed to calculate DevScore.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleQuickScore = (gene, hgvs) => {
    setGeneInput(gene);
    setSelectedGene(gene);
    setHgvsInput(hgvs);
    setHgvsValidation({ valid: true, error: null, hint: null });
    handleScore(gene, hgvs);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!selectedGene) return;
    if (hgvsValidation.valid) {
      handleScore(selectedGene, hgvsInput.trim());
    } else {
      // No valid HGVS typed → open variant picker
      openVariantModal();
    }
  };

  // ── Derive button state ────────────────────────────────────────────────────
  // Score is always enabled once a gene is confirmed.
  // If HGVS is empty/invalid: button says "Pick variant →"
  // If HGVS is valid:         button says "Score ↗"
  const geneConfirmed = !!selectedGene;
  const readyToScore  = geneConfirmed && hgvsValidation.valid;
  const btnLabel      = loading ? null : readyToScore ? 'Score ↗' : 'Pick variant →';
  const btnDisabled   = loading || !geneConfirmed;

  return (
    <>
      <Navbar />
      <div className="page-container" style={{ position: 'relative' }}>

        {/* ── Variant picker modal ───────────────────────────────────────────── */}
          {showVariantModal && (
          <div className="modal-overlay" onMouseDown={e => { if (e.target === e.currentTarget) setShowVariantModal(false); }}>
            <div className="modal-box">
              <h2>Pre-loaded variants</h2>
              <p>
                A curated sample of ClinVar entries for{' '}
                <strong style={{ color: 'var(--color-primary)' }}>{selectedGene}</strong>.
                <br />
                <strong>Don't see yours?</strong> Close this and type any valid
                HGVS in the search field — <em>all existing variants are accepted</em>.
              </p>

              {loadingVariants ? (
                <div className="modal-loading">Loading variants…</div>
              ) : variants.length === 0 ? (
                <div className="modal-empty" style={{ padding: '24px 0', textAlign: 'center', color: '#888' }}>
                  No pre-loaded variants for this gene.
                  <br /><span style={{ fontSize: '0.85rem' }}>Type your own HGVS notation in the field above.</span>
                </div>
              ) : (
                <div className="modal-variant-list">
                  {variants.map(v => (
                    <button
                      key={v}
                      className="modal-variant-btn"
                      onClick={() => handleScore(selectedGene, v)}
                    >
                      {selectedGene} {v}
                    </button>
                  ))}
                </div>
              )}

              <div className="modal-info">
                <strong>All valid variants accepted.</strong>
                The pre-loaded list is just a convenience sample.
                You can type any HGVS notation (c.70C{'>'}T, c.5266dupC, p.Gly12Val, etc.)
                directly in the search field.
              </div>

              <button className="modal-cancel" onClick={() => setShowVariantModal(false)}>
                Cancel
              </button>
            </div>
          </div>
        )}

        <main className="hero-section animate-in" style={{
          paddingBottom: showSuggestions && geneSuggestions.length > 0
            ? `${Math.min(geneSuggestions.length * 38 + 10, 230)}px`
            : undefined,
          transition: 'padding-bottom 0.15s ease',
        }}>
          <span className="hero-badge">AUC 0.928 · 110 benchmark variants · 10 developmental stages</span>
          <h1 className="hero-title">
            Variant pathogenicity in developmental context
          </h1>
          <p className="hero-subtitle">
            The first variant impact metric that weights pathogenicity by spatiotemporal
            gene expression across human developmental stages.
          </p>

          <form onSubmit={handleSubmit} style={{ width: '100%', maxWidth: '640px', margin: '0 auto 12px' }}>
            {/* ── Two-field layout: Gene | HGVS | Button ───────────────── */}
            <div className="search-form-row">
              
              {/* Gene field with autocomplete */}
              <div className="search-gene-wrap" ref={suggestionsRef}>
                <input
                  type="text"
                  value={geneInput}
                  onChange={handleGeneChange}
                  onFocus={() => geneSuggestions.length > 0 && setShowSuggestions(true)}
                  onKeyDown={e => {
                    if (e.key === 'Enter' && geneInput.trim()) {
                      e.preventDefault();
                      const gene = geneInput.trim().toUpperCase();
                      confirmGene(gene);
                      fetch(`${API_BASE}/genes/${gene}/expression-source`)
                        .then(r => r.ok ? r.json() : null)
                        .then(d => d && setExpressionSource(d))
                        .catch(() => {});
                    }
                  }}
                  placeholder="Gene e.g. SOX2"
                  id="gene-input"
                  autoComplete="off"
                  className={`search-gene-input${selectedGene ? ' confirmed' : ''}`}
                />
                {/* Valid gene badge */}
                {selectedGene && (
                  <span className="search-gene-badge">✓</span>
                )}
                {/* Autocomplete dropdown */}
                {showSuggestions && geneSuggestions.length > 0 && (
                  <ul className="search-autocomplete">
                    {geneSuggestions.map(item => {
                      const geneName = typeof item === 'string' ? item : item.gene;
                      const src = typeof item === 'string' ? null : item;
                      return (
                        <li key={geneName}
                          className="search-suggestion"
                          onMouseDown={() => confirmGene(geneName, src)}
                        >
                          <span className="suggestion-gene">{geneName}</span>
                          {src && (
                            <span className={`suggestion-source ${src.source}`}>
                              {src.source === 'known' ? '✓' : '∼'} {src.label}
                            </span>
                          )}
                        </li>
                      );
                    })}
                  </ul>
                )}
              </div>

              {/* HGVS field */}
              <div className="search-hgvs-wrap">
                <input
                  type="text"
                  value={hgvsInput}
                  onChange={e => setHgvsInput(e.target.value)}
                  placeholder="HGVS e.g. c.70C>T (optional)"
                  id="hgvs-input"
                  disabled={!selectedGene}
                  className={`search-hgvs-input${
                    hgvsInput && !hgvsValidation.valid ? ' invalid'
                    : hgvsValidation.valid ? ' valid'
                    : ''
                  }`}
                />
                {/* Inline validation hint */}
                {selectedGene && hgvsInput && !hgvsValidation.valid && (
                  <div className="search-validation-hint">
                    {hgvsValidation.error && <span>⚠ {hgvsValidation.error}. </span>}
                    {hgvsValidation.hint && <span style={{ opacity: 0.85 }}>{hgvsValidation.hint}</span>}
                  </div>
                )}
              </div>

              {/* Submit button */}
              <button
                type="submit"
                disabled={btnDisabled}
                id="search-submit"
                className="search-submit"
              >
                {loading ? <span className="spinner" /> : btnLabel}
              </button>
            </div>

            <div className="search-helper">
              {!selectedGene && 'Type a gene symbol and press Enter, or select from autocomplete'}
              {selectedGene && !hgvsValidation.valid && 'Gene confirmed · type an HGVS variant or click "Pick variant →" to browse'}
              {selectedGene && hgvsValidation.valid && '✓ Ready — click Score to calculate DevScore'}
            </div>
          </form>

          {selectedGene && expressionSource && (
            <div className="expression-source-row">
              <span className={`expr-badge ${expressionSource.source}`}>
                {expressionSource.source === 'known' ? '✓' : '∼'} Expression:{' '}
                {expressionSource.label}
              </span>
            </div>
          )}

          {!selectedGene && (
            <div className="example-chips">
              <span className="example-chips-label">Try it now —</span>
              {QUICK_EXAMPLES.map(ex => (
                <button
                  key={`${ex.gene}-${ex.hgvs}`}
                  className="example-chip"
                  onClick={() => handleQuickScore(ex.gene, ex.hgvs)}
                >
                  {ex.gene} {ex.hgvs}
                </button>
              ))}
            </div>
          )}

          {error && (
            <div className="alert alert-error" style={{ maxWidth: '640px', margin: '12px auto 0' }}>
              {error}
            </div>
          )}
        </main>

        <div className="hero-stats animate-in animate-delay-1">
          <span className="hero-stat"><strong>120</strong> curated genes</span>
          <span className="hero-stat-divider">·</span>
          <span className="hero-stat"><strong>110</strong> benchmark variants</span>
          <span className="hero-stat-divider">·</span>
          <span className="hero-stat"><strong>AUC 0.928</strong> vs CADD +0.471</span>
          <span className="hero-stat-divider">·</span>
          <span className="hero-stat"><strong>10</strong> developmental stages</span>
        </div>

        <div className="metrics-divider animate-in animate-delay-2">
          <span className="metrics-divider-label">Platform capabilities</span>
        </div>
        <section className="metrics-grid animate-in animate-delay-1">
          <div className="metric-card">
            <div className="metric-icon" style={{background: 'var(--color-primary-bg)', color: 'var(--color-primary)'}}>
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
              </svg>
            </div>
            <div className="metric-content">
              <div className="metric-value">DevScore<span className="metric-range"> 0–100</span></div>
              <div className="metric-label">Novel developmental metric</div>
            </div>
          </div>
          <div className="metric-card">
            <div className="metric-icon" style={{background: '#E8F5F0', color: '#008B68'}}>
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
              </svg>
            </div>
            <div className="metric-content">
              <div className="metric-value">10 stages</div>
              <div className="metric-label">Embryo → adult timeline</div>
            </div>
          </div>
          <div className="metric-card">
            <div className="metric-icon" style={{background: '#FFF3E6', color: '#D06A18'}}>
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="9" y1="21" x2="9" y2="9"/>
              </svg>
            </div>
            <div className="metric-content">
              <div className="metric-value">5 tools</div>
              <div className="metric-label">CADD · SIFT · PolyPhen-2</div>
            </div>
          </div>
          <div className="metric-card">
            <div className="metric-icon" style={{background: '#F0EFFA', color: '#5E50C9'}}>
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>
              </svg>
            </div>
            <div className="metric-content">
              <div className="metric-value">PDF report</div>
              <div className="metric-label">Citable variant summary</div>
            </div>
          </div>
          <div className="metric-card">
            <div className="metric-icon" style={{background: '#FEF3E2', color: '#A85603'}}>
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/>
              </svg>
            </div>
            <div className="metric-content">
              <div className="metric-value">REST API</div>
              <div className="metric-label">Pipeline integration</div>
            </div>
          </div>
        </section>
      </div>
    </>
  );
}
