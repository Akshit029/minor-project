import React from 'react';

export interface CardProps {
  children: React.ReactNode;
  className?: string;
  title?: React.ReactNode;
  subtitle?: React.ReactNode;
  action?: React.ReactNode;
  icon?: React.ReactNode;
  footer?: React.ReactNode;
  noPadding?: boolean;
}

export const Card: React.FC<CardProps> = ({
  children,
  className = '',
  title,
  subtitle,
  action,
  icon,
  footer,
  noPadding = false,
}) => {
  return (
    <div className={`bg-white rounded-xl border border-slate-200/90 shadow-[0_1px_3px_0_rgba(0,0,0,0.04)] transition-all ${className}`}>
      {(title || subtitle || action || icon) && (
        <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-2.5 sm:gap-4 p-3.5 sm:p-5 pb-3 sm:pb-4 border-b border-slate-100">
          <div className="flex items-start gap-2.5 sm:gap-3 min-w-0">
            {icon && (
              <div className="p-1.5 sm:p-2 rounded-lg bg-slate-50 border border-slate-200 text-slate-700 mt-0.5 shrink-0">
                {icon}
              </div>
            )}
            <div className="min-w-0">
              {title && (
                <h3 className="text-xs sm:text-sm font-semibold text-slate-900 tracking-tight flex items-center gap-2">
                  {title}
                </h3>
              )}
              {subtitle && (
                <p className="text-[11px] sm:text-xs text-slate-500 mt-0.5 font-normal">
                  {subtitle}
                </p>
              )}
            </div>
          </div>
          {action && <div className="flex items-center gap-2 shrink-0 self-start sm:self-auto">{action}</div>}
        </div>
      )}

      <div className={noPadding ? '' : 'p-3.5 sm:p-5'}>
        {children}
      </div>

      {footer && (
        <div className="px-4 sm:px-5 py-2.5 sm:py-3 bg-slate-50/70 border-t border-slate-100 rounded-b-xl text-xs text-slate-500">
          {footer}
        </div>
      )}
    </div>
  );
};
