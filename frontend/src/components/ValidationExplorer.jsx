import { useState, useMemo } from 'react';
import {
  ScatterChart, Scatter, XAxis, YAxis, ZAxis, Tooltip, Legend,
  Line, ComposedChart, Area, ResponsiveContainer, ReferenceLine,
  CartesianGrid
} from 'recharts';
import benchmarkData from '../data/benchmark_results.json';

const META = benchmarkData.meta;
const ALL_GENES = benchmarkData.genes.filter(g => g.devscore != null && g.cadd != null);

const AXIS_STYLE = { fontFamily: "'Inter', sans-serif", fontSize: 12, fill: '#6B7280' };
const LABEL_STYLE = { fontFamily: "'Inter', sans-serif", fontSize: 13, fill: '#6B7280' };
const LEGEND_STYLE = { fontFamily: "'Inter', sans-serif", color: '#374151', fontSize: 13 };

function CustomScatterDot(props) {
  const { cx, cy, fill } = props;
  return <circle cx={cx} cy={cy} r={5} fill={fill} fillOpacity={0.6} stroke="rgba(255,255,255,0.85)" strokeWidth={1} />;
}

function CustomTooltip({ active, payload }) {
  if (active && payload && payload.length) {
    const d = payload[0].payload;
    return (
      <div className="scatter-tooltip">
        <strong>{d.gene}</strong>
        <span>DevScore: {d.devscore?.toFixed(1)}</span>
        <span>CADD: {d.cadd?.toFixed(1)}</span>
        <span>Class: {d.class}</span>
        <span>Peak: {d.peak_stage}</span>
      </div>
    );
  }
  return null;
}

function computeROC(genes, scoreKey, nPoints = 50) {
  const scored = genes.filter(g => g[scoreKey] != null && g.class != null);
  if (scored.length === 0) return [];
  const sorted = [...scored].sort((a, b) => b[scoreKey] - a[scoreKey]);
  const nPos = sorted.filter(g => g.class === 'developmental').length;
  const nNeg = sorted.length - nPos;
  const step = Math.max(1, Math.floor(sorted.length / nPoints));
  const points = [];
  for (let i = 0; i < sorted.length; i += step) {
    const threshold = sorted[i][scoreKey];
    let tp = 0, fp = 0;
    for (const g of sorted) {
      if (g[scoreKey] >= threshold) {
        if (g.class === 'developmental') tp++;
        else fp++;
      }
    }
    points.push({ fpr: nNeg > 0 ? fp / nNeg : 0, tpr: nPos > 0 ? tp / nPos : 0 });
  }
  points.sort((a, b) => a.fpr - b.fpr);
  if (points.length === 0 || points[0].fpr > 0 || points[0].tpr > 0) points.unshift({ fpr: 0, tpr: 0 });
  if (points[points.length - 1].fpr < 1 || points[points.length - 1].tpr < 1) points.push({ fpr: 1, tpr: 1 });
  return points;
}

export default function ValidationExplorer() {
  const [filter, setFilter] = useState('all');
  const [view, setView] = useState('scatter');

  const filteredGenes = ALL_GENES.filter(g => {
    if (filter === 'all') return true;
    return g.class === filter;
  });

  const scatterData = useMemo(() => filteredGenes.map(g => ({
    gene: g.gene,
    devscore: g.devscore,
    cadd: g.cadd,
    class: g.class,
    peak_stage: g.peak_stage,
  })), [filteredGenes]);

  const devGenes = useMemo(() => scatterData.filter(d => d.class === 'developmental'), [scatterData]);
  const adultGenes = useMemo(() => scatterData.filter(d => d.class === 'adult'), [scatterData]);

  const devROC = useMemo(() => computeROC(ALL_GENES, 'devscore'), []);
  const caddROC = useMemo(() => computeROC(ALL_GENES, 'cadd'), []);
  const siftROC = useMemo(() => computeROC(ALL_GENES, 'sift'), []);
  const pp2ROC = useMemo(() => computeROC(ALL_GENES, 'polyphen'), []);

  const chanceLine = [
    { fpr: 0, tpr: 0 },
    { fpr: 1, tpr: 1 },
  ];

  return (
    <div className="validation-explorer">
      <div className="validation-explorer-header">
        <div className="validation-tabs">
          <button
            className={`validation-tab ${view === 'scatter' ? 'active' : ''}`}
            onClick={() => setView('scatter')}
          >
            DevScore vs CADD
          </button>
          <button
            className={`validation-tab ${view === 'roc' ? 'active' : ''}`}
            onClick={() => setView('roc')}
          >
            ROC Curves
          </button>
        </div>
        {view === 'scatter' && (
          <div className="filter-toggles">
            {['all', 'developmental', 'adult'].map(f => (
              <button
                key={f}
                className={`filter-toggle ${filter === f ? 'active' : ''}`}
                onClick={() => setFilter(f)}
              >
                {f === 'all' ? 'All Genes' : f === 'developmental' ? 'Developmental' : 'Adult-onset'}
              </button>
            ))}
          </div>
        )}
      </div>

      {view === 'scatter' ? (
        <div className="explorer-chart-container">
          <ResponsiveContainer width="100%" height={420}>
            <ScatterChart margin={{ top: 20, right: 30, bottom: 40, left: 40 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#F0EFEA" />
              <XAxis
                type="number"
                dataKey="cadd"
                name="CADD"
                domain={[0, 50]}
                tick={AXIS_STYLE}
                label={{ value: 'CADD PHRED score', position: 'bottom', offset: 20, style: LABEL_STYLE }}
              />
              <YAxis
                type="number"
                dataKey="devscore"
                name="DevScore"
                domain={[0, 60]}
                tick={AXIS_STYLE}
                label={{ value: 'DevScore', angle: -90, position: 'insideLeft', offset: -5, style: LABEL_STYLE }}
              />
              <ZAxis range={[36, 36]} />
              <Tooltip content={<CustomTooltip />} cursor={{ strokeDasharray: '3 3' }} />
              <Legend
                formatter={(value) => <span style={LEGEND_STYLE}>{value}</span>}
              />
              <ReferenceLine y={8.5} stroke="#D94040" strokeDasharray="5 5" label={{ value: 'Youden threshold (8.5)', position: 'right', fill: '#D94040', fontSize: 11 }} />
              <Scatter name="Developmental" data={devGenes} fill="#6D62D9" shape={<CustomScatterDot />} />
              <Scatter name="Adult-onset" data={adultGenes} fill="#1D9E75" shape={<CustomScatterDot />} />
            </ScatterChart>
          </ResponsiveContainer>
          <div className="explorer-stats">
            <span>Spearman <em>ρ</em> = {META.spearman_rho} (p = {META.spearman_p})</span>
            <span>Partial <em>ρ</em> (controlling for class) = {META.partial_spearman_rho} (p = {META.partial_spearman_p})</span>
          </div>
        </div>
      ) : (
        <div className="explorer-chart-container">
          <ResponsiveContainer width="100%" height={420}>
            <ComposedChart margin={{ top: 20, right: 30, bottom: 40, left: 40 }}>
              <defs>
                <linearGradient id="devScoreGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#6D62D9" stopOpacity={0.25} />
                  <stop offset="100%" stopColor="#6D62D9" stopOpacity={0.04} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#F0EFEA" />
              <XAxis
                type="number"
                dataKey="fpr"
                domain={[0, 1]}
                tick={AXIS_STYLE}
                label={{ value: 'False positive rate', position: 'bottom', offset: 20, style: LABEL_STYLE }}
              />
              <YAxis
                type="number"
                dataKey="tpr"
                domain={[0, 1]}
                tick={AXIS_STYLE}
                label={{ value: 'True positive rate', angle: -90, position: 'insideLeft', offset: -5, style: LABEL_STYLE }}
              />
              <Tooltip contentStyle={{ fontFamily: "'Inter', sans-serif" }} />
              <Legend
                formatter={(value) => <span style={LEGEND_STYLE}>{value}</span>}
              />
              <Area data={devROC} type="monotone" dataKey="tpr" stroke="#6D62D9" strokeWidth={3} fill="url(#devScoreGradient)" name={`DevScore (AUC=${META.headline_auc})`} isAnimationActive={false} dot={false} />
              <Line data={chanceLine} type="linear" dataKey="tpr" stroke="#CCCCCC" strokeWidth={1} strokeDasharray="4 4" name="Random (AUC=0.50)" isAnimationActive={false} dot={false} />
              <Line data={caddROC} type="monotone" dataKey="tpr" stroke="#888780" strokeWidth={2} strokeDasharray="5 5" name={`CADD (AUC=${META.cadd_auc})`} isAnimationActive={false} dot={false} />
              <Line data={pp2ROC} type="monotone" dataKey="tpr" stroke="#E8803A" strokeWidth={1.5} strokeDasharray="3 3" name={`PolyPhen-2 (AUC=${META.polyphen_auc})`} isAnimationActive={false} dot={false} />
              <Line data={siftROC} type="monotone" dataKey="tpr" stroke="#D94040" strokeWidth={1.5} strokeDasharray="2 4" name={`SIFT (AUC=${META.sift_auc})`} isAnimationActive={false} dot={false} />
            </ComposedChart>
          </ResponsiveContainer>
          <div className="explorer-stats">
            <span>Headline DevScore (n={META.total_genes}) &mdash; AUC = {META.headline_auc}</span>
            <span>CADD margin: +{META.cadd_margin} | SIFT margin: +{META.sift_margin} | PolyPhen-2 margin: +{META.polyphen_margin}</span>
          </div>
        </div>
      )}
    </div>
  );
}
