"""
Deterministic Post-Extraction Denominator Synchronization & RCA Recalculation Script
Script: openalex_feasibility_audit/synchronize_modeling_panel_v2.py

Purpose:
Reproducibly generates the primary modeling dataset:
    openalex_feasibility_audit/openalex_modeling_panel_1025topics_v2_synchronized.csv
by combining:
  1. Preserved Original Modeling Panel v2 (openalex_modeling_panel_1025topics_v2_selected_types.csv),
     which was extracted on 2026-11-04 (23:08–23:52 UTC+1) after OpenAlex's 4 November index
     deduplication (merging ~17.3M duplicate works), and
  2. Synchronized All-Science Denominators (all_science_national_denominators_fractional_v2_live_recheck_20261105.csv),
     extracted from the identical post-deduplication OpenAlex index state (23:54 UTC+0 / 00:54 UTC+1).

Methodological & Numerical Enhancements:
  - Full pre- and post-synchronization structural validation:
      * 15,375 rows, 1,025 unique topics, 15 years (2010–2024), 15 rows per topic.
      * Uniqueness of (topic_id, year) composite keys.
      * Denominator coverage (15 years, unique, no nulls, non-zero positive).
      * Completeness of column mappings (0 unmapped/NaN values).
      * Non-negativity of publication counts and validity of denominators.
  - Denominator precision investigation:
      * Source fractional denominators in the CSV are stored with up to 4 decimal places
        (produced via round(frac, 4) in extract_denominators_v2.py).
      * Explicit .round(4) is retained as a defensive safeguard against binary floating-point
        representation drift without changing established data precision.
  - Safe numerical division:
      * Replaces np.where() with vectorized np.divide(..., out=..., where=...) to eliminate
        zero-division runtime warnings on 0/0 cells (357 zero-publication topic-year rows).
  - Safe two-stage atomic file generation:
      * Writes output to a temporary staging file first (.tmp.csv).
      * Validates its SHA-256 against EXPECTED_SYNC_PANEL_SHA256 before atomic promotion.
  - Comprehensive environment metadata logging:
      * Records Python, pandas, NumPy, platform, and CSV serialization parameters.
"""

import sys
import os
import platform
import hashlib
from pathlib import Path
from typing import Dict, Any
import pandas as pd
import numpy as np

# -----------------------------------------------------------------------------
# Configuration & Constants
# -----------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
AUDIT_DIR = BASE_DIR / "openalex_feasibility_audit"

ORIG_PANEL_PATH = AUDIT_DIR / "openalex_modeling_panel_1025topics_v2_selected_types.csv"
SYNC_DENOM_PATH = AUDIT_DIR / "all_science_national_denominators_fractional_v2_live_recheck_20261105.csv"
SYNC_PANEL_PATH = AUDIT_DIR / "openalex_modeling_panel_1025topics_v2_synchronized.csv"

EXPECTED_ORIG_PANEL_SHA256 = "3d869014a463449e2c4bd44628fe174f6aedc954cd7c878922baae9488b75d6e"
EXPECTED_SYNC_DENOM_SHA256 = "9c2d9cccee65c156494b96447ce53045d43e514c74aa10ec9f1c85915b33afce"
EXPECTED_SYNC_PANEL_SHA256 = "f0049cd71f5ba8545c2e3cbb850e036a7b849828321cd23aa1d04771e60d7175"

EXPECTED_ROWS = 15375
EXPECTED_COLS = 26
EXPECTED_TOPICS = 1025
EXPECTED_YEARS = list(range(2010, 2025))

REQUIRED_PANEL_COLUMNS = [
    "topic_id", "topic_name", "field_name", "subfield_name", "year", "retrieval_timestamp",
    "global_count", "global_allsci_denom",
    "de_whole_count", "de_frac_count", "de_allsci_whole_denom", "de_allsci_frac_denom", "rca_frac_de", "rca_whole_de",
    "cn_whole_count", "cn_frac_count", "cn_allsci_whole_denom", "cn_allsci_frac_denom", "rca_frac_cn", "rca_whole_cn",
    "jp_whole_count", "jp_frac_count", "jp_allsci_whole_denom", "jp_allsci_frac_denom", "rca_frac_jp", "rca_whole_jp"
]

REQUIRED_DENOM_COLUMNS = [
    "year", "retrieval_timestamp_utc", "query_filter", "global_allsci",
    "de_whole", "de_frac", "cn_whole", "cn_frac", "jp_whole", "jp_frac"
]

# CSV Serialization Settings (for 100% deterministic bit-for-bit output)
CSV_SERIALIZATION_SETTINGS: Dict[str, Any] = {
    "index": False,
    "encoding": "utf-8",
    "lineterminator": "\r\n" if sys.platform.startswith("win") else "\n",
    "float_format": None,
}


def sha256_file(path: Path) -> str:
    """Computes SHA-256 cryptographic hash of a file."""
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def log_environment_metadata():
    """Logs runtime environment and package versions for scientific reproducibility."""
    print("=" * 88)
    print("ENVIRONMENT & SERIALIZATION METADATA")
    print("=" * 88)
    print(f"  Python Version:     {sys.version.split()[0]} ({platform.platform()})")
    print(f"  Pandas Version:     {pd.__version__}")
    print(f"  NumPy Version:      {np.__version__}")
    print(f"  CSV Serialization:  index={CSV_SERIALIZATION_SETTINGS['index']}, "
          f"encoding={CSV_SERIALIZATION_SETTINGS['encoding']}, "
          f"lineterminator={repr(CSV_SERIALIZATION_SETTINGS['lineterminator'])}")
    print("=" * 88)


def validate_input_structures(df_panel: pd.DataFrame, df_denom: pd.DataFrame):
    """
    Performs comprehensive structural and data-type validation on input datasets
    before synchronization proceeds.
    """
    print("\n[VALIDATION 1/3] Validating Input Structures & Metadata...")

    # 1. Panel Dimensions & Keys
    if len(df_panel) != EXPECTED_ROWS:
        raise ValueError(f"Panel row count mismatch: {len(df_panel)} != {EXPECTED_ROWS}")
    if df_panel["topic_id"].nunique() != EXPECTED_TOPICS:
        raise ValueError(f"Panel topic count mismatch: {df_panel['topic_id'].nunique()} != {EXPECTED_TOPICS}")
    if sorted(df_panel["year"].unique().tolist()) != EXPECTED_YEARS:
        raise ValueError(f"Panel year coverage mismatch: expected {EXPECTED_YEARS}")
    
    counts_per_topic = df_panel.groupby("topic_id").size()
    if not (counts_per_topic == len(EXPECTED_YEARS)).all():
        raise ValueError("Panel is unbalanced: not all topics have exactly 15 annual observations.")
    
    dup_keys = df_panel.duplicated(subset=["topic_id", "year"]).sum()
    if dup_keys > 0:
        raise ValueError(f"Found {dup_keys} duplicate (topic_id, year) keys in input panel!")

    # 2. Panel Columns & Nulls
    missing_panel_cols = [c for c in REQUIRED_PANEL_COLUMNS if c not in df_panel.columns]
    if missing_panel_cols:
        raise ValueError(f"Input panel missing required columns: {missing_panel_cols}")
    null_panel = df_panel[REQUIRED_PANEL_COLUMNS].isnull().sum().sum()
    if null_panel > 0:
        raise ValueError(f"Found {null_panel} null values in input panel!")

    # 3. Panel Non-Negativity Checks
    if (df_panel["global_count"] < 0).any():
        raise ValueError("Found negative global_count values in panel!")
    for c in ["de", "cn", "jp"]:
        if (df_panel[f"{c}_whole_count"] < 0).any():
            raise ValueError(f"Found negative {c}_whole_count values in panel!")
        if (df_panel[f"{c}_frac_count"] < 0).any():
            raise ValueError(f"Found negative {c}_frac_count values in panel!")

    # 4. Denominator Dimensions & Keys
    if len(df_denom) != len(EXPECTED_YEARS):
        raise ValueError(f"Denominator row count mismatch: {len(df_denom)} != {len(EXPECTED_YEARS)}")
    if sorted(df_denom["year"].unique().tolist()) != EXPECTED_YEARS:
        raise ValueError(f"Denominator year coverage mismatch: expected {EXPECTED_YEARS}")
    if df_denom["year"].duplicated().sum() > 0:
        raise ValueError("Found duplicate year entries in denominator table!")

    # 5. Denominator Columns, Nulls & Non-Zero Validity
    missing_denom_cols = [c for c in REQUIRED_DENOM_COLUMNS if c not in df_denom.columns]
    if missing_denom_cols:
        raise ValueError(f"Denominator table missing required columns: {missing_denom_cols}")
    null_denom = df_denom[REQUIRED_DENOM_COLUMNS].isnull().sum().sum()
    if null_denom > 0:
        raise ValueError(f"Found {null_denom} null values in denominator table!")

    if (df_denom["global_allsci"] <= 0).any():
        raise ValueError("Invalid global_allsci denominator: non-positive values found!")
    for c in ["de", "cn", "jp"]:
        if (df_denom[f"{c}_whole"] <= 0).any():
            raise ValueError(f"Invalid {c}_whole denominator: non-positive values found!")
        if (df_denom[f"{c}_frac"] <= 0).any():
            raise ValueError(f"Invalid {c}_frac denominator: non-positive values found!")

    # 6. Map Coverage Verification
    panel_years = set(df_panel["year"].unique())
    denom_years = set(df_denom["year"].unique())
    if not panel_years.issubset(denom_years):
        raise ValueError(f"Panel years not covered by denominator table: {panel_years - denom_years}")

    print("  [PASS] Panel: 15,375 rows, 1,025 topics, 15 balanced years (2010–2024).")
    print("  [PASS] Keys: 0 duplicate (topic_id, year) composite pairs.")
    print("  [PASS] Completeness: 0 nulls across all 26 panel and 10 denominator columns.")
    print("  [PASS] Bounds: All publication counts non-negative; all denominators positive and valid.")
    print("  [PASS] Year Mapping: 100% of panel years map deterministically to denominator table.")


def validate_synchronized_panel(df_panel: pd.DataFrame, df_denom: pd.DataFrame):
    """
    Validates structural and numerical properties of the synchronized panel
    after denominator injection and RCA recalculation.
    """
    print("\n[VALIDATION 2/3] Validating Synchronized Panel Invariance & Precision...")

    # Verify column count and absence of NaN/Inf
    if len(df_panel) != EXPECTED_ROWS or len(df_panel.columns) != EXPECTED_COLS:
        raise ValueError(f"Synchronized panel dimension error: {df_panel.shape} != ({EXPECTED_ROWS}, {EXPECTED_COLS})")
    
    if df_panel.isnull().sum().sum() > 0:
        raise ValueError("Synchronized panel contains null values!")

    denom_map = df_denom.set_index("year")

    # Verify denominator columns strictly match denominator source for every year
    for yr in EXPECTED_YEARS:
        sub = df_panel[df_panel["year"] == yr]
        ref = denom_map.loc[yr]
        if not (sub["global_allsci_denom"] == int(ref["global_allsci"])).all():
            raise ValueError(f"Year {yr}: global_allsci_denom mismatch in panel!")
        for c in ["de", "cn", "jp"]:
            if not (sub[f"{c}_allsci_whole_denom"] == int(ref[f"{c}_whole"])).all():
                raise ValueError(f"Year {yr}: {c}_allsci_whole_denom mismatch in panel!")
            if not (np.abs(sub[f"{c}_allsci_frac_denom"] - round(float(ref[f"{c}_frac"]), 4)) < 1e-9).all():
                raise ValueError(f"Year {yr}: {c}_allsci_frac_denom mismatch in panel!")

    # Verify RCA columns are non-negative and finite
    for c in ["de", "cn", "jp"]:
        for rca_type in ["whole", "frac"]:
            col = f"rca_{rca_type}_{c}"
            if (df_panel[col] < 0).any():
                raise ValueError(f"Found negative RCA values in {col}!")
            if np.isinf(df_panel[col]).any():
                raise ValueError(f"Found infinite RCA values in {col}!")
            if np.isnan(df_panel[col]).any():
                raise ValueError(f"Found NaN RCA values in {col}!")

    print("  [PASS] Stored denominators match post-deduplication reference 100% across all 15 years.")
    print("  [PASS] All 6 Whole and Fractional RCA columns are non-negative, finite, and well-behaved.")


def synchronize_panel() -> int:
    """
    Executes reproducible, leak-free post-extraction denominator synchronization
    and RCA recalculation.
    """
    log_environment_metadata()

    print("\n" + "=" * 88)
    print("CHECKING INPUT INTEGRITY & REPRODUCIBILITY HASHES")
    print("=" * 88)

    if not ORIG_PANEL_PATH.exists():
        print(f"[FAIL] Missing input original panel: {ORIG_PANEL_PATH}")
        return 1
    if not SYNC_DENOM_PATH.exists():
        print(f"[FAIL] Missing synchronized denominator table: {SYNC_DENOM_PATH}")
        return 1

    orig_sha = sha256_file(ORIG_PANEL_PATH)
    denom_sha = sha256_file(SYNC_DENOM_PATH)
    print(f"Input Original Panel v2 SHA-256:  {orig_sha}")
    print(f"Input Sync Denominators SHA-256:  {denom_sha}")

    if orig_sha != EXPECTED_ORIG_PANEL_SHA256:
        print(f"[FAIL] Original Panel v2 SHA-256 mismatch! Expected {EXPECTED_ORIG_PANEL_SHA256}")
        return 1
    if denom_sha != EXPECTED_SYNC_DENOM_SHA256:
        print(f"[FAIL] Synchronized Denominators SHA-256 mismatch! Expected {EXPECTED_SYNC_DENOM_SHA256}")
        return 1

    print("[PASS] Input files match frozen reference SHA-256 hashes exactly.")

    # Load input data
    df_panel = pd.read_csv(ORIG_PANEL_PATH)
    df_denom = pd.read_csv(SYNC_DENOM_PATH)

    # 1. Structural Validation
    validate_input_structures(df_panel, df_denom)

    denom_map = df_denom.set_index("year")

    # 2. Update Global All-Science Denominator
    df_panel["global_allsci_denom"] = df_panel["year"].map(denom_map["global_allsci"]).astype(int)

    # Compute Global Share using safe vectorized division:
    # global_share = P_global(i, t) / W_global(t)
    # where=condition guards against zero denominators or zero global publications
    global_share = np.divide(
        df_panel["global_count"].to_numpy(dtype=float),
        df_panel["global_allsci_denom"].to_numpy(dtype=float),
        out=np.zeros(len(df_panel), dtype=float),
        where=(df_panel["global_allsci_denom"].to_numpy(dtype=float) > 0)
        & (df_panel["global_count"].to_numpy(dtype=float) > 0),
    )

    # 3. Update Country Denominators and Recalculate Whole & Fractional RCA safely
    for c in ["de", "cn", "jp"]:
        df_panel[f"{c}_allsci_whole_denom"] = df_panel["year"].map(denom_map[f"{c}_whole"]).astype(int)
        
        # Denominator precision note: Source values in CSV have up to 4 decimal places.
        # .round(4) explicitly guards against IEEE-754 representation artifacts.
        df_panel[f"{c}_allsci_frac_denom"] = df_panel["year"].map(denom_map[f"{c}_frac"]).round(4)

        # Whole RCA via safe vectorized division:
        # topic_share_w = P_whole(c, i, t) / Denom_whole(c, t)
        # rca_whole = topic_share_w / global_share
        topic_share_w = np.divide(
            df_panel[f"{c}_whole_count"].to_numpy(dtype=float),
            df_panel[f"{c}_allsci_whole_denom"].to_numpy(dtype=float),
            out=np.zeros(len(df_panel), dtype=float),
            where=(df_panel[f"{c}_allsci_whole_denom"].to_numpy(dtype=float) > 0)
            & (df_panel[f"{c}_whole_count"].to_numpy(dtype=float) > 0),
        )
        rca_whole = np.divide(
            topic_share_w,
            global_share,
            out=np.zeros(len(df_panel), dtype=float),
            where=(global_share > 0),
        )
        df_panel[f"rca_whole_{c}"] = np.round(rca_whole, 5)

        # Fractional RCA via safe vectorized division:
        # topic_share_f = P_frac(c, i, t) / Denom_frac(c, t)
        # rca_frac = topic_share_f / global_share
        topic_share_f = np.divide(
            df_panel[f"{c}_frac_count"].to_numpy(dtype=float),
            df_panel[f"{c}_allsci_frac_denom"].to_numpy(dtype=float),
            out=np.zeros(len(df_panel), dtype=float),
            where=(df_panel[f"{c}_allsci_frac_denom"].to_numpy(dtype=float) > 0)
            & (df_panel[f"{c}_frac_count"].to_numpy(dtype=float) > 0),
        )
        rca_frac = np.divide(
            topic_share_f,
            global_share,
            out=np.zeros(len(df_panel), dtype=float),
            where=(global_share > 0),
        )
        df_panel[f"rca_frac_{c}"] = np.round(rca_frac, 5)

    # 4. Post-Synchronization Structural & Precision Validation
    validate_synchronized_panel(df_panel, df_denom)

    # 5. Safe Atomic Two-Stage File Generation
    print("\n[VALIDATION 3/3] Staging to Temporary File & Verifying Output Hash...")
    temp_sync_path = SYNC_PANEL_PATH.with_suffix(".tmp.csv")

    try:
        # Write to temporary file with explicit serialization parameters
        df_panel.to_csv(
            temp_sync_path,
            index=CSV_SERIALIZATION_SETTINGS["index"],
            encoding=CSV_SERIALIZATION_SETTINGS["encoding"],
            lineterminator=CSV_SERIALIZATION_SETTINGS["lineterminator"],
        )

        temp_sha = sha256_file(temp_sync_path)
        print(f"Staged Temporary Output Path:     {temp_sync_path}")
        print(f"Staged Temporary Output Size:     {temp_sync_path.stat().st_size:,} bytes")
        print(f"Staged Temporary Output SHA-256:  {temp_sha}")

        if temp_sha != EXPECTED_SYNC_PANEL_SHA256:
            raise ValueError(
                f"Generated output SHA-256 ({temp_sha}) does not match expected hash ({EXPECTED_SYNC_PANEL_SHA256})! "
                "Promotion aborted to prevent dataset corruption."
            )

        # Atomic promotion: replace existing synchronized panel
        if SYNC_PANEL_PATH.exists():
            SYNC_PANEL_PATH.unlink()
        temp_sync_path.replace(SYNC_PANEL_PATH)
        print(f"[PASS] Promoted temporary file to primary target: {SYNC_PANEL_PATH}")

    except Exception as e:
        if temp_sync_path.exists():
            temp_sync_path.unlink()
        print(f"[FAIL] Atomic file generation error: {e}")
        return 1

    final_sha = sha256_file(SYNC_PANEL_PATH)
    print("\n" + "=" * 88)
    print("SYNCHRONIZATION & AUDIT SUMMARY")
    print("=" * 88)
    print(f"  Primary Dataset Target: {SYNC_PANEL_PATH}")
    print(f"  Final File Size:        {SYNC_PANEL_PATH.stat().st_size:,} bytes")
    print(f"  Final SHA-256 Checksum: {final_sha}")
    print(f"  Preserved Original:     {ORIG_PANEL_PATH} (SHA-256 verified unchanged)")
    print(f"  Synchronized Denoms:    {SYNC_DENOM_PATH} (SHA-256 verified unchanged)")
    print("  Numerical Precision:    All 6 RCA columns recomputed with safe np.divide (max error <= 0.00000500)")
    print("  Status:                 PASS (100% bit-for-bit deterministic reproduction)")
    print("=" * 88)
    return 0


if __name__ == "__main__":
    sys.exit(synchronize_panel())
