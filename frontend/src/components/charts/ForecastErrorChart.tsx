import React, { useState } from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts';
import type { LeadDayMetrics } from '../../types/weather';

interface ForecastErrorChartProps {
  data: LeadDayMetrics[];
}

export const ForecastErrorChart: React.FC<ForecastErrorChartProps> = ({ data }) => {
  const [metricFilter, setMetricFilter] = useState<'all' | 'mae' | 'rmse' | 'bias'>('all');

  const chartData = data.map((item) => ({
    leadDay: `Day ${item.leadDay}`,
    leadHours: `${item.leadHours}h`,
    MAE: Number(item.regionalMAE.toFixed(2)),
    RMSE: Number(item.regionalRMSE.toFixed(2)),
    Bias: Number(item.regionalBias.toFixed(2)),
  }));

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 rounded-lg border border-slate-200 shadow-md text-xs space-y-1 font-sans">
          <div className="font-bold text-slate-800 pb-1 border-b border-slate-100 flex items-center justify-between gap-4">
            <span>{label}</span>
            <span className="font-mono text-slate-400 text-[11px]">
              {payload[0]?.payload?.leadHours} Lookahead
            </span>
          </div>
          {payload.map((entry: any, index: number) => (
            <div key={`err-${index}`} className="flex items-center justify-between gap-4 py-0.5">
              <span className="flex items-center gap-1.5 text-slate-600">
                <span
                  className="w-2 h-2 rounded-full"
                  style={{ backgroundColor: entry.color }}
                />
                {entry.name}:
              </span>
              <span className="font-mono font-bold text-slate-900">
                {entry.value} °C
              </span>
            </div>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="space-y-3">
      {/* Metric Toggles */}
      <div className="flex items-center justify-between">
        <span className="text-xs text-slate-500 font-medium">
          Error Metric (Units: °C standardized against ERA5)
        </span>
        <div className="flex items-center gap-1 bg-slate-100 p-0.5 rounded-lg border border-slate-200">
          {(['all', 'mae', 'rmse', 'bias'] as const).map((mode) => (
            <button
              key={mode}
              onClick={() => setMetricFilter(mode)}
              className={`px-2.5 py-1 rounded text-xs font-medium uppercase transition-colors cursor-pointer ${
                metricFilter === mode
                  ? 'bg-white text-slate-900 shadow-2xs font-semibold'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              {mode}
            </button>
          ))}
        </div>
      </div>

      <div className="h-72 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={chartData}
            margin={{ top: 10, right: 15, left: -20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
            <XAxis
              dataKey="leadDay"
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
              unit="°"
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />

            {(metricFilter === 'all' || metricFilter === 'mae') && (
              <Line
                type="monotone"
                dataKey="MAE"
                stroke="#0284c7" // sky-600
                strokeWidth={2.5}
                dot={{ r: 3.5, fill: '#0284c7' }}
                name="MAE (Mean Absolute Error)"
              />
            )}

            {(metricFilter === 'all' || metricFilter === 'rmse') && (
              <Line
                type="monotone"
                dataKey="RMSE"
                stroke="#6366f1" // indigo-500
                strokeWidth={2.5}
                dot={{ r: 3.5, fill: '#6366f1' }}
                strokeDasharray="4 2"
                name="RMSE (Root Mean Square Error)"
              />
            )}

            {(metricFilter === 'all' || metricFilter === 'bias') && (
              <Line
                type="monotone"
                dataKey="Bias"
                stroke="#f59e0b" // amber-500
                strokeWidth={2}
                dot={{ r: 3, fill: '#f59e0b' }}
                strokeDasharray="2 2"
                name="Signed Bias (GFS - ERA5)"
              />
            )}
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="text-[11px] text-slate-500 flex items-center justify-between">
        <span>Positive bias indicates NOAA GFS overestimates ECMWF ERA5 reanalysis reference.</span>
        <span className="font-mono">Error scale threshold: 2.0 °C</span>
      </div>
    </div>
  );
};
