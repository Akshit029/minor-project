import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { WeatherApi, DistrictAnalysisApiResponse } from '../services/api';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { MetricValue } from '../components/common/MetricValue';
import { ForecastVsReferenceChart } from '../components/charts/ForecastVsReferenceChart';
import { ScientificDisclaimer } from '../components/common/ScientificDisclaimer';
import type { DistrictName } from '../types/weather';
import { APP_CONFIG } from '../data/config';
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
import { 
  MapPin, 
  Mountain, 
  Thermometer, 
  CloudRain, 
  Wind, 
  Compass, 
  Activity, 
  AlertTriangle,
  Layers
} from 'lucide-react';

export const DistrictAnalysisPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const districtParam = searchParams.get('district') as DistrictName | null;

  const [selectedDistrictName, setSelectedDistrictName] = useState<DistrictName>(
    (districtParam && APP_CONFIG.studyDistricts.includes(districtParam)) ? districtParam : 'Srinagar'
  );

  const [data, setData] = useState<DistrictAnalysisApiResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    WeatherApi.getDistrict(selectedDistrictName).then((res) => {
      setData(res);
      setLoading(false);
    });
  }, [selectedDistrictName]);

  const handleDistrictChange = (name: DistrictName) => {
    setSelectedDistrictName(name);
    setSearchParams({ district: name });
  };

  if (loading || !data) {
    return (
      <div className="space-y-6">
        <div className="h-24 bg-white rounded-xl border border-slate-200 animate-pulse" />
        <div className="grid grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="h-28 bg-white rounded-xl border border-slate-200 animate-pulse" />
          ))}
        </div>
      </div>
    );
  }

  const { district, leadDayMetrics, forecastVsReference } = data;

  const chartErrorData = leadDayMetrics.map((item) => ({
    leadLabel: `Day ${item.leadDay}`,
    MAE: item.mae,
    RMSE: item.rmse,
    Bias: item.bias,
    Reliability: item.reliability,
  }));

  return (
    <div className="space-y-6 font-sans">
      {/* Header and District Selector Dropdown */}
      <div className="bg-white rounded-xl border border-slate-200/90 shadow-2xs p-4 sm:p-6 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex flex-wrap items-center gap-1.5 sm:gap-2 mb-1.5">
              <Badge variant="blue" size="xs">
                Microclimatic District Analysis
              </Badge>
              <Badge variant="slate" size="xs">
                Elevation: {district.elevationMeters}m
              </Badge>
            </div>
            <h1 className="text-lg sm:text-2xl font-bold text-slate-900 tracking-tight">
              {district.name} In-Depth Verification
            </h1>
            <p className="text-xs sm:text-sm text-slate-500 mt-1 max-w-2xl leading-relaxed">
              {district.terrainDescription}
            </p>
          </div>

          {/* Interactive District Dropdown Selector */}
          <div className="flex items-center gap-2 self-start sm:self-auto">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              District:
            </span>
            <select
              value={selectedDistrictName}
              onChange={(e) => handleDistrictChange(e.target.value as DistrictName)}
              className="bg-white border border-slate-300 text-slate-900 text-xs font-semibold rounded-lg px-3 py-2 shadow-2xs focus:ring-2 focus:ring-slate-900 focus:border-slate-900 transition-all cursor-pointer"
            >
              {APP_CONFIG.studyDistricts.map((d) => (
                <option key={d} value={d}>
                  {d}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Current Forecast Strip */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 sm:gap-3 pt-3 border-t border-slate-100 text-xs">
          <div className="flex items-center gap-1.5 sm:gap-2 text-slate-600">
            <Thermometer className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-slate-400 shrink-0" />
            <span className="truncate">Temp: <strong className="font-mono text-slate-900">{district.currentForecast.temperature} °C</strong></span>
          </div>
          <div className="flex items-center gap-1.5 sm:gap-2 text-slate-600">
            <CloudRain className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-slate-400 shrink-0" />
            <span className="truncate">Precip: <strong className="font-mono text-slate-900">{district.currentForecast.rainfall} mm</strong></span>
          </div>
          <div className="flex items-center gap-1.5 sm:gap-2 text-slate-600">
            <Wind className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-slate-400 shrink-0" />
            <span className="truncate">Wind: <strong className="font-mono text-slate-900">{district.currentForecast.windSpeed} km/h</strong></span>
          </div>
          <div className="flex items-center gap-1.5 sm:gap-2 text-slate-600">
            <Compass className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-slate-400 shrink-0" />
            <span className="truncate">Cycle: <strong className="font-mono text-slate-900">{district.currentForecast.initCycle}</strong></span>
          </div>
        </div>
      </div>

      {/* Current District Verification Status KPIs */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
        {/* Reliability */}
        <Card noPadding className="p-4 bg-white">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">
              Empirical Reliability
            </span>
            <Activity className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="text-2xl font-bold font-mono text-slate-900">
            {district.reliability.toFixed(2)}
          </div>
          <span className="text-[11px] text-slate-500 mt-1 block">
            Tolerance Scale: 2.0 °C
          </span>
        </Card>

        {/* Uncertainty */}
        <Card noPadding className="p-4 bg-white">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">
              Forecast Uncertainty
            </span>
            <Badge
              variant={
                district.uncertainty === 'Low'
                  ? 'emerald'
                  : district.uncertainty === 'Moderate'
                  ? 'amber'
                  : 'rose'
              }
              size="xs"
            >
              {district.uncertainty}
            </Badge>
          </div>
          <div className="text-2xl font-bold text-slate-900">
            {district.uncertainty}
          </div>
          <span className="text-[11px] text-slate-500 mt-1 block">
            Atmospheric dispersion
          </span>
        </Card>

        {/* Bust Probability */}
        <Card noPadding className="p-4 bg-white">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">
              Bust Probability
            </span>
            <AlertTriangle className="w-4 h-4 text-rose-600" />
          </div>
          <div className="text-2xl font-bold font-mono text-rose-700">
            {district.bustProbability}%
          </div>
          <span className="text-[11px] text-slate-500 mt-1 block">
            Upper 90th percentile risk
          </span>
        </Card>

        {/* Lead Day MAE */}
        <Card noPadding className="p-4 bg-white">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">
              Lead Day 5 MAE
            </span>
            <Layers className="w-4 h-4 text-indigo-600" />
          </div>
          <div className="text-2xl font-bold font-mono text-indigo-700">
            {district.mae.toFixed(2)} °C
          </div>
          <span className="text-[11px] text-slate-500 mt-1 block">
            RMSE: {district.rmse.toFixed(2)} °C
          </span>
        </Card>
      </div>

      {/* Forecast vs Reference Section (NOAA GFS vs ECMWF ERA5) */}
      <Card
        title="Forecast vs Reference Verification Timeline"
        subtitle={`Comparative lookahead for ${district.name}: NOAA GFS Forecast evaluated strictly against ECMWF ERA5 Reference`}
      >
        <ForecastVsReferenceChart
          data={forecastVsReference}
          districtName={district.name}
        />
      </Card>

      {/* Historical Performance Across Lead Horizon */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Error metrics vs lead day */}
        <Card
          title="Lead Day Error Evolution"
          subtitle={`MAE, RMSE, and Signed Bias progression across Days 1–10 for ${district.name}`}
        >
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart
                data={chartErrorData}
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
                <Tooltip />
                <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
                <Line
                  type="monotone"
                  dataKey="MAE"
                  stroke="#0284c7"
                  strokeWidth={2.5}
                  dot={{ r: 3 }}
                  name="MAE (°C)"
                />
                <Line
                  type="monotone"
                  dataKey="RMSE"
                  stroke="#6366f1"
                  strokeWidth={2}
                  strokeDasharray="4 2"
                  dot={{ r: 3 }}
                  name="RMSE (°C)"
                />
                <Line
                  type="monotone"
                  dataKey="Bias"
                  stroke="#f59e0b"
                  strokeWidth={1.8}
                  strokeDasharray="2 2"
                  dot={{ r: 2.5 }}
                  name="Signed Bias (°C)"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Card>

        {/* Reliability vs lead day */}
        <Card
          title="Reliability Decay vs Lead Day"
          subtitle={`Empirical reliability curve R(t) for ${district.name}`}
        >
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart
                data={chartErrorData}
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
                  domain={[0, 1]}
                  ticks={[0, 0.25, 0.5, 0.75, 1.0]}
                  stroke="#94a3b8"
                  fontSize={11}
                  tickLine={false}
                  axisLine={{ stroke: '#e2e8f0' }}
                />
                <Tooltip />
                <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
                <Line
                  type="monotone"
                  dataKey="Reliability"
                  stroke="#059669"
                  strokeWidth={3}
                  dot={{ r: 4, fill: '#059669' }}
                  name="Empirical Reliability (R)"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>

      {/* Verification Guidelines Footer */}
      <ScientificDisclaimer type="reference" />
    </div>
  );
};
