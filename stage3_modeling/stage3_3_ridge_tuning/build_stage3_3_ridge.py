#!/usr/bin/env python3
"""Stage 3.3 Ridge Regression and GroupKFold Hyperparameter Tuning builder.

Implements strictly in-scope Stage 3.3 model selection and final estimator
fitting on the approved Stage 3.2 training splits ONLY:
- Experiment A (Test Origin 2018): training origin 2015 (N = 990)
- Experiment B (Test Origin 2021): pooled training origins 2015-2018 (N = 3,963)
- Models fitted: M1, M2, M3 (M0 recorded as unfitted direct benchmark)

Strict Stage 3.3 boundaries:
- Never reads any Stage 3.2 test or RQ3 files.
- Never generates test-set predictions, MAE test comparisons, bootstrap CIs,
  RQ3 rankings/Hits@50, or sensitivity models (M3-LogRCA, M2-WC, M3-WC).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.linear_model import Ridge
from sklearn.model_selection import GridSearchCV, GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SPLITS_DIR = REPO_ROOT / "stage3_modeling" / "stage3_2_splits"
STAGE3_2_MANIFEST_PATH = SPLITS_DIR / "stage3_2_splits_manifest.json"
DEFAULT_OUT_DIR = Path(__file__).resolve().parent

LOCKED_TRAIN_FILES = {
    "2018": {
        "features_file": "train_2018_features.csv",
        "features_sha256": "89b220d14407d6b3b3cde69c2a9fb3ac1a8b6fc92bc0af28411520b708730ce1",
        "targets_file": "train_2018_targets.csv",
        "targets_sha256": "307c2bfce2dd663a1f133d679d58875ec4060cfb91155469da719b84c2543a7a",
        "expected_rows": 990,
        "expected_origins": [2015],
        "expected_unique_topics": 990,
        "expected_val_fold_sizes": [198, 198, 198, 198, 198],
    },
    "2021": {
        "features_file": "train_2021_features.csv",
        "features_sha256": "cfa72f2ef21142b917feecddef57434bbc998becadd511747aa123cd1c72c8dc",
        "targets_file": "train_2021_targets.csv",
        "targets_sha256": "262d7ee044b5b158fbf844ebf19d71e077bf2ec2fdbd9d339cc6d15a877779da",
        "expected_rows": 3963,
        "expected_origins": [2015, 2016, 2017, 2018],
        "expected_unique_topics": 993,
        "expected_val_fold_sizes": [796, 790, 796, 789, 792],
    },
}

LOCKED_IDENTIFIER_COLUMNS = [
    "forecast_origin",
    "topic_id",
    "topic_name",
    "field_name",
    "subfield_name",
    "eligible",
]

FORBIDDEN_DESIGN_COLUMNS = set(LOCKED_IDENTIFIER_COLUMNS) | {
    "g_adj",
    "target_global_topic_fut3yr",
    "target_w_allsci_fut3yr",
    "hg_future",
}

LOCKED_MODEL_SPECS = {
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

PRIMARY_RIDGE_MODELS = ["M1", "M2", "M3"]
TARGET_COLUMN = "g_adj"
TIE_TOLERANCE = 1e-12
INITIAL_LOG10_MIN = -3.0
INITIAL_LOG10_MAX = 5.0
INITIAL_LOG10_STEP = 0.2
MAX_EXPANSION_ROUNDS = 4
EXPANSION_DECADES = 2.0


def sha256_file(path: Path) -> str:
    """Return lowercase hexadecimal SHA-256 digest of a file."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def to_repo_posix(path: Path) -> str:
    """Serialize path relative to repository root with forward slashes only."""
    resolved = path.resolve()
    try:
        return resolved.relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return resolved.name


def check_sklearn_floor() -> None:
    """Require scikit-learn >= 1.6 for GroupKFold(shuffle=True, random_state=...)."""
    parts = sklearn.__version__.split(".")
    major, minor = int(parts[0]), int(parts[1])
    if (major, minor) < (1, 6):
        raise RuntimeError(
            f"scikit-learn >= 1.6 required for GroupKFold(shuffle=True); "
            f"found {sklearn.__version__}"
        )


def make_alpha_grid(log10_min: float, log10_max: float, step: float = 0.2) -> np.ndarray:
    """Create logarithmically spaced ascending alpha grid aligned with logspace(-3, 5, 41)."""
    n_steps = int(round((log10_max - log10_min) / step))
    exponents = np.round(log10_min + np.arange(n_steps + 1, dtype=np.float64) * step, 10)
    return np.power(10.0, exponents)


def select_best_index_largest_alpha(cv_results: dict[str, Any]) -> int:
    """Deterministic callable `refit` selecting min CV MAE, breaking 1e-12 ties to largest alpha."""
    mean_scores = np.asarray(cv_results["mean_test_score"], dtype=np.float64)
    alphas = np.asarray(cv_results["param_ridge__alpha"], dtype=np.float64)
    best_neg_mae = float(np.max(mean_scores))
    tied_mask = mean_scores >= (best_neg_mae - TIE_TOLERANCE)
    tied_indices = np.flatnonzero(tied_mask)
    best_pos = int(np.argmax(alphas[tied_indices]))
    return int(tied_indices[best_pos])


def preflight_validate(stage3_2_manifest: dict[str, Any]) -> None:
    """Verify Stage 3.2 manifest, feature specs, and training CSV hashes before fitting."""
    manifest_sets = stage3_2_manifest.get("schema_separation", {}).get("model_feature_sets", {})
    for model_name, expected_cols in LOCKED_MODEL_SPECS.items():
        if model_name not in manifest_sets:
            raise ValueError(f"Manifest missing model feature set: {model_name}")
        if list(manifest_sets[model_name]) != expected_cols:
            raise ValueError(
                f"Manifest feature set mismatch for {model_name}: "
                f"expected {expected_cols}, got {manifest_sets[model_name]}"
            )
        overlap = set(expected_cols) & FORBIDDEN_DESIGN_COLUMNS
        if overlap:
            raise ValueError(
                f"Forbidden identifier/target column in {model_name}: {sorted(overlap)}"
            )

    manifest_id_cols = stage3_2_manifest.get("schema_separation", {}).get(
        "identifier_columns", []
    )
    if list(manifest_id_cols) != LOCKED_IDENTIFIER_COLUMNS:
        raise ValueError(f"Identifier columns mismatch in manifest: {manifest_id_cols}")

    outputs_meta = stage3_2_manifest.get("outputs", {})
    for orig_str, cfg in LOCKED_TRAIN_FILES.items():
        for kind in ("features", "targets"):
            fname = cfg[f"{kind}_file"]
            expected_hash = cfg[f"{kind}_sha256"]
            fpath = SPLITS_DIR / fname
            if not fpath.is_file():
                raise FileNotFoundError(f"Missing Stage 3.2 training file: {to_repo_posix(fpath)}")
            actual_hash = sha256_file(fpath)
            if actual_hash != expected_hash:
                raise ValueError(
                    f"SHA-256 mismatch for {fname}: expected {expected_hash}, got {actual_hash}"
                )
            if outputs_meta.get(fname, {}).get("sha256") != actual_hash:
                raise ValueError(f"Stage 3.2 manifest SHA-256 mismatch for {fname}")

        exp_meta = stage3_2_manifest.get("experiments", {}).get(orig_str, {})
        if exp_meta.get("train_rows") != cfg["expected_rows"]:
            raise ValueError(f"Unexpected train_rows in manifest for {orig_str}")
        if exp_meta.get("train_origins") != cfg["expected_origins"]:
            raise ValueError(f"Unexpected train_origins in manifest for {orig_str}")


def load_aligned_training_data(
    orig_str: str, stage3_2_manifest: dict[str, Any]
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Load, validate, and one-to-one join training features and targets for an experiment."""
    cfg = LOCKED_TRAIN_FILES[orig_str]
    feat_df = pd.read_csv(SPLITS_DIR / cfg["features_file"], float_precision="round_trip")
    targ_df = pd.read_csv(SPLITS_DIR / cfg["targets_file"], float_precision="round_trip")

    if len(feat_df) != cfg["expected_rows"] or len(targ_df) != cfg["expected_rows"]:
        raise ValueError(
            f"Row count mismatch in {orig_str}: features={len(feat_df)}, targets={len(targ_df)}"
        )

    # Check exact training origins and uniqueness of (forecast_origin, topic_id).
    actual_origins = sorted(feat_df["forecast_origin"].astype(int).unique().tolist())
    if actual_origins != cfg["expected_origins"]:
        raise ValueError(
            f"Unexpected training origins for {orig_str}: {actual_origins}"
        )
    if feat_df.duplicated(subset=["forecast_origin", "topic_id"]).any():
        raise ValueError(f"Duplicate keys in {cfg['features_file']}")
    if targ_df.duplicated(subset=["forecast_origin", "topic_id"]).any():
        raise ValueError(f"Duplicate keys in {cfg['targets_file']}")

    # Strict one-to-one inner join + verify zero missing rows against both tables.
    merged = feat_df.merge(
        targ_df,
        on=["forecast_origin", "topic_id"],
        how="inner",
        validate="one_to_one",
    )
    if len(merged) != cfg["expected_rows"]:
        raise ValueError(
            f"One-to-one join row loss for {orig_str}: merged={len(merged)}"
        )

    # Sort deterministically by (forecast_origin, topic_id).
    merged = merged.sort_values(["forecast_origin", "topic_id"], ascending=True).reset_index(
        drop=True
    )

    # Verify required predictor columns and target column exist and are strictly finite.
    required_predictors = LOCKED_MODEL_SPECS["M3"]
    missing_cols = [c for c in required_predictors + [TARGET_COLUMN] if c not in merged.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns for {orig_str}: {missing_cols}")

    if not (merged["eligible"] == True).all():  # noqa: E712
        raise ValueError(f"Found non-eligible row in training set {orig_str}")

    numeric_vals = merged[required_predictors + [TARGET_COLUMN]].to_numpy(dtype=np.float64)
    if not np.isfinite(numeric_vals).all():
        raise ValueError(f"Found NaN/Inf in training predictors or target for {orig_str}")

    if merged["topic_id"].nunique() != cfg["expected_unique_topics"]:
        raise ValueError(f"Unique topic count mismatch for {orig_str}")

    # Recompute GroupKFold(n_splits=5, shuffle=True, random_state=42) deterministically.
    gkf = GroupKFold(n_splits=5, shuffle=True, random_state=42)
    groups = merged["topic_id"].to_numpy()
    splits = list(gkf.split(merged, merged[TARGET_COLUMN].to_numpy(), groups=groups))

    val_fold_sizes = []
    fold_records = []
    val_assign = np.full(len(merged), -1, dtype=np.int64)

    for fold_idx, (tr_idx, va_idx) in enumerate(splits):
        tr_topics = set(groups[tr_idx].tolist())
        va_topics = set(groups[va_idx].tolist())
        overlap = len(tr_topics & va_topics)
        if overlap != 0:
            raise ValueError(f"Origin {orig_str} fold {fold_idx} topic overlap={overlap}")
        val_assign[va_idx] = fold_idx
        val_fold_sizes.append(int(len(va_idx)))
        fold_records.append(
            {
                "fold": fold_idx,
                "train_rows": int(len(tr_idx)),
                "val_rows": int(len(va_idx)),
                "train_unique_topics": int(len(tr_topics)),
                "val_unique_topics": int(len(va_topics)),
                "topic_overlap": overlap,
            }
        )

    if np.any(val_assign < 0):
        raise ValueError(f"Unassigned rows in CV fold assignment for {orig_str}")
    if val_fold_sizes != cfg["expected_val_fold_sizes"]:
        raise ValueError(
            f"Fold sizes mismatch for {orig_str}: "
            f"expected {cfg['expected_val_fold_sizes']}, got {val_fold_sizes}"
        )

    # Compare against Stage 3.2 manifest GroupKFold preview.
    preview_folds = stage3_2_manifest["experiments"][orig_str]["group_kfold_preview"]["folds"]
    if fold_records != preview_folds:
        raise ValueError(
            f"Actual GroupKFold metadata diverges from Stage 3.2 preview for {orig_str}"
        )

    fold_df = pd.DataFrame(
        {
            "forecast_origin": merged["forecast_origin"].astype(int),
            "topic_id": merged["topic_id"].astype(str),
            "cv_fold": val_assign,
        }
    )

    return merged, {
        "splits": splits,
        "fold_records": fold_records,
        "fold_df": fold_df,
    }


def run_ridge_gridsearch(
    X: pd.DataFrame,
    y: np.ndarray,
    splits: list[tuple[np.ndarray, np.ndarray]],
    feature_cols: list[str],
) -> dict[str, Any]:
    """Run GroupKFold GridSearchCV with boundary expansion if needed."""
    # Explicit column subset assertion: design matrix contains exact predictors only.
    if list(X.columns) != feature_cols:
        raise ValueError(f"Design matrix columns {list(X.columns)} != {feature_cols}")
    if set(X.columns) & FORBIDDEN_DESIGN_COLUMNS:
        raise ValueError(f"Forbidden columns present in X: {set(X.columns) & FORBIDDEN_DESIGN_COLUMNS}")

    log10_min = INITIAL_LOG10_MIN
    log10_max = INITIAL_LOG10_MAX
    expansion_history: list[dict[str, Any]] = []

    X_arr = X.to_numpy(dtype=np.float64)

    for round_idx in range(MAX_EXPANSION_ROUNDS + 1):
        alpha_grid = make_alpha_grid(log10_min, log10_max, INITIAL_LOG10_STEP)
        if round_idx == 0:
            expected_initial = np.logspace(-3, 5, 41)
            if not np.allclose(alpha_grid, expected_initial, rtol=1e-14, atol=0.0):
                raise RuntimeError("Initial alpha grid does not match np.logspace(-3, 5, 41)")

        pipe = Pipeline([("scaler", StandardScaler()), ("ridge", Ridge())])
        gs = GridSearchCV(
            estimator=pipe,
            param_grid={"ridge__alpha": alpha_grid},
            scoring="neg_mean_absolute_error",
            cv=splits,
            refit=select_best_index_largest_alpha,
            n_jobs=1,
            return_train_score=False,
        )
        gs.fit(X_arr, y)

        best_idx = int(gs.best_index_)
        selected_alpha = float(gs.cv_results_["param_ridge__alpha"][best_idx])
        best_cv_mae = -float(gs.cv_results_["mean_test_score"][best_idx])

        hit_lower = best_idx == 0
        hit_upper = best_idx == (len(alpha_grid) - 1)

        if not hit_lower and not hit_upper:
            return {
                "gridsearch": gs,
                "alpha_grid": alpha_grid,
                "log10_min": log10_min,
                "log10_max": log10_max,
                "expansion_history": expansion_history,
                "hit_boundary_final": False,
            }

        boundary_side = "lower" if hit_lower else "upper"
        expansion_history.append(
            {
                "round": round_idx,
                "log10_min": log10_min,
                "log10_max": log10_max,
                "n_candidates": int(len(alpha_grid)),
                "selected_alpha": selected_alpha,
                "selected_cv_mae": best_cv_mae,
                "boundary_hit": boundary_side,
            }
        )
        if round_idx == MAX_EXPANSION_ROUNDS:
            raise RuntimeError(
                f"Selected alpha {selected_alpha} remained on {boundary_side} boundary "
                f"after {MAX_EXPANSION_ROUNDS} expansions"
            )
        if hit_lower:
            log10_min -= EXPANSION_DECADES
        if hit_upper:
            log10_max += EXPANSION_DECADES

    raise RuntimeError("Unreachable loop exit in run_ridge_gridsearch")


def format_cv_results_table(
    gs: GridSearchCV,
    alpha_grid: np.ndarray,
    experiment_origin: int,
    model_name: str,
) -> pd.DataFrame:
    """Extract complete CV candidates table with MAE metrics, fold MAEs, and ranks."""
    cv_res = gs.cv_results_
    alphas = np.asarray(cv_res["param_ridge__alpha"], dtype=np.float64)
    mean_mae = -np.asarray(cv_res["mean_test_score"], dtype=np.float64)
    std_mae = np.asarray(cv_res["std_test_score"], dtype=np.float64)
    fold_maes = [
        -np.asarray(cv_res[f"split{k}_test_score"], dtype=np.float64)
        for k in range(5)
    ]

    min_mae = float(np.min(mean_mae))
    within_tol = mean_mae <= (min_mae + TIE_TOLERANCE)

    # Candidate rank: ascending by mean_cv_mae (with larger alpha winning tie rank).
    order = sorted(
        range(len(alphas)),
        key=lambda idx: (round(float(mean_mae[idx]), 12), -float(alphas[idx])),
    )
    tiebreak_rank = np.empty(len(alphas), dtype=np.int64)
    for r_pos, orig_idx in enumerate(order, start=1):
        tiebreak_rank[orig_idx] = r_pos

    df = pd.DataFrame(
        {
            "test_origin": experiment_origin,
            "model": model_name,
            "candidate_index": np.arange(len(alphas), dtype=np.int64),
            "alpha": alphas,
            "log10_alpha": np.round(np.log10(alphas), 10),
            "mean_cv_mae": mean_mae,
            "std_cv_mae": std_mae,
            "fold0_mae": fold_maes[0],
            "fold1_mae": fold_maes[1],
            "fold2_mae": fold_maes[2],
            "fold3_mae": fold_maes[3],
            "fold4_mae": fold_maes[4],
            "sklearn_rank_test_score": np.asarray(cv_res["rank_test_score"], dtype=np.int64),
            "tiebreak_rank": tiebreak_rank,
            "within_tie_tolerance": within_tol,
            "is_grid_boundary": [
                (i == 0 or i == len(alpha_grid) - 1) for i in range(len(alphas))
            ],
            "selected": [i == int(gs.best_index_) for i in range(len(alphas))],
        }
    )
    return df


def build_stage3_3(out_dir: Path) -> dict[str, Any]:
    """Execute Stage 3.3 hyperparameter tuning and final model fitting."""
    check_sklearn_floor()
    if not STAGE3_2_MANIFEST_PATH.is_file():
        raise FileNotFoundError(
            f"Missing Stage 3.2 manifest: {to_repo_posix(STAGE3_2_MANIFEST_PATH)}"
        )

    stage3_2_manifest = json.loads(STAGE3_2_MANIFEST_PATH.read_text(encoding="utf-8"))
    preflight_validate(stage3_2_manifest)

    out_dir.mkdir(parents=True, exist_ok=True)
    models_dir = out_dir / "models"
    cv_dir = out_dir / "cv_results"
    models_dir.mkdir(parents=True, exist_ok=True)
    cv_dir.mkdir(parents=True, exist_ok=True)

    summary_rows: list[dict[str, Any]] = []
    experiments_meta: dict[str, Any] = {}
    outputs_meta: dict[str, Any] = {}

    for orig_str in ("2018", "2021"):
        test_origin = int(orig_str)
        train_df, cv_info = load_aligned_training_data(orig_str, stage3_2_manifest)
        y_train = train_df[TARGET_COLUMN].to_numpy(dtype=np.float64)

        # Export CV fold assignments.
        fold_filename = f"cv_folds_{orig_str}.csv"
        fold_path = out_dir / fold_filename
        cv_info["fold_df"].to_csv(fold_path, index=False, lineterminator="\n")
        outputs_meta[fold_filename] = {
            "relative_path": to_repo_posix(fold_path),
            "role": "cv_fold_assignments",
            "rows": int(len(cv_info["fold_df"])),
            "columns": int(cv_info["fold_df"].shape[1]),
            "sha256": sha256_file(fold_path),
        }

        # Include M0 direct benchmark entry in model summary (unfitted).
        summary_rows.append(
            {
                "test_origin": test_origin,
                "model": "M0",
                "n_features": 0,
                "features": "m0_adj (direct unfitted benchmark)",
                "train_rows": int(len(train_df)),
                "train_unique_topics": int(train_df["topic_id"].nunique()),
                "fitted": False,
                "selected_alpha": np.nan,
                "log10_alpha": np.nan,
                "mean_cv_mae": np.nan,
                "std_cv_mae": np.nan,
                "fold0_mae": np.nan,
                "fold1_mae": np.nan,
                "fold2_mae": np.nan,
                "fold3_mae": np.nan,
                "fold4_mae": np.nan,
                "n_tied_candidates": 0,
                "n_grid_candidates": 0,
                "grid_expanded": False,
                "grid_log10_min": np.nan,
                "grid_log10_max": np.nan,
                "selected_on_boundary": False,
                "pipeline_path": "",
                "cv_results_path": "",
            }
        )

        models_meta: dict[str, Any] = {
            "M0": {
                "fitted": False,
                "role": "unfitted_direct_momentum_benchmark",
                "feature_columns": [],
                "benchmark_column": "m0_adj",
            }
        }

        for model_name in PRIMARY_RIDGE_MODELS:
            feature_cols = LOCKED_MODEL_SPECS[model_name]
            X_train = train_df.loc[:, feature_cols].copy()

            search_out = run_ridge_gridsearch(
                X=X_train,
                y=y_train,
                splits=cv_info["splits"],
                feature_cols=feature_cols,
            )
            gs: GridSearchCV = search_out["gridsearch"]
            alpha_grid: np.ndarray = search_out["alpha_grid"]

            best_idx = int(gs.best_index_)
            selected_alpha = float(gs.best_params_["ridge__alpha"])
            # Explicitly read CV MAE via cv_results_ and best_index_ per Spec Section 7.3.
            mean_cv_mae = -float(gs.cv_results_["mean_test_score"][best_idx])
            std_cv_mae = float(gs.cv_results_["std_test_score"][best_idx])
            fold_maes = [
                -float(gs.cv_results_[f"split{k}_test_score"][best_idx])
                for k in range(5)
            ]

            cv_table = format_cv_results_table(gs, alpha_grid, test_origin, model_name)
            n_tied = int(cv_table["within_tie_tolerance"].sum())

            cv_filename = f"cv_results_{orig_str}_{model_name.lower()}.csv"
            cv_path = cv_dir / cv_filename
            cv_table.to_csv(cv_path, index=False, lineterminator="\n")
            cv_sha = sha256_file(cv_path)
            outputs_meta[f"cv_results/{cv_filename}"] = {
                "relative_path": to_repo_posix(cv_path),
                "role": "cv_results",
                "rows": int(cv_table.shape[0]),
                "columns": int(cv_table.shape[1]),
                "sha256": cv_sha,
            }

            # Verify best_estimator_ is Pipeline([StandardScaler, Ridge]) refitted on full train set.
            best_est: Pipeline = gs.best_estimator_
            if list(best_est.named_steps.keys()) != ["scaler", "ridge"]:
                raise RuntimeError(f"Unexpected Pipeline steps: {best_est.named_steps}")
            if not isinstance(best_est.named_steps["scaler"], StandardScaler):
                raise RuntimeError("Missing StandardScaler in fitted Pipeline")
            if not isinstance(best_est.named_steps["ridge"], Ridge):
                raise RuntimeError("Missing Ridge in fitted Pipeline")
            if int(best_est.named_steps["scaler"].n_samples_seen_) != len(train_df):
                raise RuntimeError("Final Pipeline not refitted on full training set")

            model_filename = f"ridge_pipeline_{orig_str}_{model_name.lower()}.joblib"
            model_path = models_dir / model_filename
            joblib.dump(best_est, model_path, compress=0)
            model_sha = sha256_file(model_path)
            outputs_meta[f"models/{model_filename}"] = {
                "relative_path": to_repo_posix(model_path),
                "role": "fitted_pipeline",
                "n_samples_fit": int(best_est.named_steps["scaler"].n_samples_seen_),
                "n_features_fit": int(best_est.named_steps["scaler"].n_features_in_),
                "sha256": model_sha,
            }

            summary_rows.append(
                {
                    "test_origin": test_origin,
                    "model": model_name,
                    "n_features": int(len(feature_cols)),
                    "features": "|".join(feature_cols),
                    "train_rows": int(len(train_df)),
                    "train_unique_topics": int(train_df["topic_id"].nunique()),
                    "fitted": True,
                    "selected_alpha": selected_alpha,
                    "log10_alpha": float(round(np.log10(selected_alpha), 10)),
                    "mean_cv_mae": mean_cv_mae,
                    "std_cv_mae": std_cv_mae,
                    "fold0_mae": fold_maes[0],
                    "fold1_mae": fold_maes[1],
                    "fold2_mae": fold_maes[2],
                    "fold3_mae": fold_maes[3],
                    "fold4_mae": fold_maes[4],
                    "n_tied_candidates": n_tied,
                    "n_grid_candidates": int(len(alpha_grid)),
                    "grid_expanded": len(search_out["expansion_history"]) > 0,
                    "grid_log10_min": float(search_out["log10_min"]),
                    "grid_log10_max": float(search_out["log10_max"]),
                    "selected_on_boundary": bool(search_out["hit_boundary_final"]),
                    "pipeline_path": model_path.relative_to(out_dir).as_posix(),
                    "cv_results_path": cv_path.relative_to(out_dir).as_posix(),
                }
            )

            ridge_step: Ridge = best_est.named_steps["ridge"]
            scaler_step: StandardScaler = best_est.named_steps["scaler"]
            models_meta[model_name] = {
                "fitted": True,
                "feature_columns": list(feature_cols),
                "n_features": int(len(feature_cols)),
                "train_rows_refit": int(scaler_step.n_samples_seen_),
                "selected_alpha": selected_alpha,
                "selected_log10_alpha": float(round(np.log10(selected_alpha), 10)),
                "best_index": best_idx,
                "mean_cv_mae": mean_cv_mae,
                "std_cv_mae": std_cv_mae,
                "fold_maes": fold_maes,
                "n_tied_candidates_within_1e_12": n_tied,
                "grid_expanded": len(search_out["expansion_history"]) > 0,
                "expansion_history": search_out["expansion_history"],
                "final_alpha_grid": {
                    "log10_min": float(search_out["log10_min"]),
                    "log10_max": float(search_out["log10_max"]),
                    "log10_step": INITIAL_LOG10_STEP,
                    "n_candidates": int(len(alpha_grid)),
                    "alpha_min": float(alpha_grid[0]),
                    "alpha_max": float(alpha_grid[-1]),
                },
                "selected_on_boundary": bool(search_out["hit_boundary_final"]),
                "refit_intercept": float(ridge_step.intercept_),
                "refit_standardized_coefs": {
                    col: float(coef)
                    for col, coef in zip(feature_cols, ridge_step.coef_.tolist())
                },
                "pipeline_relative_path": to_repo_posix(model_path),
                "pipeline_sha256": model_sha,
                "cv_results_relative_path": to_repo_posix(cv_path),
                "cv_results_sha256": cv_sha,
            }

        experiments_meta[orig_str] = {
            "test_origin": test_origin,
            "train_origins": LOCKED_TRAIN_FILES[orig_str]["expected_origins"],
            "train_rows": int(len(train_df)),
            "train_unique_topics": int(train_df["topic_id"].nunique()),
            "target_column": TARGET_COLUMN,
            "cv_splitter": "GroupKFold(n_splits=5, shuffle=True, random_state=42)",
            "group_column": "topic_id",
            "folds": cv_info["fold_records"],
            "fold_assignments_relative_path": to_repo_posix(fold_path),
            "fold_assignments_sha256": outputs_meta[fold_filename]["sha256"],
            "models": models_meta,
        }

    summary_df = pd.DataFrame(summary_rows)
    summary_filename = "stage3_3_model_selection_summary.csv"
    summary_path = out_dir / summary_filename
    summary_df.to_csv(summary_path, index=False, lineterminator="\n")
    outputs_meta[summary_filename] = {
        "relative_path": to_repo_posix(summary_path),
        "role": "model_selection_summary",
        "rows": int(summary_df.shape[0]),
        "columns": int(summary_df.shape[1]),
        "sha256": sha256_file(summary_path),
    }

    manifest = {
        "stage": "3.3",
        "title": "Ridge Regression and GroupKFold Hyperparameter Tuning",
        "environment": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "scikit_learn": sklearn.__version__,
            "joblib": joblib.__version__,
            "sklearn_min_required": "1.6",
        },
        "source_inputs": {
            "stage3_2_manifest_relative_path": to_repo_posix(STAGE3_2_MANIFEST_PATH),
            "stage3_2_manifest_sha256": sha256_file(STAGE3_2_MANIFEST_PATH),
            "training_files_used": {
                orig: {
                    "features_path": to_repo_posix(SPLITS_DIR / cfg["features_file"]),
                    "features_sha256": cfg["features_sha256"],
                    "targets_path": to_repo_posix(SPLITS_DIR / cfg["targets_file"]),
                    "targets_sha256": cfg["targets_sha256"],
                }
                for orig, cfg in LOCKED_TRAIN_FILES.items()
            },
        },
        "locked_hyperparameter_protocol": {
            "pipeline_steps": ["StandardScaler()", "Ridge()"],
            "scoring": "neg_mean_absolute_error",
            "cv_splitter": "GroupKFold(n_splits=5, shuffle=True, random_state=42)",
            "initial_alpha_grid": "np.logspace(-3, 5, 41)",
            "tie_breaking_rule": "max_alpha within 1e-12 absolute tolerance of min mean CV MAE",
            "tie_tolerance": TIE_TOLERANCE,
            "score_extraction": "-float(gs.cv_results_['mean_test_score'][gs.best_index_])",
            "n_jobs": 1,
        },
        "experiments": experiments_meta,
        "outputs": outputs_meta,
        "boundary_assertions": {
            "strict_stage3_3_only": True,
            "test_files_read": False,
            "test_predictions_generated": False,
            "test_mae_evaluated": False,
            "bootstrap_evaluated": False,
            "rq3_top50_evaluated": False,
            "sensitivity_models_fitted": False,
        },
    }

    manifest_path = out_dir / "stage3_3_ridge_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
    manifest["manifest_sha256"] = sha256_file(manifest_path)
    return manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Stage 3.3 Ridge regression and GroupKFold hyperparameter tuning."
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=DEFAULT_OUT_DIR,
        help="Output directory for Stage 3.3 artifacts.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    manifest = build_stage3_3(args.out_dir)
    for orig_str in ("2018", "2021"):
        exp = manifest["experiments"][orig_str]
        print(f"[Stage 3.3] Experiment {orig_str} (train_rows={exp['train_rows']}, topics={exp['train_unique_topics']}):")
        for m in PRIMARY_RIDGE_MODELS:
            info = exp["models"][m]
            print(
                f"  {m}: alpha={info['selected_alpha']:.6g}, "
                f"mean_cv_mae={info['mean_cv_mae']:.6f}, "
                f"std={info['std_cv_mae']:.6f}, "
                f"grid_expanded={info['grid_expanded']}, "
                f"ties={info['n_tied_candidates_within_1e_12']}"
            )
    print(f"[Stage 3.3] Wrote manifest & artifacts to {to_repo_posix(args.out_dir)}")


if __name__ == "__main__":
    main()

