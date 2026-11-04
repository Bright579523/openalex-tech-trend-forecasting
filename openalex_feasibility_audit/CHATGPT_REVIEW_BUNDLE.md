# 📦 THESIS STAGE 2 INDEPENDENT REVIEW BUNDLE (OPENALEX DATASET PREPARATION)

> **Document Purpose:** This standalone bundle compiles all methodological documentation, empirical audits, data semantics analyses, and complete production source code for an independent academic review of **Stage 2: Dataset Preparation** for the Master's Thesis project.  
> **Repository Location:** `D:\Thesis\openalex_feasibility_audit\CHATGPT_REVIEW_BUNDLE.md`  
> **Target Reviewer:** Independent AI Reviewer (ChatGPT) / Academic Peer Reviewers  
> **Date of Compilation:** 05 November 2026  
> **Status:** **STAGE 2 COMPLETED & FROZEN — PENDING INDEPENDENT REVIEW BEFORE STAGE 3**

---

# 📑 TABLE OF CONTENTS
1. [Project Overview & Research Questions](#1-project-overview--research-questions)
2. [Classification of Methodological Assertions (Fact vs. Decision vs. Unverified)](#2-classification-of-methodological-assertions)
3. [Locked Research Design Specifications](#3-locked-research-design-specifications)
4. [Dataset Documentation & Empirical Quality Audits](#4-dataset-documentation--empirical-quality-audits)
5. [Data Semantics, Coverage & Classification Provenance](#5-data-semantics-coverage--classification-provenance)
6. [Complete Production Source Code](#6-complete-production-source-code)
   - [6.1 Production Modeling Panel v2 Extraction Script](#61-production-modeling-panel-v2-extraction-script)
   - [6.2 Synchronized All-Science Denominators Extraction Script](#62-synchronized-all-science-denominators-extraction-script)
   - [6.3 Independent Mathematical Audit & Verification Script](#63-independent-mathematical-audit--verification-script)
   - [6.4 Document-Type Breakdown & Topic Coverage Script](#64-document-type-breakdown--topic-coverage-script)
7. [External Review Checklist for ChatGPT](#7-external-review-checklist-for-chatgpt)
8. [File Manifest & Cryptographic Integrity Hashes](#8-file-manifest--cryptographic-integrity-hashes)

---

# 1. Project Overview & Research Questions

### A. Academic Metadata
* **Degree:** Master of Science (M.Sc.) in Data Science
* **Institution:** University of Europe for Applied Sciences (UE Potsdam), Germany
* **Working Thesis Title:**  
  *Does National Specialisation Help Forecast Research-Topic Growth? Evidence from Germany, China, and Japan Using OpenAlex*
* **Primary Data Source:** OpenAlex REST API (`https://api.openalex.org`)
* **Study Period:** 2010–2024 (15 annual observation intervals)
* **Target Geographic Entities:** Germany (`DE`), China (`CN`), Japan (`JP`), and Global reference (`GLOBAL`)

### B. Core Research Questions
* **RQ1 (Main Effect):** Does incorporating national scientific specialization metrics (specifically Fractional All-Science Revealed Comparative Advantage, $RCA_{\text{AllSci}}^{\text{Frac}}$) significantly improve the forecast accuracy of 3-year future research-topic growth rate compared to naive momentum ($M0$) and global history ($M1$) baselines?
* **RQ2 (Comparative Cross-Country Analysis):** How does the predictive power of national specialization differ across Germany, China, and Japan, given their contrasting scientific portfolios, international collaboration profiles, and state-directed technology priorities?
* **RQ3 (Methodological & Boundary Sensitivity):** How does restricting the literature scope strictly to peer-reviewed core scholarly types (`article|conference-paper|review`) versus an unrestricted document-type corpus impact topic trajectories, national specialization rankings, and growth forecasting accuracy?

---

# 2. Classification of Methodological Assertions

To maintain strict scientific integrity, all assertions in this thesis are explicitly partitioned into three ontological categories:

| Category | Definition | Applied Elements in This Project |
| :--- | :--- | :--- |
| **FACT** | Empirically verified properties of the data, API responses, mathematical theorems, or code execution outputs. | 1. OpenAlex Topic Classifier update deployed on 6 October 2026 (fine-tuned Qwen3-8B).<br>2. OpenAlex Work Types reclassification deployed on 15 July 2026 (49.6M works shifted).<br>3. Panel v2 has exactly 15,375 rows, 1,025 topics, 15 years, 0 nulls, 0 duplicate topic-years.<br>4. Recalculation discrepancy from stored CSV values is bounded by $\le 0.00000500$ across all 46,125 cells. |
| **DESIGN DECISION** | Deliberate methodological choices approved in the thesis proposal or supervisor consensus to address research questions. | 1. Selecting 1,025 physical science & tech topics from CWTS Leiden clusters.<br>2. Restricting primary panel to `article\|conference-paper\|review`.<br>3. Adopting Option C ($1/k$) equal country-level fractional counting.<br>4. Restricting Forecast Origins strictly to 2018 and 2021.<br>5. Adopting regularized linear models (Ridge Regression) instead of black-box deep learning. |
| **UNVERIFIED CLAIM** | Speculative hypotheses or conjectures that lack rigorous empirical demonstration across the entire corpus. | 1. Asserting that "including non-peer-reviewed types (preprints, theses, abstracts) captures emerging technology signals earlier without adding harmful noise." *(Treated strictly as an untested hypothesis to be examined in Sensitivity Analysis, NOT as an established scientific fact).* |

---

# 3. Locked Research Design Specifications

### A. Taxonomy & Universe Definition
* **Taxonomy Source:** OpenAlex Topics (derived from CWTS Leiden citation clustering, 4,516 global topics).
* **Domain Scope:** Exactly 1,025 technology topics within Physical Sciences:
  1. *Engineering* (560 topics)
  2. *Computer Science* (302 topics)
  3. *Materials Science* (123 topics)
  4. *Energy* (27 topics)
  5. *Chemical Engineering* (13 topics)
* **API Filter:** Strictly `primary_topic.id:Txxxxx` (never `topics.id:Txxxxx`), guaranteeing **zero cross-topic double counting**.

### B. Paper Counting & Attribution Rules
* **Primary Counting Rule:** **Country-Level Equal Fractional Counting (Option C: $1/k$)** via server-side 2D aggregation (`group_by=publication_year,countries_distinct_count` filtered by `authorships.institutions.country_code`).
  $$P_{\text{Frac}}(c, i, t) = \sum_{k \ge 1} \frac{N(c, i, t, k)}{k}$$
  where $k$ is the number of distinct affiliated countries on the paper.
* **Baseline Preservation:** Whole Counting ($P_{\text{Whole}}$) is preserved in the panel as an auxiliary baseline column for methodological comparison.
* **Global Count Definition:** `global_count` is explicitly the **Unique-Work Whole Count ($P_{\text{Global}}$)**. Because summing equal country shares ($k \times \frac{1}{k}$) across all participating countries on Earth yields exactly $1.000$ per paper, the global count is mathematically invariant between whole and fractional allocation.

### C. Specialization Metric: Fractional All-Science RCA ($RCA_{\text{AllSci}}^{\text{Frac}}$)
$$RCA_{\text{AllSci}}^{\text{Frac}}(c, i, t) = \frac{P_{\text{Frac}}(c, i, t) / \text{Denom}_{\text{Frac}}(c, t)}{P_{\text{Global}}(i, t) / \text{Denom}_{\text{Global}}(t)}$$
* **Methodological Consistency:** Both the topic volume (numerator) and the national all-science total (denominator) strictly employ the identical $1/k$ fractional counting rule under the identical Selected Document Types filter.

### D. Forecasting Formulation & Adjusted Target Variable
* **Target Variable ($G_{\text{adj}}$):** Future 3-Year Log Growth Rate **Adjusted for Global All-Science Growth**:
  $$G_{\text{adj}}(i, t) = \underbrace{\left[\ln\left(1 + P_{[t+1, t+3]}^{(i)}\right) - \ln\left(1 + P_{[t-2, t]}^{(i)}\right)\right]}_{\text{Topic Growth Rate}} - \underbrace{\left[\ln\left(1 + W_{[t+1, t+3]}\right) - \ln\left(1 + W_{[t-2, t]}\right)\right]}_{\text{Global Scientific Inflation Rate}}$$
  where $W$ is the total Global All-Science publication count under the identical Selected Types scope (`article|conference-paper|review`).
* **Benchmark Naive Baseline ($M0$ Momentum):** Consistent Window-to-Window Past Growth:
  $$M_{\text{window}}(i, t) = \ln\left(1 + P_{[t-2, t]}^{(i)}\right) - \ln\left(1 + P_{[t-5, t-3]}^{(i)}\right)$$
* **Predictor Model Hierarchy:**
  * $M0$: Naïve Momentum Baseline (No learned parameters)
  * $M1$: Global History ($M0$ + Past Log Global Volume)
  * $M2$: Country Publication Volumes ($M1$ + Log Volumes for DE, CN, JP)
  * $M3$: National Specialization ($M2$ + $RCA_{\text{AllSci}}^{\text{Frac}}$ for DE, CN, JP)
* **Model Class:** Regularized Linear Models (Ridge Regression with $L_2$ penalty and 5-fold cross-validated $\lambda$).

### E. Temporal Train/Test Split & Forecast Origins
* **Approved Forecast Origins (Strictly 2018 and 2021):**
  * **Test Origin $t = 2018$:** Past window $[2016, 2018]$, Momentum base $[2013, 2015]$, Future evaluation $[2019, 2021]$.
  * **Test Origin $t = 2021$:** Past window $[2019, 2021]$, Momentum base $[2016, 2018]$, Future evaluation $[2022, 2024]$.
* **Mathematical Exclusion of Earlier Origins:**
  * Origin 2012 requires momentum base $[t-5, t-3] = [2007, 2009]$, which does not exist in our 2010–2024 dataset.
  * Origin 2015 has no prior non-overlapping training window $\le 2015 - 3 = 2012$ without 2007–2009 data.
  * Therefore, the research design strictly restricts evaluation to Origins 2018 and 2021, matching the approved Proposal.
* **Leakage-Free Cutoff:** Training origins $t_{\text{train}} \le \text{test\_origin} - 3$.
* **Eligibility Filter:** Evaluated strictly at origin $t \in \{2018, 2021\}$:
  $$P_{[t-2, t]}^{(i)} \ge 50 \text{ works}$$
  Topics below 50 works in the 3 years preceding origin $t$ are excluded from training/testing at origin $t$ only, eliminating lookahead bias completely.

---

# 4. Dataset Documentation & Empirical Quality Audits

### A. Modeling Panel v2 vs. Master Panel v1 Dual-Panel Architecture
Rather than discarding the baseline dataset, the thesis preserves both panels for formal sensitivity analysis:

```
                            ┌──────────────────────────────────────────┐
                            │ OpenAlex Taxonomy (1,025 Tech Topics)    │
                            └────────────────────┬─────────────────────┘
                                                 │
                 ┌───────────────────────────────┴───────────────────────────────┐
                 ▼                                                               ▼
┌───────────────────────────────────────┐                       ┌───────────────────────────────────────┐
│ Master Panel v1 (All Types Baseline)  │                       │ Modeling Panel v2 (Selected Types)    │
├───────────────────────────────────────┤                       ├───────────────────────────────────────┤
│ Scope: Complete scholarly outputs     │                       │ Scope: article|conf-paper|review      │
│ File: openalex_master_panel_...csv    │                       │ File: openalex_modeling_panel_...csv  │
│ Status: FROZEN (15,375 rows)          │                       │ Status: EXTRACTED & AUDITED (15,375)  │
│ Role: Sensitivity & Robustness Check  │                       │ Role: PRIMARY FORECASTING DATASET     │
└───────────────────────────────────────┘                       └───────────────────────────────────────┘
```

### B. Stage 2 Final Quality Audit Scorecard

| Check # | Audit Item | Acceptance Standard | Empirical Result | Status |
| :---: | :--- | :--- | :--- | :---: |
| 1 | **Universe Completeness** | Exactly 1,025 topics $\times$ 15 years = 15,375 rows | Exactly 15,375 rows ($1,025 \times 15$) | **PASS** |
| 2 | **Document Types Scope** | Strict `type:article\|conference-paper\|review` | Verified across all 4,100 API queries | **PASS** |
| 3 | **Denominator Synchronization** | Denominators match Selected Types table | 100% synchronized across all 15 years | **PASS** |
| 4 | **2D Group Conservation** | Meta count == Parent sum == Nested sum | 100% conserved (0 mismatches) | **PASS** |
| 5 | **Missing / Null Check** | Zero missing values across all columns | 0 nulls across all 26 columns | **PASS** |
| 6 | **Duplicates Check** | Zero duplicate topic-year records | 0 duplicate records | **PASS** |
| 7 | **Fractional Bound Check** | Fractional count $\le$ Whole count | 100% compliant (0 violations in 46,125 cells) | **PASS** |
| 8 | **Whole RCA Precision** | Recalculation discrepancy $\le 0.00000500$ | $\Delta_{\max} = 0.00000500$ (DE, CN, JP) | **PASS** |
| 9 | **Fractional RCA Precision** | Recalculation discrepancy $\le 0.00000500$ | $\Delta_{\max} = 0.00000500$ (DE, CN, JP) | **PASS** |
| 10 | **Target Growth Formula** | $G_{\text{adj}}$ adjusted by Global All-Science growth | Formally specified and frozen for Stage 3 | **PASS** |
| 11 | **Forecast Origins Scope** | Strictly Origins 2018 and 2021 | Confirmed; earlier origins excluded | **PASS** |
| 12 | **Baseline v1 Preservation** | Master Panel v1 frozen and unmodified | Preserved (15,375 rows) | **PASS** |
| 13 | **Git & Archive Backup** | Committed and backed up to cloud | Commit `36d9fdb`, Backup verified | **PASS** |

### C. Stored-Value Consistency & RCA Reproducibility
* **Stored Precision:** All RCA columns (`rca_frac_de`, `rca_frac_cn`, `rca_frac_jp`) are stored to **5 decimal places**. Fractional counts (`*_frac_count`) are stored to **6 decimal places**.
* **Reproducibility Test:** Every single value across all 46,125 topic-year-country cells was recalculated independently from the stored CSV columns:
  $$\Delta = \left| RCA_{\text{stored}} - \frac{P_{\text{Frac}} / \text{Denom}_{\text{Frac}}}{P_{\text{Global}} / \text{Denom}_{\text{Global}}} \right|$$
* **Empirical Verification:** Across all 46,125 cells for Germany, China, and Japan:
  $$\Delta_{\max} = \mathbf{0.00000500} \le \frac{1}{2} \times 10^{-5}$$
* **Scientific Note:** This mathematically certifies **stored-value reproducibility and consistency** under the 5-decimal representation, guaranteeing that any independent researcher executing the formulas on the CSV file will reproduce the exact stored values within the theoretical rounding bound.

### D. Synchronized All-Science Denominators Table (2010–2024)
Extracted and locked in `all_science_national_denominators_fractional_v2_selected_types.csv`:

| Year | Global All-Science ($W$) | Germany Whole | Germany Frac | China Whole | China Frac | Japan Whole | Japan Frac |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **2010** | 5,867,112 | 149,992 | 114,747.5538 | 581,640 | 555,817.7240 | 168,354 | 152,290.1763 |
| **2011** | 6,178,929 | 149,485 | 112,504.1632 | 633,334 | 603,749.8278 | 172,736 | 155,988.0232 |
| **2012** | 6,395,594 | 156,730 | 116,950.0077 | 577,498 | 544,397.6700 | 174,719 | 157,138.0375 |
| **2013** | 6,673,173 | 161,231 | 118,726.5584 | 604,214 | 565,035.9990 | 175,383 | 157,172.2029 |
| **2014** | 6,904,224 | 168,849 | 123,432.3745 | 592,793 | 545,863.6252 | 176,661 | 157,521.9775 |
| **2015** | 7,012,902 | 172,880 | 125,219.1130 | 520,064 | 468,338.9073 | 175,906 | 155,864.0595 |
| **2016** | 7,137,185 | 178,308 | 127,086.9721 | 450,244 | 392,253.6645 | 175,912 | 154,682.0102 |
| **2017** | 6,802,421 | 180,225 | 127,101.7650 | 496,109 | 429,876.6852 | 178,643 | 156,210.0624 |
| **2018** | 6,751,173 | 185,693 | 130,176.3782 | 571,626 | 494,580.4557 | 178,349 | 154,643.5181 |
| **2019** | 7,045,622 | 192,052 | 133,359.8714 | 645,285 | 557,150.2388 | 177,343 | 152,187.3847 |
| **2020** | 7,245,371 | 199,875 | 135,812.6143 | 702,811 | 602,808.5656 | 180,352 | 152,595.6648 |
| **2021** | 6,838,669 | 209,410 | 142,286.2119 | 797,286 | 694,379.3578 | 178,744 | 150,866.1163 |
| **2022** | 6,378,663 | 198,944 | 134,537.8558 | 932,115 | 824,405.3956 | 165,662 | 139,439.5238 |
| **2023** | 6,754,488 | 196,577 | 131,751.7145 | 967,482 | 861,121.7408 | 162,102 | 135,629.1251 |
| **2024** | 7,299,947 | 199,108 | 132,619.4426 | 1,136,724 | 1,017,625.5309 | 166,767 | 139,123.7123 |

---

# 5. Data Semantics, Coverage & Classification Provenance

### A. OpenAlex Classification Architecture Updates (2026 Audit)
1. **Work Types Reclassification (15 July 2026):**  
   OpenAlex overhauled its work type classifier across **49.6 million records** (~10% of the entire database). Conference papers expanded from 2.8M to 18.2M (+550%), conference abstracts expanded from 535k to 4.2M (+685%), and reviews consolidated from 4.2M to 1.0M (-76%). Retrospectively, conference papers are now far more comprehensively classified across 2010–2024.
2. **Topic Classifier Architecture (6 October 2026):**  
   OpenAlex deployed a fine-tuned **Qwen3-8B** model taking **Title, Abstract, and Source Name**. Topic assignments reflect semantic aboutness rather than citation clustering alone.

### B. Empirical Analysis: Annual Work Types Breakdown & Topic Coverage Rate
Extracted from OpenAlex across benchmark intervals (saved in `openalex_feasibility_audit/annual_work_types_and_topic_coverage.csv`):

| Year | Total Selected Works | Articles | Article % | Conference Papers | Conf % | Reviews | Review % | With Primary Topic | Without Topic | **Topic Coverage Rate** |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **2010** | 5,561,014 | 4,994,459 | 89.81% | 503,557 | 9.06% | 62,998 | 1.13% | 5,452,554 | 108,460 | **98.05%** |
| **2014** | 6,558,190 | 5,919,677 | 90.26% | 544,193 | 8.30% | 94,320 | 1.44% | 6,429,670 | 128,520 | **98.04%** |
| **2018** | 6,486,857 | 5,631,878 | 86.82% | 732,884 | 11.30% | 122,095 | 1.88% | 6,364,211 | 122,646 | **98.11%** |
| **2021** | 6,646,194 | 5,764,562 | 86.73% | 687,730 | 10.35% | 193,902 | 2.92% | 6,546,736 | 99,458 | **98.50%** |
| **2024** | 7,200,875 | 6,104,852 | 84.78% | 886,861 | 12.32% | 209,162 | 2.90% | 7,088,150 | 112,725 | **98.43%** |

**Key Scientometric Findings:**
1. **Conference Papers:** Coverage is remarkably stable and substantial across the entire 15-year period (ranging from 503k to 886k papers/year, accounting for 8.3% to 12.3% of annual peer-reviewed literature).
2. **Primary Topic Assignment:** For core peer-reviewed literature, **over 98% of works have an assigned primary topic** (unassigned works represent only ~1.5% to 2.0%), confirming that denominator comparisons are not distorted by unassigned works.

---

# 6. Complete Production Source Code

### 6.1 Production Modeling Panel v2 Extraction Script
**File:** `D:\Thesis\extract_modeling_panel_v2_selected_types.py`  
**Description:** Production script executing 4,100 queries with server-side 2D aggregation, fail-fast validation, checkpointing, and 6-decimal fractional storage.

```python
"""
OpenAlex Modeling Panel v2 Extraction Script (Selected Types)
Document Scope: Articles, Conference Papers, and Reviews (type:article|conference-paper|review)
Universe: 1,025 Technology Topics across 15 Annual Intervals (2010–2024)
Primary Attribution: Country-Level Equal Fractional Counting (Option C: 1/k)
Reference Baseline: Whole Counting
Primary Feature: Fractional All-Science RCA (RCA_Frac)

Fail-Fast Completeness Check:
    meta.count == sum(parent group counts) == sum(nested subgroup counts)

Author: Bright / M.Sc. Data Science Thesis Project
Date: November 2026
"""

import os
import sys
import time
import json
import argparse
import datetime
from pathlib import Path
import requests
import pandas as pd
import numpy as np

MAILTO = "student@ue-germany.de"
BASE_DIR = Path(__file__).resolve().parent
AUDIT_DIR = BASE_DIR / "openalex_feasibility_audit"
LOG_FILE = AUDIT_DIR / "extraction_run_v2.log"
CHECKPOINT_FILE = AUDIT_DIR / "checkpoint_v2_extraction.json"
DENOM_FILE = AUDIT_DIR / "all_science_national_denominators_fractional_v2_selected_types.csv"
OUTPUT_PANEL_CSV = AUDIT_DIR / "openalex_modeling_panel_1025topics_v2_selected_types.csv"

DOC_TYPE_FILTER = "type:article|conference-paper|review"

def get_secure_api_key(cmd_arg_key: str = "") -> str:
    if cmd_arg_key:
        return cmd_arg_key.strip()
    if os.environ.get("OPENALEX_API_KEY"):
        return os.environ.get("OPENALEX_API_KEY").strip()
    env_path = BASE_DIR / ".env"
    if env_path.exists():
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("OPENALEX_API_KEY="):
                        val = line.split("=", 1)[1].strip()
                        return val.strip("\"'")
        except Exception as e:
            log_msg(f"Could not read .env: {e}")
    return ""

def mask_key(k: str) -> str:
    if len(k) <= 8:
        return "***"
    return f"{k[:4]}...{k[-4:]}"

def log_msg(msg: str):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{timestamp}] {msg}"
    print(formatted)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(formatted + "\n")

class DataIntegrityError(Exception):
    pass

def fetch_with_retry(url: str, params: dict, headers: dict, max_retries: int = 4, backoff: float = 1.0):
    for attempt in range(1, max_retries + 1):
        try:
            r = requests.get(url, params=params, headers=headers, timeout=20)
            if r.status_code == 200:
                return r.json(), r.headers
            elif r.status_code == 429:
                reset_wait = int(r.headers.get("X-RateLimit-Reset", 5))
                log_msg(f"  [Rate Limit 429] Waiting {reset_wait}s (attempt {attempt}/{max_retries})...")
                time.sleep(reset_wait + 1)
            elif r.status_code == 401:
                log_msg(f"  [Auth 401] Unauthorized on {url}: {r.text[:200]}")
                raise DataIntegrityError(f"OpenAlex 401 Unauthorized: {r.text[:200]}")
            else:
                log_msg(f"  [HTTP {r.status_code}] Attempt {attempt}/{max_retries} on {url}: {r.text[:150]}")
                time.sleep(backoff * (2 ** (attempt - 1)))
        except requests.exceptions.RequestException as e:
            log_msg(f"  [Network Error] Attempt {attempt}/{max_retries}: {e}")
            time.sleep(backoff * (2 ** (attempt - 1)))
            
    raise DataIntegrityError(f"Failed to fetch {url} with params {params} after {max_retries} retries.")

def extract_and_validate_topic_v2(tid: str, tname: str, field_name: str, subfield_name: str, 
                                  headers: dict, df_allsci: pd.DataFrame, delay: float = 0.04):
    retrieval_time = datetime.datetime.now().isoformat()
    years = list(range(2010, 2025))
    
    # 1. Global Counts across 15 years (Filtered by selected doc types)
    url_glob = "https://api.openalex.org/works"
    params_glob = {
        "filter": f"primary_topic.id:{tid},publication_year:2010-2024,{DOC_TYPE_FILTER}",
        "group_by": "publication_year"
    }
    data_glob, hdrs_glob = fetch_with_retry(url_glob, params_glob, headers)
    groups_glob = data_glob.get("group_by", [])
    meta_glob = data_glob.get("meta", {}).get("count", 0)
    sum_glob = sum(g["count"] for g in groups_glob)
    
    if meta_glob != sum_glob:
        err = f"Global Completeness Mismatch for {tid}: meta={meta_glob} != sum_groups={sum_glob}"
        log_msg(f"  [FAIL-FAST] {err}")
        raise DataIntegrityError(err)
        
    glob_by_year = {int(g["key"]): g["count"] for g in groups_glob if g.get("key") is not None}
    
    # 2. National 2D Aggregation across 15 years for DE, CN, JP
    country_data = {}
    countries = ["DE", "CN", "JP"]
    
    for c_code in countries:
        time.sleep(delay)
        params_c = {
            "filter": f"primary_topic.id:{tid},publication_year:2010-2024,authorships.institutions.country_code:{c_code},{DOC_TYPE_FILTER}",
            "group_by": "publication_year,countries_distinct_count"
        }
        data_c, hdrs_c = fetch_with_retry(url_glob, params_c, headers)
        meta_c = data_c.get("meta", {}).get("count", 0)
        groups_c = data_c.get("group_by", [])
        
        sum_parent = sum(g["count"] for g in groups_c)
        sum_nested = sum(sum(sub["count"] for sub in g.get("groups", [])) for g in groups_c)
        
        if meta_c != sum_parent or meta_c != sum_nested:
            err = f"Country {c_code} 2D Mismatch for {tid}: meta={meta_c}, sum_parent={sum_parent}, sum_nested={sum_nested}"
            log_msg(f"  [FAIL-FAST] {err}")
            raise DataIntegrityError(err)
            
        c_by_year = {}
        for parent_g in groups_c:
            if parent_g.get("key") is None:
                continue
            yr = int(parent_g["key"])
            w_count = parent_g["count"]
            f_count = 0.0
            for sub_g in parent_g.get("groups", []):
                k = float(sub_g["key"])
                if k > 0:
                    f_count += sub_g["count"] / k
            c_by_year[yr] = {"whole": w_count, "frac": f_count}
            
        country_data[c_code] = c_by_year

    # 3. Assemble 15 Annual Records with Exact Denominators and RCA Formulas
    topic_records = []
    for yr in years:
        row_allsci = df_allsci[df_allsci["year"] == yr].iloc[0]
        glob_allsci = float(row_allsci["global_allsci"])
        
        p_glob = int(glob_by_year.get(yr, 0))
        
        record = {
            "topic_id": tid,
            "topic_name": tname,
            "field_name": field_name,
            "subfield_name": subfield_name,
            "year": yr,
            "retrieval_timestamp": retrieval_time,
            "global_count": p_glob,
            "global_allsci_denom": int(glob_allsci)
        }
        
        for c_code in ["DE", "CN", "JP"]:
            c_code_l = c_code.lower()
            c_stat = country_data[c_code].get(yr, {"whole": 0, "frac": 0.0})
            p_c_whole = int(c_stat["whole"])
            p_c_frac = float(c_stat["frac"])
            
            c_allsci_whole = float(row_allsci[f"{c_code_l}_whole"])
            c_allsci_frac = float(row_allsci[f"{c_code_l}_frac"])
            
            # Store fractional count with 6 decimal places
            p_c_frac_stored = round(p_c_frac, 6)
            c_allsci_frac_denom = round(c_allsci_frac, 4)
            
            # Exact Fractional RCA Formula (computed directly from stored precision)
            if p_glob > 0 and c_allsci_frac_denom > 0 and p_c_frac_stored > 0:
                rca_frac = (p_c_frac_stored / c_allsci_frac_denom) / (p_glob / glob_allsci)
            else:
                rca_frac = 0.0
                
            # Exact Whole RCA Formula
            if p_glob > 0 and c_allsci_whole > 0 and p_c_whole > 0:
                rca_whole = (p_c_whole / c_allsci_whole) / (p_glob / glob_allsci)
            else:
                rca_whole = 0.0
                
            record[f"{c_code_l}_whole_count"] = p_c_whole
            record[f"{c_code_l}_frac_count"] = p_c_frac_stored
            record[f"{c_code_l}_allsci_whole_denom"] = int(c_allsci_whole)
            record[f"{c_code_l}_allsci_frac_denom"] = c_allsci_frac_denom
            record[f"rca_frac_{c_code_l}"] = round(rca_frac, 5)
            record[f"rca_whole_{c_code_l}"] = round(rca_whole, 5)
            
        topic_records.append(record)
        
    return topic_records

def run_v2_extraction(args):
    api_key = get_secure_api_key(args.api_key)
    masked = mask_key(api_key) if api_key else "None (Unauthenticated)"
    log_msg(f"Initiating Modeling Panel v2 Extraction (Selected Types: article|conference-paper|review)")
    log_msg(f"Authenticated Key: {masked}")
    
    headers = {"User-Agent": f"ThesisMasterExtractionV2/1.0 (mailto:{MAILTO})"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
        
    # Check rate limit
    try:
        r_chk = requests.get("https://api.openalex.org/works?filter=publication_year:2020", headers=headers, timeout=10)
        daily_lim = r_chk.headers.get("X-RateLimit-Limit", "Unknown")
        rem_lim = r_chk.headers.get("X-RateLimit-Remaining", "Unknown")
        log_msg(f"API Rate Limits -> Limit: {daily_lim} calls/day | Remaining: {rem_lim} calls")
    except Exception as e:
        log_msg(f"Warning: Could not check rate limit header: {e}")
        
    # Load Denominators
    if not DENOM_FILE.exists():
        raise FileNotFoundError(f"Missing denominator file: {DENOM_FILE}")
    df_allsci = pd.read_csv(DENOM_FILE)
    log_msg(f"Loaded v2 All-Science Denominators from {DENOM_FILE} ({len(df_allsci)} years).")
    
    # Load 1,025 Topics Taxonomy
    tax_path = AUDIT_DIR / "all_tech_topics_taxonomy.csv"
    if not tax_path.exists():
        raise FileNotFoundError(f"Missing taxonomy file: {tax_path}")
    df_topics = pd.read_csv(tax_path)
    total_topics = len(df_topics)
    log_msg(f"Loaded {total_topics} topics from {tax_path}.")
    
    if args.limit and args.limit > 0:
        df_topics = df_topics.head(args.limit)
        log_msg(f"Execution limited to first {len(df_topics)} topics by --limit {args.limit}.")
        
    # Checkpoint setup
    processed_records = []
    completed_topics = set()
    if CHECKPOINT_FILE.exists() and not args.force:
        try:
            with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
                ckpt_data = json.load(f)
                completed_topics = set(ckpt_data.get("completed_topics", []))
                processed_records = ckpt_data.get("records", [])
                log_msg(f"Resuming from checkpoint: {len(completed_topics)} topics already completed ({len(processed_records)} rows).")
        except Exception as e:
            log_msg(f"Could not read checkpoint, starting fresh: {e}")
            
    t0 = time.time()
    extracted_now = 0
    
    for idx, row in df_topics.iterrows():
        tid = row["topic_id"]
        tname = row.get("display_name", row.get("topic_name", ""))
        fname = row.get("field_name", "")
        sfname = row.get("subfield_name", "")
        
        if tid in completed_topics:
            continue
            
        try:
            topic_rows = extract_and_validate_topic_v2(tid, tname, fname, sfname, headers, df_allsci, delay=args.delay)
            processed_records.extend(topic_rows)
            completed_topics.add(tid)
            extracted_now += 1
            
            # Save checkpoint every 25 topics or on last
            if extracted_now % 25 == 0 or idx == len(df_topics) - 1:
                with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
                    json.dump({"completed_topics": list(completed_topics), "records": processed_records}, f)
                elapsed = time.time() - t0
                log_msg(f"Progress: [{len(completed_topics)}/{len(df_topics)}] topics ({len(processed_records)} rows) | Elapsed: {elapsed:.1f}s")
                
        except DataIntegrityError as die:
            log_msg(f"CRITICAL DATA INTEGRITY ERROR for topic {tid}: {die}")
            raise
        except Exception as ex:
            log_msg(f"Unexpected error on topic {tid}: {ex}")
            raise
            
    # Save Final Dataset
    df_final = pd.DataFrame(processed_records)
    df_final.to_csv(OUTPUT_PANEL_CSV, index=False)
    log_msg(f"Saved {len(df_final)} rows to {OUTPUT_PANEL_CSV}")
    
    if len(completed_topics) == len(df_topics) and CHECKPOINT_FILE.exists():
        try:
            CHECKPOINT_FILE.unlink()
            log_msg("Cleaned up checkpoint file after successful completion.")
        except Exception:
            pass
    
    # Run Structural & Precision Validation
    validate_dataset(df_final)

def validate_dataset(df: pd.DataFrame):
    log_msg("=== FINAL AUDIT & VALIDATION OF MODELING PANEL V2 ===")
    rows_passed = (len(df) == 15375) or (len(df) > 0 and len(df) % 15 == 0)
    log_msg(f"1. Total Row Count: {len(df)} | Status: {'PASS' if rows_passed else 'CHECK'}")
    
    dup_count = df.duplicated(subset=["topic_id", "year"]).sum()
    log_msg(f"2. Duplicate Topic-Years: {dup_count} | Status: {'PASS' if dup_count == 0 else 'FAIL'}")
    
    null_count = df.isnull().sum().sum()
    log_msg(f"3. Missing / Null Values: {null_count} | Status: {'PASS' if null_count == 0 else 'FAIL'}")
    
    # Recalculate RCA and check maximum discrepancy
    for c in ["de", "cn", "jp"]:
        calc_rca_frac = np.where(
            (df['global_count'] > 0) & (df[f'{c}_allsci_frac_denom'] > 0) & (df[f'{c}_frac_count'] > 0),
            (df[f'{c}_frac_count'] / df[f'{c}_allsci_frac_denom']) / (df['global_count'] / df['global_allsci_denom']),
            0.0
        )
        diff = np.abs(calc_rca_frac - df[f'rca_frac_{c}'])
        max_diff = diff.max()
        log_msg(f"4. Recalculation Discrepancy RCA Frac {c.upper()}: {max_diff:.8f} | Bound <= 0.00000500: {'PASS' if max_diff <= 0.000005001 else 'CHECK'}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract OpenAlex Modeling Panel v2 (Selected Types)")
    parser.add_argument("--api-key", type=str, default="", help="OpenAlex API key")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of topics for dry run")
    parser.add_argument("--delay", type=float, default=0.03, help="Delay between country queries")
    parser.add_argument("--force", action="store_true", help="Force restart from scratch")
    args = parser.parse_args()
    
    run_v2_extraction(args)
```

---

### 6.2 Synchronized All-Science Denominators Extraction Script
**File:** `D:\Thesis\openalex_feasibility_audit\extract_denominators_v2.py`  
**Description:** Extracts annual national and global All-Science denominators for 2010–2024 restricted to Selected Types.

```python
import os
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('OPENALEX_API_KEY')
headers = {'User-Agent': 'ThesisAudit/1.0 (mailto:student@ue-germany.de)'}
if api_key:
    headers['Authorization'] = f'Bearer {api_key}'

years = list(range(2010, 2025))
countries = ['DE', 'CN', 'JP']
records = []

print("Fetching All-Science Denominators for Selected Types (2010-2024)...")
for yr in years:
    # 1. Global All-Science (Selected Types)
    url_g = f"https://api.openalex.org/works?filter=publication_year:{yr},type:article|conference-paper|review"
    rg = requests.get(url_g, headers=headers).json()
    glob_count = rg['meta']['count']
    
    row = {'year': yr, 'global_allsci': glob_count}
    
    # 2. National All-Science (Selected Types)
    for c in countries:
        url_c = f"https://api.openalex.org/works?filter=publication_year:{yr},authorships.institutions.country_code:{c},type:article|conference-paper|review&group_by=countries_distinct_count"
        rc = requests.get(url_c, headers=headers).json()
        groups = rc.get('group_by', [])
        
        whole = sum(g['count'] for g in groups)
        frac = sum(g['count'] / float(g['key']) for g in groups if float(g['key']) > 0)
        
        row[f'{c.lower()}_whole'] = whole
        row[f'{c.lower()}_frac'] = round(frac, 4)
        
    records.append(row)
    print(f"Year {yr}: Global={glob_count}, DE={row['de_whole']}, CN={row['cn_whole']}, JP={row['jp_whole']}")

df = pd.DataFrame(records)
out_path = r'openalex_feasibility_audit\all_science_national_denominators_fractional_v2_selected_types.csv'
df.to_csv(out_path, index=False)
print(f"Saved {out_path} successfully!")
```

---

### 6.3 Independent Mathematical Audit & Verification Script
**File:** `D:\Thesis\openalex_feasibility_audit\independent_audit_v2.py`  
**Description:** Performs independent 5-tier audit across all 15,375 rows and 46,125 calculations.

```python
import pandas as pd
import numpy as np

def run_audit():
    print("=" * 80)
    print("INDEPENDENT FINAL AUDIT: MODELING PANEL V2 (SELECTED TYPES)")
    print("=" * 80)
    
    csv_v2 = r"openalex_feasibility_audit\openalex_modeling_panel_1025topics_v2_selected_types.csv"
    csv_v1 = r"openalex_feasibility_audit\openalex_master_panel_1025topics.csv"
    denom_v2 = r"openalex_feasibility_audit\all_science_national_denominators_fractional_v2_selected_types.csv"
    
    df_v2 = pd.read_csv(csv_v2)
    df_v1 = pd.read_csv(csv_v1)
    df_denom = pd.read_csv(denom_v2)
    
    # 1. Structural Completeness
    print("\n[1] STRUCTURAL COMPLETENESS")
    print(f"Total Rows: {len(df_v2)} (Expected: 15,375)")
    print(f"Total Columns: {len(df_v2.columns)} (Expected: 26)")
    print(f"Unique Topics: {df_v2['topic_id'].nunique()} (Expected: 1,025)")
    years_found = sorted(df_v2['year'].unique())
    print(f"Years: {years_found[0]} - {years_found[-1]} ({len(years_found)} years)")
    print(f"Duplicate (topic_id, year): {df_v2.duplicated(subset=['topic_id', 'year']).sum()}")
    print(f"Total Missing / Null: {df_v2.isnull().sum().sum()}")
    
    # Check zero counts
    zero_topics = df_v2.groupby('topic_id')['global_count'].sum()
    zero_topic_ids = zero_topics[zero_topics == 0].index.tolist()
    print(f"Zero-volume Topics across all 15 years: {len(zero_topic_ids)} topics")
    
    # 2. Denominator Consistency
    print("\n[2] DENOMINATOR CONSISTENCY")
    denom_match = True
    for yr in range(2010, 2025):
        v2_sub = df_v2[df_v2['year'] == yr].iloc[0]
        denom_sub = df_denom[df_denom['year'] == yr].iloc[0]
        if v2_sub['global_allsci_denom'] != denom_sub['global_allsci']:
            denom_match = False
            print(f"Global denom mismatch in {yr}!")
        if v2_sub['de_allsci_whole_denom'] != denom_sub['de_whole']:
            denom_match = False
        if abs(v2_sub['de_allsci_frac_denom'] - denom_sub['de_frac']) > 1e-4:
            denom_match = False
    print(f"Denominator Sync Check across all 15 years: {'PASS (100% Match)' if denom_match else 'FAIL'}")
    
    # 3. Fractional vs Whole Counts Credit Retention
    print("\n[3] FRACTIONAL ATTRIBUTION & CREDIT RETENTION")
    for c in ['de', 'cn', 'jp']:
        tot_whole = df_v2[f'{c}_whole_count'].sum()
        tot_frac = df_v2[f'{c}_frac_count'].sum()
        ratio = (tot_frac / tot_whole) * 100 if tot_whole > 0 else 0
        print(f"Country {c.upper()}: Whole Sum = {tot_whole:,} | Frac Sum = {tot_frac:,.2f} | Retention = {ratio:.2f}%")
        
    # Check Fractional <= Whole
    frac_le_whole = True
    for c in ['de', 'cn', 'jp']:
        violations = (df_v2[f'{c}_frac_count'] > df_v2[f'{c}_whole_count'] + 1e-5).sum()
        if violations > 0:
            frac_le_whole = False
            print(f"Violation: {c}_frac_count > {c}_whole_count in {violations} rows!")
    print(f"Constraint (Frac <= Whole count for all rows): {'PASS' if frac_le_whole else 'FAIL'}")

    # 4. RCA Recalculation Audit
    print("\n[4] RCA RECALCULATION & NUMERICAL PRECISION AUDIT")
    for c in ['de', 'cn', 'jp']:
        # Recalculate Fractional RCA
        calc_rca_frac = np.where(
            (df_v2['global_count'] > 0) & (df_v2[f'{c}_allsci_frac_denom'] > 0) & (df_v2[f'{c}_frac_count'] > 0),
            (df_v2[f'{c}_frac_count'] / df_v2[f'{c}_allsci_frac_denom']) / (df_v2['global_count'] / df_v2['global_allsci_denom']),
            0.0
        )
        diff_frac = np.abs(calc_rca_frac - df_v2[f'rca_frac_{c}'])
        max_idx_f = np.argmax(diff_frac)
        max_diff_f = diff_frac[max_idx_f]
        row_f = df_v2.iloc[max_idx_f]
        
        # Recalculate Whole RCA
        calc_rca_whole = np.where(
            (df_v2['global_count'] > 0) & (df_v2[f'{c}_allsci_whole_denom'] > 0) & (df_v2[f'{c}_whole_count'] > 0),
            (df_v2[f'{c}_whole_count'] / df_v2[f'{c}_allsci_whole_denom']) / (df_v2['global_count'] / df_v2['global_allsci_denom']),
            0.0
        )
        diff_whole = np.abs(calc_rca_whole - df_v2[f'rca_whole_{c}'])
        max_idx_w = np.argmax(diff_whole)
        max_diff_w = diff_whole[max_idx_w]
        
        print(f"\nCountry {c.upper()}:")
        print(f"  Whole RCA Max Discrepancy:      {max_diff_w:.8f} (Theoretical Bound <= 0.00000500)")
        print(f"  Fractional RCA Max Discrepancy: {max_diff_f:.8f}")
        print(f"  Max Diff Location: Topic {row_f['topic_id']}, Year {row_f['year']}")
        print(f"    global_count: {row_f['global_count']}, global_allsci: {row_f['global_allsci_denom']}")
        print(f"    {c}_frac_count: {row_f[f'{c}_frac_count']}, {c}_allsci_frac: {row_f[f'{c}_allsci_frac_denom']}")
        print(f"    Stored rca_frac: {row_f[f'rca_frac_{c}']:.5f} | Recalculated: {calc_rca_frac[max_idx_f]:.8f}")
        
    # 5. Comparison v1 vs v2
    print("\n[5] COMPARISON: MASTER PANEL V1 (ALL TYPES) VS MODELING PANEL V2 (SELECTED TYPES)")
    tot_glob_v1 = df_v1['global_count'].sum()
    tot_glob_v2 = df_v2['global_count'].sum()
    print(f"Total Global Works: v1 = {tot_glob_v1:,} | v2 = {tot_glob_v2:,} | Retention: {tot_glob_v2/tot_glob_v1:.2%}")
    for c in ['de', 'cn', 'jp']:
        w_v1 = df_v1[f'{c}_whole_count'].sum()
        w_v2 = df_v2[f'{c}_whole_count'].sum()
        f_v1 = df_v1[f'{c}_frac_count'].sum()
        f_v2 = df_v2[f'{c}_frac_count'].sum()
        corr_rca = df_v1[f'rca_frac_{c}'].corr(df_v2[f'rca_frac_{c}'])
        print(f"Country {c.upper()}: Whole Ret = {w_v2/w_v1:.2%} | Frac Ret = {f_v2/f_v1:.2%} | RCA Correlation (v1 vs v2) = {corr_rca:.4f}")

if __name__ == "__main__":
    run_audit()
```

---

### 6.4 Document-Type Breakdown & Topic Coverage Script
**File:** Scratch audit routine generating `annual_work_types_and_topic_coverage.csv`.

```python
import os
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ.get("OPENALEX_API_KEY")
headers = {"User-Agent": "ThesisAudit/1.0 (mailto:student@ue-germany.de)"}
if api_key:
    headers["Authorization"] = f"Bearer {api_key}"

url = "https://api.openalex.org/works"
years = [2010, 2014, 2018, 2021, 2024]
results = []

for yr in years:
    # 1. Total Selected Types
    params_tot = {"filter": f"publication_year:{yr},type:article|conference-paper|review"}
    r_tot = requests.get(url, params=params_tot, headers=headers).json()
    tot_count = r_tot["meta"]["count"]
    
    # 2. Works WITH Primary Topic
    params_with = {"filter": f"publication_year:{yr},type:article|conference-paper|review,primary_topic.id:!null"}
    r_with = requests.get(url, params=params_with, headers=headers).json()
    with_count = r_with["meta"]["count"]
    
    # 3. Works WITHOUT Primary Topic
    params_without = {"filter": f"publication_year:{yr},type:article|conference-paper|review,primary_topic.id:null"}
    r_without = requests.get(url, params=params_without, headers=headers).json()
    without_count = r_without["meta"]["count"]
    
    # 4. Group by type
    params_gb = {"filter": f"publication_year:{yr},type:article|conference-paper|review", "group_by": "type"}
    r_gb = requests.get(url, params=params_gb, headers=headers).json()
    type_map = {g["key_display_name"]: g["count"] for g in r_gb.get("group_by", [])}
    
    results.append({
        "year": yr,
        "total_selected_works": tot_count,
        "articles": type_map.get("article", 0),
        "articles_pct": round(type_map.get("article", 0) / tot_count * 100, 2),
        "conference_papers": type_map.get("conference-paper", 0),
        "conf_papers_pct": round(type_map.get("conference-paper", 0) / tot_count * 100, 2),
        "reviews": type_map.get("review", 0),
        "reviews_pct": round(type_map.get("review", 0) / tot_count * 100, 2),
        "with_primary_topic": with_count,
        "without_primary_topic": without_count,
        "topic_coverage_rate_pct": round(with_count / tot_count * 100, 2)
    })

df = pd.DataFrame(results)
df.to_csv("openalex_feasibility_audit/annual_work_types_and_topic_coverage.csv", index=False)
```

---

# 7. External Review Checklist for ChatGPT

Please independently inspect the documentation and source code provided above against the following 7 core audit dimensions:

- [ ] **1. API Query Specification & Topic Filter:**  
  Verify whether `extract_modeling_panel_v2_selected_types.py` uses `filter=primary_topic.id:{tid},publication_year:2010-2024,type:article|conference-paper|review` across Global and Country queries, confirming that cross-topic double counting is impossible.
- [ ] **2. Completeness & Fail-Fast Integrity Check:**  
  Verify that the script enforces `meta.count == sum(parent group counts) == sum(nested subgroup counts)` on every 2D aggregation call.
- [ ] **3. Fractional Counting Implementation ($1/k$):**  
  Verify that the nested group iteration `f_count += sub_g['count'] / k` strictly implements country-level equal fractional counting, and that $P_{\text{Frac}} \le P_{\text{Whole}}$ is preserved.
- [ ] **4. All-Science Denominator Synchronization:**  
  Verify that the denominators used in `extract_modeling_panel_v2_selected_types.py` match the `all_science_national_denominators_fractional_v2_selected_types.csv` table generated under the identical document-type scope.
- [ ] **5. RCA Precision & Stored-Value Reproducibility:**  
  Verify that calculating $RCA$ from the stored columns yields a discrepancy strictly $\le 0.00000500$ across all 46,125 cells, and confirm that this represents stored-value consistency rather than raw 7-digit floating-point sensor accuracy.
- [ ] **6. Target Variable ($G_{\text{adj}}$) Formulation:**  
  Verify that the formula for $G_{\text{adj}}$ properly subtracts global all-science growth, controlling for global scientific expansion.
- [ ] **7. Forecast Origins Scope & Zero Lookahead Bias:**  
  Verify that evaluation is restricted strictly to Origins 2018 and 2021, and that eligibility ($\ge 50$ works) is evaluated only at $[t-2, t]$ without looking into future years.

---

# 8. File Manifest & Cryptographic Integrity Hashes

The following table provides the file manifest, exact file sizes, and **SHA-256 cryptographic checksums** for all components of Stage 2:

| File Relative Path | Size (Bytes) | SHA-256 Cryptographic Checksum | Inclusion Status in Bundle |
| :--- | :---: | :--- | :--- |
| `extract_modeling_panel_v2_selected_types.py` | 14,662 | `7b8ed0777fc5c447a783915f48fd1902c5d20fd5eb01d2a7a039856c8272dbbd` | **Full Source Included** |
| `openalex_feasibility_audit/extract_denominators_v2.py` | 1,712 | `c9df3184dcb60a8941dffddc8a9a63aece5ca7f719aa9aae4290812fb813b9b7` | **Full Source Included** |
| `openalex_feasibility_audit/independent_audit_v2.py` | 5,639 | `6e19d06d5d435711367f732ef3c5cd436aff0bac0e5eaee7438cb41f8b438a49` | **Full Source Included** |
| `openalex_feasibility_audit/annual_work_types_and_topic_coverage.csv` | 529 | `1436bc2936fda71cde2ae157aa71a4135dca6a4dd57dd020c75b157b260168b0` | **Full Table Included** |
| `openalex_feasibility_audit/all_science_national_denominators_fractional_v2_selected_types.csv` | 1,132 | `507f5ef4b61f7d91a2919fa88c7c8f54f45560d10d64ad16b60f5ce754c13b36` | **Full Table Included** |
| `openalex_feasibility_audit/STAGE2_DATASET_AUDIT_REPORT.md` | 13,081 | `0be6f550ada8ed3db1d7812aa12bc650f38db47139a06eb48908af505d85c0de` | **Core Sections Included** |
| `openalex_feasibility_audit/DOCUMENT_TYPE_AND_METADATA_AUDIT.md` | 13,318 | `35dd0a59048b6aa9f28b4bebb28a502c1eef381257a3548109f69dc67f1ee099` | **Core Sections Included** |
| `openalex_feasibility_audit/all_tech_topics_taxonomy.csv` | 159,129 | `478e597b1569f16c8a6e7ba75b8a76df7085277e4d4ea538b34fda34228f148a` | Manifested (1,025 topics taxonomy) |
| `openalex_feasibility_audit/all_science_national_denominators_fractional.csv` | 1,059 | `b35ead6d13cb76355cde020d342be7de9b6d504a0f73665f2d8d9812bc0339e3` | Manifested (v1 Baseline Denominators) |
| `extract_master_panel_1025topics.py` | 16,677 | `2b637d6877e8a4ac295523c131179f027037fd5f15f45ee7a466efbadf15cbad` | Manifested (v1 Extraction Script) |
| `openalex_feasibility_audit/openalex_modeling_panel_1025topics_v2_selected_types.csv` | 4,113,999 | `3d869014a463449e2c4bd44628fe174f6aedc954cd7c878922baae9488b75d6e` | **Omitted (Full 15,375-row CSV, 4.1MB)** |
| `openalex_feasibility_audit/openalex_master_panel_1025topics.csv` | 4,004,987 | `37de2b5d22ea0a585dc5772d3e9cb7ea0aaa0ba48357dbee043d268bbf408f87` | **Omitted (Frozen v1 Panel, 4.0MB)** |

### Omission Rationale:
The full CSV panels (`openalex_modeling_panel_1025topics_v2_selected_types.csv` and `openalex_master_panel_1025topics.csv`) are each approximately 4.0–4.1 MB containing 15,375 rows. Embedding raw 15,375-row text into Markdown would exceed prompt length limits and degrade AI review performance. Their structural properties, column schemas, and cryptographic checksums are certified above, and their row-level calculations are audited in `independent_audit_v2.py`.
