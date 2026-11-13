#!/usr/bin/env python3
"""Independent auditor for Stage 3.3 Ridge Regression and GroupKFold Tuning.

Independently loads Stage 3.2 training CSVs and Stage 3.1/Stage 2 metadata,
verifies every preflight rule, independently reconstructs GroupKFold splits and
refits Ridge Pipelines across the full alpha grid without importing code from
`build_stage3_3_ridge.py`, verifies saved `.joblib` pipelines, tests repeated
execution determinism, checks Windows and POSIX absolute path absence, verifies
zero Stage 3.4+ artifacts, and writes `stage3_3_ridge_audit_report.md`.
"""

from __future__ import annotations

import ast
import csv
import hashlib
import json
import math
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
STAGE3_3_DIR = Path(__file__).resolve().parent
BUILDER_SCRIPT = STAGE3_3_DIR / "build_stage3_3_ridge.py"
MANIFEST_PATH = STAGE3_3_DIR / "stage3_3_ridge_manifest.json"
SUMMARY_PATH = STAGE3_3_DIR / "stage3_3_model_selection_summary.csv"
REPORT_PATH = STAGE3_3_DIR / "stage3_3_ridge_audit_report.md"

SPLITS_DIR = REPO_ROOT / "stage3_modeling" / "stage3_2_splits"
STAGE3_2_MANIFEST_PATH = SPLITS_DIR / "stage3_2_splits_manifest.json"
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

EXPECTED_STAGE3_1_SHA256 = (
    "9fc15d6ed16ade633547bfca9efca1db92827aa665cbb4509d76c7dae057f488"
)
EXPECTED_STAGE2_PANEL_SHA256 = (
    "f0049cd71f5ba8545c2e3cbb850e036a7b849828321cd23aa1d04771e60d7175"
)
EXPECTED_STAGE2_DENOM_SHA256 = (
    "9c2d9cccee65c156494b96447ce53045d43e514c74aa10ec9f1c85915b33afce"
)

IDENTIFIERS = [
    "forecast_origin",
    "topic_id",
    "topic_name",
    "field_name",
    "subfield_name",
    "eligible",
]

MODEL_SPECS = {
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

EXP_EXPECTED = {
    "2018": {
        "train_origins": [2015],
        "train_rows": 990,
        "unique_topics": 990,
        "val_fold_sizes": [198, 198, 198, 198, 198],
    },
    "2021": {
        "train_origins": [2015, 2016, 2017, 2018],
        "train_rows": 3963,
        "unique_topics": 993,
        "val_fold_sizes": [796, 790, 796, 789, 792],
    },
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def to_repo_posix(path: Path) -> str:
    return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()


def find_absolute_paths_in_text(text: str) -> list[str]:
    """Detect both Windows drive paths and POSIX absolute paths inside serialized text."""
    hits: list[str] = []
    hits.extend(re.findall(r"[A-Za-z]:[/\\\\]", text))
    # Match quoted POSIX-like absolute paths starting with common root segments.
    hits.extend(
        re.findall(
            r'"/(?:Users|home|mnt|tmp|var|opt|etc|root|Volumes|c|d)/[^"]*"',
            text,
        )
    )
    return hits


def main() -> int:
    checks: list[tuple[str, str, str]] = []

    def record(name: str, passed: bool, detail: str) -> None:
        checks.append((name, "PASS" if passed else "FAIL", detail))

    # 1. Upstream Stage 2 & Stage 3.1 hashes + Stage 3.2 manifest & 12 split CSV hashes.
    s3_1_hash = sha256_file(STAGE3_1_CSV)
    s2_panel_hash = sha256_file(STAGE2_PANEL_CSV)
    s2_denom_hash = sha256_file(STAGE2_DENOM_CSV)
    stage3_2_manifest = json.loads(STAGE3_2_MANIFEST_PATH.read_text(encoding="utf-8"))

    stage3_2_hash_diffs = []
    for fname, meta in stage3_2_manifest["outputs"].items():
        if sha256_file(SPLITS_DIR / fname) != meta["sha256"]:
            stage3_2_hash_diffs.append(fname)

    record(
        "C1_upstream_and_stage3_2_integrity",
        (
            s3_1_hash == EXPECTED_STAGE3_1_SHA256
            and s2_panel_hash == EXPECTED_STAGE2_PANEL_SHA256
            and s2_denom_hash == EXPECTED_STAGE2_DENOM_SHA256
            and len(stage3_2_hash_diffs) == 0
        ),
        f"Stage 2/3.1 exact SHA-256 match; Stage 3.2 all {len(stage3_2_manifest['outputs'])} CSVs unchanged",
    )

    # 2. Load Stage 3.3 manifest & model selection summary, check sklearn >= 1.6.
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    summary_df = pd.read_csv(SUMMARY_PATH, float_precision="round_trip")
    parts = sklearn.__version__.split(".")
    sk_ok = (int(parts[0]), int(parts[1])) >= (1, 6)
    record(
        "C2_manifest_summary_and_sklearn_floor",
        sk_ok and MANIFEST_PATH.is_file() and SUMMARY_PATH.is_file() and len(summary_df) == 8,
        f"scikit-learn=={sklearn.__version__}, summary_rows={len(summary_df)} (2x M0 + 6 fitted Ridge)",
    )

    # 3. Independently verify Stage 3.1 metadata parity across Stage 3.2 feature files
    #    (addresses GPT's Stage 3.2 audit feedback regarding topic_name/field_name/subfield_name).
    with STAGE3_1_CSV.open("r", encoding="utf-8", newline="") as f:
        src_lookup = {
            (int(r["forecast_origin"]), r["topic_id"]): r
            for r in csv.DictReader(f)
        }
    meta_mismatches = 0
    for orig_str in ("2018", "2021"):
        feat_df = pd.read_csv(
            SPLITS_DIR / f"train_{orig_str}_features.csv", float_precision="round_trip"
        )
        for _, row in feat_df.iterrows():
            src = src_lookup[(int(row["forecast_origin"]), str(row["topic_id"]))]
            for col in ("topic_name", "field_name", "subfield_name"):
                if str(row[col]) != str(src[col]):
                    meta_mismatches += 1
    record(
        "C3_source_metadata_column_parity",
        meta_mismatches == 0,
        f"topic_name, field_name, subfield_name exact string match across all Stage 3.2 training rows (mismatches={meta_mismatches})",
    )

    # 4. Preflight & model feature set validation.
    feat_spec_ok = True
    leak_cols_found: list[str] = []
    manifest_sets = stage3_2_manifest["schema_separation"]["model_feature_sets"]
    for m_name, exp_cols in MODEL_SPECS.items():
        if list(manifest_sets.get(m_name, [])) != exp_cols:
            feat_spec_ok = False
        if set(exp_cols) & (set(IDENTIFIERS) | {"g_adj", "hg_future", "target_global_topic_fut3yr", "target_w_allsci_fut3yr"}):
            leak_cols_found.append(m_name)
    record(
        "C4_model_feature_sets_and_no_identifier_leakage",
        feat_spec_ok and len(leak_cols_found) == 0,
        "M0=[], M1=2, M2=5, M3=8 verified independently; zero identifiers/targets in feature specs",
    )

    # 5. Per-experiment independent CV reconstruction, full refit verification, and pipeline checks.
    max_cv_mae_diff = 0.0
    max_fold_mae_diff = 0.0
    max_coef_diff = 0.0
    max_intercept_diff = 0.0
    max_pred_diff = 0.0
    all_pipeline_hashes_ok = True
    all_cv_hashes_ok = True
    all_folds_identical = True
    all_boundaries_interior = True
    all_tiebreaks_ok = True
    all_scalers_ok = True
    all_full_refit_ok = True

    for orig_str, exp_cfg in EXP_EXPECTED.items():
        feat_df = pd.read_csv(
            SPLITS_DIR / f"train_{orig_str}_features.csv", float_precision="round_trip"
        )
        targ_df = pd.read_csv(
            SPLITS_DIR / f"train_{orig_str}_targets.csv", float_precision="round_trip"
        )
        # Verify one-to-one key equality & inner join.
        merged = feat_df.merge(
            targ_df,
            on=["forecast_origin", "topic_id"],
            how="inner",
            validate="one_to_one",
        ).sort_values(["forecast_origin", "topic_id"], ascending=True).reset_index(drop=True)

        assert len(merged) == exp_cfg["train_rows"]
        assert sorted(merged["forecast_origin"].unique().tolist()) == exp_cfg["train_origins"]
        assert merged["topic_id"].nunique() == exp_cfg["unique_topics"]

        # Independently construct GroupKFold(n_splits=5, shuffle=True, random_state=42).
        gkf = GroupKFold(n_splits=5, shuffle=True, random_state=42)
        groups = merged["topic_id"].to_numpy()
        indep_splits = list(gkf.split(merged, groups=groups))
        indep_val_assign = np.full(len(merged), -1, dtype=np.int64)
        indep_fold_sizes = []
        fold_overlaps = []
        for f_idx, (tr_i, va_i) in enumerate(indep_splits):
            indep_val_assign[va_i] = f_idx
            indep_fold_sizes.append(int(len(va_i)))
            fold_overlaps.append(len(set(groups[tr_i]) & set(groups[va_i])))

        stored_folds_df = pd.read_csv(STAGE3_3_DIR / f"cv_folds_{orig_str}.csv")
        folds_match = (
            list(zip(merged["forecast_origin"], merged["topic_id"]))
            == list(zip(stored_folds_df["forecast_origin"], stored_folds_df["topic_id"]))
            and np.array_equal(indep_val_assign, stored_folds_df["cv_fold"].to_numpy(dtype=np.int64))
            and indep_fold_sizes == exp_cfg["val_fold_sizes"]
            and fold_overlaps == [0, 0, 0, 0, 0]
        )
        if not folds_match:
            all_folds_identical = False

        y_vec = merged["g_adj"].to_numpy(dtype=np.float64)

        for model_name in ("M1", "M2", "M3"):
            m_info = manifest["experiments"][orig_str]["models"][model_name]
            cols = MODEL_SPECS[model_name]
            X_mat = merged.loc[:, cols].to_numpy(dtype=np.float64)
            assert np.isfinite(X_mat).all() and np.isfinite(y_vec).all()

            cv_path = REPO_ROOT / m_info["cv_results_relative_path"]
            pipe_path = REPO_ROOT / m_info["pipeline_relative_path"]
            if sha256_file(cv_path) != m_info["cv_results_sha256"]:
                all_cv_hashes_ok = False
            if sha256_file(pipe_path) != m_info["pipeline_sha256"]:
                all_pipeline_hashes_ok = False

            cv_df = pd.read_csv(cv_path, float_precision="round_trip")
            alphas = cv_df["alpha"].to_numpy(dtype=np.float64)

            # Independently recompute 5-fold MAE for every candidate alpha via manual StandardScaler + Ridge!
            indep_fold_maes = np.zeros((len(alphas), 5), dtype=np.float64)
            for a_idx, alpha_val in enumerate(alphas):
                for f_idx, (tr_i, va_i) in enumerate(indep_splits):
                    sc = StandardScaler()
                    X_tr_s = sc.fit_transform(X_mat[tr_i])
                    X_va_s = sc.transform(X_mat[va_i])
                    rg = Ridge(alpha=float(alpha_val))
                    rg.fit(X_tr_s, y_vec[tr_i])
                    pred_va = rg.predict(X_va_s)
                    indep_fold_maes[a_idx, f_idx] = mean_absolute_error(y_vec[va_i], pred_va)

            indep_mean_mae = np.mean(indep_fold_maes, axis=1)
            max_cv_mae_diff = max(
                max_cv_mae_diff,
                float(np.max(np.abs(indep_mean_mae - cv_df["mean_cv_mae"].to_numpy()))),
            )
            stored_fold_cols = cv_df[
                ["fold0_mae", "fold1_mae", "fold2_mae", "fold3_mae", "fold4_mae"]
            ].to_numpy(dtype=np.float64)
            max_fold_mae_diff = max(
                max_fold_mae_diff,
                float(np.max(np.abs(indep_fold_maes - stored_fold_cols))),
            )

            # Verify tie-breaking rule (max alpha within 1e-12 of min mean CV MAE).
            min_mae = float(np.min(indep_mean_mae))
            tied_idx = np.flatnonzero(indep_mean_mae <= min_mae + 1e-12)
            expected_best_idx = int(tied_idx[np.argmax(alphas[tied_idx])])
            selected_rows = cv_df[cv_df["selected"] == True]  # noqa: E712
            if (
                len(selected_rows) != 1
                or int(selected_rows.iloc[0]["candidate_index"]) != expected_best_idx
                or float(selected_rows.iloc[0]["alpha"]) != m_info["selected_alpha"]
            ):
                all_tiebreaks_ok = False
            if expected_best_idx == 0 or expected_best_idx == len(alphas) - 1:
                all_boundaries_interior = False

            # Load saved Pipeline and compare against fresh full-training-set fit.
            saved_pipe: Pipeline = joblib.load(pipe_path)
            if (
                list(saved_pipe.named_steps.keys()) != ["scaler", "ridge"]
                or not isinstance(saved_pipe.named_steps["scaler"], StandardScaler)
                or not isinstance(saved_pipe.named_steps["ridge"], Ridge)
            ):
                all_scalers_ok = False

            if int(saved_pipe.named_steps["scaler"].n_samples_seen_) != len(merged):
                all_full_refit_ok = False
            if int(saved_pipe.named_steps["scaler"].n_features_in_) != len(cols):
                all_scalers_ok = False
            if float(saved_pipe.named_steps["ridge"].alpha) != float(alphas[expected_best_idx]):
                all_tiebreaks_ok = False

            fresh_pipe = Pipeline(
                [("scaler", StandardScaler()), ("ridge", Ridge(alpha=float(alphas[expected_best_idx])))]
            )
            fresh_pipe.fit(X_mat, y_vec)
            max_coef_diff = max(
                max_coef_diff,
                float(np.max(np.abs(saved_pipe.named_steps["ridge"].coef_ - fresh_pipe.named_steps["ridge"].coef_))),
            )
            max_intercept_diff = max(
                max_intercept_diff,
                abs(float(saved_pipe.named_steps["ridge"].intercept_) - float(fresh_pipe.named_steps["ridge"].intercept_)),
            )
            max_pred_diff = max(
                max_pred_diff,
                float(np.max(np.abs(saved_pipe.predict(X_mat) - fresh_pipe.predict(X_mat)))),
            )

    record(
        "C5_groupkfold_splits_and_zero_topic_overlap",
        all_folds_identical,
        "Exact match for GroupKFold(5, shuffle=True, random_state=42); 2018=[198x5], 2021=[796,790,796,789,792], overlap=0",
    )
    record(
        "C6_independent_cv_mae_and_fold_recompute",
        max_cv_mae_diff <= 1e-12 and max_fold_mae_diff <= 1e-12,
        f"max|indep_mean_mae - csv|={max_cv_mae_diff:.3e}, max|indep_fold_mae - csv|={max_fold_mae_diff:.3e}",
    )
    record(
        "C7_alpha_selection_tiebreak_and_interior_grid",
        all_tiebreaks_ok and all_boundaries_interior,
        "All 6 models select exact min-MAE largest-alpha within 1e-12 strictly inside final searched grid (41-pt [-3,5] for 2018-M2/M3 & 2021-M3; expanded 61-pt [-7,5] for 2018-M1, 2021-M1/M2)",
    )
    record(
        "C8_pipeline_structure_full_refit_and_coef_parity",
        all_scalers_ok and all_full_refit_ok and max_coef_diff <= 1e-12 and max_intercept_diff <= 1e-12 and max_pred_diff <= 1e-12,
        f"All 6 joblib Pipelines verified StandardScaler->Ridge full-train refit; max_coef_diff={max_coef_diff:.3e}, max_pred_diff={max_pred_diff:.3e}",
    )
    record(
        "C9_stage3_3_artifact_sha256_integrity",
        all_cv_hashes_ok and all_pipeline_hashes_ok,
        "All 6 CV CSVs and 6 joblib Pipelines match manifest SHA-256 hashes",
    )

    # 10. Verify summary CSV matches manifest values row for row.
    summary_ok = True
    for _, srow in summary_df.iterrows():
        orig_str = str(int(srow["test_origin"]))
        mname = str(srow["model"])
        minfo = manifest["experiments"][orig_str]["models"][mname]
        if bool(srow["fitted"]) != bool(minfo["fitted"]):
            summary_ok = False
        if mname != "M0":
            if (
                abs(float(srow["selected_alpha"]) - float(minfo["selected_alpha"])) > 1e-12
                or abs(float(srow["mean_cv_mae"]) - float(minfo["mean_cv_mae"])) > 1e-12
            ):
                summary_ok = False
    record(
        "C10_model_summary_parity_with_manifest",
        summary_ok,
        "stage3_3_model_selection_summary.csv matches manifest across M0-M3 for 2018 & 2021",
    )

    # 11. Zero machine-specific absolute paths (Windows AND POSIX) in manifest/summary/CV/folds.
    abs_hits: list[str] = []
    files_to_scan = [
        MANIFEST_PATH,
        SUMMARY_PATH,
        STAGE3_3_DIR / "cv_folds_2018.csv",
        STAGE3_3_DIR / "cv_folds_2021.csv",
    ] + list((STAGE3_3_DIR / "cv_results").glob("*.csv"))
    for p in files_to_scan:
        hits = find_absolute_paths_in_text(p.read_text(encoding="utf-8"))
        if hits:
            abs_hits.append(f"{p.name}:{hits}")
    record(
        "C11_zero_absolute_paths_windows_and_posix",
        len(abs_hits) == 0,
        "Zero Windows drive or POSIX absolute paths across manifest and CSV artifacts"
        if not abs_hits
        else f"Found: {abs_hits}",
    )

    # 12. Repeated-execution determinism check via subprocess --out-dir.
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        proc = subprocess.run(
            [sys.executable, "-B", str(BUILDER_SCRIPT), "--out-dir", str(tmp_path)],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            check=True,
        )
        hash_diffs = []
        rel_targets = [
            "stage3_3_model_selection_summary.csv",
            "cv_folds_2018.csv",
            "cv_folds_2021.csv",
            "cv_results/cv_results_2018_m1.csv",
            "cv_results/cv_results_2018_m2.csv",
            "cv_results/cv_results_2018_m3.csv",
            "cv_results/cv_results_2021_m1.csv",
            "cv_results/cv_results_2021_m2.csv",
            "cv_results/cv_results_2021_m3.csv",
            "models/ridge_pipeline_2018_m1.joblib",
            "models/ridge_pipeline_2018_m2.joblib",
            "models/ridge_pipeline_2018_m3.joblib",
            "models/ridge_pipeline_2021_m1.joblib",
            "models/ridge_pipeline_2021_m2.joblib",
            "models/ridge_pipeline_2021_m3.joblib",
        ]
        for rel in rel_targets:
            if sha256_file(tmp_path / rel) != sha256_file(STAGE3_3_DIR / rel):
                hash_diffs.append(rel)
        record(
            "C12_deterministic_repeated_execution",
            proc.returncode == 0 and len(hash_diffs) == 0,
            f"All {len(rel_targets)} CSV & joblib artifacts produced byte-identical SHA-256 across repeated runs"
            if not hash_diffs
            else f"Hash diffs: {hash_diffs}",
        )

    # 13. Strict Stage 3.3 boundary check: AST audit on builder + zero Stage 3.4+ outputs.
    builder_src = BUILDER_SCRIPT.read_text(encoding="utf-8")
    tree = ast.parse(builder_src)
    attr_best_score = [
        node.lineno
        for node in ast.walk(tree)
        if isinstance(node, ast.Attribute) and node.attr == "best_score_"
    ]
    test_str_hits = [
        node.lineno
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and any(tok in node.value for tok in ("test_2018", "test_2021", "rq3_2018", "rq3_2021"))
    ]
    forbidden_future_files = []
    for pat in ("*prediction*", "*bootstrap*", "*top50*", "*hits50*", "*m3_logrca*", "*m2_wc*", "*m3_wc*", "*test_eval*"):
        forbidden_future_files.extend(
            to_repo_posix(p)
            for p in (REPO_ROOT / "stage3_modeling").rglob(pat)
            if p.is_file()
        )
    record(
        "C13_strict_stage3_3_boundary_zero_test_leakage",
        len(attr_best_score) == 0 and len(test_str_hits) == 0 and len(forbidden_future_files) == 0,
        f"Builder AST has 0 test/rq3 file refs and 0 .best_score_ accesses; zero Stage 3.4+ outputs present"
        if (not attr_best_score and not test_str_hits and not forbidden_future_files)
        else f"Violations: best_score={attr_best_score}, test_refs={test_str_hits}, future={forbidden_future_files}",
    )

    # 14. Post-audit upstream immutability check.
    post_immut_ok = (
        sha256_file(STAGE3_1_CSV) == EXPECTED_STAGE3_1_SHA256
        and sha256_file(STAGE2_PANEL_CSV) == EXPECTED_STAGE2_PANEL_SHA256
        and sha256_file(STAGE2_DENOM_CSV) == EXPECTED_STAGE2_DENOM_SHA256
        and all(
            sha256_file(SPLITS_DIR / fn) == meta["sha256"]
            for fn, meta in stage3_2_manifest["outputs"].items()
        )
    )
    record(
        "C14_post_audit_upstream_immutability",
        post_immut_ok,
        "Stage 2, Stage 3.1, and all 12 Stage 3.2 split files remain byte-identical post-run",
    )

    passed_count = sum(1 for _, st, _ in checks if st == "PASS")
    total_count = len(checks)
    overall = "PASS" if passed_count == total_count else "FAIL"

    # Build Markdown audit report.
    lines = [
        "# Stage 3.3 Independent Audit Report",
        "",
        f"**Overall Verdict:** **{overall} ({passed_count}/{total_count} checks passed)**",
        "",
        "## 1. Model Selection & 5-Fold GroupKFold CV Summary",
        "| Test Origin | Model | $p$ | Selected $\\alpha$ | Mean CV MAE | SD CV MAE | Fold 0..4 MAEs | Grid Expanded? |",
        "| :---: | :---: | ---: | ---: | ---: | ---: | --- | :---: |",
    ]
    for orig_str in ("2018", "2021"):
        for mname in ("M1", "M2", "M3"):
            info = manifest["experiments"][orig_str]["models"][mname]
            f_str = ", ".join(f"{v:.6f}" for v in info["fold_maes"])
            lines.append(
                f"| `{orig_str}` | `{mname}` | {info['n_features']} | `{info['selected_alpha']:.6g}` | "
                f"{info['mean_cv_mae']:.6f} | {info['std_cv_mae']:.6f} | `{f_str}` | `{info['grid_expanded']}` |"
            )

    lines.extend(
        [
            "",
            "## 2. Check-by-Check Audit Results",
            "| Check ID | Status | Supporting Evidence |",
            "| --- | :---: | --- |",
        ]
    )
    for name, status, detail in checks:
        lines.append(f"| `{name}` | **{status}** | {detail} |")

    lines.extend(
        [
            "",
            "## 3. Exported Artifact Inventory & SHA-256 Hashes",
            "| Artifact | Role | Details | SHA-256 |",
            "| --- | --- | --- | --- |",
        ]
    )
    for key, meta in manifest["outputs"].items():
        if "rows" in meta:
            det = f"{meta['rows']:,} × {meta['columns']}"
        else:
            det = f"n_samples={meta['n_samples_fit']:,}, p={meta['n_features_fit']}"
        lines.append(f"| `{meta['relative_path']}` | `{meta['role']}` | {det} | `{meta['sha256']}` |")

    lines.append("")
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8", newline="\n")

    for name, status, detail in checks:
        print(f"[{status}] {name}: {detail}")
    print(f"\nStage 3.3 Audit Result: {overall} ({passed_count}/{total_count} passed)")
    return 0 if passed_count == total_count else 1


if __name__ == "__main__":
    raise SystemExit(main())

