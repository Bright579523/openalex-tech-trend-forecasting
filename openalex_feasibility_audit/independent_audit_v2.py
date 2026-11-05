"""
Independent Mathematical & Structural Audit Script for Synchronized Modeling Panel v2
Audits:
  - Primary Synchronized Panel: openalex_modeling_panel_1025topics_v2_synchronized.csv
  - Synchronized Denominators:  all_science_national_denominators_fractional_v2_live_recheck_20261105.csv
  - Preserved Original v2:      openalex_modeling_panel_1025topics_v2_selected_types.csv
  - Preserved Master Panel v1:  openalex_master_panel_1025topics.csv

Enforces strict pass/fail acceptance criteria across 28 distinct checks and returns non-zero
exit status (sys.exit(1)) if any check fails.
"""

import sys
import hashlib
from pathlib import Path
import pandas as pd
import numpy as np

TOLERANCE_RCA = 0.00000500
FLOAT_EPS = 1e-12  # Guard for IEEE 754 representation of 0.00000500

EXPECTED_SHA256_V1 = "37de2b5d22ea0a585dc5772d3e9cb7ea0aaa0ba48357dbee043d268bbf408f87"
EXPECTED_SHA256_V2_ORIG = "3d869014a463449e2c4bd44628fe174f6aedc954cd7c878922baae9488b75d6e"
EXPECTED_SHA256_V2_SYNC = "f0049cd71f5ba8545c2e3cbb850e036a7b849828321cd23aa1d04771e60d7175"


def run_audit() -> int:
    print("=" * 92)
    print("INDEPENDENT FINAL AUDIT: SYNCHRONIZED MODELING PANEL V2 (SELECTED SCHOLARLY WORK TYPES)")
    print("=" * 92)

    csv_v2_sync = Path(r"openalex_feasibility_audit\openalex_modeling_panel_1025topics_v2_synchronized.csv")
    csv_v2_orig = Path(r"openalex_feasibility_audit\openalex_modeling_panel_1025topics_v2_selected_types.csv")
    csv_v1 = Path(r"openalex_feasibility_audit\openalex_master_panel_1025topics.csv")
    denom_v2_sync = Path(r"openalex_feasibility_audit\all_science_national_denominators_fractional_v2_live_recheck_20261105.csv")
    cov_csv = Path(r"openalex_feasibility_audit\annual_work_types_and_topic_coverage.csv")

    df_v2 = pd.read_csv(csv_v2_sync)
    df_v2_orig = pd.read_csv(csv_v2_orig)
    df_v1 = pd.read_csv(csv_v1)
    df_denom = pd.read_csv(denom_v2_sync)
    df_cov = pd.read_csv(cov_csv)

    checks_run = []
    failures = []

    def record_check(name: str, passed: bool, detail: str):
        idx = len(checks_run) + 1
        checks_run.append((idx, name, passed, detail))
        status = "PASS" if passed else "FAIL"
        print(f"  [{status} #{idx:02d}] {name}: {detail}")
        if not passed:
            failures.append(f"[#{idx:02d}] {name}: {detail}")

    # -------------------------------------------------------------------------
    # 0. Preservation of Frozen Datasets (2 checks)
    # -------------------------------------------------------------------------
    print("\n[0] PRESERVATION OF FROZEN DATASETS (SHA-256 CHECKSUMS)")
    sha_v1 = hashlib.sha256(csv_v1.read_bytes()).hexdigest()
    sha_v2_orig = hashlib.sha256(csv_v2_orig.read_bytes()).hexdigest()
    record_check("Master Panel v1 Unmodified", sha_v1 == EXPECTED_SHA256_V1, f"SHA256={sha_v1[:16]}...")
    record_check("Original Modeling Panel v2 Unmodified", sha_v2_orig == EXPECTED_SHA256_V2_ORIG, f"SHA256={sha_v2_orig[:16]}...")

    # -------------------------------------------------------------------------
    # 1. Structural Completeness (7 checks)
    # -------------------------------------------------------------------------
    print("\n[1] STRUCTURAL COMPLETENESS & INTEGRITY")
    total_rows = len(df_v2)
    total_cols = len(df_v2.columns)
    n_topics = df_v2["topic_id"].nunique()
    years_found = sorted(df_v2["year"].unique().tolist())
    expected_years = list(range(2010, 2025))
    rows_per_topic_ok = bool((df_v2.groupby("topic_id").size() == 15).all())
    dup_count = int(df_v2.duplicated(subset=["topic_id", "year"]).sum())
    null_count = int(df_v2.isnull().sum().sum())

    record_check("Total Row Count == 15,375", total_rows == 15375, f"Actual={total_rows:,}, Expected=15,375")
    record_check("Total Column Count == 26", total_cols == 26, f"Actual={total_cols}, Expected=26")
    record_check("Unique Topics == 1,025", n_topics == 1025, f"Actual={n_topics:,}, Expected=1,025")
    record_check("Annual Coverage == 15 years (2010-2024)", years_found == expected_years, f"Years={years_found[0]}..{years_found[-1]} ({len(years_found)} yrs)")
    record_check("Balanced Panel (15 rows per topic)", rows_per_topic_ok, f"All 1,025 topics have 15 rows={rows_per_topic_ok}")
    record_check("Zero Duplicate (topic_id, year)", dup_count == 0, f"Duplicates={dup_count}")
    record_check("Zero Missing / Null Values", null_count == 0, f"Missing/Nulls={null_count}")

    # -------------------------------------------------------------------------
    # 2. Denominator Consistency across all 15 years (9 checks)
    # -------------------------------------------------------------------------
    print("\n[2] SYNCHRONIZED DENOMINATOR CONSISTENCY (GLOBAL, DE, CN, JP ACROSS ALL 15 YEARS & ALL ROWS)")
    denom_years_ok = sorted(df_denom["year"].unique().tolist()) == expected_years
    cov_sync_ok = bool((df_denom.sort_values("year")["global_allsci"].values == df_cov.sort_values("year")["total_selected_works"].values).all())
    record_check("Denominator Table Years (2010-2024)", denom_years_ok, f"Years={len(df_denom)} rows")
    record_check("Denominator Table == Coverage Table (15 yrs)", cov_sync_ok, f"Exact 15-year match={cov_sync_ok}")

    glob_denom_mismatches = 0
    country_whole_mismatches = {"de": 0, "cn": 0, "jp": 0}
    country_frac_mismatches = {"de": 0, "cn": 0, "jp": 0}

    for yr in expected_years:
        sub_panel = df_v2[df_v2["year"] == yr]
        sub_denom = df_denom[df_denom["year"] == yr].iloc[0]

        if not (sub_panel["global_allsci_denom"] == int(sub_denom["global_allsci"])).all():
            glob_denom_mismatches += int((sub_panel["global_allsci_denom"] != int(sub_denom["global_allsci"])).sum())

        for c in ["de", "cn", "jp"]:
            w_expected = int(sub_denom[f"{c}_whole"])
            f_expected = round(float(sub_denom[f"{c}_frac"]), 4)
            w_bad = int((sub_panel[f"{c}_allsci_whole_denom"] != w_expected).sum())
            f_bad = int((np.abs(sub_panel[f"{c}_allsci_frac_denom"] - f_expected) > 1e-6).sum())
            country_whole_mismatches[c] += w_bad
            country_frac_mismatches[c] += f_bad

    record_check("Global All-Science Denominator (15 yrs x 1,025 topics)", glob_denom_mismatches == 0, f"Mismatched rows={glob_denom_mismatches}")
    for c in ["de", "cn", "jp"]:
        record_check(
            f"{c.upper()} Whole All-Science Denominator (15 yrs x 1,025 topics)",
            country_whole_mismatches[c] == 0,
            f"Mismatched rows={country_whole_mismatches[c]}"
        )
        record_check(
            f"{c.upper()} Fractional All-Science Denominator (15 yrs x 1,025 topics)",
            country_frac_mismatches[c] == 0,
            f"Mismatched rows={country_frac_mismatches[c]}"
        )

    # -------------------------------------------------------------------------
    # 3. Non-Negativity & Fractional <= Whole Count Bounds (4 checks)
    # -------------------------------------------------------------------------
    print("\n[3] COUNT NON-NEGATIVITY & FRACTIONAL BOUND CONSTRAINTS (0 <= Frac <= Whole)")
    glob_neg = int((df_v2["global_count"] < 0).sum())
    record_check("Global Topic Count >= 0", glob_neg == 0, f"Negative rows={glob_neg}")

    for c in ["de", "cn", "jp"]:
        w_col = f"{c}_whole_count"
        f_col = f"{c}_frac_count"
        neg_w = int((df_v2[w_col] < 0).sum())
        neg_f = int((df_v2[f_col] < 0).sum())
        frac_gt_whole = int((df_v2[f_col] > df_v2[w_col] + 1e-9).sum())
        zero_mismatch = int(((df_v2[w_col] == 0) & (df_v2[f_col] > 0)).sum() + ((df_v2[w_col] > 0) & (df_v2[f_col] == 0)).sum())

        tot_w = int(df_v2[w_col].sum())
        tot_f = float(df_v2[f_col].sum())
        retention = (tot_f / tot_w * 100.0) if tot_w > 0 else 0.0

        record_check(
            f"{c.upper()} Non-Negative & Bound (0 <= Frac <= Whole)",
            (neg_w == 0) and (neg_f == 0) and (frac_gt_whole == 0) and (zero_mismatch == 0),
            f"NegWhole={neg_w}, NegFrac={neg_f}, Frac>Whole={frac_gt_whole}, ZeroMismatch={zero_mismatch} | WholeSum={tot_w:,}, FracSum={tot_f:,.2f} (Retention={retention:.2f}%)"
        )

    # -------------------------------------------------------------------------
    # 4. RCA Recalculation & Numerical Precision Enforcement (6 checks)
    # -------------------------------------------------------------------------
    print(f"\n[4] RCA RECALCULATION & PRECISION ENFORCEMENT (TOLERANCE <= {TOLERANCE_RCA:.8f})")
    global_share = np.divide(
        df_v2["global_count"].to_numpy(dtype=float),
        df_v2["global_allsci_denom"].to_numpy(dtype=float),
        out=np.zeros(len(df_v2), dtype=float),
        where=(df_v2["global_allsci_denom"].to_numpy(dtype=float) > 0)
        & (df_v2["global_count"].to_numpy(dtype=float) > 0),
    )
    for c in ["de", "cn", "jp"]:
        topic_share_w = np.divide(
            df_v2[f"{c}_whole_count"].to_numpy(dtype=float),
            df_v2[f"{c}_allsci_whole_denom"].to_numpy(dtype=float),
            out=np.zeros(len(df_v2), dtype=float),
            where=(df_v2[f"{c}_allsci_whole_denom"].to_numpy(dtype=float) > 0)
            & (df_v2[f"{c}_whole_count"].to_numpy(dtype=float) > 0),
        )
        calc_rca_whole = np.divide(
            topic_share_w,
            global_share,
            out=np.zeros(len(df_v2), dtype=float),
            where=(global_share > 0),
        )
        diff_whole = np.abs(calc_rca_whole - df_v2[f"rca_whole_{c}"])
        max_idx_w = int(np.argmax(diff_whole))
        max_diff_w = float(diff_whole[max_idx_w])
        exceed_w = int((diff_whole > TOLERANCE_RCA + FLOAT_EPS).sum())
        invalid_w = int((np.isnan(df_v2[f"rca_whole_{c}"]) | np.isinf(df_v2[f"rca_whole_{c}"]) | (df_v2[f"rca_whole_{c}"] < 0)).sum())

        topic_share_f = np.divide(
            df_v2[f"{c}_frac_count"].to_numpy(dtype=float),
            df_v2[f"{c}_allsci_frac_denom"].to_numpy(dtype=float),
            out=np.zeros(len(df_v2), dtype=float),
            where=(df_v2[f"{c}_allsci_frac_denom"].to_numpy(dtype=float) > 0)
            & (df_v2[f"{c}_frac_count"].to_numpy(dtype=float) > 0),
        )
        calc_rca_frac = np.divide(
            topic_share_f,
            global_share,
            out=np.zeros(len(df_v2), dtype=float),
            where=(global_share > 0),
        )
        diff_frac = np.abs(calc_rca_frac - df_v2[f"rca_frac_{c}"])
        max_idx_f = int(np.argmax(diff_frac))
        max_diff_f = float(diff_frac[max_idx_f])
        exceed_f = int((diff_frac > TOLERANCE_RCA + FLOAT_EPS).sum())
        invalid_f = int((np.isnan(df_v2[f"rca_frac_{c}"]) | np.isinf(df_v2[f"rca_frac_{c}"]) | (df_v2[f"rca_frac_{c}"] < 0)).sum())

        row_w = df_v2.iloc[max_idx_w]
        row_f = df_v2.iloc[max_idx_f]

        record_check(
            f"{c.upper()} Whole RCA Precision (<= {TOLERANCE_RCA:.8f})",
            (exceed_w == 0) and (invalid_w == 0) and (max_diff_w <= TOLERANCE_RCA + FLOAT_EPS),
            f"MaxDiff={max_diff_w:.8f}, ExceedCount={exceed_w}, Invalid={invalid_w} (at {row_w['topic_id']}, {row_w['year']})"
        )
        record_check(
            f"{c.upper()} Fractional RCA Precision (<= {TOLERANCE_RCA:.8f})",
            (exceed_f == 0) and (invalid_f == 0) and (max_diff_f <= TOLERANCE_RCA + FLOAT_EPS),
            f"MaxDiff={max_diff_f:.8f}, ExceedCount={exceed_f}, Invalid={invalid_f} (at {row_f['topic_id']}, {row_f['year']})"
        )

    # -------------------------------------------------------------------------
    # 5. Summary Comparison: v1 vs v2 Original vs v2 Synchronized
    # -------------------------------------------------------------------------
    print("\n[5] SUMMARY COMPARISON: V1 vs. V2 ORIGINAL vs. V2 SYNCHRONIZED")
    for c in ["de", "cn", "jp"]:
        corr_v1_v2sync = float(df_v1[f"rca_frac_{c}"].corr(df_v2[f"rca_frac_{c}"]))
        corr_orig_sync = float(df_v2_orig[f"rca_frac_{c}"].corr(df_v2[f"rca_frac_{c}"]))
        print(f"  Country {c.upper()}: RCA Frac Correlation (v1 vs v2_sync)={corr_v1_v2sync:.6f} | (v2_orig vs v2_sync)={corr_orig_sync:.8f}")

    # -------------------------------------------------------------------------
    # 6. Final Verdict & Exit Code Enforcement
    # -------------------------------------------------------------------------
    total_checks = len(checks_run)
    passed_checks = total_checks - len(failures)
    print("\n" + "=" * 92)
    if failures:
        print(f"FINAL AUDIT VERDICT: FAIL ({len(failures)}/{total_checks} check(s) failed)")
        for msg in failures:
            print(f"  - {msg}")
        print("=" * 92)
        return 1
    else:
        print(f"FINAL AUDIT VERDICT: PASS (All {passed_checks}/{total_checks} critical preservation, structural, denominator, bound, and RCA checks passed)")
        print("=" * 92)
        return 0


if __name__ == "__main__":
    sys.exit(run_audit())
