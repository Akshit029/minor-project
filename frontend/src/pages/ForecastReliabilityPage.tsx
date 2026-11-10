import React, { useEffect, useState } from 'react';
import { WeatherApi } from '../services/api';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { ReliabilityHeatmap } from '../components/charts/ReliabilityHeatmap';
import { JKLeafletMap } from '../components/map/JKLeafletMap';
import { DistrictComparisonChart } from '../components/charts/DistrictComparisonChart';
import type { LeadDayMetrics, DistrictInfo, DistrictName } from '../types/weather';
import { 
  Activity, 
  Calendar, 
  ShieldCheck, 
  Info 
} from 'lucide-react';
import {
  ResponsiveContainer,
  ComposedChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ReferenceArea
} from 'recharts';

export const ForecastReliabilityPage: React.FC = () => {
  const [leadDayMetrics, setLeadDayMetrics] = useState<LeadDayMetrics[]>([]);
  const [districts, setDistricts] = useState<DistrictInfo[]>([]);
  const [selectedLeadDay, setSelectedLeadDay] = useState<number>(5);
  const [selectedDistrict, setSelectedDistrict] = useState<DistrictName | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([WeatherApi.getReliability(), WeatherApi.getForecast()]).then(
      ([relRes, fcastRes]) => {
        setLeadDayMetrics(relRes.leadDayMetrics);
        setDistricts(fcastRes);
        setLoading(false);
      }
    );
  }, []);

  if (loading || leadDayMetrics.length === 0) {
    return (
      <div className="space-y-6">
        <div className="h-24 bg-white rounded-xl border border-slate-200 animate-pulse" />
        <div className="h-64 bg-white rounded-xl border border-slate-200 animate-pulse" />
      </div>
    );
  }

  // Active metrics for the selected lead day
  const currentLeadMetric = leadDayMetrics.find((m) => m.leadDay === selectedLeadDay) || leadDayMetrics[4];

  // Dynamically update district list representations for the selected lead day
  const updatedDistricts: DistrictInfo[] = districts.map((dist) => {
    const scoreObj = currentLeadMetric.districtScores[dist.name];
    if (scoreObj) {
      return {
        ...dist,
        reliability: scoreObj.reliability,
        mae: scoreObj.mae,
        rmse: scoreObj.rmse,
        bias: scoreObj.bias,
        bustProbability: scoreObj.bustProbability,
        currentForecast: {
          ...dist.currentForecast,
          leadDay: selectedLeadDay,
          leadHours: selectedLeadDay * 24,
        },
      };
    }
    return dist;
  });

  return (
    <div className="space-y-6 font-sans">
      {/* Page Header */}
      <div className="bg-white rounded-xl border border-slate-200/90 shadow-2xs p-6 space-y-4">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1.5">
              <Badge variant="emerald" size="xs">
                Mathematical Model: Week 4 Formulation
              </Badge>
              <Badge variant="slate" size="xs">
                R = R_error × C
              </Badge>
            </div>
            <h1 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">
              Spatiotemporal Forecast Reliability
            </h1>
            <p className="text-xs sm:text-sm text-slate-500 mt-1 max-w-3xl leading-relaxed">
              Decoupling forecast accuracy from sample confidence. Explore lead days 1 through 10 across the four representative districts of Jammu &amp; Kashmir.
            </p>
          </div>

          <div className="flex items-center gap-2 bg-slate-50 border border-slate-200/80 p-2 rounded-xl text-xs">
            <span className="text-slate-500 font-medium">Verification Target:</span>
            <span className="font-semibold text-slate-800">2m Temperature (TMP)</span>
          </div>
        </div>

        {/* Lead Day Selector Buttons (Day 1 to Day 10) */}
        <div className="pt-2 border-t border-slate-100">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-slate-700 uppercase tracking-wider flex items-center gap-1.5">
              <Calendar className="w-3.5 h-3.5 text-slate-500" />
              Select Forecast Lead Horizon:
            </span>
            <span className="font-mono text-xs text-indigo-700 font-bold">
              Day {selectedLeadDay} ({selectedLeadDay * 24}h Lookahead)
            </span>
          </div>

          <div className="grid grid-cols-5 sm:grid-cols-10 gap-1.5">
            {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((day) => {
              const isSelected = selectedLeadDay === day;
              const metric = leadDayMetrics.find((m) => m.leadDay === day);
              const rel = metric?.regionalReliability ?? 0.5;

              return (
                <button
                  key={day}
                  onClick={() => setSelectedLeadDay(day)}
                  className={`py-2 px-1 rounded-lg border text-center transition-all cursor-pointer ${
                    isSelected
                      ? 'bg-slate-900 text-white border-slate-900 shadow-sm ring-2 ring-slate-900/20'
                      : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-50 hover:border-slate-300'
                  }`}
                >
                  <div className="text-xs font-bold leading-none">Day {day}</div>
                  <div className={`text-[10px] font-mono mt-1 ${isSelected ? 'text-slate-300' : 'text-slate-500'}`}>
                    R: {rel.toFixed(2)}
                  </div>
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Selected Lead Day Metric Overview KPIs */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <Card noPadding className="p-4 bg-white">
          <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block">
            Regional Reliability (R)
          </span>
          <div className="text-2xl font-bold font-mono text-slate-900 mt-1">
            {currentLeadMetric.regionalReliability.toFixed(2)}
          </div>
          <span className="text-[11px] text-slate-500">Day {selectedLeadDay} Mean</span>
        </Card>

        <Card noPadding className="p-4 bg-white">
          <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block">
            Regional MAE
          </span>
          <div className="text-2xl font-bold font-mono text-sky-700 mt-1">
            {currentLeadMetric.regionalMAE.toFixed(2)} °C
          </div>
          <span className="text-[11px] text-slate-500">Mean Absolute Error</span>
        </Card>

        <Card noPadding className="p-4 bg-white">
          <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block">
            Regional RMSE
          </span>
          <div className="text-2xl font-bold font-mono text-indigo-700 mt-1">
            {currentLeadMetric.regionalRMSE.toFixed(2)} °C
          </div>
          <span className="text-[11px] text-slate-500">Root Mean Square</span>
        </Card>

        <Card noPadding className="p-4 bg-white">
          <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block">
            Regional Signed Bias
          </span>
          <div className="text-2xl font-bold font-mono text-amber-700 mt-1">
            +{currentLeadMetric.regionalBias.toFixed(2)} °C
          </div>
          <span className="text-[11px] text-slate-500">GFS Overestimate</span>
        </Card>

        <Card noPadding className="p-4 bg-white">
          <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block">
            Regional Bust Risk
          </span>
          <div className="text-2xl font-bold font-mono text-rose-700 mt-1">
            {currentLeadMetric.regionalBustProb}%
          </div>
          <span className="text-[11px] text-rose-600">Day {selectedLeadDay} Est.</span>
        </Card>
      </div>

      {/* Heatmap Section */}
      <Card
        title="Spatiotemporal Reliability Heatmap Matrix"
        subtitle="Visualizing empirical reliability R across districts (rows) and lead horizon Days 1–10 (columns)"
        action={
          <Badge variant="slate" size="xs">
            40 District-Lead Cells
          </Badge>
        }
      >
        <ReliabilityHeatmap
          selectedDistrict={selectedDistrict}
          onSelectDistrict={(name) => setSelectedDistrict(name)}
          selectedLeadDay={selectedLeadDay}
          onSelectLeadDay={(day) => setSelectedLeadDay(day)}
        />
      </Card>

      {/* District Comparison & Map for the Selected Lead Day */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* District Comparison for selected lead day */}
        <div className="lg:col-span-7">
          <Card
            title={`District Performance on Lead Day ${selectedLeadDay}`}
            subtitle="Comparing spatial skill differences between Srinagar, Jammu, Anantnag, and Baramulla"
          >
            <DistrictComparisonChart
              districts={updatedDistricts}
              selectedDistrict={selectedDistrict}
              onSelectDistrict={(name) => setSelectedDistrict(name)}
            />
          </Card>
        </div>

        {/* Dynamic Map on selected lead day */}
        <div className="lg:col-span-5">
          <Card
            title={`Spatial Reliability (Day ${selectedLeadDay})`}
            subtitle="Map updates dynamically with selected lead day metrics"
          >
            <JKLeafletMap
              districts={updatedDistricts}
              selectedDistrict={selectedDistrict}
              onSelectDistrict={(name) => setSelectedDistrict(name)}
              leadDay={selectedLeadDay}
            />
          </Card>
        </div>
      </div>

      {/* Week 8: Forecast Uncertainty Analysis (1 to 10 Days) */}
      <Card
        title="Forecast Uncertainty Analysis across Lead Days 1 to 10 (Week 8)"
        subtitle="Empirical verification error, standard errors, and spread metrics across medium-range horizons"
        icon={<Activity className="w-5 h-5 text-indigo-600" />}
        action={
          <div className="flex items-center gap-2">
            <Badge variant="emerald" size="xs">Days 1–2 Verified</Badge>
            <Badge variant="slate" size="xs">Days 3–10 Extended</Badge>
          </div>
        }
      >
        <div className="space-y-5">
          {/* Scientific Integrity Banner */}
          <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200/90 text-xs text-slate-700 space-y-1">
            <div className="flex items-center gap-2 font-semibold text-slate-900">
              <Info className="w-4 h-4 text-indigo-600 shrink-0" />
              <span>Multi-Horizon Verification &amp; Data Provenance</span>
            </div>
            <p className="text-[11px] text-slate-600 leading-relaxed pl-6">
              Forecast verification is strictly evaluated against actual matched GFS-versus-ERA5 pairs. In the current test cycle, <strong>Lead Days 1 (24h) and 2 (48h)</strong> have complete empirical ground truth (44 matched validation events). Lead Days 3 through 10 represent extended medium-range lookahead horizons where historical reanalysis pairs are pending or unobserved. No synthetic weather observations or fabricated confidence bounds are generated.
            </p>
          </div>

          {/* Interactive Multi-Horizon Uncertainty Chart */}
          <div className="h-72 w-full pt-2">
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart
                data={leadDayMetrics.map((m) => {
                  const isVerified = m.leadDay <= 2;
                  return {
                    leadDay: `Day ${m.leadDay}`,
                    dayNum: m.leadDay,
                    mae: m.regionalMAE,
                    rmse: m.regionalRMSE,
                    reliability: m.regionalReliability,
                    bustProb: m.regionalBustProb,
                    status: isVerified ? 'Verified' : 'Extended Horizon'
                  };
                })}
                margin={{ top: 10, right: 25, left: -10, bottom: 0 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                <XAxis dataKey="leadDay" tick={{ fontSize: 11 }} />
                <YAxis
                  yAxisId="left"
                  tick={{ fontSize: 11 }}
                  unit="°C"
                  domain={[0, 8]}
                  label={{ value: 'Error (°C)', angle: -90, position: 'insideLeft', offset: 12, style: { fontSize: 10, fill: '#64748b' } }}
                />
                <YAxis
                  yAxisId="right"
                  orientation="right"
                  domain={[0, 1.0]}
                  tick={{ fontSize: 11 }}
                  label={{ value: 'Reliability Index R', angle: 90, position: 'insideRight', offset: 12, style: { fontSize: 10, fill: '#059669' } }}
                />
                <Tooltip
                  formatter={(value: any, name?: any) => {
                    if (String(name) === 'Reliability Index R') return [Number(value).toFixed(2), String(name)];
                    return [`${Number(value).toFixed(2)} °C`, String(name)];
                  }}
                  contentStyle={{ backgroundColor: 'rgba(15, 23, 42, 0.92)', borderRadius: '8px', border: 'none', color: '#fff', fontSize: '11px' }}
                />
                <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }} />
                <ReferenceArea x1="Day 3" x2="Day 10" yAxisId="left" fill="#f8fafc" fillOpacity={0.7} />
                <Line
                  yAxisId="left"
                  type="monotone"
                  dataKey="mae"
                  name="Mean Absolute Error (MAE)"
                  stroke="#2563eb"
                  strokeWidth={2.5}
                  dot={{ r: 4, fill: '#2563eb' }}
                  activeDot={{ r: 6 }}
                />
                <Line
                  yAxisId="left"
                  type="monotone"
                  dataKey="rmse"
                  name="Root Mean Square Error (RMSE)"
                  stroke="#dc2626"
                  strokeWidth={2}
                  strokeDasharray="4 4"
                  dot={{ r: 3, fill: '#dc2626' }}
                />
                <Line
                  yAxisId="right"
                  type="monotone"
                  dataKey="reliability"
                  name="Reliability Index R"
                  stroke="#059669"
                  strokeWidth={2}
                  dot={{ r: 3, fill: '#059669' }}
                />
              </ComposedChart>
            </ResponsiveContainer>
          </div>

          {/* Tabular Lead Day Breakdown */}
          <div className="overflow-x-auto border border-slate-200/80 rounded-xl">
            <table className="w-full text-xs text-left border-collapse min-w-[640px]">
              <thead className="bg-slate-50 font-semibold text-slate-700 border-b border-slate-200">
                <tr>
                  <th className="py-2.5 px-3">Horizon</th>
                  <th className="py-2.5 px-3">Verification Status</th>
                  <th className="py-2.5 px-3">Regional MAE</th>
                  <th className="py-2.5 px-3">Regional RMSE</th>
                  <th className="py-2.5 px-3">Signed Bias</th>
                  <th className="py-2.5 px-3">Empirical Reliability R</th>
                  <th className="py-2.5 px-3">Bust Probability</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {leadDayMetrics.map((m) => {
                  const isVerified = m.leadDay <= 2;
                  return (
                    <tr
                      key={m.leadDay}
                      className={m.leadDay === selectedLeadDay ? 'bg-indigo-50/50 font-semibold' : 'hover:bg-slate-50/70'}
                    >
                      <td className="py-2.5 px-3 font-mono">
                        Day {m.leadDay} ({m.leadDay * 24}h)
                      </td>
                      <td className="py-2.5 px-3">
                        {isVerified ? (
                          <Badge variant="emerald" size="xs" dot>Empirically Verified</Badge>
                        ) : (
                          <Badge variant="slate" size="xs">Extended Lookahead</Badge>
                        )}
                      </td>
                      <td className="py-2.5 px-3 font-mono text-sky-700">
                        {m.regionalMAE.toFixed(2)} °C
                      </td>
                      <td className="py-2.5 px-3 font-mono text-indigo-700">
                        {m.regionalRMSE.toFixed(2)} °C
                      </td>
                      <td className="py-2.5 px-3 font-mono text-amber-700">
                        +{m.regionalBias.toFixed(2)} °C
                      </td>
                      <td className="py-2.5 px-3 font-mono font-bold text-slate-900">
                        {m.regionalReliability.toFixed(2)}
                      </td>
                      <td className="py-2.5 px-3 font-mono font-bold text-rose-600">
                        {m.regionalBustProb}%
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </Card>

      {/* Mathematical Formulation R = R_error * C Explanation Box */}
      <Card
        title="Scientific Reliability Formulation (Week 4)"
        subtitle="Detailed mathematical definition separating empirical verification error from sample support"
        icon={<ShieldCheck className="w-5 h-5 text-indigo-600" />}
      >
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/80 space-y-2">
            <div className="font-bold text-slate-900 flex items-center justify-between">
              <span>1. Normalized Error</span>
              <span className="font-mono text-indigo-600 font-semibold">e_norm</span>
            </div>
            <div className="p-2 rounded bg-white border border-slate-200 font-mono text-[11px] text-center text-slate-800">
              e_norm = MAE / S_error
            </div>
            <p className="text-slate-600 text-[11px] leading-relaxed">
              Standardizes raw Mean Absolute Error by engineering tolerance scale <code className="bg-slate-200 px-1 py-0.5 rounded">S_error = 2.0 °C</code> for temperature.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/80 space-y-2">
            <div className="font-bold text-slate-900 flex items-center justify-between">
              <span>2. Error Component</span>
              <span className="font-mono text-indigo-600 font-semibold">R_error</span>
            </div>
            <div className="p-2 rounded bg-white border border-slate-200 font-mono text-[11px] text-center text-slate-800">
              R_error = exp(-e_norm)
            </div>
            <p className="text-slate-600 text-[11px] leading-relaxed">
              Decays smoothly from 1.0 (zero error) toward 0. Ensures bounded sensitivity without arbitrary step cutoffs.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/80 space-y-2">
            <div className="font-bold text-slate-900 flex items-center justify-between">
              <span>3. Sample Confidence</span>
              <span className="font-mono text-indigo-600 font-semibold">C factor</span>
            </div>
            <div className="p-2 rounded bg-white border border-slate-200 font-mono text-[11px] text-center text-slate-800">
              C = n / (n + k)
            </div>
            <p className="text-slate-600 text-[11px] leading-relaxed">
              Guards against small-sample bias where <code className="bg-slate-200 px-1 py-0.5 rounded">k = 10.0</code> and <code className="bg-slate-200 px-1 py-0.5 rounded">n</code> is the count of independent verified forecast cases.
            </p>
          </div>
        </div>

        <div className="mt-4 p-3 bg-amber-50/70 border border-amber-200/70 rounded-xl text-xs text-amber-900">
          <p className="leading-relaxed">
            <strong>Composite Index:</strong> <span className="font-mono font-bold">R = R_error × C</span> where <span className="font-mono">R ∈ [0, 1]</span>. Notice that R is explicitly an empirical performance index based on verification history, not a Bayesian calibrated posterior probability.
          </p>
        </div>
      </Card>
    </div>
  );
};
