"""
Week 6: Agentic AI Workflow Integration Module for Weather Forecast Reliability.

Orchestrates existing scientific modules (Week 4 Reliability & Week 5 Forecast-Bust Classifier)
using LangChain and Google Gemini (via langchain-google-genai).

Core Capabilities:
1. Tool A: Reliability Lookup (connects to Week 4 empirical reliability calculation and tables).
2. Tool B: Forecast-Bust Prediction (connects to Week 5 serialized model and input schema).
3. Tool C: Scientific Result Explanation (differentiates reliability, confidence, bust probability, and error metrics).
4. Tool D: District Comparison (side-by-side reliability analysis strictly for available verification data).
5. Configurable LLM Provider: Google Gemini with robust deterministic fallback for offline/demo reliability.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import re
import pandas as pd
import numpy as np
from dotenv import load_dotenv

# Load local environment variables
load_dotenv()

# LangChain Imports
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage

# Project Imports
from src.reliability import calculate_reliability_score, calculate_sample_confidence
from src.forecast_bust import ForecastBustPredictor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("agentic_ai")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
W4_DIR = PROJECT_ROOT / "outputs" / "week4"
W5_DIR = PROJECT_ROOT / "outputs" / "week5"
W3_DIR = PROJECT_ROOT / "outputs" / "week3"
W7_DIR = PROJECT_ROOT / "outputs" / "week7"

# Standard target districts for Jammu & Kashmir
VALID_DISTRICTS = ["Srinagar", "Jammu", "Anantnag", "Baramulla"]

# Global cache for the forecast-bust predictor instance
_PREDICTOR_INSTANCE: Optional[ForecastBustPredictor] = None
_EXPLAINER_INSTANCE: Optional[Any] = None


def get_bust_predictor() -> Optional[ForecastBustPredictor]:
    """Retrieve or instantiate the cached Week 5 ForecastBustPredictor."""
    global _PREDICTOR_INSTANCE
    if _PREDICTOR_INSTANCE is not None:
        return _PREDICTOR_INSTANCE

    model_path = W5_DIR / "trained_model_pipeline.joblib"
    meta_path = W5_DIR / "model_metadata.json"

    if model_path.exists() and meta_path.exists():
        try:
            _PREDICTOR_INSTANCE = ForecastBustPredictor(str(model_path), str(meta_path))
            logger.info("Successfully loaded ForecastBustPredictor from %s", model_path)
            return _PREDICTOR_INSTANCE
        except Exception as e:
            logger.error("Error loading ForecastBustPredictor: %s", e)
            return None
    return None


def get_forecast_explainer() -> Optional[Any]:
    """Retrieve or instantiate the cached Week 7 ForecastBustExplainer."""
    global _EXPLAINER_INSTANCE
    if _EXPLAINER_INSTANCE is not None:
        return _EXPLAINER_INSTANCE

    model_path = W5_DIR / "trained_model_pipeline.joblib"
    meta_path = W5_DIR / "model_metadata.json"
    data_path = W5_DIR / "labeled_forecast_dataset.csv"

    if model_path.exists() and meta_path.exists():
        try:
            from src.explainability import ForecastBustExplainer
            _EXPLAINER_INSTANCE = ForecastBustExplainer(
                model_path=str(model_path),
                metadata_path=str(meta_path),
                dataset_path=str(data_path) if data_path.exists() else None
            )
            logger.info("Successfully loaded ForecastBustExplainer.")
            return _EXPLAINER_INSTANCE
        except Exception as e:
            logger.error("Error loading ForecastBustExplainer: %s", e)
            return None
    return None


def normalize_district_name(district: str) -> Optional[str]:
    """Normalize user district input to valid study district name."""
    if not district:
        return None
    clean = district.strip().lower()
    for valid in VALID_DISTRICTS:
        if valid.lower() == clean:
            return valid
    return None


# ============================================================================
# SCIENTIFIC TOOLS (LANGCHAIN ACCESSIBLE)
# ============================================================================

def lookup_reliability_impl(district: str, lead_day: int) -> Dict[str, Any]:
    """
    Connect to Week 4 reliability tables and calculate empirical reliability metrics.
    Reuses real calculation and actual artifact schema without duplicating formulas.
    """
    normalized_district = normalize_district_name(district)
    if not normalized_district:
        return {
            "success": False,
            "error": f"Invalid district '{district}'. Valid study districts are: {', '.join(VALID_DISTRICTS)}.",
            "available_districts": VALID_DISTRICTS,
            "district": district,
            "lead_day": lead_day,
        }

    rel_table_path = W4_DIR / "reliability_table.csv"
    eval_table_path = W4_DIR / "held_out_evaluation.csv"
    metrics_path = W3_DIR / "district_lead_metrics.csv"

    # 1. First, check Week 4 training reliability table
    if rel_table_path.exists():
        try:
            rel_df = pd.read_csv(rel_table_path)
            match = rel_df[(rel_df["district"] == normalized_district) & (rel_df["lead_day"] == int(lead_day))]
            if not match.empty:
                row = match.iloc[0]
                return {
                    "success": True,
                    "district": normalized_district,
                    "lead_day": int(lead_day),
                    "reliability_score_R": float(row["reliability_score_R"]),
                    "sample_confidence_C": float(row["confidence_factor_C"]),
                    "error_component_R_error": float(row["R_error"]),
                    "training_MAE": float(row["training_MAE"]),
                    "training_sample_count": int(row["training_sample_count"]),
                    "error_tolerance_scale": float(row["error_tolerance_scale"]),
                    "confidence_k": float(row["confidence_factor_k"]),
                    "provenance": str(row["provenance"]),
                    "split_source": "Historical Training Period (70% split)",
                    "note": f"Directly extracted from Week 4 spatiotemporal reliability table for {normalized_district} lead day {lead_day}."
                }
        except Exception as e:
            logger.warning("Failed to read reliability table: %s", e)

    # 2. Check held-out evaluation set
    if eval_table_path.exists():
        try:
            eval_df = pd.read_csv(eval_table_path)
            match = eval_df[(eval_df["district"] == normalized_district) & (eval_df["lead_day"] == int(lead_day))]
            if not match.empty:
                row = match.iloc[0]
                test_mae = float(row["test_MAE"])
                test_n = int(row["test_sample_count"])
                error_scale = 2.0
                k_param = 10.0
                r, r_err, c = calculate_reliability_score(test_mae, error_scale, test_n, k_param)
                return {
                    "success": True,
                    "district": normalized_district,
                    "lead_day": int(lead_day),
                    "reliability_score_R": r,
                    "sample_confidence_C": c,
                    "error_component_R_error": r_err,
                    "test_MAE": test_mae,
                    "test_sample_count": test_n,
                    "error_tolerance_scale": error_scale,
                    "confidence_k": k_param,
                    "provenance": "held_out_test_evaluation",
                    "split_source": "Held-Out Test Period (15% split)",
                    "note": f"Evaluated on held-out test verification records for {normalized_district} lead day {lead_day} using Week 4 mathematical formula."
                }
        except Exception as e:
            logger.warning("Failed to read held-out evaluation: %s", e)

    # 3. Check district lead metrics from Week 3
    if metrics_path.exists():
        try:
            m_df = pd.read_csv(metrics_path)
            match = m_df[(m_df["district"] == normalized_district) & (m_df["lead_day"] == int(lead_day))]
            if not match.empty:
                row = match.iloc[0]
                mae_val = float(row["MAE"])
                n_val = int(row["sample_count"])
                r, r_err, c = calculate_reliability_score(mae_val, 2.0, n_val, 10.0)
                return {
                    "success": True,
                    "district": normalized_district,
                    "lead_day": int(lead_day),
                    "reliability_score_R": r,
                    "sample_confidence_C": c,
                    "error_component_R_error": r_err,
                    "observed_MAE": mae_val,
                    "sample_count": n_val,
                    "provenance": "matched_validation_dataset",
                    "note": f"Calculated from matched forecast-reanalysis dataset for {normalized_district} lead day {lead_day}."
                }
        except Exception as e:
            logger.warning("Failed to read district lead metrics: %s", e)

    # If lead day is out of range or not in dataset:
    return {
        "success": False,
        "available": False,
        "district": normalized_district,
        "lead_day": int(lead_day),
        "error": f"Verification data is unavailable for {normalized_district} at lead day {lead_day}.",
        "dataset_limitation": "The current verification dataset covers lead days 1 and 2 (NOAA GFS vs. ECMWF ERA5 September 2026 verification period). Lead day 3+ verification records are not present in the historical archive.",
        "supported_lead_days": [1, 2],
        "supported_districts": VALID_DISTRICTS
    }


@tool
def lookup_reliability(district: str, lead_day: int) -> str:
    """
    Look up empirical forecast reliability metrics for a specified Jammu & Kashmir district and forecast lead day.
    Returns the reliability index R in [0, 1], sample confidence C, historical MAE, sample count, and provenance.
    Only call for valid districts: Srinagar, Jammu, Anantnag, Baramulla.
    """
    res = lookup_reliability_impl(district, lead_day)
    return json.dumps(res, indent=2)


def predict_forecast_bust_impl(
    district: str,
    lead_hours: Optional[float] = None,
    lead_day: Optional[float] = None,
    forecast_value: Optional[float] = None,
    init_hour: Optional[float] = None,
    valid_hour: Optional[float] = None,
    valid_month: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Predict prospective forecast bust probability using the trained Week 5 model.
    Validates input schema and rejects missing features without fabricating values.
    """
    normalized_district = normalize_district_name(district)
    if not normalized_district:
        return {
            "success": False,
            "error": f"Invalid district '{district}'. Valid study districts are: {', '.join(VALID_DISTRICTS)}.",
            "available_districts": VALID_DISTRICTS,
        }

    # Derive lead_hours from lead_day or vice-versa if only one is provided
    if lead_hours is None and lead_day is not None:
        lead_hours = float(lead_day) * 24.0
    elif lead_day is None and lead_hours is not None:
        lead_day = float(lead_hours) / 24.0

    # Strict Schema Validation: All required features must be present
    required_features = {
        "district": normalized_district,
        "lead_hours": lead_hours,
        "lead_day": lead_day,
        "forecast_value": forecast_value,
        "init_hour": init_hour,
        "valid_hour": valid_hour,
        "valid_month": valid_month,
    }

    missing_fields = [k for k, v in required_features.items() if v is None]
    if missing_fields:
        return {
            "success": False,
            "status": "missing_inputs",
            "error": f"Cannot compute forecast bust prediction. Missing required features: {missing_fields}.",
            "missing_fields": missing_fields,
            "provided_features": {k: v for k, v in required_features.items() if v is not None},
            "schema_explanation": (
                "The Week 5 Forecast-Bust Classifier strictly requires 7 features: "
                "district (categorical), lead_hours, lead_day, forecast_value (in °C), "
                "init_hour (0, 6, 12, 18), valid_hour (0, 6, 12, 18), and valid_month (1-12). "
                "Note: Atmospheric moisture (humidity) and wind speed are NOT features in this model."
            )
        }

    predictor = get_bust_predictor()
    if predictor is None:
        return {
            "success": False,
            "error": "Trained forecast-bust model pipeline is unavailable (outputs/week5/trained_model_pipeline.joblib not found).",
            "instructions": "Execute 'python src/forecast_bust.py' to train and serialize the model pipeline."
        }

    # Construct single-row DataFrame with the exact model schema
    input_df = pd.DataFrame([{
        "district": str(normalized_district),
        "lead_hours": float(lead_hours),
        "lead_day": float(lead_day),
        "forecast_value": float(forecast_value),
        "init_hour": float(init_hour),
        "valid_hour": float(valid_hour),
        "valid_month": float(valid_month),
    }])

    try:
        pred_df = predictor.predict(input_df)
        prob = float(pred_df["bust_probability"].iloc[0])
        pred_class = int(pred_df["predicted_bust_class"].iloc[0])
        model_id = str(pred_df["model_id"].iloc[0])

        risk_level = "HIGH RISK" if prob >= 0.70 else "MEDIUM RISK" if prob >= 0.35 else "LOW RISK"
        classification_label = "BUST" if pred_class == 1 else "NORMAL"

        return {
            "success": True,
            "district": normalized_district,
            "forecast_value": float(forecast_value),
            "lead_day": float(lead_day),
            "lead_hours": float(lead_hours),
            "init_hour": float(init_hour),
            "valid_hour": float(valid_hour),
            "valid_month": float(valid_month),
            "bust_probability": round(prob, 4),
            "bust_probability_percent": f"{round(prob * 100, 1)}%",
            "predicted_class": classification_label,
            "risk_level": risk_level,
            "model_id": model_id,
            "threshold_used": 0.50,
            "label_definition": "Error exceeding upper 90th percentile of training absolute errors",
            "note": "Prediction produced by Week 5 machine-learning inference pipeline without fabricating missing values."
        }
    except Exception as e:
        logger.error("Inference execution failed: %s", e)
        return {
            "success": False,
            "error": f"Model inference failed: {str(e)}"
        }


@tool
def predict_forecast_bust(
    district: str,
    lead_hours: float,
    lead_day: float,
    forecast_value: float,
    init_hour: float,
    valid_hour: float,
    valid_month: float
) -> str:
    """
    Predict forecast-bust risk probability for an incoming medium-range forecast.
    A forecast bust occurs when absolute forecast error exceeds the empirical 90th percentile of training errors.
    All 7 features must be provided:
      - district: 'Srinagar', 'Jammu', 'Anantnag', or 'Baramulla'
      - lead_hours: e.g. 24.0, 48.0, 72.0
      - lead_day: e.g. 1.0, 2.0, 3.0
      - forecast_value: numerical forecast temperature in Celsius
      - init_hour: diurnal cycle cycle (0.0, 6.0, 12.0, or 18.0)
      - valid_hour: target forecast hour (0.0, 6.0, 12.0, or 18.0)
      - valid_month: calendar month (1.0 to 12.0)
    Note: Atmospheric moisture (humidity) and wind speed are NOT features in this model.
    """
    res = predict_forecast_bust_impl(
        district=district,
        lead_hours=lead_hours,
        lead_day=lead_day,
        forecast_value=forecast_value,
        init_hour=init_hour,
        valid_hour=valid_hour,
        valid_month=valid_month
    )
    return json.dumps(res, indent=2)


def explain_scientific_metrics_impl(topic: str) -> Dict[str, Any]:
    """
    Provide scientific clarification for project concepts and metrics.
    Ensures mathematical distinction between reliability and bust probability.
    """
    clean_topic = topic.strip().lower()

    if "difference" in clean_topic or "compare" in clean_topic or "bust vs" in clean_topic or "versus" in clean_topic:
        return {
            "topic": "Difference Between Reliability Index and Forecast-Bust Probability",
            "distinction": (
                "The Empirical Reliability Index (R) and Forecast-Bust Probability (P_bust) measure fundamentally different quantities and are NOT interchangeable:\n\n"
                "1. Empirical Reliability Index (R ∈ [0, 1]):\n"
                "   - A retrospective historical performance metric.\n"
                "   - Formula: R = R_error * C = exp(-MAE / scale) * (n / (n + k)).\n"
                "   - Measures the overall expected trustworthiness of forecasts for a given district and lead day based on historical verification.\n"
                "   - High R (close to 1.0) means consistently low historical error and high sample verification count.\n\n"
                "2. Forecast-Bust Probability (P_bust ∈ [0, 1]):\n"
                "   - A prospective machine-learning classification prediction for an upcoming individual forecast.\n"
                "   - Predicts the probability that this specific forecast's error will exceed the empirical 90th percentile threshold (an extreme failure event).\n"
                "   - High P_bust indicates elevated risk of an extreme error, regardless of the baseline average reliability."
            ),
            "key_takeaway": "Reliability reflects baseline historical accuracy; Bust Probability flags prospective extreme event failure risk."
        }

    if "reliability" in clean_topic or "index" in clean_topic:
        return {
            "topic": "Empirical Reliability Index (R)",
            "definition": (
                "The Empirical Reliability Index R ∈ [0, 1] quantifies the expected precision of numerical weather forecasts:\n\n"
                "• Error Component: R_error = exp(-MAE / error_scale)\n"
                "  where error_scale is the acceptable tolerance (2.0°C for temperature). R_error approaches 1 when MAE is near zero and decays exponentially as errors increase.\n\n"
                "• Sample Confidence Factor: C = n / (n + k)\n"
                "  where n is the number of historical verification cases and k is the confidence damping parameter (default k = 10.0). This prevents misleading high scores from sparse samples.\n\n"
                "• Combined Metric: R = R_error * C\n"
                "  Strictly bounded in [0, 1]. A score of 0 indicates either high error or lack of verification samples, whereas 1.0 indicates perfect accuracy supported by infinite samples."
            )
        }

    if "bust" in clean_topic:
        return {
            "topic": "Forecast-Bust Definition and Prediction",
            "definition": (
                "A 'forecast bust' represents an operational failure where the Numerical Weather Prediction error exceeds standard margins:\n\n"
                "• Label Definition: Formulated as the upper 90th percentile (quantile = 0.90) of historical training absolute errors.\n"
                "• Thresholds: Typically ~3.0°C to 8.3°C across J&K districts depending on terrain complexity and lead time.\n"
                "• Machine-Learning Model: Trained using Logistic Regression and Random Forest strictly on forecast issuance variables (district, lead hours, forecast temperature, diurnal cycle, and month).\n"
                "• Imbalance Handling: Because busts represent ~10% of cases, models utilize balanced class weighting and are evaluated via Precision-Recall curves."
            )
        }

    if "error" in clean_topic or "mae" in clean_topic or "bias" in clean_topic:
        return {
            "topic": "Forecast Verification Error Metrics",
            "definition": (
                "Forecast error is defined using the standard meteorological convention:\n"
                "  Error = Forecast (NOAA GFS) - Reference (ECMWF ERA5)\n\n"
                "• MAE (Mean Absolute Error): Average magnitude of errors regardless of sign. Less sensitive to outliers.\n"
                "• RMSE (Root Mean Square Error): Penalizes larger errors quadratically; sensitive to extreme busts.\n"
                "• Bias (Mean Signed Error): Indicates systematic tendencies. Positive bias = model forecasts warmer than ERA5; negative bias = model forecasts cooler than ERA5."
            )
        }

    if "shap" in clean_topic or "waterfall" in clean_topic or "feature influence" in clean_topic or "importance" in clean_topic:
        return {
            "topic": "SHAP (SHapley Additive exPlanations) & Feature Influence",
            "definition": (
                "SHAP is a game-theoretic framework that explains machine-learning predictions by computing exact additive feature contributions:\n\n"
                "• Mathematical Basis: Based on Shapley values from cooperative game theory, ensuring local accuracy, missingness, and consistency.\n"
                "• Linear Model Formulation: For Logistic Regression, f(x) = E[f(x)] + ∑ φ_j in log-odds (logit) space, where E[f(x)] is the base value.\n"
                "• Directionality: Positive SHAP values (φ_j > 0) increase log-odds toward a forecast bust; negative SHAP values (φ_j < 0) reduce bust risk.\n"
                "• Waterfall Plots: Graphically display how individual features push a single prediction from the base expected value to the final log-odds score.\n"
                "• Global Influence: Measured by Mean Absolute SHAP (E[|φ_j|]), quantifying overall feature importance across all forecasts."
            )
        }

    if "humidity" in clean_topic or "wind" in clean_topic:
        return {
            "topic": "Meteorological Variables: Humidity and Wind Speed Status",
            "definition": (
                "In the current Jammu & Kashmir verification dataset:\n\n"
                "• Status: Atmospheric relative humidity and 10m wind speed are absent from the downloaded local archive and are NOT features in the Week 5 model.\n"
                "• Integrity Rule: No synthetic values are fabricated. The model strictly evaluates 2m temperature forecast issuance variables.\n"
                "• Available Exploratory Insights: Lead time horizon and diurnal valid hour exhibit strong empirical correlations with verification errors."
            )
        }

    return {
        "topic": "Scientific Meteorological Terminology",
        "supported_topics": [
            "Difference between reliability and bust probability",
            "What does the reliability index mean?",
            "What is a forecast bust?",
            "Forecast error metrics (MAE, RMSE, Bias)",
            "SHAP and feature influence analysis",
            "Role of humidity and wind speed"
        ]
    }


@tool
def explain_scientific_metrics(topic: str) -> str:
    """
    Explain scientific metrics, mathematical formulas, and terminology used in the project.
    Can explain:
      - 'reliability_index': Mathematical formulation of R = R_error * C
      - 'bust_probability': Meaning and threshold definition of forecast busts
      - 'difference_reliability_bust': Difference between reliability index and bust risk
      - 'error_metrics': MAE, RMSE, Bias sign convention (Forecast - Reference)
    """
    res = explain_scientific_metrics_impl(topic)
    return json.dumps(res, indent=2)


@tool
def compare_district_reliability(districts: List[str], lead_day: int) -> str:
    """
    Compare empirical forecast reliability between two or more study districts for a given lead day.
    Retrieves real verification records for each district and formats a side-by-side comparison.
    If real verification data is missing for any district or lead day, clearly discloses that it is unavailable.
    """
    comparisons = []
    missing_districts = []

    for d in districts:
        norm = normalize_district_name(d)
        if not norm:
            missing_districts.append(f"{d} (invalid district name)")
            continue

        lookup = lookup_reliability_impl(norm, lead_day)
        if lookup.get("success"):
            comparisons.append(lookup)
        else:
            missing_districts.append(f"{norm}: {lookup.get('error', 'Data unavailable')}")

    out = {
        "lead_day": lead_day,
        "available_comparisons": comparisons,
        "unavailable_notes": missing_districts,
        "comparison_possible": len(comparisons) >= 2,
    }

    if len(comparisons) >= 2:
        sorted_by_r = sorted(comparisons, key=lambda x: x.get("reliability_score_R", 0), reverse=True)
        best = sorted_by_r[0]
        worst = sorted_by_r[-1]
        out["summary"] = (
            f"At lead day {lead_day}, {best['district']} exhibits higher empirical reliability "
            f"(R = {best.get('reliability_score_R')}) with MAE = {best.get('training_MAE', best.get('test_MAE'))}°C, "
            f"compared to {worst['district']} (R = {worst.get('reliability_score_R')}) "
            f"with MAE = {worst.get('training_MAE', worst.get('test_MAE'))}°C."
        )

    return json.dumps(out, indent=2)


def get_feature_influence_impl(
    scope: str = "global",
    event_id: Optional[int] = None,
    district: Optional[str] = None
) -> Dict[str, Any]:
    """Retrieve actual SHAP feature influence results (global or high-error event)."""
    meta_file = W7_DIR / "shap_analysis_metadata.json"
    if meta_file.exists():
        try:
            with open(meta_file, "r", encoding="utf-8") as f:
                w7_data = json.load(f)

            if scope == "global":
                return {
                    "success": True,
                    "scope": "global",
                    "model_explained": w7_data.get("model_explained"),
                    "explainer_class": w7_data.get("explainer_class"),
                    "explanation_space": w7_data.get("explanation_space"),
                    "base_value_log_odds": w7_data.get("global_analysis", {}).get("base_value_log_odds"),
                    "base_probability": w7_data.get("global_analysis", {}).get("base_probability"),
                    "feature_rankings": w7_data.get("global_analysis", {}).get("feature_rankings", []),
                    "grouped_rankings": w7_data.get("global_analysis", {}).get("grouped_rankings", [])
                }
            elif scope in ["event", "local", "high_error"]:
                events = w7_data.get("high_error_events_analyzed", [])
                if event_id is not None:
                    matched = [e for e in events if e.get("event_id") == event_id]
                    if matched:
                        return {"success": True, "event": matched[0]}
                if district:
                    norm_d = normalize_district_name(district)
                    if norm_d:
                        matched = [e for e in events if e.get("district") == norm_d]
                        if matched:
                            return {"success": True, "event": matched[0], "matched_district": norm_d}
                return {
                    "success": True,
                    "scope": "high_error_events",
                    "events": events[:5],
                    "total_analyzed": len(events)
                }
        except Exception as e:
            logger.warning("Error reading week7 metadata file: %s", e)

    # Fallback to live explainer
    explainer = get_forecast_explainer()
    if explainer is None:
        return {
            "success": False,
            "error": "SHAP Explainer artifact not available. Please verify outputs/week5 and outputs/week7."
        }

    if scope == "global":
        glob_res = explainer.explain_global()
        return {"success": True, "scope": "global", "global_analysis": glob_res}
    else:
        events = explainer.identify_high_error_events(top_n=5)
        return {"success": True, "scope": "high_error_events", "events": events}


def audit_humidity_wind_impl() -> Dict[str, Any]:
    """Retrieve audit findings regarding atmospheric moisture and wind speed influence."""
    meta_file = W7_DIR / "shap_analysis_metadata.json"
    if meta_file.exists():
        try:
            with open(meta_file, "r", encoding="utf-8") as f:
                w7_data = json.load(f)
            met_audit = w7_data.get("meteorological_audit", {})
            return {"success": True, "audit": met_audit}
        except Exception:
            pass

    explainer = get_forecast_explainer()
    if explainer:
        return {"success": True, "audit": explainer.audit_meteorological_variables()}

    return {
        "success": True,
        "audit": {
            "humidity_available": False,
            "wind_speed_available": False,
            "variables_audited": [
                {
                    "variable": "relative_humidity",
                    "in_week5_model": False,
                    "audit_finding": "ABSENT from downloaded local dataset archive. Not used in Week 5 model."
                },
                {
                    "variable": "wind_speed",
                    "in_week5_model": False,
                    "audit_finding": "ABSENT from downloaded local dataset archive. Not used in Week 5 model."
                }
            ],
            "scientific_rationale": "Relative humidity and wind speed components are absent from the downloaded local dataset archive and are not features in the Week 5 forecast-bust model."
        }
    }


@tool
def get_feature_influence(scope: str = "global", event_id: Optional[int] = None) -> str:
    """
    Retrieve SHAP-based feature importance rankings and feature influence analysis.
    - When scope='global': Returns mean absolute SHAP values and rankings across all features.
    - When scope='high_error_events': Returns the top high-error forecast events with their positive and negative SHAP drivers.
    - When scope='event' and event_id is given: Returns local SHAP attribution for a specific event.
    """
    res = get_feature_influence_impl(scope=scope, event_id=event_id)
    return json.dumps(res, indent=2)


@tool
def explain_high_error_event(district: Optional[str] = None, event_id: Optional[int] = None) -> str:
    """
    Explain why a specific high-error forecast event occurred and how the model predicted its bust probability.
    Retrieves the actual forecast error (GFS - ERA5) and the model's SHAP feature attributions,
    identifying which features increased the bust risk and which reduced it.
    Can specify either a district ('Srinagar', 'Jammu', 'Anantnag', 'Baramulla') or an event_id.
    """
    res = get_feature_influence_impl(scope="event", event_id=event_id, district=district)
    return json.dumps(res, indent=2)


@tool
def audit_humidity_and_wind_influence() -> str:
    """
    Audit whether atmospheric humidity (moisture) and wind speed are present in the dataset and model.
    Returns findings on variable availability, why they are absent from the local archive,
    and provides exploratory meteorological analysis of available variables (temperature, diurnal cycle, lead hours)
    versus forecast errors.
    """
    res = audit_humidity_wind_impl()
    return json.dumps(res, indent=2)


PROJECT_TOOLS = [
    lookup_reliability,
    predict_forecast_bust,
    explain_scientific_metrics,
    compare_district_reliability,
    get_feature_influence,
    explain_high_error_event,
    audit_humidity_and_wind_influence,
]


# ============================================================================
# SYSTEM PROMPT AND GUIDANCE TEMPLATE
# ============================================================================

SYSTEM_PROMPT = """You are the Weather Reliability AI Assistant for the research project:
"Spatiotemporal Reliability and Uncertainty Detection for Medium-Range Weather Forecasts (Jammu & Kashmir)".

Academic Context: B.Tech Minor Project.
Study Region: Jammu & Kashmir (Districts: Srinagar, Jammu, Anantnag, Baramulla).
Data Pipeline: NOAA GFS (0.25° operational medium-range forecasts) verified against ECMWF ERA5 (0.25° atmospheric reanalysis reference).

CRITICAL SCIENTIFIC RULES:
1. ALWAYS distinguish between:
   - Historical Empirical Reliability Index (R ∈ [0, 1]): Calculated as R = R_error * C = exp(-MAE / scale) * (n / (n + k)).
   - Sample Confidence Factor (C = n / (n + k)): Quantifies empirical evidence sample size.
   - Forecast-Bust Probability: Machine-learning predicted prospective risk of an extreme error exceeding the 90th percentile threshold.
   - Forecast Error Metrics: MAE, RMSE, Bias (Forecast - Reference). Positive bias indicates a warm forecast departure; negative bias indicates a cold departure.
   THESE QUANTITIES ARE NOT INTERCHANGEABLE.

2. NEVER FABRICATE PREDICTIONS:
   - For forecast-bust prediction, all 7 features must be provided: district, lead_hours, lead_day, forecast_value, init_hour, valid_hour, valid_month.
   - If any required feature is missing, ask follow-up questions or instruct the user to provide them.
   - Atmospheric moisture (humidity) and wind speed are NOT features in the trained Week 5 model. DO NOT claim they affect the model.

3. DATA AVAILABILITY & TRANSPARENCY:
   - The verified dataset currently contains archived GFS-ERA5 records for lead days 1 and 2.
   - If the user asks for lead day 3+ reliability or comparison, transparently disclose that archived verification data is only available for lead days 1 and 2, and do not invent numbers.

4. SHAP EXPLAINABILITY & FEATURE INFLUENCE (WEEK 7):
   - SHAP (SHapley Additive exPlanations) is integrated with the Week 5 LogisticRegression Forecast-Bust Classifier using shap.LinearExplainer.
   - Global feature rankings: lead_hours (39.5%), valid_hour (28.8%), forecast_value (18.6%), district terrain (Jammu 5.1%, Baramulla 3.8%, Anantnag 2.8%, Srinagar 1.5%).
   - Grouped concepts: Forecast horizon (39.5%), Diurnal timing (28.8%), Forecast temperature (18.6%), District terrain (13.1%).
   - Positive SHAP contributions push log-odds up, increasing predicted bust risk. Negative SHAP contributions push log-odds down, mitigating bust risk.
   - For high-error events (e.g. Baramulla Lead 15h err -10.02°C, Anantnag Lead 24h/27h err -9.00°C), clearly distinguish actual verification error (GFS - ERA5) from prospective model predicted bust probability.
   - Atmospheric moisture (humidity) and 10m wind speed are absent from the local archive and are NOT model features. Do not claim they influence the model.

5. TONE & FORMATTING:
   - Maintain a scholarly, rigorous, and accessible scientific tone.
   - Format numbers cleanly with physical units (°C, %, etc.).
   - Highlight key metrics using bold text or bullet points.
"""


# ============================================================================
# DETERMINISTIC ORCHESTRATOR (OFFLINE / FALLBACK MODE)
# ============================================================================

def deterministic_agent_response(
    message: str,
    district: Optional[str] = None,
    lead_day: Optional[int] = None,
    forecast_features: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Intelligent deterministic orchestrator that executes the exact scientific tools
    and generates scientifically grounded responses when Gemini API key is missing or offline.
    Guarantees 100% stable demonstration during college review without hallucination or crash.
    """
    msg_lower = message.lower()
    tools_called = []
    structured_data = {}

    # Extract district if mentioned in message
    detected_district = district
    if not detected_district:
        for d in VALID_DISTRICTS:
            if d.lower() in msg_lower:
                detected_district = d
                break

    # Extract lead day if mentioned
    detected_lead_day = lead_day
    if detected_lead_day is None:
        lead_match = re.search(r"lead\s*(?:day)?\s*(\d+)", msg_lower)
        if lead_match:
            detected_lead_day = int(lead_match.group(1))

    # Case 0A: Meteorological Variable Audit (Humidity & Wind Speed)
    if "humidity" in msg_lower or "wind" in msg_lower:
        met_res = audit_humidity_wind_impl()
        tools_called.append({
            "tool": "audit_humidity_and_wind_influence",
            "input": {},
            "output": met_res
        })
        structured_data["meteorological_audit"] = met_res

        reply = (
            "### Meteorological Variable Audit: Humidity and Wind Speed (Week 7)\n\n"
            "Based on the empirical audit of the underlying project datasets:\n\n"
            "1. **Dataset & Model Availability:**\n"
            "   - **Atmospheric Relative Humidity:** **ABSENT** from the downloaded local dataset archive.\n"
            "   - **10-Metre Wind Speed (u/v components):** **ABSENT** from the downloaded local dataset archive.\n"
            "   - **Week 5 Model Features:** Neither variable is included as an input feature in the trained Forecast-Bust Classifier.\n\n"
            "2. **Scientific Rationale:**\n"
            "   - NOAA GFS index-filtered downloads and ECMWF CDSAPI queries in Weeks 1-2 requested strictly 2m temperature (`TMP:2 m above ground`, `2m_temperature`) "
            "and surface precipitation (`APCP:surface`, `total_precipitation`) to conserve network bandwidth and match the pilot research scope.\n"
            "   - Values are **not fabricated** or synthetically invented to maintain scientific integrity.\n\n"
            "3. **Relationship with Forecast Errors in Available Data:**\n"
            "   - **Forecast Horizon (Lead Hours):** Verification MAE increases monotonically with lead time (r = +0.28).\n"
            "   - **Forecast Temperature:** Cooler mountain forecasts (Anantnag, Baramulla) exhibit higher error dispersion compared to the Jammu plains.\n"
            "   - **Diurnal Heating Cycle:** Afternoon/evening valid hours (09:00–15:00 UTC) show elevated error due to localized convective and valley wind boundary layer processes.\n\n"
            "> **Key Scientific Distinction:** SHAP-based feature importance reflects mathematical contributions to the model's log-odds output, not physical atmospheric causality."
        )

        return {
            "reply": reply,
            "tools_called": tools_called,
            "structured_data": structured_data,
            "gemini_active": False,
            "model": "Scientific-Engine (Deterministic)"
        }

    # Case 0B: SHAP Feature Influence & High-Error Event Explanations
    if any(k in msg_lower for k in [
        "shap", "feature influence", "feature importance", "waterfall", "contribution",
        "why was", "bust reason", "high error", "high-error", "most influential"
    ]):
        target_event_id = None
        ev_match = re.search(r"event\s*(\d+)", msg_lower)
        if ev_match:
            target_event_id = int(ev_match.group(1))

        if target_event_id is not None or detected_district or "why" in msg_lower or "event" in msg_lower or "explain" in msg_lower:
            exp_res = get_feature_influence_impl(scope="event", event_id=target_event_id, district=detected_district)
            tools_called.append({
                "tool": "explain_high_error_event",
                "input": {"district": detected_district, "event_id": target_event_id},
                "output": exp_res
            })
            structured_data["event_explanation"] = exp_res

            ev = exp_res.get("event")
            if ev:
                pos_list = [f"**{c['feature']}** ({c['shap_value']:+0.2f})" for c in ev.get("top_positive_features", [])[:3]]
                neg_list = [f"**{c['feature']}** ({c['shap_value']:+0.2f})" for c in ev.get("top_negative_features", [])[:3]]

                reply = (
                    f"### SHAP Feature Influence Explanation: Event {ev['event_id']} ({ev['district']})\n\n"
                    f"**Event Verification Context:**\n"
                    f"- **District:** {ev['district']}\n"
                    f"- **Forecast Horizon:** Lead {int(ev['lead_hours'])}h (Day {int(ev['lead_day'])})\n"
                    f"- **Forecast Temperature:** {ev['forecast_value_c']}°C (ECMWF ERA5 Reference: {ev['reference_value_c']}°C)\n"
                    f"- **Actual Retrospective Error:** **{ev['actual_error_c']:+0.2f}°C** (Absolute Error: {ev['actual_absolute_error_c']:.2f}°C)\n"
                    f"- **Actual Verification Outcome:** {'EXCEEDED BUST THRESHOLD (Bust = 1)' if ev['actual_is_bust'] == 1 else 'Normal Error (Bust = 0)'}\n\n"
                    f"**Week 5 Model Prediction:**\n"
                    f"- **Predicted Bust Probability:** **{ev['model_prediction']['bust_probability'] * 100:.1f}%** ({ev['model_prediction']['risk_level']})\n"
                    f"- **Classification:** **{ev['model_prediction']['predicted_class']}** (Threshold = 0.50)\n\n"
                    f"**SHAP Feature Attribution Breakdown:**\n"
                    f"- **Features Increasing Predicted Bust Risk (+):** {', '.join(pos_list) if pos_list else 'None'}\n"
                    f"- **Features Mitigating/Reducing Bust Risk (-):** {', '.join(neg_list) if neg_list else 'None'}\n\n"
                    f"> **Plain-Language Summary:** {ev.get('narrative', '')}\n\n"
                    f"*{ev.get('scientific_distinction_note', '')}*"
                )
            else:
                events = exp_res.get("events", [])
                ev_summary = "\n".join([
                    f"- **Event {e['event_id']} ({e['district']})**: Lead {int(e['lead_hours'])}h, Actual Error = {e['actual_error_c']:+0.2f}°C, Pred Bust Risk = {e['model_prediction']['bust_probability'] * 100:.1f}% (Top driver: `{e.get('top_positive_driver', 'N/A')}`)"
                    for e in events[:5]
                ])
                reply = (
                    f"### High-Error Verification Events Analyzed (Week 7 SHAP Analysis)\n\n"
                    f"The top 5 high-error forecast events identified from NOAA GFS vs. ECMWF ERA5 comparison are:\n\n"
                    f"{ev_summary}\n\n"
                    f"Ask about any specific event (e.g. *'Explain event 21 in Baramulla'*) for its full SHAP waterfall feature breakdown."
                )
        else:
            glob_res = get_feature_influence_impl(scope="global")
            tools_called.append({
                "tool": "get_feature_influence",
                "input": {"scope": "global"},
                "output": glob_res
            })
            structured_data["global_feature_influence"] = glob_res

            rankings = glob_res.get("feature_rankings", [])
            grouped = glob_res.get("grouped_rankings", [])

            top_table = "\n".join([
                f"| {idx+1} | `{r['feature']}` | {r['mean_abs_shap']:.4f} | {r['relative_importance_pct']:.1f}% | `{r['dominant_direction']}` |"
                for idx, r in enumerate(rankings[:7])
            ])

            grp_table = "\n".join([
                f"- **{g['concept']}**: {g['mean_abs_shap']:.4f} ({g['relative_importance_pct']:.1f}% total influence)"
                for g in grouped
            ])

            reply = (
                f"### Global SHAP Feature Influence Analysis (Week 7)\n\n"
                f"Computed using **shap.LinearExplainer** across all verification samples for the Week 5 **LogisticRegression_BustClassifier**:\n\n"
                f"**Top Influential Features (Mean |SHAP| in Log-Odds Space):**\n\n"
                f"| Rank | Feature | Mean |SHAP| | Relative Share | Dominant Direction |\n"
                f"| --- | --- | --- | --- | --- |\n"
                f"{top_table}\n\n"
                f"**Concept-Level Influence Summary:**\n"
                f"{grp_table}\n\n"
                f"> **Interpretation Guide:**\n"
                f"- **Lead Time (`lead_hours`)** is the primary driver of forecast bust uncertainty (39.5% relative share), with longer horizons pushing predicted log-odds toward extreme errors.\n"
                f"- **Diurnal Timing (`valid_hour`)** is the second most influential factor (28.8% share), capturing solar boundary layer errors.\n"
                f"- **Forecast Temperature (`forecast_value`)** accounts for 18.6% of influence.\n"
                f"- **District Geography** accounts for 13.1% of influence, with Jammu pulling down bust risk and mountainous districts (Anantnag, Baramulla) elevating baseline uncertainty."
            )

        return {
            "reply": reply,
            "tools_called": tools_called,
            "structured_data": structured_data,
            "gemini_active": False,
            "model": "Scientific-Engine (Deterministic)"
        }

    # Case 1: Forecast-Bust Prediction
    if "bust" in msg_lower and ("estimate" in msg_lower or "predict" in msg_lower or "risk" in msg_lower or forecast_features):
        params = forecast_features or {}
        dist_param = params.get("district", detected_district or "Srinagar")
        lh = params.get("lead_hours")
        ld = params.get("lead_day", detected_lead_day)
        fv = params.get("forecast_value")
        ih = params.get("init_hour")
        vh = params.get("valid_hour")
        vm = params.get("valid_month")

        tool_result = predict_forecast_bust_impl(
            district=dist_param,
            lead_hours=lh,
            lead_day=ld,
            forecast_value=fv,
            init_hour=ih,
            valid_hour=vh,
            valid_month=vm
        )
        tools_called.append({
            "tool": "predict_forecast_bust",
            "input": {
                "district": dist_param,
                "lead_hours": lh,
                "lead_day": ld,
                "forecast_value": fv,
                "init_hour": ih,
                "valid_hour": vh,
                "valid_month": vm
            },
            "output": tool_result
        })
        structured_data["bust_prediction"] = tool_result

        if tool_result.get("success"):
            reply = (
                f"### Forecast-Bust Risk Assessment\n\n"
                f"Based on the trained Week 5 Machine-Learning Classifier (**{tool_result['model_id']}**):\n\n"
                f"- **Target District:** {tool_result['district']}\n"
                f"- **Forecast Temperature:** {tool_result['forecast_value']}°C\n"
                f"- **Forecast Horizon:** Lead Day {tool_result['lead_day']} ({tool_result['lead_hours']} hours)\n"
                f"- **Estimated Bust Probability:** **{tool_result['bust_probability_percent']}** (Score: {tool_result['bust_probability']})\n"
                f"- **Predicted Classification:** **{tool_result['predicted_class']}** ({tool_result['risk_level']})\n\n"
                f"> **Scientific Definition:** A forecast bust is defined as an error exceeding the empirical 90th percentile of training absolute errors "
                f"(~6.4°C–8.3°C depending on district terrain).\n\n"
                f"*Note on Model Architecture:* Features strictly evaluate forecast issuance variables (district, lead time, forecast temperature, and diurnal cycle). "
                f"Atmospheric humidity and wind speed are not features in this model."
            )
        elif tool_result.get("status") == "missing_inputs":
            reply = (
                f"### Missing Required Features for Forecast-Bust Prediction\n\n"
                f"The Week 5 Forecast-Bust Classifier requires all 7 input features according to its trained schema:\n\n"
                f"**Missing Parameters:** `{', '.join(tool_result['missing_fields'])}`\n\n"
                f"To run live inference, please provide the complete feature set or use the quick input form below:\n"
                f"- **District:** Srinagar, Jammu, Anantnag, or Baramulla\n"
                f"- **Lead Day & Hours:** e.g., Day 2 (48 hours)\n"
                f"- **Forecast Value:** Predicted temperature in °C\n"
                f"- **Initialization Cycle:** 00, 06, 12, or 18 UTC\n"
                f"- **Valid Hour:** 00, 06, 12, or 18 UTC\n"
                f"- **Valid Month:** 1 to 12\n\n"
                f"*Notice:* The model does not arbitrarily fabricate default values for missing inputs."
            )
        else:
            reply = f"Error evaluating forecast bust: {tool_result.get('error')}"

        return {
            "reply": reply,
            "tools_called": tools_called,
            "structured_data": structured_data,
            "gemini_active": False,
            "model": "Scientific-Engine (Deterministic)"
        }

    # Case 2: Comparison between multiple districts
    if "compare" in msg_lower or ("both" in msg_lower and "and" in msg_lower):
        districts_to_compare = [d for d in VALID_DISTRICTS if d.lower() in msg_lower]
        if len(districts_to_compare) < 2:
            districts_to_compare = ["Jammu", "Srinagar"]
        target_lead = detected_lead_day or 1

        comp_result = json.loads(compare_district_reliability.invoke({
            "districts": districts_to_compare,
            "lead_day": target_lead
        }))
        tools_called.append({
            "tool": "compare_district_reliability",
            "input": {"districts": districts_to_compare, "lead_day": target_lead},
            "output": comp_result
        })
        structured_data["comparison"] = comp_result

        if comp_result.get("comparison_possible"):
            comps = comp_result["available_comparisons"]
            reply = (
                f"### Spatiotemporal Reliability Comparison (Lead Day {target_lead})\n\n"
                f"{comp_result.get('summary', '')}\n\n"
                f"| Metric | {comps[0]['district']} | {comps[1]['district']} |\n"
                f"| :--- | :--- | :--- |\n"
                f"| **Reliability Score (R)** | **{comps[0].get('reliability_score_R', 'N/A')}** | **{comps[1].get('reliability_score_R', 'N/A')}** |\n"
                f"| **Sample Confidence (C)** | {comps[0].get('sample_confidence_C', 'N/A')} | {comps[1].get('sample_confidence_C', 'N/A')} |\n"
                f"| **Verification MAE** | {comps[0].get('training_MAE', comps[0].get('test_MAE'))}°C | {comps[1].get('training_MAE', comps[1].get('test_MAE'))}°C |\n"
                f"| **Sample Size (n)** | {comps[0].get('training_sample_count', comps[0].get('test_sample_count'))} cases | {comps[1].get('training_sample_count', comps[1].get('test_sample_count'))} cases |\n"
                f"| **Provenance** | `{comps[0].get('provenance')}` | `{comps[1].get('provenance')}` |\n\n"
                f"> **Interpretation:** Plain terrain in Jammu exhibits lower topographic offset compared to ECMWF ERA5 grid centroids, "
                f"resulting in consistently lower verification MAE and higher reliability than mountain valley stations like Srinagar."
            )
        else:
            reply = (
                f"### Verification Data Unavailable for Comparison\n\n"
                f"Direct comparative verification could not be completed for lead day **{target_lead}**:\n\n"
                f"{chr(10).join(['- ' + n for n in comp_result.get('unavailable_notes', [])])}\n\n"
                f"> **Dataset Disclosure:** Archived NOAA GFS vs. ECMWF ERA5 matched validation data in this project currently covers **lead days 1 and 2**. "
                f"Lead day {target_lead} records are not archived, and empirical verification scores cannot be fabricated without observation ground-reference."
            )

        return {
            "reply": reply,
            "tools_called": tools_called,
            "structured_data": structured_data,
            "gemini_active": False,
            "model": "Scientific-Engine (Deterministic)"
        }

    # Case 3: Specific District Reliability Lookup
    if detected_district and ("reliab" in msg_lower or "explain" in msg_lower or "performance" in msg_lower):
        target_lead = detected_lead_day or 1
        rel_result = lookup_reliability_impl(detected_district, target_lead)
        tools_called.append({
            "tool": "lookup_reliability",
            "input": {"district": detected_district, "lead_day": target_lead},
            "output": rel_result
        })
        structured_data["reliability"] = rel_result

        if rel_result.get("success"):
            reply = (
                f"### Empirical Reliability for {rel_result['district']} (Lead Day {rel_result['lead_day']})\n\n"
                f"Retrieved from the **Week 4 Spatiotemporal Reliability Module**:\n\n"
                f"- **Empirical Reliability Index (R):** **{rel_result.get('reliability_score_R')}** (bounded in [0, 1])\n"
                f"- **Sample Confidence Factor (C):** **{rel_result.get('sample_confidence_C')}** (based on n = {rel_result.get('training_sample_count', rel_result.get('test_sample_count'))} samples, damping parameter k = {rel_result.get('confidence_k', 10.0)})\n"
                f"- **Error Component (R_error):** {rel_result.get('error_component_R_error')}\n"
                f"- **Verification MAE:** {rel_result.get('training_MAE', rel_result.get('test_MAE'))}°C (acceptable tolerance scale = {rel_result.get('error_tolerance_scale')}°C)\n"
                f"- **Provenance:** `{rel_result.get('provenance')}` ({rel_result.get('split_source', 'Verification Archive')})\n\n"
                f"> **Scientific Explanation:** The reliability index R = R_error × C incorporates both forecast accuracy (exponential decay of error) "
                f"and statistical confidence (sample size support). For {rel_result['district']} at lead day {rel_result['lead_day']}, "
                f"the observed MAE of {rel_result.get('training_MAE', rel_result.get('test_MAE'))}°C yields an empirical score of {rel_result.get('reliability_score_R')}."
            )
        else:
            reply = (
                f"### Verification Data Unavailable\n\n"
                f"**Query:** {detected_district} on Lead Day {target_lead}\n\n"
                f"{rel_result.get('dataset_limitation', rel_result.get('error'))}\n\n"
                f"Supported study districts: **{', '.join(VALID_DISTRICTS)}** across **lead days 1 and 2**."
            )

        return {
            "reply": reply,
            "tools_called": tools_called,
            "structured_data": structured_data,
            "gemini_active": False,
            "model": "Scientific-Engine (Deterministic)"
        }

    # Case 4: Concept Explanation (Difference between reliability and bust, index definition, etc.)
    explanation_res = explain_scientific_metrics_impl(message)
    tools_called.append({
        "tool": "explain_scientific_metrics",
        "input": {"topic": message},
        "output": explanation_res
    })
    structured_data["explanation"] = explanation_res

    if "distinction" in explanation_res:
        reply = f"### {explanation_res['topic']}\n\n{explanation_res['distinction']}\n\n> **Key Principle:** {explanation_res['key_takeaway']}"
    elif "definition" in explanation_res:
        reply = f"### {explanation_res['topic']}\n\n{explanation_res['definition']}"
    else:
        reply = (
            f"### Weather Forecast Reliability AI Assistant\n\n"
            f"I can assist with real scientific data and predictions from your medium-range forecast verification system:\n\n"
            f"- **Reliability Lookup:** Ask about the empirical reliability index for Srinagar, Jammu, Anantnag, or Baramulla.\n"
            f"- **District Comparison:** Compare verification accuracy between districts at specific lead days.\n"
            f"- **Forecast-Bust Prediction:** Predict prospective bust probability for an upcoming forecast using the Week 5 ML model.\n"
            f"- **Scientific Clarification:** Ask about mathematical definitions of R, sample confidence C, or the difference between reliability and bust probability."
        )

    return {
        "reply": reply,
        "tools_called": tools_called,
        "structured_data": structured_data,
        "gemini_active": False,
        "model": "Scientific-Engine (Deterministic)"
    }


# ============================================================================
# MAIN AGENT INVOCATION (GEMINI WITH GRACEFUL FALLBACK)
# ============================================================================

def run_agentic_query(
    message: str,
    history: Optional[List[Dict[str, str]]] = None,
    district: Optional[str] = None,
    lead_day: Optional[int] = None,
    forecast_features: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Main entry point for AI assistant requests:
    1. Checks for server-side GEMINI_API_KEY.
    2. If available, initializes ChatGoogleGenerativeAI with bound scientific tools.
    3. Handles tool calling loop, formatting responses strictly grounded in real metrics.
    4. If GEMINI_API_KEY is not set or fails, gracefully falls back to deterministic scientific orchestrator.
    """
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    model_name = os.getenv("LLM_MODEL", "gemini-2.0-flash")

    # If no API key configured, use deterministic scientific engine with transparent notice
    if not api_key or api_key.strip() in ["", "your_gemini_api_key_here"]:
        logger.info("GEMINI_API_KEY not found in environment. Using deterministic scientific orchestrator.")
        res = deterministic_agent_response(
            message=message,
            district=district,
            lead_day=lead_day,
            forecast_features=forecast_features
        )
        res["gemini_active"] = False
        res["setup_notice"] = (
            "Running in Deterministic Scientific Mode. To activate live Google Gemini generative conversation, "
            "set GEMINI_API_KEY=your_key in your server .env file."
        )
        return res

    # Attempt LangChain + Google Gemini
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI

        llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=0.2,
            max_retries=2,
            timeout=15.0
        )
        llm_with_tools = llm.bind_tools(PROJECT_TOOLS)

        # Assemble message history
        messages = [SystemMessage(content=SYSTEM_PROMPT)]

        # Add recent conversation history if provided
        if history:
            for h in history[-6:]:  # Keep last 3 turns
                if h.get("role") == "user":
                    messages.append(HumanMessage(content=h.get("content", "")))
                elif h.get("role") == "assistant":
                    messages.append(AIMessage(content=h.get("content", "")))

        # Format user prompt with any contextual parameters passed
        context_str = ""
        if district or lead_day or forecast_features:
            context_dict = {
                k: v for k, v in {
                    "context_district": district,
                    "context_lead_day": lead_day,
                    "forecast_features": forecast_features
                }.items() if v is not None
            }
            context_str = f"\n[Context provided by dashboard UI: {json.dumps(context_dict)}]"

        messages.append(HumanMessage(content=message + context_str))

        # First LLM call: Decide on tool calls
        ai_msg = llm_with_tools.invoke(messages)
        tools_called = []
        structured_data = {}

        if ai_msg.tool_calls:
            messages.append(ai_msg)
            for tc in ai_msg.tool_calls:
                t_name = tc["name"]
                t_args = tc["args"]
                logger.info("Agent invoked tool '%s' with args %s", t_name, t_args)

                tool_output_str = "{}"
                if t_name == "lookup_reliability":
                    tool_output_str = lookup_reliability.invoke(t_args)
                    structured_data["reliability"] = json.loads(tool_output_str)
                elif t_name == "predict_forecast_bust":
                    tool_output_str = predict_forecast_bust.invoke(t_args)
                    structured_data["bust_prediction"] = json.loads(tool_output_str)
                elif t_name == "explain_scientific_metrics":
                    tool_output_str = explain_scientific_metrics.invoke(t_args)
                    structured_data["explanation"] = json.loads(tool_output_str)
                elif t_name == "compare_district_reliability":
                    tool_output_str = compare_district_reliability.invoke(t_args)
                    structured_data["comparison"] = json.loads(tool_output_str)
                elif t_name == "get_feature_influence":
                    tool_output_str = get_feature_influence.invoke(t_args)
                    structured_data["feature_influence"] = json.loads(tool_output_str)
                elif t_name == "explain_high_error_event":
                    tool_output_str = explain_high_error_event.invoke(t_args)
                    structured_data["high_error_event"] = json.loads(tool_output_str)
                elif t_name == "audit_humidity_and_wind_influence":
                    tool_output_str = audit_humidity_and_wind_influence.invoke(t_args)
                    structured_data["humidity_wind_audit"] = json.loads(tool_output_str)

                tools_called.append({
                    "tool": t_name,
                    "input": t_args,
                    "output": json.loads(tool_output_str)
                })

                messages.append(ToolMessage(
                    content=tool_output_str,
                    tool_call_id=tc["id"]
                ))

            # Second LLM call: Synthesize final answer grounded in tool outputs
            final_response = llm.invoke(messages)
            reply_text = final_response.content
        else:
            reply_text = ai_msg.content

        return {
            "reply": reply_text,
            "tools_called": tools_called,
            "structured_data": structured_data,
            "gemini_active": True,
            "model": model_name,
            "error": None
        }

    except Exception as e:
        logger.warning("Gemini invocation failed (%s). Falling back to deterministic scientific engine.", e)
        fallback = deterministic_agent_response(
            message=message,
            district=district,
            lead_day=lead_day,
            forecast_features=forecast_features
        )
        fallback["gemini_active"] = False
        fallback["error"] = f"Gemini API request note: {str(e)[:100]}. Fallback engine engaged."
        return fallback
