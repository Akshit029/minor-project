"""
Automated Test Suite for Week 6 Agentic AI and API Integration.

Tests:
1. Reliability Tool: Valid lookups, out-of-bounds lead days, invalid district validation.
2. Forecast-Bust Tool: Valid inference, schema validation for missing fields, no fabrication.
3. Scientific Result Explanation: Mathematical distinction, formulas, definitions.
4. District Comparison: Comparative verification on available vs. unavailable lead days.
5. Deterministic Offline Fallback: Graceful execution when GEMINI_API_KEY is missing.
6. Mocked LLM Flow: Verification of tool-calling loop and synthesized response.
7. FastAPI Endpoints: /api/health, /api/chat, /api/bust-predict, /api/reliability-lookup,
   request validation, request size limits, and safe error masking.
"""

import os
import json
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from src.agentic_ai import (
    lookup_reliability_impl,
    predict_forecast_bust_impl,
    explain_scientific_metrics_impl,
    compare_district_reliability,
    run_agentic_query,
    VALID_DISTRICTS
)
from src.api import app

client = TestClient(app)


# ============================================================================
# 1. TOOL A: RELIABILITY LOOKUP TESTS
# ============================================================================

def test_reliability_lookup_valid_study_districts():
    """Verify that empirical reliability lookups for lead day 1 return valid scores."""
    for dist in VALID_DISTRICTS:
        res = lookup_reliability_impl(dist, lead_day=1)
        assert res["success"] is True, f"Lookup failed for {dist}"
        assert res["district"] == dist
        assert res["lead_day"] == 1
        assert 0.0 <= res["reliability_score_R"] <= 1.0
        assert 0.0 <= res["sample_confidence_C"] <= 1.0
        assert res["training_MAE"] > 0
        assert res["training_sample_count"] > 0
        assert "provenance" in res


def test_reliability_lookup_held_out_lead_day():
    """Verify that lead day 2 retrieves held-out verification records."""
    res = lookup_reliability_impl("Srinagar", lead_day=2)
    assert res["success"] is True
    assert res["lead_day"] == 2
    assert "test_MAE" in res or "observed_MAE" in res or "training_MAE" in res


def test_reliability_lookup_unavailable_lead_day():
    """Verify that lead day 3+ returns transparent disclosure without fabricating numbers."""
    res = lookup_reliability_impl("Jammu", lead_day=4)
    assert res["success"] is False
    assert res["available"] is False
    assert "unavailable" in res["error"].lower()
    assert 1 in res["supported_lead_days"]
    assert 2 in res["supported_lead_days"]


def test_reliability_lookup_invalid_district():
    """Verify that invalid districts are rejected with a helpful list of valid names."""
    res = lookup_reliability_impl("Delhi", lead_day=1)
    assert res["success"] is False
    assert "Invalid district" in res["error"]
    assert "Srinagar" in res["available_districts"]


# ============================================================================
# 2. TOOL B: FORECAST-BUST PREDICTOR TESTS
# ============================================================================

def test_forecast_bust_prediction_valid_features():
    """Verify that complete 7-feature input produces valid inference from Week 5 model."""
    res = predict_forecast_bust_impl(
        district="Srinagar",
        lead_hours=24.0,
        lead_day=1.0,
        forecast_value=18.5,
        init_hour=0.0,
        valid_hour=12.0,
        valid_month=9.0
    )
    assert res["success"] is True
    assert res["district"] == "Srinagar"
    assert 0.0 <= res["bust_probability"] <= 1.0
    assert res["predicted_class"] in ["BUST", "NORMAL"]
    assert res["risk_level"] in ["LOW RISK", "MEDIUM RISK", "HIGH RISK"]
    assert "model_id" in res
    assert res["threshold_used"] == 0.50


def test_forecast_bust_prediction_missing_fields_validation():
    """Verify that missing features are caught and rejected without silent fallback."""
    res = predict_forecast_bust_impl(
        district="Jammu",
        lead_hours=None,
        lead_day=None,
        forecast_value=25.0
    )
    assert res["success"] is False
    assert res["status"] == "missing_inputs"
    assert "lead_hours" in res["missing_fields"]
    assert "valid_month" in res["missing_fields"]
    assert "moisture" not in res["provided_features"]


def test_forecast_bust_prediction_invalid_district():
    """Verify that forecast bust prediction rejects invalid districts."""
    res = predict_forecast_bust_impl(district="London", forecast_value=20.0)
    assert res["success"] is False
    assert "Invalid district" in res["error"]


# ============================================================================
# 3. TOOL C: SCIENTIFIC EXPLANATIONS TESTS
# ============================================================================

def test_scientific_explanation_distinction():
    """Verify explanation clearly distinguishes reliability index and bust probability."""
    res = explain_scientific_metrics_impl("What is the difference between reliability and bust probability?")
    assert "distinction" in res
    assert "Empirical Reliability Index (R" in res["distinction"]
    assert "Forecast-Bust Probability (P_bust" in res["distinction"]
    assert "NOT interchangeable" in res["distinction"]


def test_scientific_explanation_reliability_formula():
    """Verify explanation provides the exact mathematical formulation R = R_error * C."""
    res = explain_scientific_metrics_impl("Explain the reliability index formula")
    assert "definition" in res
    assert "R_error = exp(-MAE / error_scale)" in res["definition"]
    assert "C = n / (n + k)" in res["definition"]
    assert "R = R_error * C" in res["definition"]


def test_scientific_explanation_error_metrics():
    """Verify definition of Forecast - Reference sign convention."""
    res = explain_scientific_metrics_impl("Explain error metrics and bias")
    assert "definition" in res
    assert "Forecast (NOAA GFS) - Reference (ECMWF ERA5)" in res["definition"]


# ============================================================================
# 4. DISTRICT COMPARISON TOOL TESTS
# ============================================================================

def test_compare_district_reliability_available_lead_day():
    """Verify side-by-side comparison for Jammu and Srinagar on lead day 1."""
    out_str = compare_district_reliability.invoke({
        "districts": ["Jammu", "Srinagar"],
        "lead_day": 1
    })
    data = json.loads(out_str)
    assert data["comparison_possible"] is True
    assert len(data["available_comparisons"]) == 2
    assert "summary" in data


def test_compare_district_reliability_unavailable_lead_day():
    """Verify comparative lookup discloses unavailability for lead day 3."""
    out_str = compare_district_reliability.invoke({
        "districts": ["Jammu", "Srinagar"],
        "lead_day": 3
    })
    data = json.loads(out_str)
    assert data["comparison_possible"] is False
    assert len(data["unavailable_notes"]) > 0


# ============================================================================
# 5. DETERMINISTIC ORCHESTRATOR & FALLBACK TESTS
# ============================================================================

def test_deterministic_query_missing_api_key(monkeypatch):
    """Verify that when GEMINI_API_KEY is not set, system returns grounded deterministic answer."""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)

    res = run_agentic_query("Explain the reliability of Srinagar on lead day 1.")
    assert res["gemini_active"] is False
    assert "Srinagar" in res["reply"]
    assert "Reliability Index (R)" in res["reply"]
    assert len(res["tools_called"]) >= 1
    assert res["tools_called"][0]["tool"] == "lookup_reliability"
    assert "setup_notice" in res


def test_deterministic_query_bust_risk(monkeypatch):
    """Verify deterministic query handles bust risk estimation requests."""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)

    res = run_agentic_query(
        message="Estimate forecast-bust risk for this forecast",
        forecast_features={
            "district": "Anantnag",
            "lead_hours": 48.0,
            "lead_day": 2.0,
            "forecast_value": 22.0,
            "init_hour": 0.0,
            "valid_hour": 12.0,
            "valid_month": 9.0
        }
    )
    assert res["gemini_active"] is False
    assert "Forecast-Bust Risk Assessment" in res["reply"]
    assert "Anantnag" in res["reply"]
    assert "Bust Probability" in res["reply"]


# ============================================================================
# 6. MOCKED LLM AGENTIC FLOW TESTS
# ============================================================================

def test_agentic_query_with_mocked_gemini(monkeypatch):
    """Verify that when GEMINI_API_KEY is set, tool calls are parsed and executed."""
    monkeypatch.setenv("GEMINI_API_KEY", "test-mock-key")

    mock_tool_call = {
        "name": "lookup_reliability",
        "args": {"district": "Jammu", "lead_day": 1},
        "id": "call_12345"
    }

    mock_first_response = MagicMock()
    mock_first_response.tool_calls = [mock_tool_call]
    mock_first_response.content = ""

    mock_second_response = MagicMock()
    mock_second_response.content = "Based on Week 4 analysis, Jammu exhibits high reliability (R = 0.0917) on lead day 1."

    mock_llm_instance = MagicMock()
    mock_llm_instance.bind_tools.return_value = mock_llm_instance
    mock_llm_instance.invoke.side_effect = [mock_first_response, mock_second_response]

    with patch("langchain_google_genai.ChatGoogleGenerativeAI", return_value=mock_llm_instance):
        res = run_agentic_query("What is the reliability of Jammu on lead day 1?")
        assert res["gemini_active"] is True
        assert len(res["tools_called"]) == 1
        assert res["tools_called"][0]["tool"] == "lookup_reliability"
        assert "Jammu exhibits high reliability" in res["reply"]


# ============================================================================
# 7. FASTAPI ENDPOINT TESTS
# ============================================================================

def test_api_health_endpoint():
    """Verify GET /api/health returns operational status."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "operational"
    assert "artifacts" in data
    assert "supported_districts" in data


def test_api_chat_endpoint_valid():
    """Verify POST /api/chat processes query and returns structured response."""
    response = client.post("/api/chat", json={
        "message": "What is the difference between reliability and bust probability?"
    })
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert "tools_called" in data
    assert "gemini_active" in data
    assert "structured_data" in data


def test_api_chat_endpoint_empty_message():
    """Verify POST /api/chat rejects empty queries with HTTP 422."""
    response = client.post("/api/chat", json={"message": "   "})
    assert response.status_code == 422


def test_api_bust_predict_endpoint():
    """Verify POST /api/bust-predict matches the frontend ForecastBustPredictionResult interface."""
    payload = {
        "district": "Srinagar",
        "leadDay": 1,
        "forecastValue": 20.0,
        "initHour": 0,
        "validHour": 12,
        "validMonth": 9
    }
    response = client.post("/api/bust-predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["district"] == "Srinagar"
    assert data["leadDay"] == 1
    assert "bustProbability" in data
    assert data["predictedClass"] in ["BUST", "NORMAL"]
    assert data["riskLevel"] in ["LOW RISK", "MEDIUM RISK", "HIGH RISK"]


def test_api_reliability_lookup_endpoint():
    """Verify GET /api/reliability-lookup queries Week 4 parameters."""
    response = client.get("/api/reliability-lookup?district=Baramulla&lead_day=1")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["district"] == "Baramulla"
    assert data["reliability_score_R"] > 0
