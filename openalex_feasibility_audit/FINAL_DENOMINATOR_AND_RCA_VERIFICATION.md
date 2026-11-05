# Final Verification Report: Modeling Panel Denominator Synchronization & RCA Recalculation

**Document:** `FINAL_DENOMINATOR_AND_RCA_VERIFICATION.md`  
**Repository Location:** `D:\Thesis\openalex_feasibility_audit\FINAL_DENOMINATOR_AND_RCA_VERIFICATION.md`  
**Date:** 05 November 2026  
**Status:** **SYNCHRONIZED PANEL CREATED, RCA RECALCULATED, AND 24/24 AUDIT CHECKS PASSED (`EXIT_CODE=0`)**

---

## 1. Executive Summary & Verification Finding

Before entering Stage 3, a direct row-by-row inspection was conducted on the original Modeling Panel v2 (`openalex_modeling_panel_1025topics_v2_selected_types.csv`) comparing its stored denominator columns (`global_allsci_denom`, `de_allsci_whole_denom`, `de_allsci_frac_denom`, `cn_allsci_whole_denom`, `cn_allsci_frac_denom`, `jp_allsci_whole_denom`, `jp_allsci_frac_denom`) against:
1. The **Old Denominator File** (`all_science_national_denominators_fractional_v2_selected_types.csv`, extracted `2026-11-04T01:09:25Z` / `02:09:25 UTC+1`), and
2. The **New Live-Rechecked Denominator File** (`all_science_national_denominators_fractional_v2_live_recheck_20261105.csv`, extracted `2026-11-04T23:54:00Z` / `2026-11-05 00:54:00 UTC+1`, which matches `annual_work_types_and_topic_coverage.csv` 100.00% across all 15 years).

### Direct Verification Result:
* **Original Modeling Panel v2 (`openalex_modeling_panel_1025topics_v2_selected_types.csv`):**
  * Matches OLD denominators (`2026-11-04T01:09:25Z`): **`True` (100% match across all 15 years and all 7 denominator columns)**
  * Matches NEW live-rechecked denominators (`2026-11-04T23:54:00Z`): **`False`**
  * Its stored RCA values (`rca_whole_*` and `rca_frac_*`) were calculated using the **old denominators** (`2026-11-04T01:09:25Z`), while its topic counts (`global_count`, `*_whole_count`, `*_frac_count`) were extracted 21 hours later (`2026-11-04 23:08–23:52 UTC+1`) after OpenAlex's daily index update.

### Corrective Action Executed:
Following the strict protocol for this case:
1. **Preserved Original Panel Unchanged:** `openalex_modeling_panel_1025topics_v2_selected_types.csv` was preserved 100% untouched (verified via SHA-256: `3d869014a463449e2c4bd44628fe174f6aedc954cd7c878922baae9488b75d6e`).
2. **Created Corrected Synchronized Modeling Panel:** Created [`openalex_modeling_panel_1025topics_v2_synchronized.csv`](file:///d:/Thesis/openalex_feasibility_audit/openalex_modeling_panel_1025topics_v2_synchronized.csv) (`15,375 rows × 26 columns`, SHA-256: `f0049cd71f5ba8545c2e3cbb850e036a7b849828321cd23aa1d04771e60d7175`), replacing all 7 denominator columns across all 15 years (`2010–2024`) with the synchronized post-update denominators from [`all_science_national_denominators_fractional_v2_live_recheck_20261105.csv`](file:///d:/Thesis/openalex_feasibility_audit/all_science_national_denominators_fractional_v2_live_recheck_20261105.csv).
3. **Recalculated All Six RCA Columns:** Recalculated `rca_whole_de`, `rca_frac_de`, `rca_whole_cn`, `rca_frac_cn`, `rca_whole_jp`, and `rca_frac_jp` across all 15,375 rows directly from the stored topic counts and the corrected synchronized denominators (rounded to 5 decimal places).
4. **Executed Strengthened Independent Audit:** Ran [`independent_audit_v2.py`](file:///d:/Thesis/openalex_feasibility_audit/independent_audit_v2.py) across all 24 critical checks. Every single check passed (`EXIT_CODE=0`), and all six country/RCA combinations achieved a maximum recalculation discrepancy of **strictly $\le 0.00000500$**.

---

## 2. Old vs. New Denominator Comparison & Stored Values across All 15 Years (2010–2024)

The table below shows the exact values stored in the **Original Panel v2** (`Old`, extracted `2026-11-04T01:09:25Z`) versus the **Corrected Synchronized Panel v2** (`New`, extracted `2026-11-04T23:54:00Z`) for Global and all three countries (Whole / Fractional):

| Year | Global Denom (`Old` in Orig v2) | **Global Denom (`New` in Sync v2)** | DE Whole / Frac (`Old` in Orig v2) | **DE Whole / Frac (`New` in Sync v2)** | CN Whole / Frac (`Old` in Orig v2) | **CN Whole / Frac (`New` in Sync v2)** | JP Whole / Frac (`Old` in Orig v2) | **JP Whole / Frac (`New` in Sync v2)** |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **2010** | 5,867,112 | **5,561,014** | 149,992 / 114747.5538 | **148,316 / 113467.7288** | 581,640 / 555817.7240 | **566,132 / 540422.2064** | 168,354 / 152290.1763 | **165,887 / 149963.9148** |
| **2011** | 6,178,929 | **5,860,170** | 149,485 / 112504.1632 | **147,881 / 111312.5921** | 633,334 / 603749.8278 | **618,897 / 589404.3100** | 172,736 / 155988.0232 | **169,884 / 153264.1597** |
| **2012** | 6,395,594 | **6,065,081** | 156,730 / 116950.0077 | **155,188 / 115821.5864** | 577,498 / 544397.6700 | **564,707 / 531739.4847** | 174,719 / 157138.0375 | **171,989 / 154558.3620** |
| **2013** | 6,673,173 | **6,332,435** | 161,231 / 118726.5584 | **159,746 / 117669.8252** | 604,214 / 565035.9990 | **589,540 / 550562.0599** | 175,383 / 157172.2029 | **172,775 / 154704.0082** |
| **2014** | 6,904,224 | **6,558,190** | 168,849 / 123432.3745 | **167,129 / 122253.3764** | 592,793 / 545863.6252 | **576,223 / 529554.3707** | 176,661 / 157521.9775 | **174,055 / 155089.3106** |
| **2015** | 7,012,902 | **6,661,927** | 172,880 / 125219.1130 | **170,907 / 123850.1275** | 520,064 / 468338.9073 | **509,514 / 458043.0236** | 175,906 / 155864.0595 | **171,663 / 151816.6634** |
| **2016** | 7,137,185 | **6,791,623** | 178,308 / 127086.9721 | **176,152 / 125660.0072** | 450,244 / 392253.6645 | **448,797 / 391044.3526** | 175,912 / 154682.0102 | **172,408 / 151406.1054** |
| **2017** | 6,802,421 | **6,517,757** | 180,225 / 127101.7650 | **178,183 / 125774.3681** | 496,109 / 429876.6852 | **494,790 / 428841.0172** | 178,643 / 156210.0624 | **175,925 / 153739.0452** |
| **2018** | 6,751,173 | **6,486,857** | 185,693 / 130176.3782 | **183,412 / 128721.1777** | 571,626 / 494580.4557 | **570,086 / 493376.6919** | 178,349 / 154643.5181 | **175,816 / 152386.8515** |
| **2019** | 7,045,622 | **6,781,509** | 192,052 / 133359.8714 | **189,598 / 131881.7076** | 645,285 / 557150.2388 | **643,755 / 555988.6066** | 177,343 / 152187.3847 | **174,602 / 149775.2166** |
| **2020** | 7,245,371 | **6,970,563** | 199,875 / 135812.6143 | **197,462 / 134319.4769** | 702,811 / 602808.5656 | **701,285 / 601652.4807** | 180,352 / 152595.6648 | **177,785 / 150333.8521** |
| **2021** | 6,838,669 | **6,646,194** | 209,410 / 142286.2119 | **207,055 / 140793.9474** | 797,286 / 694379.3578 | **796,298 / 693706.9186** | 178,744 / 150866.1163 | **176,532 / 148922.2773** |
| **2022** | 6,378,663 | **6,278,140** | 198,944 / 134537.8558 | **197,622 / 133738.5022** | 932,115 / 824405.3956 | **931,930 / 824358.1962** | 165,662 / 139439.5238 | **164,259 / 138227.4057** |
| **2023** | 6,754,488 | **6,648,700** | 196,577 / 131751.7145 | **195,261 / 130909.6731** | 967,482 / 861121.7408 | **963,918 / 857997.5045** | 162,102 / 135629.1251 | **160,483 / 134210.7849** |
| **2024** | 7,299,947 | **7,200,875** | 199,108 / 132619.4426 | **198,084 / 131960.3933** | 1,136,724 / 1017625.5309 | **1,134,749 / 1015931.6565** | 166,767 / 139123.7123 | **165,638 / 138134.2242** |

---

## 3. RCA Recalculation & Maximum Discrepancy Across All Six Country/RCA Combinations

In [`openalex_modeling_panel_1025topics_v2_synchronized.csv`](file:///d:/Thesis/openalex_feasibility_audit/openalex_modeling_panel_1025topics_v2_synchronized.csv), all six RCA columns were recalculated across all 15,375 rows using the exact formulas:
$$RCA_{\text{Whole}}(c, i, t) = \text{round}\left(\frac{P_{\text{Whole}}(c, i, t) / \text{Denom}_{\text{Whole}}^{\text{New}}(c, t)}{P_{\text{Global}}(i, t) / \text{Denom}_{\text{Global}}^{\text{New}}(t)}, 5\right)$$
$$RCA_{\text{Frac}}(c, i, t) = \text{round}\left(\frac{P_{\text{Frac}}(c, i, t) / \text{Denom}_{\text{Frac}}^{\text{New}}(c, t)}{P_{\text{Global}}(i, t) / \text{Denom}_{\text{Global}}^{\text{New}}(t)}, 5\right)$$

Independent verification via [`independent_audit_v2.py`](file:///d:/Thesis/openalex_feasibility_audit/independent_audit_v2.py) across all 15,375 rows confirms that the maximum recalculation discrepancy for all six combinations is strictly bounded by the theoretical 5-decimal rounding ceiling ($\le 0.00000500$):

| Country & RCA Type | Column Name | Evaluated Rows | Max Recalculation Discrepancy | Rows Exceeding `0.00000500` | Invalid (`NaN`/`Inf`/`<0`) | Location of Max Discrepancy | Audit Verdict |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Germany Whole RCA** | `rca_whole_de` | 15,375 | **`0.00000500`** | 0 | 0 | `T11558`, Year `2016` | **PASS** |
| **Germany Fractional RCA** | `rca_frac_de` | 15,375 | **`0.00000500`** | 0 | 0 | `T14011`, Year `2022` | **PASS** |
| **China Whole RCA** | `rca_whole_cn` | 15,375 | **`0.00000500`** | 0 | 0 | `T13183`, Year `2022` | **PASS** |
| **China Fractional RCA** | `rca_frac_cn` | 15,375 | **`0.00000500`** | 0 | 0 | `T11574`, Year `2013` | **PASS** |
| **Japan Whole RCA** | `rca_whole_jp` | 15,375 | **`0.00000500`** | 0 | 0 | `T10511`, Year `2013` | **PASS** |
| **Japan Fractional RCA** | `rca_frac_jp` | 15,375 | **`0.00000500`** | 0 | 0 | `T11277`, Year `2018` | **PASS** |

### Sample Observation Comparison (Topic `T11367`: *Particle accelerators and beam dynamics*, Year `2010`):
* **Topic Counts (Unchanged):** `global_count = 4,090`, `de_whole_count = 209`, `de_frac_count = 148.127778`, `cn_whole_count = 224`, `cn_frac_count = 201.677778`, `jp_whole_count = 425`, `jp_frac_count = 368.553968`.
* **Original Panel v2 (`Old` Denoms: `Global = 5,867,112`):**
  * `rca_whole_de = 1.99885`, `rca_frac_de = 1.85180`
  * `rca_whole_cn = 0.55245`, `rca_frac_cn = 0.52051`
  * `rca_whole_jp = 3.62132`, `rca_frac_jp = 3.47160`
* **Synchronized Panel v2 (`New` Denoms: `Global = 5,561,014`):**
  * `rca_whole_de = 1.91605`, `rca_frac_de = 1.77503`
  * `rca_whole_cn = 0.53794`, `rca_frac_cn = 0.50739`
  * `rca_whole_jp = 3.48418`, `rca_frac_jp = 3.34117`
* **Full-Panel Correlation Between Original v2 and Synchronized v2 (15,375 rows):**
  * Germany Fractional RCA: $r = \mathbf{0.99983287}$
  * China Fractional RCA: $r = \mathbf{0.99986254}$
  * Japan Fractional RCA: $r = \mathbf{0.99987468}$

---

## 4. Files Preserved, Created, and Updated

| File Relative Path | Action | Size (Bytes) | SHA-256 Checksum | Role |
| :--- | :---: | :---: | :--- | :--- |
| `openalex_feasibility_audit/openalex_master_panel_1025topics.csv` | **PRESERVED** | 4,004,987 | `37de2b5d22ea0a585dc5772d3e9cb7ea0aaa0ba48357dbee043d268bbf408f87` | Frozen Master Panel v1 (All Types Baseline) |
| `openalex_feasibility_audit/openalex_modeling_panel_1025topics_v2_selected_types.csv` | **PRESERVED** | 4,113,999 | `3d869014a463449e2c4bd44628fe174f6aedc954cd7c878922baae9488b75d6e` | Frozen Original Modeling Panel v2 (Old Denoms) |
| `openalex_feasibility_audit/all_science_national_denominators_fractional_v2_selected_types.csv` | **PRESERVED** | 1,132 | `507f5ef4b61f7d91a2919fa88c7c8f54f45560d10d64ad16b60f5ce754c13b36` | Frozen Pre-Update v2 Denominators (`01:09Z`) |
| `openalex_feasibility_audit/openalex_modeling_panel_1025topics_v2_synchronized.csv` | **CREATED** | 4,114,478 | `f0049cd71f5ba8545c2e3cbb850e036a7b849828321cd23aa1d04771e60d7175` | **Primary Synchronized Modeling Panel v2 (`23:54Z` Denoms)** |
| `openalex_feasibility_audit/all_science_national_denominators_fractional_v2_live_recheck_20261105.csv` | **PRESERVED** | 2,340 | `70631954624d3d5646fd63f38b3430c9883fc660814c1718bb327b67b141a831` | Synchronized v2 Denominators (`23:54Z`) |
| `openalex_feasibility_audit/independent_audit_v2.py` | **UPDATED** | 7,418 | *(Audits Synchronized v2 + SHA-256 of Preserved Panels)* | 24-Check Verification Gate (`exit 0`) |
| `openalex_feasibility_audit/FINAL_DENOMINATOR_AND_RCA_VERIFICATION.md` | **CREATED** | — | — | This Final Verification Report |

---

## 5. Complete Independent Audit Output (`independent_audit_v2.py`)

```text
============================================================================================
INDEPENDENT FINAL AUDIT: SYNCHRONIZED MODELING PANEL V2 (SELECTED SCHOLARLY WORK TYPES)
============================================================================================

[0] PRESERVATION OF FROZEN DATASETS (SHA-256 CHECKSUMS)
  [PASS] Master Panel v1 Unmodified: SHA256=37de2b5d22ea0a58...
  [PASS] Original Modeling Panel v2 Unmodified: SHA256=3d869014a463449e...

[1] STRUCTURAL COMPLETENESS & INTEGRITY
  [PASS] Total Row Count == 15,375: Actual=15,375, Expected=15,375
  [PASS] Total Column Count == 26: Actual=26, Expected=26
  [PASS] Unique Topics == 1,025: Actual=1,025, Expected=1,025
  [PASS] Annual Coverage == 15 years (2010-2024): Years=2010..2024 (15 yrs)
  [PASS] Balanced Panel (15 rows per topic): All 1,025 topics have 15 rows=True
  [PASS] Zero Duplicate (topic_id, year): Duplicates=0
  [PASS] Zero Missing / Null Values: Missing/Nulls=0

[2] SYNCHRONIZED DENOMINATOR CONSISTENCY (GLOBAL, DE, CN, JP ACROSS ALL 15 YEARS & ALL ROWS)
  [PASS] Denominator Table Years (2010-2024): Years=15 rows
  [PASS] Denominator Table == Coverage Table (15 yrs): Exact 15-year match=True
  [PASS] Global All-Science Denominator (15 yrs x 1,025 topics): Mismatched rows=0
  [PASS] DE Whole All-Science Denominator (15 yrs x 1,025 topics): Mismatched rows=0
  [PASS] DE Fractional All-Science Denominator (15 yrs x 1,025 topics): Mismatched rows=0
  [PASS] CN Whole All-Science Denominator (15 yrs x 1,025 topics): Mismatched rows=0
  [PASS] CN Fractional All-Science Denominator (15 yrs x 1,025 topics): Mismatched rows=0
  [PASS] JP Whole All-Science Denominator (15 yrs x 1,025 topics): Mismatched rows=0
  [PASS] JP Fractional All-Science Denominator (15 yrs x 1,025 topics): Mismatched rows=0

[3] COUNT NON-NEGATIVITY & FRACTIONAL BOUND CONSTRAINTS (0 <= Frac <= Whole)
  [PASS] Global Topic Count >= 0: Negative rows=0
  [PASS] DE Non-Negative & Bound (0 <= Frac <= Whole): NegWhole=0, NegFrac=0, Frac>Whole=0, ZeroMismatch=0 | WholeSum=722,798, FracSum=544,660.64 (Retention=75.35%)
  [PASS] CN Non-Negative & Bound (0 <= Frac <= Whole): NegWhole=0, NegFrac=0, Frac>Whole=0, ZeroMismatch=0 | WholeSum=4,653,398, FracSum=4,189,429.44 (Retention=90.03%)
  [PASS] JP Non-Negative & Bound (0 <= Frac <= Whole): NegWhole=0, NegFrac=0, Frac>Whole=0, ZeroMismatch=0 | WholeSum=816,615, FracSum=714,234.85 (Retention=87.46%)

[4] RCA RECALCULATION & PRECISION ENFORCEMENT (TOLERANCE <= 0.00000500)
  [PASS] DE Whole RCA Precision (<= 0.00000500): MaxDiff=0.00000500, ExceedCount=0, Invalid=0 (at T11558, 2016)
  [PASS] DE Fractional RCA Precision (<= 0.00000500): MaxDiff=0.00000500, ExceedCount=0, Invalid=0 (at T14011, 2022)
  [PASS] CN Whole RCA Precision (<= 0.00000500): MaxDiff=0.00000500, ExceedCount=0, Invalid=0 (at T13183, 2022)
  [PASS] CN Fractional RCA Precision (<= 0.00000500): MaxDiff=0.00000500, ExceedCount=0, Invalid=0 (at T11574, 2013)
  [PASS] JP Whole RCA Precision (<= 0.00000500): MaxDiff=0.00000500, ExceedCount=0, Invalid=0 (at T10511, 2013)
  [PASS] JP Fractional RCA Precision (<= 0.00000500): MaxDiff=0.00000500, ExceedCount=0, Invalid=0 (at T11277, 2018)

[5] SUMMARY COMPARISON: V1 vs. V2 ORIGINAL vs. V2 SYNCHRONIZED
  Country DE: RCA Frac Correlation (v1 vs v2_sync)=0.889471 | (v2_orig vs v2_sync)=0.99983287
  Country CN: RCA Frac Correlation (v1 vs v2_sync)=0.990808 | (v2_orig vs v2_sync)=0.99986254
  Country JP: RCA Frac Correlation (v1 vs v2_sync)=0.959333 | (v2_orig vs v2_sync)=0.99987468

============================================================================================
FINAL AUDIT VERDICT: PASS (All 24 critical preservation, structural, denominator, bound, and RCA checks passed)
============================================================================================
EXIT_CODE=0
```

---

> [!IMPORTANT]
> **STOP CONDITION ENFORCED:** Verification, denominator synchronization, RCA recalculation, and audit certification are complete. Stage 3 Feature Engineering and Modeling have not been initiated.
