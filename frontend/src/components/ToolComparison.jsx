import React from 'react';

export default function ToolComparison() {
  const tools = [
    { name: 'DevScore', focus: 'Developmental', years: '2024', score: '–' },
    { name: 'CADD', focus: 'General pathogenicity', years: '2014', score: '0-60' },
    { name: 'SIFT', focus: 'Protein conservation', years: '2003', score: '0-1' },
    { name: 'PolyPhen-2', focus: 'Protein structure', years: '2010', score: '0-1' }
  ];

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead className="bg-gray-100 border-b border-gray-300">
          <tr>
            <th className="px-4 py-2 text-left">Tool</th>
            <th className="px-4 py-2 text-left">Primary Focus</th>
            <th className="px-4 py-2 text-left">Published</th>
            <th className="px-4 py-2 text-left">Score Range</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200">
          {tools.map((tool) => (
            <tr key={tool.name}>
              <td className="px-4 py-2 font-semibold text-gray-900">{tool.name}</td>
              <td className="px-4 py-2">{tool.focus}</td>
              <td className="px-4 py-2">{tool.years}</td>
              <td className="px-4 py-2">{tool.score}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
