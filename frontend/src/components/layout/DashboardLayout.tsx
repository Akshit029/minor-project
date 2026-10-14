import React, { useState, useEffect } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Navbar } from './Navbar';

export const DashboardLayout: React.FC = () => {
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const location = useLocation();

  // Automatically close mobile menu on page navigation
  useEffect(() => {
    setMobileMenuOpen(false);
  }, [location.pathname]);

  const handleRefresh = () => {
    setIsRefreshing(true);
    setTimeout(() => {
      setIsRefreshing(false);
      setRefreshKey(prev => prev + 1);
    }, 450);
  };

  return (
    <div className="flex min-h-screen bg-slate-50 text-slate-900 font-sans relative overflow-x-hidden">
      {/* Sidebar: Permanent on lg+, responsive slide-over drawer on mobile/tablet */}
      <Sidebar
        alertCount={3}
        isOpen={mobileMenuOpen}
        onClose={() => setMobileMenuOpen(false)}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 w-full">
        <Navbar
          onRefresh={handleRefresh}
          isRefreshing={isRefreshing}
          alertCount={3}
          onToggleMobileMenu={() => setMobileMenuOpen(prev => !prev)}
          isMobileMenuOpen={mobileMenuOpen}
        />

        <main className="flex-1 p-3.5 sm:p-5 lg:p-8 max-w-7xl w-full mx-auto space-y-4 sm:space-y-6" key={refreshKey}>
          <Outlet />
        </main>

        {/* Global Scientific Footer */}
        <footer className="border-t border-slate-200 bg-white py-3 sm:py-4 px-4 sm:px-8 text-center text-xs text-slate-500">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-2 max-w-7xl mx-auto">
            <span className="text-[11px] sm:text-xs">
              B.Tech Minor Project: <em>Spatiotemporal Reliability &amp; Uncertainty Detection</em>
            </span>
            <span className="font-mono text-slate-400 text-[10px] sm:text-[11px]">
              NOAA GFS 0.25° • ECMWF ERA5 Single Levels • J&amp;K Domain
            </span>
          </div>
        </footer>
      </div>
    </div>
  );
};

