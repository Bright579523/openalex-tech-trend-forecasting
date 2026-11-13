# Stage 3.4 Independent Audit Report — RQ2 Held-Out Test Evaluation (M0–M3)

**Overall Verdict:** **PASS (14/14 checks passed)**
**Audited Git HEAD:** `3688d35711464d42525d27103dc55ff7a38828a7`
**Execution Timestamp (UTC):** `2026-11-13T21:26:57Z`

## 1. Held-Out RQ2 Forecasting Accuracy (Test MAE & 95% Conditional Bootstrap CI)
| Experiment (Origin) | Model | $p$ | Tuned $\alpha$ | $N_{\text{test}}$ | Test MAE | 95% Bootstrap CI (`linear`) |
| --- | :---: | ---: | ---: | ---: | ---: | --- |
| Experiment A (`2018`) | `M0` | 0 | Unfitted | 992 | 0.171799 | `[0.160387, 0.183531]` |
| Experiment A (`2018`) | `M1` | 2 | `1.58489e-07` | 992 | 0.161013 | `[0.151472, 0.171122]` |
| Experiment A (`2018`) | `M2` | 5 | `25.1189` | 992 | 0.176906 | `[0.166956, 0.187407]` |
| Experiment A (`2018`) | `M3` | 8 | `10` | 992 | 0.177358 | `[0.167315, 0.188036]` |
| Experiment B (`2021`) | `M0` | 0 | Unfitted | 995 | 0.165780 | `[0.148233, 0.186594]` |
| Experiment B (`2021`) | `M1` | 2 | `1e-06` | 995 | 0.153580 | `[0.139276, 0.170836]` |
| Experiment B (`2021`) | `M2` | 5 | `3.98107e-06` | 995 | 0.151909 | `[0.137569, 0.169217]` |
| Experiment B (`2021`) | `M3` | 8 | `63.0957` | 995 | 0.151850 | `[0.137535, 0.168942]` |

## 2. Prespecified Paired MAE Comparisons ($\Delta\text{MAE} = \text{MAE}_{\text{aug}} - \text{MAE}_{\text{ref}}$)
| Test Origin | Comparison | Observed $\Delta\text{MAE}$ | 95% Paired Bootstrap CI | Excludes 0? | Interpretation |
| :---: | --- | ---: | --- | :---: | --- |
| `2018` | `M1 vs M0` | `-0.010786` | `[-0.016473, -0.004856]` | `True` | Lower MAE (error reduction; 95% paired CI strictly < 0) |
| `2018` | `M2 vs M1` | `+0.015893` | `[+0.013204, +0.018685]` | `True` | Higher MAE (error increase; 95% paired CI strictly > 0) |
| `2018` | `M3 vs M2` | `+0.000451` | `[-0.001099, +0.001991]` | `False` | Slightly higher MAE (error increase; 95% paired CI spans 0) |
| `2018` | `M3 vs M0` | `+0.005559` | `[-0.001003, +0.012126]` | `False` | Slightly higher MAE (error increase; 95% paired CI spans 0) |
| `2021` | `M1 vs M0` | `-0.012201` | `[-0.019125, -0.005733]` | `True` | Lower MAE (error reduction; 95% paired CI strictly < 0) |
| `2021` | `M2 vs M1` | `-0.001671` | `[-0.002278, -0.001073]` | `True` | Lower MAE (error reduction; 95% paired CI strictly < 0) |
| `2021` | `M3 vs M2` | `-0.000059` | `[-0.000782, +0.000635]` | `False` | Slightly lower MAE (error reduction; 95% paired CI spans 0) |
| `2021` | `M3 vs M0` | `-0.013930` | `[-0.020898, -0.007315]` | `True` | Lower MAE (error reduction; 95% paired CI strictly < 0) |

## 3. Check-by-Check Audit Results
| Check ID | Status | Supporting Evidence |
| --- | :---: | --- |
| `C1_upstream_stage2_31_32_and_git_checkpoint` | **PASS** | Stage 2, Stage 3.1, all 12 Stage 3.2 CSVs, and checkpoint 17b5f89 verified |
| `C2_stage3_3_pipelines_and_manifest_integrity` | **PASS** | All 15 Stage 3.3 artifacts (6 joblib pipelines, 6 CV CSVs, 2 fold CSVs, summary CSV) match SHA-256 |
| `C3_test_data_counts_keys_alignment_and_finite` | **PASS** | 2018 (N=992) and 2021 (N=995) strictly 1:1 aligned, unique, eligible, and finite |
| `C4_independent_prediction_and_pipeline_parity` | **PASS** | M0 direct + frozen M1–M3 pipelines match saved predictions CSVs; max_abs_diff=0.000e+00 |
| `C5_independent_mae_recompute` | **PASS** | All 8 observed MAEs match independent recomputation; max_abs_diff=0.000e+00 |
| `C6_bootstrap_index_matrices_reproducibility` | **PASS** | Fresh default_rng(42) shapes (5000, 992) and (5000, 995) match saved .npz exactly |
| `C7_independent_bootstrap_mae_ci` | **PASS** | Loop-recomputed B=5,000 MAE CIs (linear percentile) match CSVs; max_abs_diff=0.000e+00 |
| `C8_independent_paired_mae_differences_and_ci` | **PASS** | All 8 paired Delta_MAE differences and 95% CIs match CSVs; max_abs_diff=0.000e+00 |
| `C9_thesis_tables_match_audited_metrics` | **PASS** | Table 5.1 & Table 5.2 CSVs (<=1e-12) and LaTeX formatted intervals match audited metrics 100% |
| `C10_thesis_figures_formats_and_data_parity` | **PASS** | Figure 5.1 & Figure 5.2 (PDF/SVG/PNG) present and rendered SVG labels match audited values 100% |
| `C11_manifest_sha256_and_zero_absolute_paths` | **PASS** | All 20 output hashes & 3 source script hashes verified; zero machine absolute paths |
| `C12_strict_stage3_4_boundary_no_refit_no_rq3_no_sens` | **PASS** | AST verified zero .fit()/tuning/scaler/train/RQ3/sensitivity refs; zero Stage 3.5+ files exist |
| `C13_clean_tempdir_reproducibility` | **PASS** | Clean tempdir rerun produced byte-identical SHA-256 across all 17 CSV/.npz/.tex/SVG/PNG artifacts |
| `C14_post_audit_upstream_immutability` | **PASS** | Stage 2, Stage 3.1, all 12 Stage 3.2 splits, and all 15 Stage 3.3 artifacts remain byte-identical |

## 4. Stage 3.4 Artifact Inventory & SHA-256 Hashes
| Artifact | Role | SHA-256 |
| --- | --- | --- |
| `stage3_modeling/stage3_4_rq2_evaluation/predictions/predictions_test_2018.csv` | `test_predictions` | `add240d22e2bd14ba160d7eba9c01e55973117ae942d65c911b28fa402fd2f1b` |
| `stage3_modeling/stage3_4_rq2_evaluation/bootstrap/bootstrap_indices_2018.npz` | `bootstrap_index_matrix` | `b8a44d46749ee0359043fc00624e6709c73ddf70713e3b0c5895c34c47281c23` |
| `stage3_modeling/stage3_4_rq2_evaluation/predictions/predictions_test_2021.csv` | `test_predictions` | `8dbb481a7f1dba33c19c789dee8708897a27ca6a14f411a718f8bb236f1fde22` |
| `stage3_modeling/stage3_4_rq2_evaluation/bootstrap/bootstrap_indices_2021.npz` | `bootstrap_index_matrix` | `074b6a7eb1ad9a140e532a17816b38484002fd85cfc17adfb9ad6321a9d46284` |
| `stage3_modeling/stage3_4_rq2_evaluation/bootstrap/bootstrap_metadata.json` | `bootstrap_metadata` | `bc7dfcb865448dca5f90bd3cbbf954357d2dc136e79014810fc98e61d4ad95c9` |
| `stage3_modeling/stage3_4_rq2_evaluation/metrics/mae_summary.csv` | `mae_summary` | `7e4bfbc496f9f596ab53ca7629ea6ad1451524ebfa951882d7a9fb8595806be3` |
| `stage3_modeling/stage3_4_rq2_evaluation/metrics/mae_bootstrap_ci.csv` | `mae_bootstrap_ci` | `769bced05b61f305a1c3dd968f11dff5f5730fe48a60e836bcd5d3d391ff3130` |
| `stage3_modeling/stage3_4_rq2_evaluation/metrics/paired_mae_differences.csv` | `paired_mae_differences` | `a48e6717858db46d8cbcc2ac98951d589ea97efbf6964741d0f51f071553291e` |
| `stage3_modeling/stage3_4_rq2_evaluation/metrics/paired_mae_bootstrap_ci.csv` | `paired_mae_bootstrap_ci` | `0d47c7637f04669c980494a6e6b9ea9a5aba698eb4618da4970742f95c90a7ae` |
| `stage3_modeling/stage3_4_rq2_evaluation/thesis_assets/tables/table_5_1_rq2_mae_performance.csv` | `thesis_table_csv` | `6bde2de97073ceab26561eecc1c6ddf756c52d79e7874418b7b49d3a5c4aa1f1` |
| `stage3_modeling/stage3_4_rq2_evaluation/thesis_assets/tables/table_5_1_rq2_mae_performance.tex` | `thesis_table_tex` | `7c9b68a61df4dc445932e978b5d0e404b59c5600d08492b10c3eb1fc1e12aa13` |
| `stage3_modeling/stage3_4_rq2_evaluation/thesis_assets/tables/table_5_2_rq2_paired_comparisons.csv` | `thesis_table_csv` | `b4b44bef7f34c941375ca171552d44901754050b3214785ac156fa8d748a85f1` |
| `stage3_modeling/stage3_4_rq2_evaluation/thesis_assets/tables/table_5_2_rq2_paired_comparisons.tex` | `thesis_table_tex` | `91963bc5715a30d821fd5fd851e302bcc229766a0d696f727e615c540edc90be` |
| `stage3_modeling/stage3_4_rq2_evaluation/thesis_assets/figures/fig_5_1_rq2_mae_comparison.pdf` | `thesis_figure_pdf` | `e3dcd38fe49429f5a10b162f5cd59f3beec83cf842fdc4b902e137ee82146654` |
| `stage3_modeling/stage3_4_rq2_evaluation/thesis_assets/figures/fig_5_1_rq2_mae_comparison.svg` | `thesis_figure_svg` | `33ae1105266e19c4debf796f683bcdc120889e53ff17722e729a0da12793662e` |
| `stage3_modeling/stage3_4_rq2_evaluation/thesis_assets/figures/fig_5_1_rq2_mae_comparison.png` | `thesis_figure_png` | `96847bdce176a0de42bf5c9fa412bf8891bcde0c0be45f6c4a7aaa871f78c5e9` |
| `stage3_modeling/stage3_4_rq2_evaluation/thesis_assets/figures/fig_5_2_rq2_paired_mae_differences.pdf` | `thesis_figure_pdf` | `0b2c630d4360c0d5fbd0656e700388cd723668bdb512373a442a069b3311ddc9` |
| `stage3_modeling/stage3_4_rq2_evaluation/thesis_assets/figures/fig_5_2_rq2_paired_mae_differences.svg` | `thesis_figure_svg` | `af147b21181a116593128227a6bd7f0701b24246c2ab6fc62da9a3e19bbc263e` |
| `stage3_modeling/stage3_4_rq2_evaluation/thesis_assets/figures/fig_5_2_rq2_paired_mae_differences.png` | `thesis_figure_png` | `244b4f657078764e9261704d1242eea5b674cbbbdc83f4b1e651b6735f3c62b0` |
| `stage3_modeling/stage3_4_rq2_evaluation/thesis_assets/README.md` | `thesis_assets_readme` | `3497b4f009c7222757dceea6b720bd5267c964bd7f7e1665a10d8ab1367e8ce6` |
