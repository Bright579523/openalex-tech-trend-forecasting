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
* **Target Variable:** Future 3-Year Log Growth Rate:
  $$G(i, t) = \ln\left(1 + P_{[t+1, t+3]}^{(i)}\right) - \ln\left(1 + P_{[t-2, t]}^{(i)}\right)$$
* **Primary Benchmark Baseline ($M0$ Momentum):** Consistent Window-to-Window Past Growth:
  $$M_{\text{window}}(i, t) = \ln\left(1 + P_{[t-2, t]}^{(i)}\right) - \ln\left(1 + P_{[t-5, t-3]}^{(i)}\right)$$
* **Model Hierarchy:**
  * $M0$: Naïve Momentum Baseline (No parameters)
  * $M1$: Global History ($M0$ + Past Log Global Volume)
  * $M2$: Country Publication Volumes ($M1$ + Log Volumes for DE, CN, JP)
  * $M3$: National Specialization ($M2$ + $RCA_{\text{AllSci}}$ for DE, CN, JP)
* **Model Class:** Regularized Linear Models (Ridge Regression with $L_2$ penalty). **No deep learning / black-box models.**

### E. Temporal Train/Test Split & $N_{\text{train}}$ Explanation
* **Leakage-Free Cutoff:** Training origins $t_{\text{train}} \le \text{test\_origin} - 3$.
* **Why $N_{\text{train}} = 50$ (2018) vs $N_{\text{train}} = 200$ (2021) in the pilot:**
  * The pilot constructed annual rolling origins ($t \in [2015..2021]$).
  * For Test Origin 2018: Cutoff $\le 2015 \implies$ Only origin 2015 is available ($50 \times 1 = 50$ rows).
  * For Test Origin 2021: Cutoff $\le 2018 \implies$ Origins 2015, 2016, 2017, 2018 are available ($50 \times 4 = 200$ rows).
* **Triennial Non-Overlapping Stride Alternative:**
  * Test Origin 2018: Train on 2015 ($N = 50$).
  * Test Origin 2021: Train on 2015 and 2018 ($N = 100$).

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
├── openalex_feasibility_audit\              # Master Feasibility Audit (1,025-topic universe)
│   ├── OPENALEX_FEASIBILITY_REPORT.md       # Comprehensive Audit Report (CONDITIONAL PASS)
│   ├── AUDIT_CORRECTIONS.md                 # Complete technical resolution notes
│   ├── openalex_feasibility_audit.py        # Executable 3-step audit script
│   ├── data_audit_summary.json              # Machine-readable audit summary
│   ├── run_log.md                           # Chronological API call log
│   ├── candidate_topics.csv                 # 1,025 topics classification & rationale
│   ├── all_tech_topics_taxonomy.csv         # Full 1,025 technology taxonomy metadata
│   ├── national_annual_totals_all_science.csv # All-science annual totals (Global, DE, CN, JP)
│   ├── full_1025_topics_historical_volumes.csv # 1,025 topics volume matrix across 4 origins
│   ├── full_universe_origin_eligibility.csv # Full universe eligibility statistics
│   ├── sample_topic_country_counts.csv      # Sample extracted annual counts
│   ├── enriched_panel_with_both_rcas.csv    # 50-topic pilot panel with both RCA versions
│   ├── model_pilot_results_allsci_consistent.csv # Pilot benchmark results (M0-M3)
│   ├── all_science_national_denominators_fractional.csv # Complete 15-year fractional denominators (2010-2024)
│   ├── test_option_c_fractional.py          # Option C vs Ground Truth empirical validation script
│   └── test_pre_extraction_checks.py        # 4-point pre-extraction audit verification script
│
└── proposal_audit_csvs\                     # Dedicated CSV Review Folder for Chat / Proposal Audit
    ├── audit_csv.py                         # In-place inspection script
    ├── full_1025_topics_historical_volumes.csv
    ├── full_universe_origin_eligibility.csv
    ├── enriched_panel_with_both_rcas.csv
    └── model_pilot_results_allsci_consistent.csv
```

---

## 4. Current Progress & Next Steps
1. **Feasibility Audit:** COMPLETE & VERIFIED.
2. **Fractional Counting Consensus:** COMPLETE & VERIFIED via Option C ($1/k$).
3. **Pre-Extraction 4-Point Audit:** ALL 4 CHECKS PASSED (100% group conservation, zero null/0 keys, fractional all-science denominators verified).
4. **Next Production Milestone:**
   * Extract the Full Master Panel (`openalex_master_panel_1025topics.csv`):
     - Uses Option C 2D GroupBy (`publication_year,countries_distinct_count`).
     - Extracts both Country-level Equal Fractional Counts AND Whole Counts simultaneously.
     - 1,025 topics $\times$ 3 countries = 3,075 calls (+ 1,025 global calls) = 4,100 API calls.
     - 100% free under OpenAlex $1.00/day allowance (~3–5 minutes at 20–30 req/sec).
