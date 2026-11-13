#!/usr/bin/env python3
"""Stage 3.2 deterministic train/test split and RQ3 candidate-pool builder.

Constructs strictly leakage-free temporal train/test datasets and RQ3 emerging
high-growth candidate pools for the two approved test forecast origins (2018
and 2021) from the audited Stage 3.1 feature-target dataset.

Strict Stage 3.2 scope:
- Exports predictor feature matrices separately from target/label files so
  target values (`g_adj`, `target_*_fut3yr`, `hg_future`) cannot enter fitting.
- Does NOT fit scalers, train Ridge models, tune alpha, or evaluate forecasts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import sklearn
from sklearn.model_selection import GroupKFold

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_OUT_DIR = Path(__file__).resolve().parent

STAGE3_1_CSV = REPO_ROOT / "stage3_modeling" / "stage3_origin_features_targets.csv"
STAGE3_1_SHA256 = "9fc15d6ed16ade633547bfca9efca1db92827aa665cbb4509d76c7dae057f488"

STAGE2_PANEL_CSV = (
    REPO_ROOT
    / "openalex_feasibility_audit"
    / "openalex_modeling_panel_1025topics_v2_synchronized.csv"
)
STAGE2_PANEL_SHA256 = (
    "f0049cd71f5ba8545c2e3cbb850e036a7b849828321cd23aa1d04771e60d7175"
)

STAGE2_DENOM_CSV = (
    REPO_ROOT
    / "openalex_feasibility_audit"
    / "all_science_national_denominators_fractional_v2_live_recheck_20261105.csv"
)
STAGE2_DENOM_SHA256 = (
    "9c2d9cccee65c156494b96447ce53045d43e514c74aa10ec9f1c85915b33afce"
)

IDENTIFIER_COLUMNS = [
    "forecast_origin",
    "topic_id",
    "topic_name",
    "field_name",
    "subfield_name",
    "eligible",
]

TARGET_EXPORT_COLUMNS = [
    "forecast_origin",
    "topic_id",
    "g_adj",
    "target_global_topic_fut3yr",
    "target_w_allsci_fut3yr",
]

RQ3_LABEL_EXPORT_COLUMNS = [
    "forecast_origin",
    "topic_id",
    "g_adj",
    "hg_future",
]

PREDICTOR_COLUMNS = [
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

FEATURE_EXPORT_COLUMNS = IDENTIFIER_COLUMNS + PREDICTOR_COLUMNS

MODEL_FEATURE_SETS = {
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

EXPERIMENTS = [
    {
        "experiment_id": "experiment_a_2018",
        "test_origin": 2018,
        "train_origins": [2015],
        "expected_train_rows": 990,
        "expected_test_rows": 992,
        "expected_rq3_pool_rows": 793,
        "expected_rq3_future_hg": 159,
    },
    {
        "experiment_id": "experiment_b_2021",
        "test_origin": 2021,
        "train_origins": [2015, 2016, 2017, 2018],
        "expected_train_rows": 3963,
        "expected_test_rows": 995,
        "expected_rq3_pool_rows": 796,
        "expected_rq3_future_hg": 160,
    },
]

KEY_COLUMNS = ["forecast_origin", "topic_id"]


def sha256_file(path: Path) -> str:
    """Return lowercase hexadecimal SHA-256 digest of a file."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def to_repo_posix(path: Path) -> str:
    """Serialize a path relative to repository root without absolute prefixes."""
    resolved = path.resolve()
    try:
        return resolved.relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return resolved.name


def verify_upstream_hashes() -> None:
    """Ensure Stage 3.1 and Stage 2 inputs match their locked SHA-256 hashes."""
    checks = [
        (STAGE3_1_CSV, STAGE3_1_SHA256, "Stage 3.1 canonical CSV"),
        (STAGE2_PANEL_CSV, STAGE2_PANEL_SHA256, "Stage 2 synchronized panel CSV"),
        (STAGE2_DENOM_CSV, STAGE2_DENOM_SHA256, "Stage 2 denominators CSV"),
    ]
    for path, expected, label in checks:
        if not path.is_file():
            raise FileNotFoundError(f"Missing required {label}: {to_repo_posix(path)}")
        actual = sha256_file(path)
        if actual != expected:
            raise ValueError(
                f"SHA-256 mismatch for {label}: expected {expected}, got {actual}"
            )


def check_sklearn_floor() -> None:
    """Require scikit-learn >= 1.6 for GroupKFold(shuffle=True, random_state=...)."""
    parts = sklearn.__version__.split(".")
    major, minor = int(parts[0]), int(parts[1])
    if (major, minor) < (1, 6):
        raise RuntimeError(
            f"scikit-learn >= 1.6 is required for GroupKFold(shuffle=True); "
            f"found {sklearn.__version__}"
        )


def compute_groupkfold_metadata(train_df: pd.DataFrame) -> dict[str, Any]:
    """Verify topic-grouped 5-fold CV structure without fitting any model."""
    gkf = GroupKFold(n_splits=5, shuffle=True, random_state=42)
    groups = train_df["topic_id"].to_numpy()
    folds = []
    for fold_idx, (tr_idx, val_idx) in enumerate(gkf.split(train_df, groups=groups)):
        tr_topics = set(groups[tr_idx].tolist())
        val_topics = set(groups[val_idx].tolist())
        overlap = len(tr_topics & val_topics)
        if overlap != 0:
            raise ValueError(
                f"GroupKFold fold {fold_idx} leaked {overlap} topic_id values"
            )
        folds.append(
            {
                "fold": fold_idx,
                "train_rows": int(len(tr_idx)),
                "val_rows": int(len(val_idx)),
                "train_unique_topics": int(len(tr_topics)),
                "val_unique_topics": int(len(val_topics)),
                "topic_overlap": overlap,
            }
        )
    return {
        "cv_splitter": "GroupKFold(n_splits=5, shuffle=True, random_state=42)",
        "group_column": "topic_id",
        "folds": folds,
        "zero_cross_fold_topic_overlap": all(f["topic_overlap"] == 0 for f in folds),
    }


def write_deterministic_csv(df: pd.DataFrame, path: Path) -> str:
    """Write DataFrame deterministically with Unix LF newlines and return SHA-256."""
    df.to_csv(path, index=False, lineterminator="\n")
    return sha256_file(path)


def build_stage3_2_splits(out_dir: Path) -> dict[str, Any]:
    """Construct all Stage 3.2 split CSVs and manifest inside `out_dir`."""
    check_sklearn_floor()
    verify_upstream_hashes()
    out_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(STAGE3_1_CSV, float_precision="round_trip")
    if df.shape != (7175, 42):
        raise ValueError(f"Expected Stage 3.1 shape (7175, 42), got {df.shape}")

    required_cols = set(FEATURE_EXPORT_COLUMNS + TARGET_EXPORT_COLUMNS + ["global_topic_3yr"])
    missing = sorted(required_cols - set(df.columns))
    if missing:
        raise ValueError(f"Missing expected columns in Stage 3.1 CSV: {missing}")

    eligible_df = df[df["eligible"] == True].copy()  # noqa: E712
    if not (eligible_df["global_topic_3yr"] >= 50).all():
        raise ValueError("Eligibility violation: found eligible row with global_topic_3yr < 50")

    outputs_meta: dict[str, dict[str, Any]] = {}
    experiments_meta: dict[str, dict[str, Any]] = {}

    for spec in EXPERIMENTS:
        test_origin = int(spec["test_origin"])
        train_origins = [int(y) for y in spec["train_origins"]]

        train_df = (
            eligible_df[eligible_df["forecast_origin"].isin(train_origins)]
            .sort_values(KEY_COLUMNS, ascending=True)
            .reset_index(drop=True)
        )
        test_df = (
            eligible_df[eligible_df["forecast_origin"] == test_origin]
            .sort_values(KEY_COLUMNS, ascending=True)
            .reset_index(drop=True)
        )

        if len(train_df) != spec["expected_train_rows"]:
            raise ValueError(
                f"Origin {test_origin} train rows mismatch: "
                f"expected {spec['expected_train_rows']}, got {len(train_df)}"
            )
        if len(test_df) != spec["expected_test_rows"]:
            raise ValueError(
                f"Origin {test_origin} test rows mismatch: "
                f"expected {spec['expected_test_rows']}, got {len(test_df)}"
            )
        if max(train_origins) + 3 > test_origin:
            raise ValueError(
                f"Temporal leakage detected for test origin {test_origin}: {train_origins}"
            )

        # Verify numerical finiteness across all exported columns.
        numeric_check_cols = PREDICTOR_COLUMNS + [
            "g_adj",
            "target_global_topic_fut3yr",
            "target_w_allsci_fut3yr",
        ]
        for label_name, split_df in [("train", train_df), ("test", test_df)]:
            arr = split_df[numeric_check_cols].to_numpy(dtype=np.float64)
            if not np.isfinite(arr).all():
                raise ValueError(
                    f"Non-finite values in {label_name}_{test_origin}"
                )

        # Verify G_adj(t) == M0_adj(t+3) identity for pooled training origins if applicable.
        leakage_pairs = 0
        max_identity_diff = 0.0
        if 2015 in train_origins and 2018 in train_origins:
            t15 = train_df[train_df["forecast_origin"] == 2015][["topic_id", "g_adj"]]
            t18 = train_df[train_df["forecast_origin"] == 2018][["topic_id", "m0_adj"]]
            merged = t15.merge(t18, on="topic_id", how="inner")
            leakage_pairs = int(len(merged))
            max_identity_diff = float(
                np.max(np.abs(merged["g_adj"].to_numpy() - merged["m0_adj"].to_numpy()))
            )

        # RQ3 construction strictly on test_df using locked linear quantile and >= rule.
        m0_vals = test_df["m0_adj"].to_numpy(dtype=np.float64)
        q80_past = float(np.quantile(m0_vals, 0.80, method="linear"))
        past_excluded_mask = m0_vals >= q80_past
        past_boundary_ties = int(np.sum(m0_vals == q80_past))
        excluded_count = int(np.sum(past_excluded_mask))

        pool_df = (
            test_df.loc[~past_excluded_mask]
            .sort_values(KEY_COLUMNS, ascending=True)
            .reset_index(drop=True)
        )
        if len(pool_df) != spec["expected_rq3_pool_rows"]:
            raise ValueError(
                f"Origin {test_origin} RQ3 pool rows mismatch: "
                f"expected {spec['expected_rq3_pool_rows']}, got {len(pool_df)}"
            )

        pool_g_adj = pool_df["g_adj"].to_numpy(dtype=np.float64)
        q80_future = float(np.quantile(pool_g_adj, 0.80, method="linear"))
        hg_future = (pool_g_adj >= q80_future).astype(np.int64)
        future_hg_count = int(np.sum(hg_future))
        if future_hg_count != spec["expected_rq3_future_hg"]:
            raise ValueError(
                f"Origin {test_origin} RQ3 HG count mismatch: "
                f"expected {spec['expected_rq3_future_hg']}, got {future_hg_count}"
            )
        strict_gt_count = int(np.sum(pool_g_adj > q80_future))
        future_boundary_ties = int(np.sum(pool_g_adj == q80_future))
        linear_index = float((len(pool_df) - 1) * 0.80)

        pool_df["hg_future"] = hg_future

        # Strictly separated feature and target/label exports.
        train_features_df = train_df[FEATURE_EXPORT_COLUMNS].copy()
        train_targets_df = train_df[TARGET_EXPORT_COLUMNS].copy()
        test_features_df = test_df[FEATURE_EXPORT_COLUMNS].copy()
        test_targets_df = test_df[TARGET_EXPORT_COLUMNS].copy()
        rq3_pool_features_df = pool_df[FEATURE_EXPORT_COLUMNS].copy()
        rq3_pool_labels_df = pool_df[RQ3_LABEL_EXPORT_COLUMNS].copy()

        export_specs = [
            (f"train_{test_origin}_features.csv", train_features_df, "features"),
            (f"train_{test_origin}_targets.csv", train_targets_df, "targets"),
            (f"test_{test_origin}_features.csv", test_features_df, "features"),
            (f"test_{test_origin}_targets.csv", test_targets_df, "targets"),
            (f"rq3_{test_origin}_pool_features.csv", rq3_pool_features_df, "rq3_features"),
            (f"rq3_{test_origin}_pool_labels.csv", rq3_pool_labels_df, "rq3_labels"),
        ]

        file_records: dict[str, Any] = {}
        for filename, export_df, role in export_specs:
            out_path = out_dir / filename
            file_hash = write_deterministic_csv(export_df, out_path)
            record = {
                "relative_path": to_repo_posix(out_path),
                "role": role,
                "rows": int(export_df.shape[0]),
                "columns": int(export_df.shape[1]),
                "column_names": list(export_df.columns),
                "sha256": file_hash,
            }
            outputs_meta[filename] = record
            file_records[filename] = record

        train_origin_counts = {
            str(int(k)): int(v)
            for k, v in train_df["forecast_origin"].value_counts().sort_index().items()
        }
        chance_rate = future_hg_count / len(pool_df)
        experiments_meta[str(test_origin)] = {
            "experiment_id": spec["experiment_id"],
            "test_origin": test_origin,
            "test_feature_window": f"[{test_origin - 2}, {test_origin}]",
            "test_momentum_base_window": f"[{test_origin - 5}, {test_origin - 3}]",
            "test_target_window": f"[{test_origin + 1}, {test_origin + 3}]",
            "train_origins": train_origins,
            "train_origin_row_counts": train_origin_counts,
            "train_rows": int(len(train_df)),
            "train_unique_topics": int(train_df["topic_id"].nunique()),
            "test_rows": int(len(test_df)),
            "test_unique_topics": int(test_df["topic_id"].nunique()),
            "max_train_target_end_year": int(max(train_origins) + 3),
            "test_leakage_overlap_rows": 0,
            "internal_train_target_overlap_note": (
                "No multi-origin overlap (single training origin 2015)."
                if len(train_origins) == 1
                else (
                    f"Pooled annual training origins {train_origins[0]}-{train_origins[-1]} have "
                    f"overlapping 3-year target windows strictly <= {test_origin}; includes "
                    f"{leakage_pairs} exact G_adj(2015)==M0_adj(2018) topic pairs "
                    f"(max abs diff {max_identity_diff:.2e}), requiring GroupKFold by topic_id "
                    f"in Stage 3.3."
                )
            ),
            "group_kfold_preview": compute_groupkfold_metadata(train_df),
            "rq3": {
                "quantile_method": "numpy.quantile(..., 0.80, method='linear')",
                "inclusion_operators": {
                    "past_high_growth_exclusion": "m0_adj >= q80_past",
                    "remaining_pool": "m0_adj < q80_past",
                    "future_high_growth_label": "g_adj >= q80_future",
                },
                "q80_past": q80_past,
                "past_excluded_rows": excluded_count,
                "past_boundary_ties": past_boundary_ties,
                "remaining_pool_rows": int(len(pool_df)),
                "linear_quantile_index_in_pool": linear_index,
                "q80_future": q80_future,
                "future_boundary_ties": future_boundary_ties,
                "future_hg_count_ge": future_hg_count,
                "future_hg_count_strict_gt": strict_gt_count,
                "actual_chance_rate": float(chance_rate),
                "chance_expected_hits_at_50": float(50.0 * chance_rate),
            },
            "files": list(file_records.keys()),
        }

    # Re-verify upstream hashes were not modified.
    verify_upstream_hashes()

    manifest = {
        "stage": "3.2",
        "title": "Train/Test Dataset Construction and RQ3 Candidate-Pool Splits",
        "environment": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "scikit_learn": sklearn.__version__,
            "sklearn_min_required": "1.6",
        },
        "source_inputs": {
            "stage3_1_features_targets": {
                "relative_path": to_repo_posix(STAGE3_1_CSV),
                "sha256": STAGE3_1_SHA256,
                "rows": 7175,
                "columns": 42,
            },
            "stage2_synchronized_panel": {
                "relative_path": to_repo_posix(STAGE2_PANEL_CSV),
                "sha256": STAGE2_PANEL_SHA256,
            },
            "stage2_denominators": {
                "relative_path": to_repo_posix(STAGE2_DENOM_CSV),
                "sha256": STAGE2_DENOM_SHA256,
            },
        },
        "schema_separation": {
            "identifier_columns": IDENTIFIER_COLUMNS,
            "predictor_columns": PREDICTOR_COLUMNS,
            "feature_export_columns": FEATURE_EXPORT_COLUMNS,
            "target_export_columns": TARGET_EXPORT_COLUMNS,
            "rq3_label_export_columns": RQ3_LABEL_EXPORT_COLUMNS,
            "model_feature_sets": MODEL_FEATURE_SETS,
        },
        "experiments": experiments_meta,
        "outputs": outputs_meta,
        "boundary_assertions": {
            "strict_stage3_2_only": True,
            "scalers_fitted": False,
            "models_trained": False,
            "hyperparameters_tuned": False,
            "test_predictions_generated": False,
            "bootstrap_evaluated": False,
        },
    }

    manifest_path = out_dir / "stage3_2_splits_manifest.json"
    manifest_text = json.dumps(manifest, indent=2) + "\n"
    manifest_path.write_text(manifest_text, encoding="utf-8", newline="\n")
    manifest["manifest_sha256"] = sha256_file(manifest_path)
    return manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build deterministic Stage 3.2 train/test and RQ3 split artifacts."
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=DEFAULT_OUT_DIR,
        help="Output directory for Stage 3.2 CSVs and manifest.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    manifest = build_stage3_2_splits(args.out_dir)
    for orig in ("2018", "2021"):
        exp = manifest["experiments"][orig]
        rq3 = exp["rq3"]
        print(
            f"[Stage 3.2] Origin {orig}: "
            f"train={exp['train_rows']}, test={exp['test_rows']}, "
            f"rq3_pool={rq3['remaining_pool_rows']}, "
            f"q80_past={rq3['q80_past']:.8f}, "
            f"q80_fut={rq3['q80_future']:.8f}, "
            f"hg_future={rq3['future_hg_count_ge']}"
        )
    print(f"[Stage 3.2] Wrote {len(manifest['outputs'])} CSVs + manifest to {to_repo_posix(args.out_dir)}")


if __name__ == "__main__":
    main()

