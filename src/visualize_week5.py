"""
Week 5 Visualizations Module: Forecast-Bust Classifier Evaluation.

Generates publication-quality (300 DPI) figures:
1. Precision-Recall Curves (Logistic Regression vs Random Forest)
2. Confusion Matrix Heatmaps on Held-Out Test Data
3. Model Performance Comparison (Precision, Recall, F1, Average Precision)
4. Feature Importance Analysis (Random Forest Mean Decrease in Impurity)

Outputs saved to outputs/week5/figures/
"""

import os
import json
import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import yaml
import joblib

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("visualize_week5")

plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams.update({
    "font.sans-serif": "DejaVu Sans",
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.titleweight": "bold",
    "axes.labelsize": 11,
    "axes.labelweight": "semibold",
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "figure.titlesize": 14,
    "figure.titleweight": "bold",
    "legend.fontsize": 10,
    "figure.autolayout": True,
})


def load_config(config_path: str = "config.yaml") -> dict:
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def plot_precision_recall_curves(meta: dict, out_path: str):
    """Plot Precision-Recall curves for trained models on held-out test data."""
    fig, ax = plt.subplots(figsize=(8, 6), dpi=300)

    # In case test data has PR curve data stored
    lr_info = meta.get("test_metrics", {}).get("logistic_regression", {})
    rf_info = meta.get("test_metrics", {}).get("random_forest", {})

    ax.scatter(
        [lr_info.get("recall", 0.0)], [lr_info.get("precision", 0.0)],
        color="#2b83ba", s=120, zorder=5, label=f"Logistic Regression (F1={lr_info.get('f1_score', 0):.2f})"
    )
    ax.scatter(
        [rf_info.get("recall", 0.0)], [rf_info.get("precision", 0.0)],
        color="#d7191c", s=140, marker="s", zorder=5, label=f"Random Forest (F1={rf_info.get('f1_score', 0):.2f})"
    )

    # Baseline random guessing line
    ax.axhline(0.10, color="gray", linestyle="--", alpha=0.7, label="No-Skill Prevalence Baseline (10%)")

    ax.set_title("Forecast-Bust Precision vs Recall on Held-Out Test Set", pad=12)
    ax.set_xlabel("Recall (Fraction of Actual Busts Detected)")
    ax.set_ylabel("Precision (Accuracy of Bust Predictions)")
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-0.05, 1.05)
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.legend(frameon=True, facecolor="white", edgecolor="none", loc="best")

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=300)
    plt.close(fig)
    logger.info("Saved -> %s", out_path)


def plot_confusion_matrices(meta: dict, out_path: str):
    """Plot Confusion Matrix heatmaps for both models side-by-side."""
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), dpi=300)

    models = [
        ("Logistic Regression", meta.get("test_metrics", {}).get("logistic_regression", {}).get("confusion_matrix", [[0, 0], [0, 0]])),
        ("Random Forest", meta.get("test_metrics", {}).get("random_forest", {}).get("confusion_matrix", [[0, 0], [0, 0]]))
    ]

    for ax, (name, cm) in zip(axes, models):
        cm_arr = np.array(cm)
        sns.heatmap(
            cm_arr, annot=True, fmt="d", cmap="Blues",
            xticklabels=["No Bust (0)", "Bust (1)"],
            yticklabels=["No Bust (0)", "Bust (1)"],
            cbar=False, ax=ax, annot_kws={"size": 13, "weight": "bold"}
        )
        ax.set_title(f"Confusion Matrix: {name}", pad=10)
        ax.set_xlabel("Predicted Class")
        ax.set_ylabel("True Ground Reference Class")

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=300)
    plt.close(fig)
    logger.info("Saved -> %s", out_path)


def plot_metrics_comparison_bar(metrics_df: pd.DataFrame, out_path: str):
    """Bar chart comparing Precision, Recall, F1 across classifiers."""
    fig, ax = plt.subplots(figsize=(8, 5), dpi=300)

    metric_cols = ["precision", "recall", "f1_score"]
    x = np.arange(len(metric_cols))
    width = 0.35

    models = metrics_df["model"].tolist()
    if len(models) >= 2:
        m1_vals = metrics_df.loc[metrics_df["model"] == models[0], metric_cols].values[0]
        m2_vals = metrics_df.loc[metrics_df["model"] == models[1], metric_cols].values[0]

        rects1 = ax.bar(x - width/2, m1_vals, width, label=models[0], color="#2b83ba", alpha=0.9)
        rects2 = ax.bar(x + width/2, m2_vals, width, label=models[1], color="#d7191c", alpha=0.9)

        for rect in list(rects1) + list(rects2):
            h = rect.get_height()
            ax.annotate(f"{h:.2f}",
                        xy=(rect.get_x() + rect.get_width() / 2, h),
                        xytext=(0, 3), textcoords="offset points",
                        ha="center", va="bottom", fontweight="bold", fontsize=9)

    ax.set_title("Classification Metric Comparison on Held-Out Test Cases", pad=12)
    ax.set_ylabel("Score ∈ [0, 1]")
    ax.set_xticks(x)
    ax.set_xticklabels(["Precision", "Recall", "F1-Score"], fontweight="semibold")
    ax.set_ylim(0, 1.1)
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.legend(frameon=True, facecolor="white", edgecolor="none")

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=300)
    plt.close(fig)
    logger.info("Saved -> %s", out_path)


def plot_feature_importance(pipeline_path: str, meta: dict, out_path: str):
    """Plot feature importance for Random Forest model pipeline."""
    if not os.path.exists(pipeline_path):
        return

    try:
        pipeline = joblib.load(pipeline_path)
        clf = pipeline.named_steps["classifier"]
        preprocessor = pipeline.named_steps["preprocessor"]
        feature_names = preprocessor.get_feature_names_out()
        clean_names = [f.replace("cat__district_", "district: ").replace("num__", "") for f in feature_names]

        if hasattr(clf, "feature_importances_"):
            importances = clf.feature_importances_
            title = "Forecast-Bust Feature Importance (Random Forest Gini Impurity)"
            xlabel = "Relative Feature Importance"
        elif hasattr(clf, "coef_"):
            importances = clf.coef_[0]
            title = "Forecast-Bust Feature Importance (Logistic Regression Coefficients)"
            xlabel = "Standardized Coefficient (Log-Odds Impact on Bust Probability)"
        else:
            return

        idx = np.argsort(np.abs(importances))

        fig, ax = plt.subplots(figsize=(9, 5.5), dpi=300)
        ax.barh(np.array(clean_names)[idx], importances[idx], color="#4575b4", alpha=0.88, height=0.6)
        ax.set_title(title, pad=12)
        ax.set_xlabel(xlabel)
        ax.axvline(0, color="gray", linestyle=":", linewidth=1.0)
        ax.grid(True, linestyle="--", alpha=0.6)

        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        plt.savefig(out_path, dpi=300)
        plt.close(fig)
        logger.info("Saved -> %s", out_path)
    except Exception as e:
        logger.warning("Could not plot feature importance: %s", e)


def generate_all_week5_visualizations(config_path: str = "config.yaml"):
    """Generate all Week 5 figures from outputs/week5."""
    cfg = load_config(config_path)
    w5_dir = cfg["output_dirs"].get("week5", "outputs/week5")
    fig_dir = cfg["output_dirs"].get("week5_figures", "outputs/week5/figures")
    os.makedirs(fig_dir, exist_ok=True)

    meta_path = os.path.join(w5_dir, "model_metadata.json")
    metrics_path = os.path.join(w5_dir, "held_out_metrics.csv")
    model_path = os.path.join(w5_dir, "trained_model_pipeline.joblib")

    if not os.path.exists(meta_path) or not os.path.exists(metrics_path):
        logger.warning("Week 5 model metadata or metrics missing. Skipping Week 5 visualizations.")
        return

    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    metrics_df = pd.read_csv(metrics_path)

    logger.info("Generating Week 5 visualizations into %s...", fig_dir)

    plot_precision_recall_curves(meta, os.path.join(fig_dir, "precision_recall_curve.png"))
    plot_confusion_matrices(meta, os.path.join(fig_dir, "confusion_matrix.png"))
    plot_metrics_comparison_bar(metrics_df, os.path.join(fig_dir, "model_comparison_metrics.png"))
    plot_feature_importance(model_path, meta, os.path.join(fig_dir, "feature_importance.png"))

    logger.info("Week 5 visualizations successfully generated.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate Week 5 Visualizations")
    parser.add_argument("--config", default="config.yaml", help="Path to config.yaml")
    args = parser.parse_args()

    generate_all_week5_visualizations(args.config)
