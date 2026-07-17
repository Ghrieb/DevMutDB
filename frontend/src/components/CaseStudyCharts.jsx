import { useMemo } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  ScatterChart, Scatter, ZAxis, ReferenceLine, Cell
} from 'recharts';
import benchmarkData from '../data/benchmark_results.json';

const META = benchmarkData.meta;
const ALL_GENES = benchmarkData.genes.filter(g => g.devscore != null && g.cadd != null);

const COLORS = {
  devscore: '#6D62D9',
  cadd: '#888780',
  sift: '#D94040',
  polyphen: '#E8803A',
  developmental: '#6D62D9',
  adult: '#1D9E75',
  V: '#5546C8',
  E_peak: '#2563EB',
  C_stage: '#D97706',
  D_domain: '#059669',
};

const AXIS_STYLE = { fontFamily: "'Inter', sans-serif", fontSize: 12, fill: '#6B7280' };
const LEGEND_STYLE = { fontFamily: "'Inter', sans-serif", color: '#374151', fontSize: 12 };

const CASE_GENES = ['SOX2', 'MECP2', 'MYH7', 'TP53'];

const LABELS = {
  V: 'Variant severity',
  E_peak: 'Peak expression',
  C_stage: 'Stage criticality',
  D_domain: 'Domain weight',
};

const TOOL_ORDER = [
  { key: 'devscore', label: 'DevScore', color: COLORS.devscore },
  { key: 'cadd', label: 'CADD', color: COLORS.cadd },
  { key: 'sift', label: 'SIFT', color: COLORS.sift },
  { key: 'polyphen', label: 'PolyPhen-2', color: COLORS.polyphen },
];

const BINS = [0, 2, 4, 6, 8, 10, 15, 20, 30, 40, 60];

function AUCComparison() {
  const data = TOOL_ORDER.map(t => ({
    name: t.label,
    auc: META[`${t.key}_auc`] ?? (t.key === 'devscore' ? META.headline_auc : null),
    fill: t.color,
    isDevscore: t.key === 'devscore',
  }));

  return (
    <div className="cs-card cs-auc-card">
      <h3 className="cs-card-title">AUC Comparison</h3>
      <p className="cs-card-subtitle">DevScore vs standard tools</p>
      <ResponsiveContainer width="100%" height={140}>
        <BarChart data={data} layout="vertical" margin={{ left: 10, right: 50, top: 5, bottom: 5 }}>
          <CartesianGrid horizontal={false} stroke="#F0EFEA" />
          <XAxis type="number" domain={[0, 1]} tick={AXIS_STYLE} tickFormatter={v => v.toFixed(2)} />
          <YAxis type="category" dataKey="name" tick={AXIS_STYLE} width={85} />
          <Tooltip
            formatter={(value) => [value.toFixed(3), 'AUC']}
            contentStyle={{ fontFamily: "'Inter', sans-serif", fontSize: 13 }}
          />
          <Bar dataKey="auc" radius={[0, 4, 4, 0]} maxBarSize={22}>
            {data.map((entry, i) => (
              <Cell key={i} fill={entry.fill} fillOpacity={entry.isDevscore ? 1 : 0.55} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <div className="cs-auc-margins">
        {TOOL_ORDER.filter(t => t.key !== 'devscore').map(t => (
          <span key={t.key} className="cs-auc-margin">
            <span className="cs-margin-dot" style={{ background: t.color }} />
            vs {t.label}: <strong>+{META[`${t.key}_margin`]}</strong>
          </span>
        ))}
      </div>
    </div>
  );
}

function TopGenesChart() {
  const topGenes = useMemo(() =>
    ALL_GENES
      .filter(g => g.class === 'developmental')
      .sort((a, b) => b.devscore - a.devscore)
      .slice(0, 10)
      .map(g => ({ ...g, shortName: g.gene.length > 8 ? g.gene.slice(0, 7) + '…' : g.gene }))
  , []);

  return (
    <div className="cs-card">
      <h3 className="cs-card-title">Top 10 Developmental Genes</h3>
      <p className="cs-card-subtitle">Ranked by DevScore</p>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={topGenes} layout="vertical" margin={{ left: 5, right: 30, top: 5, bottom: 5 }}>
          <CartesianGrid horizontal={false} stroke="#F0EFEA" />
          <XAxis type="number" domain={[0, 60]} tick={AXIS_STYLE} />
          <YAxis type="category" dataKey="gene" tick={AXIS_STYLE} width={55} />
          <Tooltip
            formatter={(value, name) => [value.toFixed(1), name === 'devscore' ? 'DevScore' : name]}
            labelFormatter={(label) => {
              const g = topGenes.find(x => x.gene === label);
              return g ? `${g.gene} — ${g.disease}` : label;
            }}
            contentStyle={{ fontFamily: "'Inter', sans-serif", fontSize: 13 }}
          />
          <Bar dataKey="devscore" fill={COLORS.devscore} radius={[0, 4, 4, 0]} maxBarSize={18} name="DevScore" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

function ComponentBreakdownChart() {
  const caseData = useMemo(() =>
    CASE_GENES.map(geneName => {
      const gene = ALL_GENES.find(g => g.gene === geneName);
      if (!gene) return null;
      return {
        name: geneName,
        class: gene.class,
        V: gene.V,
        E_peak: gene.E_peak,
        C_stage: gene.C_stage,
        D_domain: gene.D_domain,
        devscore: gene.devscore,
      };
    }).filter(Boolean)
  , []);

  return (
    <div className="cs-card">
      <h3 className="cs-card-title">Component Breakdown</h3>
      <p className="cs-card-subtitle">How each gene builds its DevScore</p>
      <ResponsiveContainer width="100%" height={260}>
        <BarChart data={caseData} margin={{ left: 5, right: 20, top: 10, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#F0EFEA" />
          <XAxis dataKey="name" tick={AXIS_STYLE} />
          <YAxis domain={[0, 1]} tick={AXIS_STYLE} tickFormatter={v => v.toFixed(1)} />
          <Tooltip
            contentStyle={{ fontFamily: "'Inter', sans-serif", fontSize: 13 }}
          />
          <Legend
            formatter={(value) => <span style={LEGEND_STYLE}>{LABELS[value] || value}</span>}
          />
          <Bar dataKey="V" fill={COLORS.V} radius={[4, 4, 0, 0]} maxBarSize={18} />
          <Bar dataKey="E_peak" fill={COLORS.E_peak} radius={[4, 4, 0, 0]} maxBarSize={18} />
          <Bar dataKey="C_stage" fill={COLORS.C_stage} radius={[4, 4, 0, 0]} maxBarSize={18} />
          <Bar dataKey="D_domain" fill={COLORS.D_domain} radius={[4, 4, 0, 0]} maxBarSize={18} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

function ScoreDistributionChart() {
  const { devBins, adultBins } = useMemo(() => {
    const dev = ALL_GENES.filter(g => g.class === 'developmental');
    const adult = ALL_GENES.filter(g => g.class === 'adult');
    const binData = BINS.slice(0, -1).map((start, i) => {
      const end = BINS[i + 1];
      const label = end <= 10 ? `${start}–${end}` : end <= 30 ? `${start}–${end}` : `${start}+`;
      return {
        range: label,
        developmental: dev.filter(g => g.devscore >= start && g.devscore < end).length,
        adult: adult.filter(g => g.devscore >= start && g.devscore < end).length,
        devPct: dev.length,
        adultPct: adult.length,
      };
    });
    return {
      devBins: binData.map(b => ({ range: b.range, count: b.developmental, pct: dev.length > 0 ? b.developmental / dev.length * 100 : 0 })),
      adultBins: binData.map(b => ({ range: b.range, count: b.adult, pct: adult.length > 0 ? b.adult / adult.length * 100 : 0 })),
      combined: binData,
    };
  }, []);

  const combined = useMemo(() =>
    BINS.slice(0, -1).map((start, i) => {
      const end = BINS[i + 1];
      const dev = ALL_GENES.filter(g => g.class === 'developmental' && g.devscore >= start && g.devscore < end).length;
      const adult = ALL_GENES.filter(g => g.class === 'adult' && g.devscore >= start && g.devscore < end).length;
      return {
        range: end <= 10 ? `${start}–${end}` : `${start}+`,
        developmental: dev,
        adult: adult,
      };
    })
  , []);

  return (
    <div className="cs-card cs-distribution-card">
      <h3 className="cs-card-title">Score Distribution</h3>
      <p className="cs-card-subtitle">Developmental vs adult-onset genes</p>
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={combined} margin={{ left: 5, right: 20, top: 10, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#F0EFEA" />
          <XAxis dataKey="range" tick={AXIS_STYLE} />
          <YAxis tick={AXIS_STYLE} allowDecimals={false} />
          <Tooltip
            contentStyle={{ fontFamily: "'Inter', sans-serif", fontSize: 13 }}
          />
          <Legend
            formatter={(value) => <span style={LEGEND_STYLE}>{value === 'developmental' ? 'Developmental' : 'Adult-onset'}</span>}
          />
          <Bar dataKey="developmental" fill={COLORS.developmental} radius={[4, 4, 0, 0]} maxBarSize={22} name="developmental" />
          <Bar dataKey="adult" fill={COLORS.adult} radius={[4, 4, 0, 0]} maxBarSize={22} name="adult" />
        </BarChart>
      </ResponsiveContainer>
      <div className="cs-distribution-stats">
        <span>Median: Dev <strong>{META.dev_median}</strong> &middot; Adult <strong>{META.adult_median}</strong></span>
        <span>Cohen&rsquo;s d = <strong>{META.cohens_d}</strong></span>
        <span>p &lt; 10<sup>&minus;14</sup></span>
      </div>
    </div>
  );
}

function ScatterCard() {
  const devGenes = ALL_GENES.filter(g => g.class === 'developmental');
  const adultGenes = ALL_GENES.filter(g => g.class === 'adult');

  function CustomScatterDot(props) {
    const { cx, cy, fill } = props;
    return <circle cx={cx} cy={cy} r={5} fill={fill} fillOpacity={0.55} stroke="rgba(255,255,255,0.85)" strokeWidth={1} />;
  }

  function CustomTooltip({ active, payload }) {
    if (active && payload && payload.length) {
      const d = payload[0].payload;
      return (
        <div className="cs-tooltip">
          <strong>{d.gene}</strong>
          <span>DevScore: {d.devscore?.toFixed(1)}</span>
          <span>CADD: {d.cadd?.toFixed(1)}</span>
          <span>Class: {d.class}</span>
        </div>
      );
    }
    return null;
  }

  return (
    <div className="cs-card cs-scatter-card">
      <h3 className="cs-card-title">DevScore vs CADD</h3>
      <p className="cs-card-subtitle">110 genes &middot; hover for details</p>
      <ResponsiveContainer width="100%" height={340}>
        <ScatterChart margin={{ top: 15, right: 25, bottom: 30, left: 30 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#F0EFEA" />
          <XAxis
            type="number" dataKey="cadd" name="CADD" domain={[0, 50]}
            tick={AXIS_STYLE}
            label={{ value: 'CADD PHRED', position: 'bottom', offset: 15, style: { ...AXIS_STYLE, fontSize: 11 } }}
          />
          <YAxis
            type="number" dataKey="devscore" name="DevScore" domain={[0, 60]}
            tick={AXIS_STYLE}
            label={{ value: 'DevScore', angle: -90, position: 'insideLeft', offset: 0, style: { ...AXIS_STYLE, fontSize: 11 } }}
          />
          <ZAxis range={[36, 36]} />
          <Tooltip content={<CustomTooltip />} cursor={{ strokeDasharray: '3 3' }} />
          <Legend
            formatter={(value) => <span style={LEGEND_STYLE}>{value}</span>}
          />
          <ReferenceLine y={8.5} stroke="#D94040" strokeDasharray="5 5" label={{ value: 'Youden threshold', position: 'right', fill: '#D94040', fontSize: 10 }} />
          <Scatter name="Developmental" data={devGenes} fill={COLORS.developmental} shape={<CustomScatterDot />} />
          <Scatter name="Adult-onset" data={adultGenes} fill={COLORS.adult} shape={<CustomScatterDot />} />
        </ScatterChart>
      </ResponsiveContainer>
      <div className="cs-scatter-stats">
        <span>Spearman <em>&rho;</em> = {META.spearman_rho} (p = {META.spearman_p})</span>
        <span>Partial <em>&rho;</em> (adj.) = {META.partial_spearman_rho}</span>
      </div>
    </div>
  );
}

export default function CaseStudyCharts() {
  return (
    <section className="cs-section">
      <div className="section-kicker">Validation & Case Studies</div>
      <h2>See DevScore in action</h2>
      <p className="cs-intro">
        Interactive charts below show how DevScore separates developmental from adult-onset disease genes,
        how its components work together, and how it compares to standard tools.
      </p>

      <div className="cs-auc-row">
        <AUCComparison />
      </div>

      <div className="cs-grid-2">
        <TopGenesChart />
        <ComponentBreakdownChart />
      </div>

      <div className="cs-grid-2">
        <ScoreDistributionChart />
        <ScatterCard />
      </div>
    </section>
  );
}
