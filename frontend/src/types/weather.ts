export type DistrictName = 'Srinagar' | 'Jammu' | 'Anantnag' | 'Baramulla';

export type ReliabilityLevel = 'high' | 'moderate' | 'low' | 'uncertain';

export type UncertaintyLevel = 'Low' | 'Moderate' | 'High';

export type BustRiskLevel = 'LOW RISK' | 'MEDIUM RISK' | 'HIGH RISK';

export type AlertSeverity = 'low' | 'moderate' | 'high' | 'critical';

export type AlertType = 
  | 'high_uncertainty' 
  | 'low_reliability' 
  | 'potential_forecast_bust' 
  | 'data_quality_warning';

export interface DistrictInfo {
  id: DistrictName;
  name: DistrictName;
  lat: number;
  lon: number;
  elevationMeters: number;
  terrainDescription: string;
  currentForecast: {
    temperature: number; // °C
    rainfall: number; // mm
    relativeHumidity: number; // %
    windSpeed: number; // km/h
    weatherCondition: string;
    validTime: string;
    initCycle: string;
    leadDay: number;
    leadHours: number;
  };
  reliability: number; // 0 - 1
  uncertainty: UncertaintyLevel;
  bustProbability: number; // 0 - 100%
  mae: number;
  rmse: number;
  bias: number;
  lastUpdated: string;
}

export interface LeadDayMetrics {
  leadDay: number;
  leadHours: number;
  regionalReliability: number;
  regionalMAE: number;
  regionalRMSE: number;
  regionalBias: number;
  regionalBustProb: number;
  districtScores: Record<DistrictName, {
    reliability: number;
    mae: number;
    rmse: number;
    bias: number;
    bustProbability: number;
    provenance: 'district_lead_day' | 'regional_fallback';
  }>;
}

export interface AlertItem {
  id: string;
  severity: AlertSeverity;
  district: DistrictName | 'Regional';
  leadDay: number;
  alertType: AlertType;
  reliability: number;
  bustProbability: number;
  title: string;
  explanation: string;
  timestamp: string;
  status: 'Active' | 'Investigating' | 'Resolved';
  variable: 'temperature_c' | 'precipitation_mm';
  forecastValue: number;
  thresholdValue?: number;
}

export interface ModelMetricsData {
  modelId: string;
  modelName: string;
  precision: number;
  recall: number;
  f1Score: number;
  averagePrecision: number;
  confusionMatrix: [[number, number], [number, number]]; // [[TN, FP], [FN, TP]]
  trainingCases: number;
  validationCases: number;
  testCases: number;
  bustQuantile: number;
  classificationThreshold: number;
}

export interface FeatureImportanceItem {
  feature: string;
  importance: number;
  label: string;
  description: string;
}

export interface PRCurvePoint {
  recall: number;
  logisticRegression: number;
  randomForest: number;
}

export interface ForecastVsReferenceRecord {
  id: string;
  date: string;
  validTime: string;
  leadDay: number;
  district: DistrictName;
  gfsForecast: number;       // NOAA GFS Forecast
  era5Reference: number;     // ECMWF ERA5 Reference
  biasCorrectedForecast: number;
  signedError: number;       // Forecast - Reference
  absoluteError: number;
  isBust: boolean;
}

export interface OverviewKPIs {
  overallReliability: number;
  overallReliabilityLabel: string;
  forecastBustRisk: number;
  forecastBustRiskLabel: string;
  bestPerformingDistrict: DistrictName;
  highestUncertaintyDistrict: DistrictName;
  forecastLead: string;
  datasetStatus: string;
  lastUpdated: string;
  activeAlertCount: number;
  forecastHorizon: string;
  regionName: string;
  modelStatus: string;
}

export interface ForecastBustPredictionResult {
  district: DistrictName;
  leadHours: number;
  leadDay: number;
  forecastValue: number;
  initHour: number;
  validHour: number;
  validMonth: number;
  bustProbability: number;
  predictedClass: 'BUST' | 'NORMAL';
  riskLevel: BustRiskLevel;
  modelUsed: 'Logistic Regression' | 'Random Forest';
  computedTimestamp: string;
}
