# Implementation Checklist & Audit: Weeks 3, 4 & 5

## Repository Audit Summary
- **Domain**: Jammu & Kashmir (Lat 31.0°N–38.0°N, Lon 73.0°E–81.0°E), Districts: Srinagar, Jammu, Anantnag, Baramulla.
- **Data Schemas**:
  - `gfs_clean.csv`: `district`, `latitude`, `longitude`, `initialization_time`, `forecast_hour`, `valid_time`, `temperature_c`, `precipitation_mm`.
  - `era5_clean.csv`: `district`, `latitude`, `longitude`, `valid_time`, `temperature_c`, `precipitation_mm`.
- **Variables Audit**:
  - Temperature: Supported in both GFS and ERA5 in °C.
  - Precipitation: Present in GFS and ERA5. Accumulation semantics require scrutiny (hourly vs 3/6-hr accumulated).
  - Pressure: Surface pressure / mean sea level pressure is **absent** from the local ERA5 NetCDF and GFS downloaded variables. Variable availability check implemented; explicitly documented as unsupported by current dataset without fabricating values.
- **Python Environment**:
  - Python 3.13.2 in `.venv`.
  - Dependencies: numpy, pandas, xarray, scipy, matplotlib, seaborn, pyyaml, scikit-learn, joblib, pytest.
- **Existing Tests**: 10 tests in `test_preprocess.py`, `test_features.py`, `test_anomaly.py` - all passing.

---

## Phase Checklist

### Week 3: Forecast-Observation Error Analysis
- [x] Repository audit & variables availability check (Temperature supported, Precipitation accumulation verified, Pressure documented as absent).
- [ ] Implement enhanced matched validation dataset (`src/error_analysis.py` / `src/validate.py`):
  - Retain `district`, `initialization_time`, `valid_time`, `lead_hours`, `lead_day`, `variable`, `forecast_value`, `reference_value`, `error` (`forecast_value - reference_value`), `absolute_error`, `squared_error`, `bias`.
  - Normalization of timestamps, removal/flagging of invalid values, no silent zero-filling.
- [ ] Baseline error metrics for lead days 1–10:
  - MAE, RMSE, Bias, sample_count, median absolute error, std of error.
  - Lead-day aggregation convention (Day 1: 0-23h or 24-47h clearly documented).
- [ ] Temperature bias correction:
  - Mean-bias correction (`corrected_forecast = forecast_value - training_bias`).
  - Learned strictly from historical training split, evaluated on held-out split.
  - District-specific with fallback hierarchy to regional.
  - Minimum sample threshold.
- [ ] Week 3 visualizations (`src/visualize_week3.py`):
  - MAE vs lead day, RMSE vs lead day, Bias vs lead day.
  - District-wise error distributions (boxplots).
  - District-wise absolute error distributions.
  - Before vs after bias-correction comparison.
  - Forecast vs ERA5 scatterplots with 1:1 line.
- [ ] Week 3 output artifacts & report:
  - `outputs/week3/matched_validation_dataset.csv`
  - `outputs/week3/lead_day_metrics.csv`
  - `outputs/week3/district_metrics.csv`
  - `outputs/week3/bias_correction_params.csv`
  - `outputs/week3/bias_correction_eval.csv`
  - `outputs/week3/data_matching_summary.csv`
  - `outputs/week3/reports/week3_error_analysis.md`

### Week 4: Spatiotemporal Modelling for Reliability Scoring
- [ ] Dedicated reliability module (`src/reliability.py`):
  - Mathematical formulation:
    - $normalized\_error = MAE / error\_scale$
    - $E = \sum(w_i \cdot normalized\_error_i) / \sum w_i$
    - $R_{error} = \exp(-E)$
    - Confidence factor $C = n / (n + k)$
    - Reliability score $R = R_{error} \cdot C \in [0, 1]$
  - Clearly designated as an empirical reliability index.
  - Insufficient sample handling (unknown / NaN, not zero).
- [ ] Temporal and spatial leakage prevention:
  - Chronological sorting: estimate on historical training, evaluate on held-out.
  - Independent case counting.
- [ ] Spatiotemporal variation:
  - District, lead day, variable, district × lead day, seasonal where applicable.
  - Documented fallback hierarchy.
- [ ] Sensitivity analysis:
  - Score vs lead day.
  - Sensitivity to error tolerance scale and parameter $k$.
  - District × lead-day heatmap.
- [ ] Week 4 visualizations & reports (`src/visualize_week4.py`):
  - Reliability vs lead day, district comparison, heatmap, sensitivity curves.
  - `outputs/week4/reliability_table.csv`
  - `outputs/week4/sensitivity_analysis.csv`
  - `outputs/week4/reports/week4_reliability_report.md`

### Week 5: Machine-Learning Forecast-Bust Model
- [ ] Label generation module (`src/forecast_bust.py`):
  - Empirical upper quantile threshold (e.g. 90th percentile) computed strictly on training set.
  - Bust = 1 if $|error| > threshold$, 0 otherwise.
- [ ] Feature engineering (Strictly Leakage-Free):
  - Only features available at forecast initialization / issuance time:
    - `forecast_hour` / `lead_day`, `district` (one-hot/ordinal encoded), initialization month/hour, forecast values, forecast rolling/daily features.
  - Strictly excluded: ERA5 reference, signed error, absolute error, bust labels, future reference data.
- [ ] Baseline Classifier Training:
  - Chronological split: 70% Train, 15% Validation, 15% Test.
  - Logistic Regression (interpretable) & Random Forest (nonlinear).
  - Preprocessing (StandardScaler, etc.) fit on training set only.
- [ ] Comprehensive Evaluation:
  - Precision, Recall, F1, Average Precision, Confusion Matrix, Precision-Recall Curve.
  - Saved model pipeline (`joblib`) and metadata JSON.
  - Reusable inference prediction function with input schema validation.
- [ ] Week 5 visualizations & reports (`src/visualize_week5.py`):
  - Precision-recall curve, confusion matrix heatmap, feature importance.
  - `outputs/week5/labeled_dataset.csv`
  - `outputs/week5/model_metadata.json`
  - `outputs/week5/classification_metrics.csv`
  - `outputs/week5/reports/week5_bust_model_report.md`

### Integration, Config, Testing & Documentation
- [ ] Extend `config.yaml` with all Week 3–5 parameters.
- [ ] Update `src/run_pipeline.py` to seamlessly orchestrate all stages (1 through 14) and support running individual stages.
- [ ] Add comprehensive unit tests in `tests/test_week3.py`, `tests/test_week4.py`, `tests/test_week5.py`.
- [ ] Update `README.md` and generate comprehensive research summary report.
- [ ] Full pipeline execution and test verification.
