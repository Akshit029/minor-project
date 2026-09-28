"""
NOAA Global Forecast System (GFS) 0.25-degree Data Acquisition Module.

Downloads operational GFS forecast GRIB2 data for specified dates, cycles,
and forecast lead times. Supports fast index-based byte-range downloading
from NOAA Open Data on AWS S3, with fallback to NOAA NOMADS.
"""

import os
import re
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
import requests
import yaml
from tqdm import tqdm

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("download_gfs")

# Primary and fallback base URLs
AWS_GFS_BASE = "https://noaa-gfs-bdp-pds.s3.amazonaws.com"
NOMADS_GFS_BASE = "https://nomads.ncep.noaa.gov/pub/data/nccf/com/gfs/prod"


def load_config(config_path: str = "config.yaml") -> dict:
    """Load project YAML configuration."""
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def build_gfs_url(date_str: str, cycle: str, forecast_hour: int, base_url: str = AWS_GFS_BASE) -> str:
    """
    Construct GFS file URL.
    Format: https://.../gfs.YYYYMMDD/HH/atmos/gfs.tHHz.pgrb2.0p25.fFFF
    """
    date_formatted = date_str.replace("-", "")
    lead_str = f"{forecast_hour:03d}"
    return f"{base_url}/gfs.{date_formatted}/{cycle}/atmos/gfs.t{cycle}z.pgrb2.0p25.f{lead_str}"


def parse_idx_ranges(idx_text: str, target_vars: List[str]) -> List[Tuple[int, Optional[int]]]:
    """
    Parse .idx file to identify byte ranges for target variables (e.g. TMP:2 m above ground, APCP:surface).
    Format of idx: record:start_byte:date:var:level:forecast:
    """
    lines = idx_text.strip().split("\n")
    parsed_records = []
    
    for line in lines:
        parts = line.strip().split(":")
        if len(parts) >= 6:
            rec_id = int(parts[0])
            start_byte = int(parts[1])
            var = parts[3]
            level = parts[4]
            full_match = f"{var}:{level}"
            parsed_records.append((rec_id, start_byte, var, level, full_match))
            
    ranges = []
    for i, (rec_id, start_byte, var, level, full_match) in enumerate(parsed_records):
        match = any(target in full_match for target in target_vars)
        if match:
            # End byte is the start of the next record minus 1
            if i + 1 < len(parsed_records):
                end_byte = parsed_records[i + 1][1] - 1
            else:
                end_byte = None  # to EOF
            ranges.append((start_byte, end_byte))
            
    return ranges


def download_byte_range(url: str, start: int, end: Optional[int], retries: int = 3) -> bytes:
    """Download specific byte range from a URL with retries."""
    headers = {"Range": f"bytes={start}-{end if end is not None else ''}"}
    for attempt in range(retries):
        try:
            resp = requests.get(url, headers=headers, timeout=30)
            if resp.status_code in (200, 206):
                return resp.content
            logger.warning("Attempt %d: HTTP %d fetching byte range %d-%s", attempt + 1, resp.status_code, start, end)
        except requests.RequestException as e:
            logger.warning("Attempt %d error fetching %s: %s", attempt + 1, url, e)
        time.sleep(2 ** attempt)
    raise RuntimeError(f"Failed to download byte range {start}-{end} from {url} after {retries} retries.")


def download_gfs_lead(
    date_str: str,
    cycle: str,
    forecast_hour: int,
    output_dir: str,
    target_vars: Optional[List[str]] = None,
    force: bool = False
) -> Optional[str]:
    """
    Download GFS GRIB2 file for a single lead time.
    Uses index-based byte ranges to download only required variables if available,
    saving bandwidth and storage.
    """
    if target_vars is None:
        target_vars = ["TMP:2 m above ground", "APCP:surface"]

    os.makedirs(output_dir, exist_ok=True)
    date_formatted = date_str.replace("-", "")
    lead_str = f"{forecast_hour:03d}"
    out_filename = f"gfs_{date_formatted}_{cycle}_f{lead_str}.grib2"
    out_path = os.path.join(output_dir, out_filename)

    if not force and os.path.exists(out_path) and os.path.getsize(out_path) > 1024:
        logger.debug("File %s already exists (size %d bytes). Skipping.", out_filename, os.path.getsize(out_path))
        return out_path

    # Try AWS first, then NOMADS
    bases = [AWS_GFS_BASE, NOMADS_GFS_BASE]
    for base in bases:
        grib_url = build_gfs_url(date_str, cycle, forecast_hour, base)
        idx_url = f"{grib_url}.idx"

        try:
            # 1. Check if .idx is accessible
            idx_resp = requests.get(idx_url, timeout=15)
            if idx_resp.status_code == 200:
                ranges = parse_idx_ranges(idx_resp.text, target_vars)
                if ranges:
                    logger.debug("Downloading %d targeted byte ranges for %s f%s...", len(ranges), date_str, lead_str)
                    combined_data = bytearray()
                    for start, end in ranges:
                        chunk = download_byte_range(grib_url, start, end)
                        combined_data.extend(chunk)

                    with open(out_path, "wb") as f:
                        f.write(combined_data)
                    logger.info("Saved targeted GRIB2 (%d KB) -> %s", len(combined_data) // 1024, out_filename)
                    return out_path

            # 2. Fallback: Direct download if idx parsing was empty or unavailable
            logger.info("Index byte ranges unavailable. Attempting direct stream download from %s...", grib_url)
            resp = requests.get(grib_url, stream=True, timeout=30)
            if resp.status_code == 200:
                with open(out_path, "wb") as f:
                    for chunk in resp.iter_content(chunk_size=65536):
                        if chunk:
                            f.write(chunk)
                logger.info("Saved full GRIB2 (%d KB) -> %s", os.path.getsize(out_path) // 1024, out_filename)
                return out_path

        except Exception as e:
            logger.warning("Failed downloading from %s: %s", base, e)

    logger.error("Unable to download GFS for %s cycle %s f%03d from any source.", date_str, cycle, forecast_hour)
    return None


def download_gfs_range(config: dict, test_mode: bool = False) -> List[str]:
    """
    Download GFS forecast data over the configured date range, cycles, and lead times.
    """
    cfg = config["gfs"]
    out_dir = config["output_dirs"]["raw_gfs"]

    if test_mode:
        t_cfg = cfg.get("test_mode", {})
        start_date_str = t_cfg.get("start_date", cfg["start_date"])
        end_date_str = t_cfg.get("end_date", cfg["start_date"])
        cycles = t_cfg.get("cycles", ["00"])
        max_hour = t_cfg.get("max_forecast_hour", 12)
        interval = t_cfg.get("forecast_interval", 3)
    else:
        start_date_str = cfg["start_date"]
        end_date_str = cfg["end_date"]
        cycles = cfg.get("cycles", ["00", "06", "12", "18"])
        max_hour = cfg.get("max_forecast_hour", 168)
        interval = cfg.get("forecast_interval", 3)

    start_dt = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date_str, "%Y-%m-%d")
    lead_hours = list(range(0, max_hour + 1, interval))

    date_list = []
    curr = start_dt
    while curr <= end_dt:
        date_list.append(curr.strftime("%Y-%m-%d"))
        curr += timedelta(days=1)

    total_tasks = len(date_list) * len(cycles) * len(lead_hours)
    logger.info("Starting GFS download: %d dates, %s cycles, lead times up to %dh (%d total steps).",
                len(date_list), cycles, max_hour, total_tasks)

    downloaded_files = []
    pbar = tqdm(total=total_tasks, desc="GFS Downloads")

    for d_str in date_list:
        for cyc in cycles:
            for lh in lead_hours:
                pbar.set_postfix({"date": d_str, "cycle": cyc, "lead": f"{lh:03d}h"})
                res = download_gfs_lead(
                    date_str=d_str,
                    cycle=cyc,
                    forecast_hour=lh,
                    output_dir=out_dir
                )
                if res:
                    downloaded_files.append(res)
                pbar.update(1)

    pbar.close()
    logger.info("GFS download finished. Total files ready: %d / %d", len(downloaded_files), total_tasks)
    return downloaded_files


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Download NOAA GFS forecast data")
    parser.add_argument("--config", default="config.yaml", help="Path to config.yaml")
    parser.add_argument("--test", action="store_true", help="Run in small test mode")
    args = parser.parse_args()

    config_data = load_config(args.config)
    download_gfs_range(config_data, test_mode=args.test)
