# Stage 3.4 Thesis Assets — Chapter 5 (RQ2 Forecasting Accuracy)

Generated strictly from audited Stage 3.4 outputs (`metrics/mae_summary.csv` and `metrics/paired_mae_differences.csv`).

## Table 5.1 — Held-Out Forecasting Performance

| Experiment | Model | Tuned alpha | Test N | MAE (95% Bootstrap CI) |
| --- | :---: | ---: | ---: | --- |
| Experiment A (2018) | M0 | Unfitted | 992 | 0.1718 [0.1604, 0.1835] |
| Experiment A (2018) | M1 | 1.58489e-07 | 992 | 0.1610 [0.1515, 0.1711] |
| Experiment A (2018) | M2 | 25.1189 | 992 | 0.1769 [0.1670, 0.1874] |
| Experiment A (2018) | M3 | 10 | 992 | 0.1774 [0.1673, 0.1880] |
| Experiment B (2021) | M0 | Unfitted | 995 | 0.1658 [0.1482, 0.1866] |
| Experiment B (2021) | M1 | 1e-06 | 995 | 0.1536 [0.1393, 0.1708] |
| Experiment B (2021) | M2 | 3.98107e-06 | 995 | 0.1519 [0.1376, 0.1692] |
| Experiment B (2021) | M3 | 63.0957 | 995 | 0.1519 [0.1375, 0.1689] |

* **Files:** `tables/table_5_1_rq2_mae_performance.csv`, `tables/table_5_1_rq2_mae_performance.tex`

## Table 5.2 — Prespecified Paired MAE Comparisons

| Experiment | Comparison | Delta_MAE (95% Paired CI) | Direction Interpretation |
| --- | --- | --- | --- |
| Experiment A (2018) | M1 vs M0 | -0.0108 [-0.0165, -0.0049] | Lower MAE (error reduction; 95% paired CI strictly < 0) |
| Experiment A (2018) | M2 vs M1 | +0.0159 [+0.0132, +0.0187] | Higher MAE (error increase; 95% paired CI strictly > 0) |
| Experiment A (2018) | M3 vs M2 | +0.0005 [-0.0011, +0.0020] | Slightly higher MAE (error increase; 95% paired CI spans 0) |
| Experiment A (2018) | M3 vs M0 | +0.0056 [-0.0010, +0.0121] | Slightly higher MAE (error increase; 95% paired CI spans 0) |
| Experiment B (2021) | M1 vs M0 | -0.0122 [-0.0191, -0.0057] | Lower MAE (error reduction; 95% paired CI strictly < 0) |
| Experiment B (2021) | M2 vs M1 | -0.0017 [-0.0023, -0.0011] | Lower MAE (error reduction; 95% paired CI strictly < 0) |
| Experiment B (2021) | M3 vs M2 | -0.0001 [-0.0008, +0.0006] | Slightly lower MAE (error reduction; 95% paired CI spans 0) |
| Experiment B (2021) | M3 vs M0 | -0.0139 [-0.0209, -0.0073] | Lower MAE (error reduction; 95% paired CI strictly < 0) |

* **Files:** `tables/table_5_2_rq2_paired_comparisons.csv`, `tables/table_5_2_rq2_paired_comparisons.tex`

## Figures
- `figures/fig_5_1_rq2_mae_comparison.{pdf,svg,png}` — Held-out MAE comparison across M0–M3 for Test Origins 2018 and 2021.
- `figures/fig_5_2_rq2_paired_mae_differences.{pdf,svg,png}` — Paired Delta_MAE intervals for the four prespecified nested comparisons.
