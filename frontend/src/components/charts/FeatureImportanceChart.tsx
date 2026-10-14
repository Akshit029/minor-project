import React from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from 'recharts';
import type { FeatureImportanceItem } from '../../types/weather';

interface FeatureImportanceChartProps {
  data: FeatureImportanceItem[];
}

export const FeatureImportanceChart: React.FC<FeatureImportanceChartProps> = ({ data }) => {
  // Sort descending by importance
  const sortedData = [...data].sort((a, b) => a.importance - b.importance);

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const item = payload[0].payload as FeatureImportanceItem;
      return (
        <div className="bg-white p-3 rounded-lg border border-slate-200 shadow-md text-xs space-y-1 font-sans max-w-xs">
          <div className="font-bold text-slate-800 pb-1 border-b border-slate-100 flex justify-between">
            <span>{item.feature}</span>
            <span className="font-mono text-emerald-700 font-bold">
              {(item.importance * 100).toFixed(1)}%
            </span>
          </div>
          <p className="text-[11px] text-slate-600 leading-normal">
            {item.description}
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="space-y-3 font-sans">
      <div className="flex items-center justify-between text-xs text-slate-500">
        <span>Gini Impurity reduction across 100 decision trees (Random Forest).</span>
        <span className="font-mono text-[11px] text-slate-600">Strictly Leakage-Free</span>
      </div>

      <div className="h-72 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            layout="vertical"
            data={sortedData}
            margin={{ top: 5, right: 30, left: 75, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" horizontal={false} />
            <XAxis
              type="number"
              domain={[0, 0.4]}
              stroke="#94a3b8"
              fontSize={11}
              tickLine={false}
              axisLine={{ stroke: '#e2e8f0' }}
              tickFormatter={(v) => `${(v * 100).toFixed(0)}%`}
            />
            <YAxis
              type="category"
              dataKey="feature"
              stroke="#475569"
              fontSize={11}
              tickLine={false}
              axisLine={{ stroke: '#e2e8f0' }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Bar
              dataKey="importance"
              fill="#0f172a"
              radius={[0, 4, 4, 0]}
              barSize={20}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="text-[11px] text-slate-500 flex items-center justify-between">
        <span>All features originate strictly from forecast issuance parameters (lead, cycle, district, value).</span>
        <span className="text-amber-700 font-medium">Demo Data (Week 5 Prototype)</span>
      </div>
    </div>
  );
};
