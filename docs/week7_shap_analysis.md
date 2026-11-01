# Week 7: SHAP-based Feature Influence Analysis

**Project Title:** Spatiotemporal Reliability and Uncertainty Detection for Medium-Range Weather Forecasts  
**Focus Domain:** Jammu and Kashmir (Srinagar, Jammu, Anantnag, Baramulla)  
**Academic Context:** B.Tech Minor Project  
**Implementation Phase:** Week 7 (Explainable AI via SHapley Additive exPlanations)

---

## 1. What SHAP Is

**SHAP (SHapley Additive exPlanations)** is an axiomatic, game-theoretic approach to explain machine learning models developed by Lundberg and Lee (2017). It assigns each feature an importance value (a Shapley value) for a particular prediction by calculating the feature's marginal contribution across all possible feature subsets.

Mathematically, for an input $x$, the explanation model $g(x')$ is an additive linear function of binary feature attribution variables:

$$g(z') = \phi_0 + \sum_{j=1}^M \phi_j z'_j$$

where:
- $\phi_0 = \mathbb{E}[f(x)]$ is the base expected model prediction over the background dataset (the prior).
- $\phi_j \in \mathbb{R}$ is the Shapley attribution value for feature $j$.
- $z'_j \in \{0, 1\}$ indicates the presence or absence of feature $j$.

SHAP uniquely satisfies four fundamental axiomatic properties that no other attribution framework simultaneously fulfills:
1. **Efficiency / Local Accuracy:** $\sum_{j=0}^M \phi_j = f(x)$ — the sum of attributions exactly equals the difference between the model output and the expected base output.
2. **Missingness:** If a feature is absent or uninformative, its attribution is zero ($\phi_j = 0$).
3. **Consistency:** If a model changes so that the marginal contribution of a feature increases or stays the same regardless of other features, that feature's attribution cannot decrease.
4. **Anonymity / Symmetry:** If two features contribute identically to all possible coalitions, their Shapley values are equal.

---

## 2. Why SHAP Is Used in This Project

In operational meteorology and disaster management, machine learning models predicting "forecast busts" (extreme forecast breakdowns where error exceeds the 90th percentile) cannot operate as uninterpretable black boxes. Forecasters and decision-makers require transparent justification:

1. **Safety-Critical Decision Support:** Meteorologists must know *why* an incoming forecast is flagged with elevated bust risk before issuing severe weather advisories or reservoir release warnings.
2. **Terrain-Aware Diagnostics:** Jammu and Kashmir features severe orographic heterogeneity (ranging from the subtropical outer plains of Jammu at 327m to high Himalayan valley floors in Srinagar, Anantnag, and Baramulla above 1,580m). SHAP isolates whether terrain encoding or atmospheric variables are driving forecast uncertainty.
3. **Model Validation & Debugging:** Verifies that the model learns physically sensible atmospheric relationships (e.g. longer forecast horizons increasing uncertainty) rather than spurious statistical artifacts.
4. **Distinction from Raw Correlation:** Unlike classical feature correlation coefficients, SHAP accounts for non-linear interactions and conditional dependencies between predictors.

---

## 3. How SHAP Integrates with the Week 5 Model

### Pipeline Architecture

The Week 5 forecast-bust classifier (`outputs/week5/trained_model_pipeline.joblib`) is a scikit-learn `Pipeline` consisting of:
1. **Preprocessor (`ColumnTransformer`):**
   - Categorical transformer: `OneHotEncoder(handle_unknown='ignore', sparse_output=False)` applied to `['district']`.
   - Numerical transformer: `StandardScaler()` applied to `['lead_hours', 'lead_day', 'forecast_value', 'init_hour', 'valid_hour', 'valid_month']`.
2. **Estimator:**
   - `LogisticRegression(class_weight='balanced', max_iter=1000, random_state=42)`.

### Explainer Selection

Because the fitted classifier is a linear model, `src/explainability.py` selects **`shap.LinearExplainer`**:
- **Exact Analytical Solution:** For linear models, Shapley values can be calculated analytically without Monte Carlo sampling variance:
  $$\phi_j(x) = w_j (x_j - \mathbb{E}[x_j])$$
- **Zero Retraining Required:** The explainer hooks directly into the serialized Week 5 weights and training feature background without modifying or retraining the model artifact.
- **Log-Odds Explanation Space:** Explanations are evaluated in logit (log-odds) space:
  $$\text{logit}(P) = \phi_0 + \sum_{j=1}^{10} \phi_j$$
  $$\text{Probability of Bust } P = \sigma\left(\phi_0 + \sum_{j=1}^{10} \phi_j\right) = \frac{1}{1 + e^{-(\phi_0 + \sum \phi_j)}}$$
- **Feature Name Preservation:** Preprocessed features (`cat__district_Anantnag`, `num__lead_hours`, etc.) are cleanly mapped to human-readable names (`district: Anantnag`, `lead_hours`, `forecast_value`, `valid_hour`).

---

## 4. How High-Error Events Are Selected

High-error events are identified using **real ground-truth verification data** from the NOAA GFS versus ECMWF ERA5 comparison dataset (`outputs/week5/labeled_forecast_dataset.csv`):

1. **Error Definition:** Standard meteorological convention:
   $$\text{Error} = \text{Forecast (GFS)} - \text{Reference (ERA5)}$$
   $$\text{Absolute Error} = |\text{Forecast} - \text{Reference}|$$
2. **Ranking Criterion:** Events are ranked strictly by retrospective `absolute_error` descending.
3. **No Synthetic Data:** Events reflect verified historical forecasts for the September 2026 verification period across Jammu and Kashmir.

### Top Analyzed High-Error Events

| Event ID | District | Lead Time | Valid Time (UTC) | Forecast (°C) | ERA5 Ref (°C) | Actual Error (°C) | Empirical Threshold | Actual Bust? | Model $P(\text{Bust})$ | Top Risk-Increasing Driver | Top Mitigating Driver |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **21** | Baramulla | 15h (Day 1) | 2026-09-15 15:00 | 13.46 | 23.48 | **-10.02** | 8.35°C | **Yes (1)** | **67.4%** | `valid_hour` (+0.76) | `district: Baramulla` (-0.18) |
| **32** | Anantnag | 24h (Day 2) | 2026-09-16 00:00 | 10.98 | 19.98 | **-9.00** | 7.68°C | **Yes (1)** | **57.0%** | `lead_hours` (+1.04) | `valid_hour` (-0.98) |
| **36** | Anantnag | 27h (Day 2) | 2026-09-16 03:00 | 15.23 | 24.23 | **-9.00** | 7.68°C | **Yes (1)** | **66.0%** | `lead_hours` (+1.39) | `valid_hour` (-0.63) |
| **20** | Anantnag | 15h (Day 1) | 2026-09-15 15:00 | 15.36 | 24.23 | **-8.87** | 8.04°C | **Yes (1)** | **65.8%** | `valid_hour` (+0.76) | `district: Anantnag` (-0.13) |
| **33** | Baramulla | 24h (Day 2) | 2026-09-16 00:00 | 10.98 | 19.23 | **-8.25** | 7.68°C | **Yes (1)** | **55.4%** | `lead_hours` (+1.04) | `valid_hour` (-0.98) |

### Strict Scientific Distinction
- **Actual Retrospective Forecast Error:** Ground-truth difference between GFS operational forecast and ERA5 atmospheric reanalysis (e.g., $-10.02^\circ\text{C}$).
- **Prospective Predicted Bust Probability:** Machine-learning model's estimated risk ($67.4\%$) that the forecast will exceed the empirical 90th percentile threshold, evaluated **strictly from issuance features**.

---

## 5. Global versus Local Explanations

| Aspect | Global Explanation | Local Explanation |
| :--- | :--- | :--- |
| **Scope** | Aggregated across all 44 verification cases. | Evaluated for a single specific forecast issuance. |
| **Core Metric** | Mean Absolute SHAP: $\frac{1}{N} \sum_{i=1}^N \|\phi_{i, j}\|$ | Local attribution: $\phi_j$ (log-odds $\Delta\text{logit}$). |
| **Objective** | Identify which overall features govern model behavior. | Diagnose why a particular forecast was flagged as a bust. |
| **Visualization** | Global bar chart, Beeswarm summary plot. | Waterfall plot, Diverging horizontal contribution plot. |
| **Output File** | `outputs/week7/figures/shap_global_feature_importance.png` | `outputs/week7/figures/shap_waterfall_event_21_Baramulla_lead15h.png` |

---

## 6. Feature Contribution Interpretation

### Global Mean |SHAP| Rankings

| Rank | Feature | Mean \|SHAP\| | Relative Influence (%) | Dominant Direction | Physical / Atmospheric Meaning |
| :---: | :--- | :---: | :---: | :---: | :--- |
| **1** | `lead_hours` | 0.9458 | **39.53%** | Risk-Increasing for long lead | Atmospheric chaotic divergence and decay of initial condition predictability over forecast horizon. |
| **2** | `valid_hour` | 0.6879 | **28.75%** | Risk-Increasing for afternoon | Diurnal solar heating cycle; peak convective turbulence during 12:00–15:00 UTC. |
| **3** | `forecast_value` | 0.4449 | **18.60%** | Risk-Increasing for extreme cold | Extreme cool departures in elevated valley floors exhibit wider variance than moderate temperatures. |
| **4** | `district: Jammu` | 0.1209 | **5.05%** | Risk-Decreasing | Subtropical outer plains (327m) have simpler topography and lower baseline forecast error. |
| **5** | `district: Baramulla` | 0.0911 | **3.81%** | Risk-Increasing | Complex northern valley terrain subject to orographic sheltering. |
| **6** | `district: Anantnag` | 0.0659 | **2.76%** | Risk-Increasing | High-elevation southern valley head with frequent mountain-valley wind shifts. |
| **7** | `district: Srinagar` | 0.0361 | **1.51%** | Risk-Decreasing | Central bowl valley location with intermediate error profile. |
| **8–10** | `lead_day`, `init_hour`, `valid_month` | 0.0000 | **0.00%** | Neutral | Inactive/constant coefficients (`lead_hours` captured lead effects; cycle was constant 00 UTC). |

---

## 7. Humidity and Wind Speed Analysis

An explicit requirement of Week 7 was to document the influence of atmospheric humidity and wind speed on forecast uncertainty.

### Variable Audit Findings

A rigorous audit was performed across all datasets:
1. **NOAA GFS Forecast Datasets (`data/raw/gfs/`):** Grib2 messages contain `2t` (2m temperature), `aptmp` (apparent temperature), and `tp` (precipitation). Atmospheric moisture (`RH:2 m above ground`) and wind components (`UGRD`, `VGRD`) were **not retrieved** in the pilot index-filter byte-range downloads.
2. **ECMWF ERA5 Reanalysis Datasets (`data/raw/era5/`):** NetCDF variables contain `t2m` and `tp`. 10m wind speed (`10m_u_component_of_wind`, `10m_v_component_of_wind`) and relative humidity were **not requested** in the CDSAPI query.
3. **Week 5 Model Schema (`outputs/week5/model_metadata.json`):** The model strictly trains on 7 issuance features: `district`, `lead_hours`, `lead_day`, `forecast_value`, `init_hour`, `valid_hour`, `valid_month`.

### Audit Summary Table (`outputs/week7/meteorological_variable_audit.csv`)

| Variable | Units | In GFS Raw? | In ERA5 Raw? | In Week 5 Model? | Finding & Rationale |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Relative Humidity** | % | No | No | **No** | **ABSENT from local archive.** Not used in Week 5 model. Zero values fabricated. |
| **10m Wind Speed** | m/s | No | No | **No** | **ABSENT from local archive.** Not used in Week 5 model. Zero values fabricated. |
| **2m Temperature** | °C | Yes | Yes | **Yes** | **AVAILABLE and active.** Included as `forecast_value`. Primary predictand. |
| **Precipitation** | mm | Yes | Yes | **No** | **AVAILABLE but excluded.** Intentionally excluded to avoid accumulation interval mismatches. |

### Exploratory Meteorological Analysis of Available Data

Instead of fabricating unverified data, an exploratory analysis was conducted using the verified atmospheric variables present in the local archive:
1. **Forecast Horizon (Lead Hours):** Verification MAE increases with lead time from $4.85^\circ\text{C}$ at lead 0h to $8.12^\circ\text{C}$ at lead 27h ($r = +0.284$).
2. **Diurnal Solar Cycle:** Afternoon/evening valid hours (09:00–15:00 UTC) show elevated error ($\text{MAE} \approx 7.8^\circ\text{C}$–$8.2^\circ\text{C}$) due to planetary boundary layer heating and localized valley wind circulation.
3. **Temperature Magnitude:** Cooler forecasts exhibit higher absolute error ($r = -0.312$), reflecting GFS difficulties with nocturnal radiative cooling in snow-fed mountain basins.

> **Scientific Principle:** SHAP attributions represent mathematical contributions to the statistical model, not proof of atmospheric physical causation.

---

## 8. Limitations of the Analysis

1. **Archive Temporal Coverage:** Current verification data covers lead days 1 and 2 (NOAA GFS vs. ECMWF ERA5 September 2026 pilot period). Longer lead times (days 3–10) require historical multi-season GFS archive expansion.
2. **Atmospheric Moisture & Wind Absence:** As documented in the variable audit, humidity and wind speed are absent from the downloaded local archive. While their physical importance is acknowledged, they cannot be attributed by SHAP without expanding raw downloads.
3. **Linear Model Assumption:** Because Week 5 selected Logistic Regression as the best interpretable baseline, feature attributions operate strictly in logit space.

---

## 9. Commands to Execute Week 7

### Execute Week 7 Pipeline Stage
```bash
# Run Week 7 SHAP explainability directly
python src/explainability.py

# Or run via orchestrator stage filter
python src/run_pipeline.py --stage week7
```

### Run Test Suite
```bash
# Run dedicated Week 7 tests (18 tests)
pytest tests/test_week7_explainability.py -v

# Run full project test suite (66 tests)
pytest -v
```

### Run Backend API Server
```bash
python -m uvicorn src.api:app --host 0.0.0.0 --port 8000 --reload
```

### Build & Run Frontend Dashboard
```bash
cd frontend
npm run build
npm run dev
```

---

## 10. Generated Plots and Artifact Locations

All Week 7 outputs are stored in `outputs/week7/`:

```
outputs/week7/
├── figures/
│   ├── shap_global_feature_importance.png       # 300 DPI: Global mean |SHAP| bar chart
│   ├── shap_beeswarm_summary.png                # 300 DPI: SHAP beeswarm distribution plot
│   ├── shap_grouped_feature_importance.png      # 300 DPI: Grouped concept importance bar chart
│   ├── meteorological_error_relationships.png   # 300 DPI: Exploratory meteorological multi-panel
│   ├── shap_waterfall_event_21_Baramulla_lead15h.png
│   ├── shap_waterfall_event_32_Anantnag_lead24h.png
│   ├── shap_waterfall_event_36_Anantnag_lead27h.png
│   ├── shap_waterfall_event_20_Anantnag_lead15h.png
│   ├── shap_waterfall_event_33_Baramulla_lead24h.png
│   ├── shap_contribution_event_21.png
│   ├── shap_contribution_event_32.png
│   ├── shap_contribution_event_36.png
│   ├── shap_contribution_event_20.png
│   └── shap_contribution_event_33.png
├── global_feature_importance.csv                # Tabular feature rankings and statistics
├── high_error_events_analyzed.csv               # Top high-error events with positive/negative drivers
├── meteorological_variable_audit.csv            # Formal audit of atmospheric variables
└── shap_analysis_metadata.json                  # Complete master JSON metadata for API consumption
```

