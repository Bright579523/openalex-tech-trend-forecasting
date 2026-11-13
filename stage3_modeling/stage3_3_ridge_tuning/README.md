# Stage 3.3 — Ridge Regression & GroupKFold Hyperparameter Tuning

## Purpose
This directory implements **Stage 3.3 only**: hyperparameter tuning via topic-grouped 5-fold cross-validation (`GroupKFold(n_splits=5, shuffle=True, random_state=42)`) and full training-set `Pipeline([StandardScaler(), Ridge()])` fitting for the three learned primary specifications (`M1`, `M2`, `M3`) across Experiment A (Test Origin `2018`) and Experiment B (Test Origin `2021`). `M0` is recorded as an unfitted direct benchmark (`m0_adj`).

Strict Stage 3.3 boundaries:
- Uses Stage 3.2 training files only (`train_2018_*`, `train_2021_*`). Never reads test or RQ3 files.
- Never generates test predictions, out-of-sample test MAE comparisons, paired bootstrap CIs, RQ3 Top-50 rankings/Hits@50, or sensitivity models (`M3-LogRCA`, `M2-WC`, `M3-WC`).

## Locked Specifications
1. **Model Feature Sets (explicit column names only, zero identifier leakage):**
   - `M0`: unfitted direct baseline (`m0_adj`)
   - `M1` (`2` features): `m0_adj`, `ln_global_topic_3yr`
   - `M2` (`5` features): `M1` + `ln_frac_de_3yr`, `ln_frac_cn_3yr`, `ln_frac_jp_3yr`
   - `M3` (`8` features): `M2` + `rca_frac_de_3yr`, `rca_frac_cn_3yr`, `rca_frac_jp_3yr`
2. **Pipeline & CV Protocol:** `Pipeline([("scaler", StandardScaler()), ("ridge", Ridge())])` with `GroupKFold(n_splits=5, shuffle=True, random_state=42)` grouped by `topic_id` (requires `scikit-learn >= 1.6`). Identical 5 folds shared across `M1–M3` within each experiment.
3. **Alpha Search & Tie-Breaking:** Initial grid `np.logspace(-3, 5, 41)`, `scoring="neg_mean_absolute_error"`, `n_jobs=1`, custom callable `refit` minimizing mean 5-fold CV MAE and breaking ties within `1e-12` toward the **largest `alpha`**. Automatic grid expansion triggers if an optimal `alpha` falls on the grid boundary. CV score is extracted via `-float(gs.cv_results_["mean_test_score"][gs.best_index_])` (never `best_score_`).

## Execution Order
Run from repository root:

```powershell
python -B stage3_modeling/stage3_3_ridge_tuning/build_stage3_3_ridge.py
python -B stage3_modeling/stage3_3_ridge_tuning/audit_stage3_3_ridge.py
```

## Outputs
- `stage3_3_model_selection_summary.csv`: Consolidated summary for `M0–M3` across Origins `2018` and `2021`.
- `cv_folds_2018.csv`, `cv_folds_2021.csv`: Deterministic 5-fold `GroupKFold` assignment tables.
- `cv_results/cv_results_{2018,2021}_{m1,m2,m3}.csv`: Full candidate alpha grids (`alpha`, `mean_cv_mae`, `std_cv_mae`, `fold0_mae..fold4_mae`, ranks, boundary flags).
- `models/ridge_pipeline_{2018,2021}_{m1,m2,m3}.joblib`: Six final `StandardScaler -> Ridge` pipelines refitted on the complete respective training sets.
- `stage3_3_ridge_manifest.json`, `stage3_3_ridge_audit_report.md`: Manifest and independent audit certification.

