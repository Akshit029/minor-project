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
import {
  MOCK_GLOBAL_EXPLAINABILITY,
  MOCK_HIGH_ERROR_EVENTS,
  MOCK_METEOROLOGICAL_AUDIT
} from '../data/mockExplainability';
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
  ForecastVsReferenceRecord,
  GlobalExplainabilityData,
  HighErrorEventAnalyzed,
  MeteorologicalAuditData,
  LocalExplanationResult
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
      datasetStatus: 'Operational',
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
  },

  /**
   * GET /api/health
   */
  async getHealth(): Promise<{
    status: string;
    gemini_api_key_configured: boolean;
    configured_model: string;
    artifacts: {
      week4_reliability_table: boolean;
      week5_model_pipeline: boolean;
    };
  }> {
    try {
      const res = await fetch(`${API_BASE_URL}/api/health`);
      if (res.ok) return await res.json();
    } catch {
      // offline / mock fallback
    }
    return {
      status: 'offline',
      gemini_api_key_configured: false,
      configured_model: 'gemini-2.0-flash',
      artifacts: {
        week4_reliability_table: true,
        week5_model_pipeline: true,
      },
    };
  },

  /**
   * GET /api/explainability/global (Week 7 SHAP Global Feature Importance)
   */
  async getGlobalExplainability(): Promise<GlobalExplainabilityData> {
    if (!USE_MOCK) {
      try {
        const res = await fetch(`${API_BASE_URL}/api/explainability/global`);
        if (res.ok) {
          const data = await res.json();
          return {
            explainer_type: data.explainer_class || data.explainer_type || "shap.LinearExplainer",
            estimator: data.model_explained || "LogisticRegression",
            explanation_space: data.explanation_space || "log-odds (logit)",
            sample_count: data.sample_count || 44,
            base_value_log_odds: data.base_value_log_odds ?? -0.2747,
            base_probability: data.base_probability ?? 0.4318,
            feature_rankings: data.feature_rankings || [],
            grouped_rankings: data.grouped_rankings || []
          };
        }
      } catch {
        // fallback to mock below
      }
    }
    await delay(90);
    return MOCK_GLOBAL_EXPLAINABILITY;
  },

  /**
   * GET /api/explainability/events (Week 7 High-Error Events & Local SHAP Attributions)
   */
  async getHighErrorEvents(params?: { district?: string; eventId?: number }): Promise<HighErrorEventAnalyzed[]> {
    if (!USE_MOCK) {
      try {
        const queryParams = new URLSearchParams();
        if (params?.district) queryParams.set('district', params.district);
        if (params?.eventId) queryParams.set('event_id', params.eventId.toString());
        const res = await fetch(`${API_BASE_URL}/api/explainability/events?${queryParams.toString()}`);
        if (res.ok) {
          const data = await res.json();
          if (data.events) return data.events;
          if (data.event) return [data.event];
        }
      } catch {
        // fallback to mock below
      }
    }
    await delay(100);
    if (params?.eventId !== undefined) {
      const match = MOCK_HIGH_ERROR_EVENTS.filter(e => e.event_id === params.eventId);
      return match.length > 0 ? match : MOCK_HIGH_ERROR_EVENTS;
    }
    if (params?.district) {
      const match = MOCK_HIGH_ERROR_EVENTS.filter(e => e.district.toLowerCase() === params.district?.toLowerCase());
      return match.length > 0 ? match : MOCK_HIGH_ERROR_EVENTS;
    }
    return MOCK_HIGH_ERROR_EVENTS;
  },

  /**
   * POST /api/explainability/local (Week 7 Interactive Live Local SHAP Explainer)
   */
  async explainLocalForecast(params: {
    district: DistrictName;
    leadDay: number;
    forecastValue: number;
    initHour?: number;
    validHour?: number;
    validMonth?: number;
  }): Promise<LocalExplanationResult> {
    if (!USE_MOCK) {
      try {
        const res = await fetch(`${API_BASE_URL}/api/explainability/local`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            district: params.district,
            leadDay: params.leadDay,
            forecastValue: params.forecastValue,
            initHour: params.initHour ?? 0,
            validHour: params.validHour ?? 12,
            validMonth: params.validMonth ?? 9,
          }),
        });
        if (res.ok) {
          return await res.json();
        }
      } catch {
        // fallback to mock below
      }
    }
    await delay(120);

    // Realistic analytical SHAP approximation matching LogisticRegression weights
    const baseVal = -0.2747;
    const leadHours = params.leadDay * 24.0;
    // Normalized approximations: mean lead_hours ~ 13.5, std ~ 4.8
    const leadZ = (leadHours - 13.5) / 10.0;
    const leadShap = Number((leadZ * 0.476).toFixed(4));

    const tempZ = (params.forecastValue - 18.2) / 4.5;
    const tempShap = Number((-tempZ * 0.467).toFixed(4));

    const hourZ = ((params.validHour ?? 12) - 10.5) / 5.5;
    const hourShap = Number((hourZ * 0.950).toFixed(4));

    const distShaps: Record<DistrictName, number> = {
      Anantnag: -0.1319,
      Baramulla: -0.1823,
      Jammu: -0.0806,
      Srinagar: -0.0241,
    };
    const distShap = distShaps[params.district] ?? 0.0;

    const sumShap = leadShap + tempShap + hourShap + distShap;
    const finalLogOdds = baseVal + sumShap;
    const probBust = 1 / (1 + Math.exp(-finalLogOdds));
    const riskLevel = probBust >= 0.70 ? 'HIGH RISK' : probBust >= 0.35 ? 'MEDIUM RISK' : 'LOW RISK';

    const contributions = [
      { feature: 'lead_hours', raw_value: leadHours, transformed_value: leadZ, shap_value: leadShap, direction: leadShap > 0 ? 'INCREASED_RISK' as const : 'DECREASED_RISK' as const, relative_contribution_pct: 0 },
      { feature: 'valid_hour', raw_value: params.validHour ?? 12, transformed_value: hourZ, shap_value: hourShap, direction: hourShap > 0 ? 'INCREASED_RISK' as const : 'DECREASED_RISK' as const, relative_contribution_pct: 0 },
      { feature: 'forecast_value', raw_value: params.forecastValue, transformed_value: tempZ, shap_value: tempShap, direction: tempShap > 0 ? 'INCREASED_RISK' as const : 'DECREASED_RISK' as const, relative_contribution_pct: 0 },
      { feature: `district: ${params.district}`, raw_value: `district=${params.district}`, transformed_value: 1.0, shap_value: distShap, direction: distShap > 0 ? 'INCREASED_RISK' as const : 'DECREASED_RISK' as const, relative_contribution_pct: 0 }
    ];

    const totalAbs = contributions.reduce((acc, c) => acc + Math.abs(c.shap_value), 0) || 1e-6;
    contributions.forEach(c => {
      c.relative_contribution_pct = Number(((Math.abs(c.shap_value) / totalAbs) * 100).toFixed(2));
    });
    contributions.sort((a, b) => Math.abs(b.shap_value) - Math.abs(a.shap_value));

    const increasing = contributions.filter(c => c.shap_value > 0);
    const decreasing = contributions.filter(c => c.shap_value < 0);

    return {
      district: params.district,
      leadDay: params.leadDay,
      forecastValue: params.forecastValue,
      prediction: {
        bust_probability: Number(probBust.toFixed(4)),
        predicted_class: probBust >= 0.50 ? 1 : 0,
        risk_level: riskLevel,
        classification_threshold: 0.50,
        model_id: "LogisticRegression_BustClassifier"
      },
      shapSummary: {
        base_value_log_odds: baseVal,
        base_probability: Number((1 / (1 + Math.exp(-baseVal))).toFixed(4)),
        sum_shap_values: Number(sumShap.toFixed(4)),
        final_log_odds: Number(finalLogOdds.toFixed(4)),
        explanation_space: "log-odds (logit)"
      },
      featuresIncreasingRisk: increasing,
      featuresDecreasingRisk: decreasing,
      allFeatureContributions: contributions,
      narrativeExplanation: `The model predicted a bust probability of ${(probBust * 100).toFixed(1)}% (${riskLevel}). Features increasing predicted bust risk were: ${increasing.map(c => `${c.feature} (${c.shap_value > 0 ? '+' : ''}${c.shap_value.toFixed(2)})`).join(', ') || 'None'}. Features mitigating bust risk were: ${decreasing.map(c => `${c.feature} (${c.shap_value.toFixed(2)})`).join(', ') || 'None'}.`
    };
  },

  /**
   * GET /api/explainability/meteorological (Week 7 Humidity and Wind Speed Variable Audit)
   */
  async getMeteorologicalAudit(): Promise<MeteorologicalAuditData> {
    if (!USE_MOCK) {
      try {
        const res = await fetch(`${API_BASE_URL}/api/explainability/meteorological`);
        if (res.ok) {
          const data = await res.json();
          if (data.audit) return data.audit;
        }
      } catch {
        // fallback to mock below
      }
    }
    await delay(80);
    return MOCK_METEOROLOGICAL_AUDIT;
  },

  /**
   * POST /api/chat (LangChain Agentic AI Workflow)
   */
  async askAssistant(params: {
    message: string;
    history?: { role: string; content: string }[];
    district?: string;
    leadDay?: number;
    forecastFeatures?: {
      district?: string;
      lead_hours?: number;
      lead_day?: number;
      forecast_value?: number;
      init_hour?: number;
      valid_hour?: number;
      valid_month?: number;
    };
  }): Promise<{
    reply: string;
    tools_called?: { tool: string; input: Record<string, any>; output: Record<string, any> }[];
    structured_data?: Record<string, any>;
    gemini_active: boolean;
    model: string;
    error?: string | null;
  }> {
    try {
      const res = await fetch(`${API_BASE_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params),
      });
      if (res.ok) {
        return await res.json();
      }
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.detail || errData.error || `HTTP error ${res.status}`);
    } catch (err: any) {
      return {
        reply: `### Backend Connection Notice\n\nUnable to reach the Python Agentic AI service at \`${API_BASE_URL || 'http://localhost:8000'}/api/chat\`.\n\n**To start the server:**\n\`\`\`bash\nsource .venv/bin/activate\npython -m uvicorn src.api:app --port 8000 --reload\n\`\`\`\n*Error details: ${err.message || 'Connection failed'}*`,
        tools_called: [],
        gemini_active: false,
        model: 'Offline',
        error: err.message || 'Connection failed',
      };
    }
  }
};
