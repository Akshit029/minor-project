"""
FastAPI Server for Weather Forecast Reliability and Week 6 Agentic AI Integration.

Provides:
- POST /api/chat: Invokes LangChain Agent with Google Gemini / deterministic fallback.
- POST /api/bust-predict: Live Week 5 machine-learning inference for forecast busts.
- GET /api/reliability-lookup: Direct Week 4 spatiotemporal reliability parameter query.
- GET /api/health: Operational health and environment status.
"""

import os
import sys
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator
from dotenv import load_dotenv

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv()

from src.agentic_ai import (
    run_agentic_query,
    lookup_reliability_impl,
    predict_forecast_bust_impl,
    get_forecast_explainer,
    get_feature_influence_impl,
    audit_humidity_wind_impl,
    VALID_DISTRICTS
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("api")

app = FastAPI(
    title="Weather Reliability & Uncertainty AI API",
    description="Backend API hosting Week 6 Agentic AI and Weeks 1-5 Scientific Modules for Jammu & Kashmir Medium-Range Weather Forecasts.",
    version="1.0.0"
)

# Enable CORS for frontend development and production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (e.g. http://localhost:5173)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Maximum request body size guard (1 MB)
MAX_REQUEST_SIZE = 1024 * 1024


@app.middleware("http")
async def limit_request_size_and_catch_errors(request: Request, call_next):
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > MAX_REQUEST_SIZE:
        return JSONResponse(
            status_code=413,
            content={"error": "Request body exceeds maximum size limit (1 MB)."}
        )
    try:
        response = await call_next(request)
        return response
    except Exception as exc:
        logger.error("Unhandled server exception: %s", exc, exc_info=True)
        # Safe error masking to prevent stack traces or internal secrets leaking
        return JSONResponse(
            status_code=500,
            content={"error": "An internal server error occurred while processing the request."}
        )


# ============================================================================
# PYDANTIC SCHEMAS
# ============================================================================

class ChatHistoryItem(BaseModel):
    role: str = Field(..., description="'user' or 'assistant'")
    content: str = Field(..., max_length=5000)


class ForecastFeaturesInput(BaseModel):
    district: Optional[str] = None
    lead_hours: Optional[float] = None
    lead_day: Optional[float] = None
    forecast_value: Optional[float] = None
    init_hour: Optional[float] = None
    valid_hour: Optional[float] = None
    valid_month: Optional[float] = None


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, description="User's query")
    history: Optional[List[ChatHistoryItem]] = Field(default=None, description="Recent conversation history")
    district: Optional[str] = Field(default=None, description="Optional target district")
    lead_day: Optional[int] = Field(default=None, description="Optional forecast lead day")
    forecast_features: Optional[ForecastFeaturesInput] = Field(default=None, description="Optional forecast features")

    @field_validator("message")
    @classmethod
    def message_not_empty(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Message cannot be empty or whitespace only.")
        return stripped


class BustPredictRequest(BaseModel):
    district: str = Field(..., description="Target study district (Srinagar, Jammu, Anantnag, Baramulla)")
    leadDay: int = Field(..., ge=1, le=10, description="Lead day (1 to 10)")
    forecastValue: float = Field(..., description="Forecast temperature in Celsius")
    initHour: int = Field(default=0, ge=0, le=23, description="Initialization cycle hour (0, 6, 12, 18)")
    validHour: int = Field(default=12, ge=0, le=23, description="Forecast target valid hour (0, 6, 12, 18)")
    validMonth: int = Field(default=10, ge=1, le=12, description="Target calendar month")


class LocalExplanationRequest(BaseModel):
    district: str = Field(..., description="Target study district (Srinagar, Jammu, Anantnag, Baramulla)")
    leadDay: int = Field(..., ge=1, le=10, description="Lead day (1 to 10)")
    forecastValue: float = Field(..., description="Forecast temperature in Celsius")
    initHour: int = Field(default=0, ge=0, le=23, description="Initialization cycle hour (0, 6, 12, 18)")
    validHour: int = Field(default=12, ge=0, le=23, description="Forecast target valid hour (0, 6, 12, 18)")
    validMonth: int = Field(default=9, ge=1, le=12, description="Target calendar month")


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/api/health")
async def health_check():
    """Operational health check returning model and environment status."""
    has_gemini = bool(os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))
    w4_table = PROJECT_ROOT / "outputs" / "week4" / "reliability_table.csv"
    w5_model = PROJECT_ROOT / "outputs" / "week5" / "trained_model_pipeline.joblib"
    w7_meta = PROJECT_ROOT / "outputs" / "week7" / "shap_analysis_metadata.json"

    return {
        "status": "operational",
        "service": "Weather Reliability AI Service (Weeks 1-7)",
        "gemini_api_key_configured": has_gemini,
        "configured_model": os.getenv("LLM_MODEL", "gemini-2.0-flash"),
        "artifacts": {
            "week4_reliability_table": w4_table.exists(),
            "week5_model_pipeline": w5_model.exists(),
            "week7_shap_metadata": w7_meta.exists()
        },
        "supported_districts": VALID_DISTRICTS
    }


@app.post("/api/chat")
async def chat_endpoint(payload: ChatRequest):
    """
    Main AI Assistant conversational endpoint.
    Orchestrates scientific tools using LangChain and Google Gemini,
    with automatic deterministic fallback when API keys are absent.
    """
    history_list = None
    if payload.history:
        history_list = [{"role": h.role, "content": h.content} for h in payload.history]

    feat_dict = None
    if payload.forecast_features:
        feat_dict = payload.forecast_features.model_dump(exclude_none=True)

    try:
        response = run_agentic_query(
            message=payload.message,
            history=history_list,
            district=payload.district,
            lead_day=payload.lead_day,
            forecast_features=feat_dict
        )
        return response
    except Exception as e:
        logger.error("Chat endpoint processing error: %s", e)
        raise HTTPException(
            status_code=500,
            detail="Error generating assistant response."
        )


@app.post("/api/bust-predict")
async def predict_bust_endpoint(payload: BustPredictRequest):
    """
    Production machine-learning forecast-bust inference endpoint.
    Directly compatible with frontend WeatherApi.predictBust interface.
    """
    res = predict_forecast_bust_impl(
        district=payload.district,
        lead_hours=payload.leadDay * 24.0,
        lead_day=float(payload.leadDay),
        forecast_value=payload.forecastValue,
        init_hour=float(payload.initHour),
        valid_hour=float(payload.validHour),
        valid_month=float(payload.validMonth)
    )

    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("error", "Prediction failed."))

    # Return format matching ForecastBustPredictionResult interface in frontend
    return {
        "district": res["district"],
        "leadHours": int(res["lead_hours"]),
        "leadDay": int(res["lead_day"]),
        "forecastValue": res["forecast_value"],
        "initHour": int(res["init_hour"]),
        "validHour": int(res["valid_hour"]),
        "validMonth": int(res["valid_month"]),
        "bustProbability": int(round(res["bust_probability"] * 100)),
        "predictedClass": res["predicted_class"],
        "riskLevel": res["risk_level"],
        "modelUsed": res["model_id"],
        "computedTimestamp": res.get("note", "Week 5 Inference Pipeline")
    }


@app.get("/api/reliability-lookup")
async def reliability_lookup_endpoint(
    district: str = Query(..., description="Target district"),
    lead_day: int = Query(..., ge=1, le=10, description="Lead day (1 to 10)")
):
    """Direct query endpoint for Week 4 spatiotemporal reliability score."""
    res = lookup_reliability_impl(district, lead_day)
    return res


# ============================================================================
# WEEK 7 EXPLAINABILITY ENDPOINTS
# ============================================================================

@app.get("/api/explainability/global")
async def explainability_global_endpoint():
    """Retrieve global SHAP feature importance rankings and concept summaries."""
    res = get_feature_influence_impl(scope="global")
    if not res.get("success"):
        raise HTTPException(status_code=500, detail=res.get("error", "Failed to retrieve global SHAP analysis."))
    return res


@app.get("/api/explainability/events")
async def explainability_events_endpoint(
    district: Optional[str] = Query(None, description="Optional district filter"),
    event_id: Optional[int] = Query(None, description="Optional event ID")
):
    """Retrieve high-error forecast events with their actual error and local SHAP attributions."""
    res = get_feature_influence_impl(scope="event", event_id=event_id, district=district)
    if not res.get("success"):
        raise HTTPException(status_code=500, detail=res.get("error", "Failed to retrieve high-error events."))
    return res


@app.post("/api/explainability/local")
async def explainability_local_endpoint(payload: LocalExplanationRequest):
    """Compute on-the-fly local SHAP explanation for an incoming forecast."""
    explainer = get_forecast_explainer()
    if explainer is None:
        raise HTTPException(status_code=503, detail="SHAP Explainer is not initialized or model artifact is missing.")

    try:
        explanation = explainer.explain_instance({
            "district": payload.district,
            "lead_hours": payload.leadDay * 24.0,
            "lead_day": float(payload.leadDay),
            "forecast_value": payload.forecastValue,
            "init_hour": float(payload.initHour),
            "valid_hour": float(payload.validHour),
            "valid_month": float(payload.validMonth)
        })
        return {
            "success": True,
            "district": payload.district,
            "leadDay": payload.leadDay,
            "forecastValue": payload.forecastValue,
            "prediction": explanation["prediction"],
            "shapSummary": explanation["shap_summary"],
            "featuresIncreasingRisk": explanation["features_increasing_risk"],
            "featuresDecreasingRisk": explanation["features_decreasing_risk"],
            "allFeatureContributions": explanation["all_feature_contributions"],
            "narrativeExplanation": explanation["narrative_explanation"]
        }
    except Exception as e:
        logger.error("Error computing local SHAP explanation: %s", e)
        raise HTTPException(status_code=400, detail=f"Local explanation computation failed: {str(e)}")


@app.get("/api/explainability/meteorological")
async def explainability_meteorological_endpoint():
    """Retrieve meteorological variable audit and exploratory analysis findings."""
    res = audit_humidity_wind_impl()
    return res


if __name__ == "__main__":
    import uvicorn
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    logger.info("Starting Weather Reliability AI API server on %s:%d...", host, port)
    uvicorn.run("src.api:app", host=host, port=port, reload=True)
