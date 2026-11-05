# THESIS PROJECT CONTEXT & AGENT OPERATING DIRECTIVES

> **IMPORTANT FOR ANY AI AGENT / ASSISTANT OPENING THIS REPOSITORY:**  
> This file is the **Single Source of Truth** for the Master's Thesis project. If conversation history is lost, read this file completely before taking any action. All methodological decisions, data schemas, and mathematical specifications documented here have been audited, empirically tested, and frozen.

---

## 1. Project Metadata
* **Student Degree:** M.Sc. Data Science
* **Thesis Working Title:** *Forecasting Emerging Technology Research Trends: A Comparative Study of Germany, China, and Japan Using OpenAlex Data*
* **Submission Deadline:** 12 February 2027
* **Primary Data Source:** OpenAlex REST API (`https://api.openalex.org`)
* **Primary Focus Countries:** Germany (DE), China (CN), Japan (JP) + Global reference (GLOBAL)
* **Study Period:** 2010–2024 (15 annual intervals)

---

## 2. Core Methodological Consensus (DO NOT ALTER WITHOUT EXPLICIT USER INSTRUCTION)

### A. Taxonomy & Scope (OpenAlex Topics)
* **Taxonomy Source:** **OpenAlex Topics Taxonomy** (derived from CWTS Leiden citation clustering, 4,516 global topics).
* **Domain Scope:** 5 Technology Fields within Physical Sciences:
  1. *Engineering* (560 topics)
  2. *Computer Science* (302 topics)
  3. *Materials Science* (123 topics)
  4. *Energy* (27 topics)
  5. *Chemical Engineering* (13 topics)
* **Universe Size:** Exactly **1,025 topics**.
* **Prevalence / Eligibility Rule:** **Origin-Specific Historical Eligibility** ($\ge 50$ works in $[t-2, t]$).
  * *Rationale:* Strictly eliminates Lookahead Bias. Evaluated separately at each forecast origin.
  * *Coverage:* 2012 (985 topics, 96.1%), 2015 (990 topics, 96.6%), 2018 (992 topics, 96.8%), 2021 (996 topics, 97.2%).
  * *Zero-Volume Topics:* 21 topics in the taxonomy have 0 eligible works in 2010–2021; this rule automatically and cleanly filters them out.

### B. Paper Counting & Country Attribution
* **Primary Counting Rule:** **Country-Level Equal Fractional Counting (Option C: $1/k$)** via server-side 2D aggregation (`group_by=publication_year,countries_distinct_count` with filter `authorships.institutions.country_code`).
  * *Formula:* $P_{\text{Frac}}(c, i, t) = \sum_{k \ge 1} \frac{N(c, i, t, k)}{k}$ where $k$ is the number of distinct countries on the paper.
  * *Methodological Status:* Fully satisfies the Supervisor's requirement for fractional counting; strictly verified in Pre-Extraction Audit (100% group conservation, zero missing/null $k$, $r = 0.9968$ with Whole RCA, error reduced by >50-60% vs author-level ground truth).
* **Reference Comparison Rule:** **Whole Counting** is also preserved in the master panel as an auxiliary baseline column for methodological comparison and sensitivity analysis.

### C. Revealed Comparative Advantage (RCA) Definition
* **Sole Primary Feature:** **Fractional All-Science RCA ($RCA_{\text{AllSci}}^{\text{Frac}}$)**
  $$RCA_{\text{AllSci}}^{\text{Frac}}(c, i, t) = \frac{P_{\text{Frac}}(c, i, t) / P_{\text{Frac}}(c, \text{AllSci}, t)}{P(\text{Global}, i, t) / P(\text{Global}, \text{AllSci}, t)}$$
* *Methodological Consistency:* Both the topic volume (numerator) and the national all-science total (denominator) strictly employ the identical $1/k$ fractional counting rule. Denominators for 2010–2024 are verified and saved in `all_science_national_denominators_fractional.csv`.

### D. Forecasting Formulation, Target & Baseline
* **Target Variable:** Future 3-Year Log Growth Rate Adjusted for Global Research Growth:
  $$G_{\text{adj}}(i, t) = \left[\ln\left(1 + P_{[t+1, t+3]}^{(i)}\right) - \ln\left(1 + P_{[t-2, t]}^{(i)}\right)\right] - \left[\ln\left(1 + W_{[t+1, t+3]}\right) - \ln\left(1 + W_{[t-2, t]}\right)\right]$$
  where $W$ is the total Global All-Science publication count under the identical Selected Scholarly Work Types scope (`article|conference-paper|review`).
* **Primary Benchmark Baseline ($M0_{\text{adj}}$ Adjusted Momentum):** Consistent Window-to-Window Past Growth Adjusted for Global All-Science Growth:
  $$M0_{\text{adj}}(i, t) = \left[\ln\left(1 + P_{[t-2, t]}^{(i)}\right) - \ln\left(1 + P_{[t-5, t-3]}^{(i)}\right)\right] - \left[\ln\left(1 + W_{[t-2, t]}\right) - \ln\left(1 + W_{[t-5, t-3]}\right)\right]$$
  where $[t-2, t]$ is the recent 3-year window, $[t-5, t-3]$ is the previous 3-year window, and $W$ uses the exact same two 3-year windows so that $M0_{\text{adj}}$ predicts the identical adjusted-growth concept as $G_{\text{adj}}$.
* **Model Hierarchy:**
  * $M0$: Naïve Adjusted Momentum Baseline ($M0_{\text{adj}}$, no learned parameters)
  * $M1$: Global History ($M0_{\text{adj}}$ + Past Log Global Volume)
  * $M2$: Country Publication Volumes ($M1$ + Log Volumes for DE, CN, JP)
  * $M3$: National Specialization ($M2$ + $RCA_{\text{AllSci}}^{\text{Frac}}$ for DE, CN, JP)
* **Model Class:** Regularized Linear Models (Ridge Regression with $L_2$ penalty). **No deep learning / black-box models.**
  * *Hyperparameter Selection ($\lambda$) Note for Stage 3:* Because Test Origin 2018 has only one non-overlapping prior training origin (`2015`, where $[t-5, t-3] = [2010, 2012]$, $[t-2, t] = [2013, 2015]$, and target $[t+1, t+3] = [2016, 2018]$), temporal 5-fold cross-validation across multiple training origins is not possible for Origin 2018. Therefore, Ridge penalty $\lambda$ must be selected via **cross-sectional 5-fold cross-validation across eligible topics** within the training set (or within-origin topic-level CV).

### E. Temporal Train/Test Split & Forecast Origins Scope
* **Approved Forecast Origins (Strictly 2018 and 2021):**
  * **Test Origin 2018:** Past window $[2016, 2018]$, Momentum base $[2013, 2015]$, Future evaluation $[2019, 2021]$.
  * **Test Origin 2021:** Past window $[2019, 2021]$, Momentum base $[2016, 2018]$, Future evaluation $[2022, 2024]$.
* **Why Earlier Origins (2012, 2015) are Excluded:**
  * Calculating past momentum $[t-5, t-3]$ for Origin 2012 requires data from $[2007, 2009]$, which does not exist in our 2010–2024 dataset.
  * Origin 2015 has no prior non-overlapping training window $\le 2015 - 3 = 2012$ without 2007–2009 data.
  * Therefore, the research design strictly restricts evaluation to Origins 2018 and 2021, matching the approved Proposal.
* **Leakage-Free Cutoff:** Training origins $t_{\text{train}} \le \text{test\_origin} - 3$.

---

## 3. Directory Layout & File Catalog

```
d:\Thesis\
│
├── AGENTS.md                                # This system prompt and instructions for AI agents
├── README.md                                # Project overview, quickstart, and thesis guide
├── backup_thesis.py                         # One-click backup script creating timestamped archives
├── lens-export.csv                          # Patent / literature reference export
├── Lecture 01 Master Colliquim Reseach Topic.pdf  # Academic guideline
├── Lecture 02 Master Good Thesis.pdf        # Academic guideline
│
├── openalex_feasibility_audit\              # Master Feasibility & Stage 2 Audit (1,025-topic universe)
│   ├── OPENALEX_FEASIBILITY_REPORT.md       # Comprehensive Stage 1 Audit Report (CONDITIONAL PASS)
│   ├── FINAL_FREEZE_REPORT.md               # Master Panel v1 Freeze Certification & Quality Audit
│   ├── DOCUMENT_TYPE_AND_METADATA_AUDIT.md  # Detailed Scope, Metadata & Mathematical Audit Report
│   ├── STAGE2_DATASET_AUDIT_REPORT.md       # Stage 2 Dataset Preparation Audit & Certification
│   ├── STAGE2_FINAL_CORRECTION_REPORT.md    # Stage 2 Final Correction & Reconciliation Report
│   ├── FINAL_DENOMINATOR_AND_RCA_VERIFICATION.md # Synchronized Panel v2 & RCA Verification Report
│   ├── CHATGPT_REVIEW_BUNDLE.md             # Consolidated Independent Review Bundle
│   ├── openalex_master_panel_1025topics.csv # FROZEN Master Panel v1 (All Types Baseline, 15,375 rows)
│   ├── openalex_modeling_panel_1025topics_v2_selected_types.csv # PRESERVED Original Modeling Panel v2 (15,375 rows)
│   ├── openalex_modeling_panel_1025topics_v2_synchronized.csv # PRIMARY Synchronized Modeling Panel v2 (15,375 rows)
│   ├── all_science_national_denominators_fractional.csv # All-science 15-yr fractional denominators (v1)
│   ├── all_science_national_denominators_fractional_v2_selected_types.csv # Pre-deduplication v2 denominators (preserved)
│   ├── all_science_national_denominators_fractional_v2_live_recheck_20261105.csv # Synchronized v2 denominators (post-dedup)
│   ├── annual_work_types_and_topic_coverage.csv # Reconciled 15-year coverage & work types audit table
│   ├── synchronize_modeling_panel_v2.py     # Deterministic script building synchronized v2 panel without API calls
│   ├── extract_denominators_v2.py           # Denominator extraction script for Selected Scholarly Work Types
│   ├── independent_audit_v2.py              # Automated 28-check verification script for Synchronized Panel v2
│   ├── candidate_topics.csv                 # 1,025 topics classification & rationale
│   ├── all_tech_topics_taxonomy.csv         # Full 1,025 technology taxonomy metadata
│   ├── extraction_run.log                   # Production run log for Master Panel v1 (4 Nov 01:08–01:52 UTC+1)
│   ├── extraction_run_v2.log                # Production run log for Modeling Panel v2 (4 Nov 23:08–23:52 UTC+1)
│   └── extraction_run_denominators_v2.log   # Production run log for Synchronized Denominators (4 Nov 23:54 UTC)
│
├── extract_master_panel_1025topics.py       # Production extraction script for Master Panel v1
└── extract_modeling_panel_v2_selected_types.py # Production extraction script for Modeling Panel v2 (Selected Types)
```

---

## 4. Current Progress & Next Steps
1. **Feasibility Audit:** COMPLETE & VERIFIED.
2. **Fractional Counting Consensus:** COMPLETE & VERIFIED via Option C ($1/k$).
3. **Master Panel v1 Extraction (All Types Baseline):** COMPLETE, AUDITED, AND FROZEN (15,375 rows, 26 columns, 0 nulls, 0 duplicates, 100% group conservation).
4. **Classifier Metadata Documented:**
   - Topic Classifier: Fine-tuned **Qwen3-8B** (deployed 6 October 2026, analyzing Title, Abstract, Source Name).
   - Work Type Classifier: Major reclassification update (deployed 15 July 2026, reclassified 49.6M works).
5. **RCA Numerical Precision Resolved:** Verified that Whole RCA and Fractional RCA recalculation errors across all 46,125 cells are strictly $\Delta \le \mathbf{0.00000500}$, meeting the exact theoretical rounding ceiling.
6. **Dual-Panel Architecture Established:**
   - **Master Panel v1 (All Types):** Frozen baseline for methodological comparison / sensitivity analysis (`openalex_master_panel_1025topics.csv`).
   - **Modeling Panel v2 (Selected Types: `type:article|conference-paper|review`):** Primary research design dataset matching proposal (`openalex_modeling_panel_1025topics_v2_selected_types.csv`).
7. **Stage 2: Full Modeling Dataset Extraction & Audit:** COMPLETE & CERTIFIED (READY FOR STAGE 3).
8. **Next Milestone (Stage 3):**
   - Await user approval on Dataset Readiness Report.
   - Upon approval, proceed to Feature Engineering ($M0-M3$ features) and Target Variable generation ($G(i, t)$).
