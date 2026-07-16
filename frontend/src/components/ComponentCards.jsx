const formatNumber = (value, digits = 2) => (
  Number.isFinite(value) ? value.toFixed(digits) : '-'
);

const stageLabel = (stage) => {
  if (!stage) return 'unknown stage';
  return stage.replace(/_/g, ' ');
};

export default function ComponentCards({ result }) {
  if (!result) return null;

  const explanation = result.component_explanation || {};
  const pathogenicity = explanation.V_pathogenicity || {};
  const expression = explanation.E_peak_expression || {};
  const domain = explanation.D_domain_weight || {};

  const components = [
    {
      key: 'V',
      label: 'V - variant severity',
      value: formatNumber(result.V),
      detail: `CADD ${pathogenicity.cadd_phred ?? '-'} - ${pathogenicity.clinvar_classification || 'ClinVar unknown'}`,
    },
    {
      key: 'E_peak',
      label: 'E_peak - expression',
      value: formatNumber(result.E_peak),
      detail: `${expression.peak_tpm ?? '-'} TPM at peak stage`,
    },
    {
      key: 'C_stage',
      label: 'C_stage - criticality',
      value: formatNumber(result.C_stage),
      detail: `Peak: ${stageLabel(result.peak_stage)}`,
      emphasized: result.C_stage < 0.5,
    },
    {
      key: 'D_domain',
      label: 'D_domain - domain',
      value: formatNumber(result.D_domain),
      detail: `${String(domain.domain_class || 'domain unknown').replace(/_/g, ' ')}`,
    },
    {
      key: 'DevScore',
      label: 'DevScore',
      value: formatNumber(result.score, 1),
      detail: result.score < 9 ? 'Low dev. impact' : result.score < 20 ? 'Moderate dev. impact' : 'High dev. impact',
      primary: true,
    },
  ];

  return (
    <div className="component-panel" id="component-cards">
      <div className="component-panel-title">
        <span>DevScore components</span>
        <span>V x E_peak x C_stage x D_domain x 100</span>
      </div>
      <div className="component-cards">
        {components.map((comp) => (
          <div className="component-card" key={comp.key}>
            <div className="component-card-label">{comp.label}</div>
            <div className={`component-card-value${comp.primary ? ' primary' : ''}${comp.emphasized ? ' emphasized' : ''}`}>
              {comp.value}
            </div>
            <div className="component-card-detail">{comp.detail}</div>
          </div>
        ))}
      </div>
      <div className="component-explanation">
        C_stage = {formatNumber(result.C_stage)} ({stageLabel(result.peak_stage)}) is the key timing signal. Despite V={formatNumber(result.V)} and E_peak={formatNumber(result.E_peak)}, DevScore follows the developmental window where the gene is most active.
      </div>
    </div>
  );
}
