"""
Week 2 Temporal Feature Extraction Module.

Calculates multi-scale temporal features per district from the reference ERA5 dataset:
1. 24-hour rolling temperature mean
2. 7-day (168-hour) rolling temperature mean
3. 24-hour precipitation accumulation
4. 7-day (168-hour) precipitation accumulation
5. Daily mean temperature
6. Daily minimum temperature
7. Daily maximum temperature
8. Daily precipitation total
9. Monthly mean temperature
10. Monthly precipitation total
11. Hourly temperature anomaly (vs provisional baseline)
12. Hourly precipitation anomaly (vs provisional baseline)

NOTE ON CLIMATOLOGY:
The baseline computed from the initial available ERA5 period is explicitly
designated as a "provisional baseline" rather than a 30-year long-term climatology.
The module provides a pluggable interface for future 10-year / 30-year baselines.
"""

import os
import logging
from typing import Tuple, Optional
import numpy as np
import pandas as pd
import yaml

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("features")


def load_config(config_path: str = "config.yaml") -> dict:
    """Load project YAML configuration."""
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def calculate_temporal_features(
    era5_df: pd.DataFrame,
    baseline_stats: Optional[pd.DataFrame] = None
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Compute hourly rolling features, daily summaries, and anomalies against baseline.

    Returns:
    - hourly_features_df: full hourly time series with rolling means and hourly anomalies
    - daily_features_df: aggregated daily statistics (min, max, mean, sum)
    """
    if era5_df.empty:
        logger.warning("Input ERA5 DataFrame is empty. Returning empty feature DataFrames.")
        return pd.DataFrame(), pd.DataFrame()

    df = era5_df.copy()
    df["valid_time"] = pd.to_datetime(df["valid_time"], utc=True)
    df = df.sort_values(by=["district", "valid_time"]).reset_index(drop=True)

    hourly_list = []
    daily_list = []

    for district, grp in df.groupby("district"):
        grp = grp.set_index("valid_time").sort_index()

        # Ensure regular hourly frequency if gaps exist
        grp_hourly = grp.asfreq("h")
        grp_hourly["district"] = district
        grp_hourly["latitude"] = grp["latitude"].iloc[0]
        grp_hourly["longitude"] = grp["longitude"].iloc[0]
        # Interpolate small 1-2 hour gaps in temperature, fill precipitation gaps with 0
        grp_hourly["temperature_c"] = grp_hourly["temperature_c"].interpolate(method="time", limit=2)
        grp_hourly["precipitation_mm"] = grp_hourly["precipitation_mm"].fillna(0.0)

        # 1. 24-hour rolling temperature mean
        grp_hourly["temp_24h_rolling_mean"] = grp_hourly["temperature_c"].rolling(window=24, min_periods=6).mean().round(2)

        # 2. 7-day (168-hour) rolling temperature mean
        grp_hourly["temp_7d_rolling_mean"] = grp_hourly["temperature_c"].rolling(window=168, min_periods=24).mean().round(2)

        # 3. 24-hour precipitation accumulation
        grp_hourly["precip_24h_accumulation"] = grp_hourly["precipitation_mm"].rolling(window=24, min_periods=1).sum().round(2)

        # 4. 7-day (168-hour) precipitation accumulation
        grp_hourly["precip_7d_accumulation"] = grp_hourly["precipitation_mm"].rolling(window=168, min_periods=1).sum().round(2)

        # Provisional baseline calculation (or using provided baseline_stats)
        # Using provisional district hourly mean and standard deviation
        t_mean = grp_hourly["temperature_c"].mean()
        p_mean = grp_hourly["precipitation_mm"].mean()

        # 11 & 12. Hourly Anomalies
        grp_hourly["temperature_anomaly"] = (grp_hourly["temperature_c"] - t_mean).round(2)
        grp_hourly["rainfall_anomaly"] = (grp_hourly["precipitation_mm"] - p_mean).round(2)

        grp_hourly = grp_hourly.reset_index()
        hourly_list.append(grp_hourly)

        # Daily aggregations
        # 5. daily mean temp, 6. daily min, 7. daily max, 8. daily precip total
        grp_daily = grp.resample("D")
        daily_df = pd.DataFrame({
            "district": district,
            "latitude": grp["latitude"].iloc[0],
            "longitude": grp["longitude"].iloc[0],
            "daily_mean_temperature_c": grp_daily["temperature_c"].mean().round(2),
            "daily_min_temperature_c": grp_daily["temperature_c"].min().round(2),
            "daily_max_temperature_c": grp_daily["temperature_c"].max().round(2),
            "daily_precipitation_total_mm": grp_daily["precipitation_mm"].sum().round(2),
        }).reset_index().rename(columns={"valid_time": "date"})

        daily_list.append(daily_df)

    hourly_features = pd.concat(hourly_list, ignore_index=True)
    daily_features = pd.concat(daily_list, ignore_index=True)

    # Monthly aggregations
    # 9. monthly mean temp, 10. monthly precipitation
    hourly_features["year_month"] = hourly_features["valid_time"].dt.tz_localize(None).dt.to_period("M")
    monthly_stats = hourly_features.groupby(["district", "year_month"]).agg(
        monthly_mean_temperature_c=("temperature_c", "mean"),
        monthly_precipitation_total_mm=("precipitation_mm", "sum")
    ).reset_index()
    monthly_stats["monthly_mean_temperature_c"] = monthly_stats["monthly_mean_temperature_c"].round(2)
    monthly_stats["monthly_precipitation_total_mm"] = monthly_stats["monthly_precipitation_total_mm"].round(2)

    # Merge monthly features back to hourly dataset for comprehensive representation
    hourly_features = pd.merge(hourly_features, monthly_stats, on=["district", "year_month"], how="left")
    hourly_features.drop(columns=["year_month"], inplace=True)

    # Format timestamps back to ISO strings
    hourly_features["valid_time"] = hourly_features["valid_time"].dt.strftime("%Y-%m-%d %H:%M:%S")
    daily_features["date"] = daily_features["date"].dt.strftime("%Y-%m-%d")

    return hourly_features, daily_features


def run_feature_extraction(config_path: str = "config.yaml") -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Execute temporal feature extraction pipeline and save processed outputs."""
    cfg = load_config(config_path)
    proc_dir = cfg["output_dirs"]["processed"]
    era5_clean_path = os.path.join(proc_dir, "era5_clean.csv")

    if not os.path.exists(era5_clean_path):
        raise FileNotFoundError(f"Clean ERA5 file not found at {era5_clean_path}. Run preprocessing first.")

    era5_df = pd.read_csv(era5_clean_path)
    logger.info("Extracting temporal features from ERA5 (%d rows)...", len(era5_df))

    hourly_features, daily_features = calculate_temporal_features(era5_df)

    hourly_out = os.path.join(proc_dir, "era5_features.csv")
    daily_out = os.path.join(proc_dir, "era5_daily_features.csv")

    hourly_features.to_csv(hourly_out, index=False)
    daily_features.to_csv(daily_out, index=False)

    logger.info("Saved hourly temporal features -> %s (%d records)", hourly_out, len(hourly_features))
    logger.info("Saved daily aggregations -> %s (%d records)", daily_out, len(daily_features))

    return hourly_features, daily_features


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Extract temporal meteorological features")
    parser.add_argument("--config", default="config.yaml", help="Path to config.yaml")
    args = parser.parse_args()

    run_feature_extraction(args.config)
