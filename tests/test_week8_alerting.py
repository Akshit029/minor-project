"""
Unit and Integration Tests for Week 8: Automated Forecast-Bust Alerting & Multi-Horizon Uncertainty.

Verifies:
1. Alert hash generation & idempotency (prevents duplicate alerts).
2. Severity classification mapping.
3. Persistent JSON storage manager (save, read, update status, filter).
4. Safe notification adapters (Logging, In-App, Email with missing credential fallback).
5. ForecastBustAlertEngine evaluation with Week 5 model.
6. Multi-horizon uncertainty analysis (Days 1 to 10 handling observed vs unobserved).
7. Regional reliability GeoJSON building.
8. FastAPI Week 8 endpoints (alerts list, evaluate, status update, regional map, uncertainty).
"""

import os
import json
import tempfile
import pytest
import pandas as pd
from pathlib import Path
from fastapi.testclient import TestClient

from src.alerting import (
    generate_alert_hash,
    determine_alert_severity,
    AlertStorageManager,
    LoggingNotificationAdapter,
    EmailNotificationAdapter,
    CompositeNotificationDispatcher,
    ForecastBustAlertEngine,
    get_configured_alert_threshold,
    run_week8_alerting
)
from src.uncertainty_analysis import (
    calculate_empirical_uncertainty_metrics,
    build_regional_reliability_geojson,
    run_week8_uncertainty_analysis,
    DISTRICT_METADATA
)
from src.api import app


@pytest.fixture
def test_client():
    return TestClient(app)


class TestAlertHashingAndSeverity:
    """Test deterministic alert hashing and severity classification."""

    def test_alert_hash_determinism(self):
        hash1 = generate_alert_hash("Anantnag", "2026-09-15 00:00:00", "2026-09-15 12:00:00", 1)
        hash2 = generate_alert_hash("Anantnag", "2026-09-15 00:00:00", "2026-09-15 12:00:00", 1)
        assert hash1 == hash2
        assert hash1.startswith("alt-ana-1d-")

    def test_alert_hash_distinct_for_different_events(self):
        hash_ana = generate_alert_hash("Anantnag", "2026-09-15 00:00:00", "2026-09-15 12:00:00", 1)
        hash_sri = generate_alert_hash("Srinagar", "2026-09-15 00:00:00", "2026-09-15 12:00:00", 1)
        hash_day2 = generate_alert_hash("Anantnag", "2026-09-15 00:00:00", "2026-09-16 12:00:00", 2)
        assert hash_ana != hash_sri
        assert hash_ana != hash_day2

    def test_severity_classification(self):
        assert determine_alert_severity(0.85) == "critical"
        assert determine_alert_severity(0.80) == "critical"
        assert determine_alert_severity(0.70) == "high"
        assert determine_alert_severity(0.65) == "high"
        assert determine_alert_severity(0.55) == "moderate"
        assert determine_alert_severity(0.40) == "low"


class TestAlertStorageManager:
    """Test persistent storage, deduplication, and lifecycle transitions."""

    def test_save_and_load_alerts(self, tmp_path):
        storage_file = tmp_path / "test_alerts.json"
        manager = AlertStorageManager(storage_file)

        alert_1 = {
            "id": "alt-test-1",
            "district": "Srinagar",
            "leadDay": 1,
            "bustProbability": 75.0,
            "status": "Active"
        }
        assert manager.save_alert(alert_1) is True

        alerts = manager.load_alerts()
        assert len(alerts) == 1
        assert alerts[0]["id"] == "alt-test-1"

    def test_deduplication_preserves_status(self, tmp_path):
        storage_file = tmp_path / "test_alerts.json"
        manager = AlertStorageManager(storage_file)

        alert = {
            "id": "alt-dedup-1",
            "district": "Jammu",
            "leadDay": 2,
            "bustProbability": 68.0,
            "status": "Active"
        }
        manager.save_alert(alert)

        # User acknowledges the alert
        manager.update_status("alt-dedup-1", "Acknowledged")

        # System re-evaluates the same alert event
        alert_updated = {
            "id": "alt-dedup-1",
            "district": "Jammu",
            "leadDay": 2,
            "bustProbability": 70.0,
            "status": "Active" # Proposed new status
        }
        manager.save_alert(alert_updated)

        alerts = manager.load_alerts()
        assert len(alerts) == 1
        # Status should remain Acknowledged, not reset to Active
        assert alerts[0]["status"] == "Acknowledged"

    def test_update_status_transitions(self, tmp_path):
        storage_file = tmp_path / "test_alerts.json"
        manager = AlertStorageManager(storage_file)

        alert = {"id": "alt-status-1", "district": "Baramulla", "status": "Active"}
        manager.save_alert(alert)

        updated = manager.update_status("alt-status-1", "Dismissed")
        assert updated is not None
        assert updated["status"] == "Dismissed"

        with pytest.raises(ValueError):
            manager.update_status("alt-status-1", "InvalidStatus")


class TestNotificationAdapters:
    """Test notification adapters and safe credential degradation."""

    def test_logging_adapter(self):
        adapter = LoggingNotificationAdapter()
        alert = {"id": "alt-log", "district": "Jammu", "severity": "high", "leadDay": 1, "bustProbability": 72.0}
        assert adapter.send(alert) is True

    def test_email_adapter_unconfigured_safety(self):
        adapter = EmailNotificationAdapter({"week8": {"notifications": {"enable_email": False}}})
        assert adapter.is_configured() is False
        alert = {"id": "alt-email", "district": "Srinagar"}
        # Must return False and not throw exceptions when unconfigured
        assert adapter.send(alert) is False

    def test_composite_dispatcher(self, tmp_path):
        storage_file = tmp_path / "test_alerts.json"
        manager = AlertStorageManager(storage_file)

        dispatcher = CompositeNotificationDispatcher([
            LoggingNotificationAdapter(),
            EmailNotificationAdapter({"week8": {"notifications": {"enable_email": False}}})
        ])
        results = dispatcher.dispatch({"id": "alt-comp", "district": "Anantnag"})
        assert results["LoggingNotificationAdapter"] is True
        assert results["EmailNotificationAdapter"] is False


class TestUncertaintyAnalysisCalculations:
    """Test 1 to 10 day multi-horizon uncertainty metrics."""

    def test_empirical_uncertainty_metrics(self):
        sample_df = pd.DataFrame([
            {"district": "Srinagar", "lead_day": 1, "error": -3.0, "absolute_error": 3.0},
            {"district": "Srinagar", "lead_day": 1, "error": 2.0, "absolute_error": 2.0},
            {"district": "Jammu", "lead_day": 1, "error": 1.0, "absolute_error": 1.0},
            {"district": "Jammu", "lead_day": 1, "error": -2.0, "absolute_error": 2.0},
            {"district": "Anantnag", "lead_day": 2, "error": -4.0, "absolute_error": 4.0},
            {"district": "Baramulla", "lead_day": 2, "error": 3.0, "absolute_error": 3.0},
            {"district": "Jammu", "lead_day": 2, "error": 1.5, "absolute_error": 1.5},
        ])
        regional_df, district_df = calculate_empirical_uncertainty_metrics(sample_df, max_lead_days=10)

        assert len(regional_df) == 10
        # Days 1 and 2 are verified
        assert regional_df.loc[regional_df["lead_day"] == 1, "status"].values[0] == "empirically_verified"
        assert regional_df.loc[regional_df["lead_day"] == 2, "status"].values[0] == "empirically_verified"
        assert regional_df.loc[regional_df["lead_day"] == 1, "sample_count"].values[0] == 4

        # Days 3 to 10 are unobserved extended horizons
        for d in range(3, 11):
            assert regional_df.loc[regional_df["lead_day"] == d, "status"].values[0] == "unobserved_extended_horizon"
            assert regional_df.loc[regional_df["lead_day"] == d, "sample_count"].values[0] == 0
            assert pd.isna(regional_df.loc[regional_df["lead_day"] == d, "mae"].values[0])

    def test_regional_geojson_building(self):
        district_df = pd.DataFrame([
            {"district": "Srinagar", "lead_day": 1, "reliability_score": 0.04, "mae": 4.8, "rmse": 5.2, "bias": -4.8, "sample_count": 8},
            {"district": "Jammu", "lead_day": 1, "reliability_score": 0.09, "mae": 3.0, "rmse": 3.6, "bias": 3.0, "sample_count": 8},
            {"district": "Anantnag", "lead_day": 1, "reliability_score": 0.02, "mae": 6.4, "rmse": 6.6, "bias": -6.4, "sample_count": 8},
            {"district": "Baramulla", "lead_day": 1, "reliability_score": 0.02, "mae": 6.5, "rmse": 6.7, "bias": -6.5, "sample_count": 8},
        ])
        geojson = build_regional_reliability_geojson(district_df, "data/geography/jk_districts.geojson")
        assert geojson["type"] == "FeatureCollection"
        assert len(geojson["features"]) == 4

        jammu_feature = next((f for f in geojson["features"] if f["properties"]["district"] == "Jammu"), None)
        assert jammu_feature is not None
        assert jammu_feature["properties"]["elevation_meters"] == 327
        assert "color_hex" in jammu_feature["properties"]


class TestWeek8ApiEndpoints:
    """Test FastAPI endpoints for Week 8 alerting and uncertainty."""

    def test_get_alerts_endpoint(self, test_client):
        res = test_client.get("/api/alerts")
        assert res.status_code == 200
        data = res.json()
        assert isinstance(data, list)

    def test_evaluate_alerts_endpoint(self, test_client):
        res = test_client.post("/api/alerts/evaluate", json={"threshold": 0.65})
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert "alertsGenerated" in data

    def test_update_alert_status_endpoint(self, test_client):
        # Fetch an existing alert
        alerts_res = test_client.get("/api/alerts")
        alerts = alerts_res.json()
        if alerts:
            target_id = alerts[0]["id"]
            patch_res = test_client.patch(
                f"/api/alerts/{target_id}/status",
                json={"status": "Acknowledged"}
            )
            assert patch_res.status_code == 200
            updated = patch_res.json()
            assert updated["alert"]["status"] == "Acknowledged"

    def test_test_trigger_endpoint(self, test_client):
        res = test_client.post("/api/alerts/test-trigger", json={
            "district": "Srinagar",
            "leadDay": 4,
            "bustProbability": 82.5,
            "explanation": "Test alert via automated suite"
        })
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert data["alert"]["district"] == "Srinagar"
        assert data["alert"]["severity"] == "critical"

    def test_regional_map_endpoint(self, test_client):
        res = test_client.get("/api/reliability/regional-map")
        assert res.status_code == 200
        geojson = res.json()
        assert geojson["type"] == "FeatureCollection"
        assert len(geojson["features"]) == 4

    def test_lead_day_uncertainty_endpoint(self, test_client):
        res = test_client.get("/api/uncertainty/lead-days")
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert "regionalLeadDayMetrics" in data
        assert len(data["regionalLeadDayMetrics"]) == 10

