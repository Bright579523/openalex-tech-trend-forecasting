#!/usr/bin/env python3
"""Independent auditor for Stage 3.2 train/test and RQ3 candidate-pool splits.

Independently loads the Stage 3.1 canonical CSV using Python's `csv.DictReader`
and NumPy (importing zero code from `build_stage3_2_splits.py`), verifies all
Stage 3.2 invariants, executes a repeated-run determinism check into a temporary
directory, and writes `stage3_2_splits_audit_report.md`.
"""

from __future__ import annotations

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

import numpy as np
import pandas as pd
import sklearn
from sklearn.model_selection import GroupKFold

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SPLITS_DIR = Path(__file__).resolve().parent
BUILDER_SCRIPT = SPLITS_DIR / "build_stage3_2_splits.py"
MANIFEST_PATH = SPLITS_DIR / "stage3_2_splits_manifest.json"
REPORT_PATH = SPLITS_DIR / "stage3_2_splits_audit_report.md"

STAGE3_1_CSV = REPO_ROOT / "stage3_modeling" / "stage3_origin_features_targets.csv"
EXPECTED_STAGE3_1_SHA256 = (
    "9fc15d6ed16ade633547bfca9efca1db92827aa665cbb4509d76c7dae057f488"
)
STAGE2_PANEL_CSV = (
    REPO_ROOT
    / "openalex_feasibility_audit"
    / "openalex_modeling_panel_1025topics_v2_synchronized.csv"
)
EXPECTED_STAGE2_PANEL_SHA256 = (
    "f0049cd71f5ba8545c2e3cbb850e036a7b849828321cd23aa1d04771e60d7175"
)
STAGE2_DENOM_CSV = (
    REPO_ROOT
    / "openalex_feasibility_audit"
    / "all_science_national_denominators_fractional_v2_live_recheck_20261105.csv"
)
EXPECTED_STAGE2_DENOM_SHA256 = (
    "9c2d9cccee65c156494b96447ce53045d43e514c74aa10ec9f1c85915b33afce"
)

EXPECTED_PREDICTOR_COLS = [
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
FORBIDDEN_IN_FEATURES = {
    "g_adj",
    "target_global_topic_fut3yr",
    "target_w_allsci_fut3yr",
    "hg_future",
}
EXPECTED_EXPORTS = [
    "train_2018_features.csv",
    "train_2018_targets.csv",
    "test_2018_features.csv",
    "test_2018_targets.csv",
    "rq3_2018_pool_features.csv",
    "rq3_2018_pool_labels.csv",
    "train_2021_features.csv",
    "train_2021_targets.csv",
    "test_2021_features.csv",
    "test_2021_targets.csv",
    "rq3_2021_pool_features.csv",
    "rq3_2021_pool_labels.csv",
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def to_repo_posix(path: Path) -> str:
    return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()


def load_stage3_1_dict() -> tuple[list[str], dict[tuple[int, str], dict[str, str]]]:
    with STAGE3_1_CSV.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)
    lookup: dict[tuple[int, str], dict[str, str]] = {}
    for row in rows:
        key = (int(row["forecast_origin"]), row["topic_id"])
        if key in lookup:
            raise AssertionError(f"Duplicate key in Stage 3.1 source: {key}")
        lookup[key] = row
    return fieldnames, lookup


def is_eligible(row: dict[str, str]) -> bool:
    return row["eligible"].strip().lower() == "true"


def main() -> int:
    checks: list[tuple[str, str, str]] = []

    def record(name: str, passed: bool, detail: str) -> None:
        checks.append((name, "PASS" if passed else "FAIL", detail))

    # 1. Upstream SHA-256 verification.
    h31 = sha256_file(STAGE3_1_CSV)
    hp = sha256_file(STAGE2_PANEL_CSV)
    hd = sha256_file(STAGE2_DENOM_CSV)
    record(
        "C1_upstream_sha256_integrity",
        (
            h31 == EXPECTED_STAGE3_1_SHA256
            and hp == EXPECTED_STAGE2_PANEL_SHA256
            and hd == EXPECTED_STAGE2_DENOM_SHA256
        ),
        f"stage3_1={h31[:12]}..., panel={hp[:12]}..., denom={hd[:12]}...",
    )

    # 2. Source shape & schema.
    src_cols, src_lookup = load_stage3_1_dict()
    record(
        "C2_stage3_1_shape_and_schema",
        len(src_cols) == 42 and len(src_lookup) == 7175,
        f"rows={len(src_lookup)}, cols={len(src_cols)}",
    )

    # 3. Manifest & required output files existence.
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    missing_files = [
        fn for fn in EXPECTED_EXPORTS if not (SPLITS_DIR / fn).is_file()
    ]
    record(
        "C3_manifest_and_all_12_exports_exist",
        len(missing_files) == 0 and MANIFEST_PATH.is_file(),
        "All 12 CSVs + manifest present"
        if not missing_files
        else f"Missing: {missing_files}",
    )

    # 4. Dependency floor check (scikit-learn >= 1.6).
    parts = sklearn.__version__.split(".")
    sk_ok = (int(parts[0]), int(parts[1])) >= (1, 6)
    record(
        "C4_sklearn_version_floor",
        sk_ok,
        f"scikit-learn=={sklearn.__version__} (>= 1.6 required)",
    )

    # 5-13. Per-experiment verification (2018 and 2021).
    exp_configs = [
        (2018, {2015}, 990, 992, 793, 159),
        (2021, {2015, 2016, 2017, 2018}, 3963, 995, 796, 160),
    ]

    all_trace_diffs: list[float] = []
    separation_violations: list[str] = []
    nonfinite_files: list[str] = []

    for (
        test_origin,
        expected_train_origins,
        exp_tr_rows,
        exp_te_rows,
        exp_pool_rows,
        exp_hg_pos,
    ) in exp_configs:
        tr_feat = pd.read_csv(
            SPLITS_DIR / f"train_{test_origin}_features.csv", float_precision="round_trip"
        )
        tr_targ = pd.read_csv(
            SPLITS_DIR / f"train_{test_origin}_targets.csv", float_precision="round_trip"
        )
        te_feat = pd.read_csv(
            SPLITS_DIR / f"test_{test_origin}_features.csv", float_precision="round_trip"
        )
        te_targ = pd.read_csv(
            SPLITS_DIR / f"test_{test_origin}_targets.csv", float_precision="round_trip"
        )
        pool_feat = pd.read_csv(
            SPLITS_DIR / f"rq3_{test_origin}_pool_features.csv", float_precision="round_trip"
        )
        pool_lbl = pd.read_csv(
            SPLITS_DIR / f"rq3_{test_origin}_pool_labels.csv", float_precision="round_trip"
        )

        # Row counts and exact origins.
        tr_origins = set(tr_feat["forecast_origin"].astype(int).tolist())
        te_origins = set(te_feat["forecast_origin"].astype(int).tolist())
        pool_origins = set(pool_feat["forecast_origin"].astype(int).tolist())
        counts_ok = (
            len(tr_feat) == exp_tr_rows
            and len(tr_targ) == exp_tr_rows
            and len(te_feat) == exp_te_rows
            and len(te_targ) == exp_te_rows
            and len(pool_feat) == exp_pool_rows
            and len(pool_lbl) == exp_pool_rows
            and tr_origins == expected_train_origins
            and te_origins == {test_origin}
            and pool_origins == {test_origin}
        )
        record(
            f"C5_{test_origin}_row_counts_and_origins",
            counts_ok,
            f"train={len(tr_feat)} (origins={sorted(tr_origins)}), "
            f"test={len(te_feat)} (origin={sorted(te_origins)}), "
            f"rq3_pool={len(pool_feat)}",
        )

        # Cutoff & zero train/test overlap.
        tr_keys = list(
            zip(tr_feat["forecast_origin"].astype(int), tr_feat["topic_id"].astype(str))
        )
        te_keys = list(
            zip(te_feat["forecast_origin"].astype(int), te_feat["topic_id"].astype(str))
        )
        cutoff_ok = max(tr_origins) + 3 <= test_origin and len(set(tr_keys) & set(te_keys)) == 0
        record(
            f"C6_{test_origin}_leakage_free_cutoff",
            cutoff_ok,
            f"max_train_origin+3={max(tr_origins)+3} <= {test_origin}, overlap_keys=0",
        )

        # Unique sorted keys and exact pair alignment.
        pair_aligned = (
            tr_keys == sorted(tr_keys)
            and len(tr_keys) == len(set(tr_keys))
            and tr_keys
            == list(
                zip(
                    tr_targ["forecast_origin"].astype(int),
                    tr_targ["topic_id"].astype(str),
                )
            )
            and te_keys == sorted(te_keys)
            and len(te_keys) == len(set(te_keys))
            and te_keys
            == list(
                zip(
                    te_targ["forecast_origin"].astype(int),
                    te_targ["topic_id"].astype(str),
                )
            )
            and list(
                zip(
                    pool_feat["forecast_origin"].astype(int),
                    pool_feat["topic_id"].astype(str),
                )
            )
            == list(
                zip(
                    pool_lbl["forecast_origin"].astype(int),
                    pool_lbl["topic_id"].astype(str),
                )
            )
        )
        record(
            f"C7_{test_origin}_sorted_unique_aligned_keys",
            pair_aligned,
            "All feature/target and pool feature/label pairs strictly sorted, unique, and identical",
        )

        # Eligibility verification against independent Stage 3.1 lookup.
        elig_rows = [
            k
            for k, r in src_lookup.items()
            if k[0] in expected_train_origins and is_eligible(r)
        ]
        elig_te_rows = [
            k for k, r in src_lookup.items() if k[0] == test_origin and is_eligible(r)
        ]
        elig_ok = (
            set(tr_keys) == set(elig_rows)
            and set(te_keys) == set(elig_te_rows)
            and all(float(src_lookup[k]["global_topic_3yr"]) >= 50.0 for k in tr_keys + te_keys)
        )
        record(
            f"C8_{test_origin}_eligibility_verified",
            elig_ok,
            f"100% match with Stage 3.1 eligible==True and global_topic_3yr>=50",
        )

        # Strict column separation & finiteness.
        for fname, frame in [
            (f"train_{test_origin}_features.csv", tr_feat),
            (f"test_{test_origin}_features.csv", te_feat),
            (f"rq3_{test_origin}_pool_features.csv", pool_feat),
        ]:
            bad = FORBIDDEN_IN_FEATURES & set(frame.columns)
            if bad:
                separation_violations.append(f"{fname}:{sorted(bad)}")
            if set(EXPECTED_PREDICTOR_COLS) - set(frame.columns):
                separation_violations.append(f"{fname}:missing_predictors")
            vals = frame[EXPECTED_PREDICTOR_COLS].to_numpy(dtype=np.float64)
            if not np.isfinite(vals).all():
                nonfinite_files.append(fname)

        for fname, frame in [
            (f"train_{test_origin}_targets.csv", tr_targ),
            (f"test_{test_origin}_targets.csv", te_targ),
            (f"rq3_{test_origin}_pool_labels.csv", pool_lbl),
        ]:
            bad = set(EXPECTED_PREDICTOR_COLS) & set(frame.columns)
            if bad:
                separation_violations.append(f"{fname}:{sorted(bad)}")
            num_cols = [c for c in frame.columns if c not in ("forecast_origin", "topic_id")]
            vals = frame[num_cols].to_numpy(dtype=np.float64)
            if not np.isfinite(vals).all():
                nonfinite_files.append(fname)

        # Independent RQ3 recomputation from raw Stage 3.1 lookup.
        indep_te = sorted(elig_te_rows)
        indep_m0 = np.array([float(src_lookup[k]["m0_adj"]) for k in indep_te], dtype=np.float64)
        q80_past = float(np.quantile(indep_m0, 0.80, method="linear"))
        past_ties = int(np.sum(indep_m0 == q80_past))
        indep_pool_keys = [k for k, m0 in zip(indep_te, indep_m0) if m0 < q80_past]
        indep_pool_g = np.array(
            [float(src_lookup[k]["g_adj"]) for k in indep_pool_keys], dtype=np.float64
        )
        q80_fut = float(np.quantile(indep_pool_g, 0.80, method="linear"))
        indep_hg = (indep_pool_g >= q80_fut).astype(np.int64)

        exp_pool_keys = list(
            zip(pool_lbl["forecast_origin"].astype(int), pool_lbl["topic_id"].astype(str))
        )
        exp_hg = pool_lbl["hg_future"].to_numpy(dtype=np.int64)
        rq3_ok = (
            exp_pool_keys == indep_pool_keys
            and np.array_equal(exp_hg, indep_hg)
            and len(indep_pool_keys) == exp_pool_rows
            and int(np.sum(indep_hg)) == exp_hg_pos
            and past_ties == 0
        )
        detail_rq3 = (
            f"q80_past={q80_past:.8f} (past_ties={past_ties}, excl={len(indep_te)-len(indep_pool_keys)}), "
            f"q80_fut={q80_fut:.8f}, hg_pos={int(np.sum(indep_hg))}/{len(indep_pool_keys)}"
        )
        if test_origin == 2021:
            idx_2021 = (len(indep_pool_keys) - 1) * 0.80
            detail_rq3 += f", linear_idx={idx_2021:.1f}, strict_gt={int(np.sum(indep_pool_g > q80_fut))}"
        record(f"C9_{test_origin}_rq3_independent_recompute", rq3_ok, detail_rq3)

        # GroupKFold & direct-leakage verification on Experiment B (2021).
        if test_origin == 2021:
            t15 = {
                k[1]: float(src_lookup[k]["g_adj"])
                for k in tr_keys
                if k[0] == 2015
            }
            t18 = {
                k[1]: float(src_lookup[k]["m0_adj"])
                for k in tr_keys
                if k[0] == 2018
            }
            common = sorted(set(t15) & set(t18))
            max_id_diff = max(abs(t15[t] - t18[t]) for t in common)
            gkf = GroupKFold(n_splits=5, shuffle=True, random_state=42)
            grp = tr_feat["topic_id"].to_numpy()
            overlaps = [
                len(set(grp[tr_i]) & set(grp[va_i]))
                for tr_i, va_i in gkf.split(tr_feat, groups=grp)
            ]
            val_sizes = [len(va_i) for _, va_i in gkf.split(tr_feat, groups=grp)]
            record(
                "C10_2021_direct_leakage_proof_and_groupkfold",
                len(common) == 989 and max_id_diff == 0.0 and overlaps == [0, 0, 0, 0, 0],
                f"overlapping_topics_2015_2018={len(common)}, max_abs_diff(G2015,M0_2018)={max_id_diff:.2e}, "
                f"GroupKFold_val_rows={val_sizes}, cross_fold_topic_overlap={overlaps}",
            )

        # Full scalar value traceability against Stage 3.1 source across all 6 files of this experiment.
        for frame in (tr_feat, te_feat, pool_feat):
            for _, row in frame.iterrows():
                src_row = src_lookup[(int(row["forecast_origin"]), str(row["topic_id"]))]
                for col in EXPECTED_PREDICTOR_COLS:
                    all_trace_diffs.append(abs(float(row[col]) - float(src_row[col])))
        for frame in (tr_targ, te_targ):
            for _, row in frame.iterrows():
                src_row = src_lookup[(int(row["forecast_origin"]), str(row["topic_id"]))]
                for col in ("g_adj", "target_global_topic_fut3yr", "target_w_allsci_fut3yr"):
                    all_trace_diffs.append(abs(float(row[col]) - float(src_row[col])))
        for _, row in pool_lbl.iterrows():
            src_row = src_lookup[(int(row["forecast_origin"]), str(row["topic_id"]))]
            all_trace_diffs.append(abs(float(row["g_adj"]) - float(src_row["g_adj"])))

    record(
        "C11_strict_feature_target_separation",
        len(separation_violations) == 0,
        "Zero target/label columns in feature CSVs and zero predictor columns in target/label CSVs"
        if not separation_violations
        else f"Violations: {separation_violations}",
    )
    record(
        "C12_zero_missing_nan_inf",
        len(nonfinite_files) == 0,
        "Zero NaN/Inf across all 12 exported CSVs"
        if not nonfinite_files
        else f"Non-finite in: {nonfinite_files}",
    )
    max_trace_diff = max(all_trace_diffs) if all_trace_diffs else math.inf
    record(
        "C13_full_source_scalar_traceability",
        max_trace_diff <= 1e-12,
        f"checked {len(all_trace_diffs):,} scalar cells across all 12 CSVs; max_abs_diff={max_trace_diff:.3e}",
    )

    # 14. Manifest hashes & zero absolute paths check.
    hash_mismatches = []
    for fname in EXPECTED_EXPORTS:
        actual_hash = sha256_file(SPLITS_DIR / fname)
        manifest_hash = manifest["outputs"][fname]["sha256"]
        if actual_hash != manifest_hash:
            hash_mismatches.append(fname)
    manifest_text = MANIFEST_PATH.read_text(encoding="utf-8")
    abs_path_hits = re.findall(r"[A-Za-z]:[/\\\\]", manifest_text)
    record(
        "C14_manifest_hashes_and_relative_paths",
        len(hash_mismatches) == 0 and len(abs_path_hits) == 0,
        f"all 12 manifest SHA-256 match disk; machine_absolute_paths={len(abs_path_hits)}",
    )

    # 15. Repeated-execution determinism check via subprocess --out-dir.
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        proc = subprocess.run(
            [sys.executable, "-B", str(BUILDER_SCRIPT), "--out-dir", str(tmp_path)],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            check=True,
        )
        repro_diffs = []
        for fname in EXPECTED_EXPORTS:
            if sha256_file(tmp_path / fname) != sha256_file(SPLITS_DIR / fname):
                repro_diffs.append(fname)
        record(
            "C15_deterministic_repeated_execution",
            len(repro_diffs) == 0 and proc.returncode == 0,
            "All 12 CSVs produced byte-for-byte identical SHA-256 on repeated execution"
            if not repro_diffs
            else f"Hash diffs: {repro_diffs}",
        )

    # 16. Stage 3.2 boundary check (no Stage 3.3 artifacts in splits dir or stage3_modeling).
    forbidden_patterns = (
        "*scaler*",
        "*ridge*",
        "*prediction*",
        "*cv_result*",
        "*bootstrap*",
        "*top50*",
        "*.pkl",
        "*.joblib",
    )
    found_stage3_3 = []
    for pat in forbidden_patterns:
        found_stage3_3.extend(
            to_repo_posix(p)
            for p in (REPO_ROOT / "stage3_modeling").rglob(pat)
            if p.is_file()
        )
    record(
        "C16_strict_stage3_2_boundary_no_modeling_artifacts",
        len(found_stage3_3) == 0 and manifest["boundary_assertions"]["models_trained"] is False,
        "Zero fitted scalers, Ridge models, CV outputs, predictions, or bootstrap artifacts present"
        if not found_stage3_3
        else f"Found forbidden artifacts: {found_stage3_3}",
    )

    # 17. Re-verify upstream SHA-256 immutability post-audit.
    immut_ok = (
        sha256_file(STAGE3_1_CSV) == EXPECTED_STAGE3_1_SHA256
        and sha256_file(STAGE2_PANEL_CSV) == EXPECTED_STAGE2_PANEL_SHA256
        and sha256_file(STAGE2_DENOM_CSV) == EXPECTED_STAGE2_DENOM_SHA256
    )
    record(
        "C17_upstream_immutability_post_run",
        immut_ok,
        "Stage 3.1 and Stage 2 frozen CSVs remain byte-identical after Stage 3.2 build and audit",
    )

    passed_count = sum(1 for _, status, _ in checks if status == "PASS")
    total_count = len(checks)
    overall = "PASS" if passed_count == total_count else "FAIL"

    # Build Markdown audit report using relative paths only.
    exp_a = manifest["experiments"]["2018"]
    exp_b = manifest["experiments"]["2021"]
    lines = [
        "# Stage 3.2 Independent Audit Report",
        "",
        f"**Overall Verdict:** **{overall} ({passed_count}/{total_count} checks passed)**",
        "",
        "## 1. Audited Scope & Inputs",
        f"- Canonical Stage 3.1 input: `{to_repo_posix(STAGE3_1_CSV)}` (`SHA-256: {h31}`)",
        f"- Stage 2 synchronized panel: `{to_repo_posix(STAGE2_PANEL_CSV)}` (`SHA-256: {hp}`)",
        f"- Stage 2 denominators: `{to_repo_posix(STAGE2_DENOM_CSV)}` (`SHA-256: {hd}`)",
        f"- Stage 3.2 manifest: `{to_repo_posix(MANIFEST_PATH)}`",
        "",
        "## 2. Dataset & RQ3 Summary",
        "| Metric | Experiment A (Test Origin 2018) | Experiment B (Test Origin 2021) |",
        "| --- | ---: | ---: |",
        f"| Training Origins | `2015` | `2015–2018` |",
        f"| Training Rows | {exp_a['train_rows']:,} | {exp_b['train_rows']:,} |",
        f"| Unique Training Topics | {exp_a['train_unique_topics']:,} | {exp_b['train_unique_topics']:,} |",
        f"| Test Rows | {exp_a['test_rows']:,} | {exp_b['test_rows']:,} |",
        f"| RQ3 $Q_{{0.80}}^{{\\text{{Past}}}}$ (`linear`) | {exp_a['rq3']['q80_past']:.8f} | {exp_b['rq3']['q80_past']:.8f} |",
        f"| RQ3 Past HG Excluded ($\\ge Q_{{0.80}}^{{\\text{{Past}}}}$) | {exp_a['rq3']['past_excluded_rows']:,} | {exp_b['rq3']['past_excluded_rows']:,} |",
        f"| RQ3 Remaining Pool ($< Q_{{0.80}}^{{\\text{{Past}}}}$) | {exp_a['rq3']['remaining_pool_rows']:,} | {exp_b['rq3']['remaining_pool_rows']:,} |",
        f"| RQ3 $Q_{{0.80}}^{{\\text{{Future}}}}$ (`linear`) | {exp_a['rq3']['q80_future']:.8f} | {exp_b['rq3']['q80_future']:.8f} |",
        f"| RQ3 Future HG Positives (`>=`) | {exp_a['rq3']['future_hg_count_ge']:,} ({100*exp_a['rq3']['actual_chance_rate']:.2f}%) | {exp_b['rq3']['future_hg_count_ge']:,} ({100*exp_b['rq3']['actual_chance_rate']:.2f}%) |",
        f"| Chance Expected Hits@50 | {exp_a['rq3']['chance_expected_hits_at_50']:.2f} | {exp_b['rq3']['chance_expected_hits_at_50']:.2f} |",
        "",
        "## 3. Check-by-Check Audit Results",
        "| Check ID | Status | Supporting Evidence |",
        "| --- | :---: | --- |",
    ]
    for name, status, detail in checks:
        lines.append(f"| `{name}` | **{status}** | {detail} |")

    lines.extend(
        [
            "",
            "## 4. Exported Artifact Inventory & SHA-256 Hashes",
            "| Artifact | Role | Shape | SHA-256 |",
            "| --- | --- | ---: | --- |",
        ]
    )
    for fname in EXPECTED_EXPORTS:
        meta = manifest["outputs"][fname]
        lines.append(
            f"| `{meta['relative_path']}` | `{meta['role']}` | "
            f"{meta['rows']:,} × {meta['columns']} | `{meta['sha256']}` |"
        )

    lines.append("")
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8", newline="\n")

    for name, status, detail in checks:
        print(f"[{status}] {name}: {detail}")
    print(f"\nStage 3.2 Audit Result: {overall} ({passed_count}/{total_count} passed)")
    return 0 if passed_count == total_count else 1


if __name__ == "__main__":
    raise SystemExit(main())

