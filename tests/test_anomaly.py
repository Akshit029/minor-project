"""
Unit tests for statistical anomaly detection methods (Z-Score & Robust MAD).
"""

import numpy as np
import pandas as pd
import pytest

from src.anomaly_detection import (
    calculate_mad,
    compute_z_score,
    compute_robust_z_score,
    detect_anomalies
)


def test_calculate_mad():
    data = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0])
    mad = calculate_mad(data)
    # Median is 5.0, absolute deviations: [4, 3, 2, 1, 0, 1, 2, 3, 4] -> median is 2.0
    assert np.isclose(mad, 2.0)


def test_compute_z_score():
    data = pd.Series([10.0, 10.0, 10.0, 10.0, 10.0, 100.0])
    z = compute_z_score(data)
    assert z.iloc[-1] > 2.0  # 100.0 is a strong positive departure


def test_compute_robust_z_score():
    # Synthetic series with a severe outlier
    data = pd.Series([20.0, 20.2, 19.8, 20.1, 19.9, 20.0, 45.0])
    rob_z = compute_robust_z_score(data)
    # The outlier 45.0 should have a very high robust Z-score
    assert abs(rob_z.iloc[-1]) > 10.0


def test_detect_anomalies_workflow():
    n = 100
    times = pd.date_range("2026-01-01", periods=n, freq="h")
    # Base temperature with normal noise
    np.random.seed(42)
    temps = np.random.normal(loc=15.0, scale=2.0, size=n)
    precip = np.zeros(n)

    # Inject extreme temperature and precipitation
    temps[10] = 35.0  # +10 sigma extreme heat
    temps[20] = -15.0 # -15 sigma extreme cold
    precip[30] = 80.0 # extreme flash rainfall

    df = pd.DataFrame({
        "district": "Srinagar",
        "latitude": 34.08,
        "longitude": 74.80,
        "valid_time": times.strftime("%Y-%m-%d %H:%M:%S"),
        "temperature_c": temps,
        "precipitation_mm": precip,
    })

    enriched, anomalies = detect_anomalies(df, z_threshold=3.0, robust_z_threshold=3.5)
    assert not anomalies.empty
    # Verify flagged types exist
    anomaly_types = " ".join(anomalies["anomaly_type"].tolist())
    assert "High-temperature anomaly" in anomaly_types
    assert "Low-temperature anomaly" in anomaly_types
    assert "High-rainfall anomaly" in anomaly_types
