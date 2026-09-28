"""
GFS Forecast Verification & Validation against ERA5 Reanalysis.

Matches GFS forecast predictions with ERA5 reference reanalysis using:
(district, valid_time)

CRITICAL VERIFICATION METHODOLOGY:
GFS valid_time = initialization_time + forecast_lead_time
We strictly compare GFS valid_time against ERA5 valid_time.

Calculates verification metrics:
- Mean Absolute Error (MAE): (1/N) * sum(|GFS - ERA5|)
- Root Mean Squared Error (RMSE): sqrt((1/N) * sum((GFS - ERA5)^2))
- Mean Error / Forecast Bias: (1/N) * sum(GFS - ERA5)
- Sample Counts

Outputs:
- outputs/validation_by_lead_time.csv
- outputs/validation_by_district.csv
- outputs/tables/validation_summary.csv
"""

import os
import logging
from typing import Tuple, Dict, Any
import numpy as np
import pandas as pd
import yaml

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("validate")


def load_config(config_path: str = "config.yaml") -> dict:
    """Load project YAML configuration."""
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def calculate_metrics(gfs_series: pd.Series, era5_series: pd.Series) -> Dict[str, float]:
    """
    Compute MAE, RMSE, and Bias between GFS and ERA5.
    error = GFS - ERA5
    """
    errors = gfs_series - era5_series
    valid_errors = errors.dropna()
    n = len(valid_errors)

    if n == 0:
        return {
            "MAE": np.nan,
            "RMSE": np.nan,
            "Bias": np.nan,
            "sample_count": 0
        }

    mae = float(np.abs(valid_errors).mean())
    rmse = float(np.sqrt((valid_errors ** 2).mean()))
    bias = float(valid_errors.mean())

    return {
        "MAE": round(mae, 3),
        "RMSE": round(rmse, 3),
        "Bias": round(bias, 3),
        "sample_count": n
    }


def validate_gfs_against_era5(
    gfs_df: pd.DataFrame,
    era5_df: pd.DataFrame
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Merge GFS and ERA5 on (district, valid_time) and compute validation metrics:
    1. By forecast lead time
    2. By district
    3. Overall summary
    """
    if gfs_df.empty or era5_df.empty:
        logger.warning("Either GFS or ERA5 dataset is empty. Cannot perform validation.")
        empty_lead = pd.DataFrame(columns=["forecast_hour", "MAE", "RMSE", "Bias", "sample_count"])
        empty_dist = pd.DataFrame(columns=["district", "MAE", "RMSE", "Bias", "sample_count"])
        empty_sum = pd.DataFrame()
        return empty_lead, empty_dist, empty_sum

    gfs = gfs_df.copy()
    era5 = era5_df.copy()

    # Ensure standardized datetime comparison
    gfs["valid_time"] = pd.to_datetime(gfs["valid_time"], utc=True)
    era5["valid_time"] = pd.to_datetime(era5["valid_time"], utc=True)

    # Clean subset for merging
    gfs_sub = gfs[["district", "initialization_time", "forecast_hour", "valid_time", "temperature_c"]].rename(
        columns={"temperature_c": "gfs_temperature_c"}
    )
    era5_sub = era5[["district", "valid_time", "temperature_c"]].rename(
        columns={"temperature_c": "era5_temperature_c"}
    )

    merged = pd.merge(gfs_sub, era5_sub, on=["district", "valid_time"], how="inner")
    logger.info("Matched %d forecast-verification observation pairs.", len(merged))

    if merged.empty:
        logger.warning("No overlapping (district, valid_time) pairs found between GFS and ERA5.")
        empty_lead = pd.DataFrame(columns=["forecast_hour", "MAE", "RMSE", "Bias", "sample_count"])
        empty_dist = pd.DataFrame(columns=["district", "MAE", "RMSE", "Bias", "sample_count"])
        return empty_lead, empty_dist, pd.DataFrame()

    merged["temperature_error"] = merged["gfs_temperature_c"] - merged["era5_temperature_c"]

    # 1. Validation by forecast lead time
    lead_records = []
    for f_hour, grp in merged.groupby("forecast_hour"):
        m = calculate_metrics(grp["gfs_temperature_c"], grp["era5_temperature_c"])
        m["forecast_hour"] = int(f_hour)
        lead_records.append(m)

    by_lead_time_df = pd.DataFrame(lead_records).sort_values("forecast_hour").reset_index(drop=True)
    # Reorder columns
    by_lead_time_df = by_lead_time_df[["forecast_hour", "MAE", "RMSE", "Bias", "sample_count"]]

    # 2. Validation by district
    dist_records = []
    for district, grp in merged.groupby("district"):
        m = calculate_metrics(grp["gfs_temperature_c"], grp["era5_temperature_c"])
        m["district"] = district
        dist_records.append(m)

    by_district_df = pd.DataFrame(dist_records).sort_values("district").reset_index(drop=True)
    by_district_df = by_district_df[["district", "MAE", "RMSE", "Bias", "sample_count"]]

    # 3. Overall summary
    overall = calculate_metrics(merged["gfs_temperature_c"], merged["era5_temperature_c"])
    overall_df = pd.DataFrame([{
        "dataset_pair": "NOAA GFS vs ECMWF ERA5",
        "total_pairs": len(merged),
        "overall_MAE_c": overall["MAE"],
        "overall_RMSE_c": overall["RMSE"],
        "overall_Bias_c": overall["Bias"],
    }])

    return by_lead_time_df, by_district_df, overall_df


def run_validation(config_path: str = "config.yaml"):
    """Execute complete validation suite and export result CSVs."""
    cfg = load_config(config_path)
    proc_dir = cfg["output_dirs"]["processed"]
    gfs_path = os.path.join(proc_dir, "gfs_clean.csv")
    era5_path = os.path.join(proc_dir, "era5_clean.csv")

    if not os.path.exists(gfs_path) or not os.path.exists(era5_path):
        raise FileNotFoundError("Clean GFS or ERA5 CSV missing. Complete preprocessing first.")

    gfs_df = pd.read_csv(gfs_path)
    era5_df = pd.read_csv(era5_path)

    by_lead, by_dist, overall = validate_gfs_against_era5(gfs_df, era5_df)

    out_lead = "outputs/validation_by_lead_time.csv"
    out_dist = "outputs/validation_by_district.csv"
    out_summary = "outputs/tables/validation_summary.csv"

    os.makedirs(os.path.dirname(out_lead), exist_ok=True)
    os.makedirs(os.path.dirname(out_summary), exist_ok=True)

    by_lead.to_csv(out_lead, index=False)
    by_dist.to_csv(out_dist, index=False)
    overall.to_csv(out_summary, index=False)

    logger.info("Saved validation by lead time -> %s", out_lead)
    logger.info("Saved validation by district -> %s", out_dist)
    logger.info("Saved overall validation summary -> %s", out_summary)

    return by_lead, by_dist, overall


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Validate GFS against ERA5")
    parser.add_argument("--config", default="config.yaml", help="Path to config.yaml")
    args = parser.parse_args()

    run_validation(args.config)
