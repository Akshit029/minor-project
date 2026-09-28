"""
Data Quality Assessment & Verification Module.

Computes comprehensive quality metrics across cleaned GFS and ERA5 datasets:
- Row counts and duplicate checks
- Missingness statistics and percentages
- Physical boundary violations
- Statistical extremes (Min, Max, Mean, Median)
- Spatiotemporal coverage (Districts, Date Spans)

Outputs:
- outputs/data_quality_report.csv
- outputs/data_quality_report.txt
"""

import os
import logging
from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd
import yaml

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("data_quality")


def load_config(config_path: str = "config.yaml") -> dict:
    """Load project YAML configuration."""
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def analyze_dataset_quality(df: pd.DataFrame, dataset_name: str, config: dict) -> Dict[str, Any]:
    """
    Compute data quality metrics for a single cleaned dataset.
    """
    if df.empty:
        return {
            "dataset": dataset_name,
            "total_rows": 0,
            "duplicate_rows": 0,
            "missing_temp_count": 0,
            "missing_temp_pct": 0.0,
            "missing_precip_count": 0,
            "missing_precip_pct": 0.0,
            "temp_min_c": np.nan,
            "temp_max_c": np.nan,
            "temp_mean_c": np.nan,
            "precip_min_mm": np.nan,
            "precip_max_mm": np.nan,
            "precip_mean_mm": np.nan,
            "invalid_values_count": 0,
            "start_date": "N/A",
            "end_date": "N/A",
            "date_span_days": 0,
            "districts_covered": 0,
            "district_list": "None",
        }

    total_rows = len(df)
    dup_cols = ["district", "valid_time"] if "forecast_hour" not in df.columns else ["district", "initialization_time", "forecast_hour"]
    duplicate_rows = int(df.duplicated(subset=dup_cols).sum())

    missing_temp = int(df["temperature_c"].isna().sum())
    missing_precip = int(df["precipitation_mm"].isna().sum())

    q_cfg = config.get("quality", {})
    t_min = q_cfg.get("temp_min_c", -40.0)
    t_max = q_cfg.get("temp_max_c", 55.0)
    p_min = q_cfg.get("precip_min_mm", 0.0)
    p_max = q_cfg.get("precip_max_mm", 500.0)

    # Physical boundary violations on valid numbers
    valid_t = df["temperature_c"].dropna()
    valid_p = df["precipitation_mm"].dropna()

    invalid_temp_count = int(((valid_t < t_min) | (valid_t > t_max)).sum())
    invalid_precip_count = int(((valid_p < p_min) | (valid_p > p_max)).sum())
    invalid_total = invalid_temp_count + invalid_precip_count

    time_col = "valid_time"
    v_times = pd.to_datetime(df[time_col], utc=True)
    start_date = v_times.min().strftime("%Y-%m-%d %H:%M:%S")
    end_date = v_times.max().strftime("%Y-%m-%d %H:%M:%S")
    date_span_days = round((v_times.max() - v_times.min()).total_seconds() / 86400.0, 2)

    districts = sorted(df["district"].unique().tolist())

    metrics = {
        "dataset": dataset_name,
        "total_rows": total_rows,
        "duplicate_rows": duplicate_rows,
        "missing_temp_count": missing_temp,
        "missing_temp_pct": round(missing_temp / total_rows * 100.0, 2),
        "missing_precip_count": missing_precip,
        "missing_precip_pct": round(missing_precip / total_rows * 100.0, 2),
        "temp_min_c": round(float(valid_t.min()), 2) if not valid_t.empty else np.nan,
        "temp_max_c": round(float(valid_t.max()), 2) if not valid_t.empty else np.nan,
        "temp_mean_c": round(float(valid_t.mean()), 2) if not valid_t.empty else np.nan,
        "precip_min_mm": round(float(valid_p.min()), 2) if not valid_p.empty else np.nan,
        "precip_max_mm": round(float(valid_p.max()), 2) if not valid_p.empty else np.nan,
        "precip_mean_mm": round(float(valid_p.mean()), 2) if not valid_p.empty else np.nan,
        "invalid_values_count": invalid_total,
        "start_date": start_date,
        "end_date": end_date,
        "date_span_days": date_span_days,
        "districts_covered": len(districts),
        "district_list": ", ".join(districts),
    }
    return metrics


def run_data_quality_checks(config_path: str = "config.yaml") -> Tuple[pd.DataFrame, str]:
    """
    Run data quality checks on GFS and ERA5 clean datasets.
    Generates CSV and text report outputs.
    """
    cfg = load_config(config_path)
    proc_dir = cfg["output_dirs"]["processed"]
    gfs_path = os.path.join(proc_dir, "gfs_clean.csv")
    era5_path = os.path.join(proc_dir, "era5_clean.csv")

    reports = []
    gfs_df = pd.read_csv(gfs_path) if os.path.exists(gfs_path) else pd.DataFrame()
    era5_df = pd.read_csv(era5_path) if os.path.exists(era5_path) else pd.DataFrame()

    reports.append(analyze_dataset_quality(gfs_df, "NOAA GFS Forecast", cfg))
    reports.append(analyze_dataset_quality(era5_df, "ECMWF ERA5 Reanalysis", cfg))

    report_df = pd.DataFrame(reports)

    # Save outputs/data_quality_report.csv
    out_csv = "outputs/data_quality_report.csv"
    os.makedirs(os.path.dirname(out_csv), exist_ok=True)
    report_df.to_csv(out_csv, index=False)

    # Generate human-readable text report
    txt_lines = [
        "=" * 70,
        "METEOROLOGICAL DATA QUALITY VERIFICATION REPORT",
        "Target Region: Jammu & Kashmir (Srinagar, Jammu, Anantnag, Baramulla)",
        f"Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S UTC')}",
        "=" * 70,
        "",
    ]

    for r in reports:
        txt_lines.extend([
            f"DATASET: {r['dataset']}",
            "-" * 45,
            f"  Total Observations:        {r['total_rows']:,}",
            f"  Duplicate Records:         {r['duplicate_rows']:,}",
            f"  Missing Temperature:       {r['missing_temp_count']:,} ({r['missing_temp_pct']}%)",
            f"  Missing Precipitation:     {r['missing_precip_count']:,} ({r['missing_precip_pct']}%)",
            f"  Temperature Range:         [{r['temp_min_c']} °C, {r['temp_max_c']} °C] (Mean: {r['temp_mean_c']} °C)",
            f"  Precipitation Range:       [{r['precip_min_mm']} mm, {r['precip_max_mm']} mm] (Mean: {r['precip_mean_mm']} mm)",
            f"  Invalid / Out-of-Bounds:   {r['invalid_values_count']:,}",
            f"  Temporal Span:             {r['start_date']} to {r['end_date']} ({r['date_span_days']} days)",
            f"  Districts Covered ({r['districts_covered']}):    {r['district_list']}",
            "",
        ])

    txt_lines.append("=" * 70)
    report_text = "\n".join(txt_lines)

    out_txt = "outputs/data_quality_report.txt"
    with open(out_txt, "w", encoding="utf-8") as f:
        f.write(report_text)

    logger.info("Saved data quality report -> %s and %s", out_csv, out_txt)
    return report_df, report_text


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run data quality checks")
    parser.add_argument("--config", default="config.yaml", help="Path to config.yaml")
    args = parser.parse_args()

    run_data_quality_checks(args.config)
