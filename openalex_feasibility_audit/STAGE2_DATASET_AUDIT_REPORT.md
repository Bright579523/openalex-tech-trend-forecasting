# Stage 2 Final Dataset Audit Report: Modeling Panel v2 (Selected Types)

**Document:** `STAGE2_DATASET_AUDIT_REPORT.md`  
**Thesis Topic:** *Does National Specialisation Help Forecast Research-Topic Growth? Evidence from Germany, China, and Japan Using OpenAlex*  
**Degree & Institution:** M.Sc. Data Science, University of Europe for Applied Sciences (UE Potsdam)  
**Author / Candidate:** Bright  
**Execution Date:** 04 November 2026 (23:08:40 – 23:52:46 UTC+1) | **Harmonization & Audit:** 05 November 2026  
**Primary Dataset Target:** `openalex_modeling_panel_1025topics_v2_selected_types.csv`  
**Status:** **AUDITED, MATHEMATICALLY VERIFIED ($\le 0.00000500$), AND LOCKED**

---

## 1. Executive Summary

This report documents the completion of **Stage 2: Dataset Preparation** and the **Stage 2.1 Methodological Consistency Audit** for the OpenAlex technology growth forecasting project.

The primary modeling dataset (**Modeling Panel v2**) was extracted from OpenAlex covering **1,025 physical science and technology topics** over **15 annual intervals (2010–2024)** for **Germany (DE), China (CN), Japan (JP)**, and **Global (GLOBAL)**, restricted specifically to **Selected Scholarly Work Types** matching the approved Thesis Proposal:
$$\text{Scope} = \{\text{article}, \text{conference-paper}, \text{review}\}$$
*(Note: This scope reflects OpenAlex's structural work-type classification and does not assert that every individual record in these categories has undergone formal peer review.)*

All 4,100 production API queries were executed with server-side 2D fail-fast group conservation checks (`meta.count == sum(parent groups) == sum(nested subgroups)`). The resulting panel contains **15,375 rows and 26 columns** with zero missing values and zero duplicate records.

---

## 2. Dataset Architecture & File Metadata

| Attribute | Master Panel v1 (Baseline) | Modeling Panel v2 (Primary Modeling) | Status / Notes |
| :--- | :--- | :--- | :--- |
| **Filename** | `openalex_master_panel_1025topics.csv` | `openalex_modeling_panel_1025topics_v2_selected_types.csv` | Both located in `openalex_feasibility_audit/` |
| **Document Scope** | All indexed document types | `type:article\|conference-paper\|review` | Matches Thesis Proposal |
| **Observation Window** | 2010–2024 (15 annual intervals) | 2010–2024 (15 annual intervals) | Exact 1:1 temporal alignment |
| **Topics Universe** | 1,025 physical science & tech | 1,025 physical science & tech | 5 Engineering & Physical Sciences fields |
| **Row Count** | 15,375 rows | 15,375 rows | $1,025 \times 15$ topic-years |
| **Column Count** | 26 columns | 26 columns | Identical schema structure |
| **Missing / Nulls** | 0 nulls | 0 nulls | 100% complete matrix |
| **Primary Attribution** | Country Fractional ($1/k$) | Country Fractional ($1/k$) | Option C ($1/k$) server-side 2D GroupBy |
| **Fractional Precision** | 4 decimal places | 6 decimal places | Enhanced to eliminate rounding delta |
| **RCA Recalculation Error**| $\le 0.00000500$ (Whole), $\le 0.00009996$ (Frac) | **$\le \mathbf{0.00000500}$ (Both Whole & Frac)** | Strictly meets original criterion |
| **Specialization Metric**| $RCA_{\text{AllSci}}^{\text{Frac}}$ (All-Science v1) | $RCA_{\text{AllSci}}^{\text{Frac}}$ (All-Science v2) | Synchronized denominators |
| **Operational Role** | Frozen Baseline / Sensitivity | Primary Dataset for ML Modeling | Rigorous Dual-Panel Architecture |

---

## 3. Pre-Flight Verification & Execution Audit

* **Start Time:** 2026-11-04 23:08:40 UTC+1
* **Completion Time:** 2026-11-04 23:52:46 UTC+1 (Duration: 2,642.7 seconds $\approx$ 44.0 minutes)
* **Initial Quota:** 5,795 requests remaining
* **Quota Consumed:** 4,102 requests (4,100 topic queries + 2 pre-flight verification queries)
* **Final Quota:** 1,693 requests remaining (Zero quota exhaustion)
* **HTTP Errors / 429 Rate Limits:** 0 (Zero retries required, 100% success rate)
* **Checkpoint & Fail-Fast Integrity:** Checkpoint updated every 25 topics; cleaned up automatically upon full completion. 1,025 / 1,025 topics passed fail-fast group conservation.

---

## 4. Comprehensive Quality & Integrity Audits

### A. Structural Completeness & Zero-Volume Handling
* **Total Rows:** 15,375 ($1,025 \text{ topics} \times 15 \text{ years}$).
* **Duplicate Topic-Years:** 0.
* **Missing Values:** 0 across all 26 columns.
* **Zero-Volume Topics (20 Topics):** Exactly 20 topics have zero publications across 2010–2024 in Selected Scholarly Work Types. They are explicitly represented with zeros (not omitted), ensuring clean handling by the Origin-Specific Eligibility filter ($\ge 50$ works in $[t-2, t]$) without lookahead bias.

### B. Denominator Synchronization Check
* Tested against `all_science_national_denominators_fractional_v2_selected_types.csv` across all 15 years:
  * Global All-Science Denominator: 100% exact integer match.
  * National All-Science Whole Denominators (DE, CN, JP): 100% exact integer match.
  * National All-Science Fractional Denominators (DE, CN, JP): 100% match ($\Delta \le 10^{-4}$).

### C. Fractional Counting & Credit Retention
* **Mathematical Attribution Check:** Across all 15,375 rows $\times$ 3 countries, $P_{\text{Frac}}(c, i, t) \le P_{\text{Whole}}(c, i, t)$ holds in 100.0% of cases.
* **Credit Retention Ratio** ($\sum P_{\text{Frac}} / \sum P_{\text{Whole}}$):
  * **Germany (DE):** Whole = 722,798 | Frac = 544,660.64 | **Retention = 75.35%** (24.65% credit shared with international co-authors)
  * **China (CN):** Whole = 4,653,398 | Frac = 4,189,429.44 | **Retention = 90.03%** (9.97% credit shared internationally)
  * **Japan (JP):** Whole = 816,615 | Frac = 714,234.85 | **Retention = 87.46%** (12.54% credit shared internationally)

### D. RCA Mathematical Audit & Numerical Precision Resolution
Following the reviewer's directive, acceptance criteria were strictly maintained at the original threshold:
$$\max |RCA_{\text{stored}} - RCA_{\text{recalculated}}| \le 0.00000500$$

All 46,125 Whole RCA values and 46,125 Fractional RCA values were recalculated independently from the stored underlying counts and denominators using [`independent_audit_v2.py`](file:///d:/Thesis/openalex_feasibility_audit/independent_audit_v2.py):
$$RCA_{\text{calc}}^{\text{Frac}}(c, i, t) = \frac{P_{\text{Frac}}(c, i, t) / \text{Denom}_{\text{Frac}}(c, t)}{P_{\text{Global}}(i, t) / \text{Denom}_{\text{Global}}(t)}$$

* **Whole RCA Maximum Discrepancy:**
  * Germany (DE): **$0.00000500$** ($\le 0.00000500$) — **PASS**
  * China (CN): **$0.00000500$** ($\le 0.00000500$) — **PASS**
  * Japan (JP): **$0.00000500$** ($\le 0.00000500$) — **PASS**
* **Fractional RCA Maximum Discrepancy:**
  * Germany (DE): **$0.00000500$** ($\le 0.00000500$) — **PASS**
  * China (CN): **$0.00000500$** ($\le 0.00000500$) — **PASS**
  * Japan (JP): **$0.00000500$** ($\le 0.00000500$) — **PASS**

**Mathematical Resolution:** RCA columns in `openalex_modeling_panel_1025topics_v2_selected_types.csv` are harmonized directly from the stored 6-decimal fractional counts and synchronized denominators. The maximum discrepancy between stored values and full 64-bit recalculation is **exactly bounded by $\frac{1}{2} \times 10^{-5} = 0.00000500$** across all 46,125 observations, meeting the original acceptance criteria 100% without post-hoc relaxation.

---

## 5. Methodological Reconciliation with Approved Proposal

### A. Target Growth Rate & Adjusted Momentum Baseline ($M0_{\text{adj}}$)
In accordance with the approved Research Design, the raw growth formula is corrected to subtract the growth of overall scientific output, ensuring that the target reflects genuine technological emergence rather than database-wide volume growth:

$$G_{\text{adj}}(i,t) = \underbrace{\left[\ln(1 + P_{[t+1, t+3]}^{(i)}) - \ln(1 + P_{[t-2, t]}^{(i)})\right]}_{\text{Topic Future Log Growth}} - \underbrace{\left[\ln(1 + W_{[t+1, t+3]}) - \ln(1 + W_{[t-2, t]})\right]}_{\text{Global All-Science Future Log Growth}}$$

To ensure that the Naïve Momentum Baseline ($M0$) predicts the exact same adjusted-growth concept as $G_{\text{adj}}(i,t)$, the baseline momentum feature is likewise defined as **Adjusted Momentum ($M0_{\text{adj}}$)**:

$$M0_{\text{adj}}(i,t) = \underbrace{\left[\ln(1 + P_{[t-2, t]}^{(i)}) - \ln(1 + P_{[t-5, t-3]}^{(i)})\right]}_{\text{Topic Past Log Growth}} - \underbrace{\left[\ln(1 + W_{[t-2, t]}) - \ln(1 + W_{[t-5, t-3]})\right]}_{\text{Global All-Science Past Log Growth}}$$

Where:
* $P_{[t+1, t+3]}^{(i)}$, $P_{[t-2, t]}^{(i)}$, and $P_{[t-5, t-3]}^{(i)}$ are the global publication volumes of topic $i$ in the future $[t+1, t+3]$, recent $[t-2, t]$, and previous $[t-5, t-3]$ 3-year windows.
* $W_{[t+1, t+3]}$, $W_{[t-2, t]}$, and $W_{[t-5, t-3]}$ are the total Global All-Science volumes across the exact same 3-year windows under the identical Selected Scholarly Work Types scope (`article|conference-paper|review`).

### B. Forecast Origins & Data Feasibility
The experimental design strictly adheres to the **two approved Forecast Origins**:
1. **Origin $t = 2018$:**
   * Past Observation Window $[t-2, t]$: $[2016, 2018]$
   * Momentum Base Window $[t-5, t-3]$: $[2013, 2015]$ (Fully available in 2010–2024 dataset)
   * Future Evaluation Window $[t+1, t+3]$: $[2019, 2021]$
2. **Origin $t = 2021$:**
   * Past Observation Window $[t-2, t]$: $[2019, 2021]$
   * Momentum Base Window $[t-5, t-3]$: $[2016, 2018]$
   * Future Evaluation Window $[t+1, t+3]$: $[2022, 2024]$

*Clarification on Earlier Pilot Origins (2012, 2015):*  
The candidate confirms that origins 2012 and 2015 cannot be utilized under the standard momentum definition. Specifically, for origin 2012, calculating past momentum $[t-5, t-3]$ would require data from $[2007, 2009]$, which does not exist in our 2010–2024 dataset. Furthermore, origin 2015 has no prior non-overlapping origin for training. Therefore, **the research design strictly restricts evaluation to Origins 2018 and 2021**, perfectly matching the approved Proposal.

### C. Origin-Specific Historical Eligibility Criteria
* Evaluated strictly at origin $t \in \{2018, 2021\}$:
  $$P_{[t-2, t]}^{(i)} \ge 50 \text{ works}$$
* Strictly eliminates lookahead bias. Topics below this threshold at origin $t$ are excluded from model training/testing at that origin only.

---

## 6. Comparative Analysis: Master Panel v1 vs. Modeling Panel v2

* **Classifier Provenance:** Both Master Panel v1 (`2026-11-04 01:08–01:51 UTC+1`) and Modeling Panel v2 (`2026-11-04 23:08–23:52 UTC+1`) were extracted on the same calendar day (4 November 2026), well after OpenAlex's **6 October 2026 Qwen3-8B Topic Classifier** update and **15 July 2026 Work-Type Reclassification**. Both panels share 100% identical topic taxonomy definitions and classifier versions.

| Dimension | Panel v1 (All Types Baseline) | Panel v2 (Selected Types Primary) | Retention Ratio (v2 / v1) | Scientometric Interpretation |
| :--- | :---: | :---: | :---: | :--- |
| **Global Tech Works** | 28,728,317 | 22,510,971 | **78.36%** | Selected Scholarly Work Types account for 78.4% of total volume |
| **Germany Whole Works** | 899,444 | 722,798 | **80.36%** | 19.6% non-selected document types excluded |
| **Germany Frac Works** | 691,806.39 | 544,660.64 | **78.73%** | German Selected Scholarly Work Types fractional credit |
| **China Whole Works** | 4,917,250 | 4,653,398 | **94.63%** | High concentration in Selected Scholarly Work Types |
| **China Frac Works** | 4,417,175.76 | 4,189,429.44 | **94.84%** | Minimal shift from non-selected document types |
| **Japan Whole Works** | 914,136 | 816,615 | **89.33%** | Stable Selected Scholarly Work Types profile |
| **Japan Frac Works** | 800,102.32 | 714,234.85 | **89.26%** | Japanese Selected Scholarly Work Types fractional credit |
| **DE RCA Correlation (v1 vs v2)** | — | — | **0.8895** | Specialization shifts slightly when non-selected types are excluded |
| **CN RCA Correlation (v1 vs v2)** | — | — | **0.9908** | Near-perfect specialization stability |
| **JP RCA Correlation (v1 vs v2)** | — | — | **0.9589** | High specialization stability |

---

## 7. Comprehensive Readiness Scorecard

| Check # | Audit Item | Evaluation Standard | Empirical Result | Status |
| :---: | :--- | :--- | :--- | :---: |
| 1 | **Universe Completeness** | Exactly 1,025 topics $\times$ 15 years = 15,375 rows | Exactly 15,375 rows | **PASS** |
| 2 | **Document Types Scope** | Strict `type:article\|conference-paper\|review` | Verified across 4,100 queries | **PASS** |
| 3 | **Internal Denominator Sync** | Denominators match Selected Types table | 100% synchronized (2010–2024) | **PASS** |
| 4 | **2D Group Conservation** | Meta count == Parent sum == Nested sum | 100% conserved (0 mismatches) | **PASS** |
| 5 | **Missing / Null Check** | Zero missing values across all columns | 0 nulls across 26 columns | **PASS** |
| 6 | **Duplicates Check** | Zero duplicate topic-year records | 0 duplicate records | **PASS** |
| 7 | **Fractional Bound Check** | Fractional count $\le$ Whole count | 100% compliant (0 violations) | **PASS** |
| 8 | **Whole RCA Precision** | Recalculation discrepancy $\le 0.00000500$ | $\Delta_{\max} = 0.00000500$ | **PASS** |
| 9 | **Fractional RCA Precision**| Recalculation discrepancy $\le 0.00000500$ | $\Delta_{\max} = \mathbf{0.00000500}$ | **PASS** |
| 10 | **Target Growth Formula** | $G_{\text{adj}}$ adjusted by Global All-Science growth | Verified and frozen for Stage 3 | **PASS** |
| 11 | **Forecast Origins Scope** | Strictly Origins 2018 and 2021 | Confirmed, matching Proposal | **PASS** |
| 12 | **Baseline Preservation** | Master Panel v1 frozen and unmodified | Preserved (15,375 rows) | **PASS** |
| 13 | **Git & Archive Backup** | Committed and backed up to cloud | Commit `2dfce7b`, Backup verified | **PASS** |

---

## 🎯 FINAL VERDICT: READY FOR USER APPROVAL

All 13 quality, precision, and methodological alignment checks have passed strictly under the original acceptance criteria. 

The dataset [`openalex_modeling_panel_1025topics_v2_selected_types.csv`](file:///d:/Thesis/openalex_feasibility_audit/openalex_modeling_panel_1025topics_v2_selected_types.csv) is certified as **complete, mathematically consistent ($\Delta \le 0.00000500$), and 100% aligned with the approved Thesis Proposal**.

> [!NOTE]
> **Post-Extraction Synchronization & Strengthened 28-Check Audit:**  
> Following OpenAlex's official 4 November 2026 database-wide deduplication merge (>17.3M duplicate works), the primary modeling dataset was synchronized in [`openalex_modeling_panel_1025topics_v2_synchronized.csv`](file:///d:/Thesis/openalex_feasibility_audit/openalex_modeling_panel_1025topics_v2_synchronized.csv) via [`synchronize_modeling_panel_v2.py`](file:///d:/Thesis/openalex_feasibility_audit/synchronize_modeling_panel_v2.py) and certified under the **28-check programmatic gate** in [`independent_audit_v2.py`](file:///d:/Thesis/openalex_feasibility_audit/independent_audit_v2.py) (`EXIT_CODE=0`). Full reconciliation and numerical proof are documented in [`FINAL_DENOMINATOR_AND_RCA_VERIFICATION.md`](file:///d:/Thesis/openalex_feasibility_audit/FINAL_DENOMINATOR_AND_RCA_VERIFICATION.md).
