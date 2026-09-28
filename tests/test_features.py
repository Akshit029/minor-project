"""
Unit tests for temporal feature extraction routines.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import pytest

from src.features import calculate_temporal_features


def create_sample_era5_data():
    dates = pd.date_range(start="2026-01-01 00:00:00", periods=72, freq="h", tz="UTC")
    df_list = []
    for district in ["Srinagar", "Jammu"]:
        base_temp = 10.0 if district == "Srinagar" else 20.0
        # Create sinusoidal diurnal temperature and small rainfall events
        temps = base_temp + 5.0 * np.sin(np.linspace(0, 6 * np.pi, len(dates)))
        precip = np.where(np.arange(len(dates)) % 12 == 0, 2.5, 0.0)

        df = pd.DataFrame({
            "district": district,
            "latitude": 34.0,
            "longitude": 74.5,
            "valid_time": dates.strftime("%Y-%m-%d %H:%M:%S"),
            "temperature_c": temps.round(2),
            "precipitation_mm": precip.round(2),
        })
        df_list.append(df)
    return pd.concat(df_list, ignore_index=True)


def test_calculate_temporal_features():
    df = create_sample_era5_data()
    hourly_feat, daily_feat = calculate_temporal_features(df)

    assert not hourly_feat.empty
    assert not daily_feat.empty

    # Check that required feature columns are present
    required_hourly = [
        "temp_24h_rolling_mean",
        "temp_7d_rolling_mean",
        "precip_24h_accumulation",
        "precip_7d_accumulation",
        "temperature_anomaly",
        "rainfall_anomaly",
        "monthly_mean_temperature_c",
        "monthly_precipitation_total_mm",
    ]
    for col in required_hourly:
        assert col in hourly_feat.columns, f"Missing {col} in hourly features"

    required_daily = [
        "daily_mean_temperature_c",
        "daily_min_temperature_c",
        "daily_max_temperature_c",
        "daily_precipitation_total_mm",
    ]
    for col in required_daily:
        assert col in daily_feat.columns, f"Missing {col} in daily features"

    # Verify 24h rolling mean is non-null for later steps
    srinagar_hourly = hourly_feat[hourly_feat["district"] == "Srinagar"]
    assert not srinagar_hourly["temp_24h_rolling_mean"].iloc[25:].isna().all()

    # Verify daily min <= daily mean <= daily max
    for _, row in daily_feat.iterrows():
        assert row["daily_min_temperature_c"] <= row["daily_mean_temperature_c"] <= row["daily_max_temperature_c"]
