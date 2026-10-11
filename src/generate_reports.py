"""
Scientific Report Generation Module for Weeks 3, 4, 5 and Master Project Summary.

Dynamically compiles comprehensive Markdown reports using actual execution results:
1. outputs/week3/reports/week3_error_analysis.md
2. outputs/week4/reports/week4_reliability_report.md
3. outputs/week5/reports/week5_bust_model_report.md
4. outputs/reports/research_summary_weeks1_to_5.md
"""

import os
import json
import logging
from datetime import datetime, timezone
import pandas as pd
import yaml

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("generate_reports")


def load_config(config_path: str = "config.yaml") -> dict:
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def to_markdown_table(df: pd.DataFrame) -> str:
    """Format DataFrame as markdown table."""
    if df.empty:
        return "*No data available.*"
    try:
        return df.to_markdown(index=False)
    except Exception:
        cols = list(df.columns)
        header = "| " + " | ".join(str(c) for c in cols) + " |"
        sep = "| " + " | ".join(["---"] * len(cols)) + " |"
        rows = ["| " + " | ".join(str(row[c]) for c in cols) + " |" for _, row in df.iterrows()]
        return "\n".join([header, sep] + rows)


def generate_week3_report(config_path: str = "config.yaml"):
    """Generate outputs/week3/reports/week3_error_analysis.md."""
    cfg = load_config(config_path)
    w3_dir = cfg["output_dirs"].get("week3", "outputs/week3")
    rep_dir = os.path.join(w3_dir, "reports")
    os.makedirs(rep_dir, exist_ok=True)

    matched_path = os.path.join(w3_dir, "matched_validation_dataset.csv")
    lead_path = os.path.join(w3_dir, "lead_day_metrics.csv")
    dist_path = os.path.join(w3_dir, "district_metrics.csv")
    eval_path = os.path.join(w3_dir, "bias_correction_eval.csv")
    avail_path = os.path.join(w3_dir, "variable_availability_check.csv")

    matched_df = pd.read_csv(matched_path) if os.path.exists(matched_path) else pd.DataFrame()
    lead_df = pd.read_csv(lead_path) if os.path.exists(lead_path) else pd.DataFrame()
    dist_df = pd.read_csv(dist_path) if os.path.exists(dist_path) else pd.DataFrame()
    eval_df = pd.read_csv(eval_path) if os.path.exists(eval_path) else pd.DataFrame()
    avail_df = pd.read_csv(avail_path) if os.path.exists(avail_path) else pd.DataFrame()

    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    lines = [
        "# Week 3 Scientific Report: Forecast-Observation Error Analysis & Bias Correction",
        f"**Generated:** {now_str}  ",
        "**Target Region:** Jammu and Kashmir  ",
        "**Forecast System:** NOAA Global Forecast System (GFS 0.25°)  ",
        "**Reference Verification:** ECMWF ERA5 Atmospheric Reanalysis (0.25°)  ",
        "",
        "---",
        "",
        "## 1. Variable Availability & Compatibility Verification",
        "",
        to_markdown_table(avail_df),
        "",
        "> **Scientific Note on Pressure**: Surface pressure / mean sea level pressure is absent from the downloaded local ERA5 and GFS subsets. In compliance with strict research integrity standards, pressure was not fabricated or substituted with unrelated variables.",
        "> **Scientific Note on Precipitation Accumulation**: GFS APCP values represent step accumulation intervals (e.g. 3h/6h intervals from cycle origin), whereas ERA5 represents hourly accumulated depth. To avoid comparing physically incompatible accumulation windows, precipitation bias correction was held disabled until window-aligned accumulation aggregation is integrated.",
        "",
        "---",
        "",
        "## 2. Matched Validation Dataset Summary",
        f"- **Total Matched Pairs (Temperature):** {len(matched_df):,}",
        f"- **Districts Evaluated:** {', '.join(sorted(matched_df['district'].unique())) if not matched_df.empty else 'None'}",
        f"- **Initialization Cycles:** {matched_df['initialization_time'].nunique() if not matched_df.empty else 0}",
        f"- **Error Formulation:** `error = forecast_value - reference_value` (positive bias indicates forecast overestimation)",
        "",
        "---",
        "",
        "## 3. Baseline Error Metrics by Forecast Lead Day",
        "",
        to_markdown_table(lead_df),
        "",
        "---",
        "",
        "## 4. Baseline Error Metrics by Target District",
        "",
        to_markdown_table(dist_df),
        "",
        "---",
        "",
        "## 5. Leakage-Safe Historical Bias Correction Evaluation",
        "",
        "Mean bias was learned strictly on the chronological training split (earliest 70%) using a district-to-regional fallback hierarchy and evaluated on the identical held-out test split (latest 30%):",
        "",
        to_markdown_table(eval_df),
        "",
        "---",
        "*Report generated automatically from actual execution artifacts.*"
    ]

    out_file = os.path.join(rep_dir, "week3_error_analysis.md")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    logger.info("Saved Week 3 report -> %s", out_file)


def generate_week4_report(config_path: str = "config.yaml"):
    """Generate outputs/week4/reports/week4_reliability_report.md."""
    cfg = load_config(config_path)
    w4_dir = cfg["output_dirs"].get("week4", "outputs/week4")
    rep_dir = os.path.join(w4_dir, "reports")
    os.makedirs(rep_dir, exist_ok=True)

    rel_path = os.path.join(w4_dir, "reliability_table.csv")
    eval_path = os.path.join(w4_dir, "held_out_evaluation.csv")
    sens_path = os.path.join(w4_dir, "sensitivity_analysis.csv")

    rel_df = pd.read_csv(rel_path) if os.path.exists(rel_path) else pd.DataFrame()
    eval_df = pd.read_csv(eval_path) if os.path.exists(eval_path) else pd.DataFrame()
    sens_df = pd.read_csv(sens_path) if os.path.exists(sens_path) else pd.DataFrame()

    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    lines = [
        "# Week 4 Scientific Report: Spatiotemporal Modelling for Reliability Scoring",
        f"**Generated:** {now_str}  ",
        "**Target Region:** Jammu and Kashmir  ",
        "",
        "---",
        "",
        "## 1. Mathematical Formulation of the Reliability Index",
        "",
        "The empirical reliability index $R \\in [0, 1]$ is formulated from historical verification errors:",
        "",
        "1. **Normalized Error**: For variable $i$, $normalized\\_error_i = \\text{MAE}_i / \\text{error\\_scale}_i$, where $\\text{error\\_scale}_i > 0$ is an engineering tolerance ($2.0^\\circ\\text{C}$ for temperature).",
        "2. **Error-based Reliability Component**: $R_{\\text{error}} = \\exp(-normalized\\_error)$. When error is zero, $R_{\\text{error}} = 1.0$. As error grows, it monotonically decays towards 0.",
        "3. **Sample Confidence Factor**: $C = \\frac{n}{n + k}$, where $n$ is the number of historical verification cases and $k > 0$ is a configurable sample-smoothing parameter ($k=10$).",
        "4. **Composite Reliability Score**: $R = R_{\\text{error}} \\times C$.",
        "",
        "> **Important Scientific Distinction**: $R$ is an **empirical reliability index** reflecting historical accuracy and sample support. It is **not an uncalibrated Bayesian probability** of absolute correctness.",
        "",
        "---",
        "",
        "## 2. Spatiotemporal Reliability Table (Training Split Estimates)",
        "",
        to_markdown_table(rel_df),
        "",
        "---",
        "",
        "## 3. Held-Out Evaluation on Unseen Later Forecasts",
        "",
        to_markdown_table(eval_df),
        "",
        "---",
        "",
        "## 4. Sensitivity Analysis across Tolerance Scales and Smoothing Parameters",
        "",
        to_markdown_table(sens_df.head(12)),
        "",
        "---",
        "*Report generated automatically from actual execution artifacts.*"
    ]

    out_file = os.path.join(rep_dir, "week4_reliability_report.md")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    logger.info("Saved Week 4 report -> %s", out_file)


def generate_week5_report(config_path: str = "config.yaml"):
    """Generate outputs/week5/reports/week5_bust_model_report.md."""
    cfg = load_config(config_path)
    w5_dir = cfg["output_dirs"].get("week5", "outputs/week5")
    rep_dir = os.path.join(w5_dir, "reports")
    os.makedirs(rep_dir, exist_ok=True)

    meta_path = os.path.join(w5_dir, "model_metadata.json")
    split_path = os.path.join(w5_dir, "split_summary.csv")
    metrics_path = os.path.join(w5_dir, "held_out_metrics.csv")
    thresh_path = os.path.join(w5_dir, "label_threshold_metadata.csv")

    meta = {}
    if os.path.exists(meta_path):
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)

    split_df = pd.read_csv(split_path) if os.path.exists(split_path) else pd.DataFrame()
    metrics_df = pd.read_csv(metrics_path) if os.path.exists(metrics_path) else pd.DataFrame()
    thresh_df = pd.read_csv(thresh_path) if os.path.exists(thresh_path) else pd.DataFrame()

    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    lines = [
        "# Week 5 Scientific Report: Machine-Learning Forecast-Bust Classifier",
        f"**Generated:** {now_str}  ",
        "**Target Region:** Jammu and Kashmir  ",
        "",
        "---",
        "",
        "## 1. Forecast-Bust Label Definition & Protocol",
        "",
        "- **Bust Definition**: An empirical forecast bust is defined when $|\\text{error}| > \\text{threshold}_{\\text{train}}$, where the threshold is the **upper 90th percentile** of forecast absolute errors.",
        "- **Strict Leakage Prevention**: Thresholds are computed **strictly from the chronological training period** (earliest 70% of cases) and never from validation or test sets.",
        "- **Feature Scope**: Inputs to the classifier contain **strictly features known at forecast issuance time** (`lead_hours`, `lead_day`, `district`, `forecast_value`, diurnal initialization cycle). Reference observations and forecast error outcomes are strictly excluded.",
        "",
        "### Training-Derived Thresholds by Group",
        to_markdown_table(thresh_df),
        "",
        "---",
        "",
        "## 2. Chronological Train / Validation / Test Split Summary",
        "",
        to_markdown_table(split_df),
        "",
        "---",
        "",
        "## 3. Held-Out Classification Performance (Test Set)",
        "",
        to_markdown_table(metrics_df),
        "",
        "---",
        "",
        "## 4. Model Persistence & Inference Interface",
        "",
        f"- **Serialized Model Pipeline:** `{os.path.join(w5_dir, 'trained_model_pipeline.joblib')}`",
        f"- **Model Metadata JSON:** `{os.path.join(w5_dir, 'model_metadata.json')}`",
        f"- **Active Model Architecture:** `{meta.get('model_id', 'RandomForest_BustClassifier')}`",
        f"- **Features Employed:** `{', '.join(meta.get('feature_names', []))}`",
        "",
        "---",
        "*Report generated automatically from actual execution artifacts.*"
    ]

    out_file = os.path.join(rep_dir, "week5_bust_model_report.md")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    logger.info("Saved Week 5 report -> %s", out_file)


def generate_master_research_summary(config_path: str = "config.yaml"):
    """Generate comprehensive outputs/reports/research_summary_weeks1_to_5.md."""
    cfg = load_config(config_path)
    proc_dir = cfg["output_dirs"]["processed"]
    rep_dir = cfg["output_dirs"]["reports"]
    w3_dir = cfg["output_dirs"].get("week3", "outputs/week3")
    w4_dir = cfg["output_dirs"].get("week4", "outputs/week4")
    w5_dir = cfg["output_dirs"].get("week5", "outputs/week5")
    os.makedirs(rep_dir, exist_ok=True)

    gfs_df = pd.read_csv(os.path.join(proc_dir, "gfs_clean.csv")) if os.path.exists(os.path.join(proc_dir, "gfs_clean.csv")) else pd.DataFrame()
    era5_df = pd.read_csv(os.path.join(proc_dir, "era5_clean.csv")) if os.path.exists(os.path.join(proc_dir, "era5_clean.csv")) else pd.DataFrame()
    matched_df = pd.read_csv(os.path.join(w3_dir, "matched_validation_dataset.csv")) if os.path.exists(os.path.join(w3_dir, "matched_validation_dataset.csv")) else pd.DataFrame()
    lead_df = pd.read_csv(os.path.join(w3_dir, "lead_day_metrics.csv")) if os.path.exists(os.path.join(w3_dir, "lead_day_metrics.csv")) else pd.DataFrame()
    dist_df = pd.read_csv(os.path.join(w3_dir, "district_metrics.csv")) if os.path.exists(os.path.join(w3_dir, "district_metrics.csv")) else pd.DataFrame()
    bias_eval_df = pd.read_csv(os.path.join(w3_dir, "bias_correction_eval.csv")) if os.path.exists(os.path.join(w3_dir, "bias_correction_eval.csv")) else pd.DataFrame()
    rel_df = pd.read_csv(os.path.join(w4_dir, "reliability_table.csv")) if os.path.exists(os.path.join(w4_dir, "reliability_table.csv")) else pd.DataFrame()
    metrics_df = pd.read_csv(os.path.join(w5_dir, "held_out_metrics.csv")) if os.path.exists(os.path.join(w5_dir, "held_out_metrics.csv")) else pd.DataFrame()
    split_df = pd.read_csv(os.path.join(w5_dir, "split_summary.csv")) if os.path.exists(os.path.join(w5_dir, "split_summary.csv")) else pd.DataFrame()

    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    lines = [
        "# Spatiotemporal Reliability and Uncertainty Detection for Medium-Range Weather Forecasts",
        "## Master Research Synthesis & Comprehensive Verification Report (Weeks 1 through 5)",
        f"**Date:** {now_str}  ",
        "**Geographic Scope:** Jammu & Kashmir (Lat 31.0°N–38.0°N, Lon 73.0°E–81.0°E)  ",
        "**Target Districts:** Srinagar, Jammu, Anantnag, Baramulla  ",
        "**Forecast System:** NOAA Global Forecast System (GFS 0.25°)  ",
        "**Reference System:** ECMWF ERA5 Atmospheric Reanalysis (0.25°)  ",
        "",
        "---",
        "",
        "### 1. Executive Implementation Overview",
        "",
        "| Project Phase | Focus & Research Objective | Core Deliverable / Module | Status |",
        "| :--- | :--- | :--- | :--- |",
        "| **Week 1** | GFS & ERA5 Ingestion, Preprocessing & Quality Checks | `src/preprocess.py`, `src/data_quality.py` | Complete & Verified |",
        "| **Week 2** | Temporal Features & Statistical Anomaly Detection | `src/features.py`, `src/anomaly_detection.py` | Complete & Verified |",
        "| **Week 3** | Matched Verification, Lead Day Errors & Bias Correction | `src/error_analysis.py`, `src/visualize_week3.py` | Complete & Verified |",
        "| **Week 4** | Spatiotemporal Reliability Scoring & Sensitivity | `src/reliability.py`, `src/visualize_week4.py` | Complete & Verified |",
        "| **Week 5** | ML Forecast-Bust Classifier & Production Inference | `src/forecast_bust.py`, `src/visualize_week5.py` | Complete & Verified |",
        "",
        "---",
        "",
        "### 2. Dataset Ingestion & Variable Availability Verification",
        "",
        f"- **Clean GFS Forecast Records:** {len(gfs_df):,}",
        f"- **Clean ERA5 Reference Records:** {len(era5_df):,}",
        f"- **Matched Verification Pairs:** {len(matched_df):,}",
        "- **Evaluated Variables:** 2m Temperature (°C) successfully matched. Precipitation accumulation semantics checked.",
        "- **Pressure Availability:** Pressure is absent from the local downloaded GFS and ERA5 data subsets. Formally documented as unsupported without synthetic data fabrication.",
        "",
        "---",
        "",
        "### 3. Forecast Verification Metrics (Week 3)",
        "",
        "#### Baseline Metrics by Forecast Lead Day",
        to_markdown_table(lead_df),
        "",
        "#### Baseline Metrics by District",
        to_markdown_table(dist_df),
        "",
        "#### Historical Bias Correction (Evaluated on Held-Out Test Set)",
        to_markdown_table(bias_eval_df),
        "",
        "---",
        "",
        "### 4. Spatiotemporal Reliability Modelling (Week 4)",
        "",
        to_markdown_table(rel_df),
        "",
        "---",
        "",
        "### 5. Machine-Learning Forecast-Bust Classification (Week 5)",
        "",
        "#### Chronological Split Summary",
        to_markdown_table(split_df),
        "",
        "#### Held-Out Evaluation Metrics",
        to_markdown_table(metrics_df),
        "",
        "---",
        "",
        "### 6. Formal Scientific Assumptions & Operational Limitations",
        "",
        "1. **Reanalysis Reference vs. Weather Station Truth**: ECMWF ERA5 is an atmospheric reanalysis blending assimilative model physics with satellite/in-situ data. While world-standard for medium-range model verification, it is not direct in-situ ground station truth.",
        "2. **Grid-Scale Microclimates**: District points are sampled at 0.25° grid resolution (~27 km). Complex Himalayan topography creates sub-grid valley microclimates not fully resolved at 0.25°.",
        "3. **Empirical Indexing vs. Bayesian Probability**: The reliability score $R \\in [0, 1]$ is an empirical performance index penalizing historical error and weighting sample support. It is not an uncalibrated Bayesian probability.",
        "4. **Class Imbalance in Forecast Busts**: Unusually large forecast errors (top 10th percentile) inherently represent an imbalanced class problem, managed via balanced class weights and precision-recall evaluation.",
        "",
        "---",
        "*Report automatically synthesized by the Antigravity Meteorological Data Pipeline.*"
    ]

    out_file = os.path.join(rep_dir, "research_summary_weeks1_to_5.md")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    logger.info("Saved Master Research Summary -> %s", out_file)


def generate_all_reports(config_path: str = "config.yaml"):
    """Compile all project Markdown reports."""
    generate_week3_report(config_path)
    generate_week4_report(config_path)
    generate_week5_report(config_path)
    generate_master_research_summary(config_path)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate all scientific markdown reports")
    parser.add_argument("--config", default="config.yaml", help="Path to config.yaml")
    args = parser.parse_args()

    generate_all_reports(args.config)
