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

export interface ShapFeatureRanking {
  feature: string;
  raw_feature: string;
  mean_abs_shap: number;
  mean_shap: number;
  std_shap: number;
  min_shap: number;
  max_shap: number;
  relative_importance_pct: number;
  pct_positive_impact: number;
  dominant_direction: 'RISK_INCREASING' | 'RISK_DECREASING';
}

export interface GroupedConceptRanking {
  concept: string;
  mean_abs_shap: number;
  relative_importance_pct: number;
}

export interface GlobalExplainabilityData {
  explainer_type: string;
  estimator: string;
  explanation_space: string;
  sample_count: number;
  base_value_log_odds: number;
  base_probability: number;
  feature_rankings: ShapFeatureRanking[];
  grouped_rankings: GroupedConceptRanking[];
}

export interface LocalFeatureContribution {
  feature: string;
  raw_value: any;
  transformed_value: number;
  shap_value: number;
  direction: 'INCREASED_RISK' | 'DECREASED_RISK';
  relative_contribution_pct: number;
}

export interface HighErrorEventAnalyzed {
  event_id: number;
  district: DistrictName;
  lead_hours: number;
  lead_day: number;
  initialization_time: string;
  valid_time: string;
  forecast_value_c: number;
  reference_value_c: number | null;
  actual_error_c: number;
  actual_absolute_error_c: number;
  empirical_bust_threshold_c: number | null;
  actual_is_bust: number;
  model_prediction: {
    bust_probability: number;
    predicted_class: number;
    risk_level: string;
    classification_threshold: number;
    model_id: string;
  };
  shap_summary: {
    base_value_log_odds: number;
    base_probability: number;
    sum_shap_values: number;
    final_log_odds: number;
    explanation_space: string;
  };
  top_positive_features: LocalFeatureContribution[];
  top_negative_features: LocalFeatureContribution[];
  all_contributions: LocalFeatureContribution[];
  narrative: string;
  scientific_distinction_note: string;
}

export interface MeteorologicalAuditItem {
  variable: string;
  display_name: string;
  units: string;
  in_gfs_archive: boolean;
  in_era5_archive: boolean;
  in_processed_data: boolean;
  in_week5_model: boolean;
  required_source_key: string;
  audit_finding: string;
  scientific_rationale: string;
}

export interface MeteorologicalAuditData {
  audit_date: string;
  study_region: string;
  variables_audited: MeteorologicalAuditItem[];
  humidity_available: boolean;
  wind_speed_available: boolean;
  exploratory_meteorological_analysis: {
    lead_time_relationship?: {
      description: string;
      lead_hours: number[];
      mean_abs_error: number[];
      correlation: number;
    };
    temperature_relationship?: {
      description: string;
      bins: string[];
      mean_abs_error: number[];
      correlation: number;
    };
    diurnal_relationship?: {
      description: string;
      valid_hours: number[];
      mean_abs_error: number[];
    };
  };
  scientific_disclaimer: string;
}

export interface LocalExplanationResult {
  district: DistrictName;
  leadDay: number;
  forecastValue: number;
  prediction: {
    bust_probability: number;
    predicted_class: number;
    risk_level: string;
    classification_threshold: number;
    model_id: string;
  };
  shapSummary: {
    base_value_log_odds: number;
    base_probability: number;
    sum_shap_values: number;
    final_log_odds: number;
    explanation_space: string;
  };
  featuresIncreasingRisk: LocalFeatureContribution[];
  featuresDecreasingRisk: LocalFeatureContribution[];
  allFeatureContributions: LocalFeatureContribution[];
  narrativeExplanation: string;
}
