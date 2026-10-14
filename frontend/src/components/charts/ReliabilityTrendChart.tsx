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
  ReferenceLine,
} from 'recharts';
import type { LeadDayMetrics, DistrictName } from '../../types/weather';
import { ScientificDisclaimer } from '../common/ScientificDisclaimer';

interface ReliabilityTrendChartProps {
  data: LeadDayMetrics[];
  highlightDistrict?: DistrictName | null;
}

export const ReliabilityTrendChart: React.FC<ReliabilityTrendChartProps> = ({
  data,
  highlightDistrict,
}) => {
  const [showAllDistricts, setShowAllDistricts] = useState(true);

  // Format data for chart
  const chartData = data.map((item) => ({
    leadDay: `Day ${item.leadDay}`,
    leadHours: `${item.leadHours}h`,
    dayNum: item.leadDay,
    Regional: Number(item.regionalReliability.toFixed(2)),
    Srinagar: Number(item.districtScores.Srinagar.reliability.toFixed(2)),
    Jammu: Number(item.districtScores.Jammu.reliability.toFixed(2)),
    Anantnag: Number(item.districtScores.Anantnag.reliability.toFixed(2)),
    Baramulla: Number(item.districtScores.Baramulla.reliability.toFixed(2)),
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
            <div key={`tooltip-${index}`} className="flex items-center justify-between gap-4 py-0.5">
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
    <div className="space-y-3">
      {/* Controls */}
      <div className="flex items-center justify-between text-xs pb-1">
        <span className="text-slate-500 font-medium">
          Empirical Score Range: 0.0 (Unreliable) to 1.0 (Optimal)
        </span>
        <button
          onClick={() => setShowAllDistricts(!showAllDistricts)}
          className="text-slate-600 hover:text-slate-900 font-medium underline underline-offset-2 transition-colors cursor-pointer"
        >
          {showAllDistricts ? 'Focus Regional Mean' : 'Show All Districts'}
        </button>
      </div>

      {/* Chart */}
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
              domain={[0, 1]}
              ticks={[0, 0.25, 0.5, 0.75, 1.0]}
              stroke="#94a3b8"
              fontSize={11}
              tickLine={false}
              axisLine={{ stroke: '#e2e8f0' }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend
              wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }}
              iconType="circle"
            />
            
            {/* Critical Threshold Reference Line (0.50) */}
            <ReferenceLine
              y={0.5}
              stroke="#f59e0b"
              strokeDasharray="4 4"
              label={{
                value: 'Uncertainty Threshold (0.50)',
                fill: '#b45309',
                fontSize: 10,
                position: 'insideTopRight',
              }}
            />

            {/* Regional Aggregate Line */}
            <Line
              type="monotone"
              dataKey="Regional"
              stroke="#0f172a"
              strokeWidth={showAllDistricts ? 3 : 3.5}
              dot={{ r: 4, fill: '#0f172a', strokeWidth: 0 }}
              activeDot={{ r: 6 }}
            />

            {/* District Lines */}
            {showAllDistricts && (
              <>
                <Line
                  type="monotone"
                  dataKey="Srinagar"
                  stroke="#3b82f6"
                  strokeWidth={highlightDistrict === 'Srinagar' ? 3 : 1.8}
                  dot={{ r: 3 }}
                  strokeDasharray={highlightDistrict === 'Srinagar' ? undefined : '2 2'}
                />
                <Line
                  type="monotone"
                  dataKey="Jammu"
                  stroke="#10b981"
                  strokeWidth={highlightDistrict === 'Jammu' ? 3 : 1.8}
                  dot={{ r: 3 }}
                />
                <Line
                  type="monotone"
                  dataKey="Anantnag"
                  stroke="#ef4444"
                  strokeWidth={highlightDistrict === 'Anantnag' ? 3 : 1.8}
                  dot={{ r: 3 }}
                />
                <Line
                  type="monotone"
                  dataKey="Baramulla"
                  stroke="#f97316"
                  strokeWidth={highlightDistrict === 'Baramulla' ? 3 : 1.8}
                  dot={{ r: 3 }}
                  strokeDasharray="3 3"
                />
              </>
            )}
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Mandatory Scientific Explanation note as required by the prompt */}
      <ScientificDisclaimer type="reliability" compact />
    </div>
  );
};
