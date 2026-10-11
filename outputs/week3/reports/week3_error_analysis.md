# Week 3 Scientific Report: Forecast-Observation Error Analysis & Bias Correction
**Generated:** 2026-10-11 22:47:44 UTC  
**Target Region:** Jammu and Kashmir  
**Forecast System:** NOAA Global Forecast System (GFS 0.25°)  
**Reference Verification:** ECMWF ERA5 Atmospheric Reanalysis (0.25°)  

---

## 1. Variable Availability & Compatibility Verification

| variable         | supported   | gfs_available   | era5_available   | units   | notes                                                                                                                                                                                                   |
|:-----------------|:------------|:----------------|:-----------------|:--------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| temperature_c    | True        | True            | True             | °C      | Direct 2m instantaneous temperature matched across grid points.                                                                                                                                         |
| precipitation_mm | True        | True            | True             | mm      | Caution: GFS precipitation accumulation represents step accumulation (3-6h intervals) whereas ERA5 represents hourly accumulated depth. Direct unaligned subtraction requires accumulation aggregation. |
| pressure_hpa     | False       | False           | False            | hPa     | Pressure variable is absent from downloaded local ERA5 and GFS subsets. Documented as unsupported by current dataset without fabricating observations.                                                  |

> **Scientific Note on Pressure**: Surface pressure / mean sea level pressure is absent from the downloaded local ERA5 and GFS subsets. In compliance with strict research integrity standards, pressure was not fabricated or substituted with unrelated variables.
> **Scientific Note on Precipitation Accumulation**: GFS APCP values represent step accumulation intervals (e.g. 3h/6h intervals from cycle origin), whereas ERA5 represents hourly accumulated depth. To avoid comparing physically incompatible accumulation windows, precipitation bias correction was held disabled until window-aligned accumulation aggregation is integrated.

---

## 2. Matched Validation Dataset Summary
- **Total Matched Pairs (Temperature):** 44
- **Districts Evaluated:** Anantnag, Baramulla, Jammu, Srinagar
- **Initialization Cycles:** 1
- **Error Formulation:** `error = forecast_value - reference_value` (positive bias indicates forecast overestimation)

---

## 3. Baseline Error Metrics by Forecast Lead Day

|   MAE |   RMSE |   Bias |   Median_AE |   Std_Error |   sample_count |   unique_init_cycles |   lead_day | variable      |
|------:|-------:|-------:|------------:|------------:|---------------:|---------------------:|-----------:|:--------------|
| 5.297 |  5.721 | -3.619 |       5.785 |       4.502 |             32 |                    1 |          1 | temperature_c |
| 6.142 |  6.761 | -5.808 |       7.35  |       3.614 |             12 |                    1 |          2 | temperature_c |

---

## 4. Baseline Error Metrics by Target District

|   MAE |   RMSE |   Bias |   Median_AE |   Std_Error |   sample_count |   unique_init_cycles | district   | variable      |
|------:|-------:|-------:|------------:|------------:|---------------:|---------------------:|:-----------|:--------------|
| 6.93  |  7.14  | -6.93  |        7.21 |       1.804 |             11 |                    1 | Anantnag   | temperature_c |
| 6.762 |  6.947 | -6.762 |        6.68 |       1.67  |             11 |                    1 | Baramulla  | temperature_c |
| 2.874 |  3.278 |  2.37  |        2.32 |       2.375 |             11 |                    1 | Jammu      | temperature_c |
| 5.544 |  5.925 | -5.544 |        5.99 |       2.193 |             11 |                    1 | Srinagar   | temperature_c |

---

## 5. Leakage-Safe Historical Bias Correction Evaluation

Mean bias was learned strictly on the chronological training split (earliest 70%) using a district-to-regional fallback hierarchy and evaluated on the identical held-out test split (latest 30%):

| evaluation_split                  | stage                         |   MAE |   RMSE |   Bias |   Median_AE |   Std_Error |   sample_count |
|:----------------------------------|:------------------------------|------:|-------:|-------:|------------:|------------:|---------------:|
| Held-Out Test Set (Chronological) | Uncorrected (Raw Forecast)    | 6.059 |  6.603 | -4.943 |        6.43 |       4.544 |             14 |
| Held-Out Test Set (Chronological) | Corrected (Mean Bias Removed) | 3.441 |  3.747 | -1.489 |        3.73 |       3.568 |             14 |

---
*Report generated automatically from actual execution artifacts.*