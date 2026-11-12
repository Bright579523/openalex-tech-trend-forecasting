"""
Stage 3.1: Independent Verification & Leakage Audit Script
Script: stage3_modeling/audit_stage3_features_targets.py

Purpose:
Independently verifies stage3_origin_features_targets.csv and
stage3_feature_target_manifest.json against the frozen Stage 2 source files
without importing any calculation function from build_stage3_features_targets.py.

Uses row-by-row pure-Python scalar lookups (csv.DictReader + math.log1p) plus
an explicit forward-time poisoning invariance test to prove strict causal
window boundaries ([t-5,t-3], [t-2,t], [t+1,t+3]) and zero future leakage.

Exits with code 0 only if ALL checks pass; exits with code 1 on any failure.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
import sklearn

# -----------------------------------------------------------------------------
# Paths & Reference Constants
# -----------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
AUDIT_DIR = BASE_DIR / "openalex_feasibility_audit"
STAGE3_DIR = BASE_DIR / "stage3_modeling"

PANEL_PATH = AUDIT_DIR / "openalex_modeling_panel_1025topics_v2_synchronized.csv"
DENOM_PATH = AUDIT_DIR / "all_science_national_denominators_fractional_v2_live_recheck_20261105.csv"
OUTPUT_CSV_PATH = STAGE3_DIR / "stage3_origin_features_targets.csv"
MANIFEST_JSON_PATH = STAGE3_DIR / "stage3_feature_target_manifest.json"
REPORT_MD_PATH = STAGE3_DIR / "stage3_feature_target_audit_report.md"

EXPECTED_PANEL_SHA256 = "f0049cd71f5ba8545c2e3cbb850e036a7b849828321cd23aa1d04771e60d7175"
EXPECTED_DENOM_SHA256 = "9c2d9cccee65c156494b96447ce53045d43e514c74aa10ec9f1c85915b33afce"
REQUIRED_ANCESTOR = "ffc1716"

VALID_ORIGINS = [2015, 2016, 2017, 2018, 2019, 2020, 2021]
KNOWN_ELIGIBLE_COUNTS = {2015: 990, 2016: 990, 2017: 991, 2018: 992, 2021: 995}
EXPECTED_FIELD_COUNTS = {
    "Engineering": 560,
    "Computer Science": 302,
    "Materials Science": 123,
    "Energy": 27,
    "Chemical Engineering": 13,
}
EXPECTED_W_WINDOWS = {
    (2010, 2012): 17486265,
    (2013, 2015): 19552552,
    (2016, 2018): 19796237,
    (2019, 2021): 20398266,
    (2022, 2024): 20127715,
}
TOL = 1e-12


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def load_raw_tables() -> Tuple[
    Dict[Tuple[str, int], Dict[str, Any]],
    Dict[int, Dict[str, Any]],
    List[str],
]:
    """Load raw Stage 2 CSVs purely via stdlib csv.DictReader for independent math."""
    panel_map: Dict[Tuple[str, int], Dict[str, Any]] = {}
    topics_seen = set()
    with open(PANEL_PATH, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tid = row["topic_id"]
            yr = int(row["year"])
            topics_seen.add(tid)
            panel_map[(tid, yr)] = {
                "topic_name": row["topic_name"],
                "field_name": row["field_name"],
                "subfield_name": row["subfield_name"],
                "global_count": int(row["global_count"]),
                "de_frac_count": float(row["de_frac_count"]),
                "cn_frac_count": float(row["cn_frac_count"]),
                "jp_frac_count": float(row["jp_frac_count"]),
                "de_whole_count": int(row["de_whole_count"]),
                "cn_whole_count": int(row["cn_whole_count"]),
                "jp_whole_count": int(row["jp_whole_count"]),
                "rca_frac_de_annual": float(row["rca_frac_de"]),
                "rca_frac_cn_annual": float(row["rca_frac_cn"]),
                "rca_frac_jp_annual": float(row["rca_frac_jp"]),
            }

    denom_map: Dict[int, Dict[str, Any]] = {}
    with open(DENOM_PATH, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            yr = int(row["year"])
            denom_map[yr] = {
                "global_allsci": int(row["global_allsci"]),
                "de_frac": float(row["de_frac"]),
                "cn_frac": float(row["cn_frac"]),
                "jp_frac": float(row["jp_frac"]),
                "de_whole": int(row["de_whole"]),
                "cn_whole": int(row["cn_whole"]),
                "jp_whole": int(row["jp_whole"]),
            }

    return panel_map, denom_map, sorted(topics_seen)


def scalar_recompute_row(
    tid: str,
    origin: int,
    panel_map: Dict[Tuple[str, int], Dict[str, Any]],
    denom_map: Dict[int, Dict[str, Any]],
) -> Dict[str, Any]:
    """Independently compute every feature and target for one (topic_id, origin)."""
    prev_years = (origin - 5, origin - 4, origin - 3)
    past_years = (origin - 2, origin - 1, origin)
    fut_years = (origin + 1, origin + 2, origin + 3)

    p_prev = sum(panel_map[(tid, y)]["global_count"] for y in prev_years)
    p_past = sum(panel_map[(tid, y)]["global_count"] for y in past_years)
    p_fut = sum(panel_map[(tid, y)]["global_count"] for y in fut_years)

    w_prev = sum(denom_map[y]["global_allsci"] for y in prev_years)
    w_past = sum(denom_map[y]["global_allsci"] for y in past_years)
    w_fut = sum(denom_map[y]["global_allsci"] for y in fut_years)

    g_adj = (math.log1p(p_fut) - math.log1p(p_past)) - (
        math.log1p(w_fut) - math.log1p(w_past)
    )
    m0_adj = (math.log1p(p_past) - math.log1p(p_prev)) - (
        math.log1p(w_past) - math.log1p(w_prev)
    )

    out: Dict[str, Any] = {
        "eligible": (p_past >= 50),
        "global_topic_prev3yr": p_prev,
        "global_topic_3yr": p_past,
        "target_global_topic_fut3yr": p_fut,
        "w_allsci_prev3yr": w_prev,
        "w_allsci_past3yr": w_past,
        "target_w_allsci_fut3yr": w_fut,
        "g_adj": g_adj,
        "m0_adj": m0_adj,
        "ln_global_topic_3yr": math.log1p(p_past),
    }

    g_share = (p_past / w_past) if p_past > 0 else 0.0

    for c in ("de", "cn", "jp"):
        frac_sum = sum(panel_map[(tid, y)][f"{c}_frac_count"] for y in past_years)
        d_frac_sum = round(sum(denom_map[y][f"{c}_frac"] for y in past_years), 4)
        rca_f = ((frac_sum / d_frac_sum) / g_share) if p_past > 0 else 0.0

        whole_sum = sum(panel_map[(tid, y)][f"{c}_whole_count"] for y in past_years)
        d_whole_sum = sum(denom_map[y][f"{c}_whole"] for y in past_years)
        rca_w = ((whole_sum / d_whole_sum) / g_share) if p_past > 0 else 0.0

        out[f"frac_{c}_3yr"] = frac_sum
        out[f"denom_frac_{c}_3yr"] = d_frac_sum
        out[f"ln_frac_{c}_3yr"] = math.log1p(frac_sum)
        out[f"rca_frac_{c}_3yr"] = rca_f
        out[f"ln_rca_frac_{c}_3yr"] = math.log1p(rca_f)

        out[f"whole_{c}_3yr"] = whole_sum
        out[f"denom_whole_{c}_3yr"] = d_whole_sum
        out[f"ln_whole_{c}_3yr"] = math.log1p(whole_sum)
        out[f"rca_whole_{c}_3yr"] = rca_w

    return out


def run_audit() -> int:
    checks: List[Tuple[str, str, str]] = []
    failures: List[str] = []

    def record(name: str, passed: bool, detail: str) -> None:
        status = "PASS" if passed else "FAIL"
        checks.append((name, status, detail))
        print(f"[{status}] {name}: {detail}")
        if not passed:
            failures.append(f"{name}: {detail}")

    print("=" * 92)
    print("INDEPENDENT AUDIT: STAGE 3.1 FEATURE AND TARGET CONSTRUCTION")
    print("=" * 92)

    # -------------------------------------------------------------------------
    # Check 0: Prerequisite Files, Checksums, Git HEAD & Software Stack
    # -------------------------------------------------------------------------
    git_head = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=BASE_DIR, text=True
    ).strip()
    git_anc = (
        subprocess.run(
            ["git", "merge-base", "--is-ancestor", REQUIRED_ANCESTOR, "HEAD"],
            cwd=BASE_DIR,
        ).returncode
        == 0
    )
    record("Git Checkpoint Ancestor (ffc1716)", git_anc, f"HEAD={git_head}")

    sk_parts = tuple(int(p) for p in sklearn.__version__.split(".")[:2])
    record(
        "Dependency Constraint (scikit-learn >= 1.6)",
        sk_parts >= (1, 6),
        f"scikit-learn={sklearn.__version__}, numpy={np.__version__}, pandas={pd.__version__}",
    )

    files_exist = all(
        p.exists() for p in (PANEL_PATH, DENOM_PATH, OUTPUT_CSV_PATH, MANIFEST_JSON_PATH)
    )
    record("Required Stage 2 & Stage 3.1 Files Exist", files_exist, f"All 4 files present={files_exist}")
    if not files_exist:
        return 1

    panel_sha = sha256_file(PANEL_PATH)
    denom_sha = sha256_file(DENOM_PATH)
    out_sha = sha256_file(OUTPUT_CSV_PATH)
    manifest = json.loads(MANIFEST_JSON_PATH.read_text(encoding="utf-8"))

    record("Frozen Panel SHA-256 Unchanged", panel_sha == EXPECTED_PANEL_SHA256, panel_sha)
    record("Frozen Denoms SHA-256 Unchanged", denom_sha == EXPECTED_DENOM_SHA256, denom_sha)
    record(
        "Output CSV SHA-256 Matches Manifest",
        out_sha == manifest["output"]["sha256"],
        out_sha,
    )

    # -------------------------------------------------------------------------
    # Check 1: Structural & Metadata Completeness
    # -------------------------------------------------------------------------
    df_out = pd.read_csv(OUTPUT_CSV_PATH, float_precision="round_trip")
    panel_map, denom_map, raw_topics = load_raw_tables()

    record(
        "Output Dimensions (7,175 x 42)",
        df_out.shape == (7175, 42),
        f"shape={df_out.shape}",
    )
    origins_actual = sorted(df_out["forecast_origin"].unique().tolist())
    record("Forecast Origins == 2015..2021", origins_actual == VALID_ORIGINS, str(origins_actual))

    dup_keys = int(df_out.duplicated(subset=["forecast_origin", "topic_id"]).sum())
    per_origin_counts = df_out.groupby("forecast_origin")["topic_id"].nunique().to_dict()
    record(
        "1,025 Unique Topics per Origin & Zero Duplicates",
        dup_keys == 0 and all(v == 1025 for v in per_origin_counts.values()),
        f"duplicates={dup_keys}, per_origin={per_origin_counts}",
    )

    field_counts_ok = True
    for t in VALID_ORIGINS:
        fc = Counter(df_out[df_out["forecast_origin"] == t]["field_name"])
        if dict(fc) != EXPECTED_FIELD_COUNTS:
            field_counts_ok = False
    record(
        "Balanced 5-Field Taxonomy Counts Across All Origins",
        field_counts_ok,
        str(EXPECTED_FIELD_COUNTS),
    )

    # Verify W_[a,b] reference constants independently
    w_match = True
    for (a, b), exp_w in EXPECTED_W_WINDOWS.items():
        calc_w = denom_map[a]["global_allsci"] + denom_map[a + 1]["global_allsci"] + denom_map[b]["global_allsci"]
        if calc_w != exp_w:
            w_match = False
    record("Window All-Science Sums W_[a,b] Match Locked Spec", w_match, str(EXPECTED_W_WINDOWS))

    # -------------------------------------------------------------------------
    # Check 2: Independent Scalar Formula Recomputation (All 7,175 rows)
    # -------------------------------------------------------------------------
    model_float_cols = [
        "g_adj", "m0_adj", "ln_global_topic_3yr",
        "ln_frac_de_3yr", "ln_frac_cn_3yr", "ln_frac_jp_3yr",
        "rca_frac_de_3yr", "rca_frac_cn_3yr", "rca_frac_jp_3yr",
        "ln_rca_frac_de_3yr", "ln_rca_frac_cn_3yr", "ln_rca_frac_jp_3yr",
        "ln_whole_de_3yr", "ln_whole_cn_3yr", "ln_whole_jp_3yr",
        "rca_whole_de_3yr", "rca_whole_cn_3yr", "rca_whole_jp_3yr",
    ]
    sum_float_cols = [
        "frac_de_3yr", "frac_cn_3yr", "frac_jp_3yr",
        "denom_frac_de_3yr", "denom_frac_cn_3yr", "denom_frac_jp_3yr",
    ]
    max_model_abs_diffs: Dict[str, float] = {col: 0.0 for col in model_float_cols}
    max_sum_rel_diffs: Dict[str, float] = {col: 0.0 for col in sum_float_cols}

    int_mismatches = 0
    bool_mismatches = 0
    meta_mismatches = 0

    for row in df_out.itertuples(index=False):
        tid = row.topic_id
        t = int(row.forecast_origin)
        ref = scalar_recompute_row(tid, t, panel_map, denom_map)
        meta = panel_map[(tid, t)]

        if (
            row.topic_name != meta["topic_name"]
            or row.field_name != meta["field_name"]
            or row.subfield_name != meta["subfield_name"]
        ):
            meta_mismatches += 1
        if bool(row.eligible) != bool(ref["eligible"]):
            bool_mismatches += 1

        for icol in (
            "global_topic_prev3yr",
            "global_topic_3yr",
            "target_global_topic_fut3yr",
            "w_allsci_prev3yr",
            "w_allsci_past3yr",
            "target_w_allsci_fut3yr",
            "whole_de_3yr",
            "whole_cn_3yr",
            "whole_jp_3yr",
            "denom_whole_de_3yr",
            "denom_whole_cn_3yr",
            "denom_whole_jp_3yr",
        ):
            if int(getattr(row, icol)) != int(ref[icol]):
                int_mismatches += 1

        for fcol in model_float_cols:
            diff = abs(float(getattr(row, fcol)) - float(ref[fcol]))
            if diff > max_model_abs_diffs[fcol]:
                max_model_abs_diffs[fcol] = diff

        for scol in sum_float_cols:
            actual_v = float(getattr(row, scol))
            ref_v = float(ref[scol])
            rel = abs(actual_v - ref_v) / max(abs(ref_v), 1.0)
            if rel > max_sum_rel_diffs[scol]:
                max_sum_rel_diffs[scol] = rel

    worst_model_col = max(max_model_abs_diffs, key=max_model_abs_diffs.get)
    worst_model_diff = max_model_abs_diffs[worst_model_col]
    worst_sum_col = max(max_sum_rel_diffs, key=max_sum_rel_diffs.get)
    worst_sum_rel = max_sum_rel_diffs[worst_sum_col]
    record(
        "Independent Scalar Recomputation (All 7,175 Rows)",
        (meta_mismatches == 0)
        and (bool_mismatches == 0)
        and (int_mismatches == 0)
        and (worst_model_diff < TOL)
        and (worst_sum_rel < 1e-13),
        f"meta_err={meta_mismatches}, bool_err={bool_mismatches}, int_err={int_mismatches}, max_model_abs_diff={worst_model_diff:.3e} ({worst_model_col}), max_sum_rel_diff={worst_sum_rel:.3e} ({worst_sum_col})",
    )

    # Confirm 3-yr Ratio-of-Sums RCA != 3-yr Mean of Annual RCA & M3 Raw RCA not log/winsorized
    elig_df = df_out[df_out["eligible"]].copy()
    ros_vs_mean_diffs = []
    for row in elig_df[elig_df["forecast_origin"] == 2018].itertuples(index=False):
        mean_ann = (
            panel_map[(row.topic_id, 2016)]["rca_frac_de_annual"]
            + panel_map[(row.topic_id, 2017)]["rca_frac_de_annual"]
            + panel_map[(row.topic_id, 2018)]["rca_frac_de_annual"]
        ) / 3.0
        ros_vs_mean_diffs.append(abs(row.rca_frac_de_3yr - mean_ann))
    max_ros_vs_mean = max(ros_vs_mean_diffs)
    max_rca_raw = float(elig_df["rca_frac_jp_3yr"].max())
    raw_vs_log_diff = float(
        np.max(np.abs(elig_df["rca_frac_de_3yr"] - elig_df["ln_rca_frac_de_3yr"]))
    )
    record(
        "RCA Uses Ratio-of-Sums (Not Annual Mean) & Is Raw/Unwinsorized",
        (max_ros_vs_mean > 0.1) and (raw_vs_log_diff > 1.0) and (max_rca_raw > 12.0),
        f"max|RoS - MeanAnnual|(2018 DE)={max_ros_vs_mean:.4f}, max_raw_JP_RCA={max_rca_raw:.4f}, max|RCA - ln(1+RCA)|={raw_vs_log_diff:.4f}",
    )

    # -------------------------------------------------------------------------
    # Check A: Mathematical Identity G_adj(i,t) == M0_adj(i,t+3)
    # -------------------------------------------------------------------------
    ident_details = []
    ident_pass = True
    for t in (2015, 2016, 2017, 2018):
        s0 = df_out[df_out["forecast_origin"] == t].set_index("topic_id").loc[raw_topics]
        s3 = df_out[df_out["forecast_origin"] == t + 3].set_index("topic_id").loc[raw_topics]
        diff_all = float(np.max(np.abs(s0["g_adj"].to_numpy() - s3["m0_adj"].to_numpy())))
        both_elig = s0["eligible"] & s3["eligible"]
        diff_elig = float(
            np.max(np.abs(s0.loc[both_elig, "g_adj"] - s3.loc[both_elig, "m0_adj"]))
        )
        if diff_all >= TOL or diff_elig >= TOL:
            ident_pass = False
        ident_details.append(f"{t}->{t+3}: all={diff_all:.2e}, elig={diff_elig:.2e} (n={int(both_elig.sum())})")
    record(
        "Check A: Identity G_adj(i,t) == M0_adj(i,t+3) < 1e-12",
        ident_pass,
        "; ".join(ident_details),
    )

    # -------------------------------------------------------------------------
    # Check B: Time-Window Integrity & Forward-Time Poisoning Leakage Test
    # -------------------------------------------------------------------------
    # Poison EVERY year y > origin t across ALL topics and ALL columns in memory,
    # then verify features + eligibility match exact 0.0 scalar invariance (and < 1e-12 vs CSV)
    # while target g_adj strictly diverges!
    feature_union = sorted(
        {col for cols in manifest["schema_roles"]["model_feature_sets"].values() for col in cols}
    )
    max_poison_scalar_diff = 0.0
    max_poison_csv_diff = 0.0
    min_poison_target_diff = float("inf")

    for t in VALID_ORIGINS:
        poisoned_panel = {
            k: (
                {
                    **v,
                    "global_count": 999999999,
                    "de_frac_count": 999999999.0,
                    "cn_frac_count": 999999999.0,
                    "jp_frac_count": 999999999.0,
                    "de_whole_count": 999999999,
                    "cn_whole_count": 999999999,
                    "jp_whole_count": 999999999,
                }
                if k[1] > t
                else v
            )
            for k, v in panel_map.items()
        }
        poisoned_denom = {
            yr: (
                {
                    "global_allsci": 999999999,
                    "de_frac": 999999999.0,
                    "cn_frac": 999999999.0,
                    "jp_frac": 999999999.0,
                    "de_whole": 999999999,
                    "cn_whole": 999999999,
                    "jp_whole": 999999999,
                }
                if yr > t
                else v
            )
            for yr, v in denom_map.items()
        }
        sub_t = df_out[df_out["forecast_origin"] == t]
        for row in sub_t.itertuples(index=False):
            clean_res = scalar_recompute_row(row.topic_id, t, panel_map, denom_map)
            p_res = scalar_recompute_row(row.topic_id, t, poisoned_panel, poisoned_denom)
            if bool(row.eligible) != bool(p_res["eligible"]):
                max_poison_scalar_diff = float("inf")
                max_poison_csv_diff = float("inf")
            for fcol in feature_union:
                ds = abs(float(clean_res[fcol]) - float(p_res[fcol]))
                if ds > max_poison_scalar_diff:
                    max_poison_scalar_diff = ds
                dc = abs(float(getattr(row, fcol)) - float(p_res[fcol]))
                if dc > max_poison_csv_diff:
                    max_poison_csv_diff = dc
            td = abs(float(row.g_adj) - float(p_res["g_adj"]))
            if td < min_poison_target_diff:
                min_poison_target_diff = td

    forbidden_cols = set(
        manifest["schema_roles"]["identifier_columns"]
        + [manifest["schema_roles"]["target_column"]]
        + manifest["schema_roles"]["audit_future_window_columns"]
    )
    schema_leak_free = all(
        len(forbidden_cols.intersection(cols)) == 0
        for cols in manifest["schema_roles"]["model_feature_sets"].values()
    )
    record(
        "Check B: Forward-Year Poisoning Invariance & Schema Leakage Gate",
        (max_poison_scalar_diff == 0.0)
        and (max_poison_csv_diff < TOL)
        and (min_poison_target_diff > 1.0)
        and schema_leak_free,
        f"scalar_invariance_diff={max_poison_scalar_diff:.2e}, max_csv_vs_poison_diff={max_poison_csv_diff:.2e}, min_target_diff={min_poison_target_diff:.2f}, schema_disjoint={schema_leak_free}",
    )

    # -------------------------------------------------------------------------
    # Check C: Eligibility Rule & Origin Sample Counts (All 7 Origins)
    # -------------------------------------------------------------------------
    origin_elig_table: Dict[int, Tuple[int, int]] = {}
    elig_ok = True
    for t in VALID_ORIGINS:
        sub_t = df_out[df_out["forecast_origin"] == t]
        n_el = int(sub_t["eligible"].sum())
        n_in = len(sub_t) - n_el
        origin_elig_table[t] = (n_el, n_in)
        if t in KNOWN_ELIGIBLE_COUNTS and n_el != KNOWN_ELIGIBLE_COUNTS[t]:
            elig_ok = False
        # Also verify boundary condition >= 50 directly on global_topic_3yr
        if not bool(((sub_t["global_topic_3yr"] >= 50) == sub_t["eligible"]).all()):
            elig_ok = False

    record(
        "Check C: Origin Eligibility (>= 50 Works in [t-2,t])",
        elig_ok,
        ", ".join(f"{t}: {v[0]}/1025" for t, v in origin_elig_table.items()),
    )

    # -------------------------------------------------------------------------
    # Check D: Numerical Validity (Full & Eligible)
    # -------------------------------------------------------------------------
    num_cols = df_out.select_dtypes(include=[np.number]).columns.tolist()
    n_nulls = int(df_out.isnull().sum().sum())
    n_inf_all = int(np.isinf(df_out[num_cols].to_numpy(dtype=np.float64)).sum())
    n_inf_elig = int(np.isinf(elig_df[num_cols].to_numpy(dtype=np.float64)).sum())

    bounds_ok = True
    for c in ("de", "cn", "jp"):
        if (
            (df_out[f"ln_frac_{c}_3yr"] < 0).any()
            or (df_out[f"ln_whole_{c}_3yr"] < 0).any()
            or (df_out[f"rca_frac_{c}_3yr"] < 0).any()
            or (df_out[f"rca_whole_{c}_3yr"] < 0).any()
            or (df_out[f"ln_rca_frac_{c}_3yr"] < 0).any()
            or (df_out[f"frac_{c}_3yr"] > df_out[f"whole_{c}_3yr"] + 1e-9).any()
            or (df_out[f"whole_{c}_3yr"] > df_out["global_topic_3yr"]).any()
        ):
            bounds_ok = False

    record(
        "Check D: Zero Nulls/Infs & Valid Fractional/Whole/RCA Bounds",
        (n_nulls == 0) and (n_inf_all == 0) and (n_inf_elig == 0) and bounds_ok,
        f"nulls={n_nulls}, inf_all={n_inf_all}, inf_elig={n_inf_elig}, bounds_ok={bounds_ok}",
    )

    # -------------------------------------------------------------------------
    # Check E: Feature Definitions & Whole-Counting Basis Consistency
    # -------------------------------------------------------------------------
    fsets = manifest["schema_roles"]["model_feature_sets"]
    counts_ok = (
        len(fsets["M0"]) == 0
        and len(fsets["M1"]) == 2
        and len(fsets["M2"]) == 5
        and len(fsets["M3"]) == 8
        and len(fsets["M3-LogRCA"]) == 8
        and len(fsets["M2-WC"]) == 5
        and len(fsets["M3-WC"]) == 8
    )
    hierarchy_ok = (
        fsets["M2"][:2] == fsets["M1"]
        and fsets["M3"][:5] == fsets["M2"]
        and fsets["M3-LogRCA"][:5] == fsets["M2"]
        and fsets["M2-WC"][:2] == fsets["M1"]
        and fsets["M3-WC"][:5] == fsets["M2-WC"]
    )
    wc_basis_ok = all(
        bool((df_out[f"denom_whole_{c}_3yr"] > df_out[f"denom_frac_{c}_3yr"]).all())
        for c in ("de", "cn", "jp")
    )
    record(
        "Check E: Feature Lengths, Progressive Hierarchy & Consistent Counting Basis",
        counts_ok and hierarchy_ok and wc_basis_ok,
        f"counts_ok={counts_ok}, hierarchy_ok={hierarchy_ok}, wc_denom_strictly_paired={wc_basis_ok}",
    )

    # -------------------------------------------------------------------------
    # Check F: Post-Audit Frozen Source Preservation
    # -------------------------------------------------------------------------
    panel_sha_post = sha256_file(PANEL_PATH)
    denom_sha_post = sha256_file(DENOM_PATH)
    record(
        "Check F: Post-Audit Frozen Source Datasets Byte-for-Byte Preserved",
        (panel_sha_post == EXPECTED_PANEL_SHA256) and (denom_sha_post == EXPECTED_DENOM_SHA256),
        f"panel_ok={panel_sha_post == EXPECTED_PANEL_SHA256}, denom_ok={denom_sha_post == EXPECTED_DENOM_SHA256}",
    )

    # -------------------------------------------------------------------------
    # Write Independent Audit Report Markdown
    # -------------------------------------------------------------------------
    verdict = "PASS" if not failures else "FAIL"
    report_ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    lines = [
        "# Stage 3.1 Feature and Target Construction — Independent Audit Report",
        "",
        f"> **Audit Timestamp (UTC):** `{report_ts}`  ",
        f"> **Git HEAD:** `{git_head}` *(checkpoint `ffc1716` verified ancestor: `{git_anc}`)*  ",
        f"> **Final Audit Verdict:** **`{verdict}`** (`{len(checks) - len(failures)} / {len(checks)}` checks PASS)",
        "",
        "---",
        "",
        "## 1. Input & Output Cryptographic Integrity",
        "",
        "| Artifact | Role | Dimensions | SHA-256 |",
        "| :--- | :--- | :---: | :--- |",
        f"| `openalex_modeling_panel_1025topics_v2_synchronized.csv` | Frozen Primary Panel v2 | `15,375 x 26` | `{panel_sha_post}` |",
        f"| `all_science_national_denominators_fractional_v2_live_recheck_20261105.csv` | Frozen Synchronized Denoms | `15 x 10` | `{denom_sha_post}` |",
        f"| `stage3_origin_features_targets.csv` | Stage 3.1 Canonical Table | `{df_out.shape[0]:,} x {df_out.shape[1]}` | `{out_sha}` |",
        "",
        "---",
        "",
        "## 2. Independently Verified Origin Eligibility Counts (`sum(global_count over [t-2, t]) >= 50`)",
        "",
        "| Forecast Origin ($t$) | Momentum Base $[t-5,t-3]$ | Recent Feature Window $[t-2,t]$ | Target Window $[t+1,t+3]$ | Total Topics | Eligible (`True`) | Ineligible (`False`) | Coverage |",
        "| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |",
    ]
    for t in VALID_ORIGINS:
        n_el, n_in = origin_elig_table[t]
        cov = n_el / 1025.0 * 100.0
        lines.append(
            f"| **{t}** | `{t-5}-{t-3}` | `{t-2}-{t}` | `{t+1}-{t+3}` | `1,025` | **`{n_el}`** | `{n_in}` | `{cov:.2f}%` |"
        )

    lines += [
        "",
        "---",
        "",
        "## 3. Complete Validation Checklist",
        "",
        "| # | Check Name | Verdict | Observed Evidence |",
        "| :---: | :--- | :---: | :--- |",
    ]
    for idx, (cname, cstat, cdet) in enumerate(checks, start=1):
        lines.append(f"| {idx} | {cname} | **`{cstat}`** | `{cdet}` |")

    lines += [
        "",
        "---",
        "",
        "## 4. Model Feature Sets & Schema Isolation Verified",
        "",
        "| Model | Feature Count | Columns |",
        "| :--- | :---: | :--- |",
    ]
    for mname, cols in fsets.items():
        col_str = ", ".join(f"`{c}`" for c in cols) if cols else "*Unfitted benchmark (`m0_adj` direct prediction)*"
        lines.append(f"| `{mname}` | `{len(cols)}` | {col_str} |")

    lines += [
        "",
        "* **Target column:** `g_adj`",
        "* **Identifier columns:** `forecast_origin`, `topic_id`, `topic_name`, `field_name`, `subfield_name`, `eligible`",
        "* **Scope confirmation:** Stage 3.1 only (no train/test splitting, no Ridge fitting, no scaling, no CV, no predictions, no bootstrap).",
    ]

    REPORT_MD_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n" + "=" * 92)
    print(f"AUDIT VERDICT: {verdict} ({len(checks) - len(failures)}/{len(checks)} passed)")
    print(f"Report written: {REPORT_MD_PATH}")
    print("=" * 92)
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(run_audit())
