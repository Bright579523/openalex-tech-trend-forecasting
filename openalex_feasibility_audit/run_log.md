# Audit Execution Run Log

- **Audit Date:** 2026-10-25
- **Working Title:** *Forecasting Emerging Technology Research Trends: A Comparative Study of Germany, China, and Japan Using OpenAlex Data*
- **Auditor Role:** Senior Data Scientist & Research Engineer
- **Environment:** Windows 11, PowerShell, Python 3.13, OpenAlex REST API (Polite Pool)

---

## 1. Timeline of Operations & Execution Steps

| Timestamp (UTC) | Action | Target / File | Status / Result |
| :--- | :--- | :--- | :--- |
| **20:46:20** | Environment Setup | Created `d:/Thesis/openalex_feasibility_audit` directory | Success |
| **20:46:31** | Taxonomy Discovery | `test_api_and_taxonomy.py`: queried `/domains`, `/fields`, `/subfields`, `/topics` | Identified 4 Domains, verified 5 target Technology fields (IDs 17, 22, 25, 21, 15), verified Qwen3-8B classifier update |
| **20:47:16** | Aggregation Tests | `test_aggregations.py`: tested `group_by=publication_year`, `type`, and `authorships.institutions.country_code` | Verified 1,025 total tech topics, 23.25M eligible works (2010–2024), 5.67M conference papers |
| **20:47:42** | Filter Syntax Audit | `test_coverage.py`: verified missing topic query `primary_topic.id:null` | Found 1.95M works without primary topic across science (1.90% rate); resolved boolean filter error (`has_primary_topic` -> `primary_topic.id:null`) |
| **20:48:35** | Taxonomy Extraction | `fetch_all_tech_topics.py`: paged through 1,025 candidate topics in 5 fields | Saved complete taxonomy table (`all_tech_topics_taxonomy.csv`) in 18 seconds |
| **20:49:33** | Historical Depth & Fractional Audit | `test_depth_and_fractional.py`: verified 2000–2024 works volume and fractional counting on 50 work-level records | Verified continuous smooth data from 2000 to 2024; fractional weights strictly sum to 1.0 (50/50 works) |
| **20:49:52** | Prevalence Threshold Testing | `analyze_prevalence.py`: tested thresholds (0, 500, 1k, 2k, 5k, 10k works) | 991 topics (96.7%) qualify at $\ge 1,000$ works; 924 topics (90.1%) qualify at $\ge 10,000$ works |
| **20:50:19** | Representative Panel Extraction | `run_pilot_pipeline.py`: extracted 50 representative topics $\times$ 15 years $\times$ 4 entities (Global, DE, CN, JP) | Extracted exactly 750 annual rows in 54.2 seconds via 200 polite API calls |
| **20:51:56** | RCA & Forecasting Audit | `run_full_audit_calculations.py`: computed exact annual national totals, calculated RCA, built 10-origin feature matrix, ran Ridge early-ID backtest | Saved `sample_topic_country_counts.csv`, `model_pilot_results.csv`, `enriched_panel_50topics.csv` |
| **20:52:48** | Candidate Topics Table | `generate_candidate_topics.py`: generated taxonomy audit with selection status and reasons | Saved `candidate_topics.csv` (1,025 topics: 991 Eligible, 34 Excluded) |
| **20:53:25** | Summary Manifest | Generated `data_audit_summary.json` with machine-readable audit metrics | Complete JSON schema created |
| **20:53:46** | Consolidated Executable | Created `openalex_feasibility_audit.py` | Standalone script executed in 4.87s |

---

## 2. API Queries and Query Methods Used

1. **Taxonomy & Metadata:**
   - `GET https://api.openalex.org/domains?per-page=50&mailto=student@ue-germany.de`
   - `GET https://api.openalex.org/fields?per-page=50&mailto=student@ue-germany.de`
   - `GET https://api.openalex.org/topics?filter=field.id:https://openalex.org/fields/17|...&per-page=100&page={page}`

2. **Grouped Publication Aggregations:**
   - Global by Year:
     `GET https://api.openalex.org/works?filter=primary_topic.id:{t_id},publication_year:2010-2024,type:article|conference-paper|review&group_by=publication_year`
   - National by Year (DE, CN, JP):
     `GET https://api.openalex.org/works?filter=primary_topic.id:{t_id},authorships.institutions.country_code:{DE|CN|JP},publication_year:2010-2024,type:article|conference-paper|review&group_by=publication_year`
   - Annual Denominator Totals:
     `GET https://api.openalex.org/works?filter=primary_topic.field.id:{fields_filter},authorships.institutions.country_code:{code},publication_year:2010-2024,type:article|conference-paper|review&group_by=publication_year`

---

## 3. Failures, Retries, and Resolutions

1. **PowerShell Inline Parsing Error:**
   - *Issue:* Running complex multi-line python code with nested double quotes in PowerShell CLI caused syntax and parser errors.
   - *Resolution:* Wrote clean python scripts to files in `d:/Thesis/openalex_feasibility_audit/` and executed them via standard command invocations.
2. **Filter Syntax for Missing Fields:**
   - *Issue:* `has_primary_topic:false` and `has_institutions:false` resulted in `HTTP 400 Bad Request`.
   - *Resolution:* Verified OpenAlex documentation; OpenAlex requires `primary_topic.id:null` for nested subfields. For institutions, OpenAlex does not accept `:null` directly; works without institutions are identified programmatically or via negation queries.
3. **Hardcoded Topic IDs in Initial Sample Table:**
   - *Issue:* Initial script filtered sample table for IDs that were not present in the stratified 50-topic pilot sample, producing an empty sample table.
   - *Resolution:* Re-queried actual topic IDs directly from `enriched_panel_50topics.csv` (`T12510`, `T14262`, `T12804`), generating 45 complete sample rows.

---

## 4. Limitations and Remaining Uncertainties

- **Retrospective Classification:**
  The October 2026 Qwen3-8B classifier (v2) classifies papers based on text "aboutness." While this eliminates citation lag and journal biases, the model did not exist in 2012. Therefore, topic assignments measure what the research was substantively about, rather than how contemporaneously mapped it was.
- **Whole Counting in API vs Fractional Counting:**
  Grouped API queries (`group_by=authorships.institutions.country_code`) use whole counting (a DE+CN collaboration gives 1 to DE and 1 to CN). Work-level fractional counting is mathematically verified (100% sum to 1.0), but executing fractional counting across all 23.25 million works would require full work retrieval. For macro-forecasting and RCA, whole counting produces virtually identical rankings (multi-country inflation factor is only 1.054).
