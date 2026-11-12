"""
Stage 3.1: Deterministic Feature and Target Construction Script
Script: stage3_modeling/build_stage3_features_targets.py

Purpose:
Builds the origin-level feature and target dataset strictly from the frozen,
audited Stage 2 Synchronized Modeling Panel v2 and National All-Science
Denominators across all mathematically valid forecast origins (2015–2021).

Scope Guard:
This script performs ONLY Stage 3.1 (feature & target engineering + manifest
export). It does NOT perform train/test splitting, Ridge regression fitting,
StandardScaler estimation, cross-validation, prediction, bootstrap resampling,
or thesis evaluation.

Authoritative Specification:
  - AGENTS.md
  - openalex_feasibility_audit/CHAPTER4_METHODOLOGY_MASTER_SPEC.md (Decisions 1-4 & Section 7)
  - Git checkpoint commit: ffc1716
"""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import pandas as pd
import scipy
import sklearn

# -----------------------------------------------------------------------------
# Paths & Frozen Stage 2 Cryptographic References
# -----------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
AUDIT_DIR = BASE_DIR / "openalex_feasibility_audit"
STAGE3_DIR = BASE_DIR / "stage3_modeling"

PANEL_PATH = AUDIT_DIR / "openalex_modeling_panel_1025topics_v2_synchronized.csv"
DENOM_PATH = AUDIT_DIR / "all_science_national_denominators_fractional_v2_live_recheck_20261105.csv"

OUTPUT_CSV_PATH = STAGE3_DIR / "stage3_origin_features_targets.csv"
MANIFEST_JSON_PATH = STAGE3_DIR / "stage3_feature_target_manifest.json"

EXPECTED_PANEL_SHA256 = "f0049cd71f5ba8545c2e3cbb850e036a7b849828321cd23aa1d04771e60d7175"
EXPECTED_DENOM_SHA256 = "9c2d9cccee65c156494b96447ce53045d43e514c74aa10ec9f1c85915b33afce"
REQUIRED_ANCESTOR_COMMIT = "ffc1716"

# -----------------------------------------------------------------------------
# Locked Methodological Constants
# -----------------------------------------------------------------------------
FORECAST_ORIGINS: List[int] = [2015, 2016, 2017, 2018, 2019, 2020, 2021]
EXPECTED_TOPICS = 1025
EXPECTED_PANEL_YEARS = list(range(2010, 2025))
ELIGIBILITY_MIN_GLOBAL_WORKS = 50
COUNTRIES = ["de", "cn", "jp"]

EXPECTED_ELIGIBLE_COUNTS_KNOWN: Dict[int, int] = {
    2015: 990,
    2016: 990,
    2017: 991,
    2018: 992,
    2021: 995,
}

# Canonical Column Separation: Identifiers vs. Target vs. Features vs. Audit Sums
IDENTIFIER_COLUMNS: List[str] = [
    "forecast_origin",
    "topic_id",
    "topic_name",
    "field_name",
    "subfield_name",
    "eligible",
]

TARGET_COLUMN = "g_adj"

MODEL_FEATURE_SETS: Dict[str, List[str]] = {
    "M0": [],  # Unfitted adjusted momentum benchmark: pred = m0_adj (no Ridge parameters)
    "M1": [
        "m0_adj",
        "ln_global_topic_3yr",
    ],
    "M2": [
        "m0_adj",
        "ln_global_topic_3yr",
        "ln_frac_de_3yr",
        "ln_frac_cn_3yr",
        "ln_frac_jp_3yr",
    ],
    "M3": [
        "m0_adj",
        "ln_global_topic_3yr",
        "ln_frac_de_3yr",
        "ln_frac_cn_3yr",
        "ln_frac_jp_3yr",
        "rca_frac_de_3yr",
        "rca_frac_cn_3yr",
        "rca_frac_jp_3yr",
    ],
    "M3-LogRCA": [
        "m0_adj",
        "ln_global_topic_3yr",
        "ln_frac_de_3yr",
        "ln_frac_cn_3yr",
        "ln_frac_jp_3yr",
        "ln_rca_frac_de_3yr",
        "ln_rca_frac_cn_3yr",
        "ln_rca_frac_jp_3yr",
    ],
    "M2-WC": [
        "m0_adj",
        "ln_global_topic_3yr",
        "ln_whole_de_3yr",
        "ln_whole_cn_3yr",
        "ln_whole_jp_3yr",
    ],
    "M3-WC": [
        "m0_adj",
        "ln_global_topic_3yr",
        "ln_whole_de_3yr",
        "ln_whole_cn_3yr",
        "ln_whole_jp_3yr",
        "rca_whole_de_3yr",
        "rca_whole_cn_3yr",
        "rca_whole_jp_3yr",
    ],
}

AUDIT_AUX_PAST_COLUMNS: List[str] = [
    "global_topic_prev3yr",
    "global_topic_3yr",
    "w_allsci_prev3yr",
    "w_allsci_past3yr",
    "frac_de_3yr",
    "frac_cn_3yr",
    "frac_jp_3yr",
    "denom_frac_de_3yr",
    "denom_frac_cn_3yr",
    "denom_frac_jp_3yr",
    "whole_de_3yr",
    "whole_cn_3yr",
    "whole_jp_3yr",
    "denom_whole_de_3yr",
    "denom_whole_cn_3yr",
    "denom_whole_jp_3yr",
]

AUDIT_AUX_FUTURE_COLUMNS: List[str] = [
    "target_global_topic_fut3yr",
    "target_w_allsci_fut3yr",
]

OUTPUT_COLUMN_ORDER: List[str] = (
    IDENTIFIER_COLUMNS
    + [TARGET_COLUMN]
    + [
        "m0_adj",
        "ln_global_topic_3yr",
        "ln_frac_de_3yr",
        "ln_frac_cn_3yr",
        "ln_frac_jp_3yr",
        "rca_frac_de_3yr",
        "rca_frac_cn_3yr",
        "rca_frac_jp_3yr",
        "ln_rca_frac_de_3yr",
        "ln_rca_frac_cn_3yr",
        "ln_rca_frac_jp_3yr",
        "ln_whole_de_3yr",
        "ln_whole_cn_3yr",
        "ln_whole_jp_3yr",
        "rca_whole_de_3yr",
        "rca_whole_cn_3yr",
        "rca_whole_jp_3yr",
    ]
    + AUDIT_AUX_PAST_COLUMNS
    + AUDIT_AUX_FUTURE_COLUMNS
)


def sha256_file(path: Path) -> str:
    """Compute SHA-256 hex digest of a file without altering it."""
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def check_git_checkpoint() -> Dict[str, Any]:
    """Verify repository HEAD exists and includes documentation checkpoint ffc1716."""
    head = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=BASE_DIR, text=True
    ).strip()
    is_ancestor_proc = subprocess.run(
        ["git", "merge-base", "--is-ancestor", REQUIRED_ANCESTOR_COMMIT, "HEAD"],
        cwd=BASE_DIR,
    )
    if is_ancestor_proc.returncode != 0:
        raise RuntimeError(
            f"Git HEAD ({head}) does not contain required checkpoint commit {REQUIRED_ANCESTOR_COMMIT}."
        )
    return {
        "git_head": head,
        "required_checkpoint_commit": REQUIRED_ANCESTOR_COMMIT,
        "checkpoint_is_ancestor": True,
    }


def check_software_environment() -> Dict[str, str]:
    """Verify pinned dependency floor (scikit-learn >= 1.6) and capture versions."""
    sk_parts = tuple(int(p) for p in sklearn.__version__.split(".")[:2])
    if sk_parts < (1, 6):
        raise RuntimeError(
            f"scikit-learn >= 1.6 is required by locked Section 7 spec; found {sklearn.__version__}"
        )
    return {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "numpy": np.__version__,
        "pandas": pd.__version__,
        "scipy": scipy.__version__,
        "scikit_learn": sklearn.__version__,
    }


def validate_inputs(df_panel: pd.DataFrame, df_denom: pd.DataFrame) -> None:
    """Validate structure, bounds, and panel-to-denominator synchronization."""
    if df_panel.shape != (15375, 26):
        raise ValueError(f"Unexpected panel shape: {df_panel.shape} != (15375, 26)")
    if df_denom.shape != (15, 10):
        raise ValueError(f"Unexpected denominator shape: {df_denom.shape} != (15, 10)")
    if df_panel["topic_id"].nunique() != EXPECTED_TOPICS:
        raise ValueError(f"Expected {EXPECTED_TOPICS} topics, got {df_panel['topic_id'].nunique()}")
    if sorted(df_panel["year"].unique().tolist()) != EXPECTED_PANEL_YEARS:
        raise ValueError("Panel year coverage mismatch; expected 2010–2024.")
    if sorted(df_denom["year"].unique().tolist()) != EXPECTED_PANEL_YEARS:
        raise ValueError("Denominator year coverage mismatch; expected 2010–2024.")
    if df_panel.duplicated(subset=["topic_id", "year"]).any():
        raise ValueError("Duplicate (topic_id, year) rows detected in input panel.")
    if df_panel.isnull().any().any() or df_denom.isnull().any().any():
        raise ValueError("Null values detected in frozen Stage 2 input files.")

    # Verify panel annual denominator columns match denominator CSV 100%
    denom_by_yr = df_denom.set_index("year")
    for yr in EXPECTED_PANEL_YEARS:
        sub = df_panel[df_panel["year"] == yr]
        ref = denom_by_yr.loc[yr]
        if not (sub["global_allsci_denom"] == int(ref["global_allsci"])).all():
            raise ValueError(f"Year {yr}: panel global_allsci_denom diverges from denominator CSV.")
        for c in COUNTRIES:
            if not (sub[f"{c}_allsci_whole_denom"] == int(ref[f"{c}_whole"])).all():
                raise ValueError(f"Year {yr}: panel {c}_allsci_whole_denom diverges.")
            if not (np.abs(sub[f"{c}_allsci_frac_denom"] - float(ref[f"{c}_frac"])) < 1e-9).all():
                raise ValueError(f"Year {yr}: panel {c}_allsci_frac_denom diverges.")


def compute_window_sum(
    matrix: pd.DataFrame, start_year: int, end_year: int
) -> np.ndarray:
    """Compute closed-interval 3-year sum across columns [start_year, end_year]."""
    years = list(range(start_year, end_year + 1))
    if len(years) != 3:
        raise ValueError(f"Window [{start_year}, {end_year}] must span exactly 3 years.")
    return matrix.loc[:, years].to_numpy(dtype=np.float64).sum(axis=1)


def compute_three_year_rca(
    country_3yr: np.ndarray,
    country_denom_3yr: float,
    global_topic_3yr: np.ndarray,
    global_denom_3yr: float,
) -> np.ndarray:
    """
    Compute 3-year ratio-of-sums RCA safely:
        RCA = (P_c / D_c) / (P_global / W_global)
    Returns 0.0 identically where P_global == 0 (ineligible zero-volume topics).
    """
    if country_denom_3yr <= 0 or global_denom_3yr <= 0:
        raise ValueError("All-science 3-year denominators must be strictly positive.")

    topic_share = country_3yr / country_denom_3yr
    global_share = global_topic_3yr / global_denom_3yr
    return np.divide(
        topic_share,
        global_share,
        out=np.zeros_like(topic_share, dtype=np.float64),
        where=global_share > 0.0,
    )


def build_origin_dataframe(
    origin: int,
    topic_meta: pd.DataFrame,
    pivots: Dict[str, pd.DataFrame],
    denom_by_yr: pd.DataFrame,
) -> pd.DataFrame:
    """Construct all 1,025 topic-origin rows for a single forecast origin t."""
    # Explicit disjoint 3-year windows
    prev_start, prev_end = origin - 5, origin - 3
    past_start, past_end = origin - 2, origin
    fut_start, fut_end = origin + 1, origin + 3

    if prev_start < 2010 or fut_end > 2024:
        raise ValueError(f"Origin {origin} exceeds 2010–2024 panel bounds.")

    # Global topic 3-year counts
    p_prev3yr = compute_window_sum(pivots["global_count"], prev_start, prev_end)
    p_past3yr = compute_window_sum(pivots["global_count"], past_start, past_end)
    p_fut3yr = compute_window_sum(pivots["global_count"], fut_start, fut_end)

    # Global all-science 3-year sums W_[a,b]
    w_prev3yr = float(denom_by_yr.loc[prev_start:prev_end, "global_allsci"].sum())
    w_past3yr = float(denom_by_yr.loc[past_start:past_end, "global_allsci"].sum())
    w_fut3yr = float(denom_by_yr.loc[fut_start:fut_end, "global_allsci"].sum())

    # Target G_adj(i,t) and Benchmark M0_adj(i,t)
    g_adj = (np.log1p(p_fut3yr) - np.log1p(p_past3yr)) - (
        np.log1p(w_fut3yr) - np.log1p(w_past3yr)
    )
    m0_adj = (np.log1p(p_past3yr) - np.log1p(p_prev3yr)) - (
        np.log1p(w_past3yr) - np.log1p(w_prev3yr)
    )

    # Eligibility rule strictly from past [t-2, t] global volume >= 50
    eligible = p_past3yr >= ELIGIBILITY_MIN_GLOBAL_WORKS

    data: Dict[str, Any] = {
        "forecast_origin": np.full(len(topic_meta), origin, dtype=np.int64),
        "topic_id": topic_meta["topic_id"].to_numpy(),
        "topic_name": topic_meta["topic_name"].to_numpy(),
        "field_name": topic_meta["field_name"].to_numpy(),
        "subfield_name": topic_meta["subfield_name"].to_numpy(),
        "eligible": eligible.astype(bool),
        "g_adj": g_adj,
        "m0_adj": m0_adj,
        "ln_global_topic_3yr": np.log1p(p_past3yr),
        "global_topic_prev3yr": p_prev3yr.astype(np.int64),
        "global_topic_3yr": p_past3yr.astype(np.int64),
        "target_global_topic_fut3yr": p_fut3yr.astype(np.int64),
        "w_allsci_prev3yr": np.full(len(topic_meta), int(round(w_prev3yr)), dtype=np.int64),
        "w_allsci_past3yr": np.full(len(topic_meta), int(round(w_past3yr)), dtype=np.int64),
        "target_w_allsci_fut3yr": np.full(len(topic_meta), int(round(w_fut3yr)), dtype=np.int64),
    }

    # Country features over [t-2, t]: fractional primary + log-RCA + whole-count sensitivity
    for c in COUNTRIES:
        c_frac_3yr = compute_window_sum(pivots[f"{c}_frac_count"], past_start, past_end)
        # Source annual fractional denominators are exact to 4 decimal places; round(4) removes IEEE-754 addition noise
        d_frac_3yr = round(float(denom_by_yr.loc[past_start:past_end, f"{c}_frac"].sum()), 4)
        rca_frac_3yr = compute_three_year_rca(c_frac_3yr, d_frac_3yr, p_past3yr, w_past3yr)

        c_whole_3yr = compute_window_sum(pivots[f"{c}_whole_count"], past_start, past_end)
        d_whole_3yr = float(denom_by_yr.loc[past_start:past_end, f"{c}_whole"].sum())
        rca_whole_3yr = compute_three_year_rca(c_whole_3yr, d_whole_3yr, p_past3yr, w_past3yr)

        data[f"ln_frac_{c}_3yr"] = np.log1p(c_frac_3yr)
        data[f"rca_frac_{c}_3yr"] = rca_frac_3yr
        data[f"ln_rca_frac_{c}_3yr"] = np.log1p(rca_frac_3yr)

        data[f"ln_whole_{c}_3yr"] = np.log1p(c_whole_3yr)
        data[f"rca_whole_{c}_3yr"] = rca_whole_3yr

        data[f"frac_{c}_3yr"] = c_frac_3yr
        data[f"denom_frac_{c}_3yr"] = np.full(len(topic_meta), d_frac_3yr, dtype=np.float64)
        data[f"whole_{c}_3yr"] = c_whole_3yr.astype(np.int64)
        data[f"denom_whole_{c}_3yr"] = np.full(len(topic_meta), int(round(d_whole_3yr)), dtype=np.int64)

    return pd.DataFrame(data)[OUTPUT_COLUMN_ORDER]


def run_builder_validations(df_out: pd.DataFrame) -> Dict[str, Any]:
    """Run Checks A-E strictly inside builder prior to persistence."""
    expected_rows = EXPECTED_TOPICS * len(FORECAST_ORIGINS)
    if df_out.shape != (expected_rows, len(OUTPUT_COLUMN_ORDER)):
        raise ValueError(f"Output shape mismatch: {df_out.shape}")

    # Check A: G_adj(i,t) == M0_adj(i,t+3) across all 1,025 topics for t=2015..2018
    identity_diffs: Dict[str, float] = {}
    for t in [2015, 2016, 2017, 2018]:
        s_t = df_out[df_out["forecast_origin"] == t].sort_values("topic_id")
        s_t3 = df_out[df_out["forecast_origin"] == t + 3].sort_values("topic_id")
        if not (s_t["topic_id"].to_numpy() == s_t3["topic_id"].to_numpy()).all():
            raise AssertionError(f"Topic misalignment at {t} vs {t+3}")
        max_diff = float(np.max(np.abs(s_t["g_adj"].to_numpy() - s_t3["m0_adj"].to_numpy())))
        if max_diff >= 1e-12:
            raise AssertionError(f"Identity failure at t={t}: max_diff={max_diff}")
        identity_diffs[f"{t}_to_{t+3}"] = max_diff

    # Check C: Eligibility counts
    elig_counts: Dict[int, Dict[str, int]] = {}
    for t in FORECAST_ORIGINS:
        sub = df_out[df_out["forecast_origin"] == t]
        n_elig = int(sub["eligible"].sum())
        n_total = len(sub)
        if t in EXPECTED_ELIGIBLE_COUNTS_KNOWN and n_elig != EXPECTED_ELIGIBLE_COUNTS_KNOWN[t]:
            raise AssertionError(
                f"Origin {t}: eligible={n_elig} != expected {EXPECTED_ELIGIBLE_COUNTS_KNOWN[t]}"
            )
        elig_counts[t] = {
            "total_topics": n_total,
            "eligible_topics": n_elig,
            "ineligible_topics": n_total - n_elig,
        }

    # Check D: Finite, Null-Free & Bounds checks on all rows & eligible rows
    if df_out.isnull().any().any():
        raise AssertionError("Null values found in output dataset.")
    num_cols = df_out.select_dtypes(include=[np.number]).columns.tolist()
    if not np.isfinite(df_out[num_cols].to_numpy(dtype=np.float64)).all():
        raise AssertionError("Non-finite (Inf/NaN) values found in output numeric columns.")
    for c in COUNTRIES:
        if (df_out[f"rca_frac_{c}_3yr"] < 0).any() or (df_out[f"rca_whole_{c}_3yr"] < 0).any():
            raise AssertionError(f"Negative RCA detected for {c}.")
        if (df_out[f"frac_{c}_3yr"] > df_out[f"whole_{c}_3yr"] + 1e-9).any():
            raise AssertionError(f"Fractional count exceeds whole count for {c}.")
        if (df_out[f"whole_{c}_3yr"] > df_out["global_topic_3yr"]).any():
            raise AssertionError(f"Whole count exceeds global count for {c}.")

    # Check E: Feature definitions & future leakage isolation
    assert len(MODEL_FEATURE_SETS["M1"]) == 2
    assert len(MODEL_FEATURE_SETS["M2"]) == 5
    assert len(MODEL_FEATURE_SETS["M3"]) == 8
    assert len(MODEL_FEATURE_SETS["M3-LogRCA"]) == 8
    assert len(MODEL_FEATURE_SETS["M2-WC"]) == 5
    assert len(MODEL_FEATURE_SETS["M3-WC"]) == 8

    forbidden = set(IDENTIFIER_COLUMNS + [TARGET_COLUMN] + AUDIT_AUX_FUTURE_COLUMNS)
    for model_name, feats in MODEL_FEATURE_SETS.items():
        overlap = forbidden.intersection(feats)
        if overlap:
            raise AssertionError(f"Model {model_name} contains forbidden columns: {overlap}")

    return {
        "check_a_identity_max_abs_diff": identity_diffs,
        "check_c_eligibility_counts": elig_counts,
        "check_d_all_rows_finite_no_nulls": True,
        "check_e_feature_lengths_and_leakage_isolation": True,
    }


def main() -> int:
    print("=" * 88)
    print("STAGE 3.1: FEATURE AND TARGET CONSTRUCTION")
    print("=" * 88)

    git_info = check_git_checkpoint()
    env_info = check_software_environment()
    print(f"Git HEAD:      {git_info['git_head']} (contains {REQUIRED_ANCESTOR_COMMIT})")
    print(
        f"Environment:   Python {env_info['python']} | pandas {env_info['pandas']} | "
        f"numpy {env_info['numpy']} | scipy {env_info['scipy']} | scikit-learn {env_info['scikit_learn']}"
    )

    if not PANEL_PATH.exists() or not DENOM_PATH.exists():
        raise FileNotFoundError("Frozen Stage 2 input file(s) missing.")

    panel_sha_pre = sha256_file(PANEL_PATH)
    denom_sha_pre = sha256_file(DENOM_PATH)
    print(f"Pre-run Panel SHA-256: {panel_sha_pre}")
    print(f"Pre-run Denom SHA-256: {denom_sha_pre}")

    if panel_sha_pre != EXPECTED_PANEL_SHA256:
        raise ValueError(f"Panel SHA-256 mismatch: {panel_sha_pre} != {EXPECTED_PANEL_SHA256}")
    if denom_sha_pre != EXPECTED_DENOM_SHA256:
        raise ValueError(f"Denom SHA-256 mismatch: {denom_sha_pre} != {EXPECTED_DENOM_SHA256}")

    # Load frozen inputs read-only
    df_panel = pd.read_csv(PANEL_PATH)
    df_denom = pd.read_csv(DENOM_PATH)
    validate_inputs(df_panel, df_denom)

    df_panel = df_panel.sort_values(["topic_id", "year"]).reset_index(drop=True)
    denom_by_yr = df_denom.sort_values("year").set_index("year")

    topic_meta = (
        df_panel[["topic_id", "topic_name", "field_name", "subfield_name"]]
        .drop_duplicates()
        .sort_values("topic_id")
        .reset_index(drop=True)
    )

    pivot_cols = ["global_count"] + [
        f"{c}_{kind}_count" for c in COUNTRIES for kind in ("frac", "whole")
    ]
    pivots = {
        col: df_panel.pivot(index="topic_id", columns="year", values=col).loc[
            topic_meta["topic_id"]
        ]
        for col in pivot_cols
    }

    origin_frames = [
        build_origin_dataframe(t, topic_meta, pivots, denom_by_yr)
        for t in FORECAST_ORIGINS
    ]
    df_out = (
        pd.concat(origin_frames, ignore_index=True)
        .sort_values(["forecast_origin", "topic_id"])
        .reset_index(drop=True)
    )

    validation_summary = run_builder_validations(df_out)

    # Ensure output directory exists and serialize deterministically
    STAGE3_DIR.mkdir(parents=True, exist_ok=True)
    df_out.to_csv(
        OUTPUT_CSV_PATH,
        index=False,
        encoding="utf-8",
        lineterminator="\n",
    )
    output_sha = sha256_file(OUTPUT_CSV_PATH)

    # Check F: Post-write frozen input hash re-verification
    panel_sha_post = sha256_file(PANEL_PATH)
    denom_sha_post = sha256_file(DENOM_PATH)
    if panel_sha_post != EXPECTED_PANEL_SHA256 or denom_sha_post != EXPECTED_DENOM_SHA256:
        raise RuntimeError("Frozen source dataset hash altered during processing!")

    created_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    manifest: Dict[str, Any] = {
        "stage": "3.1_feature_and_target_construction",
        "created_utc": created_utc,
        "git": git_info,
        "software_environment": env_info,
        "inputs": {
            "primary_panel": {
                "path": str(PANEL_PATH.relative_to(BASE_DIR)).replace("\\", "/"),
                "rows": int(df_panel.shape[0]),
                "columns": int(df_panel.shape[1]),
                "sha256_pre": panel_sha_pre,
                "sha256_post": panel_sha_post,
                "expected_sha256": EXPECTED_PANEL_SHA256,
                "preserved_byte_for_byte": (panel_sha_pre == panel_sha_post == EXPECTED_PANEL_SHA256),
            },
            "national_denominators": {
                "path": str(DENOM_PATH.relative_to(BASE_DIR)).replace("\\", "/"),
                "rows": int(df_denom.shape[0]),
                "columns": int(df_denom.shape[1]),
                "sha256_pre": denom_sha_pre,
                "sha256_post": denom_sha_post,
                "expected_sha256": EXPECTED_DENOM_SHA256,
                "preserved_byte_for_byte": (denom_sha_pre == denom_sha_post == EXPECTED_DENOM_SHA256),
            },
        },
        "output": {
            "path": str(OUTPUT_CSV_PATH.relative_to(BASE_DIR)).replace("\\", "/"),
            "rows": int(df_out.shape[0]),
            "columns": int(df_out.shape[1]),
            "column_order": OUTPUT_COLUMN_ORDER,
            "sha256": output_sha,
            "csv_serialization": {
                "index": False,
                "encoding": "utf-8",
                "lineterminator": "\\n",
                "float_format": None,
            },
        },
        "forecast_origins": FORECAST_ORIGINS,
        "topics_per_origin": EXPECTED_TOPICS,
        "eligibility_definition": {
            "column": "eligible",
            "rule": "sum(global_count over [t-2, t]) >= 50",
            "min_global_works_3yr": ELIGIBILITY_MIN_GLOBAL_WORKS,
            "ineligible_rows_retained": True,
        },
        "schema_roles": {
            "identifier_columns": IDENTIFIER_COLUMNS,
            "target_column": TARGET_COLUMN,
            "audit_past_window_columns": AUDIT_AUX_PAST_COLUMNS,
            "audit_future_window_columns": AUDIT_AUX_FUTURE_COLUMNS,
            "model_feature_sets": MODEL_FEATURE_SETS,
        },
        "formulas_and_windows": {
            "g_adj": "[ln(1 + P_Global(i,[t+1,t+3])) - ln(1 + P_Global(i,[t-2,t]))] - [ln(1 + W([t+1,t+3])) - ln(1 + W([t-2,t]))]",
            "m0_adj": "[ln(1 + P_Global(i,[t-2,t])) - ln(1 + P_Global(i,[t-5,t-3]))] - [ln(1 + W([t-2,t])) - ln(1 + W([t-5,t-3]))]",
            "log_counts": "ln(1 + sum(count over [t-2, t]))",
            "rca_frac_3yr": "ratio-of-sums: (sum_3yr(P_frac_c) / sum_3yr(Denom_frac_c)) / (sum_3yr(P_global) / sum_3yr(W_allsci)); 0.0 when P_global_3yr == 0",
            "ln_rca_frac_3yr": "ln(1 + rca_frac_c_3yr)",
            "rca_whole_3yr": "ratio-of-sums: (sum_3yr(P_whole_c) / sum_3yr(Denom_whole_c)) / (sum_3yr(P_global) / sum_3yr(W_allsci)); 0.0 when P_global_3yr == 0",
            "windows": {
                "momentum_base": "[t-5, t-3]",
                "recent_features_and_eligibility": "[t-2, t]",
                "future_target_only": "[t+1, t+3]",
            },
        },
        "builder_validation_results": validation_summary,
    }

    with open(MANIFEST_JSON_PATH, "w", encoding="utf-8", newline="\n") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")

    print(f"\nOutput CSV:    {OUTPUT_CSV_PATH} ({df_out.shape[0]:,} x {df_out.shape[1]})")
    print(f"Output SHA256: {output_sha}")
    print(f"Manifest JSON: {MANIFEST_JSON_PATH}")
    print("\nEligible counts per origin:")
    for t in FORECAST_ORIGINS:
        cinfo = validation_summary["check_c_eligibility_counts"][t]
        print(
            f"  Origin {t}: eligible={cinfo['eligible_topics']:,} / {cinfo['total_topics']:,} "
            f"(ineligible={cinfo['ineligible_topics']})"
        )
    print("\nMax |G_adj(i,t) - M0_adj(i,t+3)| across 1,025 topics:")
    for k, v in validation_summary["check_a_identity_max_abs_diff"].items():
        print(f"  {k}: {v:.3e}")
    print("\n[PASS] Stage 3.1 feature and target construction completed cleanly.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
