# Week 5 Scientific Report: Machine-Learning Forecast-Bust Classifier
**Generated:** 2026-10-11 22:47:44 UTC  
**Target Region:** Jammu and Kashmir  

---

## 1. Forecast-Bust Label Definition & Protocol

- **Bust Definition**: An empirical forecast bust is defined when $|\text{error}| > \text{threshold}_{\text{train}}$, where the threshold is the **upper 90th percentile** of forecast absolute errors.
- **Strict Leakage Prevention**: Thresholds are computed **strictly from the chronological training period** (earliest 70% of cases) and never from validation or test sets.
- **Feature Scope**: Inputs to the classifier contain **strictly features known at forecast issuance time** (`lead_hours`, `lead_day`, `district`, `forecast_value`, diurnal initialization cycle). Reference observations and forecast error outcomes are strictly excluded.

### Training-Derived Thresholds by Group
| district   |   lead_day |   bust_quantile |   error_threshold |   training_sample_count | provenance        |
|:-----------|-----------:|----------------:|------------------:|------------------------:|:------------------|
| Anantnag   |          1 |             0.9 |             8.037 |                       8 | district_lead_day |
| Baramulla  |          1 |             0.9 |             8.347 |                       8 | district_lead_day |
| Jammu      |          1 |             0.9 |             4.394 |                       7 | district_lead_day |
| Srinagar   |          1 |             0.9 |             6.982 |                       7 | district_lead_day |

---

## 2. Chronological Train / Validation / Test Split Summary

| split           |   sample_count |   bust_count |   bust_percentage | start_time          | end_time            |
|:----------------|---------------:|-------------:|------------------:|:--------------------|:--------------------|
| Training        |             30 |            4 |             13.33 | 2026-09-15 00:00:00 | 2026-09-15 21:00:00 |
| Validation      |              7 |            5 |             71.43 | 2026-09-15 21:00:00 | 2026-09-16 03:00:00 |
| Test (Held-Out) |              7 |            2 |             28.57 | 2026-09-16 03:00:00 | 2026-09-16 06:00:00 |

---

## 3. Held-Out Classification Performance (Test Set)

| model               |   test_samples |   test_bust_events |   test_bust_pct |   precision |   recall |   f1_score |   average_precision |
|:--------------------|---------------:|-------------------:|----------------:|------------:|---------:|-----------:|--------------------:|
| Logistic Regression |              7 |                  2 |           28.57 |      0.2857 |        1 |     0.4444 |              0.4167 |
| Random Forest       |              7 |                  2 |           28.57 |      0      |        0 |     0      |              0.5833 |

---

## 4. Model Persistence & Inference Interface

- **Serialized Model Pipeline:** `outputs/week5/trained_model_pipeline.joblib`
- **Model Metadata JSON:** `outputs/week5/model_metadata.json`
- **Active Model Architecture:** `LogisticRegression_BustClassifier`
- **Features Employed:** `district, lead_hours, lead_day, forecast_value, init_hour, valid_hour, valid_month`

---
*Report generated automatically from actual execution artifacts.*