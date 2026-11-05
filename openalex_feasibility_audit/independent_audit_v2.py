"""
Independent Mathematical & Structural Audit Script for Modeling Panel v2 (Selected Scholarly Work Types)
Enforces strict pass/fail acceptance criteria and returns non-zero exit status (sys.exit(1)) if any check fails.
"""

import sys
import pandas as pd
import numpy as np

TOLERANCE_RCA = 0.00000500
FLOAT_EPS = 1e-12  # Guard for IEEE 754 representation of 0.00000500


def run_audit() -> int:
    print("=" * 88)
    print("INDEPENDENT FINAL AUDIT: MODELING PANEL V2 (SELECTED SCHOLARLY WORK TYPES)")
    print("=" * 88)

    csv_v2 = r"openalex_feasibility_audit\openalex_modeling_panel_1025topics_v2_selected_types.csv"
    csv_v1 = r"openalex_feasibility_audit\openalex_master_panel_1025topics.csv"
    denom_v2 = r"openalex_feasibility_audit\all_science_national_denominators_fractional_v2_selected_types.csv"

    df_v2 = pd.read_csv(csv_v2)
    df_v1 = pd.read_csv(csv_v1)
    df_denom = pd.read_csv(denom_v2)

    failures = []

    def record_check(name: str, passed: bool, detail: str):
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {name}: {detail}")
        if not passed:
            failures.append(f"{name}: {detail}")

    # -------------------------------------------------------------------------
    # 1. Structural Completeness (1,025 topics, 15 years, 15,375 rows, 26 cols)
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
    # 2. Denominator Consistency across all 15 years (Global, DE, CN, JP)
    # -------------------------------------------------------------------------
    print("\n[2] DENOMINATOR CONSISTENCY (GLOBAL, DE, CN, JP ACROSS ALL 15 YEARS & ALL ROWS)")
    denom_years_ok = sorted(df_denom["year"].unique().tolist()) == expected_years
    record_check("Denominator Table Years (2010-2024)", denom_years_ok, f"Years={len(df_denom)} rows")

    glob_denom_mismatches = 0
    country_whole_mismatches = {"de": 0, "cn": 0, "jp": 0}
    country_frac_mismatches = {"de": 0, "cn": 0, "jp": 0}

    for yr in expected_years:
        sub_panel = df_v2[df_v2["year"] == yr]
        sub_denom = df_denom[df_denom["year"] == yr].iloc[0]

        # Global denominator check across all 1,025 rows in year yr
        if not (sub_panel["global_allsci_denom"] == int(sub_denom["global_allsci"])).all():
            glob_denom_mismatches += int((sub_panel["global_allsci_denom"] != int(sub_denom["global_allsci"])).sum())

        # Country whole and fractional denominator checks across all 1,025 rows in year yr
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
    # 3. Non-Negativity & Fractional <= Whole Count Bounds
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
    # 4. RCA Recalculation & Numerical Precision Enforcement (<= 0.00000500)
    # -------------------------------------------------------------------------
    print(f"\n[4] RCA RECALCULATION & PRECISION ENFORCEMENT (TOLERANCE <= {TOLERANCE_RCA:.8f})")
    for c in ["de", "cn", "jp"]:
        # Whole RCA recalculation from saved CSV columns
        calc_rca_whole = np.where(
            (df_v2["global_count"] > 0) & (df_v2[f"{c}_allsci_whole_denom"] > 0) & (df_v2[f"{c}_whole_count"] > 0),
            (df_v2[f"{c}_whole_count"] / df_v2[f"{c}_allsci_whole_denom"]) / (df_v2["global_count"] / df_v2["global_allsci_denom"]),
            0.0
        )
        diff_whole = np.abs(calc_rca_whole - df_v2[f"rca_whole_{c}"])
        max_idx_w = int(np.argmax(diff_whole))
        max_diff_w = float(diff_whole[max_idx_w])
        exceed_w = int((diff_whole > TOLERANCE_RCA + FLOAT_EPS).sum())
        invalid_w = int((np.isnan(df_v2[f"rca_whole_{c}"]) | np.isinf(df_v2[f"rca_whole_{c}"]) | (df_v2[f"rca_whole_{c}"] < 0)).sum())

        # Fractional RCA recalculation from saved CSV columns
        calc_rca_frac = np.where(
            (df_v2["global_count"] > 0) & (df_v2[f"{c}_allsci_frac_denom"] > 0) & (df_v2[f"{c}_frac_count"] > 0),
            (df_v2[f"{c}_frac_count"] / df_v2[f"{c}_allsci_frac_denom"]) / (df_v2["global_count"] / df_v2["global_allsci_denom"]),
            0.0
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
    # 5. Summary Comparison: Master Panel v1 vs Modeling Panel v2
    # -------------------------------------------------------------------------
    print("\n[5] SUMMARY COMPARISON: MASTER PANEL V1 (ALL TYPES) VS MODELING PANEL V2 (SELECTED TYPES)")
    tot_glob_v1 = int(df_v1["global_count"].sum())
    tot_glob_v2 = int(df_v2["global_count"].sum())
    print(f"  Total Global Works: v1={tot_glob_v1:,} | v2={tot_glob_v2:,} | Retention={tot_glob_v2/tot_glob_v1:.2%}")
    for c in ["de", "cn", "jp"]:
        w_v1 = int(df_v1[f"{c}_whole_count"].sum())
        w_v2 = int(df_v2[f"{c}_whole_count"].sum())
        f_v1 = float(df_v1[f"{c}_frac_count"].sum())
        f_v2 = float(df_v2[f"{c}_frac_count"].sum())
        corr_rca = float(df_v1[f"rca_frac_{c}"].corr(df_v2[f"rca_frac_{c}"]))
        print(f"  Country {c.upper()}: Whole Ret={w_v2/w_v1:.2%} | Frac Ret={f_v2/f_v1:.2%} | RCA Correlation (v1 vs v2)={corr_rca:.4f}")

    # -------------------------------------------------------------------------
    # 6. Final Verdict & Exit Code Enforcement
    # -------------------------------------------------------------------------
    print("\n" + "=" * 88)
    if failures:
        print(f"FINAL AUDIT VERDICT: FAIL ({len(failures)} check(s) failed)")
        for idx, msg in enumerate(failures, 1):
            print(f"  {idx}. {msg}")
        print("=" * 88)
        return 1
    else:
        print("FINAL AUDIT VERDICT: PASS (All 21 critical structural, denominator, bound, and RCA checks passed)")
        print("=" * 88)
        return 0


if __name__ == "__main__":
    sys.exit(run_audit())
