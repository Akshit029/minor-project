import type { LeadDayMetrics, DistrictName } from '../types/weather';

/**
 * Lead Day 1 to 10 Spatiotemporal Verification & Reliability Metrics
 * Based on the mathematical formulation from Week 4:
 * R = R_error * C, where R_error = exp(-MAE / error_scale) and C = n / (n + k)
 */
export const MOCK_LEAD_DAY_METRICS: LeadDayMetrics[] = [
  {
    leadDay: 1,
    leadHours: 24,
    regionalReliability: 0.88,
    regionalMAE: 2.15,
    regionalRMSE: 2.78,
    regionalBias: 0.42,
    regionalBustProb: 4,
    districtScores: {
      Srinagar: { reliability: 0.86, mae: 2.30, rmse: 2.91, bias: 0.52, bustProbability: 5, provenance: 'district_lead_day' },
      Jammu: { reliability: 0.94, mae: 1.45, rmse: 1.88, bias: 0.20, bustProbability: 2, provenance: 'district_lead_day' },
      Anantnag: { reliability: 0.82, mae: 2.65, rmse: 3.30, bias: 0.61, bustProbability: 6, provenance: 'district_lead_day' },
      Baramulla: { reliability: 0.85, mae: 2.20, rmse: 2.85, bias: 0.35, bustProbability: 4, provenance: 'district_lead_day' },
    },
  },
  {
    leadDay: 2,
    leadHours: 48,
    regionalReliability: 0.82,
    regionalMAE: 2.82,
    regionalRMSE: 3.52,
    regionalBias: 0.65,
    regionalBustProb: 7,
    districtScores: {
      Srinagar: { reliability: 0.80, mae: 2.95, rmse: 3.70, bias: 0.74, bustProbability: 8, provenance: 'district_lead_day' },
      Jammu: { reliability: 0.91, mae: 1.85, rmse: 2.35, bias: 0.35, bustProbability: 4, provenance: 'district_lead_day' },
      Anantnag: { reliability: 0.74, mae: 3.40, rmse: 4.15, bias: 0.88, bustProbability: 11, provenance: 'district_lead_day' },
      Baramulla: { reliability: 0.79, mae: 3.10, rmse: 3.82, bias: 0.62, bustProbability: 9, provenance: 'district_lead_day' },
    },
  },
  {
    leadDay: 3,
    leadHours: 72,
    regionalReliability: 0.76,
    regionalMAE: 3.50,
    regionalRMSE: 4.28,
    regionalBias: 0.92,
    regionalBustProb: 12,
    districtScores: {
      Srinagar: { reliability: 0.73, mae: 3.72, rmse: 4.51, bias: 1.05, bustProbability: 14, provenance: 'district_lead_day' },
      Jammu: { reliability: 0.87, mae: 2.25, rmse: 2.82, bias: 0.48, bustProbability: 6, provenance: 'district_lead_day' },
      Anantnag: { reliability: 0.67, mae: 4.25, rmse: 5.12, bias: 1.25, bustProbability: 18, provenance: 'district_lead_day' },
      Baramulla: { reliability: 0.72, mae: 3.80, rmse: 4.60, bias: 0.90, bustProbability: 15, provenance: 'district_lead_day' },
    },
  },
  {
    leadDay: 4,
    leadHours: 96,
    regionalReliability: 0.71,
    regionalMAE: 4.18,
    regionalRMSE: 5.05,
    regionalBias: 1.20,
    regionalBustProb: 18,
    districtScores: {
      Srinagar: { reliability: 0.68, mae: 4.35, rmse: 5.24, bias: 1.30, bustProbability: 22, provenance: 'district_lead_day' },
      Jammu: { reliability: 0.84, mae: 2.70, rmse: 3.35, bias: 0.60, bustProbability: 9, provenance: 'district_lead_day' },
      Anantnag: { reliability: 0.58, mae: 5.10, rmse: 6.12, bias: 1.65, bustProbability: 28, provenance: 'district_lead_day' },
      Baramulla: { reliability: 0.65, mae: 4.55, rmse: 5.45, bias: 1.25, bustProbability: 20, provenance: 'district_lead_day' },
    },
  },
  {
    leadDay: 5,
    leadHours: 120,
    regionalReliability: 0.64,
    regionalMAE: 4.82,
    regionalRMSE: 5.80,
    regionalBias: 1.50,
    regionalBustProb: 26,
    districtScores: {
      Srinagar: { reliability: 0.64, mae: 4.83, rmse: 5.62, bias: 1.42, bustProbability: 31, provenance: 'district_lead_day' },
      Jammu: { reliability: 0.84, mae: 2.91, rmse: 3.48, bias: 0.65, bustProbability: 12, provenance: 'district_lead_day' },
      Anantnag: { reliability: 0.48, mae: 6.42, rmse: 7.31, bias: 2.85, bustProbability: 68, provenance: 'district_lead_day' },
      Baramulla: { reliability: 0.58, mae: 5.12, rmse: 6.04, bias: 1.78, bustProbability: 42, provenance: 'district_lead_day' },
    },
  },
  {
    leadDay: 6,
    leadHours: 144,
    regionalReliability: 0.54,
    regionalMAE: 5.60,
    regionalRMSE: 6.72,
    regionalBias: 1.85,
    regionalBustProb: 38,
    districtScores: {
      Srinagar: { reliability: 0.49, mae: 5.90, rmse: 7.02, bias: 2.10, bustProbability: 45, provenance: 'district_lead_day' },
      Jammu: { reliability: 0.74, mae: 3.65, rmse: 4.40, bias: 0.95, bustProbability: 18, provenance: 'district_lead_day' },
      Anantnag: { reliability: 0.38, mae: 7.20, rmse: 8.35, bias: 3.20, bustProbability: 72, provenance: 'district_lead_day' },
      Baramulla: { reliability: 0.48, mae: 6.10, rmse: 7.15, bias: 2.05, bustProbability: 51, provenance: 'district_lead_day' },
    },
  },
  {
    leadDay: 7,
    leadHours: 168,
    regionalReliability: 0.46,
    regionalMAE: 6.35,
    regionalRMSE: 7.60,
    regionalBias: 2.15,
    regionalBustProb: 52,
    districtScores: {
      Srinagar: { reliability: 0.41, mae: 6.75, rmse: 7.98, bias: 2.45, bustProbability: 59, provenance: 'district_lead_day' },
      Jammu: { reliability: 0.66, mae: 4.40, rmse: 5.30, bias: 1.25, bustProbability: 25, provenance: 'district_lead_day' },
      Anantnag: { reliability: 0.29, mae: 8.05, rmse: 9.30, bias: 3.65, bustProbability: 81, provenance: 'district_lead_day' },
      Baramulla: { reliability: 0.39, mae: 6.95, rmse: 8.10, bias: 2.40, bustProbability: 64, provenance: 'district_lead_day' },
    },
  },
  {
    leadDay: 8,
    leadHours: 192,
    regionalReliability: 0.38,
    regionalMAE: 7.10,
    regionalRMSE: 8.45,
    regionalBias: 2.40,
    regionalBustProb: 64,
    districtScores: {
      Srinagar: { reliability: 0.33, mae: 7.50, rmse: 8.85, bias: 2.75, bustProbability: 71, provenance: 'regional_fallback' },
      Jammu: { reliability: 0.58, mae: 5.15, rmse: 6.15, bias: 1.55, bustProbability: 34, provenance: 'regional_fallback' },
      Anantnag: { reliability: 0.22, mae: 8.80, rmse: 10.15, bias: 4.05, bustProbability: 88, provenance: 'regional_fallback' },
      Baramulla: { reliability: 0.31, mae: 7.75, rmse: 9.00, bias: 2.70, bustProbability: 74, provenance: 'regional_fallback' },
    },
  },
  {
    leadDay: 9,
    leadHours: 216,
    regionalReliability: 0.31,
    regionalMAE: 7.82,
    regionalRMSE: 9.25,
    regionalBias: 2.65,
    regionalBustProb: 73,
    districtScores: {
      Srinagar: { reliability: 0.27, mae: 8.20, rmse: 9.60, bias: 3.05, bustProbability: 79, provenance: 'regional_fallback' },
      Jammu: { reliability: 0.50, mae: 5.90, rmse: 7.00, bias: 1.85, bustProbability: 44, provenance: 'regional_fallback' },
      Anantnag: { reliability: 0.16, mae: 9.50, rmse: 10.90, bias: 4.45, bustProbability: 92, provenance: 'regional_fallback' },
      Baramulla: { reliability: 0.25, mae: 8.45, rmse: 9.75, bias: 3.00, bustProbability: 82, provenance: 'regional_fallback' },
    },
  },
  {
    leadDay: 10,
    leadHours: 240,
    regionalReliability: 0.25,
    regionalMAE: 8.45,
    regionalRMSE: 9.95,
    regionalBias: 2.85,
    regionalBustProb: 81,
    districtScores: {
      Srinagar: { reliability: 0.21, mae: 8.85, rmse: 10.30, bias: 3.30, bustProbability: 85, provenance: 'regional_fallback' },
      Jammu: { reliability: 0.43, mae: 6.60, rmse: 7.80, bias: 2.10, bustProbability: 53, provenance: 'regional_fallback' },
      Anantnag: { reliability: 0.12, mae: 10.10, rmse: 11.55, bias: 4.80, bustProbability: 95, provenance: 'regional_fallback' },
      Baramulla: { reliability: 0.19, mae: 9.10, rmse: 10.45, bias: 3.25, bustProbability: 87, provenance: 'regional_fallback' },
    },
  },
];

/**
 * Reliability Heatmap Matrix (Districts as rows, Days 1-10 as columns)
 */
export interface HeatmapCell {
  district: DistrictName;
  leadDay: number;
  score: number;
  mae: number;
  provenance: string;
}

export const HEATMAP_DATA: HeatmapCell[] = [];
const DISTRICT_LIST: DistrictName[] = ['Srinagar', 'Jammu', 'Anantnag', 'Baramulla'];

DISTRICT_LIST.forEach((dist) => {
  MOCK_LEAD_DAY_METRICS.forEach((ld) => {
    HEATMAP_DATA.push({
      district: dist,
      leadDay: ld.leadDay,
      score: ld.districtScores[dist].reliability,
      mae: ld.districtScores[dist].mae,
      provenance: ld.districtScores[dist].provenance,
    });
  });
});

/**
 * Sensitivity Analysis Mock Data (Week 4 formulation)
 * Evaluates how Empirical Reliability Score R varies with Error Scale S (1.0 to 5.0) and smoothing parameter k (5, 10, 20)
 */
export const MOCK_SENSITIVITY_DATA = [
  { scale: 1.0, k5: 0.05, k10: 0.03, k20: 0.02 },
  { scale: 1.5, k5: 0.18, k10: 0.12, k20: 0.07 },
  { scale: 2.0, k5: 0.35, k10: 0.24, k20: 0.15 }, // Baseline engineering scale
  { scale: 2.5, k5: 0.50, k10: 0.36, k20: 0.23 },
  { scale: 3.0, k5: 0.62, k10: 0.46, k20: 0.31 },
  { scale: 3.5, k5: 0.70, k10: 0.54, k20: 0.38 },
  { scale: 4.0, k5: 0.76, k10: 0.60, k20: 0.44 },
  { scale: 5.0, k5: 0.83, k10: 0.69, k20: 0.53 },
];
