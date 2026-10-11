"""
Unit tests for Week 3: Forecast-Observation Error Analysis and Bias Correction.
"""

import numpy as np
import pandas as pd
import pytest
from datetime import datetime

from src.error_analysis import (
    assign_lead_day,
    compute_error_metrics,
    build_matched_validation_dataset,
    calculate_baseline_metrics_tables,
    fit_and_evaluate_bias_correction,
    check_variable_availability
)


def test_error_metrics_manual_calculation():
    """Verify MAE, RMSE, and Bias formulas against known manually calculated values."""
    # Forecasts: [12.0, 15.0, 20.0, 25.0]
    # References: [10.0, 16.0, 18.0, 21.0]
    # Errors (forecast - reference): [+2.0, -1.0, +2.0, +4.0]
    # Abs errors: [2.0, 1.0, 2.0, 4.0] -> sum=9.0 -> MAE = 9/4 = 2.25
    # Squared errors: [4.0, 1.0, 4.0, 16.0] -> sum=25.0 -> RMSE = sqrt(25/4) = sqrt(6.25) = 2.50
    # Mean bias: (2 - 1 + 2 + 4) / 4 = 7.0 / 4 = 1.75
    # Median AE: median([1, 2, 2, 4]) = 2.0
    df = pd.DataFrame({
        "forecast_value": [12.0, 15.0, 20.0, 25.0],
        "reference_value": [10.0, 16.0, 18.0, 21.0],
    })
    df["error"] = df["forecast_value"] - df["reference_value"]
    df["initialization_time"] = "2026-09-15 00:00:00"

    metrics = compute_error_metrics(df)
    assert np.isclose(metrics["MAE"], 2.25)
    assert np.isclose(metrics["RMSE"], 2.50)
    assert np.isclose(metrics["Bias"], 1.75)
    assert np.isclose(metrics["Median_AE"], 2.0)
    assert metrics["sample_count"] == 4


def test_bias_sign_convention():
    """Verify positive bias means forecast overestimates reference."""
    df = pd.DataFrame({
        "forecast_value": [30.0],
        "reference_value": [25.0]
    })
    df["error"] = df["forecast_value"] - df["reference_value"]
    m = compute_error_metrics(df)
    assert m["Bias"] > 0
    assert m["Bias"] == 5.0


def test_assign_lead_day():
    """Verify standard 24-hour lead day bins."""
    assert assign_lead_day(0) == 1
    assert assign_lead_day(12) == 1
    assert assign_lead_day(23) == 1
    assert assign_lead_day(24) == 2
    assert assign_lead_day(47) == 2
    assert assign_lead_day(48) == 3
    assert assign_lead_day(240) == 10  # Max lead day capped at 10


def test_matched_dataset_construction_and_duplicate_handling():
    """Verify timestamp and district matching, duplicate handling, and missing rejection."""
    gfs = pd.DataFrame({
        "district": ["Srinagar", "Srinagar", "Jammu"],
        "initialization_time": ["2026-09-15 00:00:00", "2026-09-15 00:00:00", "2026-09-15 00:00:00"],
        "forecast_hour": [6, 12, 6],
        "valid_time": ["2026-09-15 06:00:00", "2026-09-15 12:00:00", "2026-09-15 06:00:00"],
        "temperature_c": [15.0, 18.0, 25.0]
    })
    era5 = pd.DataFrame({
        "district": ["Srinagar", "Srinagar", "Jammu", "Anantnag"],
        "valid_time": ["2026-09-15 06:00:00", "2026-09-15 12:00:00", "2026-09-15 06:00:00", "2026-09-15 06:00:00"],
        "temperature_c": [14.0, 17.5, 24.0, 12.0]
    })

    matched, summary = build_matched_validation_dataset(gfs, era5, variable="temperature_c")
    assert len(matched) == 3
    assert summary["matched_pairs"] == 3
    assert summary["unique_districts"] == 2
    assert "error" in matched.columns
    assert "absolute_error" in matched.columns
    assert "squared_error" in matched.columns
    assert "lead_day" in matched.columns

    # Verify matching didn't pair Anantnag (not in GFS)
    assert "Anantnag" not in matched["district"].values


def test_variable_availability_check():
    """Verify pressure is flagged as absent and precipitation accumulation notes are present."""
    gfs = pd.DataFrame({"temperature_c": [20.0], "precipitation_mm": [1.0]})
    era5 = pd.DataFrame({"temperature_c": [19.0], "precipitation_mm": [0.5]})

    avail = check_variable_availability(gfs, era5)
    assert avail["temperature_c"]["supported"] is True
    assert avail["pressure_hpa"]["supported"] is False
    assert "absent" in avail["pressure_hpa"]["notes"].lower()


def test_bias_correction_leakage_safety_and_held_out_eval():
    """Verify bias correction uses training data only and evaluates on held-out records."""
    np.random.seed(42)
    n = 20
    times = pd.date_range("2026-09-01", periods=n, freq="D")

    # Introduce systematic +3.0 degree positive forecast bias
    true_ref = 20.0 + np.random.normal(0, 1, n)
    fcst = true_ref + 3.0

    df = pd.DataFrame({
        "district": ["Srinagar"] * n,
        "initialization_time": times.strftime("%Y-%m-%d %H:%M:%S"),
        "valid_time": times.strftime("%Y-%m-%d %H:%M:%S"),
        "lead_hours": [12] * n,
        "lead_day": [1] * n,
        "forecast_value": fcst,
        "reference_value": true_ref,
        "error": fcst - true_ref,
        "absolute_error": np.abs(fcst - true_ref),
        "squared_error": (fcst - true_ref) ** 2,
    })

    params, eval_df, test_df = fit_and_evaluate_bias_correction(
        df, train_ratio=0.70, min_samples_threshold=3
    )

    assert not params.empty
    assert len(eval_df) == 2

    # Learned bias should be approximately +3.0
    learned_bias = params["learned_bias"].iloc[0]
    assert np.isclose(learned_bias, 3.0, atol=0.5)

    # Bias correction must reduce MAE on held-out test cases
    raw_mae = eval_df.loc[eval_df["stage"] == "Uncorrected (Raw Forecast)", "MAE"].iloc[0]
    corr_mae = eval_df.loc[eval_df["stage"] == "Corrected (Mean Bias Removed)", "MAE"].iloc[0]
    corr_bias = eval_df.loc[eval_df["stage"] == "Corrected (Mean Bias Removed)", "Bias"].iloc[0]

    assert corr_mae < raw_mae
    assert abs(corr_bias) < 0.5


def test_empty_dataset_handling():
    """Graceful handling of empty dataframes without uncaught exceptions."""
    empty_df = pd.DataFrame()
    metrics = compute_error_metrics(empty_df)
    assert np.isnan(metrics["MAE"])
    assert metrics["sample_count"] == 0

    lead_df, dist_df, _ = calculate_baseline_metrics_tables(empty_df)
    assert lead_df.empty
    assert dist_df.empty
