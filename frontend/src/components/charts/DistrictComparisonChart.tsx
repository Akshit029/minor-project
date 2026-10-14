import React, { useState } from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts';
import type { DistrictInfo, DistrictName } from '../../types/weather';
import { Badge } from '../common/Badge';

interface DistrictComparisonChartProps {
  districts: DistrictInfo[];
  selectedDistrict?: DistrictName | null;
  onSelectDistrict?: (name: DistrictName) => void;
}

export const DistrictComparisonChart: React.FC<DistrictComparisonChartProps> = ({
  districts,
  selectedDistrict,
  onSelectDistrict,
}) => {
  const [metricKey, setMetricKey] = useState<'reliability' | 'error' | 'bust'>('reliability');

  const comparisonData = districts.map((d) => ({
    name: d.name,
    Reliability: Number(d.reliability.toFixed(2)),
    MAE: Number(d.mae.toFixed(2)),
    RMSE: Number(d.rmse.toFixed(2)),
    Bias: Number(d.bias.toFixed(2)),
    'Bust Probability (%)': d.bustProbability,
    elevation: d.elevationMeters,
  }));

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 rounded-lg border border-slate-200 shadow-md text-xs space-y-1 font-sans">
          <div className="font-bold text-slate-800 pb-1 border-b border-slate-100 flex items-center justify-between gap-4">
            <span>{label}</span>
            <span className="font-mono text-slate-400 text-[11px]">
              Elev: {payload[0]?.payload?.elevation}m
            </span>
          </div>
          {payload.map((entry: any, index: number) => (
            <div key={`comp-${index}`} className="flex items-center justify-between gap-4 py-0.5">
              <span className="flex items-center gap-1.5 text-slate-600">
                <span
                  className="w-2 h-2 rounded-full"
                  style={{ backgroundColor: entry.color }}
                />
                {entry.name}:
              </span>
              <span className="font-mono font-bold text-slate-900">
                {entry.value}
              </span>
            </div>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="space-y-4">
      {/* Metric Mode Selector & Interactive District Chips */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5">
        <div className="flex flex-wrap items-center gap-1.5">
          {districts.map((d) => {
            const isSelected = selectedDistrict === d.name;
            return (
              <button
                key={d.id}
                onClick={() => onSelectDistrict && onSelectDistrict(d.name)}
                className={`px-2.5 sm:px-3 py-1 rounded-lg text-[11px] sm:text-xs font-medium border transition-all cursor-pointer ${
                  isSelected
                    ? 'bg-slate-900 text-white border-slate-900 shadow-2xs'
                    : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-50'
                }`}
              >
                {d.name}
              </button>
            );
          })}
        </div>

        <div className="flex items-center gap-1 bg-slate-100 p-0.5 rounded-lg border border-slate-200 self-start sm:self-auto overflow-x-auto max-w-full">
          <button
            onClick={() => setMetricKey('reliability')}
            className={`px-2 sm:px-2.5 py-1 rounded text-[11px] sm:text-xs transition-colors cursor-pointer whitespace-nowrap ${
              metricKey === 'reliability'
                ? 'bg-white text-slate-900 font-semibold shadow-2xs'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Reliability
          </button>
          <button
            onClick={() => setMetricKey('error')}
            className={`px-2 sm:px-2.5 py-1 rounded text-[11px] sm:text-xs transition-colors cursor-pointer whitespace-nowrap ${
              metricKey === 'error'
                ? 'bg-white text-slate-900 font-semibold shadow-2xs'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Errors
          </button>
          <button
            onClick={() => setMetricKey('bust')}
            className={`px-2 sm:px-2.5 py-1 rounded text-[11px] sm:text-xs transition-colors cursor-pointer whitespace-nowrap ${
              metricKey === 'bust'
                ? 'bg-white text-slate-900 font-semibold shadow-2xs'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Bust Risk (%)
          </button>
        </div>
      </div>

      {/* Bar Chart */}
      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={comparisonData}
            margin={{ top: 10, right: 15, left: -20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
            <XAxis
              dataKey="name"
              stroke="#94a3b8"
              fontSize={11}
              tickLine={false}
              axisLine={{ stroke: '#e2e8f0' }}
            />
            <YAxis
              stroke="#94a3b8"
              fontSize={11}
              tickLine={false}
              axisLine={{ stroke: '#e2e8f0' }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />

            {metricKey === 'reliability' && (
              <Bar
                dataKey="Reliability"
                fill="#059669"
                radius={[4, 4, 0, 0]}
                barSize={38}
              />
            )}

            {metricKey === 'error' && (
              <>
                <Bar
                  dataKey="MAE"
                  fill="#0284c7"
                  radius={[4, 4, 0, 0]}
                  barSize={24}
                />
                <Bar
                  dataKey="RMSE"
                  fill="#6366f1"
                  radius={[4, 4, 0, 0]}
                  barSize={24}
                />
              </>
            )}

            {metricKey === 'bust' && (
              <Bar
                dataKey="Bust Probability (%)"
                fill="#e11d48"
                radius={[4, 4, 0, 0]}
                barSize={38}
              />
            )}
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* District Comparison Mini Cards Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2">
        {districts.map((dist) => {
          const isSelected = selectedDistrict === dist.name;
          return (
            <div
              key={dist.id}
              onClick={() => onSelectDistrict && onSelectDistrict(dist.name)}
              className={`p-3 rounded-lg border transition-all cursor-pointer ${
                isSelected
                  ? 'bg-slate-50 border-slate-900 shadow-2xs'
                  : 'bg-white border-slate-200/80 hover:border-slate-300'
              }`}
            >
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-xs font-bold text-slate-800">{dist.name}</span>
                <Badge
                  variant={
                    dist.reliability >= 0.7
                      ? 'emerald'
                      : dist.reliability >= 0.5
                      ? 'amber'
                      : 'rose'
                  }
                  size="xs"
                >
                  R: {dist.reliability.toFixed(2)}
                </Badge>
              </div>
              <div className="text-[11px] text-slate-500 space-y-0.5">
                <div className="flex justify-between">
                  <span>MAE:</span>
                  <span className="font-mono text-slate-700">{dist.mae.toFixed(2)} °C</span>
                </div>
                <div className="flex justify-between">
                  <span>Bust Prob:</span>
                  <span className="font-mono text-slate-700">{dist.bustProbability}%</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
