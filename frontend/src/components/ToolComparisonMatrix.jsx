import React from 'react';

export default function ToolComparisonMatrix() {
  return (
    <div className="mt-16">
      <h2 className="text-xl font-bold mb-4">Scientific Comparison of DevScore</h2>
      <div style={{ overflowX: 'auto', paddingBottom: '16px' }}>
        <table className="comparison-matrix-tbl w-full text-sm border-collapse">
          <thead>
            <tr>
              <th className="font-medium text-left p-3 border-b border-gray-300" style={{ minWidth: '160px' }}>Dimension</th>
              <th className="font-medium text-left p-3 border-b border-gray-300">SIFT</th>
              <th className="font-medium text-left p-3 border-b border-gray-300">PolyPhen-2</th>
              <th className="font-medium text-left p-3 border-b border-gray-300">CADD</th>
              <th className="font-medium text-left p-3 border-b border-gray-300 text-purple-700 bg-purple-50">DevScore (ours)</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td className="p-3 border-b border-gray-200 font-medium text-gray-900 whitespace-nowrap">Method type</td>
              <td className="p-3 border-b border-gray-200 text-gray-600">Sequence conservation</td>
              <td className="p-3 border-b border-gray-200 text-gray-600">Structure + conservation</td>
              <td className="p-3 border-b border-gray-200 text-gray-600">ML ensemble (C-score)</td>
              <td className="p-3 border-b border-gray-200 text-gray-600 bg-purple-50">Multiplicative formula</td>
            </tr>
            <tr>
              <td className="p-3 border-b border-gray-200 font-medium text-gray-900 whitespace-nowrap">Input</td>
              <td className="p-3 border-b border-gray-200 text-gray-600">AA substitution</td>
              <td className="p-3 border-b border-gray-200 text-gray-600">AA substitution + 3D</td>
              <td className="p-3 border-b border-gray-200 text-gray-600">Any variant type</td>
              <td className="p-3 border-b border-gray-200 text-gray-600 bg-purple-50">Any variant + gene</td>
            </tr>
            <tr>
              <td className="p-3 border-b border-gray-200 font-medium text-gray-900 whitespace-nowrap">Variant types</td>
              <td className="p-3 border-b border-gray-200 text-gray-600">Missense only</td>
              <td className="p-3 border-b border-gray-200 text-gray-600">Missense only</td>
              <td className="p-3 border-b border-gray-200 text-gray-600">SNV, indel, splice</td>
              <td className="p-3 border-b border-gray-200 text-gray-600 bg-purple-50">SNV, indel, splice</td>
            </tr>
            <tr>
              <td className="p-3 border-b border-gray-200 font-medium text-gray-900 whitespace-nowrap">Developmental context</td>
              <td className="p-3 border-b border-gray-200"><span className="badge-no">No</span></td>
              <td className="p-3 border-b border-gray-200"><span className="badge-no">No</span></td>
              <td className="p-3 border-b border-gray-200"><span className="badge-no">No</span></td>
              <td className="p-3 border-b border-gray-200 bg-purple-50"><span className="badge-yes">Yes — core axis</span></td>
            </tr>
            <tr>
              <td className="p-3 border-b border-gray-200 font-medium text-gray-900 whitespace-nowrap">Expression timing</td>
              <td className="p-3 border-b border-gray-200"><span className="badge-no">No</span></td>
              <td className="p-3 border-b border-gray-200"><span className="badge-no">No</span></td>
              <td className="p-3 border-b border-gray-200"><span className="badge-no">No</span></td>
              <td className="p-3 border-b border-gray-200 bg-purple-50"><span className="badge-yes">Yes — E_peak × C_stage</span></td>
            </tr>
            <tr>
              <td className="p-3 border-b border-gray-200 font-medium text-gray-900 whitespace-nowrap">Stage criticality weight</td>
              <td className="p-3 border-b border-gray-200"><span className="badge-no">No</span></td>
              <td className="p-3 border-b border-gray-200"><span className="badge-no">No</span></td>
              <td className="p-3 border-b border-gray-200"><span className="badge-no">No</span></td>
              <td className="p-3 border-b border-gray-200 bg-purple-50"><span className="badge-yes">Yes — Waddington-derived</span></td>
            </tr>
            <tr>
              <td className="p-3 border-b border-gray-200 font-medium text-gray-900 whitespace-nowrap">Domain essentiality</td>
              <td className="p-3 border-b border-gray-200"><span className="badge-partial">Partial</span></td>
              <td className="p-3 border-b border-gray-200"><span className="badge-yes">Yes (HumDiv/HumVar)</span></td>
              <td className="p-3 border-b border-gray-200"><span className="badge-partial">Partial (Reg. feat.)</span></td>
              <td className="p-3 border-b border-gray-200 bg-purple-50"><span className="badge-yes">Yes — UniProt domain class</span></td>
            </tr>
            <tr>
              <td className="p-3 border-b border-gray-200 font-medium text-gray-900 whitespace-nowrap">Interpretability (XAI)</td>
              <td className="p-3 border-b border-gray-200"><span className="badge-yes">Score + tolerance</span></td>
              <td className="p-3 border-b border-gray-200"><span className="badge-yes">Score + category</span></td>
              <td className="p-3 border-b border-gray-200"><span className="badge-no">Black box ML</span></td>
              <td className="p-3 border-b border-gray-200 bg-purple-50"><span className="badge-yes">Full component breakdown</span></td>
            </tr>
            <tr>
              <td className="p-3 border-b border-gray-200 font-medium text-gray-900 whitespace-nowrap">Score range</td>
              <td className="p-3 border-b border-gray-200 text-gray-600">0–1 (lower = damaging)</td>
              <td className="p-3 border-b border-gray-200 text-gray-600">0–1 (higher = damaging)</td>
              <td className="p-3 border-b border-gray-200 text-gray-600">1–99 PHRED-scaled</td>
              <td className="p-3 border-b border-gray-200 text-gray-600 bg-purple-50">0–100 (higher = more impact)</td>
            </tr>
            <tr>
              <td className="p-3 border-b border-gray-200 font-medium text-gray-900 whitespace-nowrap">Free &amp; open API</td>
              <td className="p-3 border-b border-gray-200"><span className="badge-yes">Yes</span></td>
              <td className="p-3 border-b border-gray-200"><span className="badge-yes">Yes</span></td>
              <td className="p-3 border-b border-gray-200"><span className="badge-yes">Yes (via VEP)</span></td>
              <td className="p-3 border-b border-gray-200 bg-purple-50"><span className="badge-yes">Yes — fully open</span></td>
            </tr>
            <tr>
              <td className="p-3 border-b border-gray-200 font-medium text-gray-900 whitespace-nowrap">Suited for congenital disease</td>
              <td className="p-3 border-b border-gray-200"><span className="badge-partial">Partial</span></td>
              <td className="p-3 border-b border-gray-200"><span className="badge-partial">Partial</span></td>
              <td className="p-3 border-b border-gray-200"><span className="badge-partial">Partial</span></td>
              <td className="p-3 border-b border-gray-200 bg-purple-50"><span className="badge-yes">Yes — primary use case</span></td>
            </tr>
            <tr>
              <td className="p-3 border-b border-gray-200 font-medium text-gray-900 whitespace-nowrap border-b-0">Training data bias</td>
              <td className="p-3 border-b border-gray-200 text-gray-600 border-b-0">Adult protein alignments</td>
              <td className="p-3 border-b border-gray-200 text-gray-600 border-b-0">Adult protein structures</td>
              <td className="p-3 border-b border-gray-200 text-gray-600 border-b-0">Adult ENCODE features</td>
              <td className="p-3 border-b border-gray-200 text-gray-600 bg-purple-50 border-b-0">Developmental expression series</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}
