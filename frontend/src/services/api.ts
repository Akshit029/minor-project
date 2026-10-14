import { APP_CONFIG } from '../data/config';
import { MOCK_DISTRICTS, MOCK_FORECAST_VS_REFERENCE } from '../data/mockForecasts';
import { MOCK_LEAD_DAY_METRICS, HEATMAP_DATA, MOCK_SENSITIVITY_DATA } from '../data/mockReliability';
import { MOCK_ALERTS } from '../data/mockAlerts';
import { 
  MOCK_MODEL_METRICS, 
  MOCK_FEATURE_IMPORTANCE, 
  MOCK_PR_CURVE, 
  MOCK_BUST_PREDICTIONS 
} from '../data/mockModelMetrics';
import type { 
  DistrictInfo, 
  DistrictName, 
  OverviewKPIs, 
  LeadDayMetrics, 
  AlertItem, 
  ModelMetricsData, 
  FeatureImportanceItem, 
  PRCurvePoint, 
  ForecastBustPredictionResult,
  ForecastVsReferenceRecord
} from '../types/weather';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';
const USE_MOCK = !API_BASE_URL || import.meta.env.VITE_USE_MOCK !== 'false';

// Helper for realistic smooth async mock latency
const delay = (ms: number = 80) => new Promise((resolve) => setTimeout(resolve, ms));

export interface OverviewApiResponse {
  kpis: OverviewKPIs;
  districts: DistrictInfo[];
  leadDayMetrics: LeadDayMetrics[];
  recentAlerts: AlertItem[];
  currentLeadDay: number;
}

export interface DistrictAnalysisApiResponse {
  district: DistrictInfo;
  leadDayMetrics: { leadDay: number; mae: number; rmse: number; bias: number; reliability: number }[];
  forecastVsReference: ForecastVsReferenceRecord[];
}

export interface ModelPerformanceApiResponse {
  models: Record<'logisticRegression' | 'randomForest', ModelMetricsData>;
  featureImportance: FeatureImportanceItem[];
  prCurve: PRCurvePoint[];
}

export const WeatherApi = {
  /**
   * GET /api/overview
   */
  async getOverview(): Promise<OverviewApiResponse> {
    if (!USE_MOCK) {
      const res = await fetch(`${API_BASE_URL}/api/overview`);
      if (!res.ok) throw new Error(`Overview fetch failed: ${res.statusText}`);
      return res.json();
    }
    await delay(100);

    const kpis: OverviewKPIs = {
      overallReliability: 0.78,
      overallReliabilityLabel: 'Empirical Reliability Index',
      forecastBustRisk: 23,
      forecastBustRiskLabel: 'Current estimated probability',
      bestPerformingDistrict: 'Jammu',
      highestUncertaintyDistrict: 'Srinagar',
      forecastLead: 'Day 5',
      datasetStatus: 'Demo Data',
      lastUpdated: '2026-10-14 12:00 UTC',
      activeAlertCount: MOCK_ALERTS.filter(a => a.status === 'Active').length,
      forecastHorizon: APP_CONFIG.forecastHorizon,
      regionName: APP_CONFIG.region.name,
      modelStatus: APP_CONFIG.modelStatus,
    };

    return {
      kpis,
      districts: Object.values(MOCK_DISTRICTS),
      leadDayMetrics: MOCK_LEAD_DAY_METRICS,
      recentAlerts: MOCK_ALERTS.slice(0, 4),
      currentLeadDay: 5,
    };
  },

  /**
   * GET /api/forecast
   */
  async getForecast(): Promise<DistrictInfo[]> {
    if (!USE_MOCK) {
      const res = await fetch(`${API_BASE_URL}/api/forecast`);
      if (!res.ok) throw new Error(`Forecast fetch failed: ${res.statusText}`);
      return res.json();
    }
    await delay(70);
    return Object.values(MOCK_DISTRICTS);
  },

  /**
   * GET /api/reliability
   */
  async getReliability(): Promise<{
    leadDayMetrics: LeadDayMetrics[];
    heatmap: typeof HEATMAP_DATA;
    sensitivity: typeof MOCK_SENSITIVITY_DATA;
  }> {
    if (!USE_MOCK) {
      const res = await fetch(`${API_BASE_URL}/api/reliability`);
      if (!res.ok) throw new Error(`Reliability fetch failed: ${res.statusText}`);
      return res.json();
    }
    await delay(100);
    return {
      leadDayMetrics: MOCK_LEAD_DAY_METRICS,
      heatmap: HEATMAP_DATA,
      sensitivity: MOCK_SENSITIVITY_DATA,
    };
  },

  /**
   * GET /api/district/:name
   */
  async getDistrict(name: DistrictName): Promise<DistrictAnalysisApiResponse> {
    if (!USE_MOCK) {
      const res = await fetch(`${API_BASE_URL}/api/district/${name}`);
      if (!res.ok) throw new Error(`District fetch failed: ${res.statusText}`);
      return res.json();
    }
    await delay(90);
    const district = MOCK_DISTRICTS[name] || MOCK_DISTRICTS['Srinagar'];

    const districtLeadDayMetrics = MOCK_LEAD_DAY_METRICS.map(ld => ({
      leadDay: ld.leadDay,
      mae: ld.districtScores[name]?.mae ?? ld.regionalMAE,
      rmse: ld.districtScores[name]?.rmse ?? ld.regionalRMSE,
      bias: ld.districtScores[name]?.bias ?? ld.regionalBias,
      reliability: ld.districtScores[name]?.reliability ?? ld.regionalReliability,
    }));

    const districtFvr = MOCK_FORECAST_VS_REFERENCE.filter(r => r.district === name);

    return {
      district,
      leadDayMetrics: districtLeadDayMetrics,
      forecastVsReference: districtFvr.length > 0 ? districtFvr : MOCK_FORECAST_VS_REFERENCE.slice(0, 10),
    };
  },

  /**
   * GET /api/alerts
   */
  async getAlerts(): Promise<AlertItem[]> {
    if (!USE_MOCK) {
      const res = await fetch(`${API_BASE_URL}/api/alerts`);
      if (!res.ok) throw new Error(`Alerts fetch failed: ${res.statusText}`);
      return res.json();
    }
    await delay(60);
    return MOCK_ALERTS;
  },

  /**
   * GET /api/model-performance
   */
  async getModelPerformance(): Promise<ModelPerformanceApiResponse> {
    if (!USE_MOCK) {
      const res = await fetch(`${API_BASE_URL}/api/model-performance`);
      if (!res.ok) throw new Error(`Model performance fetch failed: ${res.statusText}`);
      return res.json();
    }
    await delay(110);
    return {
      models: MOCK_MODEL_METRICS,
      featureImportance: MOCK_FEATURE_IMPORTANCE,
      prCurve: MOCK_PR_CURVE,
    };
  },

  /**
   * GET /api/bust-prediction
   */
  async getBustPredictions(): Promise<ForecastBustPredictionResult[]> {
    if (!USE_MOCK) {
      const res = await fetch(`${API_BASE_URL}/api/bust-prediction`);
      if (!res.ok) throw new Error(`Bust prediction fetch failed: ${res.statusText}`);
      return res.json();
    }
    await delay(80);
    return MOCK_BUST_PREDICTIONS;
  },

  /**
   * POST /api/bust-predict (Live interactive inference)
   */
  async predictBust(params: {
    district: DistrictName;
    leadDay: number;
    forecastValue: number;
    initHour: number;
    validHour: number;
    validMonth: number;
  }): Promise<ForecastBustPredictionResult> {
    if (!USE_MOCK) {
      const res = await fetch(`${API_BASE_URL}/api/bust-predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params),
      });
      if (!res.ok) throw new Error(`Prediction inference failed: ${res.statusText}`);
      return res.json();
    }
    await delay(150);

    // Realistic inference calculation simulating Random Forest & Logistic Regression
    // Error increases with leadDay, extreme terrain (Anantnag > Baramulla > Srinagar > Jammu)
    const terrainPenalty = {
      Anantnag: 22,
      Baramulla: 16,
      Srinagar: 12,
      Jammu: 4,
    }[params.district];

    const leadFactor = Math.pow(params.leadDay / 10, 1.4) * 65;
    const extremeFactor = Math.abs(params.forecastValue - 22) * 1.5;
    const rawProb = Math.min(96, Math.max(3, Math.round(terrainPenalty + leadFactor + extremeFactor)));

    const riskLevel = rawProb >= 70 ? 'HIGH RISK' : rawProb >= 35 ? 'MEDIUM RISK' : 'LOW RISK';
    const predictedClass = rawProb >= 50 ? 'BUST' : 'NORMAL';

    return {
      district: params.district,
      leadHours: params.leadDay * 24,
      leadDay: params.leadDay,
      forecastValue: params.forecastValue,
      initHour: params.initHour,
      validHour: params.validHour,
      validMonth: params.validMonth,
      bustProbability: rawProb,
      predictedClass,
      riskLevel,
      modelUsed: 'Random Forest',
      computedTimestamp: new Date().toISOString().replace('T', ' ').substring(0, 19) + ' UTC',
    };
  }
};
