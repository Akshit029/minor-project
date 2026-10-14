import React, { useState } from 'react';
import { useLocation, Link } from 'react-router-dom';
import { 
  RefreshCw, 
  Bell, 
  MapPin, 
  Clock, 
  AlertTriangle,
  GraduationCap
} from 'lucide-react';
import { APP_CONFIG } from '../../data/config';

interface NavbarProps {
  onRefresh?: () => void;
  isRefreshing?: boolean;
  alertCount?: number;
}

export const Navbar: React.FC<NavbarProps> = ({
  onRefresh,
  isRefreshing = false,
  alertCount = 3,
}) => {
  const location = useLocation();
  const [showDemoModal, setShowDemoModal] = useState(false);

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
    <header className="h-16 bg-white border-b border-slate-200/90 px-6 flex items-center justify-between sticky top-0 z-30 shadow-2xs">
      {/* Left: Project title & Current Page Breadcrumb */}
      <div className="flex items-center gap-3">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              {APP_CONFIG.projectTitle}
            </span>
            <span className="text-slate-300">/</span>
            <span className="text-xs font-semibold text-slate-800">
              {getPageTitle(location.pathname)}
            </span>
          </div>
          <div className="flex items-center gap-2 text-xs text-slate-500 mt-0.5">
            <span className="flex items-center gap-1 font-medium text-slate-600">
              <MapPin className="w-3.5 h-3.5 text-slate-400" />
              {APP_CONFIG.region.name} (31°N–38°N, 73°E–81°E)
            </span>
          </div>
        </div>
      </div>

      {/* Right: Region Info, Timestamp, Refresh, Alerts, and Demo Pill */}
      <div className="flex items-center gap-3">
        {/* Demo Data indicator */}
        <button
          onClick={() => setShowDemoModal(true)}
          className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-amber-50 border border-amber-200 text-amber-800 text-[11px] font-semibold hover:bg-amber-100 transition-colors cursor-pointer"
          title="Click to view dataset disclaimer"
        >
          <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
          <span>DEMO DATA</span>
        </button>

        {/* Timestamp */}
        <div className="hidden lg:flex items-center gap-1.5 px-3 py-1 rounded-lg bg-slate-50 border border-slate-200/80 text-xs font-mono text-slate-600">
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
        >
          <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin text-indigo-600' : ''}`} />
        </button>

        {/* Alert Bell */}
        <Link
          to="/alerts"
          className="relative p-2 rounded-lg border border-slate-200 text-slate-600 hover:text-slate-900 hover:bg-slate-50 transition-colors"
          title="View Alerts"
        >
          <Bell className="w-4 h-4" />
          {alertCount > 0 && (
            <span className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-rose-600 text-white text-[10px] font-bold flex items-center justify-center ring-2 ring-white">
              {alertCount}
            </span>
          )}
        </Link>

        {/* User / Project Avatar */}
        <div className="flex items-center gap-2 pl-2 border-l border-slate-200">
          <div className="w-8 h-8 rounded-lg bg-slate-100 border border-slate-300 flex items-center justify-center text-slate-700 shadow-2xs">
            <GraduationCap className="w-4 h-4 text-slate-700" />
          </div>
          <div className="hidden sm:block text-left">
            <div className="text-xs font-semibold text-slate-800 leading-tight">
              B.Tech Project
            </div>
            <div className="text-[10px] text-slate-400 font-medium">
              Research Prototype
            </div>
          </div>
        </div>
      </div>

      {/* Demo Data Explanation Modal */}
      {showDemoModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-xs p-4">
          <div className="bg-white rounded-xl max-w-md w-full border border-slate-200 shadow-xl p-6 space-y-4">
            <div className="flex items-start gap-3">
              <div className="p-2 rounded-lg bg-amber-100 text-amber-700">
                <AlertTriangle className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-base font-semibold text-slate-900">
                  Demo Dataset Notice
                </h3>
                <p className="text-xs text-slate-500 mt-0.5">
                  Scientific integrity note regarding frontend metrics
                </p>
              </div>
            </div>

            <div className="text-xs text-slate-600 space-y-2 leading-relaxed bg-slate-50 p-4 rounded-lg border border-slate-200">
              <p>
                <strong>Current Status:</strong> The frontend is operating in <em>Demo Data Mode</em> while the 2,000+ day historical GFS/ERA5 matched dataset and full training cycle are completed by the Python research pipeline.
              </p>
              <p>
                <strong>No Fabrication:</strong> The numbers displayed are illustrative samples based on early pipeline runs and engineering thresholds. They must not be cited as definitive verified meteorological findings.
              </p>
              <p>
                <strong>Ready for REST Integration:</strong> The frontend is fully decoupled and ready to connect to <code className="bg-slate-200 px-1 py-0.5 rounded font-mono">GET /api/*</code> endpoints without modifying UI components.
              </p>
            </div>

            <div className="flex justify-end pt-2">
              <button
                onClick={() => setShowDemoModal(false)}
                className="px-4 py-2 rounded-lg bg-slate-900 text-white text-xs font-semibold hover:bg-slate-800 transition-colors"
              >
                Understood
              </button>
            </div>
          </div>
        </div>
      )}
    </header>
  );
};
