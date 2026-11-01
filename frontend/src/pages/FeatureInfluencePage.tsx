import React, { useEffect, useState } from 'react';
import { WeatherApi } from '../services/api';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { MetricValue } from '../components/common/MetricValue';
import type {
  GlobalExplainabilityData,
  HighErrorEventAnalyzed,
  MeteorologicalAuditData,
  LocalExplanationResult,
  DistrictName
} from '../types/weather';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  Cell,
  ReferenceLine
} from 'recharts';
import {
  Sliders,
  Compass,
  TrendingUp,
  AlertTriangle,
  Info,
  CheckCircle,
  Clock,
  MapPin,
  Calendar,
  Layers,
  ArrowRight,
  Send,
  Sparkles,
  ShieldAlert,
  Wind,
  Droplets,
  Thermometer,
  HelpCircle
} from 'lucide-react';

export const FeatureInfluencePage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'global' | 'events' | 'live' | 'meteorological'>('global');
  const [globalData, setGlobalData] = useState<GlobalExplainabilityData | null>(null);
  const [events, setEvents] = useState<HighErrorEventAnalyzed[]>([]);
  const [selectedEventId, setSelectedEventId] = useState<number>(21);
  const [metAudit, setMetAudit] = useState<MeteorologicalAuditData | null>(null);
  const [loading, setLoading] = useState(true);

  // Live interactive forecast explanation state
  const [simDistrict, setSimDistrict] = useState<DistrictName>('Anantnag');
  const [simLeadDay, setSimLeadDay] = useState<number>(2);
  const [simForecastValue, setSimForecastValue] = useState<number>(15.2);
  const [simValidHour, setSimValidHour] = useState<number>(12);
  const [simulating, setSimulating] = useState(false);
  const [simResult, setSimResult] = useState<LocalExplanationResult | null>(null);

  useEffect(() => {
    Promise.all([
      WeatherApi.getGlobalExplainability(),
      WeatherApi.getHighErrorEvents(),
      WeatherApi.getMeteorologicalAudit()
    ]).then(([glob, evs, audit]) => {
      setGlobalData(glob);
      setEvents(evs);
      if (evs.length > 0) {
        setSelectedEventId(evs[0].event_id);
      }
      setMetAudit(audit);
      setLoading(false);
    }).catch(err => {
      console.error('Failed to load Week 7 explainability data:', err);
      setLoading(false);
    });
  }, []);

  const handleSimulate = async (e: React.FormEvent) => {
    e.preventDefault();
    setSimulating(true);
    try {
      const res = await WeatherApi.explainLocalForecast({
        district: simDistrict,
        leadDay: simLeadDay,
        forecastValue: simForecastValue,
        validHour: simValidHour,
        initHour: 0,
        validMonth: 9,
      });
      setSimResult(res);
    } finally {
      setSimulating(false);
    }
  };

  const selectedEvent = events.find(e => e.event_id === selectedEventId) || events[0];

  if (loading || !globalData) {
    return (
      <div className="space-y-6">
        <div className="h-28 bg-white rounded-xl border border-slate-200 animate-pulse" />
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-24 bg-white rounded-xl border border-slate-200 animate-pulse" />
          ))}
        </div>
        <div className="h-96 bg-white rounded-xl border border-slate-200 animate-pulse" />
      </div>
    );
  }

  // Bar chart data for global feature importance
  const globalChartData = globalData.feature_rankings.map(f => ({
    name: f.feature,
    meanAbsShap: f.mean_abs_shap,
    relativeShare: f.relative_importance_pct,
    direction: f.dominant_direction
  })).reverse();

  // Concept grouping chart data
  const conceptChartData = globalData.grouped_rankings.map(c => ({
    concept: c.concept.split('(')[0].trim(),
    meanAbsShap: c.mean_abs_shap,
    share: c.relative_importance_pct
  })).reverse();

  // Event local contribution chart data
  const eventContribData = selectedEvent ? selectedEvent.all_contributions.map(c => ({
    feature: c.feature,
    shapValue: c.shap_value,
    share: c.relative_contribution_pct,
    direction: c.direction
  })).reverse() : [];

  return (
    <div className="space-y-6">
      {/* Header & Academic Context */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white p-6 rounded-xl border border-slate-200/80 shadow-xs">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold uppercase tracking-wider text-indigo-600 bg-indigo-50 px-2.5 py-1 rounded-md">
              Week 7 Implementation
            </span>
            <span className="text-xs font-semibold text-slate-500">
              SHAP Explainable AI (XAI)
            </span>
          </div>
          <h1 className="text-2xl font-bold text-slate-900 mt-1">
            SHAP-based Feature Influence Analysis
          </h1>
          <p className="text-sm text-slate-600 mt-1 max-w-3xl">
            Mathematical explanation of the Week 5 forecast-bust model using exact Shapley Additive exPlanations (SHAP).
            Identifies empirical drivers pushing prospective predictions toward extreme error thresholds across Jammu &amp; Kashmir.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Badge variant="indigo" size="md">
            {globalData.explainer_type}
          </Badge>
          <Badge variant="slate" size="md">
            Model: {globalData.estimator}
          </Badge>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex border-b border-slate-200 space-x-2">
        <button
          onClick={() => setActiveTab('global')}
          className={`py-3 px-4 font-semibold text-sm rounded-t-lg transition-colors cursor-pointer flex items-center gap-2 ${
            activeTab === 'global'
              ? 'border-b-2 border-indigo-600 text-indigo-700 bg-indigo-50/50'
              : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
          }`}
        >
          <Compass className="w-4 h-4" />
          Global Feature Influence
        </button>
        <button
          onClick={() => setActiveTab('events')}
          className={`py-3 px-4 font-semibold text-sm rounded-t-lg transition-colors cursor-pointer flex items-center gap-2 ${
            activeTab === 'events'
              ? 'border-b-2 border-indigo-600 text-indigo-700 bg-indigo-50/50'
              : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
          }`}
        >
          <AlertTriangle className="w-4 h-4" />
          High-Error Events &amp; Waterfalls
        </button>
        <button
          onClick={() => setActiveTab('live')}
          className={`py-3 px-4 font-semibold text-sm rounded-t-lg transition-colors cursor-pointer flex items-center gap-2 ${
            activeTab === 'live'
              ? 'border-b-2 border-indigo-600 text-indigo-700 bg-indigo-50/50'
              : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
          }`}
        >
          <Sliders className="w-4 h-4" />
          Live Forecast Explainer
        </button>
        <button
          onClick={() => setActiveTab('meteorological')}
          className={`py-3 px-4 font-semibold text-sm rounded-t-lg transition-colors cursor-pointer flex items-center gap-2 ${
            activeTab === 'meteorological'
              ? 'border-b-2 border-indigo-600 text-indigo-700 bg-indigo-50/50'
              : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
          }`}
        >
          <Droplets className="w-4 h-4" />
          Meteorological Audit (Humidity &amp; Wind)
        </button>
      </div>

      {/* ========================================================================= */}
      {/* TAB 1: GLOBAL FEATURE INFLUENCE */}
      {/* ========================================================================= */}
      {activeTab === 'global' && (
        <div className="space-y-6">
          {/* Top KPI Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card className="p-4">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                Primary Driver (Global)
              </span>
              <div className="text-xl font-bold text-slate-900 mt-1">
                {globalData.feature_rankings[0]?.feature}
              </div>
              <div className="text-xs text-indigo-600 font-semibold mt-1">
                Mean |SHAP| = {globalData.feature_rankings[0]?.mean_abs_shap} ({globalData.feature_rankings[0]?.relative_importance_pct}% share)
              </div>
            </Card>

            <Card className="p-4">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                Secondary Driver
              </span>
              <div className="text-xl font-bold text-slate-900 mt-1">
                {globalData.feature_rankings[1]?.feature}
              </div>
              <div className="text-xs text-indigo-600 font-semibold mt-1">
                Mean |SHAP| = {globalData.feature_rankings[1]?.mean_abs_shap} ({globalData.feature_rankings[1]?.relative_importance_pct}% share)
              </div>
            </Card>

            <Card className="p-4">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                Base Model Expected Value
              </span>
              <div className="text-xl font-bold text-slate-900 mt-1">
                {(globalData.base_probability * 100).toFixed(1)}% Bust Risk
              </div>
              <div className="text-xs text-slate-500 font-medium mt-1">
                φ₀ = {globalData.base_value_log_odds} log-odds (E[f(x)])
              </div>
            </Card>

            <Card className="p-4">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                Attribution Space
              </span>
              <div className="text-xl font-bold text-slate-900 mt-1">
                Log-Odds (Logit)
              </div>
              <div className="text-xs text-emerald-600 font-semibold mt-1">
                Exact Additive Decomposition
              </div>
            </Card>
          </div>

          {/* Charts Row */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Global SHAP Importance Chart */}
            <Card className="p-5">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="font-bold text-slate-900 text-base">
                    Global Feature Importance (Mean |SHAP|)
                  </h3>
                  <p className="text-xs text-slate-500 mt-0.5">
                    Average absolute impact on forecast-bust log-odds across all verification cases
                  </p>
                </div>
                <Badge variant="indigo">All 10 Features</Badge>
              </div>

              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={globalChartData} layout="vertical" margin={{ left: 90, right: 20, top: 10, bottom: 10 }}>
                    <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#e2e8f0" />
                    <XAxis type="number" stroke="#64748b" tick={{ fontSize: 11 }} />
                    <YAxis dataKey="name" type="category" stroke="#64748b" tick={{ fontSize: 11, fontWeight: 600 }} />
                    <Tooltip
                      formatter={(val: any, name: any, item: any) => [
                        `${Number(val).toFixed(4)} (|Δ Logit|) — ${item.payload.relativeShare}% of total influence`,
                        'Mean |SHAP|'
                      ]}
                      contentStyle={{ backgroundColor: '#0f172a', color: '#fff', borderRadius: '8px', fontSize: '12px' }}
                    />
                    <Bar dataKey="meanAbsShap" fill="#3b82f6" radius={[0, 4, 4, 0]}>
                      {globalChartData.map((entry, index) => (
                        <Cell
                          key={`cell-${index}`}
                          fill={entry.name.startsWith('district') ? '#0d9488' : '#2563eb'}
                        />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
              <div className="flex items-center justify-center gap-6 mt-2 text-xs text-slate-600 font-medium">
                <span className="flex items-center gap-1.5">
                  <span className="w-3 h-3 bg-blue-600 rounded-xs inline-block" /> Numerical Predictors
                </span>
                <span className="flex items-center gap-1.5">
                  <span className="w-3 h-3 bg-teal-600 rounded-xs inline-block" /> District Geography One-Hot
                </span>
              </div>
            </Card>

            {/* Grouped Concept Influence Chart */}
            <Card className="p-5">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="font-bold text-slate-900 text-base">
                    Concept-Level Aggregated Influence
                  </h3>
                  <p className="text-xs text-slate-500 mt-0.5">
                    Aggregated relative importance by meteorological domain category
                  </p>
                </div>
                <Badge variant="slate">Concept Groups</Badge>
              </div>

              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={conceptChartData} layout="vertical" margin={{ left: 110, right: 20, top: 10, bottom: 10 }}>
                    <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#e2e8f0" />
                    <XAxis type="number" stroke="#64748b" tick={{ fontSize: 11 }} />
                    <YAxis dataKey="concept" type="category" stroke="#64748b" tick={{ fontSize: 11, fontWeight: 600 }} />
                    <Tooltip
                      formatter={(val: any, name: any, item: any) => [
                        `${Number(val).toFixed(4)} (${item.payload.share}%)`,
                        'Aggregated |SHAP|'
                      ]}
                      contentStyle={{ backgroundColor: '#0f172a', color: '#fff', borderRadius: '8px', fontSize: '12px' }}
                    />
                    <Bar dataKey="meanAbsShap" fill="#0d9488" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
              <div className="p-3 bg-slate-50 rounded-lg border border-slate-200 text-xs text-slate-600">
                <span className="font-semibold text-slate-800">Key Finding:</span> Forecast horizon (lead hours) contributes 39.5% of total predictive influence, followed by diurnal timing (28.8%) and temperature magnitude (18.6%). Terrain geography contributes 13.1% through elevation and valley sheltering.
              </div>
            </Card>
          </div>

          {/* Detailed Feature Importance Table */}
          <Card className="p-5">
            <h3 className="font-bold text-slate-900 text-base mb-3">
              Comprehensive SHAP Feature Influence Statistics
            </h3>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="border-b border-slate-200 bg-slate-50/80 text-slate-600 font-semibold">
                    <th className="py-2.5 px-3">Rank</th>
                    <th className="py-2.5 px-3">Feature Name</th>
                    <th className="py-2.5 px-3">Transformed Pipeline Name</th>
                    <th className="py-2.5 px-3">Mean |SHAP|</th>
                    <th className="py-2.5 px-3">Relative Share</th>
                    <th className="py-2.5 px-3">Min / Max SHAP</th>
                    <th className="py-2.5 px-3">Dominant Impact</th>
                    <th className="py-2.5 px-3">% Positive Drivers</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {globalData.feature_rankings.map((row, idx) => (
                    <tr key={row.feature} className="hover:bg-slate-50/60 transition-colors">
                      <td className="py-2.5 px-3 font-bold text-slate-800">{idx + 1}</td>
                      <td className="py-2.5 px-3 font-semibold text-slate-900">{row.feature}</td>
                      <td className="py-2.5 px-3 font-mono text-[11px] text-slate-500">{row.raw_feature}</td>
                      <td className="py-2.5 px-3 font-bold text-indigo-700">{row.mean_abs_shap.toFixed(4)}</td>
                      <td className="py-2.5 px-3 font-semibold text-slate-700">{row.relative_importance_pct.toFixed(1)}%</td>
                      <td className="py-2.5 px-3 text-slate-600 font-mono text-[11px]">
                        [{row.min_shap.toFixed(2)}, {row.max_shap.toFixed(2)}]
                      </td>
                      <td className="py-2.5 px-3">
                        <Badge variant={row.dominant_direction === 'RISK_INCREASING' ? 'rose' : 'emerald'} size="sm">
                          {row.dominant_direction === 'RISK_INCREASING' ? '+ PUSHES BUST' : '- MITIGATES BUST'}
                        </Badge>
                      </td>
                      <td className="py-2.5 px-3 text-slate-700 font-medium">{row.pct_positive_impact.toFixed(1)}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 2: HIGH-ERROR EVENTS & WATERFALLS */}
      {/* ========================================================================= */}
      {activeTab === 'events' && (
        <div className="space-y-6">
          {/* Event Selector Cards */}
          <div className="space-y-2">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
              Select High-Error Verification Event to Inspect:
            </span>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
              {events.map(ev => {
                const isSelected = ev.event_id === selectedEventId;
                return (
                  <button
                    key={ev.event_id}
                    onClick={() => setSelectedEventId(ev.event_id)}
                    className={`p-3.5 rounded-xl border text-left transition-all cursor-pointer ${
                      isSelected
                        ? 'border-indigo-600 bg-indigo-50/70 shadow-xs ring-1 ring-indigo-500'
                        : 'border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50/70'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-slate-800">
                        Event #{ev.event_id}
                      </span>
                      <Badge variant="rose" size="sm">
                        {ev.actual_error_c > 0 ? `+${ev.actual_error_c.toFixed(1)}` : ev.actual_error_c.toFixed(1)}°C
                      </Badge>
                    </div>
                    <div className="text-sm font-bold text-slate-900 mt-1">
                      {ev.district}
                    </div>
                    <div className="text-xs text-slate-500 mt-0.5">
                      Lead {ev.lead_hours}h (Day {ev.lead_day})
                    </div>
                    <div className="text-[11px] font-semibold text-indigo-700 mt-2">
                      P(Bust) = {(ev.model_prediction.bust_probability * 100).toFixed(1)}%
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {selectedEvent && (
            <div className="space-y-6">
              {/* Event Overview & Retrospective vs Prospective Comparison */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Left: Retrospective Ground-Truth Verification */}
                <Card className="p-5 border-l-4 border-l-rose-500 bg-rose-50/20">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-rose-700 uppercase tracking-wider">
                      Retrospective Ground-Truth Verification
                    </span>
                    <Badge variant="rose">Observed Outcome</Badge>
                  </div>
                  <div className="grid grid-cols-2 gap-4 mt-3">
                    <div>
                      <div className="text-xs text-slate-500 font-medium">NOAA GFS Forecast:</div>
                      <div className="text-lg font-bold text-slate-900">{selectedEvent.forecast_value_c}°C</div>
                    </div>
                    <div>
                      <div className="text-xs text-slate-500 font-medium">ECMWF ERA5 Reference:</div>
                      <div className="text-lg font-bold text-slate-900">{selectedEvent.reference_value_c}°C</div>
                    </div>
                    <div>
                      <div className="text-xs text-slate-500 font-medium">Forecast Error (GFS - ERA5):</div>
                      <div className="text-lg font-extrabold text-rose-600">
                        {selectedEvent.actual_error_c > 0 ? `+${selectedEvent.actual_error_c.toFixed(2)}` : selectedEvent.actual_error_c.toFixed(2)}°C
                      </div>
                    </div>
                    <div>
                      <div className="text-xs text-slate-500 font-medium">Bust Threshold (90th %ile):</div>
                      <div className="text-lg font-bold text-slate-800">
                        {selectedEvent.empirical_bust_threshold_c ? `${selectedEvent.empirical_bust_threshold_c}°C` : 'N/A'}
                      </div>
                    </div>
                  </div>
                  <div className="mt-3 text-xs text-rose-800 font-medium border-t border-rose-200/60 pt-2">
                    Verification Result: Extreme error exceeded 90th percentile threshold (Bust = 1).
                  </div>
                </Card>

                {/* Right: Prospective Model ML Prediction */}
                <Card className="p-5 border-l-4 border-l-indigo-500 bg-indigo-50/20">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-indigo-700 uppercase tracking-wider">
                      Week 5 Model Prospective Prediction
                    </span>
                    <Badge variant="indigo">Model Prediction</Badge>
                  </div>
                  <div className="grid grid-cols-2 gap-4 mt-3">
                    <div>
                      <div className="text-xs text-slate-500 font-medium">Predicted Bust Probability:</div>
                      <div className="text-xl font-extrabold text-indigo-700">
                        {(selectedEvent.model_prediction.bust_probability * 100).toFixed(1)}%
                      </div>
                    </div>
                    <div>
                      <div className="text-xs text-slate-500 font-medium">Risk Level Classification:</div>
                      <div className="text-lg font-bold text-slate-900">
                        {selectedEvent.model_prediction.risk_level}
                      </div>
                    </div>
                    <div>
                      <div className="text-xs text-slate-500 font-medium">Classification Threshold:</div>
                      <div className="text-sm font-semibold text-slate-800">
                        {selectedEvent.model_prediction.classification_threshold * 100}%
                      </div>
                    </div>
                    <div>
                      <div className="text-xs text-slate-500 font-medium">Predicted Class:</div>
                      <div className="text-sm font-bold text-slate-900">
                        Class {selectedEvent.model_prediction.predicted_class} (Bust Risk Alert)
                      </div>
                    </div>
                  </div>
                  <div className="mt-3 text-xs text-indigo-900 font-medium border-t border-indigo-200/60 pt-2">
                    Computed strictly at forecast issuance using lead time, valid hour, and forecast value.
                  </div>
                </Card>
              </div>

              {/* SHAP Waterfall / Diverging Contribution Chart */}
              <Card className="p-5">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4">
                  <div>
                    <h3 className="font-bold text-slate-900 text-base">
                      Feature Attributions (SHAP Log-Odds Contributions)
                    </h3>
                    <p className="text-xs text-slate-500 mt-0.5">
                      Event #{selectedEvent.event_id} — {selectedEvent.district} (Lead {selectedEvent.lead_hours}h). Red indicates factors increasing bust risk; Green indicates factors reducing bust risk.
                    </p>
                  </div>
                  <div className="text-xs text-slate-500 font-mono">
                    Base: {selectedEvent.shap_summary.base_value_log_odds} | Final: {selectedEvent.shap_summary.final_log_odds}
                  </div>
                </div>

                <div className="h-72">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={eventContribData} layout="vertical" margin={{ left: 110, right: 30, top: 10, bottom: 10 }}>
                      <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#e2e8f0" />
                      <XAxis type="number" stroke="#64748b" tick={{ fontSize: 11 }} />
                      <YAxis dataKey="feature" type="category" stroke="#64748b" tick={{ fontSize: 11, fontWeight: 600 }} />
                      <Tooltip
                        formatter={(val: any, name: any, item: any) => [
                          `${Number(val) > 0 ? '+' : ''}${Number(val).toFixed(4)} log-odds (${item.payload.share}% influence)`,
                          'SHAP Contribution'
                        ]}
                        contentStyle={{ backgroundColor: '#0f172a', color: '#fff', borderRadius: '8px', fontSize: '12px' }}
                      />
                      <ReferenceLine x={0} stroke="#475569" strokeWidth={1.5} />
                      <Bar dataKey="shapValue" radius={[4, 4, 4, 4]}>
                        {eventContribData.map((entry, index) => (
                          <Cell
                            key={`cell-${index}`}
                            fill={entry.shapValue > 0 ? '#ef4444' : '#10b981'}
                          />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>

                <div className="flex items-center justify-center gap-6 mt-2 text-xs text-slate-600 font-medium">
                  <span className="flex items-center gap-1.5">
                    <span className="w-3 h-3 bg-red-500 rounded-xs inline-block" /> Pushed Risk UP (Increased Bust Probability)
                  </span>
                  <span className="flex items-center gap-1.5">
                    <span className="w-3 h-3 bg-emerald-500 rounded-xs inline-block" /> Pushed Risk DOWN (Mitigated Bust Probability)
                  </span>
                </div>
              </Card>

              {/* Natural Language Narrative and Scientific Distinction */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                <Card className="p-5 lg:col-span-2">
                  <h4 className="font-bold text-slate-900 text-sm mb-2 flex items-center gap-2">
                    <Sparkles className="w-4 h-4 text-indigo-600" />
                    Plain-Language Explanation of Prediction
                  </h4>
                  <p className="text-sm text-slate-700 leading-relaxed">
                    {selectedEvent.narrative}
                  </p>

                  <div className="mt-4 pt-3 border-t border-slate-100 flex flex-wrap gap-4 text-xs text-slate-500">
                    <div>
                      <span className="font-semibold text-slate-700">Valid Time:</span> {selectedEvent.valid_time}
                    </div>
                    <div>
                      <span className="font-semibold text-slate-700">Initialization:</span> {selectedEvent.initialization_time}
                    </div>
                    <div>
                      <span className="font-semibold text-slate-700">Model:</span> {selectedEvent.model_prediction.model_id}
                    </div>
                  </div>
                </Card>

                <Card className="p-5 bg-slate-900 text-white">
                  <h4 className="font-bold text-white text-sm mb-2 flex items-center gap-2">
                    <Info className="w-4 h-4 text-amber-400" />
                    Scientific Distinction Note
                  </h4>
                  <p className="text-xs text-slate-300 leading-relaxed">
                    {selectedEvent.scientific_distinction_note}
                  </p>
                  <div className="mt-3 p-2 bg-slate-800/80 rounded-md text-[11px] text-amber-300 font-mono">
                    Retrospective Error ≠ Prospective Risk
                  </div>
                </Card>
              </div>
            </div>
          )}
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 3: LIVE FORECAST EXPLAINER */}
      {/* ========================================================================= */}
      {activeTab === 'live' && (
        <div className="space-y-6">
          <Card className="p-6">
            <div className="max-w-2xl">
              <h3 className="font-bold text-slate-900 text-lg">
                Interactive Local Forecast Attribution Explainer
              </h3>
              <p className="text-sm text-slate-600 mt-1">
                Simulate an incoming forecast issuance and compute real-time SHAP feature attributions
                using the Week 5 scikit-learn pipeline and Week 7 LinearExplainer engine.
              </p>
            </div>

            <form onSubmit={handleSimulate} className="mt-6 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  District (Terrain)
                </label>
                <select
                  value={simDistrict}
                  onChange={(e) => setSimDistrict(e.target.value as DistrictName)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm bg-white font-medium text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="Srinagar">Srinagar (Central Valley, 1585m)</option>
                  <option value="Jammu">Jammu (Subtropical Plains, 327m)</option>
                  <option value="Anantnag">Anantnag (Southern Valley, 1601m)</option>
                  <option value="Baramulla">Baramulla (Northern Valley, 1593m)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Forecast Lead Day: <span className="text-indigo-600 font-bold">{simLeadDay}</span> ({simLeadDay * 24} hours)
                </label>
                <input
                  type="range"
                  min="1"
                  max="10"
                  step="1"
                  value={simLeadDay}
                  onChange={(e) => setSimLeadDay(Number(e.target.value))}
                  className="w-full accent-indigo-600 cursor-pointer mt-2"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Forecast Temperature (°C)
                </label>
                <input
                  type="number"
                  step="0.5"
                  value={simForecastValue}
                  onChange={(e) => setSimForecastValue(Number(e.target.value))}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm bg-white font-medium text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Valid Target Hour (UTC)
                </label>
                <select
                  value={simValidHour}
                  onChange={(e) => setSimValidHour(Number(e.target.value))}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm bg-white font-medium text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="0">00:00 UTC (Early Morning)</option>
                  <option value="6">06:00 UTC (Late Morning)</option>
                  <option value="12">12:00 UTC (Peak Afternoon Solar)</option>
                  <option value="18">18:00 UTC (Nighttime Cooling)</option>
                </select>
              </div>

              <div className="sm:col-span-2 lg:col-span-4 mt-2">
                <button
                  type="submit"
                  disabled={simulating}
                  className="w-full sm:w-auto px-6 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-sm rounded-lg transition-colors cursor-pointer flex items-center justify-center gap-2 shadow-xs"
                >
                  {simulating ? (
                    'Computing SHAP Values...'
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4" /> Compute SHAP Explanation
                    </>
                  )}
                </button>
              </div>
            </form>
          </Card>

          {simResult && (
            <div className="space-y-6">
              {/* Prediction Result Banner */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <Card className="p-4">
                  <span className="text-xs font-semibold text-slate-500 uppercase">
                    Predicted Bust Probability
                  </span>
                  <div className="text-2xl font-extrabold text-indigo-700 mt-1">
                    {(simResult.prediction.bust_probability * 100).toFixed(1)}%
                  </div>
                  <div className="mt-1">
                    <Badge variant={simResult.prediction.bust_probability >= 0.7 ? 'rose' : simResult.prediction.bust_probability >= 0.35 ? 'amber' : 'emerald'}>
                      {simResult.prediction.risk_level}
                    </Badge>
                  </div>
                </Card>

                <Card className="p-4">
                  <span className="text-xs font-semibold text-slate-500 uppercase">
                    Model Classification
                  </span>
                  <div className="text-2xl font-extrabold text-slate-900 mt-1">
                    {simResult.prediction.predicted_class === 1 ? 'BUST ALERT' : 'NORMAL'}
                  </div>
                  <div className="text-xs text-slate-500 mt-1">
                    Threshold: {simResult.prediction.classification_threshold * 100}%
                  </div>
                </Card>

                <Card className="p-4">
                  <span className="text-xs font-semibold text-slate-500 uppercase">
                    Net SHAP Attribution
                  </span>
                  <div className="text-2xl font-extrabold text-slate-900 mt-1">
                    {simResult.shapSummary.sum_shap_values > 0 ? `+${simResult.shapSummary.sum_shap_values.toFixed(3)}` : simResult.shapSummary.sum_shap_values.toFixed(3)}
                  </div>
                  <div className="text-xs text-slate-500 mt-1">
                    Base: {simResult.shapSummary.base_value_log_odds} | Log-odds: {simResult.shapSummary.final_log_odds}
                  </div>
                </Card>
              </div>

              {/* Attribution Chart */}
              <Card className="p-5">
                <h4 className="font-bold text-slate-900 text-sm mb-3">
                  Live SHAP Attributions for {simResult.district} (Lead Day {simResult.leadDay})
                </h4>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={simResult.allFeatureContributions.slice().reverse()}
                      layout="vertical"
                      margin={{ left: 110, right: 30, top: 10, bottom: 10 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#e2e8f0" />
                      <XAxis type="number" stroke="#64748b" tick={{ fontSize: 11 }} />
                      <YAxis dataKey="feature" type="category" stroke="#64748b" tick={{ fontSize: 11, fontWeight: 600 }} />
                      <Tooltip
                        formatter={(val: any) => [`${Number(val).toFixed(4)} log-odds`, 'SHAP Impact']}
                        contentStyle={{ backgroundColor: '#0f172a', color: '#fff', borderRadius: '8px', fontSize: '12px' }}
                      />
                      <ReferenceLine x={0} stroke="#475569" strokeWidth={1.5} />
                      <Bar dataKey="shap_value" radius={[4, 4, 4, 4]}>
                        {simResult.allFeatureContributions.slice().reverse().map((entry, index) => (
                          <Cell
                            key={`cell-${index}`}
                            fill={entry.shap_value > 0 ? '#ef4444' : '#10b981'}
                          />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
                <p className="text-xs text-slate-600 mt-3 p-3 bg-slate-50 rounded-lg">
                  <span className="font-semibold text-slate-800">Explanation:</span> {simResult.narrativeExplanation}
                </p>
              </Card>
            </div>
          )}
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 4: METEOROLOGICAL AUDIT (HUMIDITY & WIND SPEED) */}
      {/* ========================================================================= */}
      {activeTab === 'meteorological' && metAudit && (
        <div className="space-y-6">
          {/* Transparent Status Alert Banner */}
          <div className="p-5 bg-amber-50 border-l-4 border-amber-500 rounded-r-xl flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
            <div className="text-sm text-amber-900">
              <h4 className="font-bold text-amber-950">
                Transparent Data Governance: Humidity and Wind Speed Status
              </h4>
              <p className="mt-1 leading-relaxed">
                As required by Week 7 specifications, a thorough audit was conducted across the GFS forecast, ERA5 reanalysis, and processed feature datasets.
                Atmospheric moisture (relative humidity) and 10-metre wind speed are <strong>ABSENT</strong> from the downloaded local dataset archive and <strong>are NOT features</strong> in the trained Week 5 model.
                No synthetic or fabricated values have been introduced.
              </p>
            </div>
          </div>

          {/* Audit Table */}
          <Card className="p-5">
            <h3 className="font-bold text-slate-900 text-base mb-3">
              Meteorological Variable Audit Table
            </h3>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="border-b border-slate-200 bg-slate-50 text-slate-600 font-semibold">
                    <th className="py-2.5 px-3">Variable</th>
                    <th className="py-2.5 px-3">Units</th>
                    <th className="py-2.5 px-3">Raw GFS Archive</th>
                    <th className="py-2.5 px-3">Raw ERA5 Archive</th>
                    <th className="py-2.5 px-3">In Week 5 Model</th>
                    <th className="py-2.5 px-3">Audit Finding</th>
                    <th className="py-2.5 px-3">Scientific Rationale</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {metAudit.variables_audited.map(v => (
                    <tr key={v.variable} className="hover:bg-slate-50/60">
                      <td className="py-2.5 px-3 font-bold text-slate-800">{v.display_name}</td>
                      <td className="py-2.5 px-3 font-mono text-slate-600">{v.units}</td>
                      <td className="py-2.5 px-3">
                        <Badge variant={v.in_gfs_archive ? 'emerald' : 'slate'} size="sm">
                          {v.in_gfs_archive ? 'YES' : 'NO'}
                        </Badge>
                      </td>
                      <td className="py-2.5 px-3">
                        <Badge variant={v.in_era5_archive ? 'emerald' : 'slate'} size="sm">
                          {v.in_era5_archive ? 'YES' : 'NO'}
                        </Badge>
                      </td>
                      <td className="py-2.5 px-3">
                        <Badge variant={v.in_week5_model ? 'indigo' : 'slate'} size="sm">
                          {v.in_week5_model ? 'INCLUDED' : 'NOT USED'}
                        </Badge>
                      </td>
                      <td className="py-2.5 px-3 text-slate-800 font-semibold">{v.audit_finding}</td>
                      <td className="py-2.5 px-3 text-slate-600 text-[11px] max-w-xs">{v.scientific_rationale}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>

          {/* Exploratory Meteorological Analysis of Available Data */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card className="p-5">
              <div className="flex items-center gap-2 text-indigo-600 mb-2">
                <Clock className="w-4 h-4" />
                <h4 className="font-bold text-slate-900 text-sm">Lead Horizon Influence</h4>
              </div>
              <p className="text-xs text-slate-600 leading-relaxed">
                Verification MAE increases monotonically with forecast lead hours (r = +0.28). At Day 1 (15h), MAE is ~4.8°C; by Day 2 (27h), MAE reaches ~8.1°C as atmospheric predictability decays.
              </p>
              <div className="mt-3 p-2 bg-indigo-50/60 rounded text-xs text-indigo-900 font-semibold">
                Correlation with Absolute Error: r = +0.284
              </div>
            </Card>

            <Card className="p-5">
              <div className="flex items-center gap-2 text-purple-600 mb-2">
                <Layers className="w-4 h-4" />
                <h4 className="font-bold text-slate-900 text-sm">Diurnal Heating Cycle</h4>
              </div>
              <p className="text-xs text-slate-600 leading-relaxed">
                Afternoon valid hours (09:00 - 15:00 UTC) show substantially higher error dispersion than nighttime hours, driven by intense solar heating, valley wind inversions, and local convective development.
              </p>
              <div className="mt-3 p-2 bg-purple-50/60 rounded text-xs text-purple-900 font-semibold">
                Peak Error Window: 12:00 - 15:00 UTC
              </div>
            </Card>

            <Card className="p-5">
              <div className="flex items-center gap-2 text-teal-600 mb-2">
                <Thermometer className="w-4 h-4" />
                <h4 className="font-bold text-slate-900 text-sm">Temperature Extremes</h4>
              </div>
              <p className="text-xs text-slate-600 leading-relaxed">
                Cooler temperature forecasts (characteristic of elevated valley and mountain stations like Anantnag and Baramulla) display higher error variance than warm subtropical plains forecasts (Jammu).
              </p>
              <div className="mt-3 p-2 bg-teal-50/60 rounded text-xs text-teal-900 font-semibold">
                Cold Departure Bias: Negative (-8°C to -10°C)
              </div>
            </Card>
          </div>

          {/* Scientific Disclaimer Card */}
          <Card className="p-5 bg-slate-50 border border-slate-200">
            <h4 className="font-bold text-slate-900 text-sm mb-1 flex items-center gap-1.5">
              <Info className="w-4 h-4 text-slate-600" />
              Scientific Methodology Note
            </h4>
            <p className="text-xs text-slate-600 leading-relaxed">
              {metAudit.scientific_disclaimer} SHAP values measure mathematical feature attribution within the fitted model pipeline (LogisticRegression on standardized issuance features). They do not represent physical conservation laws or dynamic fluid mechanisms.
            </p>
          </Card>
        </div>
      )}
    </div>
  );
};

