# Stage 3.1 Feature and Target Construction — Independent Audit Report

> **Audit Timestamp (UTC):** `2026-11-12T01:05:50Z`  
> **Git HEAD:** `ffc17163b0a914d62fa4861a0f9e9a5c3e8eb382` *(checkpoint `ffc1716` verified ancestor: `True`)*  
> **Final Audit Verdict:** **`PASS`** (`19 / 19` checks PASS)

---

## 1. Input & Output Cryptographic Integrity

| Artifact | Role | Dimensions | SHA-256 |
| :--- | :--- | :---: | :--- |
| `openalex_modeling_panel_1025topics_v2_synchronized.csv` | Frozen Primary Panel v2 | `15,375 x 26` | `f0049cd71f5ba8545c2e3cbb850e036a7b849828321cd23aa1d04771e60d7175` |
| `all_science_national_denominators_fractional_v2_live_recheck_20261105.csv` | Frozen Synchronized Denoms | `15 x 10` | `9c2d9cccee65c156494b96447ce53045d43e514c74aa10ec9f1c85915b33afce` |
| `stage3_origin_features_targets.csv` | Stage 3.1 Canonical Table | `7,175 x 42` | `9fc15d6ed16ade633547bfca9efca1db92827aa665cbb4509d76c7dae057f488` |

---

## 2. Independently Verified Origin Eligibility Counts (`sum(global_count over [t-2, t]) >= 50`)

| Forecast Origin ($t$) | Momentum Base $[t-5,t-3]$ | Recent Feature Window $[t-2,t]$ | Target Window $[t+1,t+3]$ | Total Topics | Eligible (`True`) | Ineligible (`False`) | Coverage |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **2015** | `2010-2012` | `2013-2015` | `2016-2018` | `1,025` | **`990`** | `35` | `96.59%` |
| **2016** | `2011-2013` | `2014-2016` | `2017-2019` | `1,025` | **`990`** | `35` | `96.59%` |
| **2017** | `2012-2014` | `2015-2017` | `2018-2020` | `1,025` | **`991`** | `34` | `96.68%` |
| **2018** | `2013-2015` | `2016-2018` | `2019-2021` | `1,025` | **`992`** | `33` | `96.78%` |
| **2019** | `2014-2016` | `2017-2019` | `2020-2022` | `1,025` | **`994`** | `31` | `96.98%` |
| **2020** | `2015-2017` | `2018-2020` | `2021-2023` | `1,025` | **`995`** | `30` | `97.07%` |
| **2021** | `2016-2018` | `2019-2021` | `2022-2024` | `1,025` | **`995`** | `30` | `97.07%` |

---

## 3. Complete Validation Checklist

| # | Check Name | Verdict | Observed Evidence |
| :---: | :--- | :---: | :--- |
| 1 | Git Checkpoint Ancestor (ffc1716) | **`PASS`** | `HEAD=ffc17163b0a914d62fa4861a0f9e9a5c3e8eb382` |
| 2 | Dependency Constraint (scikit-learn >= 1.6) | **`PASS`** | `scikit-learn=1.8.0, numpy=2.2.4, pandas=2.2.3` |
| 3 | Required Stage 2 & Stage 3.1 Files Exist | **`PASS`** | `All 4 files present=True` |
| 4 | Frozen Panel SHA-256 Unchanged | **`PASS`** | `f0049cd71f5ba8545c2e3cbb850e036a7b849828321cd23aa1d04771e60d7175` |
| 5 | Frozen Denoms SHA-256 Unchanged | **`PASS`** | `9c2d9cccee65c156494b96447ce53045d43e514c74aa10ec9f1c85915b33afce` |
| 6 | Output CSV SHA-256 Matches Manifest | **`PASS`** | `9fc15d6ed16ade633547bfca9efca1db92827aa665cbb4509d76c7dae057f488` |
| 7 | Output Dimensions (7,175 x 42) | **`PASS`** | `shape=(7175, 42)` |
| 8 | Forecast Origins == 2015..2021 | **`PASS`** | `[2015, 2016, 2017, 2018, 2019, 2020, 2021]` |
| 9 | 1,025 Unique Topics per Origin & Zero Duplicates | **`PASS`** | `duplicates=0, per_origin={2015: 1025, 2016: 1025, 2017: 1025, 2018: 1025, 2019: 1025, 2020: 1025, 2021: 1025}` |
| 10 | Balanced 5-Field Taxonomy Counts Across All Origins | **`PASS`** | `{'Engineering': 560, 'Computer Science': 302, 'Materials Science': 123, 'Energy': 27, 'Chemical Engineering': 13}` |
| 11 | Window All-Science Sums W_[a,b] Match Locked Spec | **`PASS`** | `{(2010, 2012): 17486265, (2013, 2015): 19552552, (2016, 2018): 19796237, (2019, 2021): 20398266, (2022, 2024): 20127715}` |
| 12 | Independent Scalar Recomputation (All 7,175 Rows) | **`PASS`** | `meta_err=0, bool_err=0, int_err=0, max_model_abs_diff=2.665e-15 (rca_frac_cn_3yr), max_sum_rel_diff=2.217e-16 (frac_jp_3yr)` |
| 13 | RCA Uses Ratio-of-Sums (Not Annual Mean) & Is Raw/Unwinsorized | **`PASS`** | `max|RoS - MeanAnnual|(2018 DE)=0.5434, max_raw_JP_RCA=12.4237, max|RCA - ln(1+RCA)|=7.0299` |
| 14 | Check A: Identity G_adj(i,t) == M0_adj(i,t+3) < 1e-12 | **`PASS`** | `2015->2018: all=0.00e+00, elig=0.00e+00 (n=989); 2016->2019: all=0.00e+00, elig=0.00e+00 (n=990); 2017->2020: all=0.00e+00, elig=0.00e+00 (n=991); 2018->2021: all=0.00e+00, elig=0.00e+00 (n=992)` |
| 15 | Check B: Forward-Year Poisoning Invariance & Schema Leakage Gate | **`PASS`** | `scalar_invariance_diff=0.00e+00, max_csv_vs_poison_diff=2.66e-15, min_target_diff=5.94, schema_disjoint=True` |
| 16 | Check C: Origin Eligibility (>= 50 Works in [t-2,t]) | **`PASS`** | `2015: 990/1025, 2016: 990/1025, 2017: 991/1025, 2018: 992/1025, 2019: 994/1025, 2020: 995/1025, 2021: 995/1025` |
| 17 | Check D: Zero Nulls/Infs & Valid Fractional/Whole/RCA Bounds | **`PASS`** | `nulls=0, inf_all=0, inf_elig=0, bounds_ok=True` |
| 18 | Check E: Feature Lengths, Progressive Hierarchy & Consistent Counting Basis | **`PASS`** | `counts_ok=True, hierarchy_ok=True, wc_denom_strictly_paired=True` |
| 19 | Check F: Post-Audit Frozen Source Datasets Byte-for-Byte Preserved | **`PASS`** | `panel_ok=True, denom_ok=True` |

---

## 4. Model Feature Sets & Schema Isolation Verified

| Model | Feature Count | Columns |
| :--- | :---: | :--- |
| `M0` | `0` | *Unfitted benchmark (`m0_adj` direct prediction)* |
| `M1` | `2` | `m0_adj`, `ln_global_topic_3yr` |
| `M2` | `5` | `m0_adj`, `ln_global_topic_3yr`, `ln_frac_de_3yr`, `ln_frac_cn_3yr`, `ln_frac_jp_3yr` |
| `M3` | `8` | `m0_adj`, `ln_global_topic_3yr`, `ln_frac_de_3yr`, `ln_frac_cn_3yr`, `ln_frac_jp_3yr`, `rca_frac_de_3yr`, `rca_frac_cn_3yr`, `rca_frac_jp_3yr` |
| `M3-LogRCA` | `8` | `m0_adj`, `ln_global_topic_3yr`, `ln_frac_de_3yr`, `ln_frac_cn_3yr`, `ln_frac_jp_3yr`, `ln_rca_frac_de_3yr`, `ln_rca_frac_cn_3yr`, `ln_rca_frac_jp_3yr` |
| `M2-WC` | `5` | `m0_adj`, `ln_global_topic_3yr`, `ln_whole_de_3yr`, `ln_whole_cn_3yr`, `ln_whole_jp_3yr` |
| `M3-WC` | `8` | `m0_adj`, `ln_global_topic_3yr`, `ln_whole_de_3yr`, `ln_whole_cn_3yr`, `ln_whole_jp_3yr`, `rca_whole_de_3yr`, `rca_whole_cn_3yr`, `rca_whole_jp_3yr` |

* **Target column:** `g_adj`
* **Identifier columns:** `forecast_origin`, `topic_id`, `topic_name`, `field_name`, `subfield_name`, `eligible`
* **Scope confirmation:** Stage 3.1 only (no train/test splitting, no Ridge fitting, no scaling, no CV, no predictions, no bootstrap).
