import React from 'react';
import { useLocation, Link } from 'react-router-dom';
import { 
  RefreshCw, 
  Bell, 
  MapPin, 
  Clock, 
  GraduationCap,
  Menu
} from 'lucide-react';
import { APP_CONFIG } from '../../data/config';

interface NavbarProps {
  onRefresh?: () => void;
  isRefreshing?: boolean;
  alertCount?: number;
  onToggleMobileMenu?: () => void;
  isMobileMenuOpen?: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({
  onRefresh,
  isRefreshing = false,
  alertCount = 3,
  onToggleMobileMenu,
}) => {
  const location = useLocation();

  // Derive human-readable page name from path
  const getPageTitle = (pathname: string) => {
    switch (pathname) {
      case '/':
      case '/overview':
        return 'Overview Dashboard';
      case '/reliability':
        return 'Forecast Reliability Analysis';
      case '/district-analysis':
        return 'District In-Depth Verification';
      case '/forecast-bust':
        return 'Forecast-Bust ML Prediction';
      case '/alerts':
        return 'Alerts & Anomaly History';
      case '/model-performance':
        return 'Model Performance & Evaluation';
      case '/methodology':
        return 'Scientific Methodology & Pipeline';
      default:
        return 'Dashboard';
    }
  };

  return (
    <header className="h-14 sm:h-16 bg-white border-b border-slate-200/90 px-3 sm:px-6 flex items-center justify-between sticky top-0 z-30 shadow-2xs">
      {/* Left: Mobile Menu Toggle + Breadcrumbs */}
      <div className="flex items-center gap-2 sm:gap-3 min-w-0">
        {/* Mobile Hamburger Button */}
        <button
          id="mobile-menu-btn"
          onClick={onToggleMobileMenu}
          className="lg:hidden p-2 rounded-lg border border-slate-200 text-slate-700 hover:text-slate-900 hover:bg-slate-100 transition-colors shrink-0 cursor-pointer active:scale-95"
          aria-label="Toggle Navigation Menu"
        >
          <Menu className="w-4 h-4 sm:w-5 sm:h-5" />
        </button>

        <div className="min-w-0">
          <div className="flex items-center gap-1.5 sm:gap-2 text-xs truncate">
            <span className="hidden sm:inline font-semibold text-slate-400 uppercase tracking-wider text-[11px]">
              {APP_CONFIG.projectTitle}
            </span>
            <span className="hidden sm:inline text-slate-300">/</span>
            <span className="font-bold text-slate-900 truncate text-xs sm:text-sm">
              {getPageTitle(location.pathname)}
            </span>
          </div>
          <div className="flex items-center gap-2 text-[11px] sm:text-xs text-slate-500 mt-0.5 truncate">
            <span className="flex items-center gap-1 font-medium text-slate-600 truncate">
              <MapPin className="w-3 h-3 text-slate-400 shrink-0" />
              <span className="truncate">{APP_CONFIG.region.name}</span>
              <span className="hidden md:inline text-slate-400">(31°N–38°N, 73°E–81°E)</span>
            </span>
          </div>
        </div>
      </div>

      {/* Right: Timestamp, Refresh, Alerts, User Avatar */}
      <div className="flex items-center gap-1.5 sm:gap-3 shrink-0">
        {/* Timestamp (hidden on small/medium screens to save space) */}
        <div className="hidden xl:flex items-center gap-1.5 px-3 py-1 rounded-lg bg-slate-50 border border-slate-200/80 text-xs font-mono text-slate-600">
          <Clock className="w-3.5 h-3.5 text-slate-400" />
          <span>2026-10-14 12:00 UTC</span>
        </div>

        {/* Refresh button */}
        <button
          onClick={onRefresh}
          disabled={isRefreshing}
          className={`p-2 rounded-lg border border-slate-200 text-slate-600 hover:text-slate-900 hover:bg-slate-50 transition-all ${
            isRefreshing ? 'opacity-70 cursor-not-allowed' : 'cursor-pointer active:scale-95'
          }`}
          title="Simulate data refresh"
          aria-label="Refresh data"
        >
          <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin text-indigo-600' : ''}`} />
        </button>

        {/* Alert Bell */}
        <Link
          to="/alerts"
          className="relative p-2 rounded-lg border border-slate-200 text-slate-600 hover:text-slate-900 hover:bg-slate-50 transition-colors"
          title="View Alerts"
          aria-label="View Alerts"
        >
          <Bell className="w-4 h-4" />
          {alertCount > 0 && (
            <span className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-rose-600 text-white text-[10px] font-bold flex items-center justify-center ring-2 ring-white">
              {alertCount}
            </span>
          )}
        </Link>

        {/* User / Project Avatar */}
        <div className="flex items-center gap-2 pl-1.5 sm:pl-2 border-l border-slate-200">
          <div className="w-7 h-7 sm:w-8 sm:h-8 rounded-lg bg-slate-100 border border-slate-300 flex items-center justify-center text-slate-700 shadow-2xs shrink-0">
            <GraduationCap className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-slate-700" />
          </div>
          <div className="hidden md:block text-left">
            <div className="text-xs font-semibold text-slate-800 leading-tight">
              B.Tech Project
            </div>
            <div className="text-[10px] text-slate-400 font-medium">
              Research Prototype
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

