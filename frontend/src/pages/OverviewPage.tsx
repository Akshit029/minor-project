import React, { useEffect, useState } from 'react';
import { WeatherApi, OverviewApiResponse } from '../services/api';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { MetricValue } from '../components/common/MetricValue';
import { Skeleton } from '../components/common/Skeleton';
import { JKLeafletMap } from '../components/map/JKLeafletMap';
import { ReliabilityTrendChart } from '../components/charts/ReliabilityTrendChart';
import { ForecastErrorChart } from '../components/charts/ForecastErrorChart';
import { DistrictComparisonChart } from '../components/charts/DistrictComparisonChart';
import { AlertCard } from '../components/alerts/AlertCard';
import { AlertModal } from '../components/alerts/AlertModal';
import type { DistrictName, AlertItem } from '../types/weather';
import { 
  Activity, 
  AlertTriangle, 
  Award, 
  HelpCircle, 
  Calendar, 
  Database, 
  MapPin, 
  ArrowRight,
  ShieldCheck,
  TrendingDown,
  Layers
} from 'lucide-react';
import { Link } from 'react-router-dom';

export const OverviewPage: React.FC = () => {
  const [data, setData] = useState<OverviewApiResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedDistrict, setSelectedDistrict] = useState<DistrictName | null>(null);
  const [activeAlertModal, setActiveAlertModal] = useState<AlertItem | null>(null);

  useEffect(() => {
    let isMounted = true;
    WeatherApi.getOverview()
      .then((res) => {
        if (isMounted) {
          setData(res);
          setLoading(false);
        }
      })
      .catch((err) => {
        console.error('Failed to load overview data:', err);
        if (isMounted) setLoading(false);
      });
    return () => {
      isMounted = false;
    };
  }, []);

  if (loading || !data) {
    return (
      <div className="space-y-6">
        <div className="h-20 bg-white rounded-xl border border-slate-200 p-6 animate-pulse" />
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="h-28 bg-white rounded-xl border border-slate-200 p-4 animate-pulse" />
          ))}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          <div className="lg:col-span-8 h-96 bg-white rounded-xl border border-slate-200 animate-pulse" />
          <div className="lg:col-span-4 h-96 bg-white rounded-xl border border-slate-200 animate-pulse" />
        </div>
      </div>
    );
  }

  const { kpis, districts, leadDayMetrics, recentAlerts, currentLeadDay } = data;

  return (
    <div className="space-y-6 font-sans">
      {/* 4. Overview Header */}
      <div className="bg-white rounded-xl border border-slate-200/90 shadow-2xs p-4 sm:p-6 space-y-4">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div>
            <div className="flex flex-wrap items-center gap-1.5 sm:gap-2 mb-1.5">
              <Badge variant="slate" size="xs">
                J&amp;K UT Domain
              </Badge>
              <Badge variant="blue" size="xs">
                {kpis.forecastHorizon}
              </Badge>
              <Badge variant="amber" size="xs" dot>
                Research Prototype
              </Badge>
            </div>
            <h1 className="text-lg sm:text-2xl font-bold text-slate-900 tracking-tight">
              Jammu &amp; Kashmir Forecast Reliability
            </h1>
            <p className="text-xs sm:text-sm text-slate-500 mt-1 font-normal max-w-3xl leading-relaxed">
              Spatiotemporal analysis of medium-range numerical weather forecast uncertainty across complex mountainous terrain.
            </p>
          </div>

          {/* Quick Context Stats */}
          <div className="flex flex-wrap items-center gap-3 sm:gap-4 text-xs text-slate-600 bg-slate-50/80 p-3 sm:px-4 sm:py-2.5 rounded-xl border border-slate-200/80">
            <div>
              <span className="text-[10px] text-slate-400 font-medium block uppercase tracking-wider">
                Study Districts
              </span>
              <span className="font-semibold text-slate-800">4 Locations</span>
            </div>
            <div className="w-px h-6 bg-slate-200" />
            <div>
              <span className="text-[10px] text-slate-400 font-medium block uppercase tracking-wider">
                Model Pipeline
              </span>
              <span className="font-semibold text-emerald-700 flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                Operational
              </span>
            </div>
            <div className="w-px h-6 bg-slate-200" />
            <div>
              <span className="text-[10px] text-slate-400 font-medium block uppercase tracking-wider">
                Updated
              </span>
              <span className="font-mono text-slate-700 text-[11px] sm:text-xs">{kpis.lastUpdated}</span>
            </div>
          </div>
        </div>
      </div>

      {/* 5. KPI Cards (6 clean cards) */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 sm:gap-4">
        {/* Card 1: Overall Reliability */}
        <Card noPadding className="p-3 sm:p-4 bg-white hover:border-slate-300">
          <div className="flex items-center justify-between mb-1.5">
            <span className="text-[10px] sm:text-[11px] font-semibold text-slate-500 uppercase tracking-wider truncate">
              Overall Reliability
            </span>
            <Activity className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-emerald-600 shrink-0" />
          </div>
          <div className="text-xl sm:text-2xl font-bold font-mono text-emerald-700 tracking-tight">
            {kpis.overallReliability.toFixed(2)}
          </div>
          <div className="text-[10px] sm:text-[11px] text-slate-500 mt-1 leading-tight line-clamp-1 sm:line-clamp-none">
            {kpis.overallReliabilityLabel}
          </div>
        </Card>

        {/* Card 2: Forecast Bust Risk */}
        <Card noPadding className="p-3 sm:p-4 bg-white hover:border-slate-300">
          <div className="flex items-center justify-between mb-1.5">
            <span className="text-[10px] sm:text-[11px] font-semibold text-slate-500 uppercase tracking-wider truncate">
              Bust Risk
            </span>
            <AlertTriangle className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-amber-500 shrink-0" />
          </div>
          <div className="text-xl sm:text-2xl font-bold font-mono text-amber-700 tracking-tight">
            {kpis.forecastBustRisk}%
          </div>
          <div className="text-[10px] sm:text-[11px] text-slate-500 mt-1 leading-tight line-clamp-1 sm:line-clamp-none">
            {kpis.forecastBustRiskLabel}
          </div>
        </Card>

        {/* Card 3: Best Performing District */}
        <Card noPadding className="p-3 sm:p-4 bg-white hover:border-slate-300">
          <div className="flex items-center justify-between mb-1.5">
            <span className="text-[10px] sm:text-[11px] font-semibold text-slate-500 uppercase tracking-wider truncate">
              Best District
            </span>
            <Award className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-sky-600 shrink-0" />
          </div>
          <div className="text-lg sm:text-xl font-bold text-slate-900 tracking-tight truncate">
            {kpis.bestPerformingDistrict}
          </div>
          <div className="text-[10px] sm:text-[11px] text-emerald-600 font-medium mt-1 truncate">
            Lowest hist. MAE
          </div>
        </Card>

        {/* Card 4: Highest Uncertainty */}
        <Card noPadding className="p-3 sm:p-4 bg-white hover:border-slate-300">
          <div className="flex items-center justify-between mb-1.5">
            <span className="text-[10px] sm:text-[11px] font-semibold text-slate-500 uppercase tracking-wider truncate">
              High Uncertainty
            </span>
            <TrendingDown className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-rose-500 shrink-0" />
          </div>
          <div className="text-lg sm:text-xl font-bold text-slate-900 tracking-tight truncate">
            {kpis.highestUncertaintyDistrict}
          </div>
          <div className="text-[10px] sm:text-[11px] text-rose-600 font-medium mt-1 truncate">
            Elevated variance
          </div>
        </Card>

        {/* Card 5: Forecast Lead */}
        <Card noPadding className="p-3 sm:p-4 bg-white hover:border-slate-300">
          <div className="flex items-center justify-between mb-1.5">
            <span className="text-[10px] sm:text-[11px] font-semibold text-slate-500 uppercase tracking-wider truncate">
              Forecast Lead
            </span>
            <Calendar className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-indigo-500 shrink-0" />
          </div>
          <div className="text-lg sm:text-xl font-bold font-mono text-slate-900 tracking-tight">
            {kpis.forecastLead}
          </div>
          <div className="text-[10px] sm:text-[11px] text-slate-500 mt-1">
            120h Lookahead
          </div>
        </Card>

        {/* Card 6: Verification Status */}
        <Card noPadding className="p-3 sm:p-4 bg-white hover:border-slate-300">
          <div className="flex items-center justify-between mb-1.5">
            <span className="text-[10px] sm:text-[11px] font-semibold text-slate-500 uppercase tracking-wider truncate">
              Verification Pipeline
            </span>
            <Database className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-emerald-600 shrink-0" />
          </div>
          <div className="text-lg sm:text-xl font-bold text-emerald-700 tracking-tight">
            Active
          </div>
          <div className="text-[10px] sm:text-[11px] text-slate-500 mt-1 truncate">
            GFS &amp; ERA5 Ingested
          </div>
        </Card>
      </div>

      {/* Main Map & Alerts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* 6. Interactive J&K Map (8 cols) */}
        <div className="lg:col-span-8 space-y-3">
          <Card
            title="Spatiotemporal Forecast Reliability Map"
            subtitle="Click or hover any of the 4 representative districts to inspect localized verification scores"
            action={
              <Link
                to="/reliability"
                className="text-xs font-semibold text-slate-900 hover:text-indigo-600 flex items-center gap-1 transition-colors"
              >
                <span>Lead Day Heatmap</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            }
          >
            <JKLeafletMap
              districts={districts}
              selectedDistrict={selectedDistrict}
              onSelectDistrict={(name) => setSelectedDistrict(name)}
              leadDay={currentLeadDay}
            />
          </Card>
        </div>

        {/* 7. Alert System Panel (4 cols) */}
        <div className="lg:col-span-4 space-y-3">
          <Card
            title="Forecast Alerts & Anomalies"
            subtitle={`${recentAlerts.length} active alerts detected via configurable thresholds`}
            action={
              <Link
                to="/alerts"
                className="text-xs font-semibold text-slate-900 hover:text-indigo-600 flex items-center gap-1 transition-colors"
              >
                <span>All Alerts ({recentAlerts.length})</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            }
          >
            <div className="space-y-3 max-h-[460px] overflow-y-auto pr-1">
              {recentAlerts.map((alert) => (
                <AlertCard
                  key={alert.id}
                  alert={alert}
                  onViewAnalysis={(a) => setActiveAlertModal(a)}
                />
              ))}
            </div>
          </Card>
        </div>
      </div>

      {/* 8 & 9. Charts Section: Reliability Trend & Forecast Errors */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 8. Reliability by Forecast Lead Day */}
        <Card
          title="Reliability by Forecast Lead Day"
          subtitle="Empirical performance index R in [0, 1] across 10-day lookahead horizon"
          action={
            <Badge variant="slate" size="xs">
              R = R_error × C
            </Badge>
          }
        >
          <ReliabilityTrendChart
            data={leadDayMetrics}
            highlightDistrict={selectedDistrict}
          />
        </Card>

        {/* 9. Forecast Error vs Lead Day */}
        <Card
          title="Forecast Error vs Lead Day"
          subtitle="Mean Absolute Error (MAE), RMSE, and Signed Bias against ERA5 Reference"
          action={
            <Badge variant="blue" size="xs">
              MAE / RMSE / Bias
            </Badge>
          }
        >
          <ForecastErrorChart data={leadDayMetrics} />
        </Card>
      </div>

      {/* 10. District Comparison Section */}
      <Card
        title="District Multi-Metric Comparison"
        subtitle="Comparing Srinagar, Jammu, Anantnag, and Baramulla across reliability, error magnitude, and bust risk"
        action={
          <Link
            to={`/district-analysis?district=${selectedDistrict || 'Srinagar'}`}
            className="text-xs font-semibold text-slate-900 hover:text-indigo-600 flex items-center gap-1 transition-colors"
          >
            <span>District Detail View</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        }
      >
        <DistrictComparisonChart
          districts={districts}
          selectedDistrict={selectedDistrict}
          onSelectDistrict={(name) => setSelectedDistrict(name)}
        />
      </Card>

      {/* Alert Detail Modal */}
      <AlertModal
        alert={activeAlertModal}
        onClose={() => setActiveAlertModal(null)}
      />
    </div>
  );
};
