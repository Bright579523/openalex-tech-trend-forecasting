# Stage 3.2 Independent Audit Report

**Overall Verdict:** **PASS (22/22 checks passed)**

## 1. Audited Scope & Inputs
- Canonical Stage 3.1 input: `stage3_modeling/stage3_origin_features_targets.csv` (`SHA-256: 9fc15d6ed16ade633547bfca9efca1db92827aa665cbb4509d76c7dae057f488`)
- Stage 2 synchronized panel: `openalex_feasibility_audit/openalex_modeling_panel_1025topics_v2_synchronized.csv` (`SHA-256: f0049cd71f5ba8545c2e3cbb850e036a7b849828321cd23aa1d04771e60d7175`)
- Stage 2 denominators: `openalex_feasibility_audit/all_science_national_denominators_fractional_v2_live_recheck_20261105.csv` (`SHA-256: 9c2d9cccee65c156494b96447ce53045d43e514c74aa10ec9f1c85915b33afce`)
- Stage 3.2 manifest: `stage3_modeling/stage3_2_splits/stage3_2_splits_manifest.json`

## 2. Dataset & RQ3 Summary
| Metric | Experiment A (Test Origin 2018) | Experiment B (Test Origin 2021) |
| --- | ---: | ---: |
| Training Origins | `2015` | `2015–2018` |
| Training Rows | 990 | 3,963 |
| Unique Training Topics | 990 | 993 |
| Test Rows | 992 | 995 |
| RQ3 $Q_{0.80}^{\text{Past}}$ (`linear`) | 0.17627272 | 0.14177449 |
| RQ3 Past HG Excluded ($\ge Q_{0.80}^{\text{Past}}$) | 199 | 199 |
| RQ3 Remaining Pool ($< Q_{0.80}^{\text{Past}}$) | 793 | 796 |
| RQ3 $Q_{0.80}^{\text{Future}}$ (`linear`) | 0.02160447 | 0.06890643 |
| RQ3 Future HG Positives (`>=`) | 159 (20.05%) | 160 (20.10%) |
| Chance Expected Hits@50 | 10.03 | 10.05 |

## 3. Check-by-Check Audit Results
| Check ID | Status | Supporting Evidence |
| --- | :---: | --- |
| `C1_upstream_sha256_integrity` | **PASS** | stage3_1=9fc15d6ed16a..., panel=f0049cd71f5b..., denom=9c2d9cccee65... |
| `C2_stage3_1_shape_and_schema` | **PASS** | rows=7175, cols=42 |
| `C3_manifest_and_all_12_exports_exist` | **PASS** | All 12 CSVs + manifest present |
| `C4_sklearn_version_floor` | **PASS** | scikit-learn==1.8.0 (>= 1.6 required) |
| `C5_2018_row_counts_and_origins` | **PASS** | train=990 (origins=[2015]), test=992 (origin=[2018]), rq3_pool=793 |
| `C6_2018_leakage_free_cutoff` | **PASS** | max_train_origin+3=2018 <= 2018, overlap_keys=0 |
| `C7_2018_sorted_unique_aligned_keys` | **PASS** | All feature/target and pool feature/label pairs strictly sorted, unique, and identical |
| `C8_2018_eligibility_verified` | **PASS** | 100% match with Stage 3.1 eligible==True and global_topic_3yr>=50 |
| `C9_2018_rq3_independent_recompute` | **PASS** | q80_past=0.17627272 (past_ties=0, excl=199), q80_fut=0.02160447, hg_pos=159/793 |
| `C5_2021_row_counts_and_origins` | **PASS** | train=3963 (origins=[2015, 2016, 2017, 2018]), test=995 (origin=[2021]), rq3_pool=796 |
| `C6_2021_leakage_free_cutoff` | **PASS** | max_train_origin+3=2021 <= 2021, overlap_keys=0 |
| `C7_2021_sorted_unique_aligned_keys` | **PASS** | All feature/target and pool feature/label pairs strictly sorted, unique, and identical |
| `C8_2021_eligibility_verified` | **PASS** | 100% match with Stage 3.1 eligible==True and global_topic_3yr>=50 |
| `C9_2021_rq3_independent_recompute` | **PASS** | q80_past=0.14177449 (past_ties=0, excl=199), q80_fut=0.06890643, hg_pos=160/796, linear_idx=636.0, strict_gt=159 |
| `C10_2021_direct_leakage_proof_and_groupkfold` | **PASS** | overlapping_topics_2015_2018=989, max_abs_diff(G2015,M0_2018)=0.00e+00, GroupKFold_val_rows=[796, 790, 796, 789, 792], cross_fold_topic_overlap=[0, 0, 0, 0, 0] |
| `C11_strict_feature_target_separation` | **PASS** | Zero target/label columns in feature CSVs and zero predictor columns in target/label CSVs |
| `C12_zero_missing_nan_inf` | **PASS** | Zero NaN/Inf across all 12 exported CSVs |
| `C13_full_source_scalar_traceability` | **PASS** | checked 167,402 scalar cells across all 12 CSVs; max_abs_diff=0.000e+00 |
| `C14_manifest_hashes_and_relative_paths` | **PASS** | all 12 manifest SHA-256 match disk; machine_absolute_paths=0 |
| `C15_deterministic_repeated_execution` | **PASS** | All 12 CSVs produced byte-for-byte identical SHA-256 on repeated execution |
| `C16_strict_stage3_2_boundary_no_modeling_artifacts` | **PASS** | Zero fitted scalers, Ridge models, CV outputs, predictions, or bootstrap artifacts present |
| `C17_upstream_immutability_post_run` | **PASS** | Stage 3.1 and Stage 2 frozen CSVs remain byte-identical after Stage 3.2 build and audit |

## 4. Exported Artifact Inventory & SHA-256 Hashes
| Artifact | Role | Shape | SHA-256 |
| --- | --- | ---: | --- |
| `stage3_modeling/stage3_2_splits/train_2018_features.csv` | `features` | 990 × 23 | `89b220d14407d6b3b3cde69c2a9fb3ac1a8b6fc92bc0af28411520b708730ce1` |
| `stage3_modeling/stage3_2_splits/train_2018_targets.csv` | `targets` | 990 × 5 | `307c2bfce2dd663a1f133d679d58875ec4060cfb91155469da719b84c2543a7a` |
| `stage3_modeling/stage3_2_splits/test_2018_features.csv` | `features` | 992 × 23 | `d43a96c3d4b3d8133b5553c3e0d3a568d403194d8017efce5a4ba760dd7600fa` |
| `stage3_modeling/stage3_2_splits/test_2018_targets.csv` | `targets` | 992 × 5 | `abfda6a6febae17d8b6533a2eb0fec2b61dd921e745898e8758070cec8fd11ec` |
| `stage3_modeling/stage3_2_splits/rq3_2018_pool_features.csv` | `rq3_features` | 793 × 23 | `772ac2a144c754cc3a8101b4f519067acd72ac55b76c4f45f42d6769f02a0c45` |
| `stage3_modeling/stage3_2_splits/rq3_2018_pool_labels.csv` | `rq3_labels` | 793 × 4 | `bef7b90da7ab194abe8d583fbc7ea5609de50f29dce3c9a647e05582f22e277a` |
| `stage3_modeling/stage3_2_splits/train_2021_features.csv` | `features` | 3,963 × 23 | `cfa72f2ef21142b917feecddef57434bbc998becadd511747aa123cd1c72c8dc` |
| `stage3_modeling/stage3_2_splits/train_2021_targets.csv` | `targets` | 3,963 × 5 | `262d7ee044b5b158fbf844ebf19d71e077bf2ec2fdbd9d339cc6d15a877779da` |
| `stage3_modeling/stage3_2_splits/test_2021_features.csv` | `features` | 995 × 23 | `85751d18950130c1854f96918d62dd24aca0317aaf61ad4098b922535b29ca7a` |
| `stage3_modeling/stage3_2_splits/test_2021_targets.csv` | `targets` | 995 × 5 | `ce5c55b76b95bbf0de6d4669ffc078dde7e1d784d9b920f50be99143831728db` |
| `stage3_modeling/stage3_2_splits/rq3_2021_pool_features.csv` | `rq3_features` | 796 × 23 | `1bae5ee3e15ab521adb657c6388556a771d2b1107c02629533f5117024877528` |
| `stage3_modeling/stage3_2_splits/rq3_2021_pool_labels.csv` | `rq3_labels` | 796 × 4 | `39631ca097e890464c9fe026768e16aa43af09aba4076c69d99adb54b29bf030` |
