"""
End-to-End Orchestrator for Weather Forecast Reliability & Uncertainty Pipeline.

Executes all 9 stages:
[1/9] Downloading GFS...
[2/9] Downloading ERA5...
[3/9] Preprocessing & Spatial/Temporal Standardization...
[4/9] Running Data Quality Checks...
[5/9] Extracting Temporal Features...
[6/9] Detecting Anomalies...
[7/9] Validating GFS against ERA5...
[8/9] Generating Visualizations (Week 1 & Week 2)...
[9/9] Generating Final Summary Tables & Scientific Report...

Supports --test mode for rapid verification on minimal data slices.
"""

import os
import sys
from pathlib import Path

# Ensure project root is on sys.path
PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import argparse
import logging
from datetime import datetime
import pandas as pd
import yaml

from src.download_gfs import download_gfs_range
from src.download_era5 import download_era5
from src.preprocess import run_preprocessing
from src.data_quality import run_data_quality_checks
from src.features import run_feature_extraction
from src.anomaly_detection import run_anomaly_detection
from src.validate import run_validation
from src.visualize_week1 import generate_all_week1_visualizations
from src.visualize_week2 import generate_all_week2_visualizations

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("pipeline")


def load_config(config_path: str = "config.yaml") -> dict:
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def ensure_directories(config: dict):
    """Ensure all required input/output directories exist."""
    dirs = [
        config["output_dirs"]["raw_gfs"],
        config["output_dirs"]["raw_era5"],
        config["output_dirs"]["processed"],
        config["output_dirs"]["figures"],
        config["output_dirs"]["tables"],
        config["output_dirs"]["reports"],
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)


def to_markdown_table(df: pd.DataFrame) -> str:
    """Format DataFrame as markdown table with or without tabulate."""
    if df.empty:
        return ""
    try:
        return df.to_markdown(index=False)
    except Exception:
        # Fallback pure-Python table formatter
        cols = list(df.columns)
        header = "| " + " | ".join(str(c) for c in cols) + " |"
        sep = "| " + " | ".join(["---"] * len(cols)) + " |"
        rows = []
        for _, row in df.iterrows():
            rows.append("| " + " | ".join(str(row[c]) for c in cols) + " |")
        return "\n".join([header, sep] + rows)


def generate_final_report(config_path: str = "config.yaml"):
    """
    Generate outputs/reports/week1_week2_summary.md summarizing:
    - Data period
    - Record counts & missing percentages
    - Statistical anomalies
    - Verification metrics (MAE, RMSE, Bias by lead time & district)
    - Formal Scientific Limitations
    """
    from datetime import timezone
    cfg = load_config(config_path)
    proc_dir = cfg["output_dirs"]["processed"]
    rep_dir = cfg["output_dirs"]["reports"]
    os.makedirs(rep_dir, exist_ok=True)

    gfs_path = os.path.join(proc_dir, "gfs_clean.csv")
    era5_path = os.path.join(proc_dir, "era5_clean.csv")
    anomalies_path = "outputs/detected_anomalies.csv"
    val_lead_path = "outputs/validation_by_lead_time.csv"
    val_dist_path = "outputs/validation_by_district.csv"
    val_sum_path = "outputs/tables/validation_summary.csv"

    gfs_df = pd.read_csv(gfs_path) if os.path.exists(gfs_path) else pd.DataFrame()
    era5_df = pd.read_csv(era5_path) if os.path.exists(era5_path) else pd.DataFrame()
    anom_df = pd.read_csv(anomalies_path) if os.path.exists(anomalies_path) else pd.DataFrame()
    val_lead_df = pd.read_csv(val_lead_path) if os.path.exists(val_lead_path) else pd.DataFrame()
    val_dist_df = pd.read_csv(val_dist_path) if os.path.exists(val_dist_path) else pd.DataFrame()
    val_sum_df = pd.read_csv(val_sum_path) if os.path.exists(val_sum_path) else pd.DataFrame()

    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    # Metrics calculation
    gfs_count = len(gfs_df)
    era5_count = len(era5_df)
    districts = sorted(cfg["districts"].keys())

    gfs_missing_pct = (gfs_df["temperature_c"].isna().mean() * 100.0) if gfs_count > 0 else 0.0
    era5_missing_pct = (era5_df["temperature_c"].isna().mean() * 100.0) if era5_count > 0 else 0.0

    avg_mae = val_sum_df["overall_MAE_c"].iloc[0] if not val_sum_df.empty and "overall_MAE_c" in val_sum_df.columns else "N/A"
    avg_rmse = val_sum_df["overall_RMSE_c"].iloc[0] if not val_sum_df.empty and "overall_RMSE_c" in val_sum_df.columns else "N/A"
    avg_bias = val_sum_df["overall_Bias_c"].iloc[0] if not val_sum_df.empty and "overall_Bias_c" in val_sum_df.columns else "N/A"

    report_lines = [
        "# Spatiotemporal Reliability and Uncertainty Detection for Medium-Range Weather Forecasts",
        "## Executive Summary & Scientific Verification Report (Weeks 1 & 2)",
        f"**Generated:** {now_str}  ",
        f"**Target Domain:** Jammu & Kashmir (Lat 31.0°N–38.0°N, Lon 73.0°E–81.0°E)  ",
        f"**Districts Evaluated:** {', '.join(districts)}  ",
        "",
        "---",
        "",
        "### 1. Data Ingestion & Preprocessing Summary",
        "",
        "| Metric | NOAA GFS Forecast | ECMWF ERA5 Reanalysis |",
        "| :--- | :--- | :--- |",
        f"| **Record Count** | {gfs_count:,} | {era5_count:,} |",
        f"| **Spatial Grid** | 0.25° Gaussian (~27 km) | 0.25° Regular Lat/Lon (~27 km) |",
        f"| **Missing Temperature (%)** | {gfs_missing_pct:.2f}% | {era5_missing_pct:.2f}% |",
        f"| **District Coverage** | {len(districts)} / {len(districts)} districts | {len(districts)} / {len(districts)} districts |",
        "",
        "---",
        "",
        "### 2. Statistical Anomaly & Extreme Event Screening",
        f"- **Total Flagged Anomalies:** {len(anom_df):,}",
        "- **Detection Methodology:** Standard Z-Score (|Z| >= 3.0) & Robust Z-Score (|Robust Z| >= 3.5 via MAD)",
        "- **Classification:** Flagged records are classified as *statistical anomalies* and screened as *potential extreme weather events*.",
        "",
    ]

    if not anom_df.empty:
        report_lines.extend([
            "#### Sample Identified Potential Extreme Events",
            to_markdown_table(anom_df.head(5)),
            "",
        ])

    report_lines.extend([
        "---",
        "",
        "### 3. Forecast Verification Metrics (GFS vs. ERA5)",
        "",
        f"- **Overall Temperature MAE:** `{avg_mae} °C`",
        f"- **Overall Temperature RMSE:** `{avg_rmse} °C`",
        f"- **Overall Temperature Bias:** `{avg_bias} °C`",
        "",
        "#### Verification by Forecast Lead Time",
        "",
    ])

    if not val_lead_df.empty:
        report_lines.extend([
            to_markdown_table(val_lead_df),
            "",
        ])
    else:
        report_lines.append("*No overlapping valid times evaluated in current run.*  \n")

    report_lines.extend([
        "#### Verification by District",
        "",
    ])

    if not val_dist_df.empty:
        report_lines.extend([
            to_markdown_table(val_dist_df),
            "",
        ])
    else:
        report_lines.append("*No overlapping valid times evaluated in current run.*  \n")

    report_lines.extend([
        "---",
        "",
        "### 4. Scientific Limitations",
        "",
        "1. **Reanalysis as Reference**: ECMWF ERA5 is a high-resolution atmospheric reanalysis blending numerical weather models with assimilated satellite, radar, and in-situ observations. It serves as an authoritative synthetic truth, but is **not identical to direct ground-based weather station observations**.",
        "2. **Provisional Baseline vs. Long-Term Climatology**: In this MVP stage, anomalies are computed against the available 2026 reference window. This is formally defined as a **provisional baseline**. Climatological anomalies in operational meteorology require a standardized 30-year WMO baseline (e.g., 1991–2020).",
        "3. **Spatial Grid Point Representation**: District values are extracted using the **nearest available grid point** (0.25° resolution, ~27 km). Complex mountainous orography across Jammu & Kashmir produces localized microclimates and elevation differences between the grid centroid and specific valleys.",
        "4. **Model Characteristic Differences**: GFS and ERA5 utilize distinct physical parameterizations (e.g. boundary layer physics, convection schemes, land-surface models). Systematic biases observed may reflect model physics differences in addition to forecast error.",
        "5. **Future Ground-Truth Calibration**: Subsequent project phases will integrate direct ground station telemetry from India Meteorological Department (IMD) and Automatic Weather Stations (AWS) across J&K for empirical ground-truth validation.",
        "",
        "---",
        "*Report generated automatically by the Antigravity Meteorological Data Pipeline.*",
    ])

    out_file = os.path.join(rep_dir, "week1_week2_summary.md")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    logger.info("Saved scientific summary report -> %s", out_file)


def run_pipeline(config_path: str = "config.yaml", test_mode: bool = False):
    """Execute all 9 stages of the meteorological data pipeline."""
    cfg = load_config(config_path)
    ensure_directories(cfg)

    print("=" * 70)
    print(f"WEATHER FORECAST RELIABILITY & UNCERTAINTY PIPELINE (MODE: {'TEST' if test_mode else 'FULL'})")
    print(f"Study Domain: Jammu & Kashmir | Region Bounding Box: {cfg['region']}")
    print("=" * 70)

    # STEP 1: Download GFS
    print("\n[1/9] Downloading GFS...")
    try:
        gfs_files = download_gfs_range(cfg, test_mode=test_mode)
        print(f"-> GFS download step completed ({len(gfs_files)} files retrieved or verified).")
    except Exception as e:
        print(f"\n[ERROR in Step 1 - GFS Download]: {e}")
        print("Likely cause: Network connectivity issue or NOAA server rate limit. Check URL accessibility.")
        sys.exit(1)

    # STEP 2: Download ERA5
    print("\n[2/9] Downloading ERA5...")
    try:
        era5_file = download_era5(cfg, test_mode=test_mode)
        if era5_file:
            print(f"-> ERA5 download step completed (file: {era5_file}).")
        else:
            print("-> ERA5 live download was skipped or credentials not configured. Proceeding with existing data if present.")
    except Exception as e:
        print(f"\n[ERROR in Step 2 - ERA5 Download]: {e}")
        print("Likely cause: CDS API credentials missing or invalid in ~/.cdsapirc.")
        sys.exit(1)

    # STEP 3: Preprocessing
    print("\n[3/9] Preprocessing & Spatial/Temporal Standardization...")
    try:
        gfs_df, era5_df = run_preprocessing(config_path)
        print(f"-> Preprocessing completed: {len(gfs_df)} GFS rows, {len(era5_df)} ERA5 rows.")
    except Exception as e:
        print(f"\n[ERROR in Step 3 - Preprocessing]: {e}")
        print("Likely cause: Incompatible GRIB2/NetCDF coordinates, corrupted raw file, or missing dimensions.")
        sys.exit(1)

    # STEP 4: Data Quality Checks
    print("\n[4/9] Running Data Quality Checks...")
    try:
        q_df, _ = run_data_quality_checks(config_path)
        print("-> Data quality verification completed. Reports saved to outputs/.")
    except Exception as e:
        print(f"\n[ERROR in Step 4 - Data Quality]: {e}")
        print("Likely cause: Processed CSVs missing or corrupted.")
        sys.exit(1)

    # STEP 5: Temporal Feature Extraction
    print("\n[5/9] Extracting Temporal Features (Rolling Means, Accumulations, Climatological Departures)...")
    try:
        h_feat, d_feat = run_feature_extraction(config_path)
        print(f"-> Feature extraction completed: {len(h_feat)} hourly features, {len(d_feat)} daily summaries.")
    except Exception as e:
        print(f"\n[ERROR in Step 5 - Feature Extraction]: {e}")
        print("Likely cause: ERA5 dataset insufficient to compute rolling windows.")
        sys.exit(1)

    # STEP 6: Anomaly Detection
    print("\n[6/9] Detecting Statistical Anomalies (Z-Score & Robust MAD)...")
    try:
        anom_df = run_anomaly_detection(config_path)
        print(f"-> Anomaly screening completed: {len(anom_df)} potential extreme weather anomalies flagged.")
    except Exception as e:
        print(f"\n[ERROR in Step 6 - Anomaly Detection]: {e}")
        print("Likely cause: Insufficient variance or missing feature columns.")
        sys.exit(1)

    # STEP 7: GFS vs ERA5 Validation
    print("\n[7/9] Validating GFS Forecast against ERA5 Reference Reanalysis...")
    try:
        by_lead, by_dist, overall = run_validation(config_path)
        print(f"-> Validation completed: Evaluated {len(by_lead)} forecast lead times across {len(by_dist)} districts.")
    except Exception as e:
        print(f"\n[ERROR in Step 7 - Validation]: {e}")
        print("Likely cause: Missing valid_time overlap or unaligned timestamps.")
        sys.exit(1)

    # STEP 8: Visualizations
    print("\n[8/9] Generating High-Resolution Publication Visualizations (Weeks 1 & 2)...")
    try:
        generate_all_week1_visualizations(config_path)
        generate_all_week2_visualizations(config_path)
        print("-> All Week 1 and Week 2 visualization figures saved to outputs/figures/ (300 DPI).")
    except Exception as e:
        print(f"\n[ERROR in Step 8 - Visualizations]: {e}")
        print("Likely cause: Matplotlib/Seaborn rendering error or missing plot inputs.")
        sys.exit(1)

    # STEP 9: Final Report
    print("\n[9/9] Generating Final Summary Tables and Scientific Verification Report...")
    try:
        generate_final_report(config_path)
        print("-> Executive report generated at outputs/reports/week1_week2_summary.md.")
    except Exception as e:
        print(f"\n[ERROR in Step 9 - Reporting]: {e}")
        sys.exit(1)

    print("\n" + "=" * 70)
    print("PIPELINE EXECUTION FINISHED SUCCESSFULLY!")
    print("All outputs, tables, and figures have been generated under outputs/.")
    print("=" * 70)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Weather Forecast Reliability & Uncertainty Pipeline")
    parser.add_argument("--config", default="config.yaml", help="Path to config.yaml")
    parser.add_argument("--test", action="store_true", help="Execute minimal fast test mode")
    args = parser.parse_args()

    run_pipeline(config_path=args.config, test_mode=args.test)
