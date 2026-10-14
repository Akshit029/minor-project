import React from 'react';

export interface MetricValueProps {
  value: string | number;
  unit?: string;
  label?: string;
  sublabel?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  variant?: 'default' | 'high-reliability' | 'moderate' | 'low' | 'uncertain' | 'critical';
  trend?: {
    direction: 'up' | 'down' | 'neutral';
    text: string;
  };
  className?: string;
}

export const MetricValue: React.FC<MetricValueProps> = ({
  value,
  unit,
  label,
  sublabel,
  size = 'md',
  variant = 'default',
  trend,
  className = '',
}) => {
  const sizeStyles = {
    sm: 'text-lg font-semibold',
    md: 'text-2xl font-semibold tracking-tight',
    lg: 'text-3xl font-bold tracking-tight',
    xl: 'text-4xl font-bold tracking-tight',
  };

  const variantStyles = {
    default: 'text-slate-900',
    'high-reliability': 'text-emerald-700',
    moderate: 'text-amber-700',
    low: 'text-orange-700',
    uncertain: 'text-rose-700',
    critical: 'text-rose-700',
  };

  return (
    <div className={`flex flex-col ${className}`}>
      {label && (
        <span className="text-xs font-medium text-slate-500 uppercase tracking-wider mb-1">
          {label}
        </span>
      )}
      <div className="flex items-baseline gap-1.5">
        <span className={`font-mono tabular-nums ${sizeStyles[size]} ${variantStyles[variant]}`}>
          {value}
        </span>
        {unit && (
          <span className="text-xs font-medium text-slate-500">
            {unit}
          </span>
        )}
      </div>
      {sublabel && (
        <span className="text-xs text-slate-500 mt-1">
          {sublabel}
        </span>
      )}
      {trend && (
        <div className="flex items-center gap-1 mt-1.5 text-xs text-slate-500">
          <span className={trend.direction === 'up' ? 'text-rose-600' : trend.direction === 'down' ? 'text-emerald-600' : 'text-slate-500'}>
            {trend.direction === 'up' ? '↑' : trend.direction === 'down' ? '↓' : '→'}
          </span>
          <span>{trend.text}</span>
        </div>
      )}
    </div>
  );
};
