# Stage 3.3 Independent Audit Report

**Overall Verdict:** **PASS (14/14 checks passed)**

## 1. Model Selection & 5-Fold GroupKFold CV Summary
| Test Origin | Model | $p$ | Selected $\alpha$ | Mean CV MAE | SD CV MAE | Fold 0..4 MAEs | Grid Expanded? |
| :---: | :---: | ---: | ---: | ---: | ---: | --- | :---: |
| `2018` | `M1` | 2 | `1.58489e-07` | 0.133605 | 0.007087 | `0.138533, 0.138435, 0.128903, 0.140259, 0.121895` | `True` |
| `2018` | `M2` | 5 | `25.1189` | 0.135023 | 0.007177 | `0.140882, 0.137849, 0.127637, 0.143312, 0.125433` | `False` |
| `2018` | `M3` | 8 | `10` | 0.133731 | 0.006696 | `0.139560, 0.136076, 0.127345, 0.141274, 0.124401` | `False` |
| `2021` | `M1` | 2 | `1e-06` | 0.141997 | 0.007609 | `0.149306, 0.139007, 0.141075, 0.150800, 0.129799` | `True` |
| `2021` | `M2` | 5 | `3.98107e-06` | 0.141327 | 0.007409 | `0.148274, 0.138460, 0.140566, 0.149961, 0.129376` | `True` |
| `2021` | `M3` | 8 | `63.0957` | 0.141665 | 0.007594 | `0.149641, 0.138144, 0.140412, 0.150204, 0.129926` | `False` |

## 2. Check-by-Check Audit Results
| Check ID | Status | Supporting Evidence |
| --- | :---: | --- |
| `C1_upstream_and_stage3_2_integrity` | **PASS** | Stage 2/3.1 exact SHA-256 match; Stage 3.2 all 12 CSVs unchanged |
| `C2_manifest_summary_and_sklearn_floor` | **PASS** | scikit-learn==1.8.0, summary_rows=8 (2x M0 + 6 fitted Ridge) |
| `C3_source_metadata_column_parity` | **PASS** | topic_name, field_name, subfield_name exact string match across all Stage 3.2 training rows (mismatches=0) |
| `C4_model_feature_sets_and_no_identifier_leakage` | **PASS** | M0=[], M1=2, M2=5, M3=8 verified independently; zero identifiers/targets in feature specs |
| `C5_groupkfold_splits_and_zero_topic_overlap` | **PASS** | Exact match for GroupKFold(5, shuffle=True, random_state=42); 2018=[198x5], 2021=[796,790,796,789,792], overlap=0 |
| `C6_independent_cv_mae_and_fold_recompute` | **PASS** | max|indep_mean_mae - csv|=0.000e+00, max|indep_fold_mae - csv|=0.000e+00 |
| `C7_alpha_selection_tiebreak_and_interior_grid` | **PASS** | All 6 models select exact min-MAE largest-alpha within 1e-12 strictly inside final searched grid (41-pt [-3,5] for 2018-M2/M3 & 2021-M3; expanded 61-pt [-7,5] for 2018-M1, 2021-M1/M2) |
| `C8_pipeline_structure_full_refit_and_coef_parity` | **PASS** | All 6 joblib Pipelines verified StandardScaler->Ridge full-train refit; max_coef_diff=0.000e+00, max_pred_diff=0.000e+00 |
| `C9_stage3_3_artifact_sha256_integrity` | **PASS** | All 6 CV CSVs and 6 joblib Pipelines match manifest SHA-256 hashes |
| `C10_model_summary_parity_with_manifest` | **PASS** | stage3_3_model_selection_summary.csv matches manifest across M0-M3 for 2018 & 2021 |
| `C11_zero_absolute_paths_windows_and_posix` | **PASS** | Zero Windows drive or POSIX absolute paths across manifest and CSV artifacts |
| `C12_deterministic_repeated_execution` | **PASS** | All 15 CSV & joblib artifacts produced byte-identical SHA-256 across repeated runs |
| `C13_strict_stage3_3_boundary_zero_test_leakage` | **PASS** | Builder AST has 0 test/rq3 file refs and 0 .best_score_ accesses; zero Stage 3.4+ outputs present |
| `C14_post_audit_upstream_immutability` | **PASS** | Stage 2, Stage 3.1, and all 12 Stage 3.2 split files remain byte-identical post-run |

## 3. Exported Artifact Inventory & SHA-256 Hashes
| Artifact | Role | Details | SHA-256 |
| --- | --- | --- | --- |
| `stage3_modeling/stage3_3_ridge_tuning/cv_folds_2018.csv` | `cv_fold_assignments` | 990 × 3 | `12d9331b0f1a41e1b3d81ffd47243f52e252953a82d892fb1dfba79f5804ea52` |
| `stage3_modeling/stage3_3_ridge_tuning/cv_results/cv_results_2018_m1.csv` | `cv_results` | 61 × 17 | `2c61588005747191666bcddaa3265c8ad835f6219aec9827d46739f8fd90f00e` |
| `stage3_modeling/stage3_3_ridge_tuning/models/ridge_pipeline_2018_m1.joblib` | `fitted_pipeline` | n_samples=990, p=2 | `b528e37db5f9feeed68e8d8c36680f63c91b666a0d0bf7b9cb40e2c0c9611be4` |
| `stage3_modeling/stage3_3_ridge_tuning/cv_results/cv_results_2018_m2.csv` | `cv_results` | 41 × 17 | `9f84a4b3b97b0dd9b4a179b8aece8fb738f6e8519de6936b33df689937d1fa2b` |
| `stage3_modeling/stage3_3_ridge_tuning/models/ridge_pipeline_2018_m2.joblib` | `fitted_pipeline` | n_samples=990, p=5 | `6755acef3223757c57ae8d742807c5315e3a1ed0f864907bb7f8f55196d708e5` |
| `stage3_modeling/stage3_3_ridge_tuning/cv_results/cv_results_2018_m3.csv` | `cv_results` | 41 × 17 | `2391f28abd42431dfb583c2e0c6f5fdea6aa8a914bdd324dc0023800fd04f3d1` |
| `stage3_modeling/stage3_3_ridge_tuning/models/ridge_pipeline_2018_m3.joblib` | `fitted_pipeline` | n_samples=990, p=8 | `ebe10abebbf4c02c81986f6820d318210e2fcd3e24d89684992482e974be4d4b` |
| `stage3_modeling/stage3_3_ridge_tuning/cv_folds_2021.csv` | `cv_fold_assignments` | 3,963 × 3 | `89fe89f30952307c9231f3765e16cc2540d6eb8fa79a6ea12e24d95660b7efd1` |
| `stage3_modeling/stage3_3_ridge_tuning/cv_results/cv_results_2021_m1.csv` | `cv_results` | 61 × 17 | `d000a2ff3469323b37f6198e3b0eb29614d8a6a1ba0d3eabac1a9c821e68d870` |
| `stage3_modeling/stage3_3_ridge_tuning/models/ridge_pipeline_2021_m1.joblib` | `fitted_pipeline` | n_samples=3,963, p=2 | `31c31b18409fe995191193e7db76d2304c40aff38e30f7570d920c8db102940e` |
| `stage3_modeling/stage3_3_ridge_tuning/cv_results/cv_results_2021_m2.csv` | `cv_results` | 61 × 17 | `b55210c950d167bbea15b4017b7506c826c9142a352537d897450dfc0dc90da0` |
| `stage3_modeling/stage3_3_ridge_tuning/models/ridge_pipeline_2021_m2.joblib` | `fitted_pipeline` | n_samples=3,963, p=5 | `9f7d04b414236a5d2e67df65597ca55ec40616139a638e5ad5a5c50c407ca13c` |
| `stage3_modeling/stage3_3_ridge_tuning/cv_results/cv_results_2021_m3.csv` | `cv_results` | 41 × 17 | `505092ff1171d115e29a256046f49c94c4e1471ed8636fd1818081ad03ed47c4` |
| `stage3_modeling/stage3_3_ridge_tuning/models/ridge_pipeline_2021_m3.joblib` | `fitted_pipeline` | n_samples=3,963, p=8 | `bb4ccbf8fcf526f2d517e88f9bae34e200094ddcdf3eeb78168d356bd5121cc9` |
| `stage3_modeling/stage3_3_ridge_tuning/stage3_3_model_selection_summary.csv` | `model_selection_summary` | 8 × 24 | `e98c67d225601cbf62f1abcdde8d2f42cb6f2d7d79610b10ce3389cc8805765f` |
