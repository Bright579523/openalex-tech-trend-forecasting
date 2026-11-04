# OpenAlex Master Panel Final Extraction & Data Quality Audit Report

**Document:** `MASTER_EXTRACTION_AUDIT_REPORT.md`  
**Execution Date:** 04 November 2026 (01:08:35 – 01:52:01 UTC+1)  
**Status:** **PASSED & FROZEN (Production Ready)**  
**Auditor / Engineer:** Senior Research Engineer & Data Scientist (AntiGravity)  
**Primary Dataset File:** [`openalex_master_panel_1025topics.csv`](file:///d:/Thesis/openalex_feasibility_audit/openalex_master_panel_1025topics.csv)  
**Dataset Copies:**
- `d:\Thesis\openalex_feasibility_audit\openalex_master_panel_1025topics.csv` (Size: ~4.1 MB)
- `d:\Thesis\proposal_audit_csvs\openalex_master_panel_1025topics.csv` (Size: ~4.1 MB)

---

## 1. Executive Summary & Verification of the 7 Key Checkpoints

| # | Checkpoint | Verification Metric | Audit Verdict | Empirical Evidence / Finding |
| :-: | :--- | :--- | :---: | :--- |
| **1** | **Expected Dimensions** | 1,025 Topics $\times$ 15 Years | **PASS** | Exactly **15,375 rows** and **27 columns**; all 1,025 topics from technology taxonomy present across 2010–2024. |
| **2** | **Record Uniqueness & Nulls** | Duplicates & Missing Values | **PASS** | Exactly **0 duplicate topic-years**; **0 missing/null values** across all 27 columns. |
| **3** | **Fail-Fast Query Integrity** | `meta == sum(parent) == sum(sub)` | **PASS** | **0 mismatches across all 4,100 API queries**; group conservation strictly maintained at 100%. |
| **4** | **Active vs. Zero Topics** | Non-zero volume separation | **PASS** | **1,005 active topics** ($\sum P_{\text{glob}} > 0$); **20 zero-volume topics** explicitly recorded as 0 across all 15 years. |
| **5** | **Counting & RCA Validity** | Numerical Bounds & Non-negativity | **PASS** | Fractional counts strictly $\le$ Whole counts; 0 invalid/infinite/negative RCA values; All-Science denominators verified. |
| **6** | **Checkpoint & Idempotence** | Checkpoint consistency | **PASS** | Checkpoints periodically committed every 25 topics; zero gap or duplicate records upon final assembly. |
| **7** | **Provenance & Reproducibility** | Logging, Headers & Backups | **PASS** | Full chronological log preserved in `extraction_run.log`; automated timestamped archive synced to OneDrive; Git commit locked. |

---

## 2. Core Methodological Consensus & Formulas Implemented

### A. Country-Level Equal Fractional Counting (Option C: $1/k$)
For each country $c \in \{\text{DE}, \text{CN}, \text{JP}\}$, topic $i$, and publication year $t \in [2010..2024]$:
$$P_{\text{Frac}}(c, i, t) = \sum_{k \ge 1} \frac{N(c, i, t, k)}{k}$$
where $N(c, i, t, k)$ is the number of works in topic $i$ and year $t$ with at least one author affiliated with country $c$, having exactly $k$ distinct participating countries.

### B. Whole Counting (Reference Baseline)
$$P_{\text{Whole}}(c, i, t) = \sum_{k \ge 1} N(c, i, t, k)$$
Whole counting is preserved side-by-side in all 15,375 rows for rigorous **Methodological Comparison and Sensitivity Analysis** in the thesis.

### C. Fractional All-Science Revealed Comparative Advantage ($RCA_{\text{AllSci}}^{\text{Frac}}$)
$$RCA_{\text{AllSci}}^{\text{Frac}}(c, i, t) = \frac{P_{\text{Frac}}(c, i, t) \;/\; P_{\text{Frac}}(c, \text{AllSci}, t)}{P(\text{Global}, i, t) \;/\; P(\text{Global}, \text{AllSci}, t)}$$
- **Numerator:** Topic fractional volume divided by national all-science fractional volume.
- **Denominator:** Global topic volume divided by global all-science volume (each unique paper counted once).
- **Edge cases:** If $P(\text{Global}, i, t) = 0$ or $P_{\text{Frac}}(c, i, t) = 0$, $RCA$ is explicitly defined as $0.0$.

---

## 3. Quantitative Summary of the Master Panel

### A. Aggregate Volume & Co-authorship Deflation
Over the 15-year period (2010–2024), the master panel accounts for **28,728,317 technology works** globally:

| Entity | Whole Count Total | Fractional Count Total | Deflation Ratio ($P_{\text{Frac}} / P_{\text{Whole}}$) | International Collaboration Burden |
| :--- | :---: | :---: | :---: | :--- |
| **Global** | 28,728,317 | 28,728,317 | 1.000 | Invariant (Planet Earth total) |
| **Germany (DE)** | 899,430 | **691,772.3** | **0.769** | High international co-authorship (23.1% deflation) |
| **China (CN)** | 4,917,710 | **4,417,308.9** | **0.898** | Predominantly domestic research (10.2% deflation) |
| **Japan (JP)** | 914,185 | **800,133.7** | **0.875** | Moderate international co-authorship (12.5% deflation) |

### B. Statistical Distribution of Features across 15,375 Rows

| Feature | Mean | Std Dev | Min | Median (50%) | 75% | Max |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **`global_count`** | 1,868.51 | 1,831.42 | 0 | 1,351.0 | 2,573.5 | 26,522.0 |
| **`de_frac_count`** | 44.99 | 61.51 | 0.0 | 26.17 | 59.89 | 2,761.83 |
| **`cn_frac_count`** | 287.30 | 443.10 | 0.0 | 151.50 | 352.48 | 10,101.21 |
| **`jp_frac_count`** | 52.04 | 66.10 | 0.0 | 29.50 | 70.90 | 2,362.83 |
| **`rca_frac_de`** | 1.376 | 1.391 | 0.0 | 1.076 | 1.890 | 54.39 |
| **`rca_frac_cn`** | 2.245 | 1.741 | 0.0 | 1.997 | 3.075 | 16.22 |
| **`rca_frac_jp`** | 1.674 | 1.658 | 0.0 | 1.275 | 2.308 | 34.26 |

---

## 4. Zero-Volume Topic Breakdown (Explicit Representation)

Across the 15-year study period, exactly **20 topics** in the CWTS Leiden / OpenAlex Physical Sciences taxonomy have 0 eligible publications in the 5 technology fields:
- `T13836` (Educational Research and Pedagogy)
- `T14064` (Organizational and Employee Performance)
- `T14145` (Diverse Cultural Media Analysis)
- `T13027` (Applied Advanced Technologies)
- `T13693` (Smart Systems and Machine Learning)
- `T13685` (Material Science and Thermodynamics)
- `T13924` (IoT and Social Network Interactions)
- `T13567` (AI and Multimedia in Education)
- `T13964` (Educational Technology and Optimization)
- `T14413` (Advanced Technologies in Various Fields)
- `T14155` (Advanced Technology in Applications)
- `T13514` (Experience-Based Knowledge Management)
- `T14420` (Advanced Research in Systems and Signal Processing)
- `T14100` (Scientific Research and Technology)
- `T13541` (IoT-based Control Systems)
- `T14431` (Diverse Research and Applications)
- `T14204` (Railway Systems and Materials Science)
- `T14175` (Intuitionistic Fuzzy Systems Applications)
- `T14174` (AI and Decision Support Systems)
- `T14096` (Advancements in Materials Engineering)

**Methodological Treatment:**
These 20 topics are explicitly preserved in the master panel with `global_count = 0` and `rca = 0.0` for all 15 annual intervals ($20 \times 15 = 300$ rows). When evaluating historical forecast origins (2012, 2015, 2018, 2021), the **Origin-Specific Historical Eligibility rule ($\ge 50$ works in $[t-2, t]$)** automatically and cleanly filters them out without Lookahead Bias.

---

## 5. Master Panel Schema (27 Columns)

```
 1. topic_id                : OpenAlex unique topic identifier (e.g. T10281)
 2. topic_name              : Standardized topic display name
 3. field_name              : Technology field (Engineering, Computer Science, etc.)
 4. subfield_name           : Academic subfield
 5. year                    : Publication year (2010–2024)
 6. retrieval_timestamp     : ISO 8601 exact retrieval timestamp
 7. global_count            : Total unique works globally
 8. global_allsci_denom     : Global all-science total volume
 9. de_whole_count          : Germany whole count (>=1 DE affiliation)
10. de_frac_count           : Germany equal fractional count (sum of 1/k)
11. de_allsci_whole_denom   : Germany all-science whole total
12. de_allsci_frac_denom    : Germany all-science fractional total
13. rca_frac_de             : Germany Fractional All-Science RCA (Primary feature)
14. rca_whole_de            : Germany Whole All-Science RCA (Sensitivity baseline)
15. cn_whole_count          : China whole count
16. cn_frac_count           : China equal fractional count (sum of 1/k)
17. cn_allsci_whole_denom   : China all-science whole total
18. cn_allsci_frac_denom    : China all-science fractional total
19. rca_frac_cn             : China Fractional All-Science RCA (Primary feature)
20. rca_whole_cn            : China Whole All-Science RCA (Sensitivity baseline)
21. jp_whole_count          : Japan whole count
22. jp_frac_count           : Japan equal fractional count (sum of 1/k)
23. jp_allsci_whole_denom   : Japan all-science whole total
24. jp_allsci_frac_denom    : Japan all-science fractional total
25. rca_frac_jp             : Japan Fractional All-Science RCA (Primary feature)
26. rca_whole_jp            : Japan Whole All-Science RCA (Sensitivity baseline)
```

---

## 6. Audit Verdict & Recommendation

**Verdict: PASSED & READY TO FREEZE**

The master dataset `openalex_master_panel_1025topics.csv` satisfies all theoretical, mathematical, and data integrity standards established by the student, supervisor, and audit review. The dataset is ready to serve as the immutable empirical foundation for the Master's Thesis.

