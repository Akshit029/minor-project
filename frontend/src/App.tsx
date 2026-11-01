import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { DashboardLayout } from './components/layout/DashboardLayout';
import { OverviewPage } from './pages/OverviewPage';
import { ForecastReliabilityPage } from './pages/ForecastReliabilityPage';
import { DistrictAnalysisPage } from './pages/DistrictAnalysisPage';
import { ForecastBustPage } from './pages/ForecastBustPage';
import { AlertsPage } from './pages/AlertsPage';
import { ModelPerformancePage } from './pages/ModelPerformancePage';
import { MethodologyPage } from './pages/MethodologyPage';
import { AIAssistantPage } from './pages/AIAssistantPage';
import { FeatureInfluencePage } from './pages/FeatureInfluencePage';

export function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<DashboardLayout />}>
          <Route index element={<OverviewPage />} />
          <Route path="overview" element={<Navigate to="/" replace />} />
          <Route path="reliability" element={<ForecastReliabilityPage />} />
          <Route path="district-analysis" element={<DistrictAnalysisPage />} />
          <Route path="forecast-bust" element={<ForecastBustPage />} />
          <Route path="feature-influence" element={<FeatureInfluencePage />} />
          <Route path="explainability" element={<Navigate to="/feature-influence" replace />} />
          <Route path="ai-assistant" element={<AIAssistantPage />} />
          <Route path="alerts" element={<AlertsPage />} />
          <Route path="model-performance" element={<ModelPerformancePage />} />
          <Route path="methodology" element={<MethodologyPage />} />
          {/* Fallback to Overview */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
