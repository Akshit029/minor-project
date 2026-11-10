# Spatiotemporal Reliability and Uncertainty Detection for Medium-Range Weather Forecasts

**Academic Context:** B.Tech Minor Project  
**Target Domain:** Jammu & Kashmir (Bounding Box: Lat 31.0°N–38.0°N, Lon 73.0°E–81.0°E)  
**Representative Study Districts:** Srinagar, Jammu, Anantnag, Baramulla  
**Python Environment:** Python 3.11+ (Evaluated & verified on Python 3.13 Apple Silicon macOS / Linux / Windows)

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [End-to-End System Architecture (Weeks 1–5)](#2-end-to-end-system-architecture-weeks-15)
3. [Data Sources & Variable Availability](#3-data-sources--variable-availability)
   - [NOAA Global Forecast System (GFS)](#noaa-global-forecast-system-gfs)
   - [ECMWF ERA5 Atmospheric Reanalysis](#ecmwf-era5-atmospheric-reanalysis)
   - [Variable Availability & Physical Semantics Check](#variable-availability--physical-semantics-check)
4. [Installation & Dependencies](#4-installation--dependencies)
5. [Configuration (`config.yaml`)](#5-configuration-configyaml)
6. [Pipeline Execution Guide](#6-pipeline-execution-guide)
   - [Running the Complete Pipeline](#running-the-complete-pipeline)
   - [Running Individual Pipeline Stages](#running-individual-pipeline-stages)
   - [Running Fast Test Mode](#running-fast-test-mode)
   - [Running on Existing Local Data Without Redownloading](#running-on-existing-local-data-without-redownloading)
7. [Week-by-Week Implementation & Scientific Methodology](#7-week-by-week-implementation--scientific-methodology)
   - [Weeks 1 & 2: Ingestion, Quality Checks, Features & Anomaly Screening](#weeks-1--2-ingestion-quality-checks-features--anomaly-screening)
   - [Week 3: Matched Error Analysis & Leakage-Safe Bias Correction](#week-3-matched-error-analysis--leakage-safe-bias-correction)
   - [Week 4: Spatiotemporal Modelling for Reliability Scoring](#week-4-spatiotemporal-modelling-for-reliability-scoring)
   - [Week 5: Machine-Learning Forecast-Bust Classifier](#week-5-machine-learning-forecast-bust-classifier)
   - [Week 6: Agentic AI Workflow Integration & Dashboard Assistant](#week-6-agentic-ai-workflow-integration--dashboard-assistant)
   - [Week 7: SHAP Feature Influence & Explanatory AI Analysis](#week-7-shap-feature-influence--explanatory-ai-analysis)
   - [Week 8: Regional Reliability Maps & Automated Alerting System](#week-8-regional-reliability-maps--automated-alerting-system)
   - [Week 9: Unified Pipeline Orchestration, Docker & Deployment](#week-9-unified-pipeline-orchestration-docker--deployment)
8. [Docker Containerization Guide](#8-docker-containerization-guide)
9. [Cloud Deployment Guide](#9-cloud-deployment-guide)
10. [Interpretation of Metrics & Scores](#10-interpretation-of-metrics--scores)
11. [College Review Demonstration Guide](#11-college-review-demonstration-guide)
12. [Automated Testing Suite (91 Tests)](#12-automated-testing-suite-91-tests)
13. [Directory Structure & Saved Artifacts](#13-directory-structure--saved-artifacts)
14. [Scientific Assumptions & Operational Limitations](#14-scientific-assumptions--operational-limitations)
15. [Verification Checklist](#15-verification-checklist)

---

## 1. Project Overview

Numerical Weather Prediction (NWP) models exhibit varying degrees of reliability and uncertainty across complex, high-altitude terrain. Mountainous regions such as Jammu & Kashmir introduce significant microclimatic variation, complex orographic precipitation, and localized temperature lapse rates that pose unique challenges to medium-range global models.

This research project investigates the spatiotemporal reliability, forecast skill decay, and statistical extreme uncertainty of medium-range weather forecasts over Jammu & Kashmir using operational **NOAA GFS** forecasts verified against **ECMWF ERA5** reanalysis:
- **Weeks 1 & 2:** Data acquisition, spatial-temporal preprocessing, physical bounds verification, multi-scale rolling temporal features, dual-method anomaly screening (Z-score & Robust MAD), and baseline error validation.
- **Week 3:** Matched forecast-reference error dataset creation, lead-day error metrics (lead days 1–10), district-wise error distributions, and historical mean-bias correction with district-to-regional fallback.
- **Week 4:** Mathematical formulation of an empirical spatiotemporal reliability score $R \in [0, 1]$, sample confidence factor $C$, temporal leakage avoidance, and sensitivity analysis across error tolerance scales and smoothing parameters.
- **Week 5:** Formulation of empirical training-derived forecast-bust labels, strictly leakage-free feature engineering from forecast issuance parameters, chronological train/validation/test evaluation, baseline Logistic Regression and Random Forest classifiers, precision-recall analysis, model serialization (`.joblib`), and a production inference API.
- **Week 6:** Orchestration of scientific verification and machine-learning modules through an **Agentic AI workflow** using LangChain and Google Gemini with deterministic offline fallback.
- **Week 7:** Integration of the **SHAP (SHapley Additive exPlanations)** library with the Week 5 model pipeline. Exact analytical log-odds feature attributions, high-error event analysis, domain concept grouping, and meteorological data integrity governance.
- **Week 8:** **Interactive Regional Reliability Maps & Automated Alerting System:** GeoJSON-based interactive spatial choropleths and markers across J&K, automated forecast-bust alert engine with configurable probability threshold ($\theta_{\text{alert}} = 0.60$), idempotent deduplication, persistent JSON storage, safe multi-channel notification adapters, and empirical 1–10 day uncertainty analysis.
- **Week 9:** **Unified Pipeline Orchestration, Docker Containerization & Cloud Deployment:** Full multi-stage execution pipeline connecting Stages 1–18 in `src/run_pipeline.py`, multi-container Docker and Docker Compose orchestration (FastAPI backend + Nginx React frontend), comprehensive health check monitoring, and deployment guides for Linux VM, Render, and Railway.


---

## 2. End-to-End System Architecture (Weeks 1–6)

```text
                  NOAA GFS Operational (AWS S3 / NOMADS)
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   Data Acquisition   │
                         │  Index-based Byte-   │
                         │    Range Slicing     │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │    Preprocessing     │
                         │  • Unit Conversion   │
                         │  • Nearest Grid-Pt   │
                         │  • Physical Bounds   │
                         └──────────┬───────────┘
                                    │
                         ┌──────────┴───────────┐
                         │                      │
                         ▼                      ▼
                  Clean GFS Data         Clean ERA5 Data
                 (data/processed/)      (data/processed/)
                         │                      │
                         │             ┌────────┴──────────┐
                         │             │ Temporal Features │ (Week 2)
                         │             │ • 24h/7d Rolling  │
                         │             │ • Daily Min/Max   │
                         │             │ • Anomalies       │
                         │             └────────┬──────────┘
                         │                      │
                         │             ┌────────┴──────────┐
                         │             │ Anomaly Detection │ (Week 2)
                         │             │ • Standard Z      │
                         │             │ • Robust MAD      │
                         │             └────────┬──────────┘
                         │                      │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │  Matched Validation  │ (Week 3)
                         │ (district, valid_t)  │
                         │ error = GFS - ERA5   │
                         └──────────┬───────────┘
                                    │
                         ┌──────────┴───────────┐
                         │                      │
                         ▼                      ▼
             ┌──────────────────────┐┌──────────────────────┐
             │ Error & Bias Analysis││ Reliability Scoring │ (Week 4)
             │ • Lead Days 1-10     ││ • R = R_err * C      │
             │ • Bias Correction    ││ • Spatiotemporal Map │
             │ • Boxplots & Scatter ││ • Sensitivity Curves │
             └──────────┬───────────┘└──────────┬───────────┘
                        │                       │
                        └──────────┬────────────┘
                                   │
                                   ▼
                        ┌──────────────────────┐
                        │ Forecast-Bust Model  │ (Week 5)
                        │ • Training Quantile  │
                        │ • Chronological Split│
                        │ • LR & Random Forest │
                        │ • PR Curves & CM     │
                        │ • joblib Model & API │
                        └──────────┬───────────┘
                                   │
                                   ▼
             ┌──────────────────────────────────────────────┐
             │ Automated Publication Figures, Metric CSVs,  │
             │ Model Metadata & Markdown Scientific Reports │
             │ (outputs/week3, week4, week5, reports)       │
             └──────────────────────────────────────────────┘
```

---

## 3. Data Sources & Variable Availability

### NOAA Global Forecast System (GFS)
- **Source:** NOAA Open Data Program on AWS S3 (`s3://noaa-gfs-bdp-pds/`) with fallback to NOAA NOMADS.
- **Resolution:** 0.25° Gaussian grid (~27 km).
- **Temporal Horizon:** Forecast hours `000` to `168` (0 to 7 days), 3-hourly intervals, cycles `00`, `06`, `12`, `18` UTC.
- **Variables Retrieved:** 2m Temperature (`TMP:2 m above ground`), Surface Total Precipitation (`APCP:surface`).

### ECMWF ERA5 Atmospheric Reanalysis
- **Source:** Copernicus Climate Data Store (CDS API: `reanalysis-era5-single-levels`).
- **Resolution:** 0.25° regular latitude-longitude grid (~27 km).
- **Temporal Coverage:** Hourly reanalysis reference fields.
- **Variables Retrieved:** 2m Temperature (`2m_temperature` / `t2m`), Total Precipitation (`total_precipitation` / `tp`).

### Variable Availability & Physical Semantics Check

| Variable | GFS Status | ERA5 Status | Overall Support | Physical Semantics & Research Notes |
| :--- | :--- | :--- | :--- | :--- |
| **2m Temperature (`temperature_c`)** | Available | Available | **Fully Supported** | Matched instantaneously across (district, valid_time). Units standardized to °C. |
| **Total Precipitation (`precipitation_mm`)** | Available | Available | **Evaluated with Accumulation Guard** | In GFS, APCP represents step accumulations (3-6h intervals). ERA5 represents hourly accumulated depth. Direct unaligned subtraction without interval alignment creates an accumulation mismatch; precipitation bias correction is kept disabled until multi-hour window accumulation alignment is applied. |
| **Surface Pressure (`pressure_hpa`)** | Absent in Local Subset | Absent in Local Subset | **Unsupported in Current Subset** | Neither surface pressure nor MSLP was downloaded in the local ERA5 and GFS subsets. Variable availability verification explicitly detects and documents this absence without fabricating synthetic pressure numbers. |

---

## 4. Installation & Dependencies

### Virtual Environment Setup
```bash
# Clone the repository
git clone https://github.com/Akshit029/minor-project.git
cd minor-project

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install all required dependencies
pip install -r requirements.txt
```

### Installed Dependencies
- `numpy>=1.24.0`, `pandas>=2.0.0`, `xarray>=2023.1.0`, `netCDF4>=1.6.0`, `scipy>=1.10.0`
- `matplotlib>=3.7.0`, `seaborn>=0.12.0`, `pyyaml>=6.0`, `requests>=2.28.0`
- `scikit-learn>=1.3.0`, `joblib>=1.3.0`, `pytest>=7.0.0`, `tabulate>=0.9.0`
- `eccodes`, `cfgrib` (GRIB2 parsing)

---

## 5. Configuration (`config.yaml`)

The pipeline is completely configuration-driven via `config.yaml`:
```yaml
region:
  name: "Jammu and Kashmir"
  north: 38.0
  south: 31.0
  west: 73.0
  east: 81.0

districts:
  Srinagar: { lat: 34.0837, lon: 74.7973 }
  Jammu: { lat: 32.7266, lon: 74.8570 }
  Anantnag: { lat: 33.7311, lon: 75.1487 }
  Baramulla: { lat: 34.2090, lon: 74.3429 }

week3:
  lead_days_range: [1, 10]
  hours_per_lead_day: 24
  min_samples_district: 3
  min_samples_bias_correction: 4
  bias_correction_train_split: 0.70
  check_pressure: true
  enable_precip_bias_correction: false

week4:
  error_scale:
    temperature_c: 2.0   # °C tolerance (engineering threshold)
    precipitation_mm: 5.0 # mm tolerance
  variable_weights:
    temperature_c: 1.0
    precipitation_mm: 0.5
  confidence_k: 10.0     # Sample confidence factor smoothing parameter
  min_evidence_samples: 3
  temporal_split_ratio: 0.70

week5:
  bust_quantile: 0.90    # Upper 90th percentile of training absolute error
  min_samples_threshold: 4
  train_ratio: 0.70
  val_ratio: 0.15
  test_ratio: 0.15
  random_seed: 42
  classification_threshold: 0.50
```

---

## 6. Pipeline Execution Guide

### Running the Complete Pipeline
```bash
# Execute the full 14-stage workflow across Weeks 1 to 5
python src/run_pipeline.py
```

### Running on Existing Local Data Without Redownloading
```bash
# Skip network downloads and run all analytical, ML, and reporting stages on local data
python src/run_pipeline.py --skip-download
```

### Running Individual Pipeline Stages
```bash
# Available stages: download, preprocess, quality, features, anomaly, validate,
#                   week3, week4, week5, visualize, reports
python src/run_pipeline.py --stage week3
python src/run_pipeline.py --stage week4
python src/run_pipeline.py --stage week5
python src/run_pipeline.py --stage reports
```

### Running Fast Test Mode
```bash
python src/run_pipeline.py --test
```

### Running Individual Modules Directly
```bash
# Week 3 error analysis & bias correction
python src/error_analysis.py

# Week 4 reliability scoring
python src/reliability.py

# Week 5 ML forecast-bust model training & evaluation
python src/forecast_bust.py

# Generate all figures
python src/visualize_week3.py
python src/visualize_week4.py
python src/visualize_week5.py

# Compile all markdown scientific reports
python src/generate_reports.py
```

---

## 7. Week-by-Week Implementation & Scientific Methodology

### Weeks 1 & 2: Ingestion, Quality Checks, Features & Anomaly Screening
- Ingestion of operational GFS GRIB2 forecasts using index-based byte slicing.
- Ingestion of hourly ERA5 NetCDF reanalysis.
- Spatial extraction of nearest grid points for Srinagar, Jammu, Anantnag, and Baramulla.
- Data quality verification (`outputs/data_quality_report.csv`).
- Temporal feature engineering: 24h & 7d rolling means, accumulations, daily min/max/mean, and anomalies.
- Dual-method anomaly detection: Standard Z-Score ($|Z| \ge 3.0$) and Robust Z-Score via MAD ($|\text{Robust } Z| \ge 3.5$).

### Week 3: Matched Error Analysis & Leakage-Safe Bias Correction
- **Strict Matching:** Verified strictly on `(district, valid_time)` where $\text{valid\_time} = \text{initialization\_time} + \text{lead\_hours}$.
- **Sign Convention:** $\text{error} = \text{forecast\_value} - \text{reference\_value}$. Positive bias indicates the forecast overestimates the reanalysis reference.
- **Baseline Error Metrics:** Computed MAE, RMSE, Bias, Median Absolute Error, Standard Deviation of Error, and sample counts across lead days 1 through 10.
- **Historical Mean-Bias Correction:**
  $$\text{corrected\_forecast} = \text{forecast\_value} - \text{training\_bias}$$
  $$\text{training\_bias} = \text{mean}(\text{forecast\_value} - \text{reference\_value})_{\text{train}}$$
  - Learned strictly from chronological training data (earliest 70%).
  - Hierarchy: District $\times$ Lead Day $\to$ Regional Lead Day $\to$ Global Regional Fallback.
  - Evaluated on identical held-out test records (latest 30%).
- **Visual Deliverables:** MAE/RMSE/Bias vs. lead day, district-wise signed and absolute error boxplots, before/after bias correction comparison, and 1:1 scatterplots.

### Week 4: Spatiotemporal Modelling for Reliability Scoring
- **Mathematical Formulation:**
  1. Normalized Error: $\text{normalized\_error} = \frac{\text{MAE}}{\text{error\_scale}}$ ($\text{error\_scale} = 2.0^\circ\text{C}$).
  2. Error-based Reliability Component:
     $$R_{\text{error}} = \exp(-\text{normalized\_error})$$
     When error is 0, $R_{\text{error}} = 1.0$; decays smoothly towards 0 as error grows.
  3. Sample Confidence Factor:
     $$C = \frac{n}{n + k}$$
     Where $n$ is the number of independent verification cases and $k = 10.0$ is the smoothing parameter.
  4. Composite Reliability Index:
     $$R = R_{\text{error}} \times C \in [0, 1]$$
- **Strict Leakage Prevention:** Parameters estimated strictly on earlier historical periods, evaluated on later held-out periods.
- **Provenance Tracking:** Records whether score cell was estimated at district $\times$ lead day level or through regional fallback.
- **Sensitivity Analysis:** Evaluates score sensitivity across tolerance scales (1.0 to 5.0 °C) and smoothing parameters $k$ (2 to 20).

### Week 5: Machine-Learning Forecast-Bust Classifier
- **Empirical Bust Label Definition:**
  $$\text{bust} = \begin{cases} 1 & \text{if } |\text{error}| > \text{threshold}_{\text{train}} \\ 0 & \text{otherwise} \end{cases}$$
  The threshold is the **upper 90th percentile** of absolute error estimated strictly from the chronological training split.
- **Strictly Leakage-Free Features:** Feature extraction includes strictly parameters available at forecast issuance time:
  - `lead_hours`, `lead_day`
  - `district` (encoded via OneHotEncoder fit strictly on training data)
  - `forecast_value`
  - Diurnal initialization cycle hour (`init_hour`), valid hour (`valid_hour`), and valid month (`valid_month`).
  - **Strictly excluded:** reference observations, signed errors, absolute errors, squared errors, bust thresholds, and bust labels.
- **Chronological Split:** Earliest 70% for Training, next 15% for Validation, final 15% for Held-Out Testing.
- **Models:** Interpretable Logistic Regression (`class_weight='balanced'`) and nonlinear Random Forest Classifier.
- **Evaluation:** Precision, Recall, F1-Score, Average Precision, Precision-Recall Curve, and Confusion Matrix on held-out test data.
- **Production Inference API:** Reusable `ForecastBustPredictor` class loads serialized `.joblib` pipeline and validates input schemas:
  ```python
  from src.forecast_bust import ForecastBustPredictor
  import pandas as pd

  predictor = ForecastBustPredictor(
      model_path="outputs/week5/trained_model_pipeline.joblib",
      metadata_path="outputs/week5/model_metadata.json"
  )
  incoming_forecast = pd.DataFrame([{
      "district": "Srinagar",
      "lead_hours": 24,
      "lead_day": 2,
      "forecast_value": 18.5,
      "init_hour": 0,
      "valid_hour": 0,
      "valid_month": 9
  }])
  prediction = predictor.predict(incoming_forecast)
  print(prediction[["district", "bust_probability", "predicted_bust_class"]])
  ```

### Week 6: Agentic AI Workflow Integration & Dashboard Assistant

Week 6 transitions the scientific pipeline from static offline artifacts to an interactive, conversational research assistant powered by **LangChain** and **Google Gemini** (with full deterministic offline fallback).

#### 1. Core Architectural Goals
- **Natural Language Orchestration:** Allow researchers, forecasters, and reviewers to query empirical reliability tables, trigger model inference, and clarify scientific definitions using natural language.
- **Strict Grounding & Zero Hallucination:** Predictions and metrics are strictly executed via real project tools. The assistant discloses when data is unavailable (e.g. lead day 3+ in the September archive) and refuses to fabricate numbers.
- **Strict Input Schema Validation:** The forecast-bust model strictly requires 7 issuance features. Missing inputs are requested via interactive follow-ups rather than arbitrarily imputed.
- **Configurable LLM with Resilient Fallback:** Powered by `langchain-google-genai` when `GEMINI_API_KEY` is provided, and backed by a deterministic scientific orchestrator when offline.

#### 2. Specialized LangChain Scientific Tools
- **Tool A: Reliability Lookup (`lookup_reliability`):**
  - Connects to Week 4 `reliability_table.csv` and held-out verification records.
  - Returns empirical reliability index $R \in [0, 1]$, sample confidence factor $C = \frac{n}{n + k}$, error component $R_{\text{error}}$, verification MAE, and fallback provenance.
- **Tool B: Forecast-Bust Prediction (`predict_forecast_bust`):**
  - Connects to Week 5 serialized model (`trained_model_pipeline.joblib`) and metadata.
  - Strictly validates all 7 forecast issuance features: `district`, `lead_hours`, `lead_day`, `forecast_value`, `init_hour`, `valid_hour`, `valid_month`.
  - Discloses that humidity and wind speed are not variables in the trained model.
- **Tool C: Scientific Result Explanation (`explain_scientific_metrics`):**
  - Explains the mathematical difference between retrospective empirical reliability index $R$ and prospective forecast-bust probability $P_{\text{bust}}$.
- **Tool D: District Reliability Comparison (`compare_district_reliability`):**
  - Performs multi-district comparisons for available lead days (Days 1 & 2) and reports data availability boundaries.

#### 3. Backend & Frontend Architecture
- **FastAPI Backend (`src/api.py`):**
  - `POST /api/chat`: Invokes LangChain Agent with conversation history and feature extraction.
  - `POST /api/bust-predict`: Production ML inference endpoint matching the dashboard interface.
  - `GET /api/reliability-lookup`: Direct query endpoint for spatiotemporal reliability.
  - `GET /api/health`: Health status and artifact verification.
- **React Frontend Dashboard (`frontend/src/pages/AIAssistantPage.tsx`):**
  - Native integration matching the J&K Weather Reliability Design System.
  - Instant demonstration question chips for rapid review presentation.
  - Interactive 7-feature Forecast-Bust Drawer with strict schema validation.
  - Visual summary cards displaying $R$, $C$, MAE, and Bust Risk badges.
  - Expandable "Scientific Tools Invoked" inspector for transparency.


---

## 8. Interpretation of Metrics & Scores

### MAE, RMSE, and Bias
- **MAE (Mean Absolute Error):** Average magnitude of forecast errors in physical units (°C). Linear penalty for deviations.
- **RMSE (Root Mean Squared Error):** Quadratic penalty disproportionately penalizing large outliers and bust events.
- **Mean Bias Error:** Average signed difference ($\text{GFS} - \text{ERA5}$). Positive values indicate systematic model overestimation; negative values indicate underestimation (cold bias).

### Empirical Reliability Index $R$ vs. Probability
- $R \in [0, 1]$ is an **empirical performance index** that scales with historical forecast accuracy and sample support.
- A score of $1.0$ indicates perfect historical verification with infinite sample support.
- Low scores indicate either large historical errors, small sample sizes ($n \ll k$), or both.
- **Scientific distinction:** $R$ is **not a calibrated Bayesian probability** of forecast correctness.

### Forecast-Bust Probability
- The bust classifier output $\hat{p} \in [0, 1]$ represents the statistical model's estimated likelihood that a forecast's absolute error will exceed the historical 90th percentile threshold.
- Allows operational meteorologists and disaster planners to flag high-uncertainty forecast windows in advance.

---


---

## 9. College Review Demonstration Guide

Use this step-by-step walk-through during the project review tomorrow:

### 1. Start Both Services
```bash
# Terminal 1: Start Backend API (FastAPI)
source .venv/bin/activate
python -m uvicorn src.api:app --host 127.0.0.1 --port 8000 --reload

# Terminal 2: Start Frontend Dashboard (Vite)
npm --prefix frontend run dev
```
Open browser to: `http://localhost:5173/ai-assistant`

### 2. Live Review Questions & What to Point Out

| Example Review Question | Recommended Action | What to Highlight to Reviewers |
| :--- | :--- | :--- |
| **"Explain the reliability of Srinagar on lead day 2."** | Click Chip 1 | Shows Week 4 mathematical formula evaluated on held-out test data ($R = 0.0061$, $\text{MAE} = 7.28^\circ\text{C}$, $n=3$, $C=0.2308$). Point out provenance and confidence damping. |
| **"Compare the reliability of Jammu and Srinagar on lead day 3."** | Click Chip 2 | **Demonstrates Academic Honesty:** Assistant transparently discloses that verification data in the archive covers lead days 1 & 2 and refuses to fabricate Day 3 numbers. |
| **"What does the reliability index mean?"** | Click Chip 3 | Demonstrates meteorological grounding: Explains $R = R_{\text{error}} \times C$, combining accuracy with sample size support. |
| **"What is the difference between reliability and bust probability?"** | Click Chip 4 | Shows core conceptual mastery: Explains that Reliability is retrospective historical accuracy, while Bust Probability is prospective extreme event risk. |
| **"Estimate forecast-bust risk for this forecast."** | Click Chip 5 | Shows schema validation: Prompts user for missing features. Open the **Interactive Feature Drawer**, set Day 2, 18.5°C, and click **Estimate with Form Values** to demonstrate live ML inference! |
| **"Explain why this prediction has a high estimated risk."** | Click Chip 6 | Explains that extreme terrain offset in valley districts and longer forecast horizons increase non-linear bust probability. |

---

### Week 7: SHAP-based Feature Influence Analysis

Week 7 integrates explainable AI (XAI) into the operational medium-range forecast verification system using **SHAP (SHapley Additive exPlanations)**:

#### 1. Core Objectives & Theoretical Foundations
- **Axiomatic Attribution:** Evaluates exact additive Shapley values based on cooperative game theory, ensuring local accuracy, missingness, and consistency.
- **Model Compatibility without Retraining:** Inspects the Week 5 serialized model (`LogisticRegression_BustClassifier`), automatically selecting `shap.LinearExplainer` to calculate exact log-odds feature attributions without retraining or modifying weights.
- **Transformed Feature Name Preservation:** Preserves categorical one-hot encoded variables (`district: Anantnag`, `district: Baramulla`, `district: Jammu`, `district: Srinagar`) and numerical predictors (`lead_hours`, `valid_hour`, `forecast_value`).
- **Global Feature Influence:** Computes mean absolute SHAP values across all verification cases, quantifying dominant uncertainty drivers.
- **High-Error Event Waterfalls:** Identifies top high-error verification cases (e.g. Baramulla lead 15h err -10.02°C, Anantnag lead 24h/27h err -9.00°C) and isolates features increasing versus mitigating bust risk.
- **Meteorological Variable Audit:** Audits atmospheric humidity and wind speed availability; confirms they are absent from the local archive and not used in the Week 5 model, without fabricating synthetic observations.

#### 2. Key Findings & Feature Rankings
- **Primary Driver:** Forecast horizon (`lead_hours`) accounts for **39.5%** of global model influence (Mean |SHAP| = 0.9458).
- **Secondary Driver:** Diurnal solar timing (`valid_hour`) accounts for **28.8%** of influence (Mean |SHAP| = 0.6879).
- **Temperature Magnitude:** Forecast value (`forecast_value`) accounts for **18.6%** of influence (Mean |SHAP| = 0.4449).
- **Geographic Terrain:** District encoding accounts for **13.1%** of influence, with Jammu mitigating risk (-0.081) and mountain valley districts elevating baseline uncertainty.

---

## 12. Automated Testing Suite (91 Tests)

The repository contains 91 comprehensive automated unit, integration, and end-to-end tests across 10 test modules covering all mathematical formulas, sign conventions, leakage guards, fallback hierarchies, alerting, containerization, and edge cases.

```bash
# Run the complete test suite
./.venv/bin/pytest -v
```

### Test Coverage Summary:
- `tests/test_preprocess.py`: Nearest grid index calculations, valid-time derivations, physical boundary screening.
- `tests/test_features.py`: Multi-scale rolling means, accumulations, anomaly calculations.
- `tests/test_anomaly.py`: Parametric Z-score and robust MAD anomaly screening.
- `tests/test_week3.py`: Known-value MAE/RMSE/Bias calculation, positive bias sign convention, lead-day binning, timestamp matching, variable availability checks, leakage-safe historical bias correction.
- `tests/test_week4.py`: Reliability score bounds $[0, 1]$, zero-error behavior, monotonic error decay, sample confidence factor growth, rejection of invalid scales/parameters, insufficient sample policy (returns None).
- `tests/test_week5.py`: Training-derived bust threshold calculation, leakage-free feature verification, chronological train/val/test splitting, model training, evaluation metrics, model serialization, and `ForecastBustPredictor` schema validation.
- `tests/test_week6_agentic_ai.py`: Unit and integration tests for Week 6 (20 tests):
  - Reliability tool lookups (valid, held-out, out-of-bounds, invalid district rejection).
  - Forecast-bust tool inference, strict schema validation for missing features, no fabrication.
  - Scientific explanation distinctions, mathematical definitions, and error sign conventions.
  - Multi-district comparative analysis and data availability disclosures.
  - Deterministic fallback when `GEMINI_API_KEY` is missing.
  - Mocked LangChain LLM tool-calling flow.
  - FastAPI endpoints (`/api/health`, `/api/chat`, `/api/bust-predict`, `/api/reliability-lookup`, request size limits, error masking).
- `tests/test_week7_explainability.py`: Unit and integration tests for Week 7 (18 tests):
  - SHAP explainer initialization and compatibility with Week 5 Logistic Regression pipeline.
  - Feature name preservation across ColumnTransformer one-hot and scaler steps.
  - Global feature importance rankings and concept grouping properties.
  - Exact additive decomposition check: base value + sum(SHAP) == final log-odds.
  - Directional consistency of positive (risk-increasing) and negative (risk-mitigating) attributions.
  - High-error event ranking, retrieval, and distinction between retrospective error and prospective risk.
  - Meteorological variable audit: humidity and wind speed audited as absent without data fabrication.
  - FastAPI explainability endpoints (`/api/explainability/global`, `/api/explainability/events`, `/api/explainability/local`, `/api/explainability/meteorological`).
  - Error and edge case handling for missing artifacts and schemas.
  - Agentic AI natural language responses to Week 7 explainability questions.
- `tests/test_week8_alerting.py`: Unit and integration tests for Week 8 (17 tests):
  - Idempotent alert hashing (`generate_alert_hash`) preventing duplicate alerts.
  - Severity classification thresholds (`critical`, `high`, `moderate`, `low`).
  - Persistent alert storage (`AlertStorageManager` save, load, update status lifecycle).
  - Multi-channel notification adapters (Logging, In-App, safe Email credential fallback).
  - Multi-horizon uncertainty quantification (Days 1–2 verified vs Days 3–10 unobserved).
  - Regional reliability GeoJSON building and schema validation.
  - Week 8 FastAPI endpoints (`GET /api/alerts`, `POST /api/alerts/evaluate`, `PATCH /api/alerts/{id}/status`, `POST /api/alerts/test-trigger`, `GET /api/reliability/regional-map`, `GET /api/uncertainty/lead-days`).
- `tests/test_week9_pipeline.py`: Unit and integration tests for Week 9 (8 tests):
  - Full end-to-end data-to-alert execution workflow.
  - Health check endpoint `/api/health` multi-week artifact status verification.
  - Pipeline orchestration pre-flight checks and stage execution CLI (`--stage week8`, `--stage week9`).
  - Docker containerization configuration validation (`Dockerfile`, `frontend/Dockerfile`, `docker-compose.yml`, `.env.example`).

---

## 11. Directory Structure & Saved Artifacts

```text
minor-project/
├── config.yaml                          # Master configuration file
├── requirements.txt                     # Python dependencies
├── pytest.ini                           # Pytest configuration
├── README.md                            # Comprehensive documentation
├── docs/
│   ├── implementation_checklist.md      # Implementation audit and roadmap checklist
│   └── week7_shap_analysis.md           # Week 7 SHAP explainability & feature influence report
├── src/
│   ├── download_gfs.py                  # GFS download module
│   ├── download_era5.py                 # ERA5 download module
│   ├── preprocess.py                    # Preprocessing & spatial extraction
│   ├── data_quality.py                  # Data quality screening
│   ├── features.py                      # Temporal feature extraction
│   ├── anomaly_detection.py             # Dual Z-score & MAD anomaly screening
│   ├── validate.py                      # Baseline validation
│   ├── error_analysis.py                # Week 3 error analysis & bias correction
│   ├── reliability.py                   # Week 4 spatiotemporal reliability scoring
│   ├── forecast_bust.py                 # Week 5 ML forecast-bust classifier
│   ├── explainability.py                # Week 7 SHAP Explainability & Feature Influence
│   ├── visualize_week1.py               # Week 1 visualization module
│   ├── visualize_week2.py               # Week 2 visualization module
│   ├── visualize_week3.py               # Week 3 visualization module
│   ├── visualize_week4.py               # Week 4 visualization module
│   ├── visualize_week5.py               # Week 5 visualization module
│   ├── generate_reports.py              # Dynamic scientific report generator
│   ├── agentic_ai.py                    # Week 6 LangChain Agent & Scientific Tools
│   ├── api.py                           # FastAPI Server (Weeks 6 & 7 endpoints)
│   └── run_pipeline.py                  # Master 15-stage pipeline orchestrator
├── tests/
│   ├── test_preprocess.py               # Unit tests for preprocessing
│   ├── test_features.py                 # Unit tests for features
│   ├── test_anomaly.py                  # Unit tests for anomaly detection
│   ├── test_week3.py                    # Unit tests for Week 3
│   ├── test_week4.py                    # Unit tests for Week 4
│   ├── test_week5.py                    # Unit tests for Week 5
│   ├── test_week6_agentic_ai.py         # Unit tests for Week 6 Agentic AI & API
│   └── test_week7_explainability.py     # Unit tests for Week 7 SHAP & Explainability API
├── data/
│   ├── raw/                             # Downloaded raw GRIB2 and NetCDF files
│   └── processed/                       # Clean standardized CSV datasets
└── outputs/
    ├── data_quality_report.csv          # Data quality audit
    ├── detected_anomalies.csv           # Flagged statistical anomalies
    ├── validation_by_lead_time.csv      # Baseline lead time validation
    ├── validation_by_district.csv       # Baseline district validation
    ├── figures/                         # Week 1 & 2 visualization figures (300 DPI)
    ├── week3/
    │   ├── matched_validation_dataset.csv
    │   ├── lead_day_metrics.csv
    │   ├── district_metrics.csv
    │   ├── district_lead_metrics.csv
    │   ├── bias_correction_params.csv
    │   ├── bias_correction_eval.csv
    │   ├── variable_availability_check.csv
    │   ├── data_matching_summary.csv
    │   ├── figures/                     # Week 3 plots (MAE, RMSE, Bias, Boxplots, Scatter)
    │   └── reports/
    │       └── week3_error_analysis.md
    ├── week4/
    │   ├── reliability_table.csv
    │   ├── held_out_evaluation.csv
    │   ├── sensitivity_analysis.csv
    │   ├── provenance_summary.csv
    │   ├── figures/                     # Week 4 plots (Reliability curves, Heatmap, Sensitivity)
    │   └── reports/
    │       └── week4_reliability_report.md
    ├── week5/
    │   ├── labeled_forecast_dataset.csv
    │   ├── label_threshold_metadata.csv
    │   ├── split_summary.csv
    │   ├── held_out_metrics.csv
    │   ├── trained_model_pipeline.joblib
    │   ├── model_metadata.json
    │   ├── figures/                     # Week 5 plots (PR curves, Confusion matrix, Importance)
    │   └── reports/
    │       └── week5_bust_model_report.md
    ├── week7/
    │   ├── global_feature_importance.csv     # Tabular global SHAP rankings
    │   ├── high_error_events_analyzed.csv    # Analyzed high-error verification events
    │   ├── meteorological_variable_audit.csv # Variable audit of humidity and wind speed
    │   ├── shap_analysis_metadata.json       # Master metadata for API and frontend
    │   └── figures/                          # 300 DPI publication plots (SHAP bar, beeswarm, waterfalls)
    └── reports/
        ├── week1_week2_summary.md       # Week 1 & 2 summary report
        └── research_summary_weeks1_to_5.md # Master research synthesis report
```

---

## 12. Scientific Assumptions & Operational Limitations

1. **Reanalysis Reference vs. Weather Station Truth:** ECMWF ERA5 blends numerical weather models with assimilated satellite, radar, and in-situ data. While it serves as the global standard for reference gridded verification, it is **not identical to direct in-situ ground station observations**.
2. **Nearest Grid-Point Representation:** Target districts are extracted from the nearest 0.25° grid centroid (~27 km resolution). In rugged Himalayan terrain, elevation discrepancies between the grid centroid and valley settlements (e.g. Srinagar city vs. surrounding mountains) introduce localized topographic offsets.
3. **Empirical Indexing vs. Bayesian Probability:** The reliability score $R \in [0, 1]$ is an empirical index scaling with historical accuracy and sample support. It must not be presented as a calibrated Bayesian probability.
4. **Precipitation Accumulation Mismatch:** GFS operational APCP data represents step accumulation intervals, whereas ERA5 provides hourly accumulated depth. Direct unaligned subtraction without interval alignment creates an accumulation mismatch; precipitation bias correction is held disabled until interval-aligned accumulation aggregation is integrated.
5. **Class Imbalance in Forecast Busts:** Defining busts via the upper 90th percentile inherently results in a class imbalance (~10% positive cases). The ML pipeline handles this using class-weighted loss functions (`class_weight='balanced'`) and evaluates performance primarily using Precision-Recall curves and Average Precision rather than unweighted accuracy.

---

## 13. Verification Checklist

### Week 1 Deliverables
- [x] Construction of valid NOAA GFS URLs and index-based byte-range downloading.
- [x] ECMWF ERA5 CDS API retrieval module with credential validation.
- [x] Spatial nearest-gridpoint extraction for Srinagar, Jammu, Anantnag, Baramulla.
- [x] Standardized UTC timestamps and valid-time calculation.
- [x] Unit conversion: Kelvin to Celsius, metres to millimetres.
- [x] Automated data cleaning: duplicate elimination, physical bounds screening.
- [x] Outputs saved to `data/processed/gfs_clean.csv` and `era5_clean.csv`.
- [x] Automated data quality checks: `outputs/data_quality_report.csv` & `.txt`.
- [x] Week 1 publication figures at 300 DPI in `outputs/figures/`.

### Week 2 Deliverables
- [x] 24-hour and 7-day rolling temperature means per district.
- [x] 24-hour and 7-day precipitation accumulations per district.
- [x] Daily aggregations (min, max, mean temperature, daily precipitation total).
- [x] Monthly mean temperature and precipitation totals.
- [x] Hourly temperature and rainfall anomalies against provisional baseline.
- [x] Statistical anomaly screening: Parametric Z-Score ($|Z| \ge 3.0$).
- [x] Robust anomaly screening: Median Absolute Deviation MAD ($|\text{Robust } Z| \ge 3.5$).
- [x] Identified anomalies saved to `outputs/detected_anomalies.csv`.
- [x] GFS vs. ERA5 verification matched strictly by `(district, valid_time)`.
- [x] Lead-time error breakdown: MAE, RMSE, Bias in `outputs/validation_by_lead_time.csv`.
- [x] District error breakdown: MAE, RMSE, Bias in `outputs/validation_by_district.csv`.
- [x] Global summary table in `outputs/tables/validation_summary.csv`.
- [x] Week 2 publication figures at 300 DPI.
- [x] Executive markdown summary report in `outputs/reports/week1_week2_summary.md`.

### Week 3 Deliverables
- [x] Variable availability check: temperature supported, precipitation checked, pressure documented as unsupported.
- [x] Construction of matched validation dataset (`outputs/week3/matched_validation_dataset.csv`).
- [x] Baseline error metrics for lead days 1–10 (`outputs/week3/lead_day_metrics.csv`).
- [x] District-wise error metrics (`outputs/week3/district_metrics.csv`).
- [x] Positive bias sign convention: $\text{error} = \text{forecast} - \text{reference}$.
- [x] Historical mean-bias correction learned strictly from training data (`outputs/week3/bias_correction_params.csv`).
- [x] Held-out evaluation before vs. after bias correction (`outputs/week3/bias_correction_eval.csv`).
- [x] Week 3 publication figures in `outputs/week3/figures/` (MAE/RMSE/Bias vs. lead day, boxplots, before/after comparison, 1:1 scatterplots).
- [x] Markdown Week 3 report in `outputs/week3/reports/week3_error_analysis.md`.

### Week 4 Deliverables
- [x] Dedicated reliability module (`src/reliability.py`).
- [x] Empirical reliability score $R = R_{\text{error}} \times C \in [0, 1]$.
- [x] Sample confidence factor $C = \frac{n}{n + k}$.
- [x] Insufficient samples policy returning None/unknown rather than false zero.
- [x] Chronological split to prevent temporal leakage.
- [x] Spatiotemporal reliability table with fallback provenance (`outputs/week4/reliability_table.csv`).
- [x] Held-out reliability evaluation (`outputs/week4/held_out_evaluation.csv`).
- [x] Sensitivity analysis across error tolerance and parameter $k$ (`outputs/week4/sensitivity_analysis.csv`).
- [x] Week 4 publication figures in `outputs/week4/figures/` (Reliability curves, district comparison, heatmap, sensitivity).
- [x] Markdown Week 4 report in `outputs/week4/reports/week4_reliability_report.md`.

### Week 5 Deliverables
- [x] Label generation module defining busts using upper 90th percentile of training absolute error.
- [x] Training-derived thresholds metadata (`outputs/week5/label_threshold_metadata.csv`).
- [x] Strictly leakage-free feature engineering based solely on forecast issuance parameters.
- [x] Chronological train (70%) / validation (15%) / test (15%) splits (`outputs/week5/split_summary.csv`).
- [x] Training of Logistic Regression (interpretable) and Random Forest (nonlinear) models.
- [x] Held-out test evaluation: Precision, Recall, F1, Average Precision, Confusion Matrix (`outputs/week5/held_out_metrics.csv`).
- [x] Model pipeline serialization (`outputs/week5/trained_model_pipeline.joblib`).
- [x] Model metadata JSON export (`outputs/week5/model_metadata.json`).
- [x] Production inference interface with input schema validation (`ForecastBustPredictor`).
- [x] Week 5 publication figures in `outputs/week5/figures/` (PR curves, confusion matrices, model comparison, feature importance).
- [x] Markdown Week 5 report in `outputs/week5/reports/week5_bust_model_report.md`.
- [x] Master research synthesis report in `outputs/reports/research_summary_weeks1_to_5.md`.
- [x] Full test suite passing (48 passed in `pytest`).
### Week 6 Deliverables (Agentic AI Workflow & Dashboard Assistant)
- [x] Dedicated Agentic AI module with LangChain tools (`src/agentic_ai.py`).
- [x] Tool A: Spatiotemporal reliability lookup connecting to Week 4 tables and formulas.
- [x] Tool B: Forecast-bust prediction connecting to Week 5 serialized model with strict 7-feature schema validation.
- [x] Tool C: Scientific result explanation distinguishing reliability, confidence, bust probability, and error metrics.
- [x] Tool D: Comparative district verification with data boundary disclosure.
- [x] Configurable LLM provider: Google Gemini (`langchain-google-genai`) with configurable `LLM_MODEL`.
- [x] Zero-crash deterministic scientific engine fallback when `GEMINI_API_KEY` is not provided.
- [x] FastAPI backend server (`src/api.py`) exposing `/api/chat`, `/api/bust-predict`, `/api/reliability-lookup`, and `/api/health`.
- [x] Request validation, request size limiting (1 MB), CORS support, and safe error masking without stack traces.
- [x] Full frontend integration in React 19 (`frontend/src/pages/AIAssistantPage.tsx`).
- [x] Interactive demonstration chips for rapid presentation during college review.
- [x] Interactive 7-feature Forecast-Bust Builder drawer.
- [x] Transparent "Tools Invoked" inspector and visual metric preview cards.
- [x] Updated Vite dev proxy to route `/api/*` seamlessly to FastAPI on port 8000.
- [x] `.env.example` with clear placeholders and zero committed secrets.
- [x] 20 new automated unit and integration tests (`tests/test_week6_agentic_ai.py`).
- [x] Full test suite passing (48 of 48 tests passed in `pytest`).

### Week 7 Deliverables (SHAP Feature Influence Analysis)
- [x] Dedicated Explainability module (`src/explainability.py`).
- [x] Direct integration with Week 5 model pipeline (`outputs/week5/trained_model_pipeline.joblib`) via `shap.LinearExplainer` without retraining.
- [x] Preservation of clean transformed feature names across OneHotEncoding and StandardScaler steps.
- [x] Global feature importance rankings and concept grouping (`outputs/week7/global_feature_importance.csv`).
- [x] Identification and local SHAP explanation of top high-error verification cases (`outputs/week7/high_error_events_analyzed.csv`).
- [x] Separation of risk-increasing (positive) and risk-mitigating (negative) SHAP attributions in log-odds space.
- [x] Ground-truth meteorological variable audit of humidity and wind speed (`outputs/week7/meteorological_variable_audit.csv`) without data fabrication.
- [x] Exploratory meteorological analysis of available variables (lead horizon, diurnal cycle, temperature extremes) vs. forecast error.
- [x] 300 DPI publication visualizations in `outputs/week7/figures/`:
  - `shap_global_feature_importance.png`
  - `shap_beeswarm_summary.png`
  - `shap_grouped_feature_importance.png`
  - `meteorological_error_relationships.png`
  - Individual event waterfall and horizontal contribution plots for Events 21, 32, 36, 20, 33.
- [x] Master JSON metadata export (`outputs/week7/shap_analysis_metadata.json`).
- [x] FastAPI explainability endpoints (`/api/explainability/global`, `/api/explainability/events`, `/api/explainability/local`, `/api/explainability/meteorological`).
- [x] Integration with Week 6 LangChain AI assistant: tools `get_feature_influence`, `explain_high_error_event`, `audit_humidity_and_wind_influence` with full offline deterministic fallback.
- [x] Dedicated frontend dashboard module (`frontend/src/pages/FeatureInfluencePage.tsx`) with global rankings, interactive event waterfalls, live forecast explainer, and meteorological audit.
- [x] Seamless navigation integration in sidebar (`/feature-influence`), router, and direct callout banner from Forecast Bust page.
- [x] Pipeline orchestrator integration (`python src/run_pipeline.py --stage week7`).
- [x] Comprehensive documentation in `docs/week7_shap_analysis.md`.
- [x] 18 automated unit and integration tests (`tests/test_week7_explainability.py`).
- [x] Full test suite passing (66 of 66 tests passed in `pytest`).

