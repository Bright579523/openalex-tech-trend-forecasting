# Stage 3.1 Thesis-Ready Tables and Figures (`thesis_assets/`)

> **Provenance:** All tables and workflow figures in this directory are derived strictly from the audited Stage 3.1 artifacts (`stage3_origin_features_targets.csv`, `stage3_feature_target_manifest.json`, `stage3_feature_target_audit_report.md`) at Git checkpoint `ffc1716`. No models have been trained and no canonical datasets or thesis chapters were altered.

---

## Asset Inventory & Thesis Mapping

### 1. Model Feature Definitions (`M0–M3` and Pre-Declared Sensitivities)
* **Files:**
  * [`table_4_model_feature_definitions.csv`](table_4_model_feature_definitions.csv) *(generated tabular data)*
  * [`table_4_model_feature_definitions.tex`](table_4_model_feature_definitions.tex) *(generated LaTeX `booktabs` fragment)*
* **Generator Script:** [`build_thesis_tables.py`](build_thesis_tables.py) *(editable generator)*
* **Suggested Thesis Number:** **Table 4.2** *(or next sequential table number in Chapter 4; tentative placeholder label `tab:model-features`)*
* **Suggested Caption:** *Feature definitions, counts, and analytical roles for benchmark, primary (`M0`–`M3`), and pre-declared sensitivity specifications.*
* **Chapter & Subsection Placement:** **Chapter 4 (Methodology), Sections 4.4–4.5** — Feature Engineering and Forecasting Model Hierarchy (`M0–M3`).
* **What the Reader Should Learn:**
  1. The progressive `2 + 3 + 3` nested hierarchy separating global growth history (`M1`), national fractional publication counts (`M2`), and untransformed three-year ratio-of-sums fractional RCA (`M3`).
  2. That `M0` serves as an unfitted benchmark (`m0_adj`) rather than a regression model, and that two pre-declared sensitivity variants (`M3-LogRCA`, plus whole-counting paired `M2-WC` / `M3-WC`) are locked cleanly before model training.
  3. Exact feature column lists (`X`) strictly exclude the future outcome `g_adj` and target-window sums.
* **Authoritative Source:** `stage3_modeling/stage3_feature_target_manifest.json` (`schema_roles.model_feature_sets`), verified against `stage3_modeling/stage3_origin_features_targets.csv` (`7,175 × 42`) and `openalex_feasibility_audit/CHAPTER4_METHODOLOGY_MASTER_SPEC.md` (Section 6 Decision 2).
* **Editability Status:** CSV and `.tex` files are **generated** deterministically by `build_thesis_tables.py` (do not hand-edit numbers; regenerate if upstream spec changes).

---

### 2. Eligible Topics by Forecast Origin (`2015–2021`)
* **Files:**
  * [`table_4_eligible_topics_by_origin.csv`](table_4_eligible_topics_by_origin.csv) *(generated tabular data)*
  * [`table_4_eligible_topics_by_origin.tex`](table_4_eligible_topics_by_origin.tex) *(generated LaTeX `booktabs` fragment)*
* **Generator Script:** [`build_thesis_tables.py`](build_thesis_tables.py) *(editable generator)*
* **Suggested Thesis Number:** **Table 4.3** *(tentative placeholder label `tab:origin-eligibility`)*
* **Suggested Caption:** *Topic eligibility counts across all valid forecast origins (2015–2021) under the origin-specific historical rule $\sum_{y=t-2}^{t} P_{\text{Global}}(i, y) \ge 50$.*
* **Chapter & Subsection Placement:** **Chapter 4 (Methodology), Section 4.6** — Temporal Train/Test Split, Forecast Origins, and Eligibility Construction.
* **What the Reader Should Learn:**
  1. Exactly how the 1,025-topic universe maps across all seven mathematically valid forecast origins (`2015–2021`), showing past momentum (`[t-5, t-3]`), recent feature/eligibility (`[t-2, t]`), and future target (`[t+1, t+3]`) windows.
  2. Verified eligible counts (`990`, `990`, `991`, `992`, `994`, `995`, `995` — `6,947` eligible and `228` ineligible rows out of `7,175` canonical rows) depend strictly on historical output $\ge 50$ works in `[t-2, t]`.
  3. How the Stage 3.1 origins map to the Stage 3.2 temporal design (`2015 -> 2018` with $N_{\text{train}}=990, N_{\text{test}}=992$; and `2015–2018 -> 2021` with $N_{\text{train}}=3,963, N_{\text{test}}=995$).
* **Authoritative Source:** Calculated directly from `stage3_modeling/stage3_origin_features_targets.csv` (`global_topic_3yr >= 50` verified against `eligible`) and `stage3_modeling/stage3_feature_target_manifest.json`.
* **Editability Status:** CSV and `.tex` files are **generated** deterministically by `build_thesis_tables.py`.

---

### 3. Stage 3.1 Validation and Leakage-Audit Summary
* **Files:**
  * [`table_a_stage3_1_validation_summary.csv`](table_a_stage3_1_validation_summary.csv) *(generated tabular data)*
  * [`table_a_stage3_1_validation_summary.tex`](table_a_stage3_1_validation_summary.tex) *(generated LaTeX `booktabs` fragment)*
* **Generator Script:** [`build_thesis_tables.py`](build_thesis_tables.py) *(editable generator)*
* **Suggested Thesis Number:** **Table A.2** *(following Appendix A's 29-check Stage 2 panel audit table; tentative placeholder label `tab:stage31-validation`)*
* **Suggested Caption:** *Summary of Stage 3.1 feature and target construction validation checks and independent leakage audit results.*
* **Chapter & Subsection Placement:** **Appendix A (Independent Audit and Verification Protocol)** — Stage 3.1 Feature and Target Construction Audit.
* **What the Reader Should Learn:**
  1. Complete verification that all mathematical formulas, window boundaries, ratio-of-sums RCA values, missing/infinite checks (`0` nulls/Infs), and the algebraic identity $G_{\text{adj}}(i,t) = M0_{\text{adj}}(i,t+3)$ hold to numerical machine precision (`0.00` identity difference; `2.665e-15` independent scalar max diff).
  2. Empirical proof of zero forward-time leakage via a full forward-year poisoning test (`year > t` set to `999,999,999`, leaving every feature and eligibility flag unchanged while shifting every target observation).
  3. Cryptographic preservation of the frozen Stage 2 source datasets throughout Stage 3.1 (`19/19 PASS`, `exit 0`).
* **Authoritative Source:** `stage3_modeling/stage3_feature_target_audit_report.md` (`19/19 PASS`) and `stage3_modeling/stage3_feature_target_manifest.json`.
* **Editability Status:** CSV and `.tex` files are **generated** deterministically by `build_thesis_tables.py`.

---

### 4. Feature and Target Construction Workflow Diagram
* **Files:**
  * [`fig_4_feature_target_workflow.py`](fig_4_feature_target_workflow.py) *(editable Matplotlib vector source script)*
  * [`fig_4_feature_target_workflow.svg`](fig_4_feature_target_workflow.svg) *(generated scalable vector graphic)*
  * [`fig_4_feature_target_workflow.pdf`](fig_4_feature_target_workflow.pdf) *(generated vector PDF for LaTeX `\includegraphics`)*
  * [`fig_4_feature_target_workflow.png`](fig_4_feature_target_workflow.png) *(generated 300-DPI raster PNG)*
* **Suggested Thesis Number:** **Figure 4.1** *(tentative placeholder label `fig:stage31-workflow`)*
* **Suggested Caption:** *Causal workflow for Stage 3.1 feature, eligibility, and target construction at forecast origin $t$, illustrating strict isolation between historical predictors ($y \le t$) and future growth targets ($y \in [t+1, t+3]$).*
* **Chapter & Subsection Placement:** **Chapter 4 (Methodology), Sections 4.3–4.4** — Panel-to-Origin Aggregation, Causal Eligibility Gate, and Target Construction.
* **What the Reader Should Learn:**
  1. Historical publication data ($y \le t$) feeds both the origin eligibility gate ($\sum_{[t-2, t]} P_{\text{Global}} \ge 50$) and all predictive feature vectors (`M0–M3` plus sensitivities), with zero upward flow from the future evaluation window.
  2. Future publications ($y \in [t+1, t+3]$) enter solely into the adjusted growth target $G_{\text{adj}}(i, t)$ (alongside downward-only `[t-2, t]` base normalization counts), and are stored strictly in a separate target vector (`g_adj`) isolated from all predictor sets `X`.
  3. All 1,025 topics per origin are retained with an explicit Boolean eligibility flag in Stage 3.1 (`7,175 × 42`), leaving training/test subset filtering cleanly to Stage 3.2.
* **Authoritative Source:** `AGENTS.md`, `openalex_feasibility_audit/CHAPTER4_METHODOLOGY_MASTER_SPEC.md` (Sections 3, 6, 7), `stage3_modeling/stage3_feature_target_manifest.json`, and `stage3_modeling/stage3_feature_target_audit_report.md`.
* **Editability Status:** `fig_4_feature_target_workflow.py` is **directly editable**; `.svg`, `.pdf`, and `.png` are **generated** identically from that single script.

---

## Reproducibility Commands

```bash
python -B stage3_modeling/thesis_assets/build_thesis_tables.py
python -B stage3_modeling/thesis_assets/fig_4_feature_target_workflow.py
python -B stage3_modeling/thesis_assets/build_stage3_2_thesis_assets.py
```

---

## Stage 3.2 Thesis Assets (Derived Strictly from Audited Stage 3.2 Splits)

### 5. Temporal Split, Topic-Grouped CV, and RQ3 Cohort Summary Table
* **Files:**
  * [`table_4_temporal_split_and_rq3_pool.csv`](table_4_temporal_split_and_rq3_pool.csv)
  * [`table_4_temporal_split_and_rq3_pool.tex`](table_4_temporal_split_and_rq3_pool.tex)
* **Generator Script:** [`build_stage3_2_thesis_assets.py`](build_stage3_2_thesis_assets.py)
* **Suggested Thesis Number:** **Table 4.x** *(Chapter 4 Methodology; tentative label `tab:stage32-splits-rq3`)*
* **Suggested Caption:** *Temporal Train/Test Partitions, Topic-Grouped Cross-Validation Structure, and RQ3 Cohort Filtering Summary for Test Forecast Origins 2018 and 2021.*
* **Chapter & Subsection Placement:** **Chapter 4 (Methodology), Sections 4.6–4.7** — Temporal Train/Test Split, Topic-Grouped CV, and RQ3 Remaining Pool Filtering.
* **Authoritative Source:** `stage3_modeling/stage3_2_splits/stage3_2_splits_manifest.json` and `stage3_modeling/stage3_2_splits/stage3_2_splits_audit_report.md` (`22/22 PASS`).

### 6. Temporal Backtesting & Empirical RQ3 Cohort Partition Figure
* **Files:**
  * [`fig_4_temporal_split_and_rq3_design.svg`](fig_4_temporal_split_and_rq3_design.svg)
  * [`fig_4_temporal_split_and_rq3_design.pdf`](fig_4_temporal_split_and_rq3_design.pdf)
  * [`fig_4_temporal_split_and_rq3_design.png`](fig_4_temporal_split_and_rq3_design.png)
* **Generator Script:** [`build_stage3_2_thesis_assets.py`](build_stage3_2_thesis_assets.py)
* **Suggested Thesis Number:** **Figure 4.x** *(Chapter 4 Methodology; tentative label `fig:stage32-splits-rq3`)*
* **Suggested Caption:** *Leakage-free expanding backtesting timeline (2010–2024) and empirical RQ3 high-growth cohort partitioning on verified eligible test topics at Forecast Origins 2018 ($N=992$) and 2021 ($N=995$).*
* **Chapter & Subsection Placement:** **Chapter 4 (Methodology), Sections 4.6–4.7**.
* **Authoritative Source:** Plotted 100% from real Stage 3.2 verified files (`test_2018.csv`, `test_2021.csv`, `rq3_pool_2018.csv`, `rq3_pool_2021.csv`, `stage3_2_splits_manifest.json`).
