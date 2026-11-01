import type {
  GlobalExplainabilityData,
  HighErrorEventAnalyzed,
  MeteorologicalAuditData
} from '../types/weather';

export const MOCK_GLOBAL_EXPLAINABILITY: GlobalExplainabilityData = {
  explainer_type: "shap.LinearExplainer",
  estimator: "LogisticRegression",
  explanation_space: "log-odds (logit)",
  sample_count: 44,
  base_value_log_odds: -0.2747,
  base_probability: 0.4318,
  feature_rankings: [
    {
      feature: "lead_hours",
      raw_feature: "num__lead_hours",
      mean_abs_shap: 0.9458,
      mean_shap: -0.0,
      std_shap: 1.0967,
      min_shap: -1.7341,
      max_shap: 1.7341,
      relative_importance_pct: 39.53,
      pct_positive_impact: 45.5,
      dominant_direction: "RISK_DECREASING"
    },
    {
      feature: "valid_hour",
      raw_feature: "num__valid_hour",
      mean_abs_shap: 0.6879,
      mean_shap: 0.0,
      std_shap: 0.7939,
      min_shap: -0.9774,
      max_shap: 1.4503,
      relative_importance_pct: 28.75,
      pct_positive_impact: 45.5,
      dominant_direction: "RISK_INCREASING"
    },
    {
      feature: "forecast_value",
      raw_feature: "num__forecast_value",
      mean_abs_shap: 0.4449,
      mean_shap: 0.0,
      std_shap: 0.4961,
      min_shap: -1.0142,
      max_shap: 0.6698,
      relative_importance_pct: 18.60,
      pct_positive_impact: 47.7,
      dominant_direction: "RISK_INCREASING"
    },
    {
      feature: "district: Jammu",
      raw_feature: "cat__district_Jammu",
      mean_abs_shap: 0.1209,
      mean_shap: -0.0,
      std_shap: 0.1396,
      min_shap: -0.0806,
      max_shap: 0.2418,
      relative_importance_pct: 5.05,
      pct_positive_impact: 25.0,
      dominant_direction: "RISK_DECREASING"
    },
    {
      feature: "district: Baramulla",
      raw_feature: "cat__district_Baramulla",
      mean_abs_shap: 0.0911,
      mean_shap: 0.0,
      std_shap: 0.1052,
      min_shap: -0.1823,
      max_shap: 0.0608,
      relative_importance_pct: 3.81,
      pct_positive_impact: 75.0,
      dominant_direction: "RISK_INCREASING"
    },
    {
      feature: "district: Anantnag",
      raw_feature: "cat__district_Anantnag",
      mean_abs_shap: 0.0659,
      mean_shap: 0.0,
      std_shap: 0.0761,
      min_shap: -0.1319,
      max_shap: 0.0440,
      relative_importance_pct: 2.76,
      pct_positive_impact: 75.0,
      dominant_direction: "RISK_INCREASING"
    },
    {
      feature: "district: Srinagar",
      raw_feature: "cat__district_Srinagar",
      mean_abs_shap: 0.0361,
      mean_shap: 0.0,
      std_shap: 0.0417,
      min_shap: -0.0241,
      max_shap: 0.0723,
      relative_importance_pct: 1.51,
      pct_positive_impact: 25.0,
      dominant_direction: "RISK_DECREASING"
    },
    {
      feature: "lead_day",
      raw_feature: "num__lead_day",
      mean_abs_shap: 0.0,
      mean_shap: 0.0,
      std_shap: 0.0,
      min_shap: 0.0,
      max_shap: 0.0,
      relative_importance_pct: 0.0,
      pct_positive_impact: 0.0,
      dominant_direction: "RISK_DECREASING"
    },
    {
      feature: "init_hour",
      raw_feature: "num__init_hour",
      mean_abs_shap: 0.0,
      mean_shap: 0.0,
      std_shap: 0.0,
      min_shap: 0.0,
      max_shap: 0.0,
      relative_importance_pct: 0.0,
      pct_positive_impact: 0.0,
      dominant_direction: "RISK_DECREASING"
    },
    {
      feature: "valid_month",
      raw_feature: "num__valid_month",
      mean_abs_shap: 0.0,
      mean_shap: 0.0,
      std_shap: 0.0,
      min_shap: 0.0,
      max_shap: 0.0,
      relative_importance_pct: 0.0,
      pct_positive_impact: 0.0,
      dominant_direction: "RISK_DECREASING"
    }
  ],
  grouped_rankings: [
    {
      concept: "lead_time (forecast horizon)",
      mean_abs_shap: 0.9458,
      relative_importance_pct: 39.53
    },
    {
      concept: "diurnal_cycle (timing)",
      mean_abs_shap: 0.6879,
      relative_importance_pct: 28.75
    },
    {
      concept: "forecast_temperature (°C)",
      mean_abs_shap: 0.4449,
      relative_importance_pct: 18.60
    },
    {
      concept: "district (geographic terrain)",
      mean_abs_shap: 0.3140,
      relative_importance_pct: 13.12
    },
    {
      concept: "seasonality (month)",
      mean_abs_shap: 0.0,
      relative_importance_pct: 0.0
    }
  ]
};

export const MOCK_HIGH_ERROR_EVENTS: HighErrorEventAnalyzed[] = [
  {
    event_id: 21,
    district: "Baramulla",
    lead_hours: 15.0,
    lead_day: 1.0,
    initialization_time: "2026-09-15 00:00:00",
    valid_time: "2026-09-15 15:00:00",
    forecast_value_c: 13.46,
    reference_value_c: 23.48,
    actual_error_c: -10.02,
    actual_absolute_error_c: 10.02,
    empirical_bust_threshold_c: 8.35,
    actual_is_bust: 1,
    model_prediction: {
      bust_probability: 0.6741,
      predicted_class: 1,
      risk_level: "MEDIUM RISK",
      classification_threshold: 0.50,
      model_id: "LogisticRegression_BustClassifier"
    },
    shap_summary: {
      base_value_log_odds: -0.2747,
      base_probability: 0.4318,
      sum_shap_values: 1.0016,
      final_log_odds: 0.7269,
      explanation_space: "log-odds (logit)"
    },
    top_positive_features: [
      {
        feature: "valid_hour",
        raw_value: 15.0,
        transformed_value: 0.797,
        shap_value: 0.7567,
        direction: "INCREASED_RISK",
        relative_contribution_pct: 48.86
      },
      {
        feature: "forecast_value",
        raw_value: 13.46,
        transformed_value: -1.043,
        shap_value: 0.4877,
        direction: "INCREASED_RISK",
        relative_contribution_pct: 31.49
      },
      {
        feature: "district: Anantnag",
        raw_value: "district=Baramulla",
        transformed_value: 0.0,
        shap_value: 0.0440,
        direction: "INCREASED_RISK",
        relative_contribution_pct: 2.84
      }
    ],
    top_negative_features: [
      {
        feature: "district: Baramulla",
        raw_value: "district=Baramulla",
        transformed_value: 1.0,
        shap_value: -0.1823,
        direction: "DECREASED_RISK",
        relative_contribution_pct: 11.77
      },
      {
        feature: "district: Jammu",
        raw_value: "district=Baramulla",
        transformed_value: 0.0,
        shap_value: -0.0806,
        direction: "DECREASED_RISK",
        relative_contribution_pct: 5.20
      }
    ],
    all_contributions: [
      { feature: "valid_hour", raw_value: 15.0, transformed_value: 0.797, shap_value: 0.7567, direction: "INCREASED_RISK", relative_contribution_pct: 48.86 },
      { feature: "forecast_value", raw_value: 13.46, transformed_value: -1.043, shap_value: 0.4877, direction: "INCREASED_RISK", relative_contribution_pct: 31.49 },
      { feature: "district: Baramulla", raw_value: "district=Baramulla", transformed_value: 1.0, shap_value: -0.1823, direction: "DECREASED_RISK", relative_contribution_pct: 11.77 },
      { feature: "district: Jammu", raw_value: "district=Baramulla", transformed_value: 0.0, shap_value: -0.0806, direction: "DECREASED_RISK", relative_contribution_pct: 5.20 },
      { feature: "district: Anantnag", raw_value: "district=Baramulla", transformed_value: 0.0, shap_value: 0.0440, direction: "INCREASED_RISK", relative_contribution_pct: 2.84 }
    ],
    narrative: "The model predicted a forecast bust probability of 67.4% (MEDIUM RISK). Features that increased the predicted bust risk were: valid_hour (+0.76), forecast_value (+0.49), district: Anantnag (+0.04). Features that mitigated/reduced the predicted bust risk were: district: Baramulla (-0.18), district: Jammu (-0.08).",
    scientific_distinction_note: "Actual Forecast Error = Forecast - ERA5 = -10.02°C (magnitude 10.02°C). Predicted Bust Probability = 67.4%. Actual error reflects retrospective ground-truth verification; predicted bust risk reflects prospective model classification based strictly on issuance features."
  },
  {
    event_id: 32,
    district: "Anantnag",
    lead_hours: 24.0,
    lead_day: 2.0,
    initialization_time: "2026-09-15 00:00:00",
    valid_time: "2026-09-16 00:00:00",
    forecast_value_c: 10.98,
    reference_value_c: 19.98,
    actual_error_c: -9.00,
    actual_absolute_error_c: 9.00,
    empirical_bust_threshold_c: 7.68,
    actual_is_bust: 1,
    model_prediction: {
      bust_probability: 0.5701,
      predicted_class: 1,
      risk_level: "MEDIUM RISK",
      classification_threshold: 0.50,
      model_id: "LogisticRegression_BustClassifier"
    },
    shap_summary: {
      base_value_log_odds: -0.2747,
      base_probability: 0.4318,
      sum_shap_values: 0.5568,
      final_log_odds: 0.2821,
      explanation_space: "log-odds (logit)"
    },
    top_positive_features: [
      {
        feature: "lead_hours",
        raw_value: 24.0,
        transformed_value: 2.184,
        shap_value: 1.0404,
        direction: "INCREASED_RISK",
        relative_contribution_pct: 35.63
      },
      {
        feature: "forecast_value",
        raw_value: 10.98,
        transformed_value: -1.398,
        shap_value: 0.6698,
        direction: "INCREASED_RISK",
        relative_contribution_pct: 22.94
      },
      {
        feature: "district: Baramulla",
        raw_value: "district=Anantnag",
        transformed_value: 0.0,
        shap_value: 0.0608,
        direction: "INCREASED_RISK",
        relative_contribution_pct: 2.08
      }
    ],
    top_negative_features: [
      {
        feature: "valid_hour",
        raw_value: 0.0,
        transformed_value: -1.498,
        shap_value: -0.9774,
        direction: "DECREASED_RISK",
        relative_contribution_pct: 33.47
      },
      {
        feature: "district: Anantnag",
        raw_value: "district=Anantnag",
        transformed_value: 1.0,
        shap_value: -0.1319,
        direction: "DECREASED_RISK",
        relative_contribution_pct: 4.52
      }
    ],
    all_contributions: [
      { feature: "lead_hours", raw_value: 24.0, transformed_value: 2.184, shap_value: 1.0404, direction: "INCREASED_RISK", relative_contribution_pct: 35.63 },
      { feature: "valid_hour", raw_value: 0.0, transformed_value: -1.498, shap_value: -0.9774, direction: "DECREASED_RISK", relative_contribution_pct: 33.47 },
      { feature: "forecast_value", raw_value: 10.98, transformed_value: -1.398, shap_value: 0.6698, direction: "INCREASED_RISK", relative_contribution_pct: 22.94 },
      { feature: "district: Anantnag", raw_value: "district=Anantnag", transformed_value: 1.0, shap_value: -0.1319, direction: "DECREASED_RISK", relative_contribution_pct: 4.52 },
      { feature: "district: Jammu", raw_value: "district=Anantnag", transformed_value: 0.0, shap_value: -0.0806, direction: "DECREASED_RISK", relative_contribution_pct: 2.76 }
    ],
    narrative: "The model predicted a forecast bust probability of 57.0% (MEDIUM RISK). Features that increased the predicted bust risk were: lead_hours (+1.04), forecast_value (+0.67), district: Baramulla (+0.06). Features that mitigated/reduced the predicted bust risk were: valid_hour (-0.98), district: Anantnag (-0.13), district: Jammu (-0.08).",
    scientific_distinction_note: "Actual Forecast Error = Forecast - ERA5 = -9.00°C (magnitude 9.00°C). Predicted Bust Probability = 57.0%. Actual error reflects retrospective ground-truth verification; predicted bust risk reflects prospective model classification based strictly on issuance features."
  },
  {
    event_id: 36,
    district: "Anantnag",
    lead_hours: 27.0,
    lead_day: 2.0,
    initialization_time: "2026-09-15 00:00:00",
    valid_time: "2026-09-16 03:00:00",
    forecast_value_c: 15.23,
    reference_value_c: 24.23,
    actual_error_c: -9.00,
    actual_absolute_error_c: 9.00,
    empirical_bust_threshold_c: 7.68,
    actual_is_bust: 1,
    model_prediction: {
      bust_probability: 0.6602,
      predicted_class: 1,
      risk_level: "MEDIUM RISK",
      classification_threshold: 0.50,
      model_id: "LogisticRegression_BustClassifier"
    },
    shap_summary: {
      base_value_log_odds: -0.2747,
      base_probability: 0.4318,
      sum_shap_values: 0.9388,
      final_log_odds: 0.6641,
      explanation_space: "log-odds (logit)"
    },
    top_positive_features: [
      {
        feature: "lead_hours",
        raw_value: 27.0,
        transformed_value: 2.643,
        shap_value: 1.3872,
        direction: "INCREASED_RISK",
        relative_contribution_pct: 51.52
      },
      {
        feature: "forecast_value",
        raw_value: 15.23,
        transformed_value: -0.790,
        shap_value: 0.3578,
        direction: "INCREASED_RISK",
        relative_contribution_pct: 13.29
      },
      {
        feature: "district: Baramulla",
        raw_value: "district=Anantnag",
        transformed_value: 0.0,
        shap_value: 0.0608,
        direction: "INCREASED_RISK",
        relative_contribution_pct: 2.26
      }
    ],
    top_negative_features: [
      {
        feature: "valid_hour",
        raw_value: 3.0,
        transformed_value: -1.039,
        shap_value: -0.6306,
        direction: "DECREASED_RISK",
        relative_contribution_pct: 23.42
      },
      {
        feature: "district: Anantnag",
        raw_value: "district=Anantnag",
        transformed_value: 1.0,
        shap_value: -0.1319,
        direction: "DECREASED_RISK",
        relative_contribution_pct: 4.90
      }
    ],
    all_contributions: [
      { feature: "lead_hours", raw_value: 27.0, transformed_value: 2.643, shap_value: 1.3872, direction: "INCREASED_RISK", relative_contribution_pct: 51.52 },
      { feature: "valid_hour", raw_value: 3.0, transformed_value: -1.039, shap_value: -0.6306, direction: "DECREASED_RISK", relative_contribution_pct: 23.42 },
      { feature: "forecast_value", raw_value: 15.23, transformed_value: -0.790, shap_value: 0.3578, direction: "INCREASED_RISK", relative_contribution_pct: 13.29 },
      { feature: "district: Anantnag", raw_value: "district=Anantnag", transformed_value: 1.0, shap_value: -0.1319, direction: "DECREASED_RISK", relative_contribution_pct: 4.90 },
      { feature: "district: Jammu", raw_value: "district=Anantnag", transformed_value: 0.0, shap_value: -0.0806, direction: "DECREASED_RISK", relative_contribution_pct: 2.99 }
    ],
    narrative: "The model predicted a forecast bust probability of 66.0% (MEDIUM RISK). Features that increased the predicted bust risk were: lead_hours (+1.39), forecast_value (+0.36), district: Baramulla (+0.06). Features that mitigated/reduced the predicted bust risk were: valid_hour (-0.63), district: Anantnag (-0.13), district: Jammu (-0.08).",
    scientific_distinction_note: "Actual Forecast Error = Forecast - ERA5 = -9.00°C (magnitude 9.00°C). Predicted Bust Probability = 66.0%. Actual error reflects retrospective ground-truth verification; predicted bust risk reflects prospective model classification based strictly on issuance features."
  }
];

export const MOCK_METEOROLOGICAL_AUDIT: MeteorologicalAuditData = {
  audit_date: "2026-11-01",
  study_region: "Jammu and Kashmir",
  variables_audited: [
    {
      variable: "relative_humidity",
      display_name: "Atmospheric Relative Humidity",
      units: "%",
      in_gfs_archive: false,
      in_era5_archive: false,
      in_processed_data: false,
      in_week5_model: false,
      required_source_key: "GFS: 'RH:2 m above ground' | ERA5: '2m_dewpoint_temperature' / 'relative_humidity'",
      audit_finding: "ABSENT from downloaded local dataset archive. Not used in Week 5 model.",
      scientific_rationale: "NOAA GFS index-filtered downloads and ECMWF CDSAPI queries in Weeks 1-2 requested strictly 2m temperature and precipitation to conserve network bandwidth for the pilot domain. Atmospheric moisture was not retrieved in raw Grib2/NetCDF files."
    },
    {
      variable: "wind_speed",
      display_name: "10-Metre Wind Speed",
      units: "m/s",
      in_gfs_archive: false,
      in_era5_archive: false,
      in_processed_data: false,
      in_week5_model: false,
      required_source_key: "GFS: 'UGRD:10 m above ground', 'VGRD:10 m above ground' | ERA5: '10m_u_component_of_wind', '10m_v_component_of_wind'",
      audit_finding: "ABSENT from downloaded local dataset archive. Not used in Week 5 model.",
      scientific_rationale: "Zonal (u) and meridional (v) 10m wind components were not included in the original GFS/ERA5 download pipelines. Documented as absent without fabricating synthetic observations."
    },
    {
      variable: "temperature_c",
      display_name: "2-Metre Air Temperature",
      units: "°C",
      in_gfs_archive: true,
      in_era5_archive: true,
      in_processed_data: true,
      in_week5_model: true,
      required_source_key: "GFS: 'TMP:2 m above ground' | ERA5: '2m_temperature'",
      audit_finding: "AVAILABLE and actively included in model as 'forecast_value'.",
      scientific_rationale: "Primary medium-range meteorological predictand verified across all 4 districts."
    },
    {
      variable: "precipitation_mm",
      display_name: "Surface Precipitation",
      units: "mm",
      in_gfs_archive: true,
      in_era5_archive: true,
      in_processed_data: true,
      in_week5_model: false,
      required_source_key: "GFS: 'APCP:surface' | ERA5: 'total_precipitation'",
      audit_finding: "AVAILABLE in processed datasets, but intentionally excluded from Week 5 model input schema.",
      scientific_rationale: "Excluded from Week 5 forecast-bust classifier to maintain single-variable focus on temperature bust events and avoid accumulation interval mismatches (3-hour vs 1-hour)."
    }
  ],
  humidity_available: false,
  wind_speed_available: false,
  exploratory_meteorological_analysis: {
    lead_time_relationship: {
      description: "Verification MAE increases monotonically with forecast horizon.",
      lead_hours: [0, 3, 6, 9, 12, 15, 18, 21, 24, 27],
      mean_abs_error: [4.85, 4.92, 5.10, 5.35, 5.82, 6.45, 6.90, 7.30, 7.75, 8.12],
      correlation: 0.284
    },
    temperature_relationship: {
      description: "Cooler forecasts (mountainous locations) exhibit higher absolute error.",
      bins: ["Cool (<15°C)", "Mild (15-22°C)", "Warm (>22°C)"],
      mean_abs_error: [7.21, 5.48, 3.82],
      correlation: -0.312
    },
    diurnal_relationship: {
      description: "Afternoon/evening forecasts (09:00 - 15:00 UTC) show higher error due to solar heating and convection.",
      valid_hours: [0, 3, 6, 9, 12, 15, 18, 21],
      mean_abs_error: [5.2, 5.4, 6.1, 7.4, 7.8, 8.2, 6.3, 5.6]
    }
  },
  scientific_disclaimer: "SHAP values measure empirical feature attributions within the trained mathematical model, not physical atmospheric causality. Humidity and wind speed were not included in the model because they were not present in the downloaded local dataset archive."
};

