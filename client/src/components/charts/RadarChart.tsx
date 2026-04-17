import {
  Radar,
  RadarChart as RechartsRadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Tooltip,
} from 'recharts';

interface RadarDataPoint {
  subject: string;
  value: number;
}

interface Props {
  data: RadarDataPoint[];
  color?: string;
}

export function RadarChart({ data, color = '#4a9eff' }: Props) {
  return (
    <ResponsiveContainer width="100%" height={320}>
      <RechartsRadarChart data={data} margin={{ top: 10, right: 30, bottom: 10, left: 30 }}>
        <PolarGrid stroke="rgba(255,255,255,0.1)" />
        <PolarAngleAxis dataKey="subject" tick={{ fontSize: 11, fill: 'rgba(255,255,255,0.7)' }} />
        <PolarRadiusAxis
          domain={[0, 10]}
          tick={{ fontSize: 9, fill: 'rgba(255,255,255,0.4)' }}
          axisLine={false}
          tickCount={5}
        />
        <Radar
          dataKey="value"
          stroke={color}
          fill={color}
          fillOpacity={0.25}
          dot={{ r: 3, fill: color }}
        />
        <Tooltip
          formatter={(v: number) => [v.toFixed(2), 'Score']}
          contentStyle={{
            background: '#1a1a1a',
            border: '1px solid rgba(255,255,255,0.1)',
            borderRadius: 4,
            fontSize: 12,
          }}
        />
      </RechartsRadarChart>
    </ResponsiveContainer>
  );
}
