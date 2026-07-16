import Navbar from '../components/Navbar';
import ValidationExplorer from '../components/ValidationExplorer';

const components = [
  { symbol: 'V', label: 'Variant severity', evidence: 'CADD PHRED and ClinVar classification', question: 'Molecular and clinical evidence that the variant is damaging.' },
  { symbol: 'E_peak', label: 'Peak expression', evidence: 'Peak TPM normalized against 10,000 TPM ceiling (E-MTAB-6814, Cardoso-Moreira et al. 2019)', question: 'Whether the gene is strongly expressed during any developmental stage.' },
  { symbol: 'C_stage', label: 'Stage criticality', evidence: 'Developmental window of peak expression', question: 'Whether the peak falls in a highly canalized embryonic window.' },
  { symbol: 'D_domain', label: 'Domain weight', evidence: 'UniProt domain class', question: 'Whether the affected residue lies in a functionally essential region.' },
];

const stageWeights = [
  ['Zygote / cleavage', '0.88', 'Early totipotent and cleavage-stage sensitivity'],
  ['Blastocyst', '0.85', 'Pre-implantation and inner cell mass specification'],
  ['Gastrulation (wk 3)', '1.00', 'Axis formation and lineage specification'],
  ['Neurulation (wk 4)', '1.00', 'Neural tube closure and early CNS patterning'],
  ['Organogenesis (wk 5-8)', '0.95', 'Major tissue and organ patterning'],
  ['Fetal early (wk 9-16)', '0.65', 'Growth and early functional maturation'],
  ['Fetal late (wk 17-40)', '0.50', 'Late maturation with lower morphogenetic sensitivity'],
  ['Neonatal', '0.30', 'Postnatal growth and function'],
  ['Childhood', '0.28', 'Late postnatal development and refinement'],
  ['Adult', '0.25', 'Adult-onset relevance, low congenital-developmental weight'],
];

const domainWeights = [
  ['DNA-binding / transcription factor', '1.00', 'Direct disruption of transcriptional regulation'],
  ['Catalytic / enzyme active site', '1.00', 'Loss of enzymatic activity'],
  ['Structural / protein scaffold', '0.70', 'Folding perturbations sometimes tolerated'],
  ['Regulatory / signaling interface', '0.50', 'Context-dependent functional effect'],
  ['Disordered / inter-domain linker', '0.40', 'Relaxed sequence constraint'],
  ["3' UTR / mRNA regulatory", '0.20', 'Indirect impact on protein function'],
];

const caveats = [
  ['C_stage weight calibration', 'Stage weights are biologically motivated but not empirically trained. Recalibration with larger curated developmental cohorts is expected to improve accuracy.'],
  ['Benchmark scope', 'The 110-gene benchmark covers only coding variants. Non-coding, regulatory, and structural variant performance requires separate evaluation.'],
  ['Bulk tissue resolution', 'E-MTAB-6814 provides bulk tissue averages. Single-cell transcriptomics or tissue-specific embryonic profiles would improve stage-weight resolution.'],
  ['Independent replication', 'No independent replication cohort exists yet. The current benchmark compares developmental vs adult-onset disease genes, not affected vs unaffected individuals.'],
  ['Incomplete CADD/SIFT/PP2 coverage', 'CADD is unavailable for 0.9% of variants; SIFT and PolyPhen-2 are unavailable for 40.9% (non-missense classes). The paired subsets mitigate this, but broader coverage is desirable.'],
  ['External API dependency', 'The current implementation depends on public APIs (Ensembl VEP, Expression Atlas). A containerized offline deployment is under development for reproducibility and clinical deployment.'],
];

const stageBars = [
  ['Zygote / cleavage', 0.88, '#E84646'],
  ['Blastocyst', 0.85, '#D94841'],
  ['Gastrulation (wk 3)', 1.0, '#EF4444'],
  ['Neurulation (wk 4)', 1.0, '#D95A2A'],
  ['Organogenesis (wk 5-8)', 0.95, '#B97813'],
  ['Fetal early (wk 9-16)', 0.65, '#F59E1B'],
  ['Fetal late (wk 17-40)', 0.5, '#FBC66D'],
  ['Neonatal', 0.3, '#9BE0CB'],
  ['Childhood', 0.28, '#54B889'],
  ['Adult', 0.25, '#1FA37A'],
];

function StageCriticalitySvg() {
  return (
    <svg className="stage-criticality-svg" viewBox="0 0 940 360" role="img" aria-label="Stage criticality weights">
      {stageBars.map(([label, value, color], index) => {
        const y = 24 + index * 30;
        const width = value * 620;
        return (
          <g key={label}>
            <text x="0" y={y + 15} className="stage-svg-label">{label}</text>
            <rect x="300" y={y} width="640" height="18" rx="5" className="stage-svg-track" />
            <rect x="300" y={y} width={width} height="18" rx="5" fill={color} />
            <text x="928" y={y + 15} className="stage-svg-value">{value.toFixed(2)}</text>
          </g>
        );
      })}
    </svg>
  );
}

const symbolColors = {
  V: '#5546C8',
  E_peak: '#2563EB',
  C_stage: '#D97706',
  D_domain: '#059669',
};

export default function Methodology() {
  return (
    <>
      <Navbar />
      <main className="page-container methodology-readable">
        <header className="methodology-intro">
          <p className="methodology-kicker">Methods appendix</p>
          <h1>DevScore methodology</h1>
          <p>
            DevScore estimates whether a pathogenic variant is likely to affect early developmental processes. The score is intentionally transparent: every result is decomposed into variant severity, expression timing, developmental stage criticality, and protein-domain importance.
          </p>
        </header>

        <section className="method-section">
          <h2>1. Definition</h2>
          <p>
            DevScore combines molecular pathogenicity with developmental timing. A severe variant receives a high developmental score only when the affected gene is strongly expressed during a sensitive developmental window and the variant affects an important domain.
          </p>
          <div className="method-formula">DevScore = V x E_peak x C_stage x D_domain x 100</div>
        </section>

        <section className="method-section formula-section">
          <div className="section-kicker">DevScore formula</div>
          <h2>The DevScore Formula</h2>
          <p>Four dimensions combine for an interpretable score (0&ndash;100):</p>
          <div className="formula-display" style={{ marginTop: 0 }}>DevScore = V x E_peak x C_stage x D_domain x 100</div>
          <div className="release-component-grid methodology-component-grid">
            {components.map((comp) => (
              <div key={comp.symbol} className="component-dimension-card">
                <div className="card-accent" style={{ background: symbolColors[comp.symbol] }} />
                <strong className="component-dimension-symbol">{comp.symbol}</strong>
                <h3 style={{ margin: '6px 0 4px', fontSize: '0.95rem' }}>{comp.label}</h3>
                <span className="component-dimension-source">{comp.evidence}</span>
                <p className="component-dimension-question">{comp.question}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="method-section">
          <h2>2. Components</h2>
          <p>
            The four components are designed to answer separate biological questions. This prevents a high CADD or ClinVar signal from being interpreted as developmental by default.
          </p>
          <table className="method-table">
            <thead>
              <tr>
                <th>Component</th>
                <th>Meaning</th>
                <th>Evidence</th>
                <th>Question answered</th>
              </tr>
            </thead>
            <tbody>
              {components.map(({ symbol, label, evidence, question }) => (
                <tr key={symbol}>
                  <td>{symbol}</td>
                  <td>{label}</td>
                  <td>{evidence}</td>
                  <td>{question}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>

        <section className="method-section">
          <h2>3. Stage criticality</h2>
          <p>
            C_stage is the developmental timing term. Early embryonic stages are assigned higher weights because perturbations during canalized windows such as gastrulation, neurulation, and organogenesis are more likely to produce congenital phenotypes.
          </p>
          <figure className="method-figure inline">
            <StageCriticalitySvg />
            <figcaption>
              Stage weights used by C_stage. Red indicates high developmental sensitivity; green indicates lower adult-stage developmental relevance.
            </figcaption>
          </figure>
          <table className="method-table compact">
            <thead>
              <tr>
                <th>Stage</th>
                <th>Weight</th>
                <th>Rationale</th>
              </tr>
            </thead>
            <tbody>
              {stageWeights.map(([stage, weight, rationale]) => (
                <tr key={stage}>
                  <td>{stage}</td>
                  <td>{weight}</td>
                  <td>{rationale}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>

        <section className="method-section">
          <h2>4. Domain weighting</h2>
          <p>
            D_domain adjusts the score by protein context. Variants in DNA-binding, catalytic, or structurally essential regions are weighted more heavily than those in disordered or regulatory regions.
          </p>
          <table className="method-table compact">
            <thead>
              <tr>
                <th>Domain class</th>
                <th>Weight</th>
                <th>Rationale</th>
              </tr>
            </thead>
            <tbody>
              {domainWeights.map(([domain, weight, rationale]) => (
                <tr key={domain}>
                  <td>{domain}</td>
                  <td>{weight}</td>
                  <td>{rationale}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>

        <section className="method-section">
          <h2>5. Validation</h2>
          <p>
            The current benchmark contains 110 genes (60 developmental disease genes against 50 adult-onset disease genes) and compares DevScore against CADD, SIFT, and PolyPhen-2 across three decoupled pairwise subsets.
          </p>

          <h3>Headline performance</h3>
          <div className="validation-summary">
            <div className="validation-metric">
              <strong>0.927</strong>
              <span>DevScore AUC (n=110, all variant classes)</span>
            </div>
            <div className="validation-metric">
              <strong>0.930</strong>
              <span>DevScore AUC (missense-only, n=66)</span>
            </div>
          </div>

          <h3>Comparison with standard tools</h3>
          <div className="validation-metrics-grid">
            <div className="validation-compare">
              <span className="compare-tool">DevScore</span>
              <span className="compare-auc">0.927</span>
              <span className="compare-margin">&mdash;</span>
            </div>
            <div className="validation-compare">
              <span className="compare-tool">CADD</span>
              <span className="compare-auc">0.457</span>
              <span className="compare-margin positive">+0.470</span>
            </div>
            <div className="validation-compare">
              <span className="compare-tool">SIFT</span>
              <span className="compare-auc">0.397</span>
              <span className="compare-margin positive">+0.533</span>
            </div>
            <div className="validation-compare">
              <span className="compare-tool">PolyPhen-2</span>
              <span className="compare-auc">0.446</span>
              <span className="compare-margin positive">+0.484</span>
            </div>
          </div>

          <h3>Effect size</h3>
          <p>
            Median DevScore for developmental genes: <strong>12.3</strong> vs adult-onset: <strong>3.0</strong>.
            Cohen&rsquo;s <em>d</em> = <strong>1.65</strong> (very large), Mann-Whitney <em>p</em> = <strong>3.97 &times; 10<sup>&minus;15</sup></strong>.
          </p>

          <h3>Orthogonality to CADD</h3>
          <p>
            Spearman <em>&rho;</em>(DevScore, CADD) = <strong>0.154</strong> (p = 0.109).
            Partial Spearman (controlling for disease class): <em>&rho;</em> = <strong>0.316</strong> (p = 7.8 &times; 10<sup>&minus;4</sup>).
            The low correlation confirms that DevScore captures developmental timing information absent from CADD.
          </p>

          <h3>Interactive explorer</h3>
          <ValidationExplorer />
        </section>

        <section className="method-section">
          <h2>6. Weight sensitivity analysis</h2>
          <p>
            A hyperparameter sweep across seven CADD:ClinVar ratios (50:50 to 80:20) was performed to validate the 60:40 operational architecture.
          </p>
          <table className="method-table compact">
            <thead>
              <tr>
                <th>CADD:ClinVar</th>
                <th>AUC</th>
                <th>Cohen&rsquo;s d</th>
                <th>p-value</th>
                <th>Spearman &rho;</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>50:50</td><td>0.930</td><td>1.549</td><td>4.82e-15</td><td>1.000</td>
              </tr>
              <tr>
                <td>55:45</td><td>0.927</td><td>1.554</td><td>7.03e-15</td><td>1.000</td>
              </tr>
              <tr className="ws-optimal">
                <td><strong>60:40</strong></td><td><strong>0.926</strong></td><td><strong>1.559</strong></td><td><strong>8.09e-15</strong></td><td><strong>1.000</strong></td>
              </tr>
              <tr>
                <td>65:35</td><td>0.926</td><td>1.561</td><td>8.88e-15</td><td>1.000</td>
              </tr>
              <tr>
                <td>70:30</td><td>0.925</td><td>1.562</td><td>1.02e-14</td><td>1.000</td>
              </tr>
              <tr>
                <td>75:25</td><td>0.922</td><td>1.562</td><td>1.42e-14</td><td>1.000</td>
              </tr>
              <tr>
                <td>80:20</td><td>0.922</td><td>1.561</td><td>1.48e-14</td><td>1.000</td>
              </tr>
            </tbody>
          </table>
          <p>
            Spearman <em>&rho;</em> = <strong>1.000</strong> across all ratios confirms rank-order invariance. The 60:40 configuration (AUC = 0.926, Cohen&rsquo;s d = 1.559, p = 8.09 &times; 10<sup>&minus;15</sup>) was selected as the optimal operational architecture.
          </p>
        </section>

        <section className="method-section">
          <h2>7. Limitations</h2>
          <table className="method-table compact">
            <thead>
              <tr>
                <th>Point</th>
                <th>Interpretation</th>
              </tr>
            </thead>
            <tbody>
              {caveats.map(([point, interpretation]) => (
                <tr key={point}>
                  <td>{point}</td>
                  <td>{interpretation}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      </main>
    </>
  );
}
