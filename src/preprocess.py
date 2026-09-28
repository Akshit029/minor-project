"""
Meteorological Data Preprocessing & Spatial/Temporal Standardization Module.

Extracts nearest grid-point time series for specified target districts across
Jammu & Kashmir from NOAA GFS GRIB2 forecast files and ECMWF ERA5 NetCDF files.
Standardizes units (Kelvin -> Celsius, m -> mm), normalizes UTC timestamps,
performs physical range screening, removes duplicates, and exports clean datasets.
"""

import os
import glob
import re
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import numpy as np
import pandas as pd
import xarray as xr
import yaml

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("preprocess")


def load_config(config_path: str = "config.yaml") -> dict:
    """Load project YAML configuration."""
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def find_nearest_indices(
    lats: np.ndarray,
    lons: np.ndarray,
    target_lat: float,
    target_lon: float
) -> Tuple[int, int, float, float]:
    """
    Find index of the nearest grid point in 1D or 2D coordinate arrays.
    Returns (lat_idx, lon_idx, actual_lat, actual_lon).
    """
    if lats.ndim == 1 and lons.ndim == 1:
        lat_idx = int(np.abs(lats - target_lat).argmin())
        lon_idx = int(np.abs(lons - target_lon).argmin())
        actual_lat = float(lats[lat_idx])
        actual_lon = float(lons[lon_idx])
        return lat_idx, lon_idx, actual_lat, actual_lon
    elif lats.ndim == 2 and lons.ndim == 2:
        dist_sq = (lats - target_lat) ** 2 + (lons - target_lon) ** 2
        flat_idx = int(dist_sq.argmin())
        lat_idx, lon_idx = np.unravel_index(flat_idx, lats.shape)
        actual_lat = float(lats[lat_idx, lon_idx])
        actual_lon = float(lons[lat_idx, lon_idx])
        return lat_idx, lon_idx, actual_lat, actual_lon
    else:
        raise ValueError(f"Unsupported coordinate dimensions: lats={lats.ndim}D, lons={lons.ndim}D")


def parse_gfs_grib_file(
    file_path: str,
    districts: Dict[str, Dict[str, float]]
) -> List[dict]:
    """
    Extract temperature and precipitation values for each district from a single GFS GRIB2 file.
    Uses xarray with cfgrib engine.
    """
    import cfgrib

    base = os.path.basename(file_path)
    pattern = r"gfs_(\d{8})_(\d{2})_f(\d{3})\.grib2"
    match = re.match(pattern, base)
    if not match:
        logger.warning("Filename %s does not match expected pattern gfs_YYYYMMDD_HH_fFFF.grib2", base)
        return []

    date_str, cycle_str, lead_str = match.groups()
    init_time = datetime.strptime(f"{date_str} {cycle_str}", "%Y%m%d %H")
    forecast_hour = int(lead_str)
    valid_time = init_time + timedelta(hours=forecast_hour)

    try:
        datasets = [xr.open_dataset(file_path, engine="cfgrib")]
    except Exception:
        try:
            datasets = cfgrib.open_datasets(file_path)
        except Exception as e:
            logger.error("Failed to parse GFS GRIB2 %s: %s", file_path, e)
            return []

    results = {}
    for ds in datasets:
        # Check temperature
        t_var = "t2m" if "t2m" in ds.data_vars else ("2t" if "2t" in ds.data_vars else None)
        p_var = "tp" if "tp" in ds.data_vars else ("apcp" if "apcp" in ds.data_vars else None)

        for d_name, d_coords in districts.items():
            if d_name not in results:
                results[d_name] = {"temp_c": None, "precip_mm": None, "lat": None, "lon": None}

            pt = ds.sel(latitude=d_coords["lat"], longitude=d_coords["lon"], method="nearest")
            if results[d_name]["lat"] is None:
                results[d_name]["lat"] = float(pt.latitude)
                results[d_name]["lon"] = float(pt.longitude)

            if t_var and results[d_name]["temp_c"] is None:
                results[d_name]["temp_c"] = round(float(pt[t_var].values) - 273.15, 2)
            if p_var and results[d_name]["precip_mm"] is None:
                p_val = float(pt[p_var].values)
                results[d_name]["precip_mm"] = round(p_val if p_val < 1000.0 else p_val * 1000.0, 2)
        ds.close()

    records = []
    for d_name, d_data in results.items():
        records.append({
            "district": d_name,
            "latitude": d_data["lat"],
            "longitude": d_data["lon"],
            "initialization_time": init_time.strftime("%Y-%m-%d %H:%M:%S"),
            "forecast_hour": forecast_hour,
            "valid_time": valid_time.strftime("%Y-%m-%d %H:%M:%S"),
            "temperature_c": d_data["temp_c"],
            "precipitation_mm": d_data["precip_mm"] if d_data["precip_mm"] is not None else 0.0,
        })
    return records


def preprocess_gfs(config: dict) -> pd.DataFrame:
    """
    Process all raw GFS GRIB2 files into standardized cleaned DataFrame.
    """
    raw_dir = config["output_dirs"]["raw_gfs"]
    districts = config["districts"]
    grib_files = sorted(glob.glob(os.path.join(raw_dir, "gfs_*.grib2")))

    if not grib_files:
        logger.warning("No raw GFS files found in %s.", raw_dir)
        return pd.DataFrame(columns=[
            "district", "latitude", "longitude", "initialization_time",
            "forecast_hour", "valid_time", "temperature_c", "precipitation_mm"
        ])

    logger.info("Preprocessing %d GFS GRIB2 files...", len(grib_files))
    all_records = []
    for fpath in grib_files:
        try:
            recs = parse_gfs_grib_file(fpath, districts)
            all_records.extend(recs)
        except Exception as e:
            logger.error("Error processing GFS file %s: %s", fpath, e)

    df = pd.DataFrame(all_records)
    if df.empty:
        return df

    # Data cleaning & validation
    # 1. Standardize timestamps
    df["initialization_time"] = pd.to_datetime(df["initialization_time"], utc=True)
    df["valid_time"] = pd.to_datetime(df["valid_time"], utc=True)

    # 2. Remove duplicate records
    dup_subset = ["district", "initialization_time", "forecast_hour"]
    n_dups = df.duplicated(subset=dup_subset).sum()
    if n_dups > 0:
        logger.info("Dropping %d duplicate GFS forecast rows.", n_dups)
        df = df.drop_duplicates(subset=dup_subset, keep="first")

    # 3. Physical range filtering
    q_cfg = config.get("quality", {})
    t_min = q_cfg.get("temp_min_c", -40.0)
    t_max = q_cfg.get("temp_max_c", 55.0)
    p_min = q_cfg.get("precip_min_mm", 0.0)
    p_max = q_cfg.get("precip_max_mm", 500.0)

    invalid_temp = (df["temperature_c"] < t_min) | (df["temperature_c"] > t_max)
    if invalid_temp.sum() > 0:
        logger.warning("Found %d GFS temperature records out of physical bounds [%.1f, %.1f]. Setting to NaN.",
                       invalid_temp.sum(), t_min, t_max)
        df.loc[invalid_temp, "temperature_c"] = np.nan

    invalid_precip = (df["precipitation_mm"] < p_min) | (df["precipitation_mm"] > p_max)
    if invalid_precip.sum() > 0:
        logger.warning("Found %d GFS precipitation records out of physical bounds [%.1f, %.1f]. Setting to NaN.",
                       invalid_precip.sum(), p_min, p_max)
        df.loc[invalid_precip, "precipitation_mm"] = np.nan

    # 4. Sort chronologically
    df = df.sort_values(by=["district", "initialization_time", "forecast_hour"]).reset_index(drop=True)

    # Format timestamps back to ISO string for CSV
    df["initialization_time"] = df["initialization_time"].dt.strftime("%Y-%m-%d %H:%M:%S")
    df["valid_time"] = df["valid_time"].dt.strftime("%Y-%m-%d %H:%M:%S")

    out_csv = os.path.join(config["output_dirs"]["processed"], "gfs_clean.csv")
    os.makedirs(os.path.dirname(out_csv), exist_ok=True)
    df.to_csv(out_csv, index=False)
    logger.info("Saved cleaned GFS dataset (%d records) -> %s", len(df), out_csv)
    return df


def preprocess_era5(config: dict) -> pd.DataFrame:
    """
    Process raw ERA5 NetCDF file into standardized cleaned DataFrame.
    """
    raw_dir = config["output_dirs"]["raw_era5"]
    districts = config["districts"]
    nc_files = sorted(glob.glob(os.path.join(raw_dir, "era5_*.nc")))

    if not nc_files:
        logger.warning("No raw ERA5 NetCDF files found in %s.", raw_dir)
        return pd.DataFrame(columns=[
            "district", "latitude", "longitude", "valid_time", "temperature_c", "precipitation_mm"
        ])

    logger.info("Preprocessing %d ERA5 NetCDF files...", len(nc_files))
    all_district_dfs = []

    for nc_path in nc_files:
        try:
            ds = xr.open_dataset(nc_path, engine="netcdf4")
        except Exception as e:
            logger.error("Failed to open ERA5 NetCDF file %s: %s", nc_path, e)
            continue

        # Coordinate dimension identification
        lat_coord = "latitude" if "latitude" in ds.coords else "lat"
        lon_coord = "longitude" if "longitude" in ds.coords else "lon"
        time_coord = "valid_time" if "valid_time" in ds.coords else ("time" if "time" in ds.coords else None)

        if time_coord is None:
            logger.error("Could not find time coordinate in %s. Available coords: %s", nc_path, list(ds.coords.keys()))
            continue

        # Variable identification
        # 2m temperature is t2m or 2t
        temp_var = "t2m" if "t2m" in ds.data_vars else ("2t" if "2t" in ds.data_vars else None)
        # precipitation is tp or total_precipitation
        precip_var = "tp" if "tp" in ds.data_vars else ("total_precipitation" if "total_precipitation" in ds.data_vars else None)

        lats = ds[lat_coord].values
        lons = ds[lon_coord].values

        for d_name, d_coords in districts.items():
            lat_idx, lon_idx, act_lat, act_lon = find_nearest_indices(
                lats, lons, d_coords["lat"], d_coords["lon"]
            )

            # Extract 1D time series for this district
            sel_dict = {lat_coord: lats[lat_idx], lon_coord: lons[lon_idx]}
            sub_ds = ds.sel(sel_dict, method="nearest")

            times = pd.to_datetime(sub_ds[time_coord].values, utc=True)
            
            # Unit conversions:
            # Temperature: Kelvin -> Celsius
            if temp_var in sub_ds:
                temp_c = (sub_ds[temp_var].values - 273.15).round(2)
            else:
                temp_c = np.full(len(times), np.nan)

            # Precipitation: m -> mm
            if precip_var in sub_ds:
                p_vals = sub_ds[precip_var].values * 1000.0
                precip_mm = np.clip(p_vals, 0.0, None).round(2)
            else:
                precip_mm = np.zeros(len(times))

            d_df = pd.DataFrame({
                "district": d_name,
                "latitude": round(act_lat, 4),
                "longitude": round(act_lon, 4),
                "valid_time": times.strftime("%Y-%m-%d %H:%M:%S"),
                "temperature_c": temp_c,
                "precipitation_mm": precip_mm,
            })
            all_district_dfs.append(d_df)

        ds.close()

    if not all_district_dfs:
        return pd.DataFrame()

    df = pd.concat(all_district_dfs, ignore_index=True)

    # Clean duplicates and sort
    df["valid_time"] = pd.to_datetime(df["valid_time"], utc=True)
    dup_subset = ["district", "valid_time"]
    n_dups = df.duplicated(subset=dup_subset).sum()
    if n_dups > 0:
        logger.info("Dropping %d duplicate ERA5 records.", n_dups)
        df = df.drop_duplicates(subset=dup_subset, keep="first")

    # Physical bounds filtering
    q_cfg = config.get("quality", {})
    t_min = q_cfg.get("temp_min_c", -40.0)
    t_max = q_cfg.get("temp_max_c", 55.0)
    p_min = q_cfg.get("precip_min_mm", 0.0)
    p_max = q_cfg.get("precip_max_mm", 500.0)

    df.loc[(df["temperature_c"] < t_min) | (df["temperature_c"] > t_max), "temperature_c"] = np.nan
    df.loc[(df["precipitation_mm"] < p_min) | (df["precipitation_mm"] > p_max), "precipitation_mm"] = np.nan

    df = df.sort_values(by=["district", "valid_time"]).reset_index(drop=True)
    df["valid_time"] = df["valid_time"].dt.strftime("%Y-%m-%d %H:%M:%S")

    out_csv = os.path.join(config["output_dirs"]["processed"], "era5_clean.csv")
    os.makedirs(os.path.dirname(out_csv), exist_ok=True)
    df.to_csv(out_csv, index=False)
    logger.info("Saved cleaned ERA5 dataset (%d records) -> %s", len(df), out_csv)
    return df


def run_preprocessing(config_path: str = "config.yaml"):
    """Execute complete preprocessing pipeline."""
    cfg = load_config(config_path)
    gfs_df = preprocess_gfs(cfg)
    era5_df = preprocess_era5(cfg)
    return gfs_df, era5_df


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Preprocess GFS and ERA5 data")
    parser.add_argument("--config", default="config.yaml", help="Path to config.yaml")
    args = parser.parse_args()

    run_preprocessing(args.config)
