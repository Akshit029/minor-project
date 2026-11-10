# Week 8: Regional Reliability Visualization & Automated Forecast-Bust Alerting System

**Project:** Spatiotemporal Reliability and Uncertainty Detection for Medium-Range Weather Forecasts  
**Target Domain:** Jammu and Kashmir (Srinagar, Jammu, Anantnag, Baramulla)  
**Verification Baseline:** GFS 0.25° Forecasts vs. ERA5 0.25° Reanalysis Ground Truth  

---

## 1. Executive Summary

Week 8 operationalizes the scientific and machine-learning discoveries of Weeks 1 through 7 into:
1. **Interactive Regional Reliability Maps:** Spatial choropleth and marker visualizations displaying district-wise reliability scores, elevation, and terrain attributes using verified geographical boundaries.
2. **Automated Forecast-Bust Alerting System:** An operational notification and persistent event-logging pipeline driven by Week 5 machine-learning predictions and a configurable bust-probability threshold.
3. **Multi-Horizon Uncertainty Quantification (1 to 10 Days):** Comprehensive quantification of error growth, standard errors, and spread across medium-range horizons with rigorous handling of observed versus unobserved lookahead days.

---

## 2. Interactive Regional Reliability Maps

### 2.1 Geographical Coverage and District Boundaries
The study domain encompasses the four primary climatic and geographical sub-regions of Jammu & Kashmir:
- **Jammu** ($32.7266^\circ\text{N}, 74.8570^\circ\text{E}$, $327\,\text{m}$): Outer plains and Shivalik foothills, sub-tropical regime.
- **Srinagar** ($34.0837^\circ\text{N}, 74.7973^\circ\text{E}$, $1585\,\text{m}$): Central intermontane valley basin, cold temperate regime.
- **Anantnag** ($33.7311^\circ\text{N}, 75.1487^\circ\text{E}$, $1600\,\text{m}$): South Kashmir basin and windward Pir Panjal slopes.
- **Baramulla** ($34.2090^\circ\text{N}, 74.3429^\circ\text{E}$, $1593\,\text{m}$): North Kashmir gorge and Kazinag pass.

District boundaries and geographical polygons are structured as GeoJSON compliant with RFC 7946 and stored at `data/geography/jk_districts.geojson`.

### 2.2 Mathematical Reliability Metric
Reliability scores are computed directly using the formulation established in Week 4:
$$R = R_{\text{error}} \times C = \exp\left(-\frac{\text{MAE}}{S_{\text{error}}}\right) \times \left(\frac{n}{n + k}\right)$$
where $S_{\text{error}} = 2.0^\circ\text{C}$ is the engineering error tolerance for 2m temperature, $k = 10.0$ is the sample confidence factor, and $n$ is the count of independent verified forecast cases.

### 2.3 Scientific Color Palette
To clearly distinguish spatial forecast reliability without visual ambiguity:
- **Emerald Green (`#059669`):** Highest Reliability ($R \ge 0.08$ or $\text{MAE} \le 3.5^\circ\text{C}$). Typical of low-altitude valley plains (Jammu).
- **Amber (`#d97706`):** Moderate Reliability ($0.03 \le R < 0.08$ or $3.5^\circ\text{C} < \text{MAE} \le 5.5^\circ\text{C}$). Typical of central valley basins (Srinagar).
- **Rose Red (`#dc2626`):** High Uncertainty ($R < 0.03$ or $\text{MAE} > 5.5^\circ\text{C}$). Typical of complex orographic passes (Baramulla, Anantnag).

---

## 3. Automated Forecast-Bust Alerting System

### 3.1 Threshold Evaluation & Configurable Governance
The alerting engine evaluates incoming forecast predictions against an operational bust-probability threshold:
$$\text{Alert Condition}: P(\text{bust} = 1 \mid \mathbf{x}) \ge \theta_{\text{alert}}$$
The threshold $\theta_{\text{alert}}$ is configurable without hardcoded dependencies:
1. **Environment Variable:** `ALERT_THRESHOLD` (e.g. `export ALERT_THRESHOLD=0.60`).
2. **Configuration File:** `config.yaml` -> `week8.alert_threshold` (default: `0.60`).
3. **API Override:** `POST /api/alerts/evaluate` supports on-the-fly threshold simulation.

### 3.2 Deduplication and Cryptographic Hashing
To prevent duplicate alerts for identical forecast events across pipeline runs or concurrent requests, each alert is assigned an idempotent SHA-256 hash:
$$\text{Alert ID} = \text{alt-}\{\text{district}\}\text{-}\{\text{lead\_day}\}\text{d-}\{\text{SHA256}(\text{district} \parallel \text{init\_time} \parallel \text{valid\_time} \parallel \text{lead\_day})[0:8]\}$$
If an alert with the same ID already exists, its state lifecycle (e.g. `Acknowledged`, `Dismissed`) is preserved rather than overwritten.

### 3.3 Alert Lifecycle Management
Alerts transition through an operational lifecycle:
- **`Active`:** Newly detected event exceeding threshold.
- **`Acknowledged`:** Operator has reviewed the uncertainty warning.
- **`Dismissed`:** Operator has determined the alert requires no further action.
- **`Investigating` / `Resolved`:** Deep diagnostic tracking.

### 3.4 Modular Notification Architecture
```
[Forecast Event] 
      │
      ▼
[ForecastBustAlertEngine] ── Evaluates P(bust) >= threshold
      │
      ▼
[CompositeNotificationDispatcher]
      ├─► [LoggingNotificationAdapter]      (System logging)
      ├─► [InAppNotificationAdapter]        (Persistent JSON storage at outputs/week8/alerts.json)
      └─► [EmailNotificationAdapter]        (Optional SMTP delivery with safe credential validation)
```
- **Strict Credential Safety:** The email adapter verifies whether `SMTP_SERVER`, `SMTP_USER`, and `ALERT_EMAIL_RECIPIENT` are set. If unset, it logs the condition and safely falls back without throwing exceptions or falsely claiming delivery.

---

## 4. Multi-Horizon Forecast Uncertainty Analysis (1 to 10 Days)

### 4.1 Observed Horizons (Days 1 & 2)
Within the historical test archive, 44 matched GFS-versus-ERA5 pairs provide empirical ground truth:
- **Lead Day 1 (24h lookahead):**
  - Regional MAE: $5.30^\circ\text{C} \pm 0.80^\circ\text{C}$
  - Regional RMSE: $5.72^\circ\text{C}$
  - Median Absolute Error: $5.79^\circ\text{C}$
  - Interquartile Range (IQR): $3.35^\circ\text{C}$
  - 90th–10th Percentile Spread: $5.80^\circ\text{C}$
- **Lead Day 2 (48h lookahead):**
  - Regional MAE: $6.14^\circ\text{C} \pm 1.04^\circ\text{C}$
  - Regional RMSE: $6.76^\circ\text{C}$
  - Median Absolute Error: $7.35^\circ\text{C}$
  - Interquartile Range (IQR): $2.25^\circ\text{C}$
  - 90th–10th Percentile Spread: $6.30^\circ\text{C}$

### 4.2 Extended Medium-Range Horizons (Days 3 to 10)
In strict accordance with scientific integrity guidelines:
- Days 3 through 10 are marked as `unobserved_extended_horizon` with `sample_count: 0`.
- Zero synthetic weather data, fake observations, or unverified statistical intervals are fabricated.
- The UI renders informative status tags and shaded areas indicating that verification observations for extended horizons are pending ingestion.

---

## 5. Artifacts and Generated Visualizations

All high-resolution (300 DPI) figures are stored in `outputs/week8/figures/`:
1. `uncertainty_vs_lead_day.png`: Dual-axis plot of MAE & RMSE with standard error bars and empirical reliability decay.
2. `district_reliability_decay.png`: District-by-district reliability curve comparisons.
3. `error_distribution_boxplots.png`: Verification error dispersion boxplots showing median, IQR, and outliers.
4. `regional_reliability_choropleth.png`: Static geographical overview of Jammu & Kashmir study points.

Tabular datasets and metadata stored in `outputs/week8/`:
- `alerts.json`: Persistent active and historical weather alerts.
- `alert_evaluation_summary.csv`: Tabular audit of all evaluated forecast events.
- `lead_day_uncertainty_metrics.csv`: 1–10 day empirical error and spread statistics.
- `district_lead_day_uncertainty.csv`: District-disaggregated horizon metrics.
- `regional_reliability_geojson.json`: Enriched GeoJSON for cartographic rendering.
- `uncertainty_analysis_metadata.json`: Analysis execution metadata.

---

## 6. Execution Commands

```bash
# Run Week 8 Uncertainty Analysis and Alert Generation
./.venv/bin/python src/run_pipeline.py --stage week8

# Run dedicated Week 8 unit and integration tests
./.venv/bin/pytest tests/test_week8_alerting.py
```

