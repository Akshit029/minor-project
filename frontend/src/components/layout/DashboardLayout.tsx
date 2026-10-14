import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Navbar } from './Navbar';

export const DashboardLayout: React.FC = () => {
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);

  const handleRefresh = () => {
    setIsRefreshing(true);
    setTimeout(() => {
      setIsRefreshing(false);
      setRefreshKey(prev => prev + 1);
    }, 450);
  };

  return (
    <div className="flex min-h-screen bg-slate-50 text-slate-900 font-sans">
      {/* Sidebar */}
      <Sidebar alertCount={3} />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        <Navbar
          onRefresh={handleRefresh}
          isRefreshing={isRefreshing}
          alertCount={3}
        />

        <main className="flex-1 p-6 lg:p-8 max-w-7xl w-full mx-auto space-y-6" key={refreshKey}>
          <Outlet />
        </main>

        {/* Global Scientific Footer */}
        <footer className="border-t border-slate-200 bg-white py-4 px-8 text-center text-xs text-slate-500">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-2 max-w-7xl mx-auto">
            <span>
              B.Tech Minor Project: <em>Spatiotemporal Reliability &amp; Uncertainty Detection for Medium-Range Weather Forecasts</em>
            </span>
            <span className="font-mono text-slate-400 text-[11px]">
              NOAA GFS 0.25° • ECMWF ERA5 Single Levels • Jammu &amp; Kashmir Domain
            </span>
          </div>
        </footer>
      </div>
    </div>
  );
};
