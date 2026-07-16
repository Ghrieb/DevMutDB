const verdictForDevScore = (score) => {
  if (score >= 20) return { label: 'High dev. impact', tone: 'danger' };
  if (score >= 9) return { label: 'Moderate dev. impact', tone: 'warning' };
  return { label: 'Low dev. impact', tone: 'success' };
};

const variantLooksFrameshift = (variant, proteinChange) => (
  /dup|del|fs|frameshift/i.test(`${variant || ''} ${proteinChange || ''}`)
);

export default function ComparisonTable({ result }) {
  if (!result) return null;

  const score = result.score ?? 0;
  const cadd = result.component_explanation?.V_pathogenicity?.cadd_phred ?? 0;
  const sift = result.sift_score != null ? parseFloat(result.sift_score) : null;
  const polyphen = result.polyphen_score != null ? parseFloat(result.polyphen_score) : null;
  const hasSift = sift != null && !isNaN(sift);
  const hasPolyphen = polyphen != null && !isNaN(polyphen);
  const frameshift = variantLooksFrameshift(result.variant, result.protein_change);
  const devVerdict = verdictForDevScore(score);
 
  const rows = [
    {
      tool: 'DevScore',
      displayScore: `${Math.round(score)} / 100`,
      barWidth: score,
      barMax: 100,
      barColor: 'var(--color-primary)',
      devContext: 'Yes',
      verdict: devVerdict.label,
      verdictTone: devVerdict.tone,
      highlight: true,
    },
    {
      tool: 'CADD',
      displayScore: `${Math.round(cadd)} (raw)`,
      barWidth: Math.min(cadd, 50),
      barMax: 50,
      barColor: '#7B7B73',
      devContext: 'No',
      verdict: cadd >= 20 ? 'Deleterious' : 'Lower severity',
      verdictTone: cadd >= 20 ? 'warning' : 'neutral',
    },
    {
      tool: 'SIFT',
      displayScore: hasSift ? `${sift.toFixed(2)} (${sift < 0.05 ? 'damaging' : 'tolerated'})` : frameshift ? '- (frameshift)' : '-',
      devContext: 'No',
      verdict: !hasSift ? 'N/A' : sift < 0.05 ? 'Damaging' : 'Tolerated',
      verdictTone: !hasSift ? 'neutral' : sift < 0.05 ? 'warning' : 'success',
    },
    {
      tool: 'PolyPhen-2',
      displayScore: hasPolyphen
        ? `${polyphen.toFixed(3)} (${polyphen > 0.85 ? 'probably dam.' : polyphen > 0.15 ? 'possibly dam.' : 'benign'})`
        : frameshift ? '- (frameshift)' : '-',
      devContext: 'No',
      verdict: !hasPolyphen ? 'N/A' : polyphen > 0.85 ? 'Damaging' : polyphen > 0.15 ? 'Possible' : 'Benign',
      verdictTone: !hasPolyphen ? 'neutral' : polyphen > 0.85 ? 'warning' : 'success',
    },
  ];

  return (
    <div id="comparison-table">
      <table className="comparison-table">
        <thead>
          <tr>
            <th style={{ width: '150px' }}>Tool</th>
            <th>Score</th>
            <th style={{ width: '140px' }}>Dev. context?</th>
            <th style={{ width: '170px' }}>Verdict</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.tool} className={row.highlight ? 'highlight-row' : ''}>
              <td className={`tool-name${row.highlight ? ' highlight' : ''}`}>
                {row.tool}
              </td>
              <td>
                {row.barWidth != null ? (
                  <div className="score-bar-container">
                    <div className="score-bar-track">
                      <div
                        className="score-bar"
                        style={{
                          width: `${Math.min((row.barWidth / row.barMax) * 100, 100)}%`,
                          backgroundColor: row.barColor,
                        }}
                      />
                    </div>
                    <span className="score-text">{row.displayScore}</span>
                  </div>
                ) : (
                  <span className="score-text muted">{row.displayScore}</span>
                )}
              </td>
              <td>
                <span className={row.devContext === 'Yes' ? 'context-yes' : 'context-no'}>
                  {row.devContext}
                </span>
              </td>
              <td>
                <span className={`verdict-pill ${row.verdictTone}`}>
                  {row.verdict}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <p className="comparison-note">
        SIFT and PolyPhen-2 are designed for missense variants and cannot score frameshifts. CADD reports molecular deleteriousness without developmental timing; DevScore adds expression stage context.
      </p>
    </div>
  );
}
