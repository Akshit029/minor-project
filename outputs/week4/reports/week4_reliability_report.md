# Week 4 Scientific Report: Spatiotemporal Modelling for Reliability Scoring
**Generated:** 2026-10-11 22:47:44 UTC  
**Target Region:** Jammu and Kashmir  

---

## 1. Mathematical Formulation of the Reliability Index

The empirical reliability index $R \in [0, 1]$ is formulated from historical verification errors:

1. **Normalized Error**: For variable $i$, $normalized\_error_i = \text{MAE}_i / \text{error\_scale}_i$, where $\text{error\_scale}_i > 0$ is an engineering tolerance ($2.0^\circ\text{C}$ for temperature).
2. **Error-based Reliability Component**: $R_{\text{error}} = \exp(-normalized\_error)$. When error is zero, $R_{\text{error}} = 1.0$. As error grows, it monotonically decays towards 0.
3. **Sample Confidence Factor**: $C = \frac{n}{n + k}$, where $n$ is the number of historical verification cases and $k > 0$ is a configurable sample-smoothing parameter ($k=10$).
4. **Composite Reliability Score**: $R = R_{\text{error}} \times C$.

> **Important Scientific Distinction**: $R$ is an **empirical reliability index** reflecting historical accuracy and sample support. It is **not an uncalibrated Bayesian probability** of absolute correctness.

---

## 2. Spatiotemporal Reliability Table (Training Split Estimates)

| district   |   lead_day | variable      |   training_sample_count |   training_MAE |   error_tolerance_scale |   confidence_factor_k |   R_error |   confidence_factor_C |   reliability_score_R | provenance        |
|:-----------|-----------:|:--------------|------------------------:|---------------:|------------------------:|----------------------:|----------:|----------------------:|----------------------:|:------------------|
| Anantnag   |          1 | temperature_c |                       8 |          6.42  |                       2 |                    10 |    0.0404 |                0.4444 |                0.0179 | district_lead_day |
| Baramulla  |          1 | temperature_c |                       8 |          6.52  |                       2 |                    10 |    0.0384 |                0.4444 |                0.0171 | district_lead_day |
| Jammu      |          1 | temperature_c |                       7 |          3.004 |                       2 |                    10 |    0.2227 |                0.4118 |                0.0917 | district_lead_day |
| Srinagar   |          1 | temperature_c |                       7 |          4.833 |                       2 |                    10 |    0.0892 |                0.4118 |                0.0367 | district_lead_day |

---

## 3. Held-Out Evaluation on Unseen Later Forecasts

| district   |   lead_day |   predicted_reliability_R |   test_sample_count |   test_MAE |   test_normalized_error |
|:-----------|-----------:|--------------------------:|--------------------:|-----------:|------------------------:|
| Jammu      |          1 |                    0.0917 |                   1 |      5.81  |                   2.905 |
| Srinagar   |          1 |                    0.0367 |                   1 |      5.31  |                   2.655 |
| Anantnag   |          2 |                  nan      |                   3 |      8.29  |                   4.145 |
| Baramulla  |          2 |                  nan      |                   3 |      7.407 |                   3.703 |
| Jammu      |          2 |                  nan      |                   3 |      1.59  |                   0.795 |
| Srinagar   |          2 |                  nan      |                   3 |      7.28  |                   3.64  |

---

## 4. Sensitivity Analysis across Tolerance Scales and Smoothing Parameters

|   lead_day |   error_scale |   k_value |   sample_count |   MAE |   R_error |   confidence_C |   reliability_score_R |
|-----------:|--------------:|----------:|---------------:|------:|----------:|---------------:|----------------------:|
|          1 |           1   |         2 |             30 | 5.279 |    0.0051 |         0.9375 |                0.0048 |
|          1 |           1   |         5 |             30 | 5.279 |    0.0051 |         0.8571 |                0.0044 |
|          1 |           1   |        10 |             30 | 5.279 |    0.0051 |         0.75   |                0.0038 |
|          1 |           1   |        20 |             30 | 5.279 |    0.0051 |         0.6    |                0.0031 |
|          1 |           1.5 |         2 |             30 | 5.279 |    0.0296 |         0.9375 |                0.0278 |
|          1 |           1.5 |         5 |             30 | 5.279 |    0.0296 |         0.8571 |                0.0254 |
|          1 |           1.5 |        10 |             30 | 5.279 |    0.0296 |         0.75   |                0.0222 |
|          1 |           1.5 |        20 |             30 | 5.279 |    0.0296 |         0.6    |                0.0178 |
|          1 |           2   |         2 |             30 | 5.279 |    0.0714 |         0.9375 |                0.0669 |
|          1 |           2   |         5 |             30 | 5.279 |    0.0714 |         0.8571 |                0.0612 |
|          1 |           2   |        10 |             30 | 5.279 |    0.0714 |         0.75   |                0.0535 |
|          1 |           2   |        20 |             30 | 5.279 |    0.0714 |         0.6    |                0.0428 |

---
*Report generated automatically from actual execution artifacts.*