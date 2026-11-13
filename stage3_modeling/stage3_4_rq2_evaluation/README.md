# Stage 3.4 — RQ2 Held-Out Test Evaluation (M0–M3 ONLY)

**Status:** **CERTIFIED PASS (14/14 checks passed)** — Audited via `audit_stage3_4_evaluation.py`  
**Audited Git HEAD:** `3688d35711464d42525d27103dc55ff7a38828a7`  
**Scope:** Strictly **RQ2 held-out predictive accuracy (MAE)** on the two predefined test forecast origins (**2018** and **2021**) using the unfitted benchmark **M0** and the frozen **Stage 3.3** `StandardScaler`–`Ridge` pipelines (**M1–M3**).

> **Strict Boundary Adherence:** Stage 3.4 performs **no** model fitting, scaler refitting, alpha retuning, cross-validation, RQ3 candidate-pool Top-50 / Hits@50 evaluation (Stage 3.5), or sensitivity analyses (`M3-LogRCA`, `M2-WC`, `M3-WC` — Stage 3.6). Test Origin 2018 and Test Origin 2021 are evaluated separately and never pooled into a single MAE.

---

## 1. Execution & Independent Audit Commands

```powershell
# Run deterministic Stage 3.4 evaluation & Chapter 5 RQ2 asset generation
python -B stage3_modeling/stage3_4_rq2_evaluation/build_stage3_4_evaluation.py

# Run independent verification suite (C1–C14, including clean temp-dir rerun)
python -B stage3_modeling/stage3_4_rq2_evaluation/audit_stage3_4_evaluation.py
```

Verified runtime environment: Python `3.13.2`, NumPy `2.2.4`, Pandas `2.2.3`, SciPy `1.17.0`, scikit-learn `1.8.0` (`>= 1.6` required), joblib `1.5.3`.

---

## 2. Directory Structure

```text
stage3_modeling/stage3_4_rq2_evaluation/
├── build_stage3_4_evaluation.py              # Deterministic Stage 3.4 RQ2 evaluator
├── audit_stage3_4_evaluation.py              # Independent 14-check verifier (C1–C14)
├── stage3_4_manifest.json                    # Machine-readable audit & SHA-256 manifest
├── stage3_4_audit_report.md                  # 14/14 PASS independent certification report
├── README.md                                 # Stage 3.4 documentation
├── predictions/
│   ├── predictions_test_2018.csv             # 992 eligible topics, M0–M3 predictions & abs errors
│   └── predictions_test_2021.csv             # 995 eligible topics, M0–M3 predictions & abs errors
├── metrics/
│   ├── mae_summary.csv                       # Observed Test MAE & 95% conditional CIs (8 rows)
│   ├── mae_bootstrap_ci.csv                  # Full bootstrap distribution summary for M0–M3
│   ├── paired_mae_differences.csv            # Prespecified nested Delta_MAE comparisons (8 rows)
│   └── paired_mae_bootstrap_ci.csv           # Full paired bootstrap difference stats & % < 0
├── bootstrap/
│   ├── bootstrap_indices_2018.npz            # Shared (5000, 992) int64 index matrix (seed=42)
│   ├── bootstrap_indices_2021.npz            # Shared (5000, 995) int64 index matrix (seed=42)
│   └── bootstrap_metadata.json               # RNG, B=5,000, percentile method & CI caveat
└── thesis_assets/
    ├── README.md                             # Chapter 5 asset summary tables
    ├── scripts/build_stage3_4_thesis_assets.py
    ├── tables/
    │   ├── table_5_1_rq2_mae_performance.{csv,tex}
    │   └── table_5_2_rq2_paired_comparisons.{csv,tex}
    └── figures/
        ├── fig_5_1_rq2_mae_comparison.{pdf,svg,png}
        └── fig_5_2_rq2_paired_mae_differences.{pdf,svg,png}
```

---

## 3. Audited RQ2 Held-Out Results

### A. Held-Out Test MAE & Conditional 95% Bootstrap CIs (`B = 5,000`, `default_rng(42)`, `method="linear"`)

| Experiment (Test Origin) | Target Window | Model | Predictors ($p$) | Tuned $\alpha$ | $N_{\text{test}}$ | Test MAE | 95% Bootstrap CI |
| :--- | :---: | :---: | :---: | ---: | ---: | ---: | :--- |
| Experiment A (`2018`) | 2019–2021 | `M0` | 0 (benchmark) | Unfitted | 992 | `0.171799` | `[0.160387, 0.183531]` |
| Experiment A (`2018`) | 2019–2021 | `M1` | 2 | `1.58489e-07` | 992 | `0.161013` | `[0.151472, 0.171122]` |
| Experiment A (`2018`) | 2019–2021 | `M2` | 5 | `25.1189` | 992 | `0.176906` | `[0.166956, 0.187407]` |
| Experiment A (`2018`) | 2019–2021 | `M3` | 8 | `10` | 992 | `0.177358` | `[0.167315, 0.188036]` |
| Experiment B (`2021`) | 2022–2024 | `M0` | 0 (benchmark) | Unfitted | 995 | `0.165780` | `[0.148233, 0.186594]` |
| Experiment B (`2021`) | 2022–2024 | `M1` | 2 | `1e-06` | 995 | `0.153580` | `[0.139276, 0.170836]` |
| Experiment B (`2021`) | 2022–2024 | `M2` | 5 | `3.98107e-06` | 995 | `0.151909` | `[0.137569, 0.169217]` |
| Experiment B (`2021`) | 2022–2024 | `M3` | 8 | `63.0957` | 995 | `0.151850` | `[0.137535, 0.168942]` |

### B. Prespecified Paired MAE Comparisons ($\Delta\text{MAE} = \text{MAE}_{\text{aug}} - \text{MAE}_{\text{ref}}$; $< 0$ favors augmented model)

| Test Origin | Comparison | Observed $\Delta\text{MAE}$ | 95% Paired Bootstrap CI | Excludes 0? | Interpretation |
| :---: | --- | ---: | :--- | :---: | --- |
| `2018` | `M1 vs M0` | `-0.010786` | `[-0.016473, -0.004856]` | Yes | Lower MAE (error reduction; 95% paired CI strictly < 0) |
| `2018` | `M2 vs M1` | `+0.015893` | `[+0.013204, +0.018685]` | Yes | Higher MAE (error increase; 95% paired CI strictly > 0) |
| `2018` | `M3 vs M2` | `+0.000451` | `[-0.001099, +0.001991]` | No | Slightly higher MAE (error increase; 95% paired CI spans 0) |
| `2018` | `M3 vs M0` | `+0.005559` | `[-0.001003, +0.012126]` | No | Slightly higher MAE (error increase; 95% paired CI spans 0) |
| `2021` | `M1 vs M0` | `-0.012201` | `[-0.019125, -0.005733]` | Yes | Lower MAE (error reduction; 95% paired CI strictly < 0) |
| `2021` | `M2 vs M1` | `-0.001671` | `[-0.002278, -0.001073]` | Yes | Lower MAE (error reduction; 95% paired CI strictly < 0) |
| `2021` | `M3 vs M2` | `-0.000059` | `[-0.000782, +0.000635]` | No | Slightly lower MAE (error reduction; 95% paired CI spans 0) |
| `2021` | `M3 vs M0` | `-0.013930` | `[-0.020898, -0.007315]` | Yes | Lower MAE (error reduction; 95% paired CI strictly < 0) |

---

## 4. Key Scope & Interpretation Caveats
1. **Conditional Bootstrap Uncertainty:** All 95% CIs quantify test-topic sampling uncertainty **conditional on the frozen Stage 3.3 Ridge weights and tuned $\alpha$ values** (no inner retraining or retuning inside bootstrap replicates).
2. **Feature-Representation Test Only:** Comparing `M3` against `M2` evaluates whether adding raw 3-year ratio-of-sums fractional RCA features improves out-of-sample predictive accuracy in the regularized linear hierarchy beyond global and country log-count features (`M2`), rather than making causal claims or claiming raw independence from publication counts.
3. **Origin-Specific Behavior:** Both test origins show strong gains from `M1` over the unfitted `M0` benchmark, divergent `M2 vs M1` country-count effects between Origin 2018 (single training origin 2015, degraded) and Origin 2021 (pooled 2015–2018 training, slight improvement), and near-zero `M3 vs M2` differences spanning `0` in both origins (`+0.000451` and `-0.000059`).
