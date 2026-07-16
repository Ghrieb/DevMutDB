import { Link } from 'react-router-dom';
import Navbar from '../components/Navbar';
import CaseStudyCharts from '../components/CaseStudyCharts';

const dataSources = [
  ['Ensembl VEP', 'Consequence terms, transcript context, CADD PHRED', 'Variant severity'],
  ['ClinVar', 'Clinical significance assertion', 'ClinVar pathogenicity weight'],
  ['gnomAD', 'Population frequency and rsID context', 'Population evidence'],
  ['Expression Atlas (E-MTAB-6814)', 'Human developmental expression profile', 'E_peak and peak stage'],
  ['UniProt', 'Protein accession, domain and functional region', 'D_domain weight'],
];

const pipelineSteps = [
  { step: '1', title: 'Input', desc: 'Gene symbol, HGVS notation, optional protein position' },
  { step: '2', title: 'Retrieve Evidence', desc: 'Async calls to Ensembl, ClinVar, gnomAD, Expression Atlas (E-MTAB-6814), UniProt' },
  { step: '3', title: 'Map Components', desc: 'Normalize CADD, map ClinVar, identify peak TPM, assign stage and domain weights' },
  { step: '4', title: 'Calculate DevScore', desc: 'V x E_peak x C_stage x D_domain x 100' },
  { step: '5', title: 'Explain', desc: 'Interpretable result page with sources' },
];

const toolComparison = [
  { dimension: 'Method type',                        sift: 'Sequence conservation',             polyphen: 'Structure + conservation',       cadd: 'ML ensemble (C-score)',          devscore: 'Multiplicative formula' },
  { dimension: 'Input',                              sift: 'AA substitution',                    polyphen: 'AA substitution + 3D',           cadd: 'Any variant type',               devscore: 'Any variant + gene' },
  { dimension: 'Variant types',                      sift: 'Missense only',                     polyphen: 'Missense only',                  cadd: 'SNV, indel, splice',             devscore: 'SNV, indel, splice' },
  { dimension: 'Developmental context',              sift: 'No',                                polyphen: 'No',                              cadd: 'No',                             devscore: 'Yes — core axis' },
  { dimension: 'Expression timing',                  sift: 'No',                                polyphen: 'No',                              cadd: 'No',                             devscore: 'Yes — E_peak × C_stage' },
  { dimension: 'Stage criticality weight',            sift: 'No',                                polyphen: 'No',                              cadd: 'No',                             devscore: 'Yes — Waddington-derived' },
  { dimension: 'Domain essentiality',                sift: 'Partial',                           polyphen: 'Yes (HumDiv/HumVar)',             cadd: 'Partial (Regulatory features)',  devscore: 'Yes — UniProt domain class' },
  { dimension: 'Interpretability (XAI)',              sift: 'Yes — Score + tolerance',            polyphen: 'Yes — Score + category',          cadd: 'No',                             devscore: 'Yes — Full breakdown' },
  { dimension: 'Score range',                        sift: '0–1 (lower = damaging)',            polyphen: '0–1 (higher = damaging)',         cadd: '1–99 PHRED-scaled',              devscore: '0–100 (higher = more impact)' },
  { dimension: 'Free & open API',                    sift: 'Yes',                               polyphen: 'Yes',                             cadd: 'Yes (via VEP)',                  devscore: 'Yes — fully open' },
  { dimension: 'Suited for congenital disease',      sift: 'Partial',                           polyphen: 'Partial',                         cadd: 'Partial',                        devscore: 'Yes — primary use case' },
  { dimension: 'Training data bias',                 sift: 'Adult protein alignments',          polyphen: 'Adult protein structures',        cadd: 'Adult ENCODE features',          devscore: 'Developmental expression series' },
];

function ComparisonBadge({ value }) {
  if (!value) return null;
  if (value === 'No') return <span className="argument-badge no">No</span>;
  if (value.startsWith('Partial')) return <span className="argument-badge partial">{value}</span>;
  if (value.startsWith('Yes')) return <span className="argument-badge yes">{value}</span>;
  return <span>{value}</span>;
}

const highlightDims = ['Developmental context', 'Expression timing', 'Stage criticality weight'];

export default function GetStarted() {
  return (
    <>
      <Navbar />
      <main className="page-container page-wide release-page">
        <section className="release-hero">
          <div className="release-eyebrow">DevScore - research release v1.0</div>
          <h1>Variant pathogenicity in developmental context</h1>
          <p>
            DevMutDB introduces DevScore &mdash; the first tool that weights mutation severity by <strong>spatiotemporal gene expression</strong> across human developmental stages. This answers: when does this gene matter most?
          </p>
          <div className="hero-stats">
            <span className="hero-stat"><strong>AUC 0.931</strong> DevScore (n=110)</span>
            <span className="hero-stat-divider" aria-hidden="true">·</span>
            <span className="hero-stat"><strong>Cohen&rsquo;s d 1.65</strong> very large</span>
            <span className="hero-stat-divider" aria-hidden="true">·</span>
            <span className="hero-stat"><strong>p = 3.97 &times; 10<sup>&minus;15</sup></strong> Mann-Whitney</span>
            <span className="hero-stat-divider" aria-hidden="true">·</span>
            <span className="hero-stat"><strong>60</strong> developmental + <strong>50</strong> adult-onset genes</span>
          </div>
          <div className="release-actions">
            <Link to="/" className="btn btn-primary">Calculate DevScore</Link>
            <Link to="/results" className="btn btn-outline">See Example Result</Link>
            <Link to="/methodology" className="btn btn-outline">Understand the Science</Link>
          </div>
        </section>

        <div className="release-layout">
          <article className="release-article-content readable-release">
            <section className="release-section">
              <div className="section-kicker">Scientific premise</div>
              <h2>Why developmental context matters</h2>
              <p className="section-paragraph">
                Classical variant scores (CADD, SIFT, PolyPhen) estimate molecular damage. DevScore adds a critical dimension:
                <strong> when the gene is active during development determines phenotype impact</strong>. A severe variant in a gene active during gastrulation (C_stage=1.0) is more likely to cause congenital defects than the same variant in a gene active only in adults (C_stage=0.25).
              </p>
              <p className="section-secondary" style={{ marginTop: '12px' }}>
                Try <strong>SOX2 c.70C&gt;T</strong> to see this in action.
              </p>
            </section>

            <section className="release-section">
              <div className="section-kicker">How it works</div>
              <h2>Instant annotation pipeline</h2>
              <div className="release-pipeline">
                {pipelineSteps.map((step, idx) => (
                  <div key={step.title}>
                    <span className="pipeline-step-number">{idx + 1}</span>
                    <strong>{step.title}</strong>
                    <span className="pipeline-step-desc">{step.desc}</span>
                  </div>
                ))}
              </div>
              <p className="pipeline-description">
                Each query triggers parallel API calls to Ensembl VEP, ClinVar, gnomAD, Expression Atlas (E-MTAB-6814), and UniProt. For genes not yet profiled in the Expression Atlas experiment, class-aware estimated profiles are used. Results are cached for 24 hours.
              </p>
            </section>

            <section className="release-section argument-section">
              <div className="section-kicker">Advantage</div>
              <h2>Unlike standard tools, DevScore includes developmental timing</h2>
              <div className="table-wrap argument-table-wrap">
                <table className="argument-table">
                  <thead>
                    <tr>
                      <th>Dimension</th>
                      <th>SIFT</th>
                      <th>PolyPhen-2</th>
                      <th>CADD</th>
                      <th>DevScore <span className="devscore-badge">BEST</span></th>
                    </tr>
                  </thead>
                  <tbody>
                    {toolComparison.map((row) => (
                      <tr key={row.dimension} className={highlightDims.includes(row.dimension) ? 'highlight-row' : ''}>
                        <td>{row.dimension}</td>
                        <td><ComparisonBadge value={row.sift} /></td>
                        <td><ComparisonBadge value={row.polyphen} /></td>
                        <td><ComparisonBadge value={row.cadd} /></td>
                        <td className="devscore-col"><ComparisonBadge value={row.devscore} /></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>

            <section className="release-section">
              <div className="section-kicker">Evidence sources</div>
              <h2>Five public genomic resources integrated</h2>
              <div className="table-wrap">
                <table className="science-table">
                  <thead>
                    <tr>
                      <th>Source</th>
                      <th>Evidence retrieved</th>
                      <th>Used for</th>
                    </tr>
                  </thead>
                  <tbody>
                    {dataSources.map(([source, evidence, contribution]) => (
                      <tr key={source}>
                        <td>{source}</td>
                        <td>{evidence}</td>
                        <td>{contribution}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>

            <CaseStudyCharts />

            <section className="release-section">
              <div className="section-kicker">AI-powered interpretation</div>
              <h2>Every score explained in clinical context</h2>
              <p className="section-paragraph">
                Each DevScore result is accompanied by a natural-language interpretation generated by <strong>Gemini 2.5 Flash</strong>, providing clinical context for the developmental impact. The AI synthesises variant severity, expression timing, stage criticality, and domain essentiality into a coherent clinical snapshot.
              </p>
              <div style={{
                border: '1px solid #e5e7eb',
                borderRadius: '10px',
                padding: '18px 20px',
                backgroundColor: '#FCFBF8',
                borderLeft: '4px solid #6366f1',
                marginTop: '16px',
                fontSize: '0.95rem',
                lineHeight: '1.6'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '10px' }}>
                  <strong style={{ fontSize: '1rem' }}>Quick Insight</strong>
                  <span style={{
                    fontSize: '0.7rem',
                    fontWeight: 600,
                    color: '#6366f1',
                    backgroundColor: '#eef2ff',
                    padding: '1px 8px',
                    borderRadius: '10px',
                    letterSpacing: '0.3px'
                  }}>&#10022; AI</span>
                </div>
                <p style={{ margin: 0, color: '#333' }}>
                  SOX2 c.70C&gt;T presents with a DevScore of <strong>52.8/100</strong> — high developmental impact. Peak expression during <strong>gastrulation</strong> (criticality 1.0) means this loss-of-function SOX2 mutation occurs during the most vulnerable window of embryogenesis, explaining the severe ocular and neurological phenotypes associated with this variant.
                </p>
              </div>
            </section>

            <div className="release-section release-cta">
              <Link to="/" className="btn btn-primary btn-lg">Calculate DevScore &rarr;</Link>
            </div>
          </article>
        </div>
      </main>
    </>
  );
}
