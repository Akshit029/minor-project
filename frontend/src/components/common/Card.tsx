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
        <div className="flex items-start justify-between gap-4 p-5 pb-4 border-b border-slate-100">
          <div className="flex items-start gap-3">
            {icon && (
              <div className="p-2 rounded-lg bg-slate-50 border border-slate-200 text-slate-700 mt-0.5">
                {icon}
              </div>
            )}
            <div>
              {title && (
                <h3 className="text-sm font-semibold text-slate-900 tracking-tight flex items-center gap-2">
                  {title}
                </h3>
              )}
              {subtitle && (
                <p className="text-xs text-slate-500 mt-0.5 font-normal">
                  {subtitle}
                </p>
              )}
            </div>
          </div>
          {action && <div className="flex items-center gap-2">{action}</div>}
        </div>
      )}

      <div className={noPadding ? '' : 'p-5'}>
        {children}
      </div>

      {footer && (
        <div className="px-5 py-3 bg-slate-50/70 border-t border-slate-100 rounded-b-xl text-xs text-slate-500">
          {footer}
        </div>
      )}
    </div>
  );
};
