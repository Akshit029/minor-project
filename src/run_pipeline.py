"""
End-to-End Orchestrator for Weather Forecast Reliability & Uncertainty Pipeline.

Executes all 14 stages across Weeks 1 through 5:
[1/14] Downloading GFS Forecast Data
[2/14] Downloading ERA5 Reanalysis Reference
[3/14] Preprocessing & Spatial/Temporal Standardization
[4/14] Data Quality Verification & Screening
[5/14] Temporal Feature Extraction (Rolling Means & Departures)
[6/14] Statistical Anomaly Detection (Z-Score & Robust MAD)
[7/14] Baseline GFS vs ERA5 Verification
[8/14] Week 3 Forecast Error Analysis & Bias Correction
[9/14] Week 4 Spatiotemporal Reliability Scoring & Sensitivity
[10/14] Week 5 Machine-Learning Forecast-Bust Classifier Training
[11/14] Week 1 & 2 High-Resolution Visualizations
[12/14] Week 3 Visualizations (Error Curves, Distributions, Bias Correction)
[13/14] Week 4 Visualizations (Reliability Curves, Spatiotemporal Heatmap)
[14/14] Week 5 Visualizations (PR Curves, Confusion Matrix, Feature Importance)
[+] Dynamic Generation of Scientific Reports & Master Summary

Supports:
- --test: Minimal test mode for rapid execution
- --skip-download: Run analysis directly on existing local data without network requests
- --stage: Run specific individual stage or 'all'
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
from datetime import datetime, timezone
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
from src.error_analysis import run_week3_analysis
from src.visualize_week3 import generate_all_week3_visualizations
from src.reliability import run_week4_reliability
from src.visualize_week4 import generate_all_week4_visualizations
from src.forecast_bust import run_week5_forecast_bust
from src.visualize_week5 import generate_all_week5_visualizations
from src.generate_reports import generate_all_reports

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("pipeline")


def load_config(config_path: str = "config.yaml") -> dict:
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def ensure_directories(config: dict):
    """Ensure all required input and output directories exist."""
    dirs = [
        config["output_dirs"]["raw_gfs"],
        config["output_dirs"]["raw_era5"],
        config["output_dirs"]["processed"],
        config["output_dirs"]["figures"],
        config["output_dirs"]["tables"],
        config["output_dirs"]["reports"],
        config["output_dirs"].get("week3", "outputs/week3"),
        config["output_dirs"].get("week3_figures", "outputs/week3/figures"),
        config["output_dirs"].get("week4", "outputs/week4"),
        config["output_dirs"].get("week4_figures", "outputs/week4/figures"),
        config["output_dirs"].get("week5", "outputs/week5"),
        config["output_dirs"].get("week5_figures", "outputs/week5/figures"),
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)


def run_pipeline(
    config_path: str = "config.yaml",
    test_mode: bool = False,
    skip_download: bool = False,
    stage: str = "all"
):
    """Execute complete weather forecast reliability pipeline or specified stage."""
    cfg = load_config(config_path)
    ensure_directories(cfg)

    stage_status = {}

    print("=" * 75)
    print(f"WEATHER FORECAST RELIABILITY & UNCERTAINTY PIPELINE")
    print(f"Mode: {'TEST' if test_mode else 'FULL'} | Stage: {stage.upper()} | Skip Download: {skip_download}")
    print(f"Domain: Jammu & Kashmir | Bounding Box: {cfg['region']['name']}")
    print("=" * 75)

    # 1. Download GFS
    if stage in ["all", "download", "gfs"]:
        print("\n[1/14] Checking / Downloading GFS Data...")
        if skip_download:
            print("-> Skipping GFS network download (--skip-download active). Using local raw GFS data.")
            stage_status["1_download_gfs"] = "SKIPPED (Used Local Data)"
        else:
            try:
                gfs_files = download_gfs_range(cfg, test_mode=test_mode)
                print(f"-> GFS download ready ({len(gfs_files)} files retrieved or verified).")
                stage_status["1_download_gfs"] = f"COMPLETED ({len(gfs_files)} files)"
            except Exception as e:
                print(f"[WARNING in GFS Download]: {e}. Attempting to use existing local files.")
                stage_status["1_download_gfs"] = f"PARTIAL/FALLBACK: {e}"
    else:
        stage_status["1_download_gfs"] = "SKIPPED (Stage Filter)"

    # 2. Download ERA5
    if stage in ["all", "download", "era5"]:
        print("\n[2/14] Checking / Downloading ERA5 Data...")
        if skip_download:
            print("-> Skipping ERA5 network download (--skip-download active). Using local raw ERA5 data.")
            stage_status["2_download_era5"] = "SKIPPED (Used Local Data)"
        else:
            try:
                era5_file = download_era5(cfg, test_mode=test_mode)
                if era5_file:
                    print(f"-> ERA5 file ready: {era5_file}.")
                    stage_status["2_download_era5"] = "COMPLETED"
                else:
                    print("-> Live ERA5 download skipped. Proceeding with existing local NetCDF file.")
                    stage_status["2_download_era5"] = "FALLBACK (Local Data)"
            except Exception as e:
                print(f"[WARNING in ERA5 Download]: {e}. Attempting to use existing local NetCDF.")
                stage_status["2_download_era5"] = f"FALLBACK: {e}"
    else:
        stage_status["2_download_era5"] = "SKIPPED (Stage Filter)"

    # 3. Preprocessing
    if stage in ["all", "preprocess"]:
        print("\n[3/14] Preprocessing & Spatial/Temporal Standardization...")
        try:
            gfs_df, era5_df = run_preprocessing(config_path)
            print(f"-> Preprocessing completed: {len(gfs_df)} GFS rows, {len(era5_df)} ERA5 rows.")
            stage_status["3_preprocessing"] = f"COMPLETED ({len(gfs_df)} GFS, {len(era5_df)} ERA5)"
        except Exception as e:
            print(f"[ERROR in Preprocessing]: {e}")
            stage_status["3_preprocessing"] = f"FAILED: {e}"
            sys.exit(1)
    else:
        stage_status["3_preprocessing"] = "SKIPPED"

    # 4. Data Quality Checks
    if stage in ["all", "quality"]:
        print("\n[4/14] Running Data Quality Checks...")
        try:
            run_data_quality_checks(config_path)
            print("-> Data quality verification reports saved to outputs/.")
            stage_status["4_data_quality"] = "COMPLETED"
        except Exception as e:
            print(f"[ERROR in Data Quality]: {e}")
            stage_status["4_data_quality"] = f"FAILED: {e}"
    else:
        stage_status["4_data_quality"] = "SKIPPED"

    # 5. Temporal Feature Extraction
    if stage in ["all", "features"]:
        print("\n[5/14] Extracting Temporal Features (Rolling Means & Departures)...")
        try:
            h_feat, d_feat = run_feature_extraction(config_path)
            print(f"-> Features extracted: {len(h_feat)} hourly features, {len(d_feat)} daily aggregations.")
            stage_status["5_features"] = f"COMPLETED ({len(h_feat)} hourly, {len(d_feat)} daily)"
        except Exception as e:
            print(f"[ERROR in Feature Extraction]: {e}")
            stage_status["5_features"] = f"FAILED: {e}"
    else:
        stage_status["5_features"] = "SKIPPED"

    # 6. Statistical Anomaly Detection
    if stage in ["all", "anomaly"]:
        print("\n[6/14] Detecting Statistical Anomalies (Z-Score & Robust MAD)...")
        try:
            anom_df = run_anomaly_detection(config_path)
            print(f"-> Statistical anomalies flagged: {len(anom_df)} events.")
            stage_status["6_anomaly_detection"] = f"COMPLETED ({len(anom_df)} anomalies)"
        except Exception as e:
            print(f"[ERROR in Anomaly Detection]: {e}")
            stage_status["6_anomaly_detection"] = f"FAILED: {e}"
    else:
        stage_status["6_anomaly_detection"] = "SKIPPED"

    # 7. Baseline Validation (Legacy Week 1/2)
    if stage in ["all", "validate"]:
        print("\n[7/14] Validating GFS against ERA5 (Baseline)...")
        try:
            run_validation(config_path)
            print("-> Baseline validation completed.")
            stage_status["7_baseline_validation"] = "COMPLETED"
        except Exception as e:
            print(f"[ERROR in Baseline Validation]: {e}")
            stage_status["7_baseline_validation"] = f"FAILED: {e}"
    else:
        stage_status["7_baseline_validation"] = "SKIPPED"

    # 8. Week 3: Forecast Error Analysis & Bias Correction
    if stage in ["all", "week3", "error_analysis"]:
        print("\n[8/14] Running Week 3 Forecast Error Analysis & Historical Bias Correction...")
        try:
            w3_res = run_week3_analysis(config_path)
            n_matched = len(w3_res["matched_df"])
            print(f"-> Week 3 completed: {n_matched} matched pairs evaluated across lead days 1-10.")
            stage_status["8_week3_error_analysis"] = f"COMPLETED ({n_matched} matched pairs)"
        except Exception as e:
            print(f"[ERROR in Week 3 Error Analysis]: {e}")
            stage_status["8_week3_error_analysis"] = f"FAILED: {e}"
            sys.exit(1)
    else:
        stage_status["8_week3_error_analysis"] = "SKIPPED"

    # 9. Week 4: Spatiotemporal Reliability Scoring
    if stage in ["all", "week4", "reliability"]:
        print("\n[9/14] Running Week 4 Spatiotemporal Reliability Scoring & Sensitivity...")
        try:
            w4_res = run_week4_reliability(config_path)
            n_rel = len(w4_res["reliability_table"])
            print(f"-> Week 4 completed: {n_rel} spatiotemporal reliability score cells estimated.")
            stage_status["9_week4_reliability"] = f"COMPLETED ({n_rel} cells)"
        except Exception as e:
            print(f"[ERROR in Week 4 Reliability Scoring]: {e}")
            stage_status["9_week4_reliability"] = f"FAILED: {e}"
            sys.exit(1)
    else:
        stage_status["9_week4_reliability"] = "SKIPPED"

    # 10. Week 5: Machine-Learning Forecast-Bust Classifier
    if stage in ["all", "week5", "bust_model"]:
        print("\n[10/14] Training & Evaluating Week 5 Forecast-Bust Classifier...")
        try:
            w5_res = run_week5_forecast_bust(config_path)
            print(f"-> Week 5 completed: Trained and serialized {w5_res['best_pipeline'].named_steps['classifier'].__class__.__name__}.")
            stage_status["10_week5_bust_classifier"] = "COMPLETED"
        except Exception as e:
            print(f"[ERROR in Week 5 Forecast-Bust Model]: {e}")
            stage_status["10_week5_bust_classifier"] = f"FAILED: {e}"
            sys.exit(1)
    else:
        stage_status["10_week5_bust_classifier"] = "SKIPPED"

    # 11. Week 1 & 2 Visualizations
    if stage in ["all", "visualize", "viz_week12"]:
        print("\n[11/14] Generating Week 1 & 2 High-Resolution Visualizations...")
        try:
            generate_all_week1_visualizations(config_path)
            generate_all_week2_visualizations(config_path)
            print("-> Saved Week 1 & 2 figures to outputs/figures/.")
            stage_status["11_visualize_week1_2"] = "COMPLETED"
        except Exception as e:
            print(f"[WARNING in Week 1/2 Visualizations]: {e}")
            stage_status["11_visualize_week1_2"] = f"PARTIAL: {e}"
    else:
        stage_status["11_visualize_week1_2"] = "SKIPPED"

    # 12. Week 3 Visualizations
    if stage in ["all", "visualize", "week3", "viz_week3"]:
        print("\n[12/14] Generating Week 3 Error & Bias Correction Figures...")
        try:
            generate_all_week3_visualizations(config_path)
            print("-> Saved Week 3 figures to outputs/week3/figures/.")
            stage_status["12_visualize_week3"] = "COMPLETED"
        except Exception as e:
            print(f"[WARNING in Week 3 Visualizations]: {e}")
            stage_status["12_visualize_week3"] = f"PARTIAL: {e}"
    else:
        stage_status["12_visualize_week3"] = "SKIPPED"

    # 13. Week 4 Visualizations
    if stage in ["all", "visualize", "week4", "viz_week4"]:
        print("\n[13/14] Generating Week 4 Reliability & Heatmap Figures...")
        try:
            generate_all_week4_visualizations(config_path)
            print("-> Saved Week 4 figures to outputs/week4/figures/.")
            stage_status["13_visualize_week4"] = "COMPLETED"
        except Exception as e:
            print(f"[WARNING in Week 4 Visualizations]: {e}")
            stage_status["13_visualize_week4"] = f"PARTIAL: {e}"
    else:
        stage_status["13_visualize_week4"] = "SKIPPED"

    # 14. Week 5 Visualizations
    if stage in ["all", "visualize", "week5", "viz_week5"]:
        print("\n[14/14] Generating Week 5 PR Curves & Model Comparison Figures...")
        try:
            generate_all_week5_visualizations(config_path)
            print("-> Saved Week 5 figures to outputs/week5/figures/.")
            stage_status["14_visualize_week5"] = "COMPLETED"
        except Exception as e:
            print(f"[WARNING in Week 5 Visualizations]: {e}")
            stage_status["14_visualize_week5"] = f"PARTIAL: {e}"
    else:
        stage_status["14_visualize_week5"] = "SKIPPED"

    # Reports Compilation
    if stage in ["all", "reports"]:
        print("\n[+] Dynamically Compiling All Scientific Markdown Reports...")
        try:
            generate_all_reports(config_path)
            print("-> All reports compiled under outputs/week3/reports/, outputs/week4/reports/, outputs/week5/reports/, and outputs/reports/.")
            stage_status["reports_generation"] = "COMPLETED"
        except Exception as e:
            print(f"[ERROR in Report Generation]: {e}")
            stage_status["reports_generation"] = f"FAILED: {e}"
    else:
        stage_status["reports_generation"] = "SKIPPED"

    print("\n" + "=" * 75)
    print("PIPELINE EXECUTION STAGE SUMMARY")
    print("=" * 75)
    for st, stat in stage_status.items():
        print(f"  * {st:<28} : {stat}")
    print("=" * 75)
    print("PIPELINE EXECUTION FINISHED SUCCESSFULLY!\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Weather Forecast Reliability & Uncertainty Pipeline (Weeks 1-5)")
    parser.add_argument("--config", default="config.yaml", help="Path to config.yaml")
    parser.add_argument("--test", action="store_true", help="Execute minimal fast test mode")
    parser.add_argument("--skip-download", action="store_true", help="Skip downloading fresh data and reuse local files")
    parser.add_argument(
        "--stage", default="all",
        choices=["all", "download", "preprocess", "quality", "features", "anomaly", "validate",
                 "week3", "week4", "week5", "visualize", "reports"],
        help="Specify individual stage to run or 'all'"
    )
    args = parser.parse_args()

    run_pipeline(
        config_path=args.config,
        test_mode=args.test,
        skip_download=args.skip_download,
        stage=args.stage
    )
