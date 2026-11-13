#!/usr/bin/env python3
"""Independent auditor for Stage 3.4 — RQ2 Held-Out Test Evaluation (M0–M3 ONLY).

Re-verifies upstream Stage 2 / 3.1 / 3.2 / 3.3 SHA-256 hashes, test data keys
and eligibility, frozen Stage 3.3 pipeline parameters, independent predictions,
independent MAE and B=5,000 paired bootstrap percentile CIs, Chapter 5 tables
and rendered figure values, zero absolute paths, strict Stage 3.4 boundaries
(zero refitting, zero RQ3, zero sensitivity analysis), temp-dir determinism,
and post-audit upstream immutability — without importing from builder scripts.
"""

from __future__ import annotations

import ast
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
EVAL_DIR = Path(__file__).resolve().parent
BUILDER_SCRIPT = EVAL_DIR / "build_stage3_4_evaluation.py"
ASSETS_SCRIPT = EVAL_DIR / "thesis_assets" / "scripts" / "build_stage3_4_thesis_assets.py"
MANIFEST_PATH = EVAL_DIR / "stage3_4_manifest.json"
REPORT_PATH = EVAL_DIR / "stage3_4_audit_report.md"

SPLITS_DIR = REPO_ROOT / "stage3_modeling" / "stage3_2_splits"
STAGE3_3_DIR = REPO_ROOT / "stage3_modeling" / "stage3_3_ridge_tuning"
STAGE3_1_CSV = REPO_ROOT / "stage3_modeling" / "stage3_origin_features_targets.csv"
STAGE2_PANEL_CSV = (
    REPO_ROOT
    / "openalex_feasibility_audit"
    / "openalex_modeling_panel_1025topics_v2_synchronized.csv"
)
STAGE2_DENOM_CSV = (
    REPO_ROOT
    / "openalex_feasibility_audit"
    / "all_science_national_denominators_fractional_v2_live_recheck_20261105.csv"
)
STAGE3_2_MANIFEST_PATH = SPLITS_DIR / "stage3_2_splits_manifest.json"
STAGE3_3_MANIFEST_PATH = STAGE3_3_DIR / "stage3_3_ridge_manifest.json"
STAGE3_3_SUMMARY_PATH = STAGE3_3_DIR / "stage3_3_model_selection_summary.csv"

EXPECTED_UPSTREAM_SHAS = {
    "stage3_1_csv": "9fc15d6ed16ade633547bfca9efca1db92827aa665cbb4509d76c7dae057f488",
    "stage2_panel": "f0049cd71f5ba8545c2e3cbb850e036a7b849828321cd23aa1d04771e60d7175",
    "stage2_denom": "9c2d9cccee65c156494b96447ce53045d43e514c74aa10ec9f1c85915b33afce",
    "stage3_2_manifest": "934f6e19fa54fb5b7b5121b02f4b278aa8e52b9c7265c4db550c30b371edafcd",
}
EXPECTED_CHECKPOINT_COMMIT = "17b5f8969eb08390b194f114d89af8b5b5762f48"

MODEL_FEATURES = {
    "M0": [],
    "M1": ["m0_adj", "ln_global_topic_3yr"],
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
}
COMPARISONS = [
    ("M1_vs_M0", "M1", "M0"),
    ("M2_vs_M1", "M2", "M1"),
    ("M3_vs_M2", "M3", "M2"),
    ("M3_vs_M0", "M3", "M0"),
]
EXP_SPECS = {
    "2018": {"origin": 2018, "n_test": 992},
    "2021": {"origin": 2021, "n_test": 995},
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def scan_for_absolute_paths(obj: Any, prefix: str = "") -> list[str]:
    hits: list[str] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            hits.extend(scan_for_absolute_paths(v, f"{prefix}.{k}" if prefix else str(k)))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            hits.extend(scan_for_absolute_paths(item, f"{prefix}[{i}]"))
    elif isinstance(obj, str):
        if re.search(r"[A-Za-z]:[/\\]", obj):
            hits.append(f"{prefix}={obj}")
        elif obj.startswith("/") and not obj.startswith("//"):
            hits.append(f"{prefix}={obj}")
    return hits


def main() -> int:
    checks: list[tuple[str, str, str]] = []

    def record(name: str, passed: bool, detail: str) -> None:
        checks.append((name, "PASS" if passed else "FAIL", detail))

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    s32_manifest = json.loads(STAGE3_2_MANIFEST_PATH.read_text(encoding="utf-8"))
    s33_manifest = json.loads(STAGE3_3_MANIFEST_PATH.read_text(encoding="utf-8"))

    # C1: Upstream Stage 2, 3.1, and 3.2 SHA-256 + Git checkpoint verification.
    c1_errs: list[str] = []
    if sha256_file(STAGE3_1_CSV) != EXPECTED_UPSTREAM_SHAS["stage3_1_csv"]:
        c1_errs.append("stage3_1_csv_hash")
    if sha256_file(STAGE2_PANEL_CSV) != EXPECTED_UPSTREAM_SHAS["stage2_panel"]:
        c1_errs.append("stage2_panel_hash")
    if sha256_file(STAGE2_DENOM_CSV) != EXPECTED_UPSTREAM_SHAS["stage2_denom"]:
        c1_errs.append("stage2_denom_hash")
    if sha256_file(STAGE3_2_MANIFEST_PATH) != EXPECTED_UPSTREAM_SHAS["stage3_2_manifest"]:
        c1_errs.append("stage3_2_manifest_hash")
    for fname, meta in s32_manifest["outputs"].items():
        if sha256_file(SPLITS_DIR / fname) != meta["sha256"]:
            c1_errs.append(f"stage3_2_{fname}")
    anc = subprocess.run(
        ["git", "merge-base", "--is-ancestor", EXPECTED_CHECKPOINT_COMMIT, "HEAD"],
        cwd=str(REPO_ROOT),
        capture_output=True,
    )
    if anc.returncode != 0:
        c1_errs.append("checkpoint_17b5f89_not_ancestor")
    record(
        "C1_upstream_stage2_31_32_and_git_checkpoint",
        len(c1_errs) == 0,
        "Stage 2, Stage 3.1, all 12 Stage 3.2 CSVs, and checkpoint 17b5f89 verified"
        if not c1_errs
        else f"Errors: {c1_errs}",
    )

    # C2: Stage 3.3 manifest, summary, CV tables, and 6 joblib pipeline SHA-256 hashes.
    c2_errs: list[str] = []
    for rel_key, meta in s33_manifest["outputs"].items():
        fpath = STAGE3_3_DIR / rel_key
        if not fpath.is_file() or sha256_file(fpath) != meta["sha256"]:
            c2_errs.append(rel_key)
    for orig_str in ("2018", "2021"):
        for m in ("M1", "M2", "M3"):
            p_meta = s33_manifest["experiments"][orig_str]["models"][m]
            if (
                manifest["upstream_references"]["stage3_3_pipelines"][orig_str][m]["sha256"]
                != p_meta["pipeline_sha256"]
            ):
                c2_errs.append(f"manifest_pipe_{orig_str}_{m}")
    record(
        "C2_stage3_3_pipelines_and_manifest_integrity",
        len(c2_errs) == 0,
        "All 15 Stage 3.3 artifacts (6 joblib pipelines, 6 CV CSVs, 2 fold CSVs, summary CSV) match SHA-256"
        if not c2_errs
        else f"Mismatches: {c2_errs}",
    )

    # C3: Held-out test datasets integrity, row counts, unique keys, and feature/target separation.
    c3_errs: list[str] = []
    test_frames: dict[str, pd.DataFrame] = {}
    for orig_str, spec in EXP_SPECS.items():
        feat = pd.read_csv(SPLITS_DIR / f"test_{orig_str}_features.csv", float_precision="round_trip")
        targ = pd.read_csv(SPLITS_DIR / f"test_{orig_str}_targets.csv", float_precision="round_trip")
        if len(feat) != spec["n_test"] or len(targ) != spec["n_test"]:
            c3_errs.append(f"{orig_str}_row_count")
        if feat.duplicated(["forecast_origin", "topic_id"]).any() or targ.duplicated(
            ["forecast_origin", "topic_id"]
        ).any():
            c3_errs.append(f"{orig_str}_dup_keys")
        if feat["topic_id"].tolist() != targ["topic_id"].tolist():
            c3_errs.append(f"{orig_str}_key_alignment")
        if (feat["forecast_origin"].astype(int) != spec["origin"]).any() or (
            targ["forecast_origin"].astype(int) != spec["origin"]
        ).any():
            c3_errs.append(f"{orig_str}_origin_mismatch")
        if not (feat["eligible"] == True).all():  # noqa: E712
            c3_errs.append(f"{orig_str}_ineligible")
        merged = feat.merge(targ, on=["forecast_origin", "topic_id"], how="inner", validate="one_to_one")
        if len(merged) != spec["n_test"]:
            c3_errs.append(f"{orig_str}_merge_loss")
        num_cols = MODEL_FEATURES["M3"] + ["g_adj"]
        if not np.isfinite(merged[num_cols].to_numpy(dtype=np.float64)).all():
            c3_errs.append(f"{orig_str}_non_finite")
        test_frames[orig_str] = merged.sort_values(["forecast_origin", "topic_id"]).reset_index(drop=True)
    record(
        "C3_test_data_counts_keys_alignment_and_finite",
        len(c3_errs) == 0,
        "2018 (N=992) and 2021 (N=995) strictly 1:1 aligned, unique, eligible, and finite"
        if not c3_errs
        else f"Errors: {c3_errs}",
    )

    # C4: Independent prediction recomputation from M0 and frozen Stage 3.3 pipelines.
    c4_max_diff = 0.0
    c4_errs: list[str] = []
    indep_abs_errs: dict[str, dict[str, np.ndarray]] = {}
    for orig_str, spec in EXP_SPECS.items():
        df = test_frames[orig_str]
        pred_csv = pd.read_csv(
            EVAL_DIR / "predictions" / f"predictions_test_{orig_str}.csv",
            float_precision="round_trip",
        )
        if len(pred_csv) != spec["n_test"]:
            c4_errs.append(f"{orig_str}_pred_rows")
        if pred_csv["topic_id"].tolist() != df["topic_id"].tolist():
            c4_errs.append(f"{orig_str}_pred_topic_order")
        y_true = df["g_adj"].to_numpy(dtype=np.float64)
        indep_abs_errs[orig_str] = {}

        # M0 direct check
        m0_pred = df["m0_adj"].to_numpy(dtype=np.float64)
        c4_max_diff = max(
            c4_max_diff, float(np.max(np.abs(m0_pred - pred_csv["pred_m0"].to_numpy(dtype=np.float64))))
        )
        m0_abs = np.abs(y_true - m0_pred)
        c4_max_diff = max(
            c4_max_diff,
            float(np.max(np.abs(m0_abs - pred_csv["abs_error_m0"].to_numpy(dtype=np.float64)))),
        )
        indep_abs_errs[orig_str]["M0"] = m0_abs

        # M1-M3 frozen pipeline checks
        for m in ("M1", "M2", "M3"):
            m_meta = s33_manifest["experiments"][orig_str]["models"][m]
            pipe = joblib.load(REPO_ROOT / m_meta["pipeline_relative_path"])
            if list(pipe.named_steps.keys()) != ["scaler", "ridge"]:
                c4_errs.append(f"{orig_str}_{m}_steps")
            ridge = pipe.named_steps["ridge"]
            if not np.isclose(float(ridge.alpha), float(m_meta["selected_alpha"]), rtol=1e-12):
                c4_errs.append(f"{orig_str}_{m}_alpha")
            X_arr = df[MODEL_FEATURES[m]].to_numpy(dtype=np.float64)
            y_hat = pipe.predict(X_arr)
            if y_hat.shape != (spec["n_test"],) or not np.isfinite(y_hat).all():
                c4_errs.append(f"{orig_str}_{m}_invalid_pred")
            col_key = m.lower()
            c4_max_diff = max(
                c4_max_diff,
                float(np.max(np.abs(y_hat - pred_csv[f"pred_{col_key}"].to_numpy(dtype=np.float64)))),
            )
            err = y_true - y_hat
            abs_err = np.abs(err)
            c4_max_diff = max(
                c4_max_diff,
                float(np.max(np.abs(err - pred_csv[f"error_{col_key}"].to_numpy(dtype=np.float64)))),
                float(np.max(np.abs(abs_err - pred_csv[f"abs_error_{col_key}"].to_numpy(dtype=np.float64)))),
            )
            indep_abs_errs[orig_str][m] = abs_err

    record(
        "C4_independent_prediction_and_pipeline_parity",
        len(c4_errs) == 0 and c4_max_diff <= 1e-12,
        f"M0 direct + frozen M1–M3 pipelines match saved predictions CSVs; max_abs_diff={c4_max_diff:.3e}"
        if not c4_errs
        else f"Errors: {c4_errs}, max_diff={c4_max_diff:.3e}",
    )

    # C5: Independent MAE recomputation.
    mae_summary_df = pd.read_csv(EVAL_DIR / "metrics" / "mae_summary.csv", float_precision="round_trip")
    mae_ci_df = pd.read_csv(EVAL_DIR / "metrics" / "mae_bootstrap_ci.csv", float_precision="round_trip")
    c5_max_diff = 0.0
    indep_mae: dict[str, dict[str, float]] = {}
    for orig_str, spec in EXP_SPECS.items():
        indep_mae[orig_str] = {}
        for m in ("M0", "M1", "M2", "M3"):
            val = float(np.mean(indep_abs_errs[orig_str][m]))
            indep_mae[orig_str][m] = val
            row_s = mae_summary_df[
                (mae_summary_df["test_origin"] == spec["origin"]) & (mae_summary_df["model"] == m)
            ].iloc[0]
            row_c = mae_ci_df[
                (mae_ci_df["test_origin"] == spec["origin"]) & (mae_ci_df["model"] == m)
            ].iloc[0]
            c5_max_diff = max(
                c5_max_diff,
                abs(val - float(row_s["mae"])),
                abs(val - float(row_c["mae_observed"])),
                abs(val - float(manifest["experiments"][orig_str]["models"][m]["mae"])),
            )
    record(
        "C5_independent_mae_recompute",
        len(mae_summary_df) == 8 and c5_max_diff <= 1e-12,
        f"All 8 observed MAEs match independent recomputation; max_abs_diff={c5_max_diff:.3e}",
    )

    # C6: Independent bootstrap index matrix regeneration & exact verification.
    c6_errs: list[str] = []
    boot_matrices: dict[str, np.ndarray] = {}
    boot_meta = json.loads((EVAL_DIR / "bootstrap" / "bootstrap_metadata.json").read_text(encoding="utf-8"))
    for orig_str, spec in EXP_SPECS.items():
        expected_idx = np.random.default_rng(42).integers(0, spec["n_test"], size=(5000, spec["n_test"]))
        with np.load(EVAL_DIR / "bootstrap" / f"bootstrap_indices_{orig_str}.npz") as npz:
            saved_idx = npz["indices"]
        if saved_idx.shape != (5000, spec["n_test"]):
            c6_errs.append(f"{orig_str}_shape_{saved_idx.shape}")
        if not np.array_equal(saved_idx, expected_idx):
            c6_errs.append(f"{orig_str}_rng_mismatch")
        if int(saved_idx.min()) < 0 or int(saved_idx.max()) >= spec["n_test"]:
            c6_errs.append(f"{orig_str}_bounds")
        if boot_meta["experiments"][orig_str]["index_matrix_shape"] != [5000, spec["n_test"]]:
            c6_errs.append(f"{orig_str}_meta_shape")
        boot_matrices[orig_str] = saved_idx
    record(
        "C6_bootstrap_index_matrices_reproducibility",
        len(c6_errs) == 0,
        "Fresh default_rng(42) shapes (5000, 992) and (5000, 995) match saved .npz exactly"
        if not c6_errs
        else f"Errors: {c6_errs}",
    )

    # C7 & C8: Independent replicate-by-replicate bootstrap loop for MAE CIs and Paired Delta CIs.
    paired_diff_df = pd.read_csv(
        EVAL_DIR / "metrics" / "paired_mae_differences.csv", float_precision="round_trip"
    )
    paired_ci_df = pd.read_csv(
        EVAL_DIR / "metrics" / "paired_mae_bootstrap_ci.csv", float_precision="round_trip"
    )
    c7_max_diff = 0.0
    c8_max_diff = 0.0
    indep_mae_ci: dict[str, dict[str, tuple[float, float]]] = {}
    indep_paired: dict[str, dict[str, tuple[float, float, float]]] = {}

    for orig_str, spec in EXP_SPECS.items():
        idx_mat = boot_matrices[orig_str]
        n_rep = idx_mat.shape[0]
        boot_mae_arrs: dict[str, np.ndarray] = {}
        indep_mae_ci[orig_str] = {}
        indep_paired[orig_str] = {}

        for m in ("M0", "M1", "M2", "M3"):
            err_vec = indep_abs_errs[orig_str][m]
            draws = np.empty(n_rep, dtype=np.float64)
            for b in range(n_rep):
                draws[b] = float(np.mean(err_vec[idx_mat[b]]))
            boot_mae_arrs[m] = draws
            lo, hi = np.percentile(draws, [2.5, 97.5], method="linear")
            indep_mae_ci[orig_str][m] = (float(lo), float(hi))

            row_s = mae_summary_df[
                (mae_summary_df["test_origin"] == spec["origin"]) & (mae_summary_df["model"] == m)
            ].iloc[0]
            row_c = mae_ci_df[
                (mae_ci_df["test_origin"] == spec["origin"]) & (mae_ci_df["model"] == m)
            ].iloc[0]
            c7_max_diff = max(
                c7_max_diff,
                abs(float(lo) - float(row_s["ci_95_low"])),
                abs(float(hi) - float(row_s["ci_95_high"])),
                abs(float(np.mean(draws)) - float(row_c["boot_mean_mae"])),
                abs(float(np.std(draws, ddof=1)) - float(row_c["boot_sd_mae"])),
                abs(float(np.median(draws)) - float(row_c["boot_median_mae"])),
            )

        for comp_id, aug_m, ref_m in COMPARISONS:
            d_obs = indep_mae[orig_str][aug_m] - indep_mae[orig_str][ref_m]
            d_draws = boot_mae_arrs[aug_m] - boot_mae_arrs[ref_m]
            d_lo, d_hi = np.percentile(d_draws, [2.5, 97.5], method="linear")
            indep_paired[orig_str][comp_id] = (float(d_obs), float(d_lo), float(d_hi))

            r_d = paired_diff_df[
                (paired_diff_df["test_origin"] == spec["origin"])
                & (paired_diff_df["comparison_id"] == comp_id)
            ].iloc[0]
            r_c = paired_ci_df[
                (paired_ci_df["test_origin"] == spec["origin"])
                & (paired_ci_df["comparison_id"] == comp_id)
            ].iloc[0]
            c8_max_diff = max(
                c8_max_diff,
                abs(float(d_obs) - float(r_d["delta_mae_observed"])),
                abs(float(d_lo) - float(r_d["ci_95_low"])),
                abs(float(d_hi) - float(r_d["ci_95_high"])),
                abs(float(np.mean(d_draws)) - float(r_c["boot_mean_delta"])),
                abs(float(np.std(d_draws, ddof=1)) - float(r_c["boot_sd_delta"])),
                abs(float(np.median(d_draws)) - float(r_c["boot_median_delta"])),
            )

    record(
        "C7_independent_bootstrap_mae_ci",
        c7_max_diff <= 1e-12,
        f"Loop-recomputed B=5,000 MAE CIs (linear percentile) match CSVs; max_abs_diff={c7_max_diff:.3e}",
    )
    record(
        "C8_independent_paired_mae_differences_and_ci",
        len(paired_diff_df) == 8 and c8_max_diff <= 1e-12,
        f"All 8 paired Delta_MAE differences and 95% CIs match CSVs; max_abs_diff={c8_max_diff:.3e}",
    )

    # C9: Thesis tables match audited metrics (both CSV and LaTeX formatted values).
    t1_csv = pd.read_csv(
        EVAL_DIR / "thesis_assets" / "tables" / "table_5_1_rq2_mae_performance.csv",
        float_precision="round_trip",
    )
    t2_csv = pd.read_csv(
        EVAL_DIR / "thesis_assets" / "tables" / "table_5_2_rq2_paired_comparisons.csv",
        float_precision="round_trip",
    )
    t1_tex = (EVAL_DIR / "thesis_assets" / "tables" / "table_5_1_rq2_mae_performance.tex").read_text(
        encoding="utf-8"
    )
    t2_tex = (EVAL_DIR / "thesis_assets" / "tables" / "table_5_2_rq2_paired_comparisons.tex").read_text(
        encoding="utf-8"
    )
    c9_errs: list[str] = []
    for orig_str, spec in EXP_SPECS.items():
        for m in ("M0", "M1", "M2", "M3"):
            r = t1_csv[(t1_csv["Test Origin"] == spec["origin"]) & (t1_csv["Model"] == m)].iloc[0]
            mae_v = indep_mae[orig_str][m]
            lo_v, hi_v = indep_mae_ci[orig_str][m]
            if max(
                abs(float(r["Test MAE"]) - mae_v),
                abs(float(r["CI 95% Low"]) - lo_v),
                abs(float(r["CI 95% High"]) - hi_v),
            ) > 1e-12:
                c9_errs.append(f"t1_csv_{orig_str}_{m}")
            expected_tex_str = f"{mae_v:.4f} [{lo_v:.4f}, {hi_v:.4f}]"
            if expected_tex_str not in t1_tex:
                c9_errs.append(f"t1_tex_{orig_str}_{m}")
        for comp_id, aug_m, ref_m in COMPARISONS:
            label = f"{aug_m} vs {ref_m}"
            r = t2_csv[
                (t2_csv["Test Origin"] == spec["origin"]) & (t2_csv["Comparison"] == label)
            ].iloc[0]
            d_v, d_lo, d_hi = indep_paired[orig_str][comp_id]
            if max(
                abs(float(r["Observed Delta MAE"]) - d_v),
                abs(float(r["CI 95% Low"]) - d_lo),
                abs(float(r["CI 95% High"]) - d_hi),
            ) > 1e-12:
                c9_errs.append(f"t2_csv_{orig_str}_{comp_id}")
            expected_tex_str = f"{d_v:+.4f} [{d_lo:+.4f}, {d_hi:+.4f}]"
            if expected_tex_str not in t2_tex:
                c9_errs.append(f"t2_tex_{orig_str}_{comp_id}")
    record(
        "C9_thesis_tables_match_audited_metrics",
        len(c9_errs) == 0,
        "Table 5.1 & Table 5.2 CSVs (<=1e-12) and LaTeX formatted intervals match audited metrics 100%"
        if not c9_errs
        else f"Errors: {c9_errs}",
    )

    # C10: Thesis figures existence, non-empty formats, and SVG numeric content parity.
    c10_errs: list[str] = []
    fig_dir = EVAL_DIR / "thesis_assets" / "figures"
    for stem in ("fig_5_1_rq2_mae_comparison", "fig_5_2_rq2_paired_mae_differences"):
        for ext in (".pdf", ".svg", ".png"):
            fpath = fig_dir / f"{stem}{ext}"
            if not fpath.is_file() or fpath.stat().st_size == 0:
                c10_errs.append(f"missing_or_empty_{fpath.name}")
    svg1 = (fig_dir / "fig_5_1_rq2_mae_comparison.svg").read_text(encoding="utf-8")
    svg2 = (fig_dir / "fig_5_2_rq2_paired_mae_differences.svg").read_text(encoding="utf-8")
    for orig_str in ("2018", "2021"):
        for m in ("M0", "M1", "M2", "M3"):
            lbl = f"{indep_mae[orig_str][m]:.4f}"
            if lbl not in svg1:
                c10_errs.append(f"svg1_missing_{orig_str}_{m}_{lbl}")
        for comp_id, _, _ in COMPARISONS:
            d_v, d_lo, d_hi = indep_paired[orig_str][comp_id]
            lbl = f"{d_v:+.4f} [{d_lo:+.4f}, {d_hi:+.4f}]"
            if lbl not in svg2:
                c10_errs.append(f"svg2_missing_{orig_str}_{comp_id}")
    record(
        "C10_thesis_figures_formats_and_data_parity",
        len(c10_errs) == 0,
        "Figure 5.1 & Figure 5.2 (PDF/SVG/PNG) present and rendered SVG labels match audited values 100%"
        if not c10_errs
        else f"Errors: {c10_errs}",
    )

    # C11: Manifest SHA-256 hashes (outputs + source scripts) & zero machine absolute paths.
    c11_errs: list[str] = []
    for rel_key, meta in manifest["outputs"].items():
        fpath = EVAL_DIR / rel_key
        if not fpath.is_file() or sha256_file(fpath) != meta["sha256"]:
            c11_errs.append(f"hash_{rel_key}")
    src_scripts = manifest.get("source_scripts", {})
    expected_src = {"builder", "auditor", "thesis_assets_generator"}
    if set(src_scripts.keys()) != expected_src:
        c11_errs.append("missing_or_extra_source_scripts_keys")
    else:
        for role_key, meta in src_scripts.items():
            spath = REPO_ROOT / meta["relative_path"]
            if not spath.is_file() or sha256_file(spath) != meta["sha256"]:
                c11_errs.append(f"source_hash_{role_key}")
    for check_json in (manifest, boot_meta):
        abs_hits = scan_for_absolute_paths(check_json)
        if abs_hits:
            c11_errs.extend(abs_hits[:5])
    for csv_path in list((EVAL_DIR / "predictions").glob("*.csv")) + list(
        (EVAL_DIR / "metrics").glob("*.csv")
    ) + list((EVAL_DIR / "thesis_assets" / "tables").glob("*.csv")):
        raw = csv_path.read_text(encoding="utf-8")
        if re.search(r"[A-Za-z]:[/\\]", raw):
            c11_errs.append(f"abs_in_{csv_path.name}")
    record(
        "C11_manifest_sha256_and_zero_absolute_paths",
        len(c11_errs) == 0,
        f"All {len(manifest['outputs'])} output hashes & {len(src_scripts)} source script hashes verified; zero machine absolute paths"
        if not c11_errs
        else f"Errors: {c11_errs}",
    )

    # C12: Strict Stage 3.4 boundary check via AST and filesystem scan.
    c12_errs: list[str] = []
    forbidden_tokens = (
        "train_2018",
        "train_2021",
        "rq3_2018",
        "rq3_2021",
        "ln_rca",
        "ln_whole",
        "rca_whole",
        "m3_logrca",
        "m2_wc",
        "m3_wc",
        "top50",
        "hits50",
        "precision@50",
    )
    forbidden_names = {"Ridge", "StandardScaler", "GridSearchCV", "GroupKFold"}
    for script_path in (BUILDER_SCRIPT, ASSETS_SCRIPT):
        tree = ast.parse(script_path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id in forbidden_names:
                c12_errs.append(f"{script_path.name}_name_{node.id}")
            if isinstance(node, ast.Attribute) and node.attr in ("fit", "fit_transform", "best_score_"):
                c12_errs.append(f"{script_path.name}_attr_{node.attr}")
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                low = node.value.lower()
                for tok in forbidden_tokens:
                    if tok in low:
                        c12_errs.append(f"{script_path.name}_str_{tok}")
    stage3_root = REPO_ROOT / "stage3_modeling"
    for pat in ("*stage3_5*", "*stage3_6*", "*stage3_7*", "*top50*", "*hits50*", "*m3_logrca*", "*m2_wc*", "*m3_wc*"):
        for hit in stage3_root.rglob(pat):
            if hit.is_file():
                c12_errs.append(f"forbidden_file_{hit.name}")
    record(
        "C12_strict_stage3_4_boundary_no_refit_no_rq3_no_sens",
        len(c12_errs) == 0,
        "AST verified zero .fit()/tuning/scaler/train/RQ3/sensitivity refs; zero Stage 3.5+ files exist"
        if not c12_errs
        else f"Violations: {c12_errs}",
    )

    # C13: Clean temporary directory reproducibility verification.
    c13_errs: list[str] = []
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        subprocess.run(
            [
                sys.executable,
                "-B",
                str(BUILDER_SCRIPT),
                "--out-dir",
                str(tmp_path),
                "--timestamp-utc",
                manifest["execution_timestamp_utc"],
            ],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            check=True,
        )
        deterministic_rels = [
            "predictions/predictions_test_2018.csv",
            "predictions/predictions_test_2021.csv",
            "metrics/mae_summary.csv",
            "metrics/mae_bootstrap_ci.csv",
            "metrics/paired_mae_differences.csv",
            "metrics/paired_mae_bootstrap_ci.csv",
            "bootstrap/bootstrap_indices_2018.npz",
            "bootstrap/bootstrap_indices_2021.npz",
            "thesis_assets/tables/table_5_1_rq2_mae_performance.csv",
            "thesis_assets/tables/table_5_1_rq2_mae_performance.tex",
            "thesis_assets/tables/table_5_2_rq2_paired_comparisons.csv",
            "thesis_assets/tables/table_5_2_rq2_paired_comparisons.tex",
            "thesis_assets/figures/fig_5_1_rq2_mae_comparison.svg",
            "thesis_assets/figures/fig_5_1_rq2_mae_comparison.png",
            "thesis_assets/figures/fig_5_2_rq2_paired_mae_differences.svg",
            "thesis_assets/figures/fig_5_2_rq2_paired_mae_differences.png",
            "thesis_assets/README.md",
        ]
        for rel in deterministic_rels:
            if sha256_file(tmp_path / rel) != sha256_file(EVAL_DIR / rel):
                c13_errs.append(f"nondet_{rel}")
        for stem in ("fig_5_1_rq2_mae_comparison", "fig_5_2_rq2_paired_mae_differences"):
            pdf_tmp = tmp_path / "thesis_assets" / "figures" / f"{stem}.pdf"
            if not pdf_tmp.is_file() or pdf_tmp.stat().st_size == 0:
                c13_errs.append(f"missing_tmp_{stem}.pdf")
    record(
        "C13_clean_tempdir_reproducibility",
        len(c13_errs) == 0,
        f"Clean tempdir rerun produced byte-identical SHA-256 across all {len(deterministic_rels)} CSV/.npz/.tex/SVG/PNG artifacts"
        if not c13_errs
        else f"Diffs: {c13_errs}",
    )

    # C14: Post-audit upstream immutability check.
    c14_errs: list[str] = []
    if sha256_file(STAGE3_1_CSV) != EXPECTED_UPSTREAM_SHAS["stage3_1_csv"]:
        c14_errs.append("stage3_1")
    if sha256_file(STAGE2_PANEL_CSV) != EXPECTED_UPSTREAM_SHAS["stage2_panel"]:
        c14_errs.append("stage2_panel")
    if sha256_file(STAGE2_DENOM_CSV) != EXPECTED_UPSTREAM_SHAS["stage2_denom"]:
        c14_errs.append("stage2_denom")
    for fname, meta in s32_manifest["outputs"].items():
        if sha256_file(SPLITS_DIR / fname) != meta["sha256"]:
            c14_errs.append(f"s32_{fname}")
    for rel_key, meta in s33_manifest["outputs"].items():
        if sha256_file(STAGE3_3_DIR / rel_key) != meta["sha256"]:
            c14_errs.append(f"s33_{rel_key}")
    record(
        "C14_post_audit_upstream_immutability",
        len(c14_errs) == 0,
        "Stage 2, Stage 3.1, all 12 Stage 3.2 splits, and all 15 Stage 3.3 artifacts remain byte-identical"
        if not c14_errs
        else f"Changed: {c14_errs}",
    )

    passed = sum(1 for _, st, _ in checks if st == "PASS")
    total = len(checks)
    overall = "PASS" if passed == total else "FAIL"

    # Write stage3_4_audit_report.md cleanly.
    lines = [
        "# Stage 3.4 Independent Audit Report — RQ2 Held-Out Test Evaluation (M0–M3)",
        "",
        f"**Overall Verdict:** **{overall} ({passed}/{total} checks passed)**",
        f"**Audited Git HEAD:** `{manifest['git_commit_hash']}`",
        f"**Execution Timestamp (UTC):** `{manifest['execution_timestamp_utc']}`",
        "",
        "## 1. Held-Out RQ2 Forecasting Accuracy (Test MAE & 95% Conditional Bootstrap CI)",
        "| Experiment (Origin) | Model | $p$ | Tuned $\\alpha$ | $N_{\\text{test}}$ | Test MAE | 95% Bootstrap CI (`linear`) |",
        "| --- | :---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for orig_str, spec in EXP_SPECS.items():
        exp_lbl = "Experiment A (`2018`)" if orig_str == "2018" else "Experiment B (`2021`)"
        for m in ("M0", "M1", "M2", "M3"):
            m_info = manifest["experiments"][orig_str]["models"][m]
            alpha_s = "Unfitted" if m == "M0" else f"`{m_info['selected_alpha']:.6g}`"
            lines.append(
                f"| {exp_lbl} | `{m}` | {m_info['n_features']} | {alpha_s} | {spec['n_test']} | "
                f"{m_info['mae']:.6f} | `[{m_info['ci_95_low']:.6f}, {m_info['ci_95_high']:.6f}]` |"
            )

    lines.extend(
        [
            "",
            "## 2. Prespecified Paired MAE Comparisons ($\\Delta\\text{MAE} = \\text{MAE}_{\\text{aug}} - \\text{MAE}_{\\text{ref}}$)",
            "| Test Origin | Comparison | Observed $\\Delta\\text{MAE}$ | 95% Paired Bootstrap CI | Excludes 0? | Interpretation |",
            "| :---: | --- | ---: | --- | :---: | --- |",
        ]
    )
    for orig_str in ("2018", "2021"):
        for comp_id, aug_m, ref_m in COMPARISONS:
            c_info = manifest["experiments"][orig_str]["paired_comparisons"][comp_id]
            lines.append(
                f"| `{orig_str}` | `{aug_m} vs {ref_m}` | `{c_info['delta_mae_observed']:+.6f}` | "
                f"`[{c_info['ci_95_low']:+.6f}, {c_info['ci_95_high']:+.6f}]` | "
                f"`{c_info['ci_95_excludes_zero']}` | {c_info['direction_interpretation']} |"
            )

    lines.extend(
        [
            "",
            "## 3. Check-by-Check Audit Results",
            "| Check ID | Status | Supporting Evidence |",
            "| --- | :---: | --- |",
        ]
    )
    for cname, st, detail in checks:
        lines.append(f"| `{cname}` | **{st}** | {detail} |")

    lines.extend(
        [
            "",
            "## 4. Stage 3.4 Artifact Inventory & SHA-256 Hashes",
            "| Artifact | Role | SHA-256 |",
            "| --- | --- | --- |",
        ]
    )
    for rel_key, meta in manifest["outputs"].items():
        lines.append(f"| `{meta['relative_path']}` | `{meta['role']}` | `{meta['sha256']}` |")
    lines.append("")

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8", newline="\n")

    for cname, st, detail in checks:
        print(f"[{st}] {cname}: {detail}")
    print(f"\nStage 3.4 Audit Result: {overall} ({passed}/{total} passed)")
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
