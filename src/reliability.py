"""
Week 4: Spatiotemporal Modelling for Reliability Scoring Module.

Implements an interpretable empirical reliability index based on historical forecast verification:
1. Mathematical definition:
     normalized_error = MAE / error_scale
     E = sum(w_i * normalized_error_i) / sum(w_i)
     R_error = exp(-E)
     C = n / (n + k)
     R = R_error * C  in [0, 1]
2. Strict temporal leakage prevention:
     Estimates reliability parameters strictly from historical training period.
     Evaluates on held-out test period.
3. Spatiotemporal aggregation:
     By district, forecast lead day, and district x lead day with fallback provenance.
4. Sensitivity analysis across error tolerance scales and sample confidence parameter k.
"""

import os
import logging
from typing import Dict, List, Tuple, Optional, Any
import numpy as np
import pandas as pd
import yaml

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("reliability")


def load_config(config_path: str = "config.yaml") -> dict:
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def calculate_sample_confidence(n: int, k: float) -> float:
    """
    Compute sample confidence factor:
    C = n / (n + k)
    where n >= 0 and k > 0.
    """
    if k <= 0:
        raise ValueError(f"Confidence parameter k must be strictly positive, got {k}")
    if n < 0:
        raise ValueError(f"Sample count n cannot be negative, got {n}")
    return float(n / (n + k))


def calculate_reliability_score(
    mae: float,
    error_scale: float,
    sample_count: int,
    k: float,
    min_evidence_samples: int = 1
) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    """
    Calculate baseline reliability score:
      normalized_error = MAE / error_scale
      R_error = exp(-normalized_error)
      C = sample_count / (sample_count + k)
      R = R_error * C

    Returns:
      (R, R_error, C)
      If sample_count < min_evidence_samples or MAE is NaN, returns (None, None, None)
      representing 'unknown' rather than artificial zero.
    """
    if error_scale <= 0:
        raise ValueError(f"Error scale must be positive, got {error_scale}")
    if k <= 0:
        raise ValueError(f"Confidence parameter k must be positive, got {k}")

    if np.isnan(mae) or sample_count < min_evidence_samples:
        return None, None, None

    normalized_error = mae / error_scale
    r_error = float(np.exp(-normalized_error))
    confidence = calculate_sample_confidence(sample_count, k)
    r = float(r_error * confidence)

    # Bound strictly in [0, 1]
    r = min(1.0, max(0.0, r))
    return round(r, 4), round(r_error, 4), round(confidence, 4)


def estimate_spatiotemporal_reliability(
    train_matched_df: pd.DataFrame,
    error_scale: float = 2.0,
    k: float = 10.0,
    min_evidence_samples: int = 3
) -> pd.DataFrame:
    """
    Estimate reliability parameters from historical training records.
    Computes at:
    1. District x Lead Day
    2. Regional Lead Day (fallback)
    3. Global Regional (fallback)
    """
    if train_matched_df.empty:
        return pd.DataFrame()

    df = train_matched_df.copy()
    unique_dists = sorted(df["district"].unique())
    unique_leads = sorted(df["lead_day"].unique())

    # Precompute statistics
    global_mae = float(df["absolute_error"].mean())
    global_n = len(df)
    global_r, global_re, global_c = calculate_reliability_score(
        global_mae, error_scale, global_n, k, min_evidence_samples=1
    )

    regional_lead_stats = df.groupby("lead_day")["absolute_error"].agg(["mean", "count"]).to_dict("index")
    dist_lead_stats = df.groupby(["district", "lead_day"])["absolute_error"].agg(["mean", "count"]).to_dict("index")

    rows = []
    for d in unique_dists:
        for l in unique_leads:
            key = (d, l)
            if key in dist_lead_stats and dist_lead_stats[key]["count"] >= min_evidence_samples:
                mae_val = float(dist_lead_stats[key]["mean"])
                n_val = int(dist_lead_stats[key]["count"])
                prov = "district_lead_day"
            elif l in regional_lead_stats and regional_lead_stats[l]["count"] >= min_evidence_samples:
                mae_val = float(regional_lead_stats[l]["mean"])
                n_val = int(regional_lead_stats[l]["count"])
                prov = "regional_lead_day_fallback"
            else:
                mae_val = global_mae
                n_val = global_n
                prov = "global_regional_fallback"

            r, r_err, c = calculate_reliability_score(
                mae_val, error_scale, n_val, k, min_evidence_samples=min_evidence_samples
            )

            rows.append({
                "district": d,
                "lead_day": int(l),
                "variable": df["variable"].iloc[0] if "variable" in df.columns else "temperature_c",
                "training_sample_count": n_val,
                "training_MAE": round(mae_val, 3),
                "error_tolerance_scale": error_scale,
                "confidence_factor_k": k,
                "R_error": r_err,
                "confidence_factor_C": c,
                "reliability_score_R": r,
                "provenance": prov,
            })

    return pd.DataFrame(rows)


def evaluate_reliability_on_held_out(
    test_matched_df: pd.DataFrame,
    reliability_table: pd.DataFrame,
    error_scale: float = 2.0
) -> pd.DataFrame:
    """
    Evaluate estimated reliability against actual held-out test errors.
    Checks whether higher predicted reliability corresponds to lower observed test MAE.
    """
    if test_matched_df.empty or reliability_table.empty:
        return pd.DataFrame()

    lookup = {(r["district"], int(r["lead_day"])): r["reliability_score_R"]
              for _, r in reliability_table.iterrows()}

    eval_rows = []
    for (d, l), grp in test_matched_df.groupby(["district", "lead_day"]):
        test_mae = float(grp["absolute_error"].mean())
        test_n = len(grp)
        pred_r = lookup.get((d, int(l)), np.nan)

        eval_rows.append({
            "district": d,
            "lead_day": int(l),
            "predicted_reliability_R": pred_r,
            "test_sample_count": test_n,
            "test_MAE": round(test_mae, 3),
            "test_normalized_error": round(test_mae / error_scale, 3),
        })

    eval_df = pd.DataFrame(eval_rows).sort_values("predicted_reliability_R", ascending=False).reset_index(drop=True)
    return eval_df


def perform_sensitivity_analysis(
    train_matched_df: pd.DataFrame,
    error_scales: Optional[List[float]] = None,
    k_values: Optional[List[float]] = None
) -> pd.DataFrame:
    """
    Sensitivity analysis across varying error tolerance scales and confidence k parameters.
    """
    if error_scales is None:
        error_scales = [1.0, 1.5, 2.0, 3.0, 4.0, 5.0]
    if k_values is None:
        k_values = [2.0, 5.0, 10.0, 20.0]

    if train_matched_df.empty:
        return pd.DataFrame()

    rows = []
    # Test regional lead-day level
    for l_day, grp in train_matched_df.groupby("lead_day"):
        mae = float(grp["absolute_error"].mean())
        n = len(grp)

        for escale in error_scales:
            for kval in k_values:
                r, r_err, c = calculate_reliability_score(mae, escale, n, kval, min_evidence_samples=1)
                rows.append({
                    "lead_day": int(l_day),
                    "error_scale": escale,
                    "k_value": kval,
                    "sample_count": n,
                    "MAE": round(mae, 3),
                    "R_error": r_err,
                    "confidence_C": c,
                    "reliability_score_R": r,
                })

    return pd.DataFrame(rows)


def run_week4_reliability(config_path: str = "config.yaml") -> Dict[str, Any]:
    """
    Execute full Week 4 Reliability Analysis:
    1. Load matched validation dataset from Week 3.
    2. Perform chronological split to prevent temporal leakage.
    3. Estimate spatiotemporal reliability on historical split.
    4. Evaluate on held-out test split.
    5. Perform sensitivity analysis.
    6. Export result tables.
    """
    cfg = load_config(config_path)
    w3_dir = cfg["output_dirs"].get("week3", "outputs/week3")
    w4_dir = cfg["output_dirs"].get("week4", "outputs/week4")
    os.makedirs(w4_dir, exist_ok=True)

    matched_path = os.path.join(w3_dir, "matched_validation_dataset.csv")
    if not os.path.exists(matched_path):
        raise FileNotFoundError(f"Matched validation dataset not found at {matched_path}. Run Week 3 analysis first.")

    matched_df = pd.read_csv(matched_path)

    w4_cfg = cfg.get("week4", {})
    t_scale = float(w4_cfg.get("error_scale", {}).get("temperature_c", 2.0))
    k_param = float(w4_cfg.get("confidence_k", 10.0))
    min_samples = int(w4_cfg.get("min_evidence_samples", 3))
    split_ratio = float(w4_cfg.get("temporal_split_ratio", 0.70))

    # Chronological split
    matched_df["dt"] = pd.to_datetime(matched_df["valid_time"])
    matched_df = matched_df.sort_values(by=["dt", "district"]).reset_index(drop=True)

    n_train = int(len(matched_df) * split_ratio)
    train_df = matched_df.iloc[:n_train].copy()
    test_df = matched_df.iloc[n_train:].copy()

    logger.info("Week 4 split: %d training cases, %d held-out test cases.", len(train_df), len(test_df))

    # 1. Spatiotemporal reliability table
    rel_table = estimate_spatiotemporal_reliability(
        train_df, error_scale=t_scale, k=k_param, min_evidence_samples=min_samples
    )
    rel_path = os.path.join(w4_dir, "reliability_table.csv")
    rel_table.to_csv(rel_path, index=False)
    logger.info("Saved reliability table (%d rows) -> %s", len(rel_table), rel_path)

    # 2. Held-out evaluation
    eval_table = evaluate_reliability_on_held_out(test_df, rel_table, error_scale=t_scale)
    eval_path = os.path.join(w4_dir, "held_out_evaluation.csv")
    eval_table.to_csv(eval_path, index=False)
    logger.info("Saved held-out reliability evaluation -> %s", eval_path)

    # 3. Sensitivity analysis
    sens_table = perform_sensitivity_analysis(train_df)
    sens_path = os.path.join(w4_dir, "sensitivity_analysis.csv")
    sens_table.to_csv(sens_path, index=False)
    logger.info("Saved sensitivity analysis -> %s", sens_path)

    # 4. Provenance & Sample Counts Summary
    prov_summary = rel_table.groupby("provenance").agg(
        group_count=("district", "count"),
        avg_samples=("training_sample_count", "mean"),
        avg_reliability=("reliability_score_R", "mean")
    ).reset_index()
    prov_path = os.path.join(w4_dir, "provenance_summary.csv")
    prov_summary.to_csv(prov_path, index=False)

    return {
        "reliability_table": rel_table,
        "evaluation_table": eval_table,
        "sensitivity_table": sens_table,
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Week 4 Reliability Scoring")
    parser.add_argument("--config", default="config.yaml", help="Path to config.yaml")
    args = parser.parse_args()

    run_week4_reliability(args.config)
