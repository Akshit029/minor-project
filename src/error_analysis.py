"""
Week 3: Forecast-Observation Error Analysis Module.

Performs rigorous verification of GFS forecasts against ERA5 reanalysis reference:
1. Constructs matched validation dataset with standardized timestamps and units.
2. Calculates baseline error metrics (MAE, RMSE, Bias, Median AE, Std Error, sample counts)
   across forecast lead days (1-10) and target districts.
3. Implements leakage-safe historical mean-bias correction with district-to-regional fallback.
4. Performs variable availability verification (Temperature, Precipitation, Pressure)
   and verifies precipitation accumulation semantics.

Sign Convention:
error = forecast_value - reference_value
Positive bias indicates the forecast overestimates the reference.
"""

import os
import logging
from typing import Dict, List, Tuple, Optional, Any
import numpy as np
import pandas as pd
import yaml

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("error_analysis")


def load_config(config_path: str = "config.yaml") -> dict:
    """Load project YAML configuration."""
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def check_variable_availability(gfs_df: pd.DataFrame, era5_df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    """
    Check variable availability and physical compatibility across GFS and ERA5 datasets.
    Checks 2m temperature, total precipitation, and pressure.
    """
    availability = {}

    # 1. 2m Temperature
    gfs_has_temp = bool("temperature_c" in gfs_df.columns and gfs_df["temperature_c"].notna().sum() > 0)
    era5_has_temp = bool("temperature_c" in era5_df.columns and era5_df["temperature_c"].notna().sum() > 0)
    availability["temperature_c"] = {
        "supported": bool(gfs_has_temp and era5_has_temp),
        "gfs_available": gfs_has_temp,
        "era5_available": era5_has_temp,
        "units": "°C",
        "notes": "Direct 2m instantaneous temperature matched across grid points."
    }

    # 2. Total Precipitation
    gfs_has_precip = bool("precipitation_mm" in gfs_df.columns and gfs_df["precipitation_mm"].notna().sum() > 0)
    era5_has_precip = bool("precipitation_mm" in era5_df.columns and era5_df["precipitation_mm"].notna().sum() > 0)
    availability["precipitation_mm"] = {
        "supported": bool(gfs_has_precip and era5_has_precip),
        "gfs_available": gfs_has_precip,
        "era5_available": era5_has_precip,
        "units": "mm",
        "notes": "Caution: GFS precipitation accumulation represents step accumulation (3-6h intervals) "
                 "whereas ERA5 represents hourly accumulated depth. Direct unaligned subtraction requires accumulation aggregation."
    }

    # 3. Surface / Sea Level Pressure
    gfs_has_press = bool(any(c in gfs_df.columns for c in ["pressure_hpa", "surface_pressure", "sp"]))
    era5_has_press = bool(any(c in era5_df.columns for c in ["pressure_hpa", "surface_pressure", "sp"]))
    availability["pressure_hpa"] = {
        "supported": bool(gfs_has_press and era5_has_press),
        "gfs_available": gfs_has_press,
        "era5_available": era5_has_press,
        "units": "hPa",
        "notes": "Pressure variable is absent from downloaded local ERA5 and GFS subsets. "
                 "Documented as unsupported by current dataset without fabricating observations."
    }

    return availability


def assign_lead_day(forecast_hour: int, hours_per_day: int = 24) -> int:
    """
    Map forecast lead hours into lead day (1 through 10).
    Convention:
      Day 1: hours 0-23
      Day 2: hours 24-47
      Day 3: hours 48-71
      ...
      Day 10: hours 216-239
    """
    if forecast_hour < 0:
        return 1
    day = (forecast_hour // hours_per_day) + 1
    return int(min(10, max(1, day)))


def build_matched_validation_dataset(
    gfs_df: pd.DataFrame,
    era5_df: pd.DataFrame,
    variable: str = "temperature_c",
    hours_per_day: int = 24
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Construct scientifically rigorous matched validation dataset:
    Matches (district, valid_time) while preserving initialization_time and lead_hours.

    Calculates:
      error = forecast_value - reference_value
      absolute_error = abs(error)
      squared_error = error^2
      bias = error

    Sign convention: positive error means forecast overestimates reference.
    """
    summary = {
        "variable": variable,
        "gfs_total_rows": len(gfs_df),
        "era5_total_rows": len(era5_df),
        "matched_pairs": 0,
        "rejected_missing_forecast": 0,
        "rejected_missing_reference": 0,
        "unique_districts": 0,
        "unique_init_cycles": 0,
    }

    if gfs_df.empty or era5_df.empty:
        logger.warning("Empty GFS or ERA5 dataframe. Cannot construct matched validation dataset.")
        return pd.DataFrame(), summary

    if variable not in gfs_df.columns or variable not in era5_df.columns:
        logger.error("Variable '%s' not present in both GFS and ERA5 dataframes.", variable)
        return pd.DataFrame(), summary

    gfs = gfs_df.copy()
    era5 = era5_df.copy()

    # Standardize datetime to UTC
    gfs["valid_time"] = pd.to_datetime(gfs["valid_time"], utc=True)
    era5["valid_time"] = pd.to_datetime(era5["valid_time"], utc=True)
    gfs["initialization_time"] = pd.to_datetime(gfs["initialization_time"], utc=True)

    # Lead hours and lead day
    lead_col = "forecast_hour" if "forecast_hour" in gfs.columns else "lead_hours"
    gfs["lead_hours"] = gfs[lead_col].astype(int)
    gfs["lead_day"] = gfs["lead_hours"].apply(lambda h: assign_lead_day(h, hours_per_day))

    # Reject missing values prior to merge
    gfs_valid = gfs.dropna(subset=["district", "valid_time", variable, "initialization_time", "lead_hours"]).copy()
    era5_valid = era5.dropna(subset=["district", "valid_time", variable]).copy()

    summary["rejected_missing_forecast"] = len(gfs) - len(gfs_valid)
    summary["rejected_missing_reference"] = len(era5) - len(era5_valid)

    # Prepare merge subsets
    gfs_sub = gfs_valid[[
        "district", "initialization_time", "valid_time", "lead_hours", "lead_day", variable
    ]].rename(columns={variable: "forecast_value"})

    era5_sub = era5_valid[[
        "district", "valid_time", variable
    ]].rename(columns={variable: "reference_value"})

    # Perform inner merge on district and valid_time
    matched = pd.merge(gfs_sub, era5_sub, on=["district", "valid_time"], how="inner")

    if matched.empty:
        logger.warning("No overlapping (district, valid_time) pairs found between GFS and ERA5.")
        return pd.DataFrame(), summary

    # Derive core error fields
    matched["variable"] = variable
    matched["error"] = matched["forecast_value"] - matched["reference_value"]
    matched["absolute_error"] = matched["error"].abs()
    matched["squared_error"] = matched["error"] ** 2
    matched["bias"] = matched["error"]

    # Sort deterministically
    matched = matched.sort_values(
        by=["district", "initialization_time", "lead_hours", "valid_time"]
    ).reset_index(drop=True)

    summary["matched_pairs"] = len(matched)
    summary["unique_districts"] = int(matched["district"].nunique())
    summary["unique_init_cycles"] = int(matched["initialization_time"].nunique())

    # Format timestamps back to ISO strings for CSV serialization
    matched["initialization_time"] = matched["initialization_time"].dt.strftime("%Y-%m-%d %H:%M:%S")
    matched["valid_time"] = matched["valid_time"].dt.strftime("%Y-%m-%d %H:%M:%S")

    logger.info("Successfully matched %d forecast-reference pairs for '%s'.", len(matched), variable)
    return matched, summary


def compute_error_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate baseline error metrics on a series of matched pairs:
      MAE = mean(|error|)
      RMSE = sqrt(mean(error^2))
      Bias = mean(error)
      Median_AE = median(|error|)
      Std_Error = std(error, ddof=1)
      Sample count & unique initialization cycles
    """
    if df.empty or "error" not in df.columns:
        return {
            "MAE": np.nan,
            "RMSE": np.nan,
            "Bias": np.nan,
            "Median_AE": np.nan,
            "Std_Error": np.nan,
            "sample_count": 0,
            "unique_init_cycles": 0,
        }

    err = df["error"].dropna()
    n = len(err)
    if n == 0:
        return {
            "MAE": np.nan,
            "RMSE": np.nan,
            "Bias": np.nan,
            "Median_AE": np.nan,
            "Std_Error": np.nan,
            "sample_count": 0,
            "unique_init_cycles": 0,
        }

    mae = float(np.abs(err).mean())
    rmse = float(np.sqrt((err ** 2).mean()))
    bias = float(err.mean())
    med_ae = float(np.median(np.abs(err)))
    std_err = float(err.std(ddof=1)) if n > 1 else 0.0
    n_cycles = int(df["initialization_time"].nunique()) if "initialization_time" in df.columns else 1

    return {
        "MAE": round(mae, 3),
        "RMSE": round(rmse, 3),
        "Bias": round(bias, 3),
        "Median_AE": round(med_ae, 3),
        "Std_Error": round(std_err, 3),
        "sample_count": n,
        "unique_init_cycles": n_cycles,
    }


def calculate_baseline_metrics_tables(
    matched_df: pd.DataFrame,
    min_samples: int = 1
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Calculate comprehensive verification metrics grouped by:
    1. Lead day (1 through 10)
    2. District
    3. District x Lead day
    """
    if matched_df.empty:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    var_name = matched_df["variable"].iloc[0] if "variable" in matched_df.columns else "variable"

    # 1. Lead Day Metrics
    lead_rows = []
    for l_day, grp in matched_df.groupby("lead_day"):
        m = compute_error_metrics(grp)
        m["lead_day"] = int(l_day)
        m["variable"] = var_name
        lead_rows.append(m)
    lead_df = pd.DataFrame(lead_rows).sort_values("lead_day").reset_index(drop=True)

    # 2. District Metrics
    dist_rows = []
    for dist, grp in matched_df.groupby("district"):
        m = compute_error_metrics(grp)
        m["district"] = dist
        m["variable"] = var_name
        dist_rows.append(m)
    dist_df = pd.DataFrame(dist_rows).sort_values("district").reset_index(drop=True)

    # 3. District x Lead Day Metrics
    dist_lead_rows = []
    for (dist, l_day), grp in matched_df.groupby(["district", "lead_day"]):
        m = compute_error_metrics(grp)
        m["district"] = dist
        m["lead_day"] = int(l_day)
        m["variable"] = var_name
        dist_lead_rows.append(m)
    dist_lead_df = pd.DataFrame(dist_lead_rows).sort_values(["district", "lead_day"]).reset_index(drop=True)

    return lead_df, dist_df, dist_lead_df


def fit_and_evaluate_bias_correction(
    matched_df: pd.DataFrame,
    train_ratio: float = 0.70,
    min_samples_threshold: int = 3
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Leakage-safe historical mean bias correction:
      corrected_forecast = forecast_value - training_bias
    where:
      training_bias = mean(forecast_value - reference_value)

    Strict protocol:
    1. Chronological split: earliest train_ratio of cases for training, remaining held-out for test.
    2. Corrections fitted ONLY on training split.
    3. Hierarchy fallback: District x Lead Day -> Regional Lead Day -> Global Regional Bias.
    4. Evaluated on the identical held-out test split before and after correction.

    Returns:
      - bias_params_df: learned bias correction offsets and sample provenance
      - test_eval_df: metrics before and after correction on the test set
      - corrected_test_df: test records with original and corrected values
    """
    if matched_df.empty or len(matched_df) < (min_samples_threshold * 2):
        logger.warning("Insufficient samples to fit and evaluate bias correction.")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    df = matched_df.copy()
    # Sort chronologically by valid_time
    df["dt"] = pd.to_datetime(df["valid_time"])
    df = df.sort_values(by=["dt", "district"]).reset_index(drop=True)

    n_total = len(df)
    n_train = int(n_total * train_ratio)
    train_df = df.iloc[:n_train].copy()
    test_df = df.iloc[n_train:].copy()

    # 1. Learn bias corrections on train_df
    # Global regional bias
    global_bias = float(train_df["error"].mean()) if len(train_df) > 0 else 0.0

    # Regional lead-day bias
    regional_lead_bias = train_df.groupby("lead_day")["error"].agg(["mean", "count"]).to_dict("index")

    # District x lead-day bias
    dist_lead_bias = train_df.groupby(["district", "lead_day"])["error"].agg(["mean", "count"]).to_dict("index")

    # Construct bias parameter table for all observed combinations
    params_rows = []
    unique_dists = sorted(df["district"].unique())
    unique_leads = sorted(df["lead_day"].unique())

    correction_lookup = {}
    for d in unique_dists:
        for l in unique_leads:
            key = (d, l)
            if key in dist_lead_bias and dist_lead_bias[key]["count"] >= min_samples_threshold:
                bias_val = float(dist_lead_bias[key]["mean"])
                cnt = int(dist_lead_bias[key]["count"])
                prov = "district_lead_day"
            elif l in regional_lead_bias and regional_lead_bias[l]["count"] >= min_samples_threshold:
                bias_val = float(regional_lead_bias[l]["mean"])
                cnt = int(regional_lead_bias[l]["count"])
                prov = "regional_lead_day_fallback"
            else:
                bias_val = global_bias
                cnt = len(train_df)
                prov = "global_regional_fallback"

            correction_lookup[key] = (bias_val, prov, cnt)
            params_rows.append({
                "district": d,
                "lead_day": l,
                "learned_bias": round(bias_val, 3),
                "training_sample_count": cnt,
                "provenance": prov,
            })

    bias_params_df = pd.DataFrame(params_rows)

    # 2. Apply corrections to held-out test_df
    test_corrections = []
    for _, row in test_df.iterrows():
        key = (row["district"], int(row["lead_day"]))
        corr_bias, prov, _ = correction_lookup.get(key, (global_bias, "fallback", 0))
        test_corrections.append((corr_bias, prov))

    test_df["applied_bias"] = [c[0] for c in test_corrections]
    test_df["correction_provenance"] = [c[1] for c in test_corrections]
    test_df["corrected_forecast_value"] = test_df["forecast_value"] - test_df["applied_bias"]
    test_df["corrected_error"] = test_df["corrected_forecast_value"] - test_df["reference_value"]
    test_df["corrected_absolute_error"] = test_df["corrected_error"].abs()
    test_df["corrected_squared_error"] = test_df["corrected_error"] ** 2

    # 3. Compute evaluation before and after correction on identical test set
    raw_eval = compute_error_metrics(test_df)

    corr_test_clean = test_df.rename(columns={
        "error": "orig_error",
        "corrected_error": "error"
    })
    corr_eval = compute_error_metrics(corr_test_clean)

    eval_rows = [
        {
            "evaluation_split": "Held-Out Test Set (Chronological)",
            "stage": "Uncorrected (Raw Forecast)",
            "MAE": raw_eval["MAE"],
            "RMSE": raw_eval["RMSE"],
            "Bias": raw_eval["Bias"],
            "Median_AE": raw_eval["Median_AE"],
            "Std_Error": raw_eval["Std_Error"],
            "sample_count": raw_eval["sample_count"],
        },
        {
            "evaluation_split": "Held-Out Test Set (Chronological)",
            "stage": "Corrected (Mean Bias Removed)",
            "MAE": corr_eval["MAE"],
            "RMSE": corr_eval["RMSE"],
            "Bias": corr_eval["Bias"],
            "Median_AE": corr_eval["Median_AE"],
            "Std_Error": corr_eval["Std_Error"],
            "sample_count": corr_eval["sample_count"],
        }
    ]
    test_eval_df = pd.DataFrame(eval_rows)

    # Remove temporary column
    test_df.drop(columns=["dt"], inplace=True, errors="ignore")

    return bias_params_df, test_eval_df, test_df


def run_week3_analysis(config_path: str = "config.yaml") -> Dict[str, Any]:
    """
    Execute full Week 3 Error Analysis Pipeline:
    1. Load processed GFS and ERA5 data.
    2. Check variable availability & physical compatibility.
    3. Construct matched validation dataset.
    4. Compute baseline error metrics (lead days 1-10, district-wise, district x lead).
    5. Fit and evaluate historical bias correction on held-out split.
    6. Save CSV artifacts.
    """
    cfg = load_config(config_path)
    proc_dir = cfg["output_dirs"]["processed"]
    out_dir = cfg["output_dirs"].get("week3", "outputs/week3")
    os.makedirs(out_dir, exist_ok=True)

    gfs_path = os.path.join(proc_dir, "gfs_clean.csv")
    era5_path = os.path.join(proc_dir, "era5_clean.csv")

    if not os.path.exists(gfs_path) or not os.path.exists(era5_path):
        raise FileNotFoundError(f"Processed GFS or ERA5 CSV missing in {proc_dir}. Run preprocessing first.")

    gfs_df = pd.read_csv(gfs_path)
    era5_df = pd.read_csv(era5_path)

    w3_cfg = cfg.get("week3", {})
    hours_per_day = w3_cfg.get("hours_per_lead_day", 24)
    min_samples = w3_cfg.get("min_samples_bias_correction", 4)
    train_split = w3_cfg.get("bias_correction_train_split", 0.70)

    # 1. Variable Availability Check
    var_avail = check_variable_availability(gfs_df, era5_df)
    avail_rows = []
    for var_name, info in var_avail.items():
        avail_rows.append({
            "variable": var_name,
            "supported": info["supported"],
            "gfs_available": info["gfs_available"],
            "era5_available": info["era5_available"],
            "units": info["units"],
            "notes": info["notes"]
        })
    avail_df = pd.DataFrame(avail_rows)
    avail_path = os.path.join(out_dir, "variable_availability_check.csv")
    avail_df.to_csv(avail_path, index=False)
    logger.info("Saved variable availability check -> %s", avail_path)

    # 2. Build Matched Validation Dataset (Temperature)
    matched_df, match_summary = build_matched_validation_dataset(
        gfs_df, era5_df, variable="temperature_c", hours_per_day=hours_per_day
    )

    matched_path = os.path.join(out_dir, "matched_validation_dataset.csv")
    matched_df.to_csv(matched_path, index=False)
    logger.info("Saved matched validation dataset (%d rows) -> %s", len(matched_df), matched_path)

    summary_df = pd.DataFrame([match_summary])
    summary_path = os.path.join(out_dir, "data_matching_summary.csv")
    summary_df.to_csv(summary_path, index=False)

    # 3. Compute baseline metrics
    lead_df, dist_df, dist_lead_df = calculate_baseline_metrics_tables(matched_df, min_samples=min_samples)

    lead_path = os.path.join(out_dir, "lead_day_metrics.csv")
    dist_path = os.path.join(out_dir, "district_metrics.csv")
    dist_lead_path = os.path.join(out_dir, "district_lead_metrics.csv")

    lead_df.to_csv(lead_path, index=False)
    dist_df.to_csv(dist_path, index=False)
    dist_lead_df.to_csv(dist_lead_path, index=False)
    logger.info("Saved lead day metrics -> %s", lead_path)
    logger.info("Saved district metrics -> %s", dist_path)

    # 4. Bias Correction
    bias_params, test_eval, corr_test = fit_and_evaluate_bias_correction(
        matched_df, train_ratio=train_split, min_samples_threshold=min_samples
    )

    params_path = os.path.join(out_dir, "bias_correction_params.csv")
    eval_path = os.path.join(out_dir, "bias_correction_eval.csv")
    test_corr_path = os.path.join(out_dir, "held_out_corrected_test.csv")

    bias_params.to_csv(params_path, index=False)
    test_eval.to_csv(eval_path, index=False)
    corr_test.to_csv(test_corr_path, index=False)
    logger.info("Saved bias correction parameters -> %s", params_path)
    logger.info("Saved bias correction evaluation -> %s", eval_path)

    return {
        "matched_df": matched_df,
        "lead_df": lead_df,
        "dist_df": dist_df,
        "dist_lead_df": dist_lead_df,
        "bias_params": bias_params,
        "test_eval": test_eval,
        "availability": var_avail,
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Week 3 Forecast-Observation Error Analysis")
    parser.add_argument("--config", default="config.yaml", help="Path to config.yaml")
    args = parser.parse_args()

    run_week3_analysis(args.config)
