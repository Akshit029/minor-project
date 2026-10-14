import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Activity, 
  MapPin, 
  AlertOctagon, 
  Bell, 
  Cpu, 
  BookOpen, 
  Layers,
  Database
} from 'lucide-react';

interface SidebarProps {
  alertCount?: number;
}

export const Sidebar: React.FC<SidebarProps> = ({ alertCount = 3 }) => {
  const navItems = [
    { to: '/', label: 'Overview', icon: LayoutDashboard },
    { to: '/reliability', label: 'Forecast Reliability', icon: Activity },
    { to: '/district-analysis', label: 'District Analysis', icon: MapPin },
    { to: '/forecast-bust', label: 'Forecast Bust', icon: AlertOctagon },
    { 
      to: '/alerts', 
      label: 'Alerts', 
      icon: Bell, 
      badge: alertCount > 0 ? alertCount : undefined 
    },
    { to: '/model-performance', label: 'Model Performance', icon: Cpu },
    { to: '/methodology', label: 'Methodology', icon: BookOpen },
  ];

  return (
    <aside className="w-64 bg-white border-r border-slate-200/90 flex flex-col shrink-0 min-h-screen select-none">
      {/* Brand & Scientific Context */}
      <div className="p-5 border-b border-slate-200/80">
        <div className="flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-lg bg-slate-900 text-white flex items-center justify-center font-bold text-sm tracking-tight shadow-xs">
            J&amp;K
          </div>
          <div>
            <div className="text-xs font-bold text-slate-900 tracking-tight leading-none uppercase">
              Weather Reliability
            </div>
            <div className="text-[11px] text-slate-500 font-medium mt-1">
              Spatiotemporal Lab
            </div>
          </div>
        </div>
      </div>

      {/* Main Navigation */}
      <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
        <div className="px-3 pt-2 pb-1.5 text-[10px] font-semibold uppercase tracking-wider text-slate-400">
          Analytics &amp; Monitoring
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/'}
              className={({ isActive }) =>
                `flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-medium transition-colors ${
                  isActive
                    ? 'bg-slate-900 text-white shadow-xs'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100/80'
                }`
              }
            >
              {({ isActive }) => (
                <>
                  <div className="flex items-center gap-3">
                    <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-500'}`} />
                    <span>{item.label}</span>
                  </div>
                  {item.badge && (
                    <span
                      className={`px-1.5 py-0.2 rounded-full text-[10px] font-semibold ${
                        isActive
                          ? 'bg-rose-500 text-white'
                          : 'bg-rose-100 text-rose-700'
                      }`}
                    >
                      {item.badge}
                    </span>
                  )}
                </>
              )}
            </NavLink>
          );
        })}
      </nav>

      {/* Research & Pipeline Meta Footer */}
      <div className="p-4 border-t border-slate-200/80 bg-slate-50/70 space-y-3">
        <div className="rounded-lg p-3 bg-white border border-slate-200 shadow-2xs space-y-2 text-xs">
          <div className="flex items-center justify-between">
            <span className="text-[11px] text-slate-500 font-medium">Project:</span>
            <span className="font-semibold text-slate-800 text-[11px]">B.Tech Minor</span>
          </div>

          <div className="flex items-center justify-between">
            <span className="text-[11px] text-slate-500 font-medium flex items-center gap-1">
              <Database className="w-3 h-3 text-slate-400" />
              Pipeline Status:
            </span>
            <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-700">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
              Operational
            </span>
          </div>

          <div className="flex items-center justify-between">
            <span className="text-[11px] text-slate-500 font-medium flex items-center gap-1">
              <Layers className="w-3 h-3 text-slate-400" />
              Model:
            </span>
            <span className="text-[11px] font-mono text-slate-700">
              LR + RF v1.0
            </span>
          </div>
        </div>

        <div className="text-[10px] text-slate-600 text-center">
          NOAA GFS (0.25°) vs ECMWF ERA5
        </div>
      </div>
    </aside>
  );
};
