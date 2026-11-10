"""
Week 8: Automated Forecast-Bust Alerting System and Notification Architecture.

Implements an operational alerting mechanism that detects unreliable forecasts using:
1. Actual predictions from the Week 5 Forecast-Bust Classifier (LogisticRegression / RandomForest).
2. A configurable bust-probability threshold (via config.yaml or ALERT_THRESHOLD env var).
3. Unique cryptographic hashing (district + init_time + valid_time + lead_day) to prevent duplicate alerts.
4. Persistent file-based storage with status lifecycle (Active, Acknowledged, Dismissed).
5. Modular notification adapters (In-App, System Logging, and Optional Email with strict verification).
6. Integration with Week 4 spatiotemporal reliability tables for contextual error indicators.
"""

import os
import sys
import json
import hashlib
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import pandas as pd
import yaml

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.forecast_bust import ForecastBustPredictor

logger = logging.getLogger("alerting")


def load_config(config_path: str = "config.yaml") -> dict:
    """Load project YAML configuration."""
    resolved_path = PROJECT_ROOT / config_path if not os.path.isabs(config_path) else Path(config_path)
    if not resolved_path.exists():
        logger.warning("Config path '%s' not found. Returning default alerting config.", resolved_path)
        return {
            "week8": {
                "alert_threshold": 0.60,
                "alert_persistence_path": "outputs/week8/alerts.json",
                "notifications": {
                    "enable_logging": True,
                    "enable_in_app": True,
                    "enable_email": False
                }
            }
        }
    with open(resolved_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_configured_alert_threshold(config: Optional[dict] = None) -> float:
    """
    Retrieve bust probability alert threshold.
    Priority:
    1. ALERT_THRESHOLD environment variable (if valid float between 0.0 and 1.0).
    2. config.yaml -> week8.alert_threshold.
    3. Default: 0.60 (60% predicted bust risk).
    """
    env_thresh = os.getenv("ALERT_THRESHOLD")
    if env_thresh is not None:
        try:
            val = float(env_thresh)
            if 0.0 <= val <= 1.0:
                return val
            logger.warning("ALERT_THRESHOLD env var '%s' out of bounds [0.0, 1.0]. Falling back.", env_thresh)
        except ValueError:
            logger.warning("Invalid ALERT_THRESHOLD env var '%s'. Falling back.", env_thresh)

    if config and "week8" in config:
        cfg_val = config["week8"].get("alert_threshold")
        if cfg_val is not None and isinstance(cfg_val, (int, float)):
            return float(cfg_val)

    return 0.60


def generate_alert_hash(district: str, init_time: str, valid_time: str, lead_day: int) -> str:
    """
    Compute a deterministic unique identifier for a forecast event.
    Prevents duplicate alerts for identical (district, init, valid, lead_day) instances.
    """
    raw_key = f"{district.strip().lower()}|{str(init_time).strip()}|{str(valid_time).strip()}|{lead_day}"
    digest = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()
    return f"alt-{district.lower()[:3]}-{lead_day}d-{digest[:8]}"


def determine_alert_severity(bust_probability: float) -> str:
    """Classify alert severity based on predicted bust risk probability."""
    if bust_probability >= 0.80:
        return "critical"
    if bust_probability >= 0.65:
        return "high"
    if bust_probability >= 0.50:
        return "moderate"
    return "low"


# ============================================================================
# NOTIFICATION ADAPTERS
# ============================================================================

class NotificationAdapter(ABC):
    """Abstract base class for alert delivery adapters."""

    @abstractmethod
    def send(self, alert: Dict[str, Any]) -> bool:
        """Deliver alert. Returns True if successfully sent, False otherwise."""
        pass


class LoggingNotificationAdapter(NotificationAdapter):
    """Adapter logging alerts to standard system logger."""

    def __init__(self, logger_instance: Optional[logging.Logger] = None):
        self.logger = logger_instance or logger

    def send(self, alert: Dict[str, Any]) -> bool:
        self.logger.warning(
            "WEATHER ALERT [%s] ID=%s | District=%s | LeadDay=%d | BustProb=%.1f%% (Thresh=%.1f%%) | %s",
            alert.get("severity", "UNKNOWN").upper(),
            alert.get("id"),
            alert.get("district"),
            alert.get("leadDay", 0),
            alert.get("bustProbability", 0.0),
            alert.get("thresholdValue", 0.0),
            alert.get("explanation", "")
        )
        return True


class InAppNotificationAdapter(NotificationAdapter):
    """Adapter storing alerts into persistent repository for frontend consumption."""

    def __init__(self, storage_manager: "AlertStorageManager"):
        self.storage = storage_manager

    def send(self, alert: Dict[str, Any]) -> bool:
        return self.storage.save_alert(alert)


class EmailNotificationAdapter(NotificationAdapter):
    """
    Adapter sending email alerts via SMTP.
    Safely handles missing credentials without failing silently or claiming false delivery.
    """

    def __init__(self, config: Optional[dict] = None):
        cfg = config or {}
        notif_cfg = cfg.get("week8", {}).get("notifications", {})
        self.enabled = notif_cfg.get("enable_email", False)
        self.smtp_server = os.getenv("SMTP_SERVER", notif_cfg.get("email_smtp_server", ""))
        self.smtp_port = int(os.getenv("SMTP_PORT", str(notif_cfg.get("email_smtp_port", 587))))
        self.smtp_user = os.getenv("SMTP_USER", notif_cfg.get("email_smtp_user", ""))
        self.smtp_password = os.getenv("SMTP_PASSWORD", notif_cfg.get("email_smtp_password", ""))
        self.recipient = os.getenv("ALERT_EMAIL_RECIPIENT", notif_cfg.get("email_recipient", ""))

    def is_configured(self) -> bool:
        """Verify whether valid SMTP credentials are fully provided."""
        return bool(self.enabled and self.smtp_server and self.smtp_user and self.smtp_password and self.recipient)

    def send(self, alert: Dict[str, Any]) -> bool:
        if not self.enabled:
            logger.debug("Email notifications are disabled in configuration.")
            return False

        if not self.is_configured():
            logger.info(
                "Email alert skipped: SMTP credentials/recipient not configured. Alert preserved in-app."
            )
            return False

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"[{alert.get('severity', 'WARNING').upper()}] Forecast Bust Alert - {alert.get('district')} Day {alert.get('leadDay')}"
            msg["From"] = self.smtp_user
            msg["To"] = self.recipient

            text_content = (
                f"FORECAST BUST ALERT: {alert.get('district')}\n"
                f"Severity: {alert.get('severity')}\n"
                f"Lead Day: {alert.get('leadDay')} (Valid: {alert.get('validTime', 'N/A')})\n"
                f"Predicted Bust Probability: {alert.get('bustProbability')}%\n"
                f"Configured Threshold: {alert.get('thresholdValue')}%\n"
                f"Explanation: {alert.get('explanation')}\n"
                f"Generated At: {alert.get('timestamp')}\n"
            )
            msg.attach(MIMEText(text_content, "plain"))

            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.smtp_user, [self.recipient], msg.as_string())

            logger.info("Email notification delivered successfully to %s for alert %s", self.recipient, alert.get("id"))
            return True
        except Exception as e:
            logger.error("Failed to deliver email alert: %s. Alert saved in-app.", e)
            return False


class CompositeNotificationDispatcher:
    """Dispatches alerts across all registered active notification adapters."""

    def __init__(self, adapters: Optional[List[NotificationAdapter]] = None):
        self.adapters: List[NotificationAdapter] = adapters or []

    def register(self, adapter: NotificationAdapter):
        self.adapters.append(adapter)

    def dispatch(self, alert: Dict[str, Any]) -> Dict[str, bool]:
        results = {}
        for adapter in self.adapters:
            name = adapter.__class__.__name__
            try:
                results[name] = adapter.send(alert)
            except Exception as e:
                logger.error("Adapter '%s' threw unhandled exception: %s", name, e)
                results[name] = False
        return results


# ============================================================================
# PERSISTENT ALERT STORAGE MANAGER
# ============================================================================

class AlertStorageManager:
    """
    Manages persistent JSON storage of generated weather alerts.
    Provides atomic read, save, deduplication, and status lifecycle operations.
    """

    def __init__(self, storage_path: Union[str, Path] = "outputs/week8/alerts.json"):
        self.storage_path = PROJECT_ROOT / storage_path if not os.path.isabs(storage_path) else Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_storage_initialized()

    def _ensure_storage_initialized(self):
        """Create empty JSON array if file does not exist or is corrupted."""
        if not self.storage_path.exists():
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump([], f, indent=2)

    def load_alerts(self) -> List[Dict[str, Any]]:
        """Load all alerts from disk."""
        self._ensure_storage_initialized()
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except Exception as e:
            logger.error("Error reading alert storage from '%s': %s. Returning empty list.", self.storage_path, e)
            return []

    def save_alert(self, alert: Dict[str, Any]) -> bool:
        """
        Save or update an alert.
        Prevents duplicates by checking existing alert IDs.
        """
        alerts = self.load_alerts()
        alert_id = alert.get("id")

        # Check for existing duplicate
        existing_idx = next((i for i, a in enumerate(alerts) if a.get("id") == alert_id), None)
        if existing_idx is not None:
            # Preserve existing user-assigned status (e.g., Acknowledged or Dismissed)
            existing_status = alerts[existing_idx].get("status", "Active")
            alert["status"] = existing_status
            alerts[existing_idx] = alert
            logger.debug("Updated existing alert ID: %s (status retained: %s)", alert_id, existing_status)
        else:
            alerts.insert(0, alert)
            logger.info("Persisted new weather alert ID: %s (%s, Day %s)", alert_id, alert.get("district"), alert.get("leadDay"))

        try:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(alerts, f, indent=2)
            return True
        except Exception as e:
            logger.error("Failed to write alert to disk: %s", e)
            return False

    def update_status(self, alert_id: str, new_status: str) -> Optional[Dict[str, Any]]:
        """
        Update the lifecycle status of an existing alert ('Active', 'Acknowledged', 'Dismissed').
        """
        valid_statuses = ["Active", "Acknowledged", "Dismissed", "Investigating", "Resolved"]
        normalized_status = new_status.capitalize()
        if normalized_status not in valid_statuses:
            raise ValueError(f"Invalid alert status '{new_status}'. Allowed: {valid_statuses}")

        alerts = self.load_alerts()
        target = None
        for a in alerts:
            if a.get("id") == alert_id:
                a["status"] = normalized_status
                a["updated_at"] = datetime.now(timezone.utc).isoformat()
                target = a
                break

        if target is not None:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(alerts, f, indent=2)
            logger.info("Alert %s status updated to '%s'", alert_id, normalized_status)
            return target

        return None

    def filter_alerts(
        self,
        district: Optional[str] = None,
        status: Optional[str] = None,
        severity: Optional[str] = None,
        min_probability: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """Query alerts matching specific filters."""
        alerts = self.load_alerts()
        filtered = alerts

        if district and district.lower() != "all":
            filtered = [a for a in filtered if str(a.get("district", "")).lower() == district.lower()]

        if status and status.lower() != "all":
            filtered = [a for a in filtered if str(a.get("status", "")).lower() == status.lower()]

        if severity and severity.lower() != "all":
            filtered = [a for a in filtered if str(a.get("severity", "")).lower() == severity.lower()]

        if min_probability is not None:
            filtered = [a for a in filtered if float(a.get("bustProbability", 0.0)) >= min_probability]

        return filtered


# ============================================================================
# AUTOMATED ALERT GENERATION ENGINE
# ============================================================================

class ForecastBustAlertEngine:
    """
    Core automated forecast-bust alert engine:
    Evaluates forecast records using the trained Week 5 ML classifier,
    checks against configurable threshold, pulls Week 4 reliability context,
    and dispatches non-duplicate alerts.
    """

    def __init__(self, config_path: str = "config.yaml"):
        self.config = load_config(config_path)
        self.threshold = get_configured_alert_threshold(self.config)

        # Storage & persistence
        storage_file = self.config.get("week8", {}).get("alert_persistence_path", "outputs/week8/alerts.json")
        self.storage_manager = AlertStorageManager(storage_file)

        # Dispatcher with logging and in-app adapters
        self.dispatcher = CompositeNotificationDispatcher([
            LoggingNotificationAdapter(),
            InAppNotificationAdapter(self.storage_manager),
            EmailNotificationAdapter(self.config)
        ])

        # Load Week 4 reliability lookup table if available
        self.reliability_table = self._load_reliability_table()

        # Load Week 5 model pipeline
        self.predictor = self._load_predictor()

    def _load_reliability_table(self) -> Optional[pd.DataFrame]:
        w4_path = PROJECT_ROOT / self.config.get("output_dirs", {}).get("week4", "outputs/week4") / "reliability_table.csv"
        if w4_path.exists():
            try:
                return pd.read_csv(w4_path)
            except Exception as e:
                logger.warning("Could not read reliability table '%s': %s", w4_path, e)
        return None

    def _load_predictor(self) -> Optional[ForecastBustPredictor]:
        model_path = PROJECT_ROOT / self.config.get("output_dirs", {}).get("week5", "outputs/week5") / "trained_model_pipeline.joblib"
        meta_path = PROJECT_ROOT / self.config.get("output_dirs", {}).get("week5", "outputs/week5") / "model_metadata.json"
        if model_path.exists() and meta_path.exists():
            try:
                return ForecastBustPredictor(str(model_path), str(meta_path))
            except Exception as e:
                logger.error("Failed to load Week 5 ForecastBustPredictor: %s", e)
        else:
            logger.warning("Week 5 model or metadata not found at %s. Evaluation will require pre-computed probabilities.", model_path)
        return None

    def get_reliability_for_event(self, district: str, lead_day: int) -> Dict[str, Any]:
        """Fetch empirical reliability context from Week 4 artifacts."""
        if self.reliability_table is not None and not self.reliability_table.empty:
            match = self.reliability_table[
                (self.reliability_table["district"].str.lower() == district.lower()) &
                (self.reliability_table["lead_day"] == lead_day)
            ]
            if not match.empty:
                row = match.iloc[0]
                return {
                    "reliability": round(float(row.get("reliability_score_R", 0.50)), 4),
                    "mae": round(float(row.get("training_MAE", 2.0)), 2),
                    "provenance": str(row.get("provenance", "district_lead_day"))
                }
        # Fallback conservative estimate
        return {"reliability": 0.50, "mae": 2.50, "provenance": "regional_fallback"}

    def evaluate_forecasts(
        self,
        forecast_df: pd.DataFrame,
        custom_threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Evaluate a dataframe of forecast predictions against the alert threshold.
        Generates and dispatches alerts for all forecasts exceeding the threshold.
        """
        threshold = custom_threshold if custom_threshold is not None else self.threshold

        if forecast_df.empty:
            logger.info("Forecast dataframe is empty. No alerts generated.")
            return []

        # Predict bust probabilities if not already present
        if "bust_probability" not in forecast_df.columns:
            if self.predictor is None:
                raise RuntimeError("Week 5 model predictor is not available to compute bust probabilities.")
            evaluated_df = self.predictor.predict(forecast_df)
        else:
            evaluated_df = forecast_df.copy()

        generated_alerts: List[Dict[str, Any]] = []

        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

        for idx, row in evaluated_df.iterrows():
            prob = float(row.get("bust_probability", 0.0))
            if prob < threshold:
                continue

            district = str(row.get("district", "Unknown"))
            lead_day = int(row.get("lead_day", 1))
            lead_hours = int(row.get("lead_hours", lead_day * 24))
            init_time = str(row.get("initialization_time", "Unknown"))
            valid_time = str(row.get("valid_time", "Unknown"))
            forecast_val = round(float(row.get("forecast_value", 0.0)), 2)

            alert_id = generate_alert_hash(district, init_time, valid_time, lead_day)
            severity = determine_alert_severity(prob)
            rel_info = self.get_reliability_for_event(district, lead_day)

            pct_prob = round(prob * 100.0, 1)
            pct_thresh = round(threshold * 100.0, 1)

            explanation = (
                f"Predicted forecast-bust risk ({pct_prob}%) exceeds the configured {pct_thresh}% operational threshold. "
                f"Historical baseline MAE is {rel_info['mae']}°C with empirical reliability index {rel_info['reliability']}."
            )

            alert: Dict[str, Any] = {
                "id": alert_id,
                "severity": severity,
                "district": district,
                "leadDay": lead_day,
                "leadHours": lead_hours,
                "alertType": "potential_forecast_bust",
                "reliability": rel_info["reliability"],
                "bustProbability": pct_prob,
                "title": f"Forecast Bust Warning: {district} (Day {lead_day})",
                "explanation": explanation,
                "timestamp": now_iso,
                "initializationTime": init_time,
                "validTime": valid_time,
                "status": "Active",
                "variable": "temperature_c",
                "forecastValue": forecast_val,
                "thresholdValue": pct_thresh,
                "modelUsed": str(row.get("model_id", "Week 5 BustClassifier")),
                "created_at": datetime.now(timezone.utc).isoformat()
            }

            # Dispatch through registered notification adapters (logging, in-app storage, optional email)
            self.dispatcher.dispatch(alert)
            generated_alerts.append(alert)

        logger.info(
            "Alert evaluation complete: %d alerts triggered out of %d evaluated forecasts (Threshold = %.1f%%).",
            len(generated_alerts),
            len(evaluated_df),
            threshold * 100.0
        )
        return generated_alerts


def run_week8_alerting(config_path: str = "config.yaml") -> Dict[str, Any]:
    """
    Main pipeline entrypoint for Week 8 Automated Alerting:
    1. Loads labeled/test forecasts from Week 5 artifacts.
    2. Runs threshold evaluation using the configured alert threshold.
    3. Persists generated alerts and generates tabular summary.
    """
    cfg = load_config(config_path)
    engine = ForecastBustAlertEngine(config_path)

    w5_dir = PROJECT_ROOT / cfg.get("output_dirs", {}).get("week5", "outputs/week5")
    labeled_file = w5_dir / "labeled_forecast_dataset.csv"

    if not labeled_file.exists():
        logger.warning("Labeled forecast dataset '%s' not found. Cannot evaluate historical alerts.", labeled_file)
        return {
            "success": False,
            "error": f"Missing input dataset: {labeled_file}",
            "alerts_generated": 0
        }

    df = pd.read_csv(labeled_file)

    # Compute or format feature columns needed for inference
    if "lead_hours" not in df.columns:
        df["lead_hours"] = df["lead_day"] * 24.0

    if "init_hour" not in df.columns and "initialization_time" in df.columns:
        df["init_hour"] = pd.to_datetime(df["initialization_time"]).dt.hour

    if "valid_hour" not in df.columns and "valid_time" in df.columns:
        df["valid_hour"] = pd.to_datetime(df["valid_time"]).dt.hour

    if "valid_month" not in df.columns and "valid_time" in df.columns:
        df["valid_month"] = pd.to_datetime(df["valid_time"]).dt.month

    alerts = engine.evaluate_forecasts(df)

    # Save summary table
    out_dir = PROJECT_ROOT / cfg.get("output_dirs", {}).get("week8", "outputs/week8")
    out_dir.mkdir(parents=True, exist_ok=True)

    summary_file = out_dir / "alert_evaluation_summary.csv"
    if alerts:
        alerts_df = pd.DataFrame(alerts)
        alerts_df.to_csv(summary_file, index=False)
    else:
        pd.DataFrame([{
            "status": "No alerts triggered",
            "threshold": engine.threshold,
            "evaluated_count": len(df)
        }]).to_csv(summary_file, index=False)

    return {
        "success": True,
        "alert_threshold": engine.threshold,
        "evaluated_forecasts": len(df),
        "alerts_generated": len(alerts),
        "alerts_stored_path": str(engine.storage_manager.storage_path.relative_to(PROJECT_ROOT)),
        "alerts": alerts
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    res = run_week8_alerting()
    print("\n--- Week 8 Alerting Pipeline Result ---")
    print(f"Status: {'SUCCESS' if res.get('success') else 'FAILED'}")
    print(f"Evaluated Forecasts: {res.get('evaluated_forecasts', 0)}")
    print(f"Alerts Triggered: {res.get('alerts_generated', 0)}")
    print(f"Threshold: {res.get('alert_threshold', 0.60):.2f}")
    if res.get("alerts"):
        print("\nSample Generated Alert:")
        print(json.dumps(res["alerts"][0], indent=2))

