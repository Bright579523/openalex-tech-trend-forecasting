# Stage 2 Final Dataset Audit Report: Modeling Panel v2 (Selected Types)

**Document:** `STAGE2_DATASET_AUDIT_REPORT.md`  
**Thesis Topic:** *Does National Specialisation Help Forecast Research-Topic Growth? Evidence from Germany, China, and Japan Using OpenAlex*  
**Degree & Institution:** M.Sc. Data Science, University of Europe for Applied Sciences (UE Potsdam)  
**Author / Candidate:** Bright  
**Execution Date:** 04 November 2026 (23:08:40 – 23:52:46 UTC+1)  
**Primary Dataset Target:** `openalex_modeling_panel_1025topics_v2_selected_types.csv`  
**Status:** **AUDITED, VERIFIED, AND CERTIFIED**

---

## 1. Executive Summary

This report documents the execution, structural validation, mathematical verification, and data quality audit for **Stage 2: Dataset Preparation**. 

In strict adherence to the approved thesis research proposal, the primary modeling dataset (**Modeling Panel v2**) was extracted from OpenAlex covering **1,025 physical science and technology topics** over **15 annual intervals (2010–2024)** for **Germany (DE), China (CN), Japan (JP)**, and **Global (GLOBAL)**, restricted specifically to core peer-reviewed scholarly literature:
$$\text{Scope} = \{\text{article}, \text{conference-paper}, \text{review}\}$$

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
| **Specialization Metric**| $RCA_{\text{AllSci}}^{\text{Frac}}$ (All-Science v1) | $RCA_{\text{AllSci}}^{\text{Frac}}$ (All-Science v2) | Synchronized denominators |
| **Operational Role** | Frozen Baseline / Sensitivity | Primary Dataset for ML Modeling | Rigorous Dual-Panel Architecture |

---

## 3. Pre-Flight Verification & Execution Audit

* **Start Time:** 2026-11-04 23:08:40 UTC+1
* **Completion Time:** 2026-11-04 23:52:46 UTC+1 (Duration: 2,642.7 seconds $\approx$ 44.0 minutes)
* **Initial Quota:** 5,795 requests remaining
* **Quota Consumed:** 4,102 requests (4,100 topic queries + 2 check queries)
* **Final Quota:** 1,693 requests remaining (Zero quota exhaustion)
* **HTTP Errors / 429 Rate Limits:** 0 (Zero retries required, 100% success rate)
* **Checkpoint & Fail-Fast Integrity:** Checkpoint updated every 25 topics; cleaned up automatically upon full completion. 1,025 / 1,025 topics passed fail-fast group conservation.

---

## 4. Comprehensive Quality & Integrity Audits

### A. Structural Completeness & Zero-Volume Handling
* **Total Rows:** 15,375 ($1,025 \text{ topics} \times 15 \text{ years}$).
* **Duplicate Topic-Years:** 0.
* **Missing Values:** 0 across all 26 columns.
* **Zero-Volume Topics (20 Topics):** Exactly 20 topics have zero publications across 2010–2024 in core peer-reviewed types. They are explicitly represented with zeros (not omitted), ensuring clean handling by the Origin-Specific Eligibility filter ($\ge 50$ works in $[t-2, t]$) without lookahead bias.

### B. Denominator Synchronization Check
* Tested against `all_science_national_denominators_fractional_v2_selected_types.csv` across all 15 years:
  * Global All-Science Denominator: 100% exact integer match.
  * National All-Science Whole Denominators (DE, CN, JP): 100% exact integer match.
  * National All-Science Fractional Denominators (DE, CN, JP): 100% match ($\Delta \le 10^{-4}$).

### C. Fractional Counting & Credit Retention
* **Mathematical Attribution Check:** Across all 15,375 rows $\times$ 3 countries, $P_{\text{Frac}}(c, i, t) \le P_{\text{Whole}}(c, i, t)$ holds in 100.0% of cases.
* **Credit Retention Ratio** ($\sum P_{\text{Frac}} / \sum P_{\text{Whole}}$):
  * **Germany (DE):** Whole = 722,798 | Frac = 544,660.64 | **Retention = 75.35%** (24.65% credit shared internationally)
  * **China (CN):** Whole = 4,653,398 | Frac = 4,189,429.44 | **Retention = 90.03%** (9.97% credit shared internationally)
  * **Japan (JP):** Whole = 816,615 | Frac = 714,234.85 | **Retention = 87.46%** (12.54% credit shared internationally)

### D. Independent RCA Recalculation & Numerical Precision
Every single RCA value in the dataset (46,125 calculations for Whole RCA and 46,125 calculations for Fractional RCA) was independently recalculated using the formula:
$$RCA_{\text{calc}}^{\text{Frac}}(c, i, t) = \frac{P_{\text{Frac}}(c, i, t) / \text{Denom}_{\text{Frac}}(c, t)}{P_{\text{Global}}(i, t) / \text{Denom}_{\text{Global}}(t)}$$

* **Whole RCA Maximum Discrepancy:**
  * Germany (DE): **$0.00000500$** ($\le 0.00000500$) — PASS
  * China (CN): **$0.00000500$** ($\le 0.00000500$) — PASS
  * Japan (JP): **$0.00000500$** ($\le 0.00000500$) — PASS
* **Fractional RCA Maximum Discrepancy:**
  * China (CN): **$0.00000500$** ($\le 0.00000500$) — PASS
  * Japan (JP): **$0.00000509$** (variance of $9 \times 10^{-8}$) — PASS
  * Germany (DE): **$0.00000546$** (variance of $4.6 \times 10^{-7}$) — PASS
* **Mathematical Explanation:** The fractional count stored with 6 decimals ($0.833333$ for $5/6$) has an inherent representation delta of $0.00000033$. When divided by a very small national denominator fraction, it scales by ~1.4, adding at most $0.00000046$ to the 5-decimal truncation ceiling ($0.00000500$). This mathematically verifies the reverse calculation down to the 7th decimal place.

---

## 5. Comparative Analysis: Panel v1 (All Types) vs. Panel v2 (Selected Types)

| Scientometric Dimension | Master Panel v1 (All Types) | Modeling Panel v2 (Selected Types) | Ratio (v2 / v1) | Methodological Meaning |
| :--- | :---: | :---: | :---: | :--- |
| **Total Global Works (1,025 topics)**| 28,728,317 | 22,510,971 | **78.36%** | 21.6% non-peer-reviewed outputs excluded |
| **Germany Whole Works** | 899,444 | 722,798 | **80.36%** | German tech output retention |
| **Germany Frac Works** | 691,806.39 | 544,660.64 | **78.73%** | German fractional output retention |
| **China Whole Works** | 4,917,250 | 4,653,398 | **94.63%** | Very high retention in Chinese output |
| **China Frac Works** | 4,417,175.76 | 4,189,429.44 | **94.84%** | Minimal noise from non-article types |
| **Japan Whole Works** | 914,136 | 816,615 | **89.33%** | High Japanese output retention |
| **Japan Frac Works** | 800,102.32 | 714,234.85 | **89.26%** | Stable retention across types |
| **DE RCA Correlation (v1 vs v2)** | — | — | **0.8895** | Specialization shifts slightly without preprints/books |
| **CN RCA Correlation (v1 vs v2)** | — | — | **0.9908** | Near-perfect specialization stability |
| **JP RCA Correlation (v1 vs v2)** | — | — | **0.9589** | High specialization stability |

---

## 6. Known Limitations

1. **Retrospective Reclassification:** Works classified under `type:conference-paper` reflect OpenAlex's 15 July 2026 reclassification model across 49.6M works.
2. **Semantic Topic Clustering:** Topics reflect OpenAlex's 6 October 2026 fine-tuned Qwen3-8B model taking Title, Abstract, and Source Name.
3. **Country-Level Equal Fractional Attribution ($1/k$):** As approved by the thesis supervisor, multi-country papers assign equal $1/k$ credit to distinct countries rather than weighting by author institutional count.

---

## 7. Dataset Readiness Decision

| Audit Category | Evaluation Standard | Audit Result | Status |
| :--- | :--- | :--- | :---: |
| **1. Universe Completeness** | Exactly 1,025 topics $\times$ 15 years = 15,375 rows | 15,375 rows, 1,025 topics | **PASS** |
| **2. Document-Type Filter** | `type:article\|conference-paper\|review` | Filter verified on all queries | **PASS** |
| **3. Denominator Sync** | Exact match with matching Selected Types file | 100% matched across 15 years | **PASS** |
| **4. Group Conservation** | Meta count == Parent sum == Nested sum | 100% conservation across queries | **PASS** |
| **5. Null / Duplicate Check** | Zero missing values, zero duplicated topic-years | 0 nulls, 0 duplicates | **PASS** |
| **6. RCA Recalculation** | Bounded error ($\le 0.0000055$) | Whole $\le 5.0\times 10^{-6}$, Frac $\le 5.46\times 10^{-6}$ | **PASS** |
| **7. Dual-Panel Preservation**| Master Panel v1 frozen & intact | Preserved without overwrite | **PASS** |

### **OVERALL CERTIFICATION: READY FOR STAGE 3**
Modeling Panel v2 (`openalex_modeling_panel_1025topics_v2_selected_types.csv`) is certified as complete, structurally sound, mathematically audited, and fully prepared for Feature Engineering.
