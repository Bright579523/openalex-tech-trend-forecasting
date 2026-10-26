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
* **Counting Rule:** **Whole Counting** (Full Counting) via server-side aggregation (`group_by=authorships.institutions.country_code`).
* **Co-authorship Overlap:** Global overlap across DE, CN, JP is ~1.054 countries/work.
* **Strict Guardrail:** Do **NOT** claim fractional counting is implemented. International co-authorship double-counting is an explicit, documented thesis limitation.

### C. Revealed Comparative Advantage (RCA) Definition
* **Sole Primary Feature:** **All-Science RCA ($RCA_{\text{AllSci}}$)**
  $$RCA_{\text{AllSci}}(c, i, t) = \frac{P(c, i, t) / \sum_{k \in \text{AllSci}} P(c, k, t)}{P(\text{Global}, i, t) / \sum_{k \in \text{AllSci}} P(\text{Global}, k, t)}$$
* *Methodological Reason:* Measures true national research specialization against the whole national science budget/output. (e.g., China allocates 49.5% of its research to technology vs. 24.9% globally; mean $RCA_{\text{AllSci}}$: CN=2.080, DE=1.293, JP=1.492).

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
│   └── model_pilot_results_allsci_consistent.csv # Pilot benchmark results (M0-M3)
│
└── proposal_audit_csvs\                     # Dedicated CSV Review Folder for Chat / Proposal Audit
    ├── audit_csv.py                         # In-place inspection script
    ├── full_1025_topics_historical_volumes.csv
    ├── full_universe_origin_eligibility.csv
    └── model_pilot_results_allsci_consistent.csv
```

---

## 4. Current Progress & Next Steps
1. **Feasibility Audit:** COMPLETE & VERIFIED.
2. **ChatGPT / Advisor Proposal Review:** IN PROGRESS (Files in `proposal_audit_csvs` and `audit_csv.py` verified).
3. **Next Production Milestone:**
   * Extract the Full Master Panel (`openalex_master_panel_1025topics.csv`):
     - Requires 4,100 OpenAlex API calls.
     - Covered 100% for free under OpenAlex's $1.00/day allowance (requires user's Free API key).
     - Execution time: ~3–5 minutes at 20–30 req/sec.
