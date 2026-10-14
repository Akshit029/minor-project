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
  ReferenceDot,
} from 'recharts';
import type { ForecastVsReferenceRecord } from '../../types/weather';
import { APP_CONFIG } from '../../data/config';
import { Badge } from '../common/Badge';

interface ForecastVsReferenceChartProps {
  data: ForecastVsReferenceRecord[];
  districtName: string;
}

export const ForecastVsReferenceChart: React.FC<ForecastVsReferenceChartProps> = ({
  data,
  districtName,
}) => {
  const [showBiasCorrected, setShowBiasCorrected] = useState(true);

  const chartData = data.map((item) => ({
    leadLabel: `Day ${item.leadDay}`,
    leadDay: item.leadDay,
    [APP_CONFIG.terminology.forecastSource]: item.gfsForecast,
    [APP_CONFIG.terminology.referenceSource]: item.era5Reference,
    'Bias-Corrected Forecast': item.biasCorrectedForecast,
    signedError: item.signedError,
    absoluteError: item.absoluteError,
    isBust: item.isBust,
  }));

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const record = payload[0]?.payload;
      return (
        <div className="bg-white p-3.5 rounded-lg border border-slate-200 shadow-lg text-xs space-y-1.5 font-sans min-w-[220px]">
          <div className="font-bold text-slate-900 pb-1 border-b border-slate-100 flex items-center justify-between">
            <span>{label} Horizon</span>
            {record?.isBust && (
              <Badge variant="rose" size="xs">
                BUST OUTLIER
              </Badge>
            )}
          </div>
          {payload.map((entry: any, index: number) => (
            <div key={`fvr-tip-${index}`} className="flex items-center justify-between py-0.5">
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
          <div className="pt-1.5 border-t border-slate-100 text-[11px] text-slate-500 flex justify-between">
            <span>Signed Error (GFS - ERA5):</span>
            <span className={`font-mono font-bold ${record?.signedError > 0 ? 'text-amber-600' : 'text-sky-600'}`}>
              {record?.signedError > 0 ? `+${record?.signedError}` : record?.signedError} °C
            </span>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="space-y-4">
      {/* Header and Toggle */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 text-xs">
        <div>
          <span className="font-semibold text-slate-800">
            {districtName}: Continuous Lookahead Horizon
          </span>
          <span className="text-slate-500 ml-2">
            Standardized 2m Temperature (°C)
          </span>
        </div>
        <div className="flex items-center gap-2">
          <label className="flex items-center gap-1.5 text-slate-600 cursor-pointer text-xs font-medium">
            <input
              type="checkbox"
              checked={showBiasCorrected}
              onChange={(e) => setShowBiasCorrected(e.target.checked)}
              className="rounded border-slate-300 text-slate-900 focus:ring-slate-500 cursor-pointer"
            />
            <span>Include Bias-Corrected Forecast</span>
          </label>
        </div>
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
              dataKey="leadLabel"
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
              unit="°C"
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />

            {/* NOAA GFS Forecast */}
            <Line
              type="monotone"
              dataKey={APP_CONFIG.terminology.forecastSource}
              stroke="#e11d48" // rose-600
              strokeWidth={2.5}
              dot={{ r: 4, fill: '#e11d48' }}
              name={APP_CONFIG.terminology.forecastSource}
            />

            {/* ECMWF ERA5 Reference */}
            <Line
              type="monotone"
              dataKey={APP_CONFIG.terminology.referenceSource}
              stroke="#0284c7" // sky-600
              strokeWidth={2.5}
              dot={{ r: 4, fill: '#0284c7' }}
              name={APP_CONFIG.terminology.referenceSource}
            />

            {/* Optional Bias-Corrected Line */}
            {showBiasCorrected && (
              <Line
                type="monotone"
                dataKey="Bias-Corrected Forecast"
                stroke="#10b981" // emerald-500
                strokeWidth={2}
                strokeDasharray="4 3"
                dot={{ r: 3, fill: '#10b981' }}
                name="Historical Bias Corrected"
              />
            )}
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Explanatory Scientific Caption */}
      <div className="p-3 bg-slate-50 border border-slate-200/90 rounded-lg text-xs text-slate-600 space-y-1">
        <div className="font-semibold text-slate-700">
          Verification Semantics:
        </div>
        <p className="text-[11px] leading-relaxed">
          The red curve traces the raw {APP_CONFIG.terminology.forecastSource} issued at 00 UTC. The blue curve denotes the verified {APP_CONFIG.terminology.referenceSource} at corresponding valid times. Dotted green depicts the historical mean-bias corrected forecast learned strictly from earlier training splits (70%) with regional fallback.
        </p>
      </div>
    </div>
  );
};
