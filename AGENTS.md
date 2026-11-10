# THESIS PROJECT CONTEXT & AGENT OPERATING DIRECTIVES

> **IMPORTANT FOR ANY AI AGENT / ASSISTANT OPENING THIS REPOSITORY:**  
> This file is the **Single Source of Truth** for the Master's Thesis project. If conversation history is lost, read this file completely before taking any action. All methodological decisions, data schemas, and mathematical specifications documented here have been audited, empirically tested, and frozen.

---

## 1. Project Metadata & Approved Proposal Specifications
* **Student:** Watcharapon Anaketanaset (Matriculation No. `94658335`)
* **Student Degree:** M.Sc. in Data Science (120 ECTS)
* **Supervisors:** First Supervisor: Prof. Dr. Iftikhar Ahmed | Second Supervisor: Dr. Shan Faiz
* **Approved Thesis Title:** *Does National Specialisation Help Forecast Research-Topic Growth? Evidence from Germany, China, and Japan Using OpenAlex*
* **Submission Deadline:** 12 February 2027
* **Primary Data Source:** OpenAlex REST API (`https://api.openalex.org`)
* **Primary Focus Countries:** Germany (DE), China (CN), Japan (JP) + Global reference (GLOBAL)
* **Study Period:** 2010–2024 (15 annual intervals)
* **Approved Research Questions (Strictly from Proposal):**
  * **RQ1:** How have technology-related research topics and national specialisation developed over time in Germany, China, and Japan?
  * **RQ2:** Do country publication counts and specialisation improve forecasts of topic growth beyond global publication history? Does specialisation add anything beyond counts?
  * **RQ3:** Do country counts and specialisation help identify topics that become high-growth but were not high-growth at the forecast date?
* **Supervisor's Official Post-Proposal Implementation Directive:**
  > *"There are just a few minor points to consider during your implementation. Please use fractional counting for publications involving multiple countries, clearly explain how the training and testing periods are constructed, and include a little more relevant literature on research trend forecasting."*

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
* **Prevalence / Eligibility Rule:** **Origin-Specific Historical Eligibility** ($\ge 50$ global works in $[t-2, t]$).
  * *Rationale:* Strictly eliminates Lookahead Bias. Evaluated separately at each forecast origin.
  * *Coverage on Primary Panel v2 (Selected Types):* Training Origin 2015 (**990 topics**, 96.59%), Training Origin 2016 (**990**, 96.59%), Training Origin 2017 (**991**, 96.68%), Test Origin 2018 (**992 topics**, 96.78%), Test Origin 2021 (**995 topics**, 97.07%).
  * *Baseline Panel v1 Note:* On the unconstrained All Types panel, coverage was 2012 (985, 96.1%), 2015 (990, 96.6%), 2018 (992, 96.8%), 2021 (996, 97.2%). For the primary research design, strictly report **992 (2018) and 995 (2021)** (with training counts **990** for Test 2018 and **3,963** pooled topic–origin observations across 2015–2018 for Test 2021).
  * *Zero-Volume Topics:* 21 topics in the taxonomy have 0 eligible works in 2010–2021 on Synchronized Panel v2 (20 across the full 2010–2024 window); the $\ge 50$ historical eligibility rule automatically and cleanly filters them out.

### B. Paper Counting & Country Attribution
* **Primary Counting Rule:** **Country-Level Equal Fractional Counting (Option C: $1/k$)** via server-side 2D aggregation (`group_by=publication_year,countries_distinct_count` with filter `authorships.institutions.country_code`).
  * *Formula:* $FC_{w,c} = \frac{1}{k_w}$; $P_{\text{Frac}}(c, i, t) = \sum_{k \ge 1} \frac{N(c, i, t, k)}{k}$ where $k_w$ is the number of distinct countries on paper $w$.
  * *Methodological Status:* Fully satisfies the Supervisor's requirement for fractional counting; strictly verified in Pre-Extraction Audit (100% group conservation, zero missing/null $k$, error reduced by >50-60% vs author-level ground truth). Note that pilot correlation $r = 0.9968$ from Phase 1 is reserved for Appendix/feasibility documentation and omitted from the main thesis text.
* **Reference Comparison Rule:** **Whole Counting** is also preserved in the modeling panel as an auxiliary baseline column for methodological comparison and the pre-declared **Whole-Counting Alternative (`M2-WC`, `M3-WC`)** sensitivity analysis on Synchronized Panel v2.

### C. Revealed Comparative Advantage (RCA) Definition
* **Sole Primary Feature:** **Fractional All-Science RCA ($RCA_{\text{AllSci}}^{\text{Frac}}$)**
  $$RCA_{\text{AllSci}}^{\text{Frac}}(c, i, t) = \frac{P_{\text{Frac}}(c, i, t) / P_{\text{Frac}}(c, \text{AllSci}, t)}{P(\text{Global}, i, t) / P(\text{Global}, \text{AllSci}, t)}$$
  For 3-year forecasting windows $[t-2, t]$, $RCA^{\text{Frac}}_{c,i,[t-2,t]}$ is computed via the **ratio-of-sums** over $[t-2, t]$ and used in its **raw (untransformed, un-winsorized)** form in the primary specification ($M3$).
* *Methodological Consistency:* Both the topic volume (numerator) and the national all-science total (denominator) strictly employ the identical $1/k$ fractional counting rule. Denominators for 2010–2024 are verified and saved in `all_science_national_denominators_fractional_v2_live_recheck_20261105.csv`.
* *Ranking Invariance:* Recalculating $RCA_{\text{AllSci}}^{\text{Frac}}$ between original and synchronized panels across all 15,375 topic-year observations yields Pearson $r = 0.99983$ (DE), $r = 0.99986$ (CN), and $r = 0.99987$ (JP), confirming that the deduplication update shifted denominator scale while preserving specialization rankings.

### D. Forecasting Formulation, Target & Baseline (Locked Decisions 2–4)
* **Target Variable:** Future 3-Year Log Growth Rate Adjusted for Global Research Growth:
  $$G_{\text{adj}}(i, t) = \left[\ln\left(1 + P_{[t+1, t+3]}^{(i)}\right) - \ln\left(1 + P_{[t-2, t]}^{(i)}\right)\right] - \left[\ln\left(1 + W_{[t+1, t+3]}\right) - \ln\left(1 + W_{[t-2, t]}\right)\right]$$
  where $W$ is the total Global All-Science publication count under the identical Selected Scholarly Work Types scope (`article|conference-paper|review`).
* **Primary Benchmark Baseline ($M0_{\text{adj}}$ Adjusted Momentum):** Consistent Window-to-Window Past Growth Adjusted for Global All-Science Growth:
  $$M0_{\text{adj}}(i, t) = \left[\ln\left(1 + P_{[t-2, t]}^{(i)}\right) - \ln\left(1 + P_{[t-5, t-3]}^{(i)}\right)\right] - \left[\ln\left(1 + W_{[t-2, t]}\right) - \ln\left(1 + W_{[t-5, t-3]}\right)\right]$$
  where $[t-2, t]$ is the recent 3-year window, $[t-5, t-3]$ is the previous 3-year window, and $W$ uses the exact same two 3-year windows so that $M0_{\text{adj}}$ predicts the identical adjusted-growth concept as $G_{\text{adj}}$.
* **Model Hierarchy (Locked Decision 2 — Option C: 2 + 3 + 3 Progressive Design):**
  * $M0$: Unfitted Adjusted Momentum Baseline ($\hat{G}_{\text{adj}}^{(M0)}(i, t) = M0_{\text{adj}}(i, t)$, no learned parameters)
  * $M1$: Global History (*2 features*: $M0_{\text{adj}}(i, t)$ and $\ln\left(1 + P_{\text{Global}, i, [t-2, t]}\right)$)
  * $M2$: Country Publication Volumes (*5 features*: $M1$ + $\ln\left(1 + P^{\text{Frac}}_{c, i, [t-2, t]}\right)$ for $c \in \{\text{DE, CN, JP}\}$)
  * $M3$: National Specialisation Primary Specification (*8 features*: $M2$ + 3-year ratio-of-sums **Raw Fractional RCA** $RCA^{\text{Frac}}_{c, i, [t-2, t]}$ for $c \in \{\text{DE, CN, JP}\}$; not winsorized in the primary specification)
  * *Statistical Interpretation:* Comparing $M2$ and $M3$ tests whether an RCA-based relative-specialisation *feature representation* improves out-of-sample predictive performance beyond global and national log-count features in a regularized linear model; it does not claim that RCA contains statistically independent raw information from publication counts.
* **Pre-Declared Closed List of Sensitivity Analyses (Evaluated on Both RQ2 and RQ3):**
  1. **`M3-LogRCA`:** Replaces the 3 raw fractional RCA features in $M3$ with $\ln\left(1 + RCA^{\text{Frac}}_{c, i, [t-2, t]}\right)$.
  2. **`Whole-Counting Alternative` (`M2-WC` and `M3-WC`):** Uses whole-count log volumes $\ln\left(1 + P^{\text{Whole}}_{c, i, [t-2, t]}\right)$ in `M2-WC` and whole-count 3-year ratio-of-sums Raw RCA ($RCA^{\text{Whole}}_{c, i, [t-2, t]}$) in `M3-WC` on Synchronized Panel v2, maintaining a strictly consistent counting basis across counts and RCA.
  * *Explicit Exclusions:* `Master Panel v1 (All Types)` is **not** used as a forecasting sensitivity dataset (study scope is strictly Selected Scholarly Work Types on Synchronized Panel v2). No ad-hoc sensitivity analyses may be added post-hoc.
* **Model Class & Hyperparameter Selection (Locked Decision 3):**
  * Regularized Linear Models (`Pipeline([("scaler", StandardScaler()), ("ridge", Ridge())])` with $L_2$ penalty; `StandardScaler` fitted strictly within each training fold; target variable never standardized). **No deep learning / black-box models.**
  * *Topic-Grouped 5-Fold Cross-Validation:* Both Test Origins (`2018` and `2021`) use `GroupKFold(n_splits=5, shuffle=True, random_state=42)` grouped by `groups = topic_id` (referred to as *Topic-grouped Cross-validation for Hyperparameter Selection*, while final evaluation is the *Temporal Holdout* at Origins 2018 and 2021).
  * *Alpha Grid & Tie-Breaking Rule:* Candidate grid $\alpha \in \operatorname{logspace}(-3, 5, 41)$ ($10^{-3}$ to $10^5$, 41 values), minimizing mean CV MAE (expand grid if boundary is hit). A custom **callable `refit` rule** selects the $\alpha$ with minimum mean CV MAE, and if multiple candidates lie within an **absolute tolerance of $10^{-12}$ (`1e-12`)** of the minimum CV MAE, selects the **largest $\alpha$** (strongest regularization). Full fold scores and CV tables for all 41 candidates are archived.
* **Evaluation & Topic-Level Paired Bootstrap Protocol (Locked Decision 4):**
  * **Forecast Accuracy (RQ2):** Mean Absolute Error ($\text{MAE}$), compared strictly within each Forecast Origin (`2018` and `2021` separately).
  * **Early Identification of Emerging High-Growth Topics (RQ3):** At each Test Origin, exclude the top 20% of eligible topics with $M0_{\text{adj}}(i, t) \ge Q_{0.80}^{\text{Past}}(t)$ (`199` topics removed; `0` boundary ties), leaving the **Remaining Pool** of **`793` topics (Origin 2018)** and **`796` topics (Origin 2021)**. Within the Remaining Pool, define future high-growth as $HG_i = \mathbb{I}\left(G_{\text{adj}}(i, t) \ge Q_{0.80}^{\text{Future}}(t)\right)$. Report the **Actual Chance Rate** ($N_{\text{Future HG}} / N_{\text{Remaining Pool}}$) and **Chance Expected Hits@50** ($50 \times N_{\text{Future HG}} / N_{\text{Remaining Pool}}$; expected $\approx 159/793 = 20.05\%$ or $10.03$ hits in 2018, and $\approx 160/796 = 20.10\%$ or $10.05$ hits in 2021). Rank the Remaining Pool descending by $\hat{G}_{\text{adj}}^{(M)}(i, t)$ across all models (`M0–M3` and sensitivity models; tie-break by ascending `topic_id`) and report both $\text{Hits@50}$ and $\text{Precision@50} = \text{Hits@50}/50$ (explicitly noting they are two representations of the same quantity).
  * **Statistical Reporting (Paired Topic Bootstrap):** Report 95% Percentile CIs (`B = 5,000` iterations, `random_state = 42`) using the **exact same bootstrap topic index draws across all models** for both model-level metrics and paired differences ($\Delta\text{MAE}$, $\Delta\text{Hits@50}$, $\Delta\text{Precision@50}$). For RQ2, resample eligible test topics ($N=992$ in 2018; $N=995$ in 2021) conditional on fitted predictions (without refitting/retuning $\alpha$ per replicate). For RQ3, resample with replacement directly within the fixed Remaining Pool ($N=793$ in 2018; $N=796$ in 2021) keeping $HG_i$ and $\hat{G}_{\text{adj}}^{(M)}$ fixed (without recomputing quantiles) and re-ranking the resampled pool to take the Top 50 slots.

### E. Temporal Train/Test Split & Forecast Origins Scope (Locked Decision 1 — Option A)
* **Approved Test Forecast Origins (Strictly 2018 and 2021):**
  * **Test Origin 2018:**
    * *Training Set:* **Origin `2015`** ($N_{\text{train}} = \mathbf{990}$ eligible topics; momentum base $[2010, 2012]$, recent window $[2013, 2015]$, training target $[2016, 2018]$).
    * *Test Set:* **Origin `2018`** ($N_{\text{test}} = \mathbf{992}$ eligible topics, RQ3 Remaining Pool $= \mathbf{793}$; momentum base $[2013, 2015]$, recent window $[2016, 2018]$, future evaluation $[2019, 2021]$).
  * **Test Origin 2021:**
    * *Training Set:* **Expanding Annual Origins `2015–2018`** ($N_{\text{train}} = 990 + 990 + 991 + 992 = \mathbf{3,963}$ pooled topic–origin observations, all with target windows $[t_{\text{train}}+1, t_{\text{train}}+3] \le 2021$).
    * *Test Set:* **Origin `2021`** ($N_{\text{test}} = \mathbf{995}$ eligible topics, RQ3 Remaining Pool $= \mathbf{796}$; momentum base $[2016, 2018]$, recent window $[2019, 2021]$, future evaluation $[2022, 2024]$).
* **Why Earlier Origins (2012, 2015) are Excluded as Test Origins:**
  * Calculating past momentum $[t-5, t-3]$ for Origin 2012 requires data from $[2007, 2009]$, which does not exist in our 2010–2024 dataset; thus Origin 2012 cannot be used as either a training or test origin.
  * **Origin 2015 is strictly retained as a Training Origin** (for both Test Origin 2018 and Test Origin 2021, because its outcome window `2016–2018` is fully observed by 2018). It is excluded **only as a Test Origin** because no earlier eligible training origin exists prior to 2015 (a leakage-free training origin for 2015 would be 2012, which lacks 2007–2009 momentum data).
  * Therefore, out-of-sample test evaluation is strictly restricted to **Test Origins 2018 and 2021**, matching the approved Proposal.
* **Leakage-Free Cutoff & Pooling Conditions:** Training origins satisfy $t_{\text{train}} \le \text{test\_origin} - 3$ (zero temporal leakage into the test period). Overlapping outcome windows among pooled training origins (`2015–2018` for Test 2021) occur strictly inside the historical training period; models are compared strictly within each Forecast Origin under a documented structural-stability assumption.

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
│   ├── DATA_PREPARATION_DRAFT_v3.md         # Definitive Data Preparation chapter draft (Bilingual, Certified Handover)
│   ├── CHAPTER4_METHODOLOGY_MASTER_SPEC.md  # Locked Chapter 4 Methodology Master Specification & Decision Lock (Decisions 1–4)
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
│   ├── independent_audit_v2.py              # Automated 29-check verification script for Synchronized Panel v2
│   ├── candidate_topics.csv                 # 1,025 topics classification & rationale
│   ├── all_tech_topics_taxonomy.csv         # Full 1,025 technology taxonomy metadata
│   ├── extraction_run.log                   # Production run log for Master Panel v1 (4 Nov 01:08–01:52 UTC+1)
│   ├── extraction_run_v2.log                # Production run log for Modeling Panel v2 (4 Nov 23:08–23:52 UTC+1)
│   └── extraction_run_denominators_v2.log   # Production run log for Synchronized Denominators (4 Nov 23:54 UTC)
│
├── extract_master_panel_1025topics.py       # Production extraction script for Master Panel v1
├── extract_modeling_panel_v2_selected_types.py # Production extraction script for Modeling Panel v2 (Selected Types)
│
└── thesis/                                  # Master LaTeX Thesis Workspace (uethesis.cls + Harvard agsm)
    ├── thesis.tex                           # Master LaTeX document combining all chapters and appendices
    ├── uethesis.cls                         # Official University of Europe for Applied Sciences LaTeX class
    ├── ue-logo.pdf                          # Official university crest logo
    ├── ref.bib                              # BibTeX bibliographic references (Author-Date Harvard agsm)
    ├── chapters/                            # Modular chapter documents
    │   ├── chapter1_introduction.tex        # Chapter 1: Introduction (Background, Problems, RQs, Contributions)
    │   ├── chapter2_background.tex          # Chapter 2: Background (Emerging Topics, Bibliometrics, RCA)
    │   ├── chapter3_literature_review.tex   # Chapter 3: Literature Review (Prior Studies, Predictors, Research Gap)
    │   ├── chapter4_methodology.tex         # Chapter 4: Methodology (OpenAlex, 1/k Counting, M0-M3, Evaluation)
    │   ├── chapter5_results_discussion.tex  # Chapter 5: Results & Discussion (RQ1, RQ2, RQ3)
    │   └── chapter6_conclusions.tex         # Chapter 6: Conclusions, Limitations, and Future Work
    ├── figures/                             # High-resolution charts, diagrams, and figures
    └── appendix/                            # Supplementary appendices
        ├── appendix_a_audit.tex             # Appendix A: 29-Check Automated Audit Protocol
        └── appendix_b_data_dict.tex         # Appendix B: 26-Column Data Dictionary & Phase 1 Pilot Note
```

---

## 4. Current Progress & Next Steps
1. **Feasibility Audit:** COMPLETE & VERIFIED.
2. **Fractional Counting Consensus:** COMPLETE & VERIFIED via Option C ($1/k$).
3. **Master Panel v1 Extraction (All Types Baseline):** COMPLETE, AUDITED, AND FROZEN (15,375 rows, 26 columns, 0 nulls, 0 duplicates, 100% group conservation).
4. **Classifier Metadata Documented:**
   - Topic Classifier: Fine-tuned **Qwen3-8B** (deployed 6 October 2026, analyzing Title, Abstract, Source Name).
   - Work Type Classifier: Major reclassification update (deployed 15 July 2026, reclassified 49.6M works).
5. **RCA Numerical Precision Resolved:** Verified that Whole RCA and Fractional RCA recalculation errors across all 92,250 cells are strictly $\Delta \le \mathbf{0.00000500}$, meeting the exact theoretical rounding ceiling.
6. **Dual-Panel Architecture Established:**
   - **Master Panel v1 (All Types):** Frozen baseline for data-scope audit comparison in Stage 2 (`openalex_master_panel_1025topics.csv`; explicitly excluded from Stage 3 forecasting sensitivity analyses).
   - **Modeling Panel v2 (Selected Types: `type:article|conference-paper|review`):** Primary research design dataset matching proposal (Synchronized: `openalex_modeling_panel_1025topics_v2_synchronized.csv`, Preserved original: `openalex_modeling_panel_1025topics_v2_selected_types.csv`).
7. **Stage 2: Full Modeling Dataset Extraction & Audit:** COMPLETE, CERTIFIED, AND FROZEN (29/29 checks PASS, `independent_audit_v2.py`).
8. **Handover & Chapter 3 / Chapter 4 Specification:** `DATA_PREPARATION_DRAFT_v3.md` established as definitive data-preparation reference; `CHAPTER4_METHODOLOGY_MASTER_SPEC.md` established and **OFFICIALLY LOCKED** for Decisions 1–4, closed sensitivity protocol (`M3-LogRCA` and `Whole-Counting Alternative` `M2-WC`/`M3-WC`), callable `refit` $\alpha$ tie-breaking rule (`1e-12` tolerance, largest $\alpha$), Actual Chance Level reporting, and Paired Topic Bootstrap (`B = 5,000`, `seed = 42`).
9. **Next Milestone (Pre-Stage 3 Diagnostic & Stage 3 Implementation):**
   - Execute the **Pre-Stage 3 Read-Only Upper-Tail Diagnostic** on 3-year Raw Fractional RCA (`Median`, `P95`, `Max`, Spearman correlation with $\ln(1 + P_{\text{Global}, i, [t-2, t]})$, and top-RCA topic inspection across eligible origins, without winsorizing or dropping topics).
   - Proceed upon user instruction to draft Chapter 4 (`Sections 4.4–4.8`) and implement Stage 3 Feature Engineering ($M0\text{–}M3$ + pre-declared sensitivities) and Target Variable generation ($G_{\text{adj}}(i, t)$) strictly on Synchronized Modeling Panel v2.
