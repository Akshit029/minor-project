import type { 
  ModelMetricsData, 
  FeatureImportanceItem, 
  PRCurvePoint, 
  ForecastBustPredictionResult 
} from '../types/weather';

export const MOCK_MODEL_METRICS: Record<'logisticRegression' | 'randomForest', ModelMetricsData> = {
  logisticRegression: {
    modelId: 'LogisticRegression_BustClassifier',
    modelName: 'Logistic Regression (Class-Weighted)',
    precision: 0.684,
    recall: 0.825,
    f1Score: 0.748,
    averagePrecision: 0.712,
    confusionMatrix: [
      [142, 38], // TN: 142, FP: 38
      [14, 66],  // FN: 14,  TP: 66
    ],
    trainingCases: 420,
    validationCases: 90,
    testCases: 90,
    bustQuantile: 0.90,
    classificationThreshold: 0.50,
  },
  randomForest: {
    modelId: 'RandomForest_BustClassifier',
    modelName: 'Random Forest Classifier (100 Trees)',
    precision: 0.782,
    recall: 0.885,
    f1Score: 0.830,
    averagePrecision: 0.846,
    confusionMatrix: [
      [162, 18], // TN: 162, FP: 18
      [9, 71],   // FN: 9,   TP: 71
    ],
    trainingCases: 420,
    validationCases: 90,
    testCases: 90,
    bustQuantile: 0.90,
    classificationThreshold: 0.50,
  },
};

/**
 * Feature Importance for Random Forest Bust Classifier
 * Features strictly extracted at issuance time (strictly leakage-free)
 */
export const MOCK_FEATURE_IMPORTANCE: FeatureImportanceItem[] = [
  {
    feature: 'lead_hours',
    importance: 0.324,
    label: 'Forecast Lead Hours (lead_hours)',
    description: 'Direct forecast lookahead duration from 24h to 240h; primary driver of forecast error dispersion.',
  },
  {
    feature: 'lead_day',
    importance: 0.218,
    label: 'Forecast Lead Day (lead_day)',
    description: 'Diurnal aggregation step reflecting multi-day atmospheric instability accumulation.',
  },
  {
    feature: 'forecast_value',
    importance: 0.165,
    label: 'NOAA GFS Forecast Value',
    description: 'Issued temperature forecast magnitude (°C); extreme forecasts exhibit higher variance.',
  },
  {
    feature: 'district',
    importance: 0.128,
    label: 'District Spatial One-Hot (district)',
    description: 'Orographic terrain category distinguishing high-valley basins (Anantnag, Srinagar) from foothills (Jammu).',
  },
  {
    feature: 'valid_month',
    importance: 0.076,
    label: 'Valid Month (Seasonal Regime)',
    description: 'Captures seasonal transitions (monsoon withdrawal vs western disturbance onset).',
  },
  {
    feature: 'valid_hour',
    importance: 0.052,
    label: 'Target Valid Hour (UTC)',
    description: 'Diurnal cycle phase (00, 06, 12, 18 UTC) corresponding to peak solar heating vs nocturnal cooling.',
  },
  {
    feature: 'init_hour',
    importance: 0.037,
    label: 'Model Cycle Run (init_hour)',
    description: 'Operational NOAA GFS assimilation cycle timing (00, 06, 12, 18 UTC).',
  },
];

/**
 * Precision-Recall Curve Comparison
 */
export const MOCK_PR_CURVE: PRCurvePoint[] = [
  { recall: 0.0, logisticRegression: 1.00, randomForest: 1.00 },
  { recall: 0.1, logisticRegression: 0.94, randomForest: 0.98 },
  { recall: 0.2, logisticRegression: 0.91, randomForest: 0.96 },
  { recall: 0.3, logisticRegression: 0.88, randomForest: 0.94 },
  { recall: 0.4, logisticRegression: 0.85, randomForest: 0.91 },
  { recall: 0.5, logisticRegression: 0.81, randomForest: 0.89 },
  { recall: 0.6, logisticRegression: 0.77, randomForest: 0.87 },
  { recall: 0.7, logisticRegression: 0.71, randomForest: 0.84 },
  { recall: 0.8, logisticRegression: 0.65, randomForest: 0.80 },
  { recall: 0.85, logisticRegression: 0.59, randomForest: 0.76 },
  { recall: 0.9, logisticRegression: 0.48, randomForest: 0.68 },
  { recall: 0.95, logisticRegression: 0.38, randomForest: 0.54 },
  { recall: 1.0, logisticRegression: 0.29, randomForest: 0.35 },
];

/**
 * Forecast Bust Predictions Table Data
 */
export const MOCK_BUST_PREDICTIONS: ForecastBustPredictionResult[] = [
  {
    district: 'Anantnag',
    leadHours: 144,
    leadDay: 6,
    forecastValue: 27.5,
    initHour: 0,
    validHour: 12,
    validMonth: 10,
    bustProbability: 72,
    predictedClass: 'BUST',
    riskLevel: 'HIGH RISK',
    modelUsed: 'Random Forest',
    computedTimestamp: '2026-10-14 12:00 UTC',
  },
  {
    district: 'Baramulla',
    leadHours: 168,
    leadDay: 7,
    forecastValue: 27.6,
    initHour: 0,
    validHour: 12,
    validMonth: 10,
    bustProbability: 64,
    predictedClass: 'BUST',
    riskLevel: 'HIGH RISK',
    modelUsed: 'Random Forest',
    computedTimestamp: '2026-10-14 12:00 UTC',
  },
  {
    district: 'Srinagar',
    leadHours: 144,
    leadDay: 6,
    forecastValue: 28.9,
    initHour: 0,
    validHour: 12,
    validMonth: 10,
    bustProbability: 45,
    predictedClass: 'NORMAL',
    riskLevel: 'MEDIUM RISK',
    modelUsed: 'Random Forest',
    computedTimestamp: '2026-10-14 12:00 UTC',
  },
  {
    district: 'Baramulla',
    leadHours: 120,
    leadDay: 5,
    forecastValue: 25.4,
    initHour: 0,
    validHour: 12,
    validMonth: 10,
    bustProbability: 42,
    predictedClass: 'NORMAL',
    riskLevel: 'MEDIUM RISK',
    modelUsed: 'Random Forest',
    computedTimestamp: '2026-10-14 12:00 UTC',
  },
  {
    district: 'Srinagar',
    leadHours: 120,
    leadDay: 5,
    forecastValue: 18.5,
    initHour: 0,
    validHour: 12,
    validMonth: 10,
    bustProbability: 31,
    predictedClass: 'NORMAL',
    riskLevel: 'LOW RISK',
    modelUsed: 'Random Forest',
    computedTimestamp: '2026-10-14 12:00 UTC',
  },
  {
    district: 'Anantnag',
    leadHours: 96,
    leadDay: 4,
    forecastValue: 21.0,
    initHour: 0,
    validHour: 12,
    validMonth: 10,
    bustProbability: 28,
    predictedClass: 'NORMAL',
    riskLevel: 'LOW RISK',
    modelUsed: 'Random Forest',
    computedTimestamp: '2026-10-14 12:00 UTC',
  },
  {
    district: 'Jammu',
    leadHours: 168,
    leadDay: 7,
    forecastValue: 34.6,
    initHour: 0,
    validHour: 12,
    validMonth: 10,
    bustProbability: 25,
    predictedClass: 'NORMAL',
    riskLevel: 'LOW RISK',
    modelUsed: 'Random Forest',
    computedTimestamp: '2026-10-14 12:00 UTC',
  },
  {
    district: 'Jammu',
    leadHours: 120,
    leadDay: 5,
    forecastValue: 28.2,
    initHour: 0,
    validHour: 12,
    validMonth: 10,
    bustProbability: 12,
    predictedClass: 'NORMAL',
    riskLevel: 'LOW RISK',
    modelUsed: 'Random Forest',
    computedTimestamp: '2026-10-14 12:00 UTC',
  },
];
