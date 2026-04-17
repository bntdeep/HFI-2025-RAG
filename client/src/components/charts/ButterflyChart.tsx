import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  ReferenceLine,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import type { ButterflyRow } from '../../types/index.js';

interface Props {
  data: ButterflyRow[];
  countries: [string, string];
}

interface MirroredRow {
  param: string;
  country_a: number;
  country_b: number;
}

function toButterflyData(rows: ButterflyRow[]): MirroredRow[] {
  return rows.map(r => ({
    param: r.param,
    country_a: -Math.abs(r.country_a),
    country_b: Math.abs(r.country_b),
  }));
}

const tickFormatter = (v: number) => Math.abs(v).toFixed(1);

export function ButterflyChart({ data, countries }: Props) {
  const mirrored = toButterflyData(data);

  return (
    <ResponsiveContainer width="100%" height={Math.max(300, data.length * 52)}>
      <BarChart
        layout="vertical"
        data={mirrored}
        margin={{ top: 8, right: 60, bottom: 8, left: 140 }}
        barCategoryGap="30%"
      >
        <XAxis
          type="number"
          domain={[-10, 10]}
          tickFormatter={tickFormatter}
          tick={{ fontSize: 11 }}
          axisLine={false}
        />
        <YAxis
          type="category"
          dataKey="param"
          width={130}
          tick={{ fontSize: 12 }}
          axisLine={false}
          tickLine={false}
        />
        <ReferenceLine x={0} stroke="rgba(255,255,255,0.3)" strokeWidth={1} />
        <Bar dataKey="country_a" name={countries[0]} fill="#4a9eff" radius={[0, 2, 2, 0]} />
        <Bar dataKey="country_b" name={countries[1]} fill="#ff6b6b" radius={[2, 0, 0, 2]} />
        <Legend
          formatter={(value) => (
            <span style={{ fontSize: 12 }}>{value}</span>
          )}
        />
        <Tooltip
          formatter={(value: number, name: string) => [
            Math.abs(value).toFixed(2),
            name,
          ]}
          contentStyle={{
            background: '#1a1a1a',
            border: '1px solid rgba(255,255,255,0.1)',
            borderRadius: 4,
            fontSize: 12,
          }}
        />
      </BarChart>
    </ResponsiveContainer>
  );
}
