"""
Unit, Integration, and End-to-End Tests for Week 9: System Integration, Pipeline Orchestration & Cloud Readiness.

Verifies:
1. End-to-End Data-to-Alert Execution Workflow:
   Raw/Processed Data -> Error Analysis -> Reliability Calculation ->
   Bust Prediction -> SHAP Explanation -> Alert Threshold Evaluation ->
   Persistent Alert Storage -> Regional GeoJSON Map Representation.
2. Operational Health Check (/api/health) verifying all Weeks 1-9 artifacts.
3. Pipeline Stage Execution (--stage week8, --stage week9).
4. Containerization & Deployment Configuration (Dockerfile, frontend/Dockerfile, docker-compose.yml, .env.example).
"""

import os
import json
import subprocess
from pathlib import Path
import pytest
import pandas as pd
from fastapi.testclient import TestClient

from src.api import app
from src.run_pipeline import ensure_directories, load_config
from src.forecast_bust import ForecastBustPredictor
from src.explainability import ForecastBustExplainer
from src.alerting import ForecastBustAlertEngine, AlertStorageManager


@pytest.fixture
def test_client():
    return TestClient(app)


class TestWeek9HealthAndEnvironment:
    """Test API health check and multi-week artifact integrity."""

    def test_health_check_endpoint(self, test_client):
        res = test_client.get("/api/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "operational"
        assert "Weeks 1-9" in data["service"]
        assert "artifacts" in data
        artifacts = data["artifacts"]

        # All key artifacts across Weeks 4, 5, 7, 8 must be present
        assert artifacts["week4_reliability_table"] is True
        assert artifacts["week5_model_pipeline"] is True
        assert artifacts["week7_shap_metadata"] is True
        assert artifacts["week8_alerts_store"] is True
        assert artifacts["week8_regional_geojson"] is True
        assert artifacts["week8_lead_day_uncertainty"] is True


class TestEndToEndDataToAlertWorkflow:
    """
    Test the complete 8-stage data-to-alert operational workflow:
    Input Forecast -> Error Metric -> Reliability Score -> ML Prediction ->
    SHAP Attribution -> Threshold Evaluation -> Persistent Alert -> Regional GeoJSON.
    """

    def test_complete_data_to_alert_lifecycle(self):
        # 1. Verify matched dataset from Week 3
        matched_path = Path("outputs/week3/matched_validation_dataset.csv")
        assert matched_path.exists(), "Week 3 matched validation dataset missing."
        matched_df = pd.read_csv(matched_path)
        assert len(matched_df) > 0

        # 2. Verify Week 4 reliability table
        rel_path = Path("outputs/week4/reliability_table.csv")
        assert rel_path.exists(), "Week 4 reliability table missing."
        rel_df = pd.read_csv(rel_path)
        assert "reliability_score_R" in rel_df.columns

        # 3. Load Week 5 ML Model Pipeline & Predict
        model_path = Path("outputs/week5/trained_model_pipeline.joblib")
        meta_path = Path("outputs/week5/model_metadata.json")
        assert model_path.exists() and meta_path.exists()
        predictor = ForecastBustPredictor(str(model_path), str(meta_path))

        test_input = pd.DataFrame([{
            "district": "Baramulla",
            "lead_hours": 120.0,
            "lead_day": 5.0,
            "forecast_value": 12.35,
            "init_hour": 0.0,
            "valid_hour": 12.0,
            "valid_month": 9.0
        }])
        pred_res = predictor.predict(test_input)
        assert len(pred_res) == 1
        bust_prob = float(pred_res.iloc[0]["bust_probability"])
        assert 0.0 <= bust_prob <= 1.0

        # 4. Compute SHAP Explanation
        explainer = ForecastBustExplainer(str(model_path), str(meta_path))
        explanation = explainer.explain_instance({
            "district": "Baramulla",
            "lead_hours": 120.0,
            "lead_day": 5.0,
            "forecast_value": 12.35,
            "init_hour": 0.0,
            "valid_hour": 12.0,
            "valid_month": 9.0
        })
        assert "shap_summary" in explanation
        assert len(explanation["all_feature_contributions"]) == 10

        # 5. Evaluate Alert Threshold
        engine = ForecastBustAlertEngine()
        alerts = engine.evaluate_forecasts(pred_res, custom_threshold=0.50)
        assert len(alerts) >= 1
        generated_alert = alerts[0]
        assert generated_alert["district"] == "Baramulla"
        assert generated_alert["leadDay"] == 5

        # 6. Verify Persistent Storage
        storage = AlertStorageManager()
        stored_alerts = storage.load_alerts()
        assert any(a["id"] == generated_alert["id"] for a in stored_alerts)

        # 7. Verify Regional GeoJSON
        geojson_path = Path("outputs/week8/regional_reliability_geojson.json")
        assert geojson_path.exists()
        with open(geojson_path, "r", encoding="utf-8") as f:
            geojson = json.load(f)
        assert geojson["type"] == "FeatureCollection"
        baramulla_prop = next(f["properties"] for f in geojson["features"] if f["properties"]["district"] == "Baramulla")
        assert "day1_reliability" in baramulla_prop


class TestPipelineOrchestrationStages:
    """Test run_pipeline.py stage selection and directory creation."""

    def test_ensure_directories(self):
        cfg = load_config()
        ensure_directories(cfg)
        for dir_key in ["week3", "week4", "week5", "week7", "week8", "week9"]:
            d_path = Path(cfg["output_dirs"].get(dir_key, f"outputs/{dir_key}"))
            assert d_path.exists()

    def test_pipeline_week9_stage_cli(self):
        cmd = ["./.venv/bin/python", "src/run_pipeline.py", "--stage", "week9"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        assert res.returncode == 0
        assert "All pipeline artifacts verified intact" in res.stdout


class TestDockerAndDeploymentConfiguration:
    """Verify Dockerfiles and Compose manifests syntax and structure."""

    def test_backend_dockerfile_structure(self):
        dockerfile = Path("Dockerfile")
        assert dockerfile.exists()
        content = dockerfile.read_text(encoding="utf-8")
        assert "FROM python:3.11-slim" in content
        assert "WORKDIR /app" in content
        assert "HEALTHCHECK" in content
        assert "uvicorn" in content

    def test_frontend_dockerfile_structure(self):
        f_dockerfile = Path("frontend/Dockerfile")
        assert f_dockerfile.exists()
        content = f_dockerfile.read_text(encoding="utf-8")
        assert "FROM node:20-alpine AS builder" in content
        assert "FROM nginx:alpine" in content
        assert "COPY --from=builder /app/dist /usr/share/nginx/html" in content

    def test_docker_compose_manifest(self):
        compose_file = Path("docker-compose.yml")
        assert compose_file.exists()
        content = compose_file.read_text(encoding="utf-8")
        assert "services:" in content
        assert "backend:" in content
        assert "frontend:" in content
        assert "./outputs:/app/outputs" in content
        assert "8000:8000" in content

    def test_env_example_documentation(self):
        env_ex = Path(".env.example")
        assert env_ex.exists()
        content = env_ex.read_text(encoding="utf-8")
        assert "ALERT_THRESHOLD" in content
        assert "GEMINI_API_KEY" in content
        assert "API_PORT" in content
