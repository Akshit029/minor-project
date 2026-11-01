"""
Unit and Integration Tests for Week 7: SHAP-based Feature Influence Analysis.

Validates:
1. SHAP explainer initialization and compatibility with Week 5 trained model.
2. Feature name consistency after ColumnTransformer preprocessing.
3. Global SHAP feature importance calculation and ranking properties.
4. Individual high-error event extraction and local SHAP explanations.
5. Mathematical consistency: base_value + sum(shap_values) == log_odds.
6. Separation of risk-increasing (positive) and risk-decreasing (negative) features.
7. Meteorological variable audit: humidity and wind speed absent, not fabricated.
8. FastAPI explainability endpoints (health, global, events, local, meteorological).
9. Missing artifact and missing input schema handling.
10. Agentic AI integration with Week 7 tools and deterministic responses.
"""

import os
import json
import pytest
import numpy as np
import pandas as pd
from pathlib import Path
from fastapi.testclient import TestClient

from src.explainability import ForecastBustExplainer, run_week7_explainability
from src.agentic_ai import (
    run_agentic_query,
    get_feature_influence_impl,
    audit_humidity_wind_impl,
    get_forecast_explainer
)
from src.api import app

PROJECT_ROOT = Path(__file__).resolve().parent.parent
W5_DIR = PROJECT_ROOT / "outputs" / "week5"
W7_DIR = PROJECT_ROOT / "outputs" / "week7"


@pytest.fixture
def explainer():
    """Fixture providing initialized ForecastBustExplainer."""
    return ForecastBustExplainer(
        model_path=str(W5_DIR / "trained_model_pipeline.joblib"),
        metadata_path=str(W5_DIR / "model_metadata.json"),
        dataset_path=str(W5_DIR / "labeled_forecast_dataset.csv")
    )


@pytest.fixture
def api_client():
    """Fixture providing FastAPI test client."""
    return TestClient(app)


# ============================================================================
# 1. INITIALIZATION & MODEL COMPATIBILITY
# ============================================================================

def test_explainer_initialization(explainer):
    """Verify explainer correctly inspects the Week 5 model pipeline."""
    assert explainer is not None
    assert explainer.classifier.__class__.__name__ == "LogisticRegression"
    assert explainer.explainer_type == "shap.LinearExplainer"
    assert explainer.explanation_space == "log-odds (logit)"
    assert len(explainer.clean_feature_names) == 10


def test_feature_name_preservation(explainer):
    """Verify clean feature names preserve categorical one-hot and numerical features."""
    names = explainer.clean_feature_names
    # Districts must be present
    assert any("district: Srinagar" in n for n in names)
    assert any("district: Jammu" in n for n in names)
    assert any("district: Anantnag" in n for n in names)
    assert any("district: Baramulla" in n for n in names)
    # Numericals must be present
    assert "lead_hours" in names
    assert "forecast_value" in names
    assert "valid_hour" in names


# ============================================================================
# 2. GLOBAL SHAP FEATURE IMPORTANCE
# ============================================================================

def test_global_feature_importance(explainer):
    """Verify global feature rankings calculation and mathematical properties."""
    glob = explainer.explain_global()
    assert glob["explainer_type"] == "shap.LinearExplainer"
    assert glob["sample_count"] == 44
    assert "base_value_log_odds" in glob
    assert "base_probability" in glob
    assert 0.0 < glob["base_probability"] < 1.0

    rankings = glob["feature_rankings"]
    assert len(rankings) == 10

    # Ensure sorted by mean_abs_shap descending
    for i in range(len(rankings) - 1):
        assert rankings[i]["mean_abs_shap"] >= rankings[i + 1]["mean_abs_shap"]

    # Relative percentages must sum approximately to 100%
    total_pct = sum(r["relative_importance_pct"] for r in rankings)
    assert pytest.approx(total_pct, abs=0.5) == 100.0

    # Top feature should be lead_hours
    assert rankings[0]["feature"] == "lead_hours"


def test_grouped_concept_importance(explainer):
    """Verify aggregated domain concept rankings."""
    glob = explainer.explain_global()
    grouped = glob["grouped_rankings"]
    assert len(grouped) >= 4
    concepts = [g["concept"] for g in grouped]
    assert any("lead_time" in c for c in concepts)
    assert any("diurnal_cycle" in c for c in concepts)
    assert any("forecast_temperature" in c for c in concepts)
    assert any("district" in c for c in concepts)


# ============================================================================
# 3. LOCAL INSTANCE EXPLANATION & ADDITIVITY
# ============================================================================

def test_local_instance_explanation(explainer):
    """Verify exact additive decomposition: base_value + sum(shap_values) == final_log_odds."""
    test_instance = {
        "district": "Baramulla",
        "lead_hours": 15.0,
        "lead_day": 1.0,
        "forecast_value": 13.46,
        "init_hour": 0.0,
        "valid_hour": 15.0,
        "valid_month": 9.0
    }
    res = explainer.explain_instance(test_instance)

    pred = res["prediction"]
    summary = res["shap_summary"]

    # Verify prediction outputs
    assert 0.0 <= pred["bust_probability"] <= 1.0
    assert pred["predicted_class"] in [0, 1]
    assert pred["risk_level"] in ["LOW RISK", "MEDIUM RISK", "HIGH RISK"]

    # Verify additivity in log-odds space
    expected_log_odds = summary["base_value_log_odds"] + summary["sum_shap_values"]
    assert pytest.approx(expected_log_odds, abs=1e-3) == summary["final_log_odds"]

    # Verify sigmoid probability consistency
    expected_prob = 1.0 / (1.0 + np.exp(-summary["final_log_odds"]))
    assert pytest.approx(expected_prob, abs=1e-3) == pred["bust_probability"]

    # Relative contributions must sum to 100%
    total_share = sum(c["relative_contribution_pct"] for c in res["all_feature_contributions"])
    assert pytest.approx(total_share, abs=0.5) == 100.0


def test_positive_negative_directionality(explainer):
    """Verify features increasing risk have positive SHAP and vice-versa."""
    test_instance = {
        "district": "Anantnag",
        "lead_hours": 27.0,
        "lead_day": 2.0,
        "forecast_value": 15.23,
        "init_hour": 0.0,
        "valid_hour": 3.0,
        "valid_month": 9.0
    }
    res = explainer.explain_instance(test_instance)

    for item in res["features_increasing_risk"]:
        assert item["shap_value"] > 0
        assert item["direction"] == "INCREASED_RISK"

    for item in res["features_decreasing_risk"]:
        assert item["shap_value"] < 0
        assert item["direction"] == "DECREASED_RISK"


# ============================================================================
# 4. HIGH-ERROR EVENT ANALYSIS
# ============================================================================

def test_high_error_events_identification(explainer):
    """Verify high-error events are sorted by actual absolute error descending."""
    events = explainer.identify_high_error_events(top_n=5)
    assert len(events) == 5

    # Check sorting by actual absolute error
    for i in range(len(events) - 1):
        assert events[i]["actual_absolute_error_c"] >= events[i + 1]["actual_absolute_error_c"]

    # Event 21 should be the highest error event (-10.02°C)
    top_ev = events[0]
    assert top_ev["event_id"] == 21
    assert top_ev["district"] == "Baramulla"
    assert pytest.approx(top_ev["actual_error_c"], abs=0.1) == -10.02
    assert top_ev["actual_is_bust"] == 1

    # Distinction note must be present
    assert "scientific_distinction_note" in top_ev
    assert "Actual Forecast Error" in top_ev["scientific_distinction_note"]
    assert "Predicted Bust Probability" in top_ev["scientific_distinction_note"]


# ============================================================================
# 5. METEOROLOGICAL VARIABLE AUDIT (HUMIDITY & WIND SPEED)
# ============================================================================

def test_meteorological_variable_audit(explainer):
    """Verify humidity and wind speed are audited as absent without data fabrication."""
    audit = explainer.audit_meteorological_variables()
    assert audit["humidity_available"] is False
    assert audit["wind_speed_available"] is False

    vars_audited = {v["variable"]: v for v in audit["variables_audited"]}
    assert "relative_humidity" in vars_audited
    assert "wind_speed" in vars_audited
    assert "temperature_c" in vars_audited

    assert vars_audited["relative_humidity"]["in_week5_model"] is False
    assert vars_audited["wind_speed"]["in_week5_model"] is False
    assert vars_audited["temperature_c"]["in_week5_model"] is True

    # Exploratory analysis on available variables must exist
    exp = audit["exploratory_meteorological_analysis"]
    assert "lead_time_relationship" in exp
    assert "temperature_relationship" in exp
    assert "diurnal_relationship" in exp


# ============================================================================
# 6. FASTAPI EXPLAINABILITY ENDPOINTS
# ============================================================================

def test_api_health_includes_week7(api_client):
    """Verify /api/health reports Week 7 metadata artifact status."""
    resp = api_client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["artifacts"]["week7_shap_metadata"] is True


def test_api_explainability_global(api_client):
    """Verify GET /api/explainability/global returns valid structured rankings."""
    resp = api_client.get("/api/explainability/global")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["scope"] == "global"
    assert len(data["feature_rankings"]) == 10
    assert data["feature_rankings"][0]["feature"] == "lead_hours"


def test_api_explainability_events(api_client):
    """Verify GET /api/explainability/events returns analyzed high-error cases."""
    resp = api_client.get("/api/explainability/events")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert len(data["events"]) >= 5
    assert data["events"][0]["event_id"] == 21


def test_api_explainability_local_post(api_client):
    """Verify POST /api/explainability/local computes on-the-fly local SHAP attributions."""
    payload = {
        "district": "Anantnag",
        "leadDay": 2,
        "forecastValue": 15.2,
        "initHour": 0,
        "validHour": 12,
        "validMonth": 9
    }
    resp = api_client.post("/api/explainability/local", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["district"] == "Anantnag"
    assert "bust_probability" in data["prediction"]
    assert len(data["allFeatureContributions"]) == 10
    assert "narrativeExplanation" in data


def test_api_explainability_meteorological(api_client):
    """Verify GET /api/explainability/meteorological audits atmospheric variables."""
    resp = api_client.get("/api/explainability/meteorological")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["audit"]["humidity_available"] is False
    assert data["audit"]["wind_speed_available"] is False


# ============================================================================
# 7. AI ASSISTANT WEEK 7 INTEGRATION
# ============================================================================

def test_agentic_query_why_bust():
    """Verify AI assistant answers why a specific forecast was a bust with SHAP drivers."""
    res = run_agentic_query("Why was the forecast in Baramulla classified as a bust?")
    assert "reply" in res
    assert "Event 21" in res["reply"] or "Baramulla" in res["reply"]
    assert "SHAP" in res["reply"]
    assert "Actual Retrospective Error" in res["reply"] or "Actual Error" in res["reply"]


def test_agentic_query_humidity_wind():
    """Verify AI assistant explains humidity and wind speed data availability accurately."""
    res = run_agentic_query("How do humidity and wind speed relate to forecast errors in the available data?")
    assert "reply" in res
    assert "ABSENT" in res["reply"]
    assert "not fabricated" in res["reply"] or "Not used in Week 5 model" in res["reply"]
    assert "Forecast Horizon" in res["reply"]


def test_agentic_query_global_importance():
    """Verify AI assistant returns global SHAP rankings."""
    res = run_agentic_query("Which features contributed most to predicted bust risk according to SHAP?")
    assert "reply" in res
    assert "lead_hours" in res["reply"]
    assert "valid_hour" in res["reply"]
    assert "forecast_value" in res["reply"]


# ============================================================================
# 8. ERROR & EDGE CASE HANDLING
# ============================================================================

def test_missing_model_file_error_handling():
    """Verify explainer raises FileNotFoundError when given non-existent paths."""
    with pytest.raises(FileNotFoundError):
        ForecastBustExplainer(model_path="non_existent_model.joblib")


def test_missing_input_feature_error_handling(explainer):
    """Verify explain_instance raises ValueError if a required feature is absent."""
    with pytest.raises(ValueError, match="Missing required feature"):
        explainer.explain_instance({"district": "Srinagar"})

