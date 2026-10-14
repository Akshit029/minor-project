import React from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ReferenceLine,
} from 'recharts';
import type { PRCurvePoint } from '../../types/weather';

interface PrecisionRecallChartProps {
  data: PRCurvePoint[];
}

export const PrecisionRecallChart: React.FC<PrecisionRecallChartProps> = ({ data }) => {
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 rounded-lg border border-slate-200 shadow-md text-xs space-y-1 font-sans">
          <div className="font-bold text-slate-800 pb-1 border-b border-slate-100 flex items-center justify-between gap-4">
            <span>Recall: {(Number(label) * 100).toFixed(0)}%</span>
          </div>
          {payload.map((entry: any, index: number) => (
            <div key={`pr-tip-${index}`} className="flex items-center justify-between gap-4 py-0.5">
              <span className="flex items-center gap-1.5 text-slate-600">
                <span
                  className="w-2 h-2 rounded-full"
                  style={{ backgroundColor: entry.color }}
                />
                {entry.name}:
              </span>
              <span className="font-mono font-bold text-slate-900">
                {(entry.value * 100).toFixed(1)}% Precision
              </span>
            </div>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="space-y-3 font-sans">
      <div className="flex items-center justify-between text-xs text-slate-500">
        <span>Evaluates classifier trade-off under extreme class imbalance (10% bust events).</span>
        <span className="font-mono text-[11px] text-slate-700">Random Forest AP: 0.846</span>
      </div>

      <div className="h-72 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={data}
            margin={{ top: 10, right: 15, left: -20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
            <XAxis
              dataKey="recall"
              stroke="#94a3b8"
              fontSize={11}
              tickLine={false}
              axisLine={{ stroke: '#e2e8f0' }}
              tickFormatter={(v) => `${(v * 100).toFixed(0)}%`}
              label={{ value: 'Recall', position: 'insideBottomRight', offset: -5, fontSize: 10 }}
            />
            <YAxis
              domain={[0, 1]}
              stroke="#94a3b8"
              fontSize={11}
              tickLine={false}
              axisLine={{ stroke: '#e2e8f0' }}
              tickFormatter={(v) => `${(v * 100).toFixed(0)}%`}
              label={{ value: 'Precision', angle: -90, position: 'insideLeft', fontSize: 10 }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />

            {/* Baseline Random Chance (No-skill rate = 0.10) */}
            <ReferenceLine
              y={0.10}
              stroke="#cbd5e1"
              strokeDasharray="4 4"
              label={{
                value: 'No-Skill Base Rate (0.10)',
                fill: '#94a3b8',
                fontSize: 10,
                position: 'insideBottomRight',
              }}
            />

            <Line
              type="monotone"
              dataKey="randomForest"
              stroke="#059669" // emerald-600
              strokeWidth={2.5}
              dot={{ r: 3, fill: '#059669' }}
              name="Random Forest (AP = 0.846)"
            />

            <Line
              type="monotone"
              dataKey="logisticRegression"
              stroke="#6366f1" // indigo-500
              strokeWidth={2}
              strokeDasharray="3 3"
              dot={{ r: 2.5, fill: '#6366f1' }}
              name="Logistic Regression (AP = 0.712)"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="text-[11px] text-slate-500 flex items-center justify-between">
        <span>Higher Average Precision (AP) indicates stronger discrimination at strict false alarm tolerances.</span>
      </div>
    </div>
  );
};
