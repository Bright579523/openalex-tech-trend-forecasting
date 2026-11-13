# Stage 3.2 — Train/Test Dataset & RQ3 Candidate-Pool Splits

## Purpose
This directory holds the deterministic **Stage 3.2** train/test splits and RQ3 emerging high-growth candidate pools for the two approved temporal test origins (`2018` and `2021`), built strictly from the audited Stage 3.1 feature-target dataset (`stage3_modeling/stage3_origin_features_targets.csv`, SHA-256 `9fc15d6ed16ade633547bfca9efca1db92827aa665cbb4509d76c7dae057f488`).

Stage 3.2 performs **data splitting and label definition only**:
- No scalers (`StandardScaler`) are fitted.
- No Ridge models are trained and no hyperparameters (`alpha`) are tuned.
- No predictions, forecast errors (MAE), Top-50 rankings, Hits@50, or bootstrap intervals are computed.

## Execution Order
Run from the repository root (`d:\Thesis` or repo working directory):

1. Build all Stage 3.2 CSV exports and manifest:
   ```powershell
   python -B stage3_modeling/stage3_2_splits/build_stage3_2_splits.py
   ```
2. Run the independent Stage 3.2 audit (including repeated-execution determinism verification):
   ```powershell
   python -B stage3_modeling/stage3_2_splits/audit_stage3_2_splits.py
   ```
3. (Optional) Regenerate Stage 3.2 thesis table and timeline figure in `stage3_modeling/thesis_assets/`:
   ```powershell
   python -B stage3_modeling/thesis_assets/build_stage3_2_thesis_assets.py
   ```

## Exported Outputs (Strict Predictor / Target Separation)
Target columns (`g_adj`, `target_global_topic_fut3yr`, `target_w_allsci_fut3yr`) and RQ3 labels (`hg_future`) are exported in separate aligned CSVs so they cannot accidentally enter model fitting as features. Every paired file is sorted identically in ascending `(forecast_origin, topic_id)` order.

### Experiment A — Test Origin `2018` (`train: 2015`, `test: 2018`)
- `train_2018_features.csv` (`990 × 23`): 6 identifier columns + 17 approved past-only predictors.
- `train_2018_targets.csv` (`990 × 5`): `forecast_origin`, `topic_id`, `g_adj`, `target_global_topic_fut3yr`, `target_w_allsci_fut3yr`.
- `test_2018_features.csv` (`992 × 23`): 6 identifier columns + 17 approved past-only predictors.
- `test_2018_targets.csv` (`992 × 5`): `forecast_origin`, `topic_id`, `g_adj`, `target_global_topic_fut3yr`, `target_w_allsci_fut3yr`.
- `rq3_2018_pool_features.csv` (`793 × 23`): non-top-20% past-growth candidate pool (`m0_adj < Q0.80_past`).
- `rq3_2018_pool_labels.csv` (`793 × 4`): `forecast_origin`, `topic_id`, `g_adj`, `hg_future` (`159` positives; `20.05%` chance rate).

### Experiment B — Test Origin `2021` (`train: 2015–2018`, `test: 2021`)
- `train_2021_features.csv` (`3,963 × 23`): 6 identifier columns + 17 approved past-only predictors.
- `train_2021_targets.csv` (`3,963 × 5`): `forecast_origin`, `topic_id`, `g_adj`, `target_global_topic_fut3yr`, `target_w_allsci_fut3yr`.
- `test_2021_features.csv` (`995 × 23`): 6 identifier columns + 17 approved past-only predictors.
- `test_2021_targets.csv` (`995 × 5`): `forecast_origin`, `topic_id`, `g_adj`, `target_global_topic_fut3yr`, `target_w_allsci_fut3yr`.
- `rq3_2021_pool_features.csv` (`796 × 23`): non-top-20% past-growth candidate pool (`m0_adj < Q0.80_past`).
- `rq3_2021_pool_labels.csv` (`796 × 4`): `forecast_origin`, `topic_id`, `g_adj`, `hg_future` (`160` positives; `20.10%` chance rate).

### Metadata & Verification Reports
- `stage3_2_splits_manifest.json`: Relative paths, SHA-256 hashes, `GroupKFold(5, shuffle=True, random_state=42)` partition preview, RQ3 thresholds, and boundary assertions.
- `stage3_2_splits_audit_report.md`: Independent 17-check audit certification (`PASS`/`FAIL`).

## Validation Rules
1. **Temporal Cutoff:** Every training origin satisfies `forecast_origin + 3 <= test_origin`. Pooled annual training origins (`2015–2018`) for Experiment B share overlapping internal 3-year target windows (`<= 2021`), creating `989` exact `G_adj(2015) == M0_adj(2018)` topic pairs that require `GroupKFold(n_splits=5, shuffle=True, random_state=42)` grouped by `topic_id` during Stage 3.3 hyperparameter tuning (`scikit-learn >= 1.6`).
2. **Origin-Specific Eligibility:** Only rows with `eligible == True` (`global_topic_3yr >= 50`) in Stage 3.1 are included.
3. **Locked RQ3 Quantile Protocol:** Both thresholds use `np.quantile(..., 0.80, method="linear")` and `>=`:
   - Step 1 (exclusion): exclude `m0_adj >= Q0.80_past` from the test origin (`199` topics excluded at each origin, zero ties).
   - Step 2 (future label): define `hg_future = 1` iff `g_adj >= Q0.80_future` within the remaining pool (`159/793` in `2018`; `160/796` in `2021`, where `(796 - 1) * 0.80 = 636.0` lands on an exact sorted observation).
4. **Determinism & Traceability:** Repeated builds produce byte-identical SHA-256 hashes across all 12 CSVs, zero NaN/Inf values, and exact scalar parity (`<= 1e-12`) against Stage 3.1.

