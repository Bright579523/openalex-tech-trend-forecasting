# Chapter 4 Methodology Master Specification & Decision Lock

> **Purpose:** Consolidated factual reference compiling all verified metadata from the Approved Proposal, `AGENTS.md`, Stage 2 Audit Reports, Primary Synchronized Dataset, Git Repository, and Python Environment — including the **Final Methodology Decision Lock** (Decisions 1–4 and pre-declared sensitivity/diagnostic protocols) governing Chapter 4 and Stage 3 implementation.  
> **Date:** 12 November 2026 (Decisions 1–4 locked 11 Nov 2026; Section 7 Implementation Lock added 12 Nov 2026)<br>
> **Status:** Stage 2 Data Frozen (`29/29` Audit Checks PASS) | **Methodology & Implementation Spec (Decisions 1–4 + Section 7): LOCKED (12 Nov 2026)** | **Stage 3 Modeling Code: NOT YET WRITTEN**

---

## 1. Proposal Alignment & Post-Proposal Supervisor Directives

Source: [`Thesis_Proposal_Watcharapon_Anaketanaset_v2.re.pdf`](file:///d:/Thesis/Documents/Thesis_Proposal_Watcharapon_Anaketanaset_v2.re.pdf) & [`AGENTS.md`](file:///d:/Thesis/AGENTS.md)

| Item | Approved Proposal (`v2.re`) | Current Locked Status (`AGENTS.md` / Stage 2) | Note for Chapter 4 |
| :--- | :--- | :--- | :--- |
| **Title** | *Does National Specialisation Help Forecast Research-Topic Growth? Evidence from Germany, China, and Japan Using OpenAlex* | Identical | — |
| **Research Questions** | **RQ1:** Topic & specialisation development (DE, CN, JP)<br>**RQ2:** Do counts & RCA improve forecasts beyond global history? Does RCA add beyond counts?<br>**RQ3:** Identify future high-growth topics not already high-growth at forecast date | Identical | Must map directly to Chapter 4 analyses |
| **Study Scope** | 2010–2024; 5 fields (~1,000 topics); `article\|conference-paper\|review`; DE, CN, JP + Global | **1,025 topics** (Eng 560, CS 302, MatSci 123, Energy 27, ChemEng 13); 15,375 rows | Exact numbers verified |
| **Topic Classifier** | 6 Oct 2026 new OpenAlex classifier only; freeze data, record download date & version | Fine-tuned **Qwen3-8B** classifier (6 Oct 2026) + Work-type update (15 Jul 2026) | Downloaded 4 Nov 2026 |
| **Eligibility Rule** | $\ge 50$ global works in previous 3 years at forecast date (past data only) | $\sum_{y=t-2}^{t} P_{\text{Global}}(i, y) \ge 50$ | **992** (2018), **995** (2021) on Sync v2 |
| **Target Growth** | Log ratio next 3 yrs vs prev 3 yrs, minus same ratio for all of OpenAlex | $G_{\text{adj}}(i, t)$ using `ln(1+x)` and Selected Scholarly Work Types $W$ | Adjusted by Global All-Science |
| **Country Counting** | Whole counting (*"counts once for each country"*; noted as limitation) | **Upgraded per Supervisor Directive:** Country-level equal fractional counting **$1/k$** (Option C) primary; Whole counting retained as auxiliary baseline | Explicitly cite supervisor feedback |
| **Test Origins** | Two non-overlapping test periods: `2019–2021` (origin `2018`) & `2022–2024` (origin `2021`) | **Strictly Origins 2018 & 2021** | Matches proposal 100% |
| **Metrics** | **RQ2:** MAE<br>**RQ3:** Exclude top 20% past growth; among rest, future top 20% = high-growth (20% chance); count hits in Top 50; Bootstrap CIs by topic | Identical (+ `Precision@50` / Hit Count out of 50) | Locked: Paired Topic Bootstrap ($B = 5,000$, `seed = 42`, 95% Percentile CI); Actual Chance Level reported |

---

## 2. Reconciled Data Facts & Audit Summary (Sections 4.2, 4.3, 4.8)

All metrics below are **directly measured** on [`openalex_modeling_panel_1025topics_v2_synchronized.csv`](file:///d:/Thesis/openalex_feasibility_audit/openalex_modeling_panel_1025topics_v2_synchronized.csv) and [`all_science_national_denominators_fractional_v2_live_recheck_20261105.csv`](file:///d:/Thesis/openalex_feasibility_audit/all_science_national_denominators_fractional_v2_live_recheck_20261105.csv):

* **Primary Modeling Dataset:** `openalex_feasibility_audit/openalex_modeling_panel_1025topics_v2_synchronized.csv`
  * **Dimensions:** `15,375` rows × `26` columns (`1,025` topics × `15` years `2010–2024`).
  * **SHA-256:** `f0049cd71f5ba8545c2e3cbb850e036a7b849828321cd23aa1d04771e60d7175`
* **Synchronized All-Science Denominators:** `openalex_feasibility_audit/all_science_national_denominators_fractional_v2_live_recheck_20261105.csv`
  * **SHA-256:** `9c2d9cccee65c156494b96447ce53045d43e514c74aa10ec9f1c85915b33afce`
* **Preserved Auxiliary / Sensitivity Files:**
  * Original pre-sync Modeling Panel v2: `openalex_modeling_panel_1025topics_v2_selected_types.csv` (`SHA-256: 3d869014...`)
  * All-Types Baseline Master Panel v1: `openalex_master_panel_1025topics.csv` (`SHA-256: 37de2b5d...`)
* **Retrieval Provenance & Deduplication Reconciliation:**
  * Topic counts pulled: `2026-11-04 23:08:40–23:52:46 UTC+1` (4,102 API calls: 1,025 topics × 4 queries + 2 pre-flight).
  * Synchronized denominators pulled: `2026-11-04 23:54:00–23:55:36 UTC+0` (`00:54–00:55 UTC+1`, 5 Nov 2026).
  * Both topic counts and synchronized denominators were retrieved **after** OpenAlex's 4 November 2026 deduplication merge (>17.3M duplicate works merged). OpenAlex does not provide a formal snapshot ID, so provenance is documented via timestamps, query filters, and deterministic synchronization.
  * Correlation of $RCA_{\text{AllSci}}^{\text{Frac}}$ before vs. after denominator sync across all 15,375 rows: **DE:** $r = 0.99983$, **CN:** $r = 0.99986$, **JP:** $r = 0.99987$.
* **15-Year Publication Totals (Sync Panel v2, 1,025 Topics, `2010–2024`):**
  * **Global (`global_count`):** `22,510,971` works
  * **Germany (DE):** Whole = `722,798` | Fractional = `544,660.64` (Retention = `75.35%`)
  * **China (CN):** Whole = `4,653,398` | Fractional = `4,189,429.44` (Retention = `90.03%`)
  * **Japan (JP):** Whole = `816,615` | Fractional = `714,234.85` (Retention = `87.46%`)
* **Zero-Volume Topics Note (Reconciled Precision):**
  * Across `2010–2021`: **21 topics** have 0 works in Sync Panel v2 (20 in Panel v1).
  * Across `2010–2024`: **20 topics** have 0 works in Sync Panel v2 (1 topic began publishing in 2022–2024).
* **Automated Verification Gate (`independent_audit_v2.py`):** **29 / 29 checks PASS (`exit 0`)**, `0` nulls across `399,750` panel cells, `0` duplicate `(topic_id, year)` rows, $0 \le P_{\text{Frac}} \le P_{\text{Whole}}$ everywhere, maximum RCA recalculation discrepancy $\le 0.00000500$ across all `92,250` RCA cells.

---

## 3. Exact Locked Equations (Target, Momentum, Counting, RCA)

### 3.1 Country-Level Equal Fractional Counting (Option C: $1/k$)
$$FC_{w,c} = \frac{1}{k_w}, \qquad P^{\text{Frac}}_{c,i,t} = \sum_{k \ge 1} \frac{N_{c,i,t,k}}{k}$$
where $k_w$ is the number of distinct affiliated countries on work $w$, and $N_{c,i,t,k}$ is the number of Selected Scholarly Works (`article`, `conference-paper`, `review`) assigned to `primary_topic` $i$ in year $t$ with country $c$ and exactly $k$ distinct countries.

### 3.2 Fractional All-Science RCA ($RCA_{\text{AllSci}}^{\text{Frac}}$)
$$RCA_{\text{AllSci}}^{\text{Frac}}(c, i, t) = \frac{P^{\text{Frac}}_{c,i,t} \,/\, P^{\text{Frac}}_{c,\text{AllSci},t}}{P_{\text{Global},i,t} \,/\, P_{\text{Global},\text{AllSci},t}}$$
Both topic counts (numerator) and national all-science denominators employ the identical $1/k$ fractional counting rule and Selected Scholarly Work Types scope.

### 3.3 Origin-Specific Historical Eligibility
$$P^{(i)}_{[t-2, t]} = \sum_{y=t-2}^{t} P_{\text{Global}}(i, y) \ge 50$$

### 3.4 Target Variable ($G_{\text{adj}}$) & Aligned Benchmark ($M0_{\text{adj}}$)
Let $P^{(i)}_{[a,b]} = \sum_{y=a}^{b} P_{\text{Global}}(i, y)$ and $W_{[a,b]} = \sum_{y=a}^{b} P_{\text{Global},\text{AllSci},y}$:
$$G_{\text{adj}}(i, t) = \left[\ln\left(1 + P^{(i)}_{[t+1, t+3]}\right) - \ln\left(1 + P^{(i)}_{[t-2, t]}\right)\right] - \left[\ln\left(1 + W_{[t+1, t+3]}\right) - \ln\left(1 + W_{[t-2, t]}\right)\right]$$
$$M0_{\text{adj}}(i, t) = \left[\ln\left(1 + P^{(i)}_{[t-2, t]}\right) - \ln\left(1 + P^{(i)}_{[t-5, t-3]}\right)\right] - \left[\ln\left(1 + W_{[t-2, t]}\right) - \ln\left(1 + W_{[t-5, t-3]}\right)\right]$$
Exact window-level Global All-Science sums $W_{[a,b]}$ in Sync v2:
* $W_{[2010,2012]} = 17,486,265$
* $W_{[2013,2015]} = 19,552,552$
* $W_{[2016,2018]} = 19,796,237$
* $W_{[2019,2021]} = 20,398,266$
* $W_{[2022,2024]} = 20,127,715$

---

## 4. Resolution of the `AGENTS.md` Origin 2015 Confusion & Complete Eligibility Counts

GPT flagged a wording conflict in `AGENTS.md` regarding Origin 2015. Here is the exact root-cause reconciliation:

* **Root of wording confusion:**
  * In `AGENTS.md` Section 2.E, the bullet heading says *"Why Earlier Origins (2012, 2015) are Excluded"* (meaning excluded **as Test Origins**), while Line 80 correctly states: *"Origin 2015 is retained as a training origin for Test Origin 2018 (its outcome window 2016–2018 is fully observed by the 2018 forecast origin). It is not a test origin because no earlier eligible training origin exists (a 2012 origin would need momentum data from 2007–2009)."*
  * Similarly, an earlier draft sentence in `STAGE2_DATASET_AUDIT_REPORT.md` (Section 5.B) ambiguously stated *"origins 2012 and 2015 cannot be utilized"*, referring only to **test** evaluation (and was later clarified in `DATA_PREPARATION_DRAFT_v3.md` and Git commit `155255e`).
* **Mathematical Fact on the 2010–2024 Panel:**
  * A complete training/test observation at origin $t$ requires $[t-5, t-3] \ge 2010 \implies t \ge 2015$ and $[t+1, t+3] \le 2024 \implies t \le 2021$.
  * Thus, all valid origins in the 15-year panel are $t \in \{2015, 2016, 2017, 2018, 2019, 2020, 2021\}$.
  * Under the leakage-free cutoff $t_{\text{train}} \le t_{\text{test}} - 3$:
    * **For Test Origin 2018** (target `2019–2021`): ONLY **`t_train = 2015`** is available (`[2010–2012]` momentum base, `[2013–2015]` recent past, `[2016–2018]` target outcome — fully known before 2019!).
    * **For Test Origin 2021** (target `2022–2024`): Any $t_{\text{train}} \in \{2015, 2016, 2017, 2018\}$ is leakage-free ($t_{\text{train}} + 3 \le 2021$).

### Measured Origin-by-Origin Counts on Sync Panel v2

| Origin ($t$) | Momentum Window $[t-5, t-3]$ | Recent Window $[t-2, t]$ | Outcome Window $[t+1, t+3]$ | Eligible Topics ($\ge 50$) | % of 1,025 | Median 3-Yr Vol | RQ3 Non-HG Pool (80%) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **2015** *(Train for 2018 & 2021)* | 2010–2012 | 2013–2015 | 2016–2018 | **990** | 96.59% | 3,280 | 792 |
| **2016** *(Train for 2021)* | 2011–2013 | 2014–2016 | 2017–2019 | **990** | 96.59% | 3,402 | — |
| **2017** *(Train for 2021)* | 2012–2014 | 2015–2017 | 2018–2020 | **991** | 96.68% | 3,330 | — |
| **2018** *(Test 1 / Train for 2021)* | 2013–2015 | 2016–2018 | 2019–2021 | **992** | 96.78% | 3,391 | **793** |
| **2021** *(Test 2)* | 2016–2018 | 2019–2021 | 2022–2024 | **995** | 97.07% | 3,315 | **796** |

*Summary Sample Sizes (Locked Decision 1 — Option A):*
* **Test Origin 2018:** $N_{\text{train}} = \mathbf{990}$ (Origin `2015`), $N_{\text{test}} = \mathbf{992}$ (RQ3 eval pool $= \mathbf{793}$).
* **Test Origin 2021:** $N_{\text{train}} = \mathbf{3,963}$ pooled topic–origin observations across Origins `2015–2018` (`990 + 990 + 991 + 992`), $N_{\text{test}} = \mathbf{995}$ (RQ3 eval pool $= \mathbf{796}$).

---

## 5. Actual Implementation & Environment Facts (Section 4.8)

Because **Stage 3 has not started**, no modeling script or Ridge hyperparameter value exists in the repository yet (the old Stage 1 pilot script was not committed and its outputs were cleaned up in `21d0dec`). Current verified runtime environment:

* **Python:** `3.13.2` (`MSC v.1942 64 bit (AMD64)`, Windows 11)
* **Libraries:** `pandas 2.2.3`, `numpy 2.2.4`, `scikit-learn 1.8.0`, `scipy 1.17.0`
* **Git Repository:** `https://github.com/Bright579523/openalex-tech-trend-forecasting.git` (active branch `main`; Methodology Decision Lock commit `c9f9de0`)
* **Existing Production / Audit Scripts:** `extract_master_panel_1025topics.py`, `extract_modeling_panel_v2_selected_types.py`, `openalex_feasibility_audit/extract_denominators_v2.py`, `openalex_feasibility_audit/synchronize_modeling_panel_v2.py`, `openalex_feasibility_audit/independent_audit_v2.py`.

---

## 6. Methodology Decision Lock

All four core methodological design choices and four implementation protocols below are **OFFICIALLY LOCKED** prior to Stage 3 implementation and Chapter 4 drafting. Any future modification may only occur due to documented empirical data anomalies or technical implementation constraints, never post-hoc result optimization.

---

### Decision 1 — Training Origins (LOCKED · Option A)

* **Test Origin 2018** (evaluating outcome window `2019–2021`):
  * **Training Origin:** `2015` ($N_{\text{train}} = \mathbf{990}$ eligible topic observations; $N_{\text{test}} = \mathbf{992}$ eligible topics).
* **Test Origin 2021** (evaluating outcome window `2022–2024`):
  * **Training Origins:** Expanding Annual Origins $t_{\text{train}} \in \{2015, 2016, 2017, 2018\}$ ($N_{\text{train}} = 990 + 990 + 991 + 992 = \mathbf{3,963}$ pooled topic–origin observations; $N_{\text{test}} = \mathbf{995}$ eligible topics).
* **Methodological & Statistical Conditions:**
  1. **Zero Temporal Leakage into Test Period:** Every training origin satisfies $t_{\text{train}} + 3 \le t_{\text{test}}$, ensuring all training target windows ($[t_{\text{train}}+1, t_{\text{train}}+3] \le 2021$) are completely observed at or before the forecast origin.
  2. **Pooled Topic–Origin Structure:** For Test Origin 2021, the `3,963` rows represent pooled topic–origin observations across four consecutive annual origins (`2015–2018`) with partially overlapping 3-year outcome windows inside the training period (not `3,963` independent topics). Repeated observations of the same topic across training origins are accounted for via topic-grouped cross-validation (`GroupKFold` grouped by `topic_id`) during hyperparameter selection and topic-level bootstrap during evaluation.
  3. **Strict Within-Origin Model Comparison:** Model performance ($\text{MAE}$ for RQ2 and $\text{Hits@50}$ / $\text{Precision@50}$ for RQ3 across `M0–M3`) must be compared strictly **within each Forecast Origin** (`2018` separately from `2021`), because training sample sizes (`990` vs `3,963`) and evaluation periods (`2019–2021` vs `2022–2024`) differ between the two origins.
  4. **Structural Stability Assumption:** Pooling multiple training origins (`2015–2018`) for Test Origin 2021 rests on the assumption that the relationship between predictors and future adjusted growth is sufficiently stable across the training window; potential temporal drift in underlying relationships is explicitly noted as a study limitation.

---

### Decision 2 — Exact Feature Vector Definitions for M0–M3 (LOCKED · Option C)

The main forecasting specification uses a progressive feature design consisting of 2 global-history features, 3 national publication-count features, and 3 national specialisation features.

* **M0 – Momentum:** Uses the adjusted historical momentum value $M0_{\text{adj}}(i,t)$ directly as an unfitted benchmark prediction ($\hat{G}_{\text{adj}}^{(M0)}(i,t) = M0_{\text{adj}}(i,t)$).
* **M1 – Global History:** Uses $M0_{\text{adj}}(i,t)$ and $\ln\left(1+P_{\text{Global},i,[t-2,t]}\right)$ *(2 features)*.
* **M2 – Country Counts:** Adds the log-transformed three-year fractional publication counts of Germany, China, and Japan: $\ln\left(1+P^{\text{Frac}}_{c,i,[t-2,t]}\right)$ for $c \in \{\text{DE}, \text{CN}, \text{JP}\}$ *(5 features total)*.
* **M3 – National Specialisation (Primary Specification):** Adds the three-year aggregated raw fractional RCA values of Germany, China, and Japan ($RCA^{\text{Frac}}_{c,i,[t-2,t]}$ for $c \in \{\text{DE}, \text{CN}, \text{JP}\}$), calculated using the ratio-of-sums approach *(8 features total)*:
  $$RCA^{\text{Frac}}_{c,i,[t-2,t]} = \frac{\sum_{y=t-2}^{t} P^{\text{Frac}}_{c,i,y} \,\big/\, \sum_{y=t-2}^{t} P^{\text{Frac}}_{c,\text{AllSci},y}}{\sum_{y=t-2}^{t} P_{\text{Global},i,y} \,\big/\, \sum_{y=t-2}^{t} P_{\text{Global},\text{AllSci},y}}$$

Raw RCA is selected as the primary representation because the empirical collinearity diagnostic indicates that its log-transformed version, $\ln(1+RCA)$, is highly explainable by the existing count features. The raw RCA representation provides an alternative relative-specialisation feature that may capture predictive relationships not adequately represented by the linear combination of log-transformed publication counts.

| Feature Added to M2 | $R^2$ Explained by the 4 Log-Count Features in M2 (Origins 2015 / 2018 / 2021) |
| :--- | :---: |
| $\ln\left(1 + RCA^{\text{Frac}}_{\text{DE},i,[t-2,t]}\right)$ | `0.874 – 0.879` |
| $\ln\left(1 + RCA^{\text{Frac}}_{\text{CN},i,[t-2,t]}\right)$ | `0.896 – 0.928` |
| $\ln\left(1 + RCA^{\text{Frac}}_{\text{JP},i,[t-2,t]}\right)$ | `0.888 – 0.900` |
| **Raw** $RCA^{\text{Frac}}_{\text{DE},i,[t-2,t]}$ *(Primary M3)* | **`0.700 – 0.716`** |
| **Raw** $RCA^{\text{Frac}}_{\text{CN},i,[t-2,t]}$ *(Primary M3)* | **`0.741 – 0.782`** |
| **Raw** $RCA^{\text{Frac}}_{\text{JP},i,[t-2,t]}$ *(Primary M3)* | **`0.691 – 0.719`** |

**Sensitivity Analysis (Pre-Declared Closed List for Both RQ2 and RQ3):**  
To prevent post-hoc specification searching, the sensitivity analyses are pre-declared as a **closed list of two specifications**, both evaluated across **RQ2 ($\text{MAE}$) and RQ3 ($\text{Hits@50}$ / $\text{Precision@50}$)**:

| Specification | Feature Vector Definition | Purpose & Scope |
| :--- | :--- | :--- |
| **Main Hierarchy (`M0`, `M1`, `M2`, `M3`)** | `M2` uses $\ln\left(1 + P^{\text{Frac}}_{c,i,[t-2,t]}\right)$; `M3` adds 3-year ratio-of-sums **Raw Fractional RCA** ($RCA^{\text{Frac}}_{c,i,[t-2,t]}$) | Primary specification for RQ2 & RQ3 |
| **Sensitivity 1: `M3-LogRCA`** | Replaces the 3 raw fractional RCA features in `M3` with $\ln\left(1 + RCA^{\text{Frac}}_{c,i,[t-2,t]}\right)$ (compared against primary `M2` and `M3`) | Tests whether main findings depend on the functional transformation of RCA |
| **Sensitivity 2: `Whole-Counting Alternative` (`M2-WC`, `M3-WC`)** | `M2-WC` uses whole-count log volumes $\ln\left(1 + P^{\text{Whole}}_{c,i,[t-2,t]}\right)$; `M3-WC` adds whole-count 3-year ratio-of-sums Raw RCA ($RCA^{\text{Whole}}_{c,i,[t-2,t]}$) | Evaluates sensitivity to fractional ($1/k$) vs. whole counting using a strictly consistent counting basis across both counts and RCA |

* **Explicit Scope Rules for Sensitivity Analysis:**
  1. *Consistent Counting Basis in Whole-Counting Alternative:* `M3-WC` must be paired with `M2-WC` (whole-count national volumes + whole-count RCA), never mixing fractional counts in `M2` with whole-count RCA in `M3`.
  2. *Exclusion of Master Panel v1 (All Types) from Forecasting Sensitivity:* `Master Panel v1 (All Types)` is **not** used as a forecasting sensitivity dataset because the approved thesis scope is strictly defined as Selected Scholarly Work Types (`article|conference-paper|review`) on the synchronized and audited `Modeling Panel v2`.
  3. *No Post-Hoc Additions:* No additional sensitivity specifications will be introduced after observing Stage 3 model results.
  4. *No Winsorization in Primary Specification:* The raw RCA values are not winsorized in the primary specification. Any additional outlier treatment, if ever examined, must be justified and estimated using training data only within each cross-validation fold.

All count and RCA features are aggregated over the three-year historical window $[t-2, t]$ preceding each forecast origin. Ridge models use `StandardScaler` within the cross-validation pipeline, ensuring that scaling parameters are estimated exclusively from each training fold (the target variable $G_{\text{adj}}$ is never standardized).

**Interpretation:** The comparison between M2 and M3 tests whether an RCA-based relative-specialisation representation improves out-of-sample predictive performance beyond global and national publication-count features. It does not imply that RCA contains statistically independent raw information from the underlying publication counts.

---

### Decision 3 — Ridge Hyperparameter Selection & Topic-Grouped Cross-Validation (LOCKED)

* **Cross-Validation Scheme (Identical Across Test Origins 2018 and 2021):**
  * **Splitter:** `GroupKFold(n_splits=5, shuffle=True, random_state=42)` grouped by `groups = topic_id` (requires `scikit-learn >= 1.6`; verified in `scikit-learn 1.8.0`).
  * **Methodological Framing:** Referred to as **Topic-grouped 5-fold Cross-validation for Hyperparameter Selection**. Grouping by `topic_id` ensures that the same research topic never appears simultaneously in both training and validation folds (which is essential when pooling 2015–2018 for Test Origin 2021, and reduces identically to shuffled 5-fold topic CV on the single-origin 2015 training set for Test Origin 2018). Because observations from different training years may still span folds in the 2021 training set, this procedure is strictly for hyperparameter tuning; final forecasting evaluation relies on the strict **Temporal Holdout** at Test Origins `2018` and `2021`.
* **Pipeline & Candidate Grid:**
  * **Pipeline:** `Pipeline([("scaler", StandardScaler()), ("ridge", Ridge())])` so standardization is estimated strictly inside each training fold.
  * **Alpha Grid:** $\alpha \in \operatorname{logspace}(-3, 5, 41)$ ($10^{-3}$ to $10^{5}$, 41 logarithmically spaced values), tuned separately for each model (`M1`, `M2`, `M3`, and pre-declared sensitivity models) and each Test Origin by minimizing mean 5-fold CV MAE (`scoring="neg_mean_absolute_error"`).
  * **Grid Boundary Check:** If any selected $\alpha$ lands on the lower ($10^{-3}$) or upper ($10^{5}$) grid boundary, inspect the validation curve and expand the grid before finalizing.
* **Alpha Tie-Breaking Rule (Callable `refit`):**
  * Because `GridSearchCV` by default selects the first index achieving the best score (which corresponds to the smallest $\alpha$ when the grid is sorted ascending), a custom **callable `refit` rule** is locked:
    1. Identify the minimum mean 5-fold cross-validation MAE ($\text{MAE}_{\min}$) across the 41 candidates.
    2. Among all candidate $\alpha$ values whose mean CV MAE is within an **absolute tolerance of $10^{-12}$ (`1e-12`)** of $\text{MAE}_{\min}$ (i.e., $\text{MAE}(\alpha) \le \text{MAE}_{\min} + 10^{-12}$), select the **largest $\alpha$** (favoring stronger regularization / greater parsimony when validation error is tied).
    3. Persist and archive the complete fold-by-fold CV MAE scores and summary table for all 41 candidate $\alpha$ values for every fitted model.

---

### Decision 4 — RQ3 Filtering, Ranking & Topic-Level Paired Bootstrap Protocol (LOCKED)

* **4.1 Past High-Growth Exclusion (80th Percentile Cutoff):**
  * At each Test Origin $t \in \{2018, 2021\}$, compute the 80th percentile $Q_{0.80}^{\text{Past}}(t)$ of $M0_{\text{adj}}(i, t)$ across all eligible topics (`992` in 2018; `995` in 2021).
  * Exclude topics already in the top 20% of past adjusted growth ($M0_{\text{adj}}(i, t) \ge Q_{0.80}^{\text{Past}}(t)$; exactly `199` topics excluded at each origin, with `0` boundary ties), leaving the **Remaining Pool** of **`793` topics (Origin 2018)** and **`796` topics (Origin 2021)**.
* **4.2 Future High-Growth Definition & Actual Chance Level Reporting:**
  * Within the Remaining Pool, define the future high-growth threshold $Q_{0.80}^{\text{Future}}(t)$ as the 80th percentile of realized future growth $G_{\text{adj}}(i, t)$, and assign the binary indicator $HG_i = \mathbb{I}\left(G_{\text{adj}}(i, t) \ge Q_{0.80}^{\text{Future}}(t)\right)$.
  * Rather than reporting a hard-coded nominal 20.00% baseline, report the **Actual Chance Rate** and **Chance Expected Hits@50** computed from the exact realized number of future high-growth topics $N_{\text{Future HG}}$ in each Remaining Pool:
    $$\text{Actual Chance Rate} = \frac{N_{\text{Future HG}}}{N_{\text{Remaining Pool}}}, \qquad \text{Chance Expected Hits@50} = 50 \times \frac{N_{\text{Future HG}}}{N_{\text{Remaining Pool}}}$$

| Test Origin | Remaining Pool ($N_{\text{Remaining Pool}}$) | Expected Future HG ($N_{\text{Future HG}}$) | Approximate Actual Chance Rate | Approximate Chance Expected Hits@50 |
| :---: | :---: | :---: | :---: | :---: |
| **2018** | `793` | `159` | `20.05%` | `10.03` |
| **2021** | `796` | `160` | `20.10%` | `10.05` |

  *(Final exact counts $N_{\text{Future HG}}$ are confirmed deterministically during Stage 3 execution under the locked quantile and tie rules.)*

* **4.3 Top-50 Ranking Across All Models (M0–M3):**
  * Rank all topics in the Remaining Pool in descending order of predicted growth $\hat{G}_{\text{adj}}^{(M)}(i, t)$ for **all four primary models (`M0`, `M1`, `M2`, `M3`)** (and pre-declared sensitivity models), breaking any exact prediction ties deterministically by ascending `topic_id`.
  * Select the Top 50 ranked topics and compute:
    $$\text{Hits@50} = \sum_{i \in \text{Top50}} HG_i, \qquad \text{Precision@50} = \frac{\text{Hits@50}}{50}$$
  * Explicitly document in Chapter 4 and Chapter 5 that $\text{Hits@50}$ and $\text{Precision@50}$ are two ways of expressing the exact same quantity (count out of 50 vs. proportion), not two independent metrics. Save full topic-level predictions for all models and test origins.
* **4.4 Topic-Level Paired Bootstrap Protocol (`B = 5,000`, `random_state = 42`, 95% Percentile CI):**
  * **RQ2 (MAE & Paired $\Delta\text{MAE}$ Bootstrap):**
    * Resample eligible test topics ($N = 992$ for Origin 2018; $N = 995$ for Origin 2021) with replacement $B = 5,000$ times (`random_state = 42`).
    * Use the **exact same bootstrap topic index draw in replicate $b$ across all models** (`M0–M3` and sensitivity models) to preserve the paired structure.
    * Report the 95% Percentile Confidence Interval (`[2.5th, 97.5th]` percentiles) for each model's MAE and for **paired model differences** (e.g., $\Delta\text{MAE}_{M3 - M2} = \text{MAE}_{M3} - \text{MAE}_{M2}$, where negative values indicate error reduction).
    * *Interpretation Note:* Document explicitly that the RQ2 bootstrap CI measures sampling uncertainty across test topics conditional on the fitted models and fixed out-of-sample predictions (it does not re-estimate Ridge weights or re-select $\alpha$ inside each bootstrap replicate).
  * **RQ3 (`Hits@50` / `Precision@50` Paired Bootstrap):**
    * Resample topics with replacement ($N = 793$ for Origin 2018; $N = 796$ for Origin 2021) **directly within the fixed Remaining Pool** $B = 5,000$ times (`random_state = 42`), using the **identical bootstrap draw across all models**.
    * Keep each topic's out-of-sample prediction $\hat{G}_{\text{adj}}^{(M)}(i, t)$ and realized binary label $HG_i$ fixed at their full-sample values (do **not** recompute past or future 80th-percentile cutoffs inside bootstrap replicates, as evaluation is conditioned on the pre-defined target cohort).
    * Within each bootstrap sample, sort the $N$ sampled topic draws descending by $\hat{G}_{\text{adj}}^{(M)}$ (breaking ties between distinct topics by ascending `topic_id`). Because sampling is with replacement, a topic drawn multiple times in replicate $b$ can occupy multiple positions in that replicate's Top 50 list, which is the standard behavior of sampling with replacement.
    * Compute $\text{Hits@50}$, $\text{Precision@50}$, and paired differences between models across the 5,000 replicates to form 95% Percentile CIs.

---

### Pre-Stage 3 Read-Only Upper-Tail Diagnostic Protocol (Locked Prerequisite)

Before writing any Stage 3 modeling code, execute a read-only diagnostic on the eligible topics of each forecast origin (`2015`, `2018`, `2021`, and `2016–2017`) to inspect the empirical behavior of the 3-year Raw Fractional RCA features:

1. **RCA Distribution Summary:** Report `Median`, `P95`, and `Maximum` of 3-year ratio-of-sums $RCA^{\text{Frac}}_{c,i,[t-2,t]}$ for Germany (`DE`), China (`CN`), and Japan (`JP`).
2. **Scale Dependence Check:** Compute the association (e.g., Spearman rank correlation $\rho$) between Raw RCA and log global topic volume $\ln\left(1 + P_{\text{Global},i,[t-2,t]}\right)$ at each origin.
3. **Upper-Tail Topic Inspection:** Inspect the top-RCA topics in each country to verify whether extreme RCA values occur primarily in smaller topics near the $\ge 50$ global-works eligibility threshold.
4. **Strict Non-Modification Rule:** Do **not** winsorize features and do **not** drop any eligible topics from the primary dataset on the basis of this diagnostic. Its purpose is strictly to understand and document the empirical distribution of RCA prior to modeling, not to alter the data to improve model fit.

---

## 7. Stage 3 Implementation Specification & Statistical Precision Protocol (LOCKED — 12 Nov 2026)

This section locks exact software, numerical, algorithmic, and reporting rules derived from the Pre-Stage 3 Implementation Audit (`pre_stage3_audit`) so that Stage 3 scripts and Chapter 4 text match without ambiguity.

### 7.1 Pre-Implementation Verification & Software Dependency Lock

* **Pre-Stage 3 Read-Only Audit Status:** Verified SHA-256 integrity of primary and auxiliary CSVs, zero missing/infinite values across all eligible feature/target frames (`2015–2021`), exact $W_{[a,b]}$ window sums, exact $G_{\text{adj}}(i, t) = M0_{\text{adj}}(i, t+3)$ identity, `GroupKFold` behavior, RQ3 quantile boundaries, and all whole-count sensitivity inputs.
* **Upper-Tail Raw Fractional RCA Diagnostic Summary (Read-Only Confirmation):** Across Origins `2015` ($N=990$), `2018` ($N=992$), `2021` ($N=995$), and Pooled `2015–2018` ($N=3,963$):
  * Maximum 3-year Raw Fractional RCA values range between `7.1188` and `12.4237` (Origin `2015`: DE `7.1188`, CN `8.4161`, JP `12.4237`; Origin `2018`: DE `9.1964`, CN `9.6911`, JP `10.5157`; Origin `2021`: DE `8.9830`, CN `8.0661`, JP `12.1597`).
  * Spearman rank correlation $\rho$ between Raw Fractional RCA and $\ln(1 + P_{\text{Global},i,[t-2,t]})$ is **positive and statistically significant** in every country and origin (`+0.0835` to `+0.1883`, all $p < 0.01$; Pooled `2015–2018`: DE $\rho = 0.1242$, CN $\rho = 0.1433$, JP $\rho = 0.1244$). Extreme upper-tail values are driven predominantly by well-established, specialized research topics (e.g., `T14146` with `2,968` global works in `2013–2015`; `T11741` with `1,649` in `2016–2018`; `T11347` with `2,828` in `2016–2018`), with only isolated smaller-topic cases (`T14351`, `53` works in JP `2015`). The non-winsorization lock is empirically confirmed.
* **Pinned Software Stack & Minimum Dependency Constraint:**
  * `Python`: `3.13.2`
  * `numpy`: `2.2.4` *(PCG64 default bit generator via `np.random.default_rng`)*
  * `pandas`: `2.2.3`
  * `scipy`: `1.17.0`
  * `scikit-learn`: **`>= 1.6` REQUIRED minimum** *(pinned runtime: `1.8.0`)*. **Explicit constraint:** `GroupKFold(shuffle=True, random_state=...)` was introduced in `scikit-learn 1.6`; running on `< 1.6` will fail with `TypeError`.

---

### 7.2 Topic-Grouped Cross-Validation & Direct Target Leakage Proof

* **Algebraic Target-Leakage Proof ($G_{\text{adj}}(i, t) = M0_{\text{adj}}(i, t+3)$):**
  By construction of the consecutive 3-year window growth equations in Section 3.4, every topic $i$ satisfies:
  $$G_{\text{adj}}(i, t) = M0_{\text{adj}}(i, t+3)$$
  (empirically verified across all `1,025` topics for $t \in \{2015, 2016, 2017, 2018\}$ with $\max |G_{\text{adj}}(i,t) - M0_{\text{adj}}(i,t+3)| = 0.00 \times 10^0$).
  In the pooled `2015–2018` training set for Test Origin `2021` (`3,963` rows across `993` unique topics: `989` appearing in all 4 origins, plus `1` with 3 rows, `1` with 2 rows, and `2` with 1 row), standard row-level `KFold` can place `(Topic A, Origin 2018)` inside a training fold while `(Topic A, Origin 2015)` sits in the corresponding validation fold — exposing the validation target $G_{\text{adj}}(A, 2015)$ directly through the training feature $M0_{\text{adj}}(A, 2018)$. Using `GroupKFold` grouped by `topic_id` therefore eliminates **direct target leakage** inherent in the lag-window formulation, rather than serving merely as a generic grouped-data precaution.
* **Exact Splitter Configuration (Identical Across Both Test Origins):**
  ```python
  cv_splitter = GroupKFold(n_splits=5, shuffle=True, random_state=42)
  ```
  with `groups = train_df["topic_id"]`.
  * *Verified Origin 2018 Behavior (`N_train = 990`, 1 row per topic):* Produces partitions strictly identical to `KFold(n_splits=5, shuffle=True, random_state=42)` (`[198, 198, 198, 198, 198]` topics per fold; `0` cross-fold overlap).
  * *Verified Origin 2021 Behavior (`N_train = 3,963`, `993` unique topics):* Eliminates all cross-fold topic overlap (`0` shared topics between train and validation folds; `[199, 199, 199, 198, 198]` unique topics and `[796, 790, 796, 789, 792]` rows per fold), while `shuffle=True` balances annual origins (`196–199` rows per year in every fold).

---

### 7.3 `GridSearchCV(refit=callable)` Implementation & CV Score Extraction Rule

* **Estimator & Parameter Grid:**
  `Pipeline([("scaler", StandardScaler()), ("ridge", Ridge())])`, `param_grid = {"ridge__alpha": np.logspace(-3, 5, 41)}`, `scoring = "neg_mean_absolute_error"`.
* **Callable `refit` Tie-Breaking Rule (`1e-12` Tolerance, Largest $\alpha$):**
  1. Read `mean_scores = cv_results["mean_test_score"]` (negative MAE).
  2. Identify `best_neg_mae = np.max(mean_scores)`.
  3. Find all candidate indices where `mean_scores >= best_neg_mae - 1e-12` (equivalently, $\text{MAE}(\alpha) \le \text{MAE}_{\min} + 10^{-12}$).
  4. Return the maximum candidate index among tied candidates (selecting the largest $\alpha$ under the ascending `np.logspace(-3, 5, 41)` grid).
* **Critical `scikit-learn` Extraction Rule (Do NOT Access `gs.best_score_`):**
  * In `scikit-learn 1.8.0`, passing a callable to `GridSearchCV(..., refit=callable)` populates `gs.best_index_`, `gs.best_params_`, and `gs.best_estimator_`, **but does NOT populate `gs.best_score_`** (calling `gs.best_score_` raises `AttributeError`).
  * All Stage 3 scripts MUST extract the selected model's 5-fold mean CV MAE via:
    ```python
    cv_mae = -float(gs.cv_results_["mean_test_score"][gs.best_index_])
    ```
  * Persist the full `cv_results_` table (`mean_test_score`, `std_test_score`, `split0_test_score` through `split4_test_score`, and `param_ridge__alpha` for all 41 candidates) for every model and origin.

---

### 7.4 RQ3 Quantile Method, Boundary Inequality (`>=`), & Origin 2021 Exact-Index Behavior

* **Uniform Quantile & Boundary Lock (Applied to Both Past Filtering and Future Classification):**
  * Explicitly invoke NumPy linear interpolation in both steps:
    ```python
    q80 = float(np.quantile(values, 0.80, method="linear"))
    ```
  * **Step 1 (Past High-Growth Exclusion):** Exclude topics with `m0_adj >= Q80_past`, leaving the Remaining Pool strictly `< Q80_past` (`793` topics for Origin 2018; `796` topics for Origin 2021; `0` boundary near-ties within `1e-9` at either origin).
  * **Step 2 (Future High-Growth Assignment):** Within the Remaining Pool, define realized high-growth as:
    ```python
    hg = (rem_df["g_adj"] >= q80_fut).astype(int)
    ```
* **Verified Boundary Counts & Origin 2021 Exact-Index Note:**
  * **Origin 2018 (`N_rem = 793`):** Linear quantile index $(793 - 1) \times 0.80 = 633.60$ interpolates strictly between two adjacent sorted observations; both `>=` and `>` produce **`159` future high-growth topics** (`Actual Chance Rate = 159 / 793 = 20.0504%`, `Chance Expected Hits@50 = 10.0252`).
  * **Origin 2021 (`N_rem = 796`):** Linear quantile index $(796 - 1) \times 0.80 = 636.00$ lands on an **exact sorted data point** (sorted index `636`, `Q80_fut = 0.06890643`, unique boundary value). Applying the locked `>=` criterion yields **`160` future high-growth topics** (`Actual Chance Rate = 160 / 796 = 20.1005%`, `Chance Expected Hits@50 = 10.0503`), whereas strict `>` would yield `159` (`19.9749%`). Per pre-registered discipline, the `>=` rule is retained without modification and explicitly documented in Chapter 4 (Section 4.7).
* **Deterministic Top-50 Ranking Tie-Breaker:** Sort topics in the Remaining Pool descending by $\hat{G}_{\text{adj}}^{(M)}(i, t)$ with ties broken by ascending `topic_id` (`sort_values(by=["pred_g_adj", "topic_id"], ascending=[False, True])`). *(Note: exact `M0_adj` duplicates exist inside the Remaining Pool — 3 duplicate pairs / 6 topics in 2018 and 1 duplicate pair / 2 topics in 2021 — and are deterministically ordered by `topic_id` when evaluating `M0`.)*

---

### 7.5 Paired Topic Bootstrap Protocol (`B = 5,000`, Generator Isolation & Conditional CI Scope)

* **Fixed Parameters:** `B = 5,000` replicates; 95% Percentile CIs computed via explicit `np.percentile(values, [2.5, 97.5], method="linear")`.
* **Per-Evaluation Generator Isolation (`np.random.default_rng(42)`):**
  Instantiate a **fresh** `rng = np.random.default_rng(42)` separately for each `(RQ, Origin)` evaluation suite and draw one integer index matrix (`rng.integers(0, N, size=(5000, N))`) reused across **all** primary (`M0–M3`) and sensitivity (`M3-LogRCA`, `M2-WC`, `M3-WC`) models within that suite:

| Evaluation Suite | Index Matrix Shape | Sampling Pool ($N$) | Fixed Conditioned Quantities |
| :--- | :---: | :--- | :--- |
| **RQ2 – Origin 2018** | `(5000, 992)` | Eligible 2018 test topics | Fitted predictions $\hat{G}_{\text{adj}}^{(M)}$ & realized $G_{\text{adj}}$ |
| **RQ2 – Origin 2021** | `(5000, 995)` | Eligible 2021 test topics | Fitted predictions $\hat{G}_{\text{adj}}^{(M)}$ & realized $G_{\text{adj}}$ |
| **RQ3 – Origin 2018** | `(5000, 793)` | Fixed 2018 Remaining Pool | Realized $HG_i$ & predictions $\hat{G}_{\text{adj}}^{(M)}$ *(no inner $Q_{0.80}$ recompute)* |
| **RQ3 – Origin 2021** | `(5000, 796)` | Fixed 2021 Remaining Pool | Realized $HG_i$ & predictions $\hat{G}_{\text{adj}}^{(M)}$ *(no inner $Q_{0.80}$ recompute)* |

* **Terminology & Statistical Precision on Generator Seeding:** Re-initializing `np.random.default_rng(42)` (`numpy 2.2.4`, PCG64) per `(RQ, Origin)` suite prevents **execution-order dependence** (reordering RQ2 vs. RQ3 or 2018 vs. 2021 calculations does not alter any evaluation table). Because each generator starts from seed `42`, the four matrices share an identical generator initialization rather than forming strictly independent cross-suite random streams; exact paired comparisons within every `(RQ, Origin)` suite remain 100% preserved, and software reproducibility is anchored by pinning `numpy 2.2.4`.
* **Conditional Confidence Interval Interpretation Scope (Explicit Limitation):** Bootstrap 95% Percentile CIs measure **test-topic sampling uncertainty conditional on the fitted Ridge coefficients and tuned $\alpha$ values**. They do **not** reflect estimation variance from refitting regression weights or re-tuning $\alpha$ across bootstrap draws. This conditional scope must be stated explicitly in Chapter 4 and Chapter 5.
* **RQ3 Re-Ranking Rule in Bootstrap Draws:** For replicate $b$, index the Remaining Pool via `matrix[b]`, sort the `N` sampled draws by `(-pred_g_adj, topic_id)`, take the first `50` positions (`[:50]`), and sum `hg` (if a topic is sampled multiple times with replacement, each sampled draw retains its identical `pred_g_adj`, `topic_id`, and `hg` and occupies consecutive slots upon sorting).

---

### 7.6 Chapter 4 Content Distribution & Bibliographic Note

* **Chapter 4 Exposition Plan (Distributing Rationales in Context):**
  * **Section 4.5:** Model hierarchy (`M0–M3` + closed sensitivities), Ridge ($L_2$) regularisation, hyperparameter $\alpha$, and fold-isolated `StandardScaler`.
  * **Section 4.6:** Temporal train/test split (`2015 -> 2018`; `2015–2018 -> 2021`), `GroupKFold` (`n_splits=5`, `shuffle=True`, `random_state=42`) with explicit $G_{\text{adj}}(i,t) = M0_{\text{adj}}(i,t+3)$ target-leakage proof, `MAE`, and conditional Paired Topic Bootstrap (`B = 5,000`, 95% Percentile CI, `method="linear"`).
  * **Section 4.7:** RQ3 emerging-growth evaluation: Past $Q_{0.80}$ exclusion (`>=`), Future $Q_{0.80}$ labeling (`>=`, highlighting Origin 2021 sorted index `636` yielding `160` topics / `20.10%`), Actual Chance Level, Top-50 deterministic ranking tie-breaker, `Hits@50` and `Precision@50` equivalence, and RQ3 conditional paired bootstrap.
  * **Section 4.8:** Consolidated Reproducibility & Environment Summary Table consolidating random seed (`42`), CV folds (`5`), bootstrap replicates (`5,000`), quantile/percentile method (`linear`), pinned software stack (`Python 3.13.2`, `numpy 2.2.4`, `pandas 2.2.3`, `scipy 1.17.0`, `scikit-learn 1.8.0` with `>= 1.6` lower bound), and data/script lineage.
* **Bibliographic Verification Note (`ref.bib`):** Prior to citing Efron & Tibshirani (1993) (*An Introduction to the Bootstrap*, Chapman & Hall) in Section 4.6/4.8, verify the exact edition, ISBN/DOI, and publisher metadata of the specific print/edition cited before inserting into `thesis/ref.bib`.

