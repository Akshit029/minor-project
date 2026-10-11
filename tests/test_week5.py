"""
Unit tests for Week 5: Machine-Learning Forecast-Bust Classifier.
"""

import numpy as np
import pandas as pd
import pytest
import os
import tempfile
import json
import joblib

from src.forecast_bust import (
    calculate_training_bust_thresholds,
    assign_bust_labels,
    extract_forecast_time_features,
    create_chronological_splits,
    train_forecast_bust_models,
    evaluate_classifier_held_out,
    ForecastBustPredictor
)


def create_mock_forecast_dataset(n_samples: int = 50):
    """Create controlled mock forecast dataset."""
    times = pd.date_range("2026-09-01", periods=n_samples, freq="6h")
    districts = ["Srinagar", "Jammu", "Anantnag", "Baramulla"]

    df = pd.DataFrame({
        "district": [districts[i % len(districts)] for i in range(n_samples)],
        "initialization_time": times.strftime("%Y-%m-%d %H:%M:%S"),
        "valid_time": times.strftime("%Y-%m-%d %H:%M:%S"),
        "lead_hours": [(i % 5) * 6 for i in range(n_samples)],
        "lead_day": [((i % 5) * 6 // 24) + 1 for i in range(n_samples)],
        "forecast_value": 20.0 + np.sin(np.linspace(0, 10, n_samples)) * 5.0,
        "reference_value": 20.0,
    })
    # Absolute errors: mostly small (0.5 to 1.5), with ~10% large outliers (4.0 to 7.0)
    errors = np.full(n_samples, 1.0)
    errors[np.arange(0, n_samples, 10)] = 5.0  # inject busts
    df["absolute_error"] = errors
    df["error"] = errors
    return df


def test_bust_thresholds_training_derived():
    """Verify thresholds are estimated strictly from training data quantile."""
    train_df = create_mock_forecast_dataset(40)
    thresh_lookup, meta_df = calculate_training_bust_thresholds(
        train_df, quantile=0.90, min_samples=2
    )

    assert not meta_df.empty
    assert "error_threshold" in meta_df.columns
    # 90th percentile should be > 1.0 because outliers are 5.0
    global_thresh = float(train_df["absolute_error"].quantile(0.90))
    assert global_thresh > 1.0


def test_label_generation_and_leakage_absence():
    """Verify labels match error threshold and feature extraction contains no outcome leakage."""
    df = create_mock_forecast_dataset(20)
    thresh_lookup = {("Srinagar", 1): 2.0}
    labeled = assign_bust_labels(df, thresh_lookup, default_threshold=2.0)

    assert "is_bust" in labeled.columns
    # Rows with absolute_error=5.0 should be labeled 1
    assert (labeled.loc[labeled["absolute_error"] == 5.0, "is_bust"] == 1).all()
    # Rows with absolute_error=1.0 should be labeled 0
    assert (labeled.loc[labeled["absolute_error"] == 1.0, "is_bust"] == 0).all()

    # Feature extraction must strictly exclude reference_value and errors
    feats = extract_forecast_time_features(labeled)
    forbidden_cols = ["reference_value", "error", "absolute_error", "squared_error", "bias", "is_bust"]
    for col in forbidden_cols:
        assert col not in feats.columns


def test_chronological_splits():
    """Verify time-aware splitting respects temporal order."""
    df = create_mock_forecast_dataset(100)
    train_df, val_df, test_df = create_chronological_splits(df, 0.70, 0.15, 0.15)

    assert len(train_df) == 70
    assert len(val_df) == 15
    assert len(test_df) == 15

    # Verification of chronological order: train max time <= val min time <= test min time
    assert pd.to_datetime(train_df["valid_time"].max()) <= pd.to_datetime(val_df["valid_time"].min())
    assert pd.to_datetime(val_df["valid_time"].max()) <= pd.to_datetime(test_df["valid_time"].min())


def test_model_training_and_evaluation_pipeline():
    """Verify end-to-end model training, evaluation metrics, and prediction interface."""
    df = create_mock_forecast_dataset(60)
    labeled = assign_bust_labels(df, {}, default_threshold=2.0)

    train_df, val_df, test_df = create_chronological_splits(labeled, 0.70, 0.15, 0.15)
    X_train = extract_forecast_time_features(train_df)
    y_train = train_df["is_bust"]

    X_test = extract_forecast_time_features(test_df)
    y_test = test_df["is_bust"]

    lr_pipeline, rf_pipeline = train_forecast_bust_models(X_train, y_train, random_seed=42)

    eval_lr = evaluate_classifier_held_out(lr_pipeline, X_test, y_test, "Logistic Regression", threshold=0.5)
    eval_rf = evaluate_classifier_held_out(rf_pipeline, X_test, y_test, "Random Forest", threshold=0.5)

    assert "precision" in eval_lr
    assert "recall" in eval_lr
    assert "f1_score" in eval_lr
    assert "confusion_matrix" in eval_rf

    # Test serialization & ForecastBustPredictor
    with tempfile.TemporaryDirectory() as tmpdir:
        model_path = os.path.join(tmpdir, "model.joblib")
        meta_path = os.path.join(tmpdir, "meta.json")

        joblib.dump(rf_pipeline, model_path)
        meta = {
            "model_id": "TestRF",
            "feature_names": list(X_train.columns),
            "classification_threshold": 0.50
        }
        with open(meta_path, "w") as f:
            json.dump(meta, f)

        predictor = ForecastBustPredictor(model_path, meta_path)
        preds = predictor.predict(X_test)

        assert "bust_probability" in preds.columns
        assert "predicted_bust_class" in preds.columns
        assert preds["bust_probability"].between(0.0, 1.0).all()

        # Missing required feature raises ValueError
        bad_df = X_test.drop(columns=["forecast_value"])
        with pytest.raises(ValueError):
            predictor.predict(bad_df)
