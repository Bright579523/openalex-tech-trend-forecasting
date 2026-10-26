# OpenAlex Feasibility Audit: Final Targeted Review and Corrections Note

**Document:** `AUDIT_CORRECTIONS.md`  
**Date:** 25 October 2026 (Final Targeted Review Pass)  
**Auditor:** Senior Research Engineer & Data Scientist  
**Working Title:** *Forecasting Emerging Technology Research Trends: A Comparative Study of Germany, China, and Japan Using OpenAlex Data*  
**Workspace:** [`d:/Thesis/openalex_feasibility_audit`](file:///d:/Thesis/openalex_feasibility_audit)  

---

## 1. Executive Summary of Final Corrections

This document records the final targeted review and corrections to the OpenAlex feasibility audit, addressing topic universe definition, origin-specific eligibility, RCA denominator conceptualization, counting rules, baseline consistency, evaluation origins, and pagination constraints.

### Corrected Feasibility Rating: **CONDITIONAL PASS**
* **Conditions:**
  1. **API Key Registration:** Register for a free OpenAlex API key to access the $1.00/day allowance (10,000 list calls/day) required for the 4,100-call master extraction.
  2. **Taxonomy & Methodological Scope:** Retain the fixed 1,025-topic taxonomy universe, evaluate eligibility origin-by-origin, adopt All-Science RCA as the primary feature, and use Whole Counting with documented international co-authorship limitations.

---

## 2. Detailed Technical Resolutions

### 1. Fixed 1,025-Topic Taxonomy Universe vs. Origin-Specific Eligibility
- **Problem Resolved:** The initial audit screened topics using cumulative 2010–2024 total volume ($\ge 1,000$ works, yielding 991 topics). This introduced lookahead bias by using future publications to select topics for earlier origins (e.g. 2012).
- **Corrected Design:** The study universe is strictly frozen to the **fixed 1,025 topics** belonging to the 5 technology fields in the CWTS Leiden taxonomy. Topic eligibility is determined strictly origin-by-origin using observable historical volume in the past 3-year observation window:
  $$P_{\text{past}}(i, t) = \sum_{y=t-2}^t P_{\text{global}}(i, y) \ge 50 \text{ works}$$
- **Full-Universe Empirical Measurement (Verified across all 1,025 topics):**  
  Rather than extrapolating from the pilot, actual publication volumes across all 1,025 topics were measured via subfield group queries ([`full_universe_origin_eligibility.csv`](file:///d:/Thesis/openalex_feasibility_audit/full_universe_origin_eligibility.csv)):
  - **Origin 2012 (2010–2012 Window):** **985 topics eligible** (96.1% of universe; median volume = 3,048 works)
  - **Origin 2015 (2013–2015 Window):** **990 topics eligible** (96.6% of universe; median volume = 3,425 works)
  - **Origin 2018 (2016–2018 Window):** **992 topics eligible** (96.8% of universe; median volume = 3,501 works)
  - **Origin 2021 (2019–2021 Window):** **996 topics eligible** (97.2% of universe; median volume = 3,389 works)
  - Complete topic-by-topic volume matrix across all 1,025 topics is saved in [`full_1025_topics_historical_volumes.csv`](file:///d:/Thesis/openalex_feasibility_audit/full_1025_topics_historical_volumes.csv).

---

### 2. Adoption of All-Science RCA as Primary Feature
- **Problem Resolved:** The previous note suggested Tech-Restricted RCA ($RCA_{\text{Tech}}$) and claimed that a correlation above 0.99 made Ridge regression coefficients "mathematically invariant." This claim is mathematically incorrect. While two collinear variables have high correlation, feature scaling, collinearity structure, and regularized shrinkage ($L_2$ penalty) alter coefficient paths and predictions.
- **Conceptual Justification for All-Science RCA:**  
  The thesis investigates national research specialization across Germany, China, and Japan. National science policy, university funding, and strategic priorities operate across all fields (competing with medicine, natural sciences, and social sciences).
  $$RCA_{\text{AllSci}}(c, i, t) = \frac{P_{c, i, t} \;/\; P_{c, \text{AllSci}, t}}{P_{\text{glob}, i, t} \;/\; P_{\text{glob}, \text{AllSci}, t}}$$
- **Difference in Substantive Interpretation:**
  - **All-Science RCA ($RCA_{\text{AllSci}}$):** Measures national prioritization relative to the *entire national research output*. China dedicates **49.5%** of its national scholarly output to technology fields (compared to 24.9% globally). As a result, China’s mean $RCA_{\text{AllSci}}$ across technology topics is **$2.080$** (median: $1.897$, max: $7.318$), reflecting its systemic national prioritization of technology. Germany’s mean is **$1.293$** (median: $0.973$) and Japan’s mean is **$1.492$** (median: $1.167$).
  - **Tech-Restricted RCA ($RCA_{\text{Tech}}$):** Measures internal portfolio allocation *conditional on a paper being in technology* (means: DE 1.096, CN 1.031, JP 1.072).
- **Decision:** The main thesis model will keep **only one RCA definition: All-Science RCA ($RCA_{\text{AllSci}}$)**.

---

### 3. Whole Counting Retained with Explicit Limitation
- **Counting Rule:** Whole Counting credits 1 full count to country $c$ if at least one author affiliation belongs to country $c$.
- **Correction of Unsupported Claim:** The assertion that an aggregate country-mention ratio of 1.054 "proves that national rankings are not distorted" has been removed. An aggregate ratio shows overall average co-authorship frequency, but does not rule out localized distortions in highly internationalized subfields (e.g. quantum computing consortia, high-energy materials).
- **Documented Limitation:** Whole counting double-counts international collaborations across all participating countries. Countries with high international co-authorship rates may have publication volume and specialization slightly inflated relative to countries with predominantly domestic authorship. Whole counting is retained strictly as a pragmatic engineering necessity to enable server-side aggregation.

---

### 4. Momentum Baseline Definition Reconciled with Target
- **Target Definition:**
  $$G(i, t) = \log(1 + P_{\text{future}}(i, t)) - \log(1 + P_{\text{past}}(i, t))$$
  where $P_{\text{past}}(i, t) = \sum_{y=t-2}^t P_{\text{global}}(i, y)$ and $P_{\text{future}}(i, t) = \sum_{y=t+1}^{t+3} P_{\text{global}}(i, y)$.
- **Momentum Definition Reconciled:**
  In the prior pilot, momentum was calculated as an annual endpoint change ($P_t$ vs. $P_{t-2}$), which differed in scale and window structure from the target.
  To ensure rigorous benchmarking, the **M0 Momentum Baseline** is defined as the growth between two consecutive 3-year aggregate windows:
  $$M_{\text{window}}(i, t) = \log(1 + P_{\text{past}}(i, t)) - \log(1 + P_{\text{prior}}(i, t))$$
  where $P_{\text{prior}}(i, t) = \sum_{y=t-5}^{t-3} P_{\text{global}}(i, y)$.
- **Consistency:** Both $G(i, t)$ and $M_{\text{window}}(i, t)$ now share identical functional forms (3-year aggregate window vs. 3-year aggregate window). Predicting future growth directly from past window growth represents a true persistent-growth / random-walk benchmark. All models are evaluated against the identical target $G(i, t)$ using MAE.

---

### 5. Primary Evaluation Origins and Statistical Dependence
Because the consistent window-to-window momentum baseline requires 6 historical years $[t-5, t]$, the earliest valid origin is **$t = 2015$** (requiring historical data from 2010 to 2015).

#### Primary Non-Overlapping Evaluation Origins:
To eliminate statistical dependence caused by overlapping target horizons, the **primary benchmark** evaluates non-overlapping test origins:
- **Test Origin 2018 (Target Outcome: 2019–2021):**
  - **Training Origin:** Origin 2015 ($N_{\text{train}} = 990$ topics).
  - Outcome window 2016–2018 is fully observable by end of 2018.
- **Test Origin 2021 (Target Outcome: 2022–2024):**
  - **Training Origins:** Origins 2015..2018 ($N_{\text{train}} \approx 3,960$ pooled topic observations under expanding window, or 2 non-overlapping training origins 2015 and 2018 with $N_{\text{train}} \approx 1,980$).
  - Outcome window 2019–2021 is fully observable by end of 2021.

#### Fold-Level Pilot Results (All-Science RCA + Window Momentum):
Tested on the representative panel ([`model_pilot_results_allsci_consistent.csv`](file:///d:/Thesis/openalex_feasibility_audit/model_pilot_results_allsci_consistent.csv)):
- **Test Fold 2018 ($N_{\text{train}}=50, N_{\text{test}}=50$):**
  - M0 (Momentum Baseline): MAE = $0.2017$, Prec@5 = $0.60$ (Lift = **3.00x**)
  - M1 (Global History Ridge): MAE = $0.2122$, Prec@5 = $0.40$ (Lift = **2.00x**)
  - M2 (Country Counts Ridge): MAE = $0.2609$, Prec@5 = $0.20$ (Lift = **1.00x**)
  - M3 (All-Science Specialization Ridge): MAE = $0.2564$, Prec@5 = $0.40$ (Lift = **2.00x**)
- **Test Fold 2021 ($N_{\text{train}}=200, N_{\text{test}}=50$):**
  - M0 (Momentum Baseline): MAE = $0.2315$, Prec@5 = $0.60$ (Lift = **3.00x**)
  - M1 (Global History Ridge): MAE = $0.2518$, Prec@5 = $0.60$ (Lift = **3.00x**)
  - M2 (Country Counts Ridge): MAE = $0.2571$, Prec@5 = $0.40$ (Lift = **2.00x**)
  - M3 (All-Science Specialization Ridge): MAE = **$0.2246$** (lowest error among all models), Prec@5 = $0.40$ (Lift = **2.00x**)

#### Acknowledgment of Statistical Dependence:
If annual rolling origins (2015..2021, 7 folds) are reported, consecutive test folds evaluate overlapping 3-year outcomes (e.g. 2019–2021 and 2020–2022 share 2 overlapping years), introducing serial correlation across test errors. Therefore, annual rolling metrics must be reported as supplementary sensitivity checks, with the non-overlapping folds (2018 and 2021) serving as the primary benchmark.

---

### 6. Corrected Pagination and Fractional Counting Estimates
- **Maximum `per_page` Parameter:** OpenAlex documentation specifies a maximum `per_page` limit of **`100`** (values of 200 are deprecated and rejected on list endpoints).
- **Corrected Fractional Counting Engineering Burden:**
  - Total technology works (2010–2024): **23,245,477 works**.
  - At 100 works per page: $23,245,477 / 100 = \mathbf{232,455 \text{ requests}}$.
  - Runtime: At 10 req/s, transfer takes **$\approx 6.46 \text{ hours}$** (or $\approx 2.15 \text{ hours}$ at 30 req/s under an API key).
  - Furthermore, because basic pagination (`page * per_page`) cannot exceed 10,000, retrieving all works strictly requires implementing **deep cursor pagination (`cursor=*`)**.
  - Local raw storage required: $\approx 23.25\text{M} \times 3\text{ KB} \approx \mathbf{70 \text{ GB}}$.
- **Conclusion:** Implementing fractional counting introduces substantial engineering friction for a single student. Whole counting via server-side aggregation (4,100 calls, 6.8 minutes, 0 GB storage) is firmly retained.

---

## 3. Corrected Summary Evidence Table

```
+──────────────────────────────────+──────────────────+───────────────────────────────────────────────────────────+
| Audit Dimension                  | Evidence Level   | Corrected Finding                                         |
+──────────────────────────────────+──────────────────+───────────────────────────────────────────────────────────+
| 1. Topic Universe Definition     | VERIFIED FACT    | Fixed 1,025-topic taxonomy universe retained              |
| 2. Origin-Specific Eligibility   | MEASURED FACT    | Full 1,025 topics: 985 (2012), 990 (2015), 992 (2018),   |
|                                  |                  | 996 (2021) qualify at >= 50 historical works              |
| 3. Primary RCA Definition        | METHOD DECISION  | All-Science RCA adopted; measures national priority across|
|                                  |                  | entire scientific economy (China mean 2.08, DE 1.29)      |
| 4. Country Counting Strategy     | METHOD DECISION  | Whole Counting retained; international co-authorship      |
|                                  |                  | documented as an explicit limitation                      |
| 5. Baseline Consistency          | CALCULATION      | M0 Momentum defined as 3yr window-to-window growth,        |
|                                  |                  | matching target G(i, t) functional form                   |
| 6. Primary Evaluation Origins    | METHOD DECISION  | Folds 2018 & 2021 primary (non-overlapping outcomes);     |
|                                  |                  | rolling origins acknowledged as serially dependent        |
| 7. API Pagination Limits         | VERIFIED FACT    | per_page max is 100; fractional requires 232,455 calls    |
+──────────────────────────────────+──────────────────+───────────────────────────────────────────────────────────+
```
