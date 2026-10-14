import React from 'react';

export interface BadgeProps {
  children: React.ReactNode;
  variant?: 'emerald' | 'amber' | 'rose' | 'slate' | 'blue' | 'indigo' | 'outline';
  size?: 'sm' | 'md' | 'xs';
  className?: string;
  dot?: boolean;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'slate',
  size = 'sm',
  className = '',
  dot = false,
}) => {
  const variantStyles = {
    emerald: 'bg-emerald-50 text-emerald-700 border-emerald-200/80',
    amber: 'bg-amber-50 text-amber-700 border-amber-200/80',
    rose: 'bg-rose-50 text-rose-700 border-rose-200/80',
    slate: 'bg-slate-100 text-slate-700 border-slate-200',
    blue: 'bg-sky-50 text-sky-700 border-sky-200',
    indigo: 'bg-indigo-50 text-indigo-700 border-indigo-200',
    outline: 'bg-transparent text-slate-600 border-slate-300',
  };

  const dotColors = {
    emerald: 'bg-emerald-500',
    amber: 'bg-amber-500',
    rose: 'bg-rose-500',
    slate: 'bg-slate-400',
    blue: 'bg-sky-500',
    indigo: 'bg-indigo-500',
    outline: 'bg-slate-400',
  };

  const sizeStyles = {
    xs: 'px-1.5 py-0.5 text-[10px] font-medium tracking-wide',
    sm: 'px-2.5 py-0.5 text-xs font-medium',
    md: 'px-3 py-1 text-xs font-semibold',
  };

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border ${variantStyles[variant]} ${sizeStyles[size]} ${className}`}
    >
      {dot && <span className={`w-1.5 h-1.5 rounded-full ${dotColors[variant]}`} />}
      {children}
    </span>
  );
};
