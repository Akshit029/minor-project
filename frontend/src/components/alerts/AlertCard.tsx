import React from 'react';
import type { AlertItem } from '../../types/weather';
import { Badge } from '../common/Badge';
import { AlertCircle, AlertTriangle, Info, Clock, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';

interface AlertCardProps {
  alert: AlertItem;
  onViewAnalysis?: (alert: AlertItem) => void;
  compact?: boolean;
}

export const AlertCard: React.FC<AlertCardProps> = ({
  alert,
  onViewAnalysis,
  compact = false,
}) => {
  const getSeverityConfig = (severity: AlertItem['severity']) => {
    switch (severity) {
      case 'critical':
        return {
          icon: AlertCircle,
          badgeVariant: 'rose' as const,
          border: 'border-l-4 border-l-rose-600',
          badgeText: 'CRITICAL BUST RISK',
        };
      case 'high':
        return {
          icon: AlertTriangle,
          badgeVariant: 'rose' as const,
          border: 'border-l-4 border-l-rose-500',
          badgeText: 'HIGH UNCERTAINTY',
        };
      case 'moderate':
        return {
          icon: AlertTriangle,
          badgeVariant: 'amber' as const,
          border: 'border-l-4 border-l-amber-500',
          badgeText: 'MODERATE UNCERTAINTY',
        };
      case 'low':
      default:
        return {
          icon: Info,
          badgeVariant: 'blue' as const,
          border: 'border-l-4 border-l-sky-500',
          badgeText: 'QUALITY WARNING',
        };
    }
  };

  const config = getSeverityConfig(alert.severity);
  const Icon = config.icon;

  return (
    <div
      className={`bg-white rounded-xl border border-slate-200/90 shadow-2xs hover:shadow-xs transition-all p-4 ${config.border} space-y-2.5 font-sans`}
    >
      {/* Top Header */}
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-2">
          <Badge variant={config.badgeVariant} size="xs" dot>
            {config.badgeText}
          </Badge>
          <span className="text-xs font-bold text-slate-800">
            {alert.district}
          </span>
          <span className="text-slate-300">•</span>
          <span className="text-xs font-mono font-medium text-slate-600">
            Day {alert.leadDay}
          </span>
        </div>

        <div className="flex items-center gap-1 text-[11px] text-slate-400 font-mono">
          <Clock className="w-3 h-3" />
          <span>{alert.timestamp}</span>
        </div>
      </div>

      {/* Title & Explanation */}
      <div>
        <h4 className="text-xs font-bold text-slate-900 leading-snug">
          {alert.title}
        </h4>
        <p className="text-xs text-slate-600 mt-1 leading-relaxed">
          {alert.explanation}
        </p>
      </div>

      {/* Metrics Strip */}
      <div className="flex items-center gap-4 pt-1 border-t border-slate-100 text-xs">
        <div>
          <span className="text-[10px] text-slate-400 uppercase tracking-wider block">
            Bust Prob
          </span>
          <span className="font-mono font-bold text-rose-600">
            {alert.bustProbability}%
          </span>
        </div>

        <div>
          <span className="text-[10px] text-slate-400 uppercase tracking-wider block">
            Reliability (R)
          </span>
          <span className="font-mono font-bold text-slate-800">
            {alert.reliability.toFixed(2)}
          </span>
        </div>

        <div>
          <span className="text-[10px] text-slate-400 uppercase tracking-wider block">
            Forecast Value
          </span>
          <span className="font-mono font-bold text-slate-800">
            {alert.forecastValue} {alert.variable === 'temperature_c' ? '°C' : 'mm'}
          </span>
        </div>

        <div className="ml-auto">
          {onViewAnalysis ? (
            <button
              onClick={() => onViewAnalysis(alert)}
              className="inline-flex items-center gap-1 text-xs font-semibold text-slate-900 hover:text-indigo-600 transition-colors cursor-pointer"
            >
              <span>View Analysis</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          ) : (
            <Link
              to={`/district-analysis?district=${alert.district}`}
              className="inline-flex items-center gap-1 text-xs font-semibold text-slate-900 hover:text-indigo-600 transition-colors"
            >
              <span>View Analysis</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          )}
        </div>
      </div>
    </div>
  );
};
