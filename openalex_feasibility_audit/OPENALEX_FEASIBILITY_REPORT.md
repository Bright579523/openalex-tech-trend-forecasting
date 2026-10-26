# OpenAlex Thesis Data Feasibility Audit Report (Final Targeted Review)

**Working Title:** *Forecasting Emerging Technology Research Trends: A Comparative Study of Germany, China, and Japan Using OpenAlex Data*  
**Degree Program:** Master of Science in Data Science (120 ECTS)  
**Submission Target Date:** 12 February 2027 (~15.7 weeks remaining)  
**Lead Auditor:** Senior Research Engineer & Data Scientist  
**Date of Audit:** 25 October 2026 (Final Targeted Review Pass)  
**Audited Directory:** [`d:/Thesis/openalex_feasibility_audit`](file:///d:/Thesis/openalex_feasibility_audit)  
**Detailed Technical Note:** [`AUDIT_CORRECTIONS.md`](file:///d:/Thesis/openalex_feasibility_audit/AUDIT_CORRECTIONS.md)  

---

## 1. Executive Summary & Final Feasibility Decision

### Overall Decision: **CONDITIONAL PASS**

Following a final targeted review of taxonomy boundaries, origin-specific eligibility, RCA denominator conceptualization, counting rules, baseline consistency, and evaluation dependence, the proposed Master’s thesis dataset and evaluation design are **feasible, methodologically sound, and achievable within the 12 February 2027 deadline**, conditional on one zero-cost operational step:
> **Operational Condition:** The candidate must register for a **free OpenAlex API Key** (no credit card required) to unlock the **$1.00/day allowance (10,000 list calls/day)**. The unauthenticated `mailto` pool is capped at $0.10/day (~1,000 calls), which is insufficient for the 4,100 calls required for the full panel extraction.

```
+----------------------------------------------------------------------------------------------------+
|                                FINAL FEASIBILITY AUDIT SCORECARD                                   |
+------------------------------------+------------------+--------------------------------------------+
| Evaluation Dimension               | Evidence Status  | Final Verified Finding                     |
+------------------------------------+------------------+--------------------------------------------+
| 1. Taxonomy Universe Definition    | VERIFIED FACT    | Fixed 1,025 topics across 5 Tech fields    |
| 2. Origin-Specific Eligibility     | MEASURED FACT    | 985 (2012), 990 (2015), 992 (2018),        |
|                                    |                  | 996 (2021) qualify at >= 50 past works     |
| 3. Primary RCA Definition          | METHOD DECISION  | All-Science RCA adopted; captures national |
|                                    |                  | prioritization across scientific economy   |
| 4. Country Counting Strategy       | METHOD DECISION  | Whole Counting retained for feasibility;   |
|                                    |                  | co-authorship documented as limitation     |
| 5. Baseline Consistency            | CALCULATION      | M0 Momentum defined as 3yr window growth,  |
|                                    |                  | matching target G(i, t) functional form    |
| 6. Primary Evaluation Origins      | METHOD DECISION  | Folds 2018 & 2021 primary (non-overlapping |
|                                    |                  | outcomes); rolling origins acknowledged    |
| 7. API Pricing & Pagination        | VERIFIED FACT    | per_page max is 100; free API key provides |
|                                    |                  | $1.00/day (10k calls); job cost is $0.41   |
| 8. Full Universe Extraction Time   | MEASURED (TEST)  | ~6.8 minutes for all 1,025 topics          |
+------------------------------------+------------------+--------------------------------------------+
```

---

## 2. OpenAlex Access, Pricing, and Pagination Limits

### 2.1 Official Pricing and Rate Limits
- **Documentation Source:** [OpenAlex Pricing & API Limits](https://docs.openalex.org)
- **Current Freemium Pricing:**
  - **Single Entity by ID/DOI:** Free.
  - **List & Filter Queries (including `group_by`):** **$0.0001 per call** ($0.10 per 1,000 calls).
  - **Search (full-text):** $0.001 per call.
- **Daily Quotas:**
  - **Unauthenticated (`mailto` only):** Capped at **$0.10/day** ($\approx 1,000$ list calls) at 10 req/s.
  - **Free API Key (Registered User):** Grants **$1.00/day for free** (resets midnight UTC, no payment method required) at **30 requests per second**.
- **Master Panel Extraction Budget:**
  - Total queries for 1,025 topics $\times$ 4 queries = **4,100 calls**.
  - Operational Cost: $4,100 \times \$0.0001 = \mathbf{\$0.41}$.
  - Under a free API key, this consumes **41% of the daily $1.00 free credit**, resulting in **$0.00 out-of-pocket financial cost**.
  - *Operational Requirement:* Registering for a free API key is mandatory because unauthenticated requests will be throttled after ~1,000 calls.

### 2.2 Pagination Rules and Fractional Counting Engineering Burden
- **Maximum `per_page` Parameter:** OpenAlex strictly enforces a maximum `per_page` limit of **`100`** on list endpoints.
- **Engineering Assessment of Optional Fractional Counting:**
  - Total technology works (2010–2024): **23,245,477 works**.
  - At 100 works per page: $23,245,477 / 100 = \mathbf{232,455 \text{ API calls}}$.
  - Runtime: At 10 req/s, download takes **$\approx 6.46 \text{ hours}$** of continuous transfer (or $\approx 2.15 \text{ hours}$ at 30 req/s under an API key).
  - Pagination Requirement: Because basic page-based pagination cannot exceed 10,000 results (`page * per_page <= 10000`), downloading all works requires implementing **deep cursor pagination (`cursor=*`)**.
  - Storage Overhead: $\approx 23.25\text{M} \times 3\text{ KB} \approx \mathbf{70 \text{ GB}}$ of raw JSON.
- *Methodological Decision:* Whole counting via server-side aggregation (4,100 calls, 6.8 minutes, 0 GB local storage) is firmly retained.

---

## 3. Technology Scope and Origin-Specific Eligibility

### 3.1 Fixed Taxonomy Universe (1,025 Topics)
The main study retains the **fixed 1,025 topics** mapped to the 5 technology fields in the CWTS Leiden taxonomy:
- **Engineering:** 560 topics
- **Computer Science:** 302 topics
- **Materials Science:** 123 topics
- **Energy:** 27 topics
- **Chemical Engineering:** 13 topics

### 3.2 Full-Universe Measurement of Origin-Specific Eligibility
Topics must not be filtered using total 2010–2024 cumulative volume (which introduces lookahead bias). Instead, eligibility is evaluated strictly using observable historical volume in the 3-year observation window:

$$P_{\text{past}}(i, t) = \sum_{y=t-2}^t P_{\text{global}}(i, y) \ge 50 \text{ works}$$

Actual publication volumes were measured across all 1,025 topics ([`full_universe_origin_eligibility.csv`](file:///d:/Thesis/openalex_feasibility_audit/full_universe_origin_eligibility.csv)):

| Origin ($t$) | Past 3-Yr Window | Topics $\ge 30$ Works | Topics $\ge 50$ Works | Topics $\ge 100$ Works | Median 3-Yr Volume |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **2012** | 2010–2012 | 990 / 1025 (96.6%) | **985 / 1025 (96.1%)** | 977 / 1025 (95.3%) | 3,048 works |
| **2015** | 2013–2015 | 992 / 1025 (96.8%) | **990 / 1025 (96.6%)** | 984 / 1025 (96.0%) | 3,425 works |
| **2018** | 2016–2018 | 995 / 1025 (97.1%) | **992 / 1025 (96.8%)** | 986 / 1025 (96.2%) | 3,501 works |
| **2021** | 2019–2021 | 997 / 1025 (97.3%) | **996 / 1025 (97.2%)** | 990 / 1025 (96.6%) | 3,389 works |

*Empirical Verification:* At the proposed threshold of $\ge 50$ works ($\approx 17$ papers/year), **985 to 996 topics qualify origin-by-origin** with zero future leakage.

---

## 4. Reconciled Counting Strategy and Missing Data Audit

### 4.1 Missing Primary Topic Audit
- **Global Corpus (All Fields, 2010–2024, `type:article|conference-paper|review`):**
  - Total Works: **102,811,351**
  - Works with Valid Primary Topic: **100,859,931 (98.10%)**
  - Works with Missing Primary Topic (`primary_topic.id:null`): **1,951,420 (1.90%)**
- **Technology Universe:** 23,245,477 works (23.05% of assigned works globally). Because works lacking primary topics carry no field attributes, they cannot be partitioned by field filters. The unassigned topic rate is strictly **1.90% globally**.

### 4.2 Whole Counting Policy and Co-Authorship Limitation
- **Counting Rule:** Whole Counting credits 1 full count to country $c$ if at least one author affiliation belongs to country $c$.
- **Explicit Limitation:** International co-authorships are credited fully to each participating nation. In highly collaborative fields, national counts and RCA may be slightly elevated relative to nations with predominantly domestic research. Whole counting is retained for feasibility, but international co-authorship must be documented as an explicit limitation in Chapter 3.

### 4.3 Quantitative Affiliation Country Coverage (Measured)
Measured on an empirical sample of **800 work-level records** across 2010, 2015, 2020, and 2024:
- **Works with matched institutions:** **96.1%** (769 / 800)
- **Works with VALID country code:** **95.9%** (767 / 800)
- **Works with NO usable country code:** **4.1%** (33 / 800)
- *Status:* **MEASURED (SAMPLE)**. Affiliation data exhibits **$95.9\%$ empirical completeness**.

---

## 5. Primary RCA Definition: All-Science Research Specialization

### 5.1 Formulation and Conceptual Rationale
Because the thesis investigates national research specialization across Germany, China, and Japan, national priorities must be normalized against the **entire scientific economy** (competing against medicine, biology, and social sciences):

$$RCA_{\text{AllSci}}(c, i, t) = \frac{P_{c, i, t} \;/\; P_{c, \text{AllSci}, t}}{P_{\text{glob}, i, t} \;/\; P_{\text{glob}, \text{AllSci}, t}}$$

### 5.2 Substantive Interpretation vs. Tech-Restricted RCA
- **All-Science RCA ($RCA_{\text{AllSci}}$ - Adopted as Sole Primary Feature):**  
  Captures macro-level national funding and policy priority. China dedicates **49.5%** of its national scholarly output to technology (compared to 24.9% globally). As a result, China’s mean $RCA_{\text{AllSci}}$ across technology topics is **$2.080$** (median: $1.897$, max: $7.318$), reflecting its systemic national prioritization of technology over life or social sciences. Germany’s mean is **$1.293$** and Japan’s mean is **$1.492$**.
- **Tech-Restricted RCA ($RCA_{\text{Tech}}$):**  
  Measures only internal portfolio allocation *conditional on a paper being in technology* (means: DE 1.096, CN 1.031, JP 1.072).
- *Methodological Decision:* The main model will keep **only one RCA definition: All-Science RCA ($RCA_{\text{AllSci}}$)**. The prior claim that correlation above 0.99 makes Ridge coefficients invariant has been removed, as regularized shrinkage ($L_2$ penalty) alters coefficient paths under different scaling.

---

## 6. Consistent Baseline and Evaluation Origin Design

### 6.1 Reconciled Momentum Baseline
The target is the 3-year window-to-window growth:
$$G(i, t) = \log(1 + P_{\text{future}}(i, t)) - \log(1 + P_{\text{past}}(i, t))$$
where $P_{\text{past}}(i, t) = \sum_{y=t-2}^t P_{\text{global}}(i, y)$ and $P_{\text{future}}(i, t) = \sum_{y=t+1}^{t+3} P_{\text{global}}(i, y)$.

To ensure exact functional consistency, the **M0 Momentum Baseline** is defined as growth between two consecutive 3-year aggregate windows:
$$M_{\text{window}}(i, t) = \log(1 + P_{\text{past}}(i, t)) - \log(1 + P_{\text{prior}}(i, t))$$
where $P_{\text{prior}}(i, t) = \sum_{y=t-5}^{t-3} P_{\text{global}}(i, y)$.  
All models are evaluated against the identical target $G(i, t)$ using MAE.

### 6.2 Primary Non-Overlapping Benchmark Origins
Because window momentum requires 6 historical years $[t-5, t]$, the earliest valid origin is **$t = 2015$** (requiring historical data from 2010 to 2015).

To prevent statistical dependence caused by overlapping target horizons, the **primary benchmark** evaluates non-overlapping test folds:
1. **Test Origin 2018 (Target: 2019–2021):**
   - **Training Set:** Origin 2015 ($N_{\text{train}} = 990$ topics; outcome 2016–2018 fully observable by end of 2018).
2. **Test Origin 2021 (Target: 2022–2024):**
   - **Training Set:** Origins 2015..2018 ($N_{\text{train}} \approx 3,960$ pooled topic observations under expanding window, or 2 non-overlapping training origins 2015 and 2018 with $N_{\text{train}} \approx 1,980$).

#### Fold-Level Pilot Results ([`model_pilot_results_allsci_consistent.csv`](file:///d:/Thesis/openalex_feasibility_audit/model_pilot_results_allsci_consistent.csv)):
```
Fold-Level Evaluation (50-Topic Pilot Panel, Consistent Baseline & All-Sci RCA)
─────────────────────────────────────────────────────────────────────────────
Model                             Origin 2018 (MAE / Prec@5)  Origin 2021 (MAE / Prec@5)
─────────────────────────────────────────────────────────────────────────────
M0: Consistent Window Momentum        0.2017 / 0.60 (3.0x)        0.2315 / 0.60 (3.0x)
M1: Global History Ridge               0.2122 / 0.40 (2.0x)        0.2518 / 0.60 (3.0x)
M2: Country Counts Ridge               0.2609 / 0.20 (1.0x)        0.2571 / 0.40 (2.0x)
M3: All-Science Specialization Ridge   0.2564 / 0.40 (2.0x)        0.2246 / 0.40 (2.0x)
─────────────────────────────────────────────────────────────────────────────
```
*Note on Dependence:* If annual rolling origins (2015..2021, 7 folds) are reported, overlapping 3-year outcomes introduce serial correlation across test errors. Therefore, annual rolling metrics must be designated as supplementary sensitivity checks, with the non-overlapping folds (2018 and 2021) serving as the primary benchmark.

---

## 7. Corrected Top 5 Critical Risks & Practical Mitigations

| Rank | Risk Description | Severity | Practical Mitigation |
| :---: | :--- | :---: | :--- |
| **1** | **API Rate-Limit Throttle Without Key:** Unauthenticated calls capped at $0.10/day (~1k calls). | **High** | Register for a **free OpenAlex API Key** to secure $1.00/day allowance (10,000 list calls/day). |
| **2** | **International Co-Authorship Inflation:** Whole counting double-counts international papers. | **Moderate** | State Whole Counting rule consistently; document co-authorship as an explicit limitation. |
| **3** | **Retrospective Classifier Semantics:** Qwen3-8B classifier classifies historical texts with modern text representations. | **Moderate** | State clearly that OpenAlex measures topic *substantive aboutness*; freeze taxonomy IDs. |
| **4** | **Temporal Outcome Overlap:** Training on origin $t-1$ when forecasting $t$ causes target leakage. | **High** | Strictly enforce the condition $t_{\text{train}} \le t_{\text{test}} - 3$; use non-overlapping folds as primary benchmark. |
| **5** | **Sparse Topic Instability:** Rare topics create extreme, noisy RCA spikes. | **Moderate** | Enforce origin-specific filter $P_{\text{past}}(i, t) \ge 50$ works in past window $[t-2, t]$; handle zero denominators gracefully. |

---

## 8. Summary of Evidence Levels

1. **Verified Facts:**
   - OpenAlex API rate limits and pricing ($0.0001/list call; $1.00/day free with API key; max `per_page` = 100).
   - Global corpus size (102,811,351 works; 1.90% null primary topic rate).
   - Technology universe size (23,245,477 works across 5 fields; 1,025 mapped topics).
   - Taxonomy structure (CWTS Leiden: 4 domains, 26 fields, 252 subfields, 4,516 topics).
2. **Measured Facts (Full Universe):**
   - Origin-specific eligibility: 985 (2012), 990 (2015), 992 (2018), 996 (2021) topics qualify at $\ge 50$ works.
3. **Measured Samples:**
   - Work-level country affiliation completeness: **95.9%** (4.1% missing across 800 sampled works).
4. **Methodological Decisions:**
   - Retain **Whole Counting** with documented co-authorship limitations.
   - Adopt **All-Science RCA ($RCA_{\text{AllSci}}$)** as the sole primary specialization feature.
   - Adopt **3-year window-to-window growth** as the consistent M0 Momentum baseline.
   - Designate **Folds 2018 and 2021** as the primary non-overlapping benchmark.

---

## 9. Immediate Action Items

1. **Register for Free OpenAlex API Key:** Obtain key at [OpenAlex](https://openalex.org).
2. **Execute Master Panel Extraction:** Run the 4,100-call production script using the API key to pull all 1,025 topics across 2010–2024 into `openalex_master_panel_1025topics.csv`.
3. **Begin Proposal Writing:** Draft Chapter 1 (Introduction) and Chapter 3 (Methodology) using the verified parameters.
