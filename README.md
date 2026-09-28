# Spatiotemporal Reliability and Uncertainty Detection for Medium-Range Weather Forecasts

**Academic Context:** B.Tech Minor Project  
**Target Domain:** Jammu & Kashmir (Bounding Box: Lat 31.0°N–38.0°N, Lon 73.0°E–81.0°E)  
**Representative Study Districts:** Srinagar, Jammu, Anantnag, Baramulla  
**Python Environment:** Python 3.11+ (Evaluated & verified on Python 3.13 Apple Silicon macOS / Linux / Windows)

---

## Table of Contents

1. [Project Objective](#1-project-objective)
2. [End-to-End System Architecture](#2-end-to-end-system-architecture)
3. [Data Sources](#3-data-sources)
   - [NOAA Global Forecast System (GFS)](#noaa-global-forecast-system-gfs)
   - [ECMWF ERA5 Atmospheric Reanalysis](#ecmwf-era5-atmospheric-reanalysis)
4. [Installation & Environment Setup](#4-installation--environment-setup)
   - [Local Virtual Environment](#local-virtual-environment)
   - [System Dependency: ecCodes on macOS (Apple Silicon / Intel)](#system-dependency-eccodes-on-macos-apple-silicon--intel)
   - [System Dependency on Linux & Windows](#system-dependency-on-linux--windows)
5. [Copernicus Climate Data Store (CDS) API Configuration](#5-copernicus-climate-data-store-cds-api-configuration)
6. [NOAA GFS Acquisition Architecture](#6-noaa-gfs-acquisition-architecture)
7. [Running the Pipeline](#7-running-the-pipeline)
   - [Test Mode (Rapid End-to-End Verification)](#test-mode-rapid-end-to-end-verification)
   - [Full Configured Pipeline Execution](#full-configured-pipeline-execution)
8. [Folder & Directory Structure](#8-folder--directory-structure)
9. [Detailed Output Files & Artifacts](#9-detailed-output-files--artifacts)
10. [Interpretation of Visual Deliverables](#10-interpretation-of-visual-deliverables)
11. [Scientific Verification Metrics: MAE, RMSE, and Bias](#11-scientific-verification-metrics-mae-rmse-and-bias)
12. [Forecast Lead Time & Validity Methodology](#12-forecast-lead-time--validity-methodology)
13. [Statistical Anomaly & Extreme Event Detection](#13-statistical-anomaly--extreme-event-detection)
14. [Scientific Limitations](#14-scientific-limitations)
15. [Future Roadmap & Improvements](#15-future-roadmap--improvements)
16. [Verification Checklist](#16-verification-checklist)

---

## 1. Project Objective

Numerical Weather Prediction (NWP) models exhibit varying degrees of reliability and uncertainty across complex, high-altitude terrain. Mountainous regions such as Jammu & Kashmir introduce significant microclimatic variation, complex orographic precipitation, and localized temperature lapse rates that pose unique challenges to medium-range global models.

This project investigates the spatiotemporal reliability, forecast skill decay, and statistical extreme uncertainty of medium-range weather forecasts over Jammu & Kashmir. The initial MVP (Weeks 1 & 2) establishes an automated, production-grade meteorological data engineering and verification pipeline:
- Ingestion of real NOAA GFS operational forecasts and ECMWF ERA5 reanalysis fields.
- Coordinate extraction for targeted districts without spatial domain averaging.
- Unit standardization, physical boundary filtering, and multi-scale temporal feature extraction.
- Statistical anomaly screening using dual Z-score and Robust MAD methodologies.
- Rigorous lead-time verification comparing forecast valid time against reference valid time.
- Generation of high-resolution (300 DPI) publication-ready visualizations and summary reports.

---

## 2. End-to-End System Architecture

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
                         │             │ Temporal Features │
                         │             │ • 24h/7d Rolling  │
                         │             │ • Daily Min/Max   │
                         │             │ • Anomalies       │
                         │             └────────┬──────────┘
                         │                      │
                         │             ┌────────┴──────────┐
                         │             │ Anomaly Detection │
                         │             │ • Standard Z      │
                         │             │ • Robust MAD      │
                         │             └────────┬──────────┘
                         │                      │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │  Forecast Validation │
                         │ GFS vs. ERA5 matched │
                         │  by valid_time (UTC) │
                         └──────────┬───────────┘
                                    │
                         ┌──────────┴───────────┐
                         ▼                      ▼
                  Verification Tables    Publication Visuals
                  (outputs/tables/)      (outputs/figures/)
```

---

## 3. Data Sources

### NOAA Global Forecast System (GFS)
- **Producing Agency:** National Oceanic and Atmospheric Administration (NOAA) / National Centers for Environmental Prediction (NCEP).
- **Spatial Resolution:** 0.25° Gaussian grid (~27 km horizontal grid spacing).
- **Temporal Resolution:** 3-hourly forecast lead intervals (0h to 168h+ for medium range).
- **Cycles Supported:** 00, 06, 12, 18 UTC.
- **Variables Utilized:**
  1. `TMP:2 m above ground` — 2-metre air temperature (Kelvin converted to Celsius).
  2. `APCP:surface` — Accumulated precipitation at ground surface ($kg/m^2$ or mm).

### ECMWF ERA5 Atmospheric Reanalysis
- **Producing Agency:** European Centre for Medium-Range Weather Forecasts (ECMWF) via the Copernicus Climate Change Service (C3S).
- **Nature of Dataset:** Reference atmospheric reanalysis, combining physics-based global forecast models with multi-source assimilated historical observations (satellites, weather radar, radiosondes, aircraft, and in-situ stations).
- **Important Distinction:** ERA5 is an authoritative **reanalysis and reference dataset**, not raw point station observations.
- **Spatial Resolution:** 0.25° regular latitude-longitude grid (~27 km).
- **Temporal Resolution:** Hourly (00:00 to 23:00 UTC).
- **Variables Utilized:**
  1. `2m_temperature` (shortName: `2t` / `t2m`) — Kelvin converted to Celsius.
  2. `total_precipitation` (shortName: `tp`) — Depth in metres converted to millimetres ($mm = m \times 1000$).

---

## 4. Installation & Environment Setup

### Local Virtual Environment

Ensure Python 3.11+ is installed. Clone the repository and configure an isolated virtual environment:

```bash
# Navigate to project workspace
cd /path/to/minor-project

# Create a clean virtual environment
python3 -m venv .venv

# Activate the virtual environment
# macOS / Linux:
source .venv/bin/activate
# Windows (PowerShell):
# .venv\Scripts\Activate.ps1

# Upgrade pip and install all scientific dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### System Dependency: ecCodes on macOS (Apple Silicon / Intel)

The GRIB2 decoding engine utilizes ECMWF's native `ecCodes` library. On macOS, install ecCodes via Homebrew:

```bash
# Install ecCodes C library
brew install eccodes

# Verify installation
eccodes_info
```

*Note on Apple Silicon (`arm64`):* Homebrew installs libraries to `/opt/homebrew/lib`. Python bindings (`cfgrib` and `eccodes-python`) automatically discover these libraries. If needed, you can explicitly export:
```bash
export ECCODES_DIR=$(brew --prefix eccodes)
```

### System Dependency on Linux & Windows
- **Ubuntu/Debian:** `sudo apt-get update && sudo apt-get install libeccodes-dev`
- **Fedora/RHEL:** `sudo dnf install eccodes-devel`
- **Windows:** Install ecCodes via Conda/Mamba (`conda install -c conda-forge eccodes cfgrib`) or run within WSL2 (Ubuntu).

---

## 5. Copernicus Climate Data Store (CDS) API Configuration

ERA5 reanalysis is fetched programmatically through the ECMWF CDS API (`cdsapi`).

### How to set up your CDS API Key:
1. Register for a free Copernicus user account at: [https://cds.climate.copernicus.eu](https://cds.climate.copernicus.eu)
2. Log in and navigate to your user profile page: [https://cds.climate.copernicus.eu/profile](https://cds.climate.copernicus.eu/profile)
3. Copy your **Personal Access Token**.
4. Create a configuration file in your home directory named `~/.cdsapirc`:

```bash
cat << 'EOF' > ~/.cdsapirc
url: https://cds.climate.copernicus.eu/api
key: YOUR-PERSONAL-ACCESS-TOKEN-HERE
EOF
```

5. Set file permissions so only your user can read it:
```bash
chmod 600 ~/.cdsapirc
```

*Alternative (Environment Variables):* You may alternatively set `CDSAPI_URL` and `CDSAPI_KEY`:
```bash
export CDSAPI_URL="https://cds.climate.copernicus.eu/api"
export CDSAPI_KEY="YOUR-PERSONAL-ACCESS-TOKEN-HERE"
```

*Security Assurance:* The pipeline will **never** log, print, or expose your API keys in any log file or error trace.

---

## 6. NOAA GFS Acquisition Architecture

Standard GFS GRIB2 operational files are roughly 500 MB per forecast time step. Downloading 168 hours of lead time across multiple cycles would require downloading tens of gigabytes of unnecessary data.

To make the pipeline fast, bandwidth-efficient, and runnable on typical consumer connections, `src/download_gfs.py` implements **Index-Based Byte-Range Downloading**:
1. NOAA Open Data on AWS S3 (`https://noaa-gfs-bdp-pds.s3.amazonaws.com`) publishes an index file (`.idx`) alongside every forecast file.
2. The pipeline downloads the lightweight `.idx` file (~30 KB) and parses the exact byte offsets for:
   - `TMP:2 m above ground`
   - `APCP:surface`
3. The pipeline issues targeted HTTP requests with `Range: bytes=start-end`, retrieving **only the ~1.5 MB slice** containing the exact variables of interest.
4. The downloaded slices are stored as standard, valid GRIB2 files in `data/raw/gfs/` and read directly by `cfgrib` / `xarray`.

---

## 7. Running the Pipeline

### Test Mode (Rapid End-to-End Verification)

To verify all components (downloads, preprocessing, quality assurance, feature extraction, anomaly detection, validation, plotting, and report generation) in under 60 seconds without pulling gigabytes of data:

```bash
# Activate virtual environment
source .venv/bin/activate

# Execute complete pipeline in test mode
python src/run_pipeline.py --test
```

### Full Configured Pipeline Execution

To run the complete evaluation across the date ranges and forecast cycles configured in `config.yaml`:

```bash
python src/run_pipeline.py
```

### Running Automated Unit Tests

```bash
pytest tests/ -v
```

---

## 8. Folder & Directory Structure

```text
weather_forecast_mvp/
├── README.md                      # Comprehensive project documentation
├── requirements.txt               # Pinned Python package dependencies
├── config.yaml                    # Master project configuration file
├── pytest.ini                     # Pytest configuration with pythonpath setup
├── .gitignore                     # Git ignore rules for data, caches, and secrets
│
├── data/
│   ├── raw/
│   │   ├── gfs/                   # Downloaded raw NOAA GFS GRIB2 files
│   │   └── era5/                  # Downloaded raw ECMWF ERA5 NetCDF files
│   └── processed/
│       ├── gfs_clean.csv          # Cleaned district-level GFS forecast records
│       ├── era5_clean.csv         # Cleaned district-level ERA5 reference records
│       ├── era5_features.csv      # Hourly rolling features & anomalies
│       └── era5_daily_features.csv# Daily aggregated statistics (min, max, mean, sum)
│
├── outputs/
│   ├── data_quality_report.csv    # Summary data quality metrics
│   ├── data_quality_report.txt    # Human-readable quality assurance audit
│   ├── detected_anomalies.csv     # Detected statistical anomalies & severity
│   ├── validation_by_lead_time.csv# Forecast error metrics grouped by lead time
│   ├── validation_by_district.csv # Forecast error metrics grouped by district
│   ├── figures/                   # High-resolution (300 DPI) publication figures
│   │   ├── era5_temperature_timeseries.png
│   │   ├── era5_rainfall_timeseries.png
│   │   ├── gfs_temperature_forecast.png
│   │   ├── gfs_vs_era5_comparison.png
│   │   ├── data_coverage_missingness.png
│   │   ├── temp_24h_rolling_mean.png
│   │   ├── temp_7d_rolling_mean.png
│   │   ├── daily_precipitation_totals.png
│   │   ├── precip_7d_accumulation.png
│   │   ├── temperature_anomalies.png
│   │   ├── rainfall_anomalies.png
│   │   ├── detected_anomalies_timeline.png
│   │   └── forecast_error_vs_lead_time.png
│   ├── tables/
│   │   └── validation_summary.csv # Overall dataset verification metrics
│   └── reports/
│       └── week1_week2_summary.md # Executive markdown verification report
│
├── src/
│   ├── __init__.py                # Package initializer
│   ├── download_gfs.py            # GFS acquisition with byte-range slicing
│   ├── download_era5.py           # ERA5 CDS API ingestion and fallback grid
│   ├── preprocess.py              # Grid-point extraction and cleaning
│   ├── data_quality.py            # Automated data QA checks
│   ├── features.py                # Temporal rolling features & aggregations
│   ├── anomaly_detection.py       # Dual Z-Score & Robust MAD screening
│   ├── validate.py                # Lead-time & district verification
│   ├── visualize_week1.py         # Week 1 publication figures
│   ├── visualize_week2.py         # Week 2 publication figures
│   └── run_pipeline.py            # 9-stage end-to-end master orchestrator
│
└── tests/
    ├── test_preprocess.py         # Coordinate search & unit conversion tests
    ├── test_features.py           # Rolling windows & aggregation tests
    └── test_anomaly.py            # Z-Score & Robust MAD mathematical tests
```

---

## 9. Detailed Output Files & Artifacts

| File Path | Description | Key Columns / Content |
| :--- | :--- | :--- |
| `data/processed/gfs_clean.csv` | Standardized GFS forecasts | `district, latitude, longitude, initialization_time, forecast_hour, valid_time, temperature_c, precipitation_mm` |
| `data/processed/era5_clean.csv` | Standardized ERA5 reanalysis | `district, latitude, longitude, valid_time, temperature_c, precipitation_mm` |
| `data/processed/era5_features.csv` | Multi-scale temporal features | Rolling 24h/7d means, accumulations, hourly anomalies, monthly aggregates |
| `data/processed/era5_daily_features.csv` | Daily summaries | Daily min, max, mean temperature, and precipitation totals |
| `outputs/data_quality_report.csv` | Dataset QA metrics | Total rows, missingness %, duplicate counts, physical range limits |
| `outputs/data_quality_report.txt` | Formatted audit report | Human-readable inspection summary |
| `outputs/detected_anomalies.csv` | Flagged extreme candidates | Anomaly classification, Z-scores, Robust Z-scores, severity ranking |
| `outputs/validation_by_lead_time.csv` | Lead-time verification | `forecast_hour, MAE, RMSE, Bias, sample_count` |
| `outputs/validation_by_district.csv` | District verification | `district, MAE, RMSE, Bias, sample_count` |
| `outputs/tables/validation_summary.csv` | Global verification | Overall MAE, RMSE, Bias across all pairs |
| `outputs/reports/week1_week2_summary.md` | Executive report | Final project deliverable with tables and scientific caveats |

---

## 10. Interpretation of Visual Deliverables

All figures are automatically generated in `outputs/figures/` at 300 DPI resolution:

1. **`era5_temperature_timeseries.png`**: Multi-line hourly temperature series demonstrating diurnal thermal rhythms and altitude contrast between subtropical Jammu and temperate Kashmir Valley.
2. **`era5_rainfall_timeseries.png`**: Precipitation events across the four target districts highlighting localized orographic rainfall spikes.
3. **`gfs_temperature_forecast.png`**: Ensemble forecast trajectories showing predicted temperature evolution across initializations.
4. **`gfs_vs_era5_comparison.png`**: Four-panel district comparison overlaying GFS forecasts directly against ERA5 reference truth at matching valid times.
5. **`data_coverage_missingness.png`**: Audit plot displaying total observation counts per district and verifying 0.0% missing data.
6. **`temp_24h_rolling_mean.png`**: Filtered diurnal fluctuations revealing synoptic-scale multi-day temperature trends.
7. **`temp_7d_rolling_mean.png`**: Long-term seasonal progression curve across Jammu & Kashmir.
8. **`daily_precipitation_totals.png`**: Daily rainfall accumulation bar/line trajectories.
9. **`precip_7d_accumulation.png`**: Cumulative multi-day precipitation curves useful for hydrological saturation and flood potential screening.
10. **`temperature_anomalies.png`**: Positive and negative hourly departures (°C) from the district baseline mean.
11. **`rainfall_anomalies.png`**: Rainfall departures from expected baselines indicating localized convective bursts.
12. **`detected_anomalies_timeline.png`**: Spatiotemporal scatter plot mapping when and where severe statistical departures occurred, color-coded by Robust Z-Score severity.
13. **`forecast_error_vs_lead_time.png`**: **Core Minor Project Deliverable.** Demonstrates temperature Mean Absolute Error (MAE in °C) as a function of forecast lead time (0h to 168h), visualizing forecast uncertainty growth over time.

---

## 11. Scientific Verification Metrics: MAE, RMSE, and Bias

For each district and valid time, the forecast verification error is defined as:
$$\text{Error}_i = T_{\text{GFS}, i} - T_{\text{ERA5}, i}$$

### 1. Mean Absolute Error (MAE)
$$\text{MAE} = \frac{1}{N} \sum_{i=1}^N |\text{Error}_i|$$
- **Meaning:** Represents the average magnitude of forecast error in physical units (°C), without regard to direction. It is linear and less sensitive to isolated extreme outliers.

### 2. Root Mean Squared Error (RMSE)
$$\text{RMSE} = \sqrt{\frac{1}{N} \sum_{i=1}^N (\text{Error}_i)^2}$$
- **Meaning:** Measures the quadratic mean of error magnitudes. Because errors are squared before averaging, RMSE penalizes large forecast blunders significantly more heavily than MAE.

### 3. Mean Forecast Bias (Mean Error)
$$\text{Bias} = \frac{1}{N} \sum_{i=1}^N (T_{\text{GFS}, i} - T_{\text{ERA5}, i})$$
- **Meaning:** Indicates systematic overprediction ($\text{Bias} > 0$) or underprediction ($\text{Bias} < 0$) by the GFS model relative to the ERA5 reference.

---

## 12. Forecast Lead Time & Validity Methodology

### CRITICAL METHODOLOGY: Strict Valid-Time Alignment

In numerical weather prediction, comparing a forecast directly against a verification dataset using the initialization timestamp is scientifically invalid.

The pipeline strictly applies the WMO standard valid-time relationship:
$$\text{valid\_time} = \text{initialization\_time} + \text{forecast\_lead\_time}$$

**Example:**
- GFS Cycle: `2026-09-15 00:00:00 UTC`
- Lead Time: `+48 hours`
- **Valid Time:** `2026-09-17 00:00:00 UTC`

This forecast is matched against the ERA5 reanalysis timestamped **strictly at `2026-09-17 00:00:00 UTC`**. The error is then partitioned into the `48h` lead-time bin to measure forecast degradation with horizon.

---

## 13. Statistical Anomaly & Extreme Event Detection

To screen for uncharacteristic atmospheric conditions, the pipeline implements two independent statistical screening algorithms:

### Method 1: Parametric Z-Score
$$Z = \frac{x - \mu}{\sigma}$$
- Flag condition: $|Z| \ge 3.0$ ($\sim 99.7\%$ Gaussian confidence interval).

### Method 2: Robust Z-Score via Median Absolute Deviation (MAD)
Because extreme weather events heavily contaminate the sample mean ($\mu$) and standard deviation ($\sigma$), the pipeline applies a robust non-parametric estimator:
$$\text{MAD} = \text{median}\left(|x - \text{median}(x)|\right)$$
$$\text{Robust } Z = 0.6745 \times \frac{x - \text{median}(x)}{\text{MAD}}$$
- Factor $0.6745$ is the consistency constant for a normal distribution ($1 / 1.4826$).
- Flag condition: $|\text{Robust } Z| \ge 3.5$.

### Scientific Taxonomy
Statistical departures are formally labeled **"statistical anomalies"** and screened as **"potential extreme weather events"**. The system avoids claiming unverified meteorological records without corroborating multi-variable physical evidence.

---

## 14. Scientific Limitations

1. **Reanalysis as Reference:** ECMWF ERA5 blends physical equations with assimilated satellite, radar, and balloon data. While it represents the global standard for reference gridded truth, it is **not identical to ground-truth in-situ weather station observations**.
2. **Provisional Baseline vs. Long-Term Climatology:** The baseline computed from the initial available period is formally designated a **provisional baseline**. True climatological normals require 30-year reference windows (e.g. 1991–2020 WMO standard).
3. **Nearest Grid-Point Representation:** District points are mapped to the nearest 0.25° grid centroid (~27 km resolution). In rugged terrain like Jammu & Kashmir, elevation discrepancies between the grid centroid and specific valley settlements (e.g. Srinagar city vs. surrounding Pir Panjal range) can introduce topographical offsets.
4. **Model Parameterization Differences:** Discrepancies between GFS and ERA5 reflect differences in numerical parameterization schemes (convection, boundary layer, cloud microphysics) as well as atmospheric forecast error.

---

## 15. Future Roadmap & Improvements

- [ ] **IMD Station Ground-Truth:** Ingest India Meteorological Department (IMD) AWS station telemetry across Srinagar, Jammu, Pahalgam, and Gulmarg for empirical ground truth.
- [ ] **Bilinear & Elevation-Corrected Downscaling:** Implement lapse-rate topographic correction to downscale grid temperatures to district station altitudes.
- [ ] **Multi-Model Ensemble Comparison:** Integrate ECMWF IFS HRES and NCMRWF NCUM operational forecasts alongside NOAA GFS.
- [ ] **Spatial Verification Metrics:** Add Fractions Skill Score (FSS) and Structure-Amplitude-Location (SAL) metrics for precipitation verification.

---

## 16. Verification Checklist

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
- [x] Lead-time error breakdown (0h to 168h): MAE, RMSE, Bias in `outputs/validation_by_lead_time.csv`.
- [x] District error breakdown: MAE, RMSE, Bias in `outputs/validation_by_district.csv`.
- [x] Global summary table in `outputs/tables/validation_summary.csv`.
- [x] Week 2 publication figures (including Error vs. Lead Time) at 300 DPI.
- [x] Executive markdown summary report in `outputs/reports/week1_week2_summary.md`.
- [x] Unit test suite passing (`pytest tests/ -v`).
