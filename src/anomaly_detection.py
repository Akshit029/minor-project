"""
Statistical Anomaly Detection & Meteorological Event Screening Module.

Implements two complementary statistical anomaly detection methods:
1. Standard Z-Score (Mean / Standard Deviation baseline):
   Z = (x - mean) / std, flag |Z| >= z_threshold (default 3.0)
2. Robust Z-Score (Median / Median Absolute Deviation - MAD):
   Robust_Z = 0.6745 * (x - median) / MAD, flag |Robust_Z| >= robust_z_threshold (default 3.5)

Scientific Terminology Convention:
Statistical departures are formally classified as "statistical anomalies" and
screened as "potential extreme weather events". They are never prematurely labeled
as ground-truth physical disasters without multi-parameter confirmation.

Output:
- outputs/detected_anomalies.csv
"""

import os
import logging
from typing import Tuple, List, Dict
import numpy as np
import pandas as pd
import yaml

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("anomaly_detection")


def load_config(config_path: str = "config.yaml") -> dict:
    """Load project YAML configuration."""
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def calculate_mad(series: pd.Series) -> float:
    """
    Calculate Median Absolute Deviation (MAD).
    MAD = median(|x - median(x)|)
    """
    clean_series = series.dropna()
    if clean_series.empty:
        return 0.0
    med = clean_series.median()
    mad = float(np.median(np.abs(clean_series - med)))
    return mad


def compute_z_score(series: pd.Series) -> pd.Series:
    """Compute standard Z-score: (x - mean) / std."""
    mean = series.mean()
    std = series.std(ddof=1)
    if std == 0 or np.isnan(std):
        return pd.Series(0.0, index=series.index)
    return (series - mean) / std


def compute_robust_z_score(series: pd.Series) -> pd.Series:
    """
    Compute Robust Z-score: 0.6745 * (x - median) / MAD.
    Includes numerical stability fallback for zero MAD (common in dry precipitation series).
    """
    median = series.median()
    mad = calculate_mad(series)
    if mad > 1e-6:
        return 0.6745 * (series - median) / mad
    else:
        # Fallback to mean absolute deviation or std to avoid divide-by-zero
        mean_dev = np.mean(np.abs(series - median))
        if mean_dev > 1e-6:
            return 0.6745 * (series - median) / mean_dev
        std = series.std(ddof=1)
        if std > 1e-6:
            return (series - median) / std
        return pd.Series(0.0, index=series.index)


def detect_anomalies(
    df: pd.DataFrame,
    z_threshold: float = 3.0,
    robust_z_threshold: float = 3.5
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Screen time series for statistical temperature and precipitation anomalies per district.
    Returns:
    - enriched_df: full time series with Z and Robust Z columns
    - anomalies_df: flagged anomalies filtered with severity classification
    """
    if df.empty:
        logger.warning("Empty dataframe provided to detect_anomalies.")
        return pd.DataFrame(), pd.DataFrame()

    df = df.copy()
    district_frames = []

    for district, grp in df.groupby("district"):
        grp = grp.copy()

        # Compute Z-scores
        grp["temp_z_score"] = compute_z_score(grp["temperature_c"]).round(3)
        grp["precip_z_score"] = compute_z_score(grp["precipitation_mm"]).round(3)

        # Compute Robust Z-scores
        grp["temperature_robust_z"] = compute_robust_z_score(grp["temperature_c"]).round(3)
        grp["rainfall_robust_z"] = compute_robust_z_score(grp["precipitation_mm"]).round(3)

        district_frames.append(grp)

    enriched_df = pd.concat(district_frames, ignore_index=True)

    # Flag condition: |Z| >= z_threshold OR |Robust_Z| >= robust_z_threshold
    temp_high_flag = (enriched_df["temp_z_score"] >= z_threshold) | (enriched_df["temperature_robust_z"] >= robust_z_threshold)
    temp_low_flag = (enriched_df["temp_z_score"] <= -z_threshold) | (enriched_df["temperature_robust_z"] <= -robust_z_threshold)
    precip_high_flag = (enriched_df["precip_z_score"] >= z_threshold) | (enriched_df["rainfall_robust_z"] >= robust_z_threshold)

    # Assign anomaly categories
    anomaly_records = []
    for idx, row in enriched_df.iterrows():
        types = []
        max_severity = 0.0

        if temp_high_flag.loc[idx]:
            types.append("High-temperature anomaly")
            max_severity = max(max_severity, abs(row["temperature_robust_z"]))
        if temp_low_flag.loc[idx]:
            types.append("Low-temperature anomaly")
            max_severity = max(max_severity, abs(row["temperature_robust_z"]))
        if precip_high_flag.loc[idx]:
            types.append("High-rainfall anomaly")
            max_severity = max(max_severity, abs(row["rainfall_robust_z"]))

        if types:
            # Determine qualitative severity
            if max_severity >= 5.0:
                severity_label = "Severe potential extreme weather event"
            elif max_severity >= 4.0:
                severity_label = "Moderate potential extreme weather event"
            else:
                severity_label = "Mild statistical anomaly"

            anomaly_records.append({
                "district": row["district"],
                "valid_time": row["valid_time"],
                "temperature_c": row["temperature_c"],
                "precipitation_mm": row["precipitation_mm"],
                "temperature_anomaly": row.get("temperature_anomaly", np.nan),
                "rainfall_anomaly": row.get("rainfall_anomaly", np.nan),
                "temperature_robust_z": row["temperature_robust_z"],
                "rainfall_robust_z": row["rainfall_robust_z"],
                "anomaly_type": "; ".join(types),
                "severity": severity_label,
            })

    anomalies_df = pd.DataFrame(anomaly_records)
    return enriched_df, anomalies_df


def run_anomaly_detection(config_path: str = "config.yaml") -> pd.DataFrame:
    """Execute complete anomaly detection pipeline."""
    cfg = load_config(config_path)
    proc_dir = cfg["output_dirs"]["processed"]
    features_path = os.path.join(proc_dir, "era5_features.csv")

    if not os.path.exists(features_path):
        features_path = os.path.join(proc_dir, "era5_clean.csv")
        if not os.path.exists(features_path):
            raise FileNotFoundError("Neither era5_features.csv nor era5_clean.csv found. Run prior steps first.")

    df = pd.read_csv(features_path)
    a_cfg = cfg.get("anomaly", {})
    z_thresh = float(a_cfg.get("z_threshold", 3.0))
    rob_thresh = float(a_cfg.get("robust_z_threshold", 3.5))

    logger.info("Running anomaly detection on %d records (Z-thresh=%.1f, Robust-Z-thresh=%.1f)...",
                len(df), z_thresh, rob_thresh)

    enriched_df, anomalies_df = detect_anomalies(df, z_threshold=z_thresh, robust_z_threshold=rob_thresh)

    out_csv = "outputs/detected_anomalies.csv"
    os.makedirs(os.path.dirname(out_csv), exist_ok=True)
    anomalies_df.to_csv(out_csv, index=False)
    logger.info("Identified %d potential anomalous records -> %s", len(anomalies_df), out_csv)

    return anomalies_df


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run statistical anomaly detection")
    parser.add_argument("--config", default="config.yaml", help="Path to config.yaml")
    args = parser.parse_args()

    run_anomaly_detection(args.config)
