const STAGE_META = {
  zygote: { label: 'Zygote', criticality: 0.88, color: '#C43B3B' },
  blastocyst: { label: 'Blastocyst', criticality: 0.85, color: '#D94841' },
  gastrulation: { label: 'Gastrulation', criticality: 1, color: '#E23D3D' },
  neurulation: { label: 'Neurulation', criticality: 1, color: '#B91C1C' },
  organogenesis: { label: 'Organogenesis', criticality: 0.95, color: '#EF7D32' },
  fetal_early: { label: 'Fetal early', criticality: 0.65, color: '#E7B642' },
  fetal_late: { label: 'Fetal late', criticality: 0.5, color: '#D7C75C' },
  neonatal: { label: 'Neonatal', criticality: 0.30, color: '#8CC9A3' },
  childhood: { label: 'Childhood', criticality: 0.28, color: '#54B889' },
  adult: { label: 'Adult', criticality: 0.25, color: '#1FA37A' },
};

const ORDERED_STAGES = [
  'zygote',
  'blastocyst',
  'gastrulation',
  'neurulation',
  'organogenesis',
  'fetal_early',
  'fetal_late',
  'neonatal',
  'childhood',
  'adult',
];

const displayStage = (stage) => STAGE_META[stage]?.label || stage;

const criticalityText = (value) => {
  if (value >= 0.95) return 'high developmental criticality';
  if (value >= 0.5) return 'moderate developmental criticality';
  return 'low developmental criticality';
};

export default function ExpressionHeatmap({ expressionData, peakStage, cStage }) {
  if (!expressionData || Object.keys(expressionData).length === 0) {
    return (
      <div className="heatmap-container" id="expression-heatmap">
        <p style={{ color: 'var(--color-text-muted)', fontSize: '0.85rem' }}>
          Expression data unavailable
        </p>
      </div>
    );
  }

  const peakEntry = Object.entries(expressionData).reduce(
    (best, [stage, tpm]) => (tpm > best.tpm ? { stage, tpm } : best),
    { stage: '', tpm: 0 }
  );

  const activeStage = peakStage || peakEntry.stage;
  const activeCriticality = cStage ?? STAGE_META[activeStage]?.criticality ?? 0.25;

  return (
    <div className="heatmap-container" id="expression-heatmap">
      <div className="heatmap-title">
        Developmental expression timeline
        <span className="results-section-subtitle">EMBL-EBI Expression Atlas - Bgee</span>
      </div>

      <div className="heatmap-bar" role="img" aria-label="Developmental stage criticality timeline">
        {ORDERED_STAGES.map((stage) => {
          const meta = STAGE_META[stage];
          const tpm = expressionData[stage] || 0;
          const isPeak = stage === activeStage;

          return (
            <div
              key={stage}
              className={`heatmap-segment${isPeak ? ' peak' : ''}`}
              style={{
                backgroundColor: meta.color,
                flexGrow: Math.max(0.45, meta.criticality),
              }}
              title={`${meta.label}: ${tpm} TPM, C_stage=${meta.criticality.toFixed(2)}`}
            />
          );
        })}
      </div>

      <div className="heatmap-labels">
        <span>Zygote</span>
        <span>Gastrulation</span>
        <span>Organogenesis</span>
        <span>Fetal</span>
        <span>Adult</span>
      </div>

      {activeStage && (
        <div className="heatmap-callout">
          <span>Peak expression: {displayStage(activeStage)} ({peakEntry.tpm} TPM)</span>
          <span>C_stage = {activeCriticality.toFixed(2)} - {criticalityText(activeCriticality)}</span>
        </div>
      )}

      <div className="heatmap-legend">
        <span><i style={{ background: '#B91C1C' }} /> Gastrulation / neurulation (C=1.00)</span>
        <span><i style={{ background: '#EF7D32' }} /> Organogenesis (C=0.95)</span>
        <span><i style={{ background: '#E7B642' }} /> Fetal (C=0.50-0.65)</span>
        <span><i style={{ background: '#1FA37A' }} /> Adult (C=0.25)</span>
      </div>
    </div>
  );
}
