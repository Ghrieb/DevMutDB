import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

export default function StageTimeline({ stageData }) {
  const getColor = (criticality) => {
    if (criticality >= 0.95) return '#ef4444'; // red for gastrulation/neurulation
    if (criticality >= 0.7) return '#f97316'; // orange
    if (criticality >= 0.5) return '#eab308'; // yellow
    return '#22c55e'; // green for adult
  };

  const data = (stageData || []).map((item) => ({
    stage: item.stage,
    value: (item.tpm || 0) * (item.criticality || 0.25),
    tpm: item.tpm || 0,
    criticality: item.criticality || 0.25,
  }));

  return (
    <div className="w-full h-80">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="stage" angle={-45} textAnchor="end" height={100} />
          <YAxis label={{ value: 'TPM × Criticality', angle: -90, position: 'insideLeft' }} />
          <Tooltip
            formatter={(value) => [value.toFixed(2), 'Value']}
            labelFormatter={(label) => `Stage: ${label}`}
          />
          <Bar
            dataKey="value"
            fill="#7F77DD"
            radius={[8, 8, 0, 0]}
            shape={
              <CustomBar
                data={data}
                getColor={getColor}
              />
            }
          >
            {data.map((entry, index) => (
              <Bar key={index} dataKey="value" fill={getColor(entry.criticality)} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

function CustomBar(props) {
  const { fill, x, y, width, height, data, getColor } = props;
  if (!data) return null;
  const dataPoint = data[props.index];
  if (!dataPoint) return null;
  
  return (
    <rect
      x={x}
      y={y}
      width={width}
      height={height}
      fill={getColor(dataPoint.criticality)}
    />
  );
}
