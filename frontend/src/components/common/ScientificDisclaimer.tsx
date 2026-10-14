import React from 'react';
import { Info, ShieldCheck } from 'lucide-react';
import { APP_CONFIG } from '../../data/config';

interface ScientificDisclaimerProps {
  type?: 'reliability' | 'reference' | 'demo' | 'accumulation';
  className?: string;
  compact?: boolean;
}

export const ScientificDisclaimer: React.FC<ScientificDisclaimerProps> = ({
  type = 'reliability',
  className = '',
  compact = false,
}) => {
  if (type === 'demo') {
    return null;
  }

  if (type === 'reference') {
    return (
      <div className={`flex items-start gap-2.5 p-3 rounded-lg bg-slate-50 border border-slate-200/80 text-xs text-slate-600 ${className}`}>
        <Info className="w-4 h-4 text-slate-500 shrink-0 mt-0.5" />
        <div>
          <span className="font-semibold text-slate-800">Verification Framework: </span>
          <span>Forecasts ({APP_CONFIG.terminology.forecastSource}) are verified against ECMWF ERA5 Atmospheric Reanalysis ({APP_CONFIG.terminology.referenceSource}). Reanalysis fields serve as a continuous reference and are not designated as station ground truth.</span>
        </div>
      </div>
    );
  }

  if (type === 'accumulation') {
    return (
      <div className={`flex items-start gap-2.5 p-3 rounded-lg bg-sky-50 border border-sky-200/80 text-xs text-sky-800 ${className}`}>
        <ShieldCheck className="w-4 h-4 text-sky-600 shrink-0 mt-0.5" />
        <div>
          <span className="font-semibold text-sky-900">Precipitation Accumulation Guard: </span>
          <span>{APP_CONFIG.terminology.accumulationGuardNote}</span>
        </div>
      </div>
    );
  }

  // Default: Empirical Reliability Index
  return (
    <div className={`flex items-start gap-2.5 ${compact ? 'p-2.5 text-[11px]' : 'p-3 text-xs'} rounded-lg bg-slate-50/90 border border-slate-200 text-slate-600 leading-relaxed ${className}`}>
      <Info className="w-4 h-4 text-slate-400 shrink-0 mt-0.5" />
      <div>
        <span className="font-semibold text-slate-700">Scientific Note: </span>
        <span>{APP_CONFIG.terminology.disclaimerText}</span>
      </div>
    </div>
  );
};
