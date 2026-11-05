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
     extracted from the identical post-deduplication OpenAlex index state.

This script recalculates all six Whole and Fractional RCA columns (DE, CN, JP) directly from
the stored topic counts and synchronized denominators without re-running 4,100 API calls,
while verifying via SHA-256 checksums that the original frozen panel is never modified.
"""

import sys
import hashlib
from pathlib import Path
import pandas as pd
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
AUDIT_DIR = BASE_DIR / "openalex_feasibility_audit"

ORIG_PANEL_PATH = AUDIT_DIR / "openalex_modeling_panel_1025topics_v2_selected_types.csv"
SYNC_DENOM_PATH = AUDIT_DIR / "all_science_national_denominators_fractional_v2_live_recheck_20261105.csv"
SYNC_PANEL_PATH = AUDIT_DIR / "openalex_modeling_panel_1025topics_v2_synchronized.csv"

EXPECTED_ORIG_PANEL_SHA256 = "3d869014a463449e2c4bd44628fe174f6aedc954cd7c878922baae9488b75d6e"
EXPECTED_SYNC_DENOM_SHA256 = "9c2d9cccee65c156494b96447ce53045d43e514c74aa10ec9f1c85915b33afce"
EXPECTED_SYNC_PANEL_SHA256 = "f0049cd71f5ba8545c2e3cbb850e036a7b849828321cd23aa1d04771e60d7175"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def synchronize_panel() -> int:
    print("=" * 88)
    print("SYNCHRONIZING MODELING PANEL V2 WITH POST-DEDUPLICATION DENOMINATORS")
    print("=" * 88)

    if not ORIG_PANEL_PATH.exists():
        print(f"[FAIL] Missing input panel: {ORIG_PANEL_PATH}")
        return 1
    if not SYNC_DENOM_PATH.exists():
        print(f"[FAIL] Missing synchronized denominator file: {SYNC_DENOM_PATH}")
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

    df_panel = pd.read_csv(ORIG_PANEL_PATH)
    df_denom = pd.read_csv(SYNC_DENOM_PATH)

    denom_map = df_denom.set_index("year")

    # 1. Update Global All-Science Denominator
    df_panel["global_allsci_denom"] = df_panel["year"].map(denom_map["global_allsci"]).astype(int)

    # 2. Update Country All-Science Denominators and Recalculate Whole & Fractional RCA
    for c in ["de", "cn", "jp"]:
        df_panel[f"{c}_allsci_whole_denom"] = df_panel["year"].map(denom_map[f"{c}_whole"]).astype(int)
        df_panel[f"{c}_allsci_frac_denom"] = df_panel["year"].map(denom_map[f"{c}_frac"]).round(4)

        # Whole RCA from stored whole counts and synchronized denominators
        calc_whole = np.where(
            (df_panel["global_count"] > 0)
            & (df_panel[f"{c}_allsci_whole_denom"] > 0)
            & (df_panel[f"{c}_whole_count"] > 0),
            (df_panel[f"{c}_whole_count"] / df_panel[f"{c}_allsci_whole_denom"])
            / (df_panel["global_count"] / df_panel["global_allsci_denom"]),
            0.0,
        )
        df_panel[f"rca_whole_{c}"] = np.round(calc_whole, 5)

        # Fractional RCA from stored 6-decimal fractional counts and synchronized denominators
        calc_frac = np.where(
            (df_panel["global_count"] > 0)
            & (df_panel[f"{c}_allsci_frac_denom"] > 0)
            & (df_panel[f"{c}_frac_count"] > 0),
            (df_panel[f"{c}_frac_count"] / df_panel[f"{c}_allsci_frac_denom"])
            / (df_panel["global_count"] / df_panel["global_allsci_denom"]),
            0.0,
        )
        df_panel[f"rca_frac_{c}"] = np.round(calc_frac, 5)

    # 3. Write synchronized panel to disk
    df_panel.to_csv(SYNC_PANEL_PATH, index=False)
    out_sha = sha256_file(SYNC_PANEL_PATH)

    print(f"Output Synchronized Panel Path:   {SYNC_PANEL_PATH}")
    print(f"Output Synchronized Panel Rows:   {len(df_panel):,} rows x {len(df_panel.columns)} columns")
    print(f"Output Synchronized Panel SHA-256:{out_sha}")

    if out_sha != EXPECTED_SYNC_PANEL_SHA256:
        print(f"[FAIL] Output SHA-256 ({out_sha}) != expected ({EXPECTED_SYNC_PANEL_SHA256})")
        return 1

    print("[PASS] Deterministic synchronization verified (100% bit-for-bit reproducible).")
    print("=" * 88)
    return 0


if __name__ == "__main__":
    sys.exit(synchronize_panel())
