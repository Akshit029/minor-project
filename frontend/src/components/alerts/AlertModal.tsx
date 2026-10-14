import React from 'react';
import type { AlertItem } from '../../types/weather';
import { Badge } from '../common/Badge';
import { X, AlertTriangle, ShieldCheck, Thermometer, Calendar, Clock } from 'lucide-react';
import { APP_CONFIG } from '../../data/config';
import { Link } from 'react-router-dom';

interface AlertModalProps {
  alert: AlertItem | null;
  onClose: () => void;
}

export const AlertModal: React.FC<AlertModalProps> = ({ alert, onClose }) => {
  if (!alert) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-xs p-4 font-sans">
      <div className="bg-white rounded-2xl max-w-lg w-full border border-slate-200 shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-150">
        {/* Header */}
        <div className="p-5 border-b border-slate-100 flex items-start justify-between bg-slate-50/70">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-rose-100 text-rose-700">
              <AlertTriangle className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <Badge variant={alert.severity === 'critical' || alert.severity === 'high' ? 'rose' : 'amber'} size="xs" dot>
                  {alert.alertType.replace(/_/g, ' ').toUpperCase()}
                </Badge>
                <span className="text-xs text-slate-400 font-mono">ID: {alert.id}</span>
              </div>
              <h3 className="text-base font-bold text-slate-900 mt-1">
                {alert.title}
              </h3>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-200/60 transition-colors cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-6 space-y-4 text-xs">
          {/* Diagnostic Key Values */}
          <div className="grid grid-cols-3 gap-3">
            <div className="p-3 rounded-xl bg-slate-50 border border-slate-200/70">
              <span className="text-[10px] text-slate-400 uppercase font-semibold tracking-wider">
                Target District
              </span>
              <div className="text-sm font-bold text-slate-900 mt-0.5">{alert.district}</div>
              <span className="text-[10px] text-slate-500">Study Location</span>
            </div>

            <div className="p-3 rounded-xl bg-slate-50 border border-slate-200/70">
              <span className="text-[10px] text-slate-400 uppercase font-semibold tracking-wider">
                Lookahead Lead
              </span>
              <div className="text-sm font-bold text-slate-900 mt-0.5">Day {alert.leadDay}</div>
              <span className="text-[10px] text-slate-500">{alert.leadDay * 24} Hours</span>
            </div>

            <div className="p-3 rounded-xl bg-rose-50/70 border border-rose-200/70">
              <span className="text-[10px] text-rose-600 uppercase font-semibold tracking-wider">
                Bust Probability
              </span>
              <div className="text-sm font-bold text-rose-700 mt-0.5">{alert.bustProbability}%</div>
              <span className="text-[10px] text-rose-600">Threshold: &gt;70%</span>
            </div>
          </div>

          {/* Detailed Scientific Diagnostics */}
          <div className="space-y-2">
            <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
              Diagnostic Rationale
            </h4>
            <p className="text-slate-600 leading-relaxed bg-slate-50 p-3 rounded-xl border border-slate-200/70">
              {alert.explanation}
            </p>
          </div>

          {/* Meteorological Parameters */}
          <div className="border border-slate-200/70 rounded-xl p-3.5 space-y-2 bg-white">
            <div className="flex items-center justify-between text-slate-600 pb-2 border-b border-slate-100">
              <span className="flex items-center gap-1.5 font-medium">
                <Thermometer className="w-4 h-4 text-slate-400" />
                Evaluated Forecast Variable:
              </span>
              <span className="font-mono font-semibold text-slate-900">
                {alert.variable} ({alert.forecastValue} {alert.variable === 'temperature_c' ? '°C' : 'mm'})
              </span>
            </div>

            <div className="flex items-center justify-between text-slate-600 pb-2 border-b border-slate-100">
              <span className="flex items-center gap-1.5 font-medium">
                <ShieldCheck className="w-4 h-4 text-slate-400" />
                Empirical Reliability Index (R):
              </span>
              <span className="font-mono font-bold text-slate-900">
                {alert.reliability.toFixed(2)} / 1.00
              </span>
            </div>

            <div className="flex items-center justify-between text-slate-600">
              <span className="flex items-center gap-1.5 font-medium">
                <Clock className="w-4 h-4 text-slate-400" />
                Detection Timestamp:
              </span>
              <span className="font-mono text-slate-700">
                {alert.timestamp}
              </span>
            </div>
          </div>

          {/* Operational Recommended Action */}
          <div className="p-3 rounded-xl bg-amber-50/80 border border-amber-200 text-amber-900 text-xs space-y-1">
            <div className="font-semibold text-amber-950 flex items-center gap-1.5">
              <span>Scientific Advisory:</span>
            </div>
            <p className="text-[11px] text-amber-800 leading-normal">
              High uncertainty detected for medium-range horizon Day {alert.leadDay}. Recommending downscaled localized bias correction and consulting multi-model ensemble spread before operational dissemination.
            </p>
          </div>
        </div>

        {/* Footer actions */}
        <div className="p-4 bg-slate-50 border-t border-slate-100 flex items-center justify-between">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg border border-slate-300 text-slate-700 hover:bg-slate-100 font-medium text-xs transition-colors cursor-pointer"
          >
            Close
          </button>
          <Link
            to={`/district-analysis?district=${alert.district}`}
            onClick={onClose}
            className="px-4 py-2 rounded-lg bg-slate-900 hover:bg-slate-800 text-white font-semibold text-xs transition-colors"
          >
            Open District Analysis →
          </Link>
        </div>
      </div>
    </div>
  );
};
