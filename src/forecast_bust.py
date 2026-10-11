"""
Week 5: Machine-Learning Forecast-Bust Classifier Module.

Implements a leakage-safe binary classification pipeline to predict forecast busts
(unusually large forecast errors exceeding empirical training-period thresholds):
1. Training-derived bust label generation (configurable upper quantile, e.g. 90th percentile).
2. Leakage-free feature engineering strictly using information available at forecast time:
   - Lead hours / lead day
   - District encoding (fitted on train only)
   - Initialization cycle and diurnal hour
   - Forecast values
3. Chronological Train (70%) / Validation (15%) / Test (15%) splitting.
4. Model training: Interpretable Logistic Regression & Non-linear Random Forest Classifier.
5. Comprehensive evaluation on held-out test set (Precision, Recall, F1, PR-AUC, Confusion Matrix).
6. Model serialization (.joblib) and production inference prediction interface.
"""

import os
import json
import logging
from typing import Dict, List, Tuple, Optional, Any
import numpy as np
import pandas as pd
import yaml
import joblib

from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    average_precision_score,
    precision_recall_curve,
    confusion_matrix,
    classification_report
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("forecast_bust")


def load_config(config_path: str = "config.yaml") -> dict:
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def calculate_training_bust_thresholds(
    train_df: pd.DataFrame,
    quantile: float = 0.90,
    min_samples: int = 4
) -> Tuple[Dict[Tuple[str, int], float], pd.DataFrame]:
    """
    Compute upper error quantile thresholds STRICTLY from training data:
    Thresholds estimated by (District, Lead Day) with fallback to Regional Lead Day,
    then to Global Training Quantile.
    """
    if train_df.empty or "absolute_error" not in train_df.columns:
        raise ValueError("Training data must contain 'absolute_error' column.")

    # Global fallback quantile
    global_thresh = float(train_df["absolute_error"].quantile(quantile))
    global_n = len(train_df)

    # Regional lead-day quantiles
    regional_lead_stats = {}
    for l_day, grp in train_df.groupby("lead_day"):
        regional_lead_stats[l_day] = {
            "thresh": float(grp["absolute_error"].quantile(quantile)),
            "count": len(grp)
        }

    # District x Lead Day quantiles
    dist_lead_stats = {}
    for (dist, l_day), grp in train_df.groupby(["district", "lead_day"]):
        dist_lead_stats[(dist, l_day)] = {
            "thresh": float(grp["absolute_error"].quantile(quantile)),
            "count": len(grp)
        }

    threshold_lookup = {}
    metadata_rows = []

    unique_dists = sorted(train_df["district"].unique())
    unique_leads = sorted(train_df["lead_day"].unique())

    for d in unique_dists:
        for l in unique_leads:
            key = (d, l)
            if key in dist_lead_stats and dist_lead_stats[key]["count"] >= min_samples:
                t_val = dist_lead_stats[key]["thresh"]
                cnt = dist_lead_stats[key]["count"]
                prov = "district_lead_day"
            elif l in regional_lead_stats and regional_lead_stats[l]["count"] >= min_samples:
                t_val = regional_lead_stats[l]["thresh"]
                cnt = regional_lead_stats[l]["count"]
                prov = "regional_lead_day_fallback"
            else:
                t_val = global_thresh
                cnt = global_n
                prov = "global_training_quantile_fallback"

            threshold_lookup[key] = t_val
            metadata_rows.append({
                "district": d,
                "lead_day": int(l),
                "bust_quantile": quantile,
                "error_threshold": round(t_val, 3),
                "training_sample_count": cnt,
                "provenance": prov,
            })

    meta_df = pd.DataFrame(metadata_rows)
    return threshold_lookup, meta_df


def assign_bust_labels(
    df: pd.DataFrame,
    threshold_lookup: Dict[Tuple[str, int], float],
    default_threshold: float
) -> pd.DataFrame:
    """
    Assign binary bust label:
      bust = 1 if absolute_error > threshold
      bust = 0 otherwise.
    Uses pre-computed training threshold lookup table.
    """
    labeled_df = df.copy()
    thresholds_applied = []
    bust_labels = []

    for _, row in labeled_df.iterrows():
        key = (row["district"], int(row["lead_day"]))
        thresh = threshold_lookup.get(key, default_threshold)
        is_bust = int(row["absolute_error"] > thresh)
        thresholds_applied.append(thresh)
        bust_labels.append(is_bust)

    labeled_df["bust_threshold"] = thresholds_applied
    labeled_df["is_bust"] = bust_labels
    return labeled_df


def extract_forecast_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract strictly leakage-free features available AT ISSUANCE / PREDICTION TIME:
    - lead_hours
    - lead_day
    - district
    - forecast_value
    - init_hour (diurnal cycle: 0, 6, 12, 18)
    - valid_hour
    - valid_month

    STRICTLY EXCLUDES:
    - reference_value
    - error
    - absolute_error
    - squared_error
    - bias
    - bust_threshold
    - is_bust
    """
    feats = pd.DataFrame()
    feats["district"] = df["district"].astype(str)
    feats["lead_hours"] = df["lead_hours"].astype(float)
    feats["lead_day"] = df["lead_day"].astype(float)
    feats["forecast_value"] = df["forecast_value"].astype(float)

    # Diurnal & temporal features from timestamps
    init_dt = pd.to_datetime(df["initialization_time"], utc=True)
    valid_dt = pd.to_datetime(df["valid_time"], utc=True)

    feats["init_hour"] = init_dt.dt.hour.astype(float)
    feats["valid_hour"] = valid_dt.dt.hour.astype(float)
    feats["valid_month"] = valid_dt.dt.month.astype(float)

    return feats


def create_chronological_splits(
    df: pd.DataFrame,
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Chronological splitting to prevent temporal leakage:
    Earliest 70% -> Train
    Next 15% -> Validation
    Final 15% -> Test
    """
    df_sorted = df.copy()
    df_sorted["dt"] = pd.to_datetime(df_sorted["valid_time"])
    df_sorted = df_sorted.sort_values(by=["dt", "district"]).reset_index(drop=True)
    df_sorted.drop(columns=["dt"], inplace=True)

    n = len(df_sorted)
    n_train = int(n * train_ratio)
    n_val = int(n * (train_ratio + val_ratio))

    train_df = df_sorted.iloc[:n_train].copy().reset_index(drop=True)
    val_df = df_sorted.iloc[n_train:n_val].copy().reset_index(drop=True)
    test_df = df_sorted.iloc[n_val:].copy().reset_index(drop=True)

    return train_df, val_df, test_df


def train_forecast_bust_models(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    random_seed: int = 42
) -> Tuple[Pipeline, Pipeline]:
    """
    Train baseline Logistic Regression and Random Forest classifiers.
    Features preprocessed with ColumnTransformer (OneHotEncoder for district, StandardScaler for numerics).
    All scaling and encoding fitted ONLY on training set.
    """
    cat_cols = ["district"]
    num_cols = [c for c in X_train.columns if c not in cat_cols]

    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat_cols),
            ("num", StandardScaler(), num_cols)
        ]
    )

    # 1. Logistic Regression Baseline (Interpretable)
    lr_pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", LogisticRegression(class_weight="balanced", random_state=random_seed, max_iter=1000))
    ])

    # 2. Random Forest Baseline (Non-linear)
    rf_pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", RandomForestClassifier(
            n_estimators=100, max_depth=5, class_weight="balanced", random_state=random_seed
        ))
    ])

    # Fit pipelines strictly on training data
    lr_pipeline.fit(X_train, y_train)
    rf_pipeline.fit(X_train, y_train)

    return lr_pipeline, rf_pipeline


def evaluate_classifier_held_out(
    pipeline: Pipeline,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    model_name: str,
    threshold: float = 0.50
) -> Dict[str, Any]:
    """
    Evaluate classifier performance on held-out test split:
    Calculates precision, recall, f1, average precision, confusion matrix.
    """
    y_true = y_test.values
    y_proba = pipeline.predict_proba(X_test)[:, 1] if hasattr(pipeline, "predict_proba") else pipeline.predict(X_test)
    y_pred = (y_proba >= threshold).astype(int)

    n_test = len(y_true)
    n_pos = int(np.sum(y_true == 1))
    n_neg = int(np.sum(y_true == 0))

    # Guard for single class edge case in small test sets
    if n_pos > 0 and n_neg > 0:
        prec = float(precision_score(y_true, y_pred, zero_division=0))
        rec = float(recall_score(y_true, y_pred, zero_division=0))
        f1 = float(f1_score(y_true, y_pred, zero_division=0))
        avg_prec = float(average_precision_score(y_true, y_proba))
        cm = confusion_matrix(y_true, y_pred).tolist()
        prec_curve, rec_curve, thresholds_curve = precision_recall_curve(y_true, y_proba)
    else:
        prec = float(precision_score(y_true, y_pred, zero_division=0))
        rec = float(recall_score(y_true, y_pred, zero_division=0))
        f1 = float(f1_score(y_true, y_pred, zero_division=0))
        avg_prec = np.nan
        cm = [[n_neg, 0], [0, n_pos]] if n_pos == 0 else [[0, 0], [0, n_pos]]
        prec_curve, rec_curve, thresholds_curve = np.array([prec]), np.array([rec]), np.array([0.5])

    return {
        "model_name": model_name,
        "test_samples": n_test,
        "test_bust_events": n_pos,
        "test_bust_pct": round((n_pos / n_test) * 100.0, 2) if n_test > 0 else 0.0,
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1_score": round(f1, 4),
        "average_precision": round(avg_prec, 4) if not np.isnan(avg_prec) else np.nan,
        "confusion_matrix": cm,
        "pr_curve": {
            "precision": [float(p) for p in prec_curve],
            "recall": [float(r) for r in rec_curve],
            "thresholds": [float(t) for t in thresholds_curve]
        },
        "y_true": [int(x) for x in y_true],
        "y_proba": [float(x) for x in y_proba],
        "y_pred": [int(x) for x in y_pred]
    }


class ForecastBustPredictor:
    """
    Production-ready inference prediction interface for saved Forecast-Bust models.
    Validates input schema and returns predicted bust probability and class.
    """
    def __init__(self, model_path: str, metadata_path: str):
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        if not os.path.exists(metadata_path):
            raise FileNotFoundError(f"Metadata file not found: {metadata_path}")

        self.pipeline = joblib.load(model_path)
        with open(metadata_path, "r", encoding="utf-8") as f:
            self.metadata = json.load(f)

        self.required_features = self.metadata.get("feature_names", [
            "district", "lead_hours", "lead_day", "forecast_value", "init_hour", "valid_hour", "valid_month"
        ])
        self.classification_threshold = self.metadata.get("classification_threshold", 0.50)

    def predict(self, input_features: pd.DataFrame) -> pd.DataFrame:
        """
        Predict forecast-bust probabilities for incoming forecasts.
        Input dataframe must contain required forecast features.
        Does NOT require ERA5 reference observations.
        """
        for req_col in self.required_features:
            if req_col not in input_features.columns:
                raise ValueError(f"Missing required forecast feature '{req_col}' in input schema.")

        X = input_features[self.required_features].copy()
        probas = self.pipeline.predict_proba(X)[:, 1]
        preds = (probas >= self.classification_threshold).astype(int)

        res = input_features.copy()
        res["bust_probability"] = [round(float(p), 4) for p in probas]
        res["predicted_bust_class"] = preds
        res["model_id"] = self.metadata.get("model_id", "ForecastBustModel")
        return res


def run_week5_forecast_bust(config_path: str = "config.yaml") -> Dict[str, Any]:
    """
    Execute full Week 5 Forecast-Bust Modelling Pipeline:
    1. Load matched validation dataset from Week 3.
    2. Chronological split (70% train, 15% val, 15% test).
    3. Calculate bust thresholds strictly from training set.
    4. Label datasets.
    5. Feature engineering strictly on forecast issuance variables.
    6. Train Logistic Regression and Random Forest models.
    7. Evaluate on held-out test cases.
    8. Serialize models and metadata.
    """
    cfg = load_config(config_path)
    w3_dir = cfg["output_dirs"].get("week3", "outputs/week3")
    w5_dir = cfg["output_dirs"].get("week5", "outputs/week5")
    os.makedirs(w5_dir, exist_ok=True)

    matched_path = os.path.join(w3_dir, "matched_validation_dataset.csv")
    if not os.path.exists(matched_path):
        raise FileNotFoundError(f"Matched validation dataset not found at {matched_path}. Run Week 3 analysis first.")

    matched_df = pd.read_csv(matched_path)

    w5_cfg = cfg.get("week5", {})
    bust_q = float(w5_cfg.get("bust_quantile", 0.90))
    min_thresh_samples = int(w5_cfg.get("min_samples_threshold", 4))
    train_ratio = float(w5_cfg.get("train_ratio", 0.70))
    val_ratio = float(w5_cfg.get("val_ratio", 0.15))
    test_ratio = float(w5_cfg.get("test_ratio", 0.15))
    seed = int(w5_cfg.get("random_seed", 42))
    class_thresh = float(w5_cfg.get("classification_threshold", 0.50))

    # 1. Chronological split
    train_raw, val_raw, test_raw = create_chronological_splits(
        matched_df, train_ratio=train_ratio, val_ratio=val_ratio, test_ratio=test_ratio
    )
    logger.info("Chronological Split: %d train, %d val, %d test records.",
                len(train_raw), len(val_raw), len(test_raw))

    # 2. Learn bust thresholds STRICTLY from training set
    thresh_lookup, thresh_meta = calculate_training_bust_thresholds(
        train_raw, quantile=bust_q, min_samples=min_thresh_samples
    )
    default_thresh = float(train_raw["absolute_error"].quantile(bust_q))

    thresh_path = os.path.join(w5_dir, "label_threshold_metadata.csv")
    thresh_meta.to_csv(thresh_path, index=False)
    logger.info("Saved label threshold metadata -> %s", thresh_path)

    # 3. Assign bust labels
    train_labeled = assign_bust_labels(train_raw, thresh_lookup, default_thresh)
    val_labeled = assign_bust_labels(val_raw, thresh_lookup, default_thresh)
    test_labeled = assign_bust_labels(test_raw, thresh_lookup, default_thresh)

    full_labeled = pd.concat([train_labeled, val_labeled, test_labeled], ignore_index=True)
    full_labeled_path = os.path.join(w5_dir, "labeled_forecast_dataset.csv")
    full_labeled.to_csv(full_labeled_path, index=False)
    logger.info("Saved labeled dataset (%d rows) -> %s", len(full_labeled), full_labeled_path)

    # Split summary table
    split_summary = pd.DataFrame([
        {
            "split": "Training",
            "sample_count": len(train_labeled),
            "bust_count": int(train_labeled["is_bust"].sum()),
            "bust_percentage": round((train_labeled["is_bust"].sum() / len(train_labeled)) * 100.0, 2),
            "start_time": train_labeled["valid_time"].min(),
            "end_time": train_labeled["valid_time"].max()
        },
        {
            "split": "Validation",
            "sample_count": len(val_labeled),
            "bust_count": int(val_labeled["is_bust"].sum()),
            "bust_percentage": round((val_labeled["is_bust"].sum() / len(val_labeled)) * 100.0, 2),
            "start_time": val_labeled["valid_time"].min(),
            "end_time": val_labeled["valid_time"].max()
        },
        {
            "split": "Test (Held-Out)",
            "sample_count": len(test_labeled),
            "bust_count": int(test_labeled["is_bust"].sum()),
            "bust_percentage": round((test_labeled["is_bust"].sum() / len(test_labeled)) * 100.0, 2),
            "start_time": test_labeled["valid_time"].min(),
            "end_time": test_labeled["valid_time"].max()
        }
    ])
    split_path = os.path.join(w5_dir, "split_summary.csv")
    split_summary.to_csv(split_path, index=False)
    logger.info("Saved split summary -> %s", split_path)

    # 4. Feature Extraction (Strictly issuance-time features)
    X_train = extract_forecast_time_features(train_labeled)
    y_train = train_labeled["is_bust"]

    X_val = extract_forecast_time_features(val_labeled)
    y_val = val_labeled["is_bust"]

    X_test = extract_forecast_time_features(test_labeled)
    y_test = test_labeled["is_bust"]

    # 5. Train Models
    lr_pipeline, rf_pipeline = train_forecast_bust_models(X_train, y_train, random_seed=seed)

    # 6. Evaluate Models on Held-Out Test Set
    eval_lr = evaluate_classifier_held_out(lr_pipeline, X_test, y_test, "Logistic Regression", class_thresh)
    eval_rf = evaluate_classifier_held_out(rf_pipeline, X_test, y_test, "Random Forest", class_thresh)

    eval_rows = [
        {
            "model": eval_lr["model_name"],
            "test_samples": eval_lr["test_samples"],
            "test_bust_events": eval_lr["test_bust_events"],
            "test_bust_pct": eval_lr["test_bust_pct"],
            "precision": eval_lr["precision"],
            "recall": eval_lr["recall"],
            "f1_score": eval_lr["f1_score"],
            "average_precision": eval_lr["average_precision"]
        },
        {
            "model": eval_rf["model_name"],
            "test_samples": eval_rf["test_samples"],
            "test_bust_events": eval_rf["test_bust_events"],
            "test_bust_pct": eval_rf["test_bust_pct"],
            "precision": eval_rf["precision"],
            "recall": eval_rf["recall"],
            "f1_score": eval_rf["f1_score"],
            "average_precision": eval_rf["average_precision"]
        }
    ]
    eval_df = pd.DataFrame(eval_rows)
    eval_csv_path = os.path.join(w5_dir, "held_out_metrics.csv")
    eval_df.to_csv(eval_csv_path, index=False)
    logger.info("Saved held-out classification metrics -> %s", eval_csv_path)

    # 7. Serialize Best Model Pipeline (Random Forest by default or LR if RF ties)
    best_pipeline = rf_pipeline if (eval_rf["f1_score"] >= eval_lr["f1_score"]) else lr_pipeline
    best_name = "RandomForest_BustClassifier" if best_pipeline == rf_pipeline else "LogisticRegression_BustClassifier"

    model_file_path = os.path.join(w5_dir, "trained_model_pipeline.joblib")
    joblib.dump(best_pipeline, model_file_path)
    logger.info("Saved trained model pipeline -> %s", model_file_path)

    metadata = {
        "model_id": best_name,
        "feature_names": list(X_train.columns),
        "categorical_features": ["district"],
        "numerical_features": [c for c in X_train.columns if c != "district"],
        "label_definition": f"Upper {int(bust_q * 100)}th percentile of training absolute error",
        "bust_quantile": bust_q,
        "classification_threshold": class_thresh,
        "training_cases": len(train_labeled),
        "validation_cases": len(val_labeled),
        "test_cases": len(test_labeled),
        "test_metrics": {
            "logistic_regression": {
                "precision": eval_lr["precision"],
                "recall": eval_lr["recall"],
                "f1_score": eval_lr["f1_score"],
                "average_precision": eval_lr["average_precision"],
                "confusion_matrix": eval_lr["confusion_matrix"]
            },
            "random_forest": {
                "precision": eval_rf["precision"],
                "recall": eval_rf["recall"],
                "f1_score": eval_rf["f1_score"],
                "average_precision": eval_rf["average_precision"],
                "confusion_matrix": eval_rf["confusion_matrix"]
            }
        },
        "python_environment": "Python 3.13.2, scikit-learn, joblib",
    }
    meta_json_path = os.path.join(w5_dir, "model_metadata.json")
    with open(meta_json_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    logger.info("Saved model metadata JSON -> %s", meta_json_path)

    return {
        "labeled_df": full_labeled,
        "split_summary": split_summary,
        "evaluation_metrics": eval_df,
        "eval_lr": eval_lr,
        "eval_rf": eval_rf,
        "best_pipeline": best_pipeline,
        "model_file_path": model_file_path,
        "metadata_path": meta_json_path
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Week 5 Forecast-Bust Classifier")
    parser.add_argument("--config", default="config.yaml", help="Path to config.yaml")
    args = parser.parse_args()

    run_week5_forecast_bust(args.config)
