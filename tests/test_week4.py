"""
Unit tests for Week 4: Spatiotemporal Modelling for Reliability Scoring.
"""

import numpy as np
import pandas as pd
import pytest

from src.reliability import (
    calculate_sample_confidence,
    calculate_reliability_score,
    estimate_spatiotemporal_reliability,
    evaluate_reliability_on_held_out,
    perform_sensitivity_analysis
)


def test_reliability_score_bounds_and_zero_error():
    """Verify score is bounded in [0, 1] and zero error yields maximum R_error = 1.0."""
    r, r_err, c = calculate_reliability_score(mae=0.0, error_scale=2.0, sample_count=100, k=10.0)
    assert r_err == 1.0
    assert 0.0 <= r <= 1.0
    assert np.isclose(c, 100 / 110)
    assert np.isclose(r, 100 / 110)


def test_monotonic_decrease_with_increasing_error():
    """Verify increasing MAE strictly decreases reliability score R."""
    r1, _, _ = calculate_reliability_score(mae=1.0, error_scale=2.0, sample_count=50, k=10.0)
    r2, _, _ = calculate_reliability_score(mae=2.0, error_scale=2.0, sample_count=50, k=10.0)
    r3, _, _ = calculate_reliability_score(mae=4.0, error_scale=2.0, sample_count=50, k=10.0)

    assert r1 > r2 > r3


def test_confidence_factor_increases_with_sample_count():
    """Verify confidence factor C increases monotonically with sample count n."""
    c1 = calculate_sample_confidence(n=5, k=10.0)
    c2 = calculate_sample_confidence(n=10, k=10.0)
    c3 = calculate_sample_confidence(n=50, k=10.0)

    assert c1 < c2 < c3
    assert np.isclose(c2, 0.5)


def test_insufficient_evidence_returns_none():
    """Verify sample counts below minimum threshold return None (not false zero)."""
    r, r_err, c = calculate_reliability_score(mae=1.5, error_scale=2.0, sample_count=2, k=10.0, min_evidence_samples=5)
    assert r is None
    assert r_err is None
    assert c is None


def test_invalid_parameters_rejected():
    """Verify non-positive error scales or smoothing k raise ValueError."""
    with pytest.raises(ValueError):
        calculate_reliability_score(mae=1.0, error_scale=-2.0, sample_count=10, k=10.0)

    with pytest.raises(ValueError):
        calculate_reliability_score(mae=1.0, error_scale=2.0, sample_count=10, k=-5.0)

    with pytest.raises(ValueError):
        calculate_sample_confidence(n=-1, k=10.0)


def test_spatiotemporal_reliability_estimation_and_provenance():
    """Verify spatiotemporal table creation and provenance tracking."""
    df = pd.DataFrame({
        "district": ["Srinagar"] * 10 + ["Jammu"] * 2,
        "lead_day": [1] * 12,
        "variable": ["temperature_c"] * 12,
        "absolute_error": [1.5] * 10 + [2.0] * 2,
    })

    rel_table = estimate_spatiotemporal_reliability(df, error_scale=2.0, k=5.0, min_evidence_samples=3)
    assert not rel_table.empty

    srinagar_row = rel_table[rel_table["district"] == "Srinagar"].iloc[0]
    jammu_row = rel_table[rel_table["district"] == "Jammu"].iloc[0]

    # Srinagar has 10 samples (>= 3), so provenance is district_lead_day
    assert srinagar_row["provenance"] == "district_lead_day"
    # Jammu has 2 samples (< 3), so it falls back to regional
    assert "fallback" in jammu_row["provenance"]


def test_sensitivity_analysis_execution():
    """Verify sensitivity analysis generates complete grid of parameters."""
    df = pd.DataFrame({
        "lead_day": [1, 1, 2, 2],
        "absolute_error": [1.0, 1.5, 2.0, 2.5]
    })
    sens = perform_sensitivity_analysis(df, error_scales=[1.0, 2.0], k_values=[5.0, 10.0])
    assert len(sens) == 2 * 2 * 2  # 2 lead days x 2 scales x 2 k values
    assert "reliability_score_R" in sens.columns
