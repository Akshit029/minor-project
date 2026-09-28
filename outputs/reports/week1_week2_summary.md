# Spatiotemporal Reliability and Uncertainty Detection for Medium-Range Weather Forecasts
## Executive Summary & Scientific Verification Report (Weeks 1 & 2)
**Generated:** 2026-09-27 19:05:55 UTC  
**Target Domain:** Jammu & Kashmir (Lat 31.0°N–38.0°N, Lon 73.0°E–81.0°E)  
**Districts Evaluated:** Anantnag, Baramulla, Jammu, Srinagar  

---

### 1. Data Ingestion & Preprocessing Summary

| Metric | NOAA GFS Forecast | ECMWF ERA5 Reanalysis |
| :--- | :--- | :--- |
| **Record Count** | 44 | 192 |
| **Spatial Grid** | 0.25° Gaussian (~27 km) | 0.25° Regular Lat/Lon (~27 km) |
| **Missing Temperature (%)** | 0.00% | 0.00% |
| **District Coverage** | 4 / 4 districts | 4 / 4 districts |

---

### 2. Statistical Anomaly & Extreme Event Screening
- **Total Flagged Anomalies:** 11
- **Detection Methodology:** Standard Z-Score (|Z| >= 3.0) & Robust Z-Score (|Robust Z| >= 3.5 via MAD)
- **Classification:** Flagged records are classified as *statistical anomalies* and screened as *potential extreme weather events*.

#### Sample Identified Potential Extreme Events
| district   | valid_time          |   temperature_c |   precipitation_mm |   temperature_anomaly |   rainfall_anomaly |   temperature_robust_z |   rainfall_robust_z | anomaly_type          | severity                                 |
|:-----------|:--------------------|----------------:|-------------------:|----------------------:|-------------------:|-----------------------:|--------------------:|:----------------------|:-----------------------------------------|
| Anantnag   | 2026-09-15 20:00:00 |           18.43 |               3    |                 -5.8  |               2.58 |                 -0.922 |               4.864 | High-rainfall anomaly | Moderate potential extreme weather event |
| Anantnag   | 2026-09-15 23:00:00 |           19.03 |               6.77 |                 -5.2  |               6.35 |                 -0.826 |              10.976 | High-rainfall anomaly | Severe potential extreme weather event   |
| Anantnag   | 2026-09-16 14:00:00 |           25.78 |               6.3  |                  1.55 |               5.88 |                  0.246 |              10.214 | High-rainfall anomaly | Severe potential extreme weather event   |
| Baramulla  | 2026-09-15 15:00:00 |           23.48 |               1.07 |                  0    |               0.96 |                  0     |               6.833 | High-rainfall anomaly | Severe potential extreme weather event   |
| Baramulla  | 2026-09-15 19:00:00 |           18.28 |               1.71 |                 -5.2  |               1.6  |                 -0.826 |              10.92  | High-rainfall anomaly | Severe potential extreme weather event   |

---

### 3. Forecast Verification Metrics (GFS vs. ERA5)

- **Overall Temperature MAE:** `5.527 °C`
- **Overall Temperature RMSE:** `6.023 °C`
- **Overall Temperature Bias:** `-4.216 °C`

#### Verification by Forecast Lead Time

|   forecast_hour |   MAE |   RMSE |   Bias |   sample_count |
|----------------:|------:|-------:|-------:|---------------:|
|               0 | 6.035 |  6.422 | -4.875 |              4 |
|               3 | 5.623 |  6.031 | -4.678 |              4 |
|               6 | 4.207 |  4.429 | -3.098 |              4 |
|               9 | 3.248 |  3.411 | -2.152 |              4 |
|              12 | 3.738 |  4.115 | -2.032 |              4 |
|              15 | 7.428 |  7.874 | -5.863 |              4 |
|              18 | 6.385 |  6.413 | -3.45  |              4 |
|              21 | 5.713 |  5.74  | -2.808 |              4 |
|              24 | 6.77  |  7.321 | -5.77  |              4 |
|              27 | 6.868 |  7.346 | -6.868 |              4 |
|              30 | 4.787 |  5.437 | -4.787 |              4 |

#### Verification by District

| district   |   MAE |   RMSE |   Bias |   sample_count |
|:-----------|------:|-------:|-------:|---------------:|
| Anantnag   | 6.93  |  7.14  | -6.93  |             11 |
| Baramulla  | 6.762 |  6.947 | -6.762 |             11 |
| Jammu      | 2.874 |  3.278 |  2.37  |             11 |
| Srinagar   | 5.544 |  5.925 | -5.544 |             11 |

---

### 4. Scientific Limitations

1. **Reanalysis as Reference**: ECMWF ERA5 is a high-resolution atmospheric reanalysis blending numerical weather models with assimilated satellite, radar, and in-situ observations. It serves as an authoritative synthetic truth, but is **not identical to direct ground-based weather station observations**.
2. **Provisional Baseline vs. Long-Term Climatology**: In this MVP stage, anomalies are computed against the available 2026 reference window. This is formally defined as a **provisional baseline**. Climatological anomalies in operational meteorology require a standardized 30-year WMO baseline (e.g., 1991–2020).
3. **Spatial Grid Point Representation**: District values are extracted using the **nearest available grid point** (0.25° resolution, ~27 km). Complex mountainous orography across Jammu & Kashmir produces localized microclimates and elevation differences between the grid centroid and specific valleys.
4. **Model Characteristic Differences**: GFS and ERA5 utilize distinct physical parameterizations (e.g. boundary layer physics, convection schemes, land-surface models). Systematic biases observed may reflect model physics differences in addition to forecast error.
5. **Future Ground-Truth Calibration**: Subsequent project phases will integrate direct ground station telemetry from India Meteorological Department (IMD) and Automatic Weather Stations (AWS) across J&K for empirical ground-truth validation.

---
*Report generated automatically by the Antigravity Meteorological Data Pipeline.*