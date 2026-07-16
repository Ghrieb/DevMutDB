import { useNavigate } from 'react-router-dom';
import { useState } from 'react';
import Navbar from '../components/Navbar';
import ScoreRing from '../components/ScoreRing';
import ExpressionHeatmap from '../components/ExpressionHeatmap';
import ComponentCards from '../components/ComponentCards';
import ComparisonTable from '../components/ComparisonTable';

const sourceLink = (kind, value, gene) => {
  if (!value && !gene) return null;
  const encoded = encodeURIComponent(value || gene);

  if (kind === 'clinvar') return `https://www.ncbi.nlm.nih.gov/clinvar/?term=${encoded}`;
  if (kind === 'gnomad') return `https://gnomad.broadinstitute.org/search?query=${encoded}`;
  if (kind === 'expression') return `https://www.ebi.ac.uk/gxa/search?geneQuery=${encoded}`;
  if (kind === 'uniprot') return `https://www.uniprot.org/uniprotkb/${encoded}/entry`;
  if (kind === 'ensembl') return `https://www.ensembl.org/Multi/Search/Results?q=${encoded}`;
  return null;
};

const sourceChips = (result) => {
  const geneInfo = result.gene_info || {};
  const clinvarId = result.source_accessions?.clinvar || null;
  const gnomadId = result.source_accessions?.gnomad || null;

  return [
    {
      label: clinvarId ? `ClinVar ${clinvarId}` : `ClinVar ${result.clinvar_classification || 'classification'}`,
      tone: 'purple',
      href: sourceLink('clinvar', clinvarId || `${result.gene} ${result.variant}`),
    },
    {
      label: gnomadId ? `gnomAD ${gnomadId}` : `gnomAD AF ${result.gnomad_af ?? 'n/a'}`,
      tone: 'teal',
      href: sourceLink('gnomad', gnomadId || `${result.gene} ${result.variant}`),
    },
    {
      label: `Expression Atlas ${geneInfo.ensembl_id || result.gene}`,
      tone: 'amber',
      href: sourceLink('expression', geneInfo.ensembl_id || result.gene),
    },
    {
      label: `UniProt ${geneInfo.uniprot_id || result.gene}`,
      tone: 'green',
      href: sourceLink('uniprot', geneInfo.uniprot_id || result.gene),
    },
    {
      label: 'Ensembl VEP',
      tone: 'gray',
      href: sourceLink('ensembl', `${result.gene} ${result.variant}`),
    },
  ];
};

const stageLabel = (stage) => (stage || 'unknown').replace(/_/g, ' ');

const timingExplanation = (result) => {
  const scoreType = result.score <= 9 ? 'low score' : result.score < 20 ? 'moderate score' : 'high score';
  const stage = stageLabel(result.peak_stage);
  const direction = result.C_stage < 0.5
    ? 'is the key driver of this low developmental score'
    : result.C_stage >= 0.95
      ? 'amplifies developmental impact because the peak falls in an early critical window'
      : 'moderates the final developmental impact';

  return `C_stage = ${result.C_stage?.toFixed(2) ?? '-'} (${stage}) ${direction}. Despite V=${result.V?.toFixed(2) ?? '-'} and E_peak=${result.E_peak?.toFixed(2) ?? '-'}, DevScore reports a ${scoreType} because expression timing changes the clinical interpretation.`;
};

export default function Results({ result }) {
  const navigate = useNavigate();

  if (!result) {
    return (
      <>
        <Navbar />
        <div className="page-container page-wide" style={{ paddingTop: '24px' }}>
          <div className="results-hero" style={{ marginBottom: '18px' }}>
            <div style={{ flex: 1 }}>
              <div className="skeleton skeleton-text" style={{ width: '35%', height: '16px', marginBottom: '12px' }} />
              <div className="skeleton skeleton-title" style={{ width: '50%', height: '32px', marginBottom: '12px' }} />
              <div className="skeleton-row">
                <span className="skeleton skeleton-badge" />
                <span className="skeleton skeleton-badge" style={{ width: '120px' }} />
                <span className="skeleton skeleton-badge" style={{ width: '90px' }} />
              </div>
            </div>
            <div className="skeleton" style={{ width: '112px', height: '112px', borderRadius: '50%', flexShrink: 0 }} />
          </div>
          <div className="skeleton skeleton-block" />
          <div className="skeleton skeleton-block" style={{ height: '180px' }} />
          <div className="skeleton skeleton-block" />
          <div style={{ textAlign: 'center', marginTop: '24px' }}>
            <p className="hero-subtitle" style={{ marginBottom: '16px' }}>Enter a gene and variant to see results.</p>
            <button onClick={() => navigate('/')} className="btn btn-primary">
              Back to Search
            </button>
          </div>
        </div>
      </>
    );
  }

  const chips = sourceChips(result);
  const score = Math.round(result.score);
  const riskLevel = score >= 20 ? 'critical' : score > 9 ? 'moderate' : 'low';
  const riskColors = {
    critical: { bg: '#E6E2FF', border: '#6B5CE7', text: '#6B5CE7' },
    moderate: { bg: '#FFFDE6', border: '#D97706', text: '#D97706' },
    low: { bg: '#ECFFEC', border: '#059669', text: '#059669' }
  };
  const colors = riskColors[riskLevel];

  const interpretation = result.interpretation || timingExplanation(result);

  return (
    <>
      <Navbar
        actions={
          <>
            <button className="btn btn-outline btn-sm">Share</button>
            <button className="btn btn-outline btn-sm" onClick={() => window.print()}>Export PDF</button>
          </>
        }
      />
      <div className="page-container page-wide animate-in results-page">
        <main className="results-hero">
          <div className="results-summary">
            <div className="results-gene-info">
              {result.gene} - chromosome {result.gene_info?.chromosome || 'unknown'} - {result.gene_info?.description || 'Gene description unavailable'}
            </div>
            <div className="results-variant-row">
              <h1 className="results-variant">{result.variant}</h1>
              <span className="results-protein-change">{result.protein_change || 'p.Unknown'}</span>
            </div>
            <div className="results-badges">
              <span className={result.clinvar_classification === 'Pathogenic' || result.clinvar_classification === 'Likely pathogenic' ? 'badge badge-danger' : 'badge badge-neutral'}>
                {result.clinvar_classification || 'Unknown significance'}
              </span>
              <span className={score <= 9 ? 'badge badge-success' : score < 20 ? 'badge badge-warning' : 'badge badge-danger'}><strong>DevScore {score}</strong> - {score <= 9 ? 'Low developmental impact' : score < 20 ? 'Moderate developmental impact' : 'High developmental impact'}</span>
              <span className="badge badge-neutral">{result.protein_change?.includes('fs') ? 'Frameshift' : 'Variant'}</span>
              <span className="badge badge-primary">5 public APIs integrated</span>
            </div>
          </div>

          <div className="score-block">
            <ScoreRing score={result.score} size={112} />
          </div>
        </main>

        {/* Quick Insight Panel */}
        <section className={`results-card ${riskLevel}`} style={{
          backgroundColor: colors.bg,
          borderLeft: `4px solid ${colors.border}`,
          padding: '20px',
          marginBottom: '24px'
        }}>
          <h2 style={{ color: colors.text, marginTop: '0', marginBottom: '12px' }}>
            Quick Insight
            {result.ai_interpretation && (
              <span style={{
                display: 'inline-block',
                fontSize: '0.7rem',
                fontWeight: 600,
                color: '#6366f1',
                backgroundColor: '#eef2ff',
                padding: '1px 8px',
                borderRadius: '10px',
                marginLeft: '10px',
                verticalAlign: 'middle',
                letterSpacing: '0.3px'
              }}>
                &#10022; AI
              </span>
            )}
          </h2>
          <p style={{ margin: '0 0 12px 0', lineHeight: '1.6' }}>
            <strong>Interpretation:</strong> {interpretation}
          </p>
          <p style={{ margin: '0', fontSize: '0.9rem', color: '#555' }}>
            <strong>Score breakdown:</strong> V={result.V?.toFixed(2)}, E_peak={result.E_peak?.toFixed(2)}, C_stage={result.C_stage?.toFixed(2)}, D_domain={result.D_domain?.toFixed(2)}
          </p>
        </section>

        {/* Component Breakdown */}
        <section className="results-card">
          <h2 className="results-section-title text-xl font-bold border-b border-gray-100 pb-2 mb-4">
            Component Breakdown
          </h2>
          <ComponentCards result={result} />
        </section>

        {/* Expression Heatmap */}
        <section className="results-card">
          <h2 className="results-section-title text-xl font-bold border-b border-gray-100 pb-2 mb-4">
            Expression Heatmap
          </h2>
          <ExpressionHeatmap
            expressionData={result.expression_profile}
            peakStage={result.peak_stage}
            cStage={result.C_stage}
          />
        </section>

        {/* Comparison with Standard Tools */}
        <section className="results-card">
          <h2 className="results-section-title text-xl font-bold border-b border-gray-100 pb-2 mb-4">
            Comparison with Standard Tools
          </h2>
          <ComparisonTable result={result} />
        </section>

        {/* Clinical Interpretation */}
        <section className="results-card clinical-card">
          <h2 className="results-section-title text-xl font-bold border-b border-gray-100 pb-2 mb-4">
            Clinical Interpretation
          </h2>
          <div className="interpretation-box" style={{
            borderLeft: `4px solid ${colors.border}`,
            paddingLeft: '12px',
            backgroundColor: '#FCFBF8',
            borderRadius: 'var(--radius-md)',
            marginBottom: '16px'
          }}>
            <p>
              <strong>{result.gene} {result.variant}</strong> presents with a <strong>DevScore of {score}/100</strong>. {interpretation}
            </p>
            <p>{timingExplanation(result)}</p>
          </div>
          <div className="source-row" style={{ marginTop: '12px', marginBottom: '16px' }}>
            <span className="font-semibold text-gray-700 mr-2">Sources:</span>
            {chips.map((chip) => (
              <a
                key={chip.label}
                href={chip.href}
                target="_blank"
                rel="noopener noreferrer"
                className={`source-chip ${chip.tone}`}
                style={{ marginRight: '8px', display: 'inline-flex', alignItems: 'center' }}
              >
                {chip.label}
              </a>
            ))}
          </div>
          <div className="results-actions" style={{ marginTop: '16px', display: 'flex', gap: '8px' }}>
            <button className="btn btn-outline" onClick={() => window.print()}>Export PDF report</button>
            <button className="btn" onClick={() => navigate('/')}>Run another variant</button>
          </div>
        </section>

        {/* Citation Block */}
        <section className="results-card citation-card" style={{ marginTop: '24px', backgroundColor: '#F8F9FA', border: '1px solid #E9ECEF', padding: '20px' }}>
          <h2 className="results-section-title text-xl font-bold border-b border-gray-200 pb-2 mb-4 flex items-center gap-2">
            Academic Citation
          </h2>
          <p className="text-sm text-gray-600 mb-4">
            If you use DevScore or the DevMutDB platform in your research, please cite our preprint:
          </p>
          <div className="bg-white p-4 rounded border border-gray-200 mb-4 font-mono text-sm text-gray-800 shadow-sm leading-relaxed select-all">
            <strong>Ghrieb, A. H.</strong> (2025). <em>DevScore: A Spatiotemporal Criticality Index for Improved Pathogenicity Prediction of Developmental Variants</em>. bioRxiv preprint. DOI: TBD
          </div>
          <details className="text-xs text-gray-500 cursor-pointer">
            <summary className="font-semibold text-purple-600 hover:text-purple-800 transition-colors mb-2">
              Show BibTeX citation
            </summary>
            <pre className="bg-gray-50 p-3 rounded border border-gray-200 font-mono overflow-x-auto text-[11px] leading-tight select-all">
{`@article{ghrieb2025devscore,
  title={DevScore: A Spatiotemporal Criticality Index for Improved Pathogenicity Prediction of Developmental Variants},
  author={Ghrieb, Abdelkarim Hani},
  journal={bioRxiv preprint},
  year={2025},
  doi={TBD}
}`}
            </pre>
          </details>
        </section>

        {result.data_warnings && result.data_warnings.length > 0 && (
          <div className="alert alert-warning" style={{ marginTop: '24px' }}>
            <strong>Data sources unavailable:</strong> {result.data_warnings.join(', ')}. Using fallback estimates where necessary.
          </div>
        )}
      </div>
    </>
  );
}