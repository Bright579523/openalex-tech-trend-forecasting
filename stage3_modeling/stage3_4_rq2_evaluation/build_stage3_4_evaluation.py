#!/usr/bin/env python3
"""Stage 3.4 — RQ2 Held-Out Test Evaluation (M0–M3 ONLY).

Evaluates the frozen Stage 3.3 primary specifications (M1, M2, M3) and the
unfitted adjusted-momentum benchmark (M0) on the held-out Stage 3.2 test sets:
- Experiment A: Test Origin 2018 (N = 992, evaluation window 2019–2021)
- Experiment B: Test Origin 2021 (N = 995, evaluation window 2022–2024)

Strict Stage 3.4 boundaries:
- Evaluates RQ2 test accuracy (MAE and paired differences) on Test Origins 2018 and 2021 only.
- Loads frozen Stage 3.3 pipelines without refitting, scaling, tuning, or cross-validation.
- Excludes training files, candidate-pool ranking metrics, and alternative feature specifications.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import io
import json
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
import scipy
import sklearn

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SPLITS_DIR = REPO_ROOT / "stage3_modeling" / "stage3_2_splits"
STAGE3_3_DIR = REPO_ROOT / "stage3_modeling" / "stage3_3_ridge_tuning"
STAGE3_2_MANIFEST_PATH = SPLITS_DIR / "stage3_2_splits_manifest.json"
STAGE3_3_MANIFEST_PATH = STAGE3_3_DIR / "stage3_3_ridge_manifest.json"
STAGE3_3_SUMMARY_PATH = STAGE3_3_DIR / "stage3_3_model_selection_summary.csv"
DEFAULT_OUT_DIR = Path(__file__).resolve().parent
BUILDER_SCRIPT_PATH = Path(__file__).resolve()
AUDIT_SCRIPT_PATH = DEFAULT_OUT_DIR / "audit_stage3_4_evaluation.py"
ASSETS_SCRIPT_PATH = (
    DEFAULT_OUT_DIR / "thesis_assets" / "scripts" / "build_stage3_4_thesis_assets.py"
)

LOCKED_TEST_EXPERIMENTS: dict[str, dict[str, Any]] = {
    "2018": {
        "experiment_id": "experiment_a_2018",
        "test_origin": 2018,
        "train_origins": [2015],
        "target_window": "[2019, 2021]",
        "features_file": "test_2018_features.csv",
        "features_sha256": "d43a96c3d4b3d8133b5553c3e0d3a568d403194d8017efce5a4ba760dd7600fa",
        "targets_file": "test_2018_targets.csv",
        "targets_sha256": "abfda6a6febae17d8b6533a2eb0fec2b61dd921e745898e8758070cec8fd11ec",
        "expected_rows": 992,
    },
    "2021": {
        "experiment_id": "experiment_b_2021",
        "test_origin": 2021,
        "train_origins": [2015, 2016, 2017, 2018],
        "target_window": "[2022, 2024]",
        "features_file": "test_2021_features.csv",
        "features_sha256": "85751d18950130c1854f96918d62dd24aca0317aaf61ad4098b922535b29ca7a",
        "targets_file": "test_2021_targets.csv",
        "targets_sha256": "ce5c55b76b95bbf0de6d4669ffc078dde7e1d784d9b920f50be99143831728db",
        "expected_rows": 995,
    },
}

LOCKED_STAGE3_2_MANIFEST_SHA256 = (
    "934f6e19fa54fb5b7b5121b02f4b278aa8e52b9c7265c4db550c30b371edafcd"
)

LOCKED_PIPELINE_SHA256: dict[str, dict[str, str]] = {
    "2018": {
        "M1": "b528e37db5f9feeed68e8d8c36680f63c91b666a0d0bf7b9cb40e2c0c9611be4",
        "M2": "6755acef3223757c57ae8d742807c5315e3a1ed0f864907bb7f8f55196d708e5",
        "M3": "ebe10abebbf4c02c81986f6820d318210e2fcd3e24d89684992482e974be4d4b",
    },
    "2021": {
        "M1": "31c31b18409fe995191193e7db76d2304c40aff38e30f7570d920c8db102940e",
        "M2": "9f7d04b414236a5d2e67df65597ca55ec40616139a638e5ad5a5c50c407ca13c",
        "M3": "bb4ccbf8fcf526f2d517e88f9bae34e200094ddcdf3eeb78168d356bd5121cc9",
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

LOCKED_MODEL_SPECS: dict[str, list[str]] = {
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

MODEL_DESCRIPTIONS: dict[str, str] = {
    "M0": "Direct momentum benchmark (M0_adj, unfitted)",
    "M1": "Ridge: M0_adj + global 3-yr log volume",
    "M2": "Ridge: M1 + DE/CN/JP 3-yr log fractional counts",
    "M3": "Ridge: M2 + DE/CN/JP 3-yr raw fractional RCA",
}

PRESPECIFIED_COMPARISONS: list[tuple[str, str, str, str]] = [
    ("M1_vs_M0", "M1", "M0", "Contribution of global topic history beyond M0 benchmark"),
    ("M2_vs_M1", "M2", "M1", "Incremental contribution of national fractional counts beyond M1"),
    ("M3_vs_M2", "M3", "M2", "Incremental contribution of raw fractional RCA beyond M2"),
    ("M3_vs_M0", "M3", "M0", "Overall improvement of M3 over direct momentum benchmark M0"),
]

PRIMARY_MODELS = ["M0", "M1", "M2", "M3"]
RIDGE_MODELS = ["M1", "M2", "M3"]
BOOTSTRAP_B = 5000
BOOTSTRAP_SEED = 42
PERCENTILE_LEVELS = [2.5, 97.5]
PERCENTILE_METHOD = "linear"


def sha256_file(path: Path) -> str:
    """Return lowercase hexadecimal SHA-256 digest of a file."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def to_repo_posix(path: Path, fallback_root: Path | None = None) -> str:
    """Serialize path relative to repository root (or fallback root) with forward slashes only."""
    resolved = path.resolve()
    try:
        return resolved.relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        if fallback_root is not None:
            try:
                return resolved.relative_to(fallback_root.resolve()).as_posix()
            except ValueError:
                pass
        return resolved.name


def save_deterministic_npz(path: Path, arrays: dict[str, np.ndarray]) -> None:
    """Write an uncompressed/compressed deterministic .npz with fixed ZIP timestamps."""
    with zipfile.ZipFile(path, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for key, arr in arrays.items():
            buf = io.BytesIO()
            np.lib.format.write_array(buf, np.asarray(arr), allow_pickle=False)
            zinfo = zipfile.ZipInfo(filename=f"{key}.npy", date_time=(1980, 1, 1, 0, 0, 0))
            zinfo.compress_type = zipfile.ZIP_DEFLATED
            zf.writestr(zinfo, buf.getvalue())


def get_git_commit_hash() -> str:
    """Return current HEAD git commit hash without mutating repository state."""
    proc = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=True,
    )
    return proc.stdout.strip()


def preflight_verify_inputs() -> tuple[dict[str, Any], dict[str, Any], pd.DataFrame]:
    """Verify upstream Stage 3.2 and Stage 3.3 manifests, test files, and saved pipelines."""
    parts = sklearn.__version__.split(".")
    if (int(parts[0]), int(parts[1])) < (1, 6):
        raise RuntimeError(f"scikit-learn >= 1.6 required; found {sklearn.__version__}")

    if not STAGE3_2_MANIFEST_PATH.is_file():
        raise FileNotFoundError("Missing Stage 3.2 manifest")
    if sha256_file(STAGE3_2_MANIFEST_PATH) != LOCKED_STAGE3_2_MANIFEST_SHA256:
        raise ValueError("Stage 3.2 manifest SHA-256 mismatch")
    stage3_2_manifest = json.loads(STAGE3_2_MANIFEST_PATH.read_text(encoding="utf-8"))

    if not STAGE3_3_MANIFEST_PATH.is_file():
        raise FileNotFoundError("Missing Stage 3.3 manifest")
    stage3_3_manifest = json.loads(STAGE3_3_MANIFEST_PATH.read_text(encoding="utf-8"))

    if not STAGE3_3_SUMMARY_PATH.is_file():
        raise FileNotFoundError("Missing Stage 3.3 model selection summary CSV")
    s33_outputs = stage3_3_manifest.get("outputs", {})
    if s33_outputs.get("stage3_3_model_selection_summary.csv", {}).get("sha256") != sha256_file(
        STAGE3_3_SUMMARY_PATH
    ):
        raise ValueError("Stage 3.3 summary CSV SHA-256 mismatch against Stage 3.3 manifest")
    stage3_3_summary = pd.read_csv(STAGE3_3_SUMMARY_PATH, float_precision="round_trip")

    # Verify model feature specs match Stage 3.2 and Stage 3.3 manifests.
    s32_sets = stage3_2_manifest.get("schema_separation", {}).get("model_feature_sets", {})
    for model_name, expected_cols in LOCKED_MODEL_SPECS.items():
        if list(s32_sets.get(model_name, [])) != expected_cols:
            raise ValueError(f"Stage 3.2 feature set mismatch for {model_name}")
        if set(expected_cols) & FORBIDDEN_DESIGN_COLUMNS:
            raise ValueError(f"Forbidden column in {model_name} spec")

    s32_outputs = stage3_2_manifest.get("outputs", {})
    for orig_str, cfg in LOCKED_TEST_EXPERIMENTS.items():
        for kind in ("features", "targets"):
            fname = cfg[f"{kind}_file"]
            fpath = SPLITS_DIR / fname
            if not fpath.is_file():
                raise FileNotFoundError(f"Missing Stage 3.2 test file: {fname}")
            actual_hash = sha256_file(fpath)
            if actual_hash != cfg[f"{kind}_sha256"]:
                raise ValueError(f"Test file SHA-256 mismatch for {fname}")
            if s32_outputs.get(fname, {}).get("sha256") != actual_hash:
                raise ValueError(f"Manifest SHA-256 mismatch for {fname}")

        s32_exp = stage3_2_manifest.get("experiments", {}).get(orig_str, {})
        if s32_exp.get("test_rows") != cfg["expected_rows"]:
            raise ValueError(f"Test row count mismatch in Stage 3.2 manifest for {orig_str}")

        s33_exp = stage3_3_manifest.get("experiments", {}).get(orig_str, {})
        for model_name in RIDGE_MODELS:
            model_meta = s33_exp.get("models", {}).get(model_name, {})
            if list(model_meta.get("feature_columns", [])) != LOCKED_MODEL_SPECS[model_name]:
                raise ValueError(f"Stage 3.3 feature mismatch for {orig_str} {model_name}")
            pipe_rel = model_meta.get("pipeline_relative_path", "")
            pipe_path = REPO_ROOT / pipe_rel
            if not pipe_path.is_file():
                raise FileNotFoundError(f"Missing Stage 3.3 pipeline: {pipe_rel}")
            actual_pipe_sha = sha256_file(pipe_path)
            if actual_pipe_sha != LOCKED_PIPELINE_SHA256[orig_str][model_name]:
                raise ValueError(f"Pipeline SHA-256 mismatch for {orig_str} {model_name}")
            if model_meta.get("pipeline_sha256") != actual_pipe_sha:
                raise ValueError(f"Manifest pipeline SHA-256 mismatch for {orig_str} {model_name}")

    return stage3_2_manifest, stage3_3_manifest, stage3_3_summary


def load_verified_test_data(orig_str: str) -> pd.DataFrame:
    """Load, validate, and one-to-one join held-out test features and targets."""
    cfg = LOCKED_TEST_EXPERIMENTS[orig_str]
    feat_df = pd.read_csv(SPLITS_DIR / cfg["features_file"], float_precision="round_trip")
    targ_df = pd.read_csv(SPLITS_DIR / cfg["targets_file"], float_precision="round_trip")

    expected_rows = cfg["expected_rows"]
    if len(feat_df) != expected_rows or len(targ_df) != expected_rows:
        raise ValueError(
            f"Test row count mismatch for {orig_str}: feat={len(feat_df)}, targ={len(targ_df)}"
        )

    if feat_df.duplicated(subset=["forecast_origin", "topic_id"]).any():
        raise ValueError(f"Duplicate keys in {cfg['features_file']}")
    if targ_df.duplicated(subset=["forecast_origin", "topic_id"]).any():
        raise ValueError(f"Duplicate keys in {cfg['targets_file']}")

    if (feat_df["forecast_origin"].astype(int) != cfg["test_origin"]).any():
        raise ValueError(f"Unexpected forecast_origin in {cfg['features_file']}")
    if (targ_df["forecast_origin"].astype(int) != cfg["test_origin"]).any():
        raise ValueError(f"Unexpected forecast_origin in {cfg['targets_file']}")

    if feat_df["topic_id"].isna().any() or targ_df["topic_id"].isna().any():
        raise ValueError(f"Missing topic_id in test {orig_str}")
    if feat_df["topic_id"].nunique() != expected_rows:
        raise ValueError(f"Non-unique topic_id count in test {orig_str}")

    if not (feat_df["eligible"] == True).all():  # noqa: E712
        raise ValueError(f"Non-eligible observation found in test {orig_str}")

    # Verify exact row-by-row sorted key alignment before and during join.
    if feat_df["topic_id"].tolist() != targ_df["topic_id"].tolist():
        raise ValueError(f"Topic order mismatch between feature and target CSVs in {orig_str}")

    merged = feat_df.merge(
        targ_df,
        on=["forecast_origin", "topic_id"],
        how="inner",
        validate="one_to_one",
    )
    if len(merged) != expected_rows:
        raise ValueError(f"One-to-one merge row loss in {orig_str}: {len(merged)}")

    merged = merged.sort_values(["forecast_origin", "topic_id"], ascending=True).reset_index(
        drop=True
    )

    required_numeric = LOCKED_MODEL_SPECS["M3"] + ["g_adj"]
    if merged[required_numeric].isna().any().any():
        raise ValueError(f"Missing numeric values in test {orig_str}")
    if not np.isfinite(merged[required_numeric].to_numpy(dtype=np.float64)).all():
        raise ValueError(f"Non-finite values in test {orig_str}")

    return merged


def load_and_verify_pipeline(
    orig_str: str, model_name: str, stage3_3_manifest: dict[str, Any]
) -> tuple[Any, dict[str, Any]]:
    """Load frozen Stage 3.3 pipeline and verify parameters match manifest without mutating."""
    model_meta = stage3_3_manifest["experiments"][orig_str]["models"][model_name]
    pipe_path = REPO_ROOT / model_meta["pipeline_relative_path"]
    pipe = joblib.load(pipe_path)

    if list(pipe.named_steps.keys()) != ["scaler", "ridge"]:
        raise RuntimeError(f"Unexpected steps in {pipe_path.name}: {pipe.named_steps}")

    scaler = pipe.named_steps["scaler"]
    ridge = pipe.named_steps["ridge"]
    expected_p = len(LOCKED_MODEL_SPECS[model_name])
    if int(scaler.n_features_in_) != expected_p:
        raise ValueError(f"Pipeline feature count mismatch for {orig_str} {model_name}")
    if int(scaler.n_samples_seen_) != stage3_3_manifest["experiments"][orig_str]["train_rows"]:
        raise ValueError(f"Pipeline train row count mismatch for {orig_str} {model_name}")
    if not np.isclose(float(ridge.alpha), float(model_meta["selected_alpha"]), rtol=1e-12, atol=0.0):
        raise ValueError(f"Pipeline alpha mismatch for {orig_str} {model_name}")
    if not np.isclose(
        float(ridge.intercept_), float(model_meta["refit_intercept"]), rtol=1e-12, atol=1e-15
    ):
        raise ValueError(f"Pipeline intercept mismatch for {orig_str} {model_name}")

    expected_coefs = np.array(
        [model_meta["refit_standardized_coefs"][c] for c in LOCKED_MODEL_SPECS[model_name]],
        dtype=np.float64,
    )
    if not np.allclose(ridge.coef_, expected_coefs, rtol=1e-12, atol=1e-15):
        raise ValueError(f"Pipeline coefs mismatch for {orig_str} {model_name}")

    return pipe, model_meta


def interpret_delta_direction(delta_obs: float, ci_low: float, ci_high: float) -> str:
    """Interpret paired Delta_MAE = MAE(aug) - MAE(ref) and its 95% CI cautiously."""
    if ci_high < 0.0:
        return "Lower MAE (error reduction; 95% paired CI strictly < 0)"
    if ci_low > 0.0:
        return "Higher MAE (error increase; 95% paired CI strictly > 0)"
    if delta_obs < 0.0:
        return "Slightly lower MAE (error reduction; 95% paired CI spans 0)"
    if delta_obs > 0.0:
        return "Slightly higher MAE (error increase; 95% paired CI spans 0)"
    return "Equal MAE (0.000000; 95% paired CI spans 0)"


def build_stage3_4(out_dir: Path, execution_timestamp_utc: str | None = None) -> dict[str, Any]:
    """Run complete Stage 3.4 RQ2 held-out evaluation and write deterministic artifacts."""
    out_dir.mkdir(parents=True, exist_ok=True)
    pred_dir = out_dir / "predictions"
    metrics_dir = out_dir / "metrics"
    boot_dir = out_dir / "bootstrap"
    for sub in (pred_dir, metrics_dir, boot_dir):
        sub.mkdir(parents=True, exist_ok=True)

    stage3_2_manifest, stage3_3_manifest, _ = preflight_verify_inputs()
    git_hash = get_git_commit_hash()
    timestamp_utc = (
        execution_timestamp_utc
        if execution_timestamp_utc is not None
        else datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    )

    outputs_meta: dict[str, Any] = {}
    experiments_meta: dict[str, Any] = {}
    bootstrap_meta: dict[str, Any] = {
        "stage": "3.4",
        "scope": "RQ2 held-out test evaluation (MAE & paired Delta_MAE)",
        "replicates_B": BOOTSTRAP_B,
        "random_seed": BOOTSTRAP_SEED,
        "rng_algorithm": "numpy.random.default_rng(42) -> PCG64",
        "quantile_levels": PERCENTILE_LEVELS,
        "percentile_method": PERCENTILE_METHOD,
        "generator_isolation": (
            "Fresh np.random.default_rng(42) per test origin; one (5000, N) index matrix "
            "reused across M0, M1, M2, and M3 within each experiment for paired comparisons."
        ),
        "conditional_ci_scope": (
            "Measures test-topic sampling uncertainty conditional on fixed Stage 3.3 "
            "fitted Ridge coefficients and tuned alpha values (no inner refitting/retuning)."
        ),
        "experiments": {},
    }

    mae_summary_rows: list[dict[str, Any]] = []
    mae_ci_rows: list[dict[str, Any]] = []
    paired_diff_rows: list[dict[str, Any]] = []
    paired_ci_rows: list[dict[str, Any]] = []

    for orig_str in ("2018", "2021"):
        cfg = LOCKED_TEST_EXPERIMENTS[orig_str]
        test_origin = int(cfg["test_origin"])
        test_df = load_verified_test_data(orig_str)
        n_test = int(len(test_df))
        y_true = test_df["g_adj"].to_numpy(dtype=np.float64)

        pred_out = test_df[
            ["forecast_origin", "topic_id", "topic_name", "field_name", "subfield_name", "m0_adj", "g_adj"]
        ].copy()

        preds: dict[str, np.ndarray] = {}
        abs_errs: dict[str, np.ndarray] = {}
        selected_alphas: dict[str, float | None] = {"M0": None}

        # M0: Direct unfitted momentum benchmark.
        preds["M0"] = test_df["m0_adj"].to_numpy(dtype=np.float64)
        if not np.isfinite(preds["M0"]).all():
            raise ValueError(f"Non-finite M0 predictions in {orig_str}")
        abs_errs["M0"] = np.abs(y_true - preds["M0"])

        # M1–M3: Frozen Stage 3.3 pipelines ONLY (no refit, no scaler fit, no tuning).
        for model_name in RIDGE_MODELS:
            pipe, model_meta = load_and_verify_pipeline(orig_str, model_name, stage3_3_manifest)
            feature_cols = LOCKED_MODEL_SPECS[model_name]
            X_frame = test_df.loc[:, feature_cols]
            if list(X_frame.columns) != feature_cols:
                raise ValueError(f"Feature column ordering mismatch for {orig_str} {model_name}")
            if set(X_frame.columns) & FORBIDDEN_DESIGN_COLUMNS:
                raise ValueError(f"Forbidden column leaked into X for {orig_str} {model_name}")

            y_pred = np.asarray(pipe.predict(X_frame.to_numpy(dtype=np.float64)), dtype=np.float64)
            if y_pred.shape != (n_test,) or not np.isfinite(y_pred).all():
                raise ValueError(f"Invalid prediction shape or non-finite values for {orig_str} {model_name}")
            preds[model_name] = y_pred
            abs_errs[model_name] = np.abs(y_true - y_pred)
            selected_alphas[model_name] = float(model_meta["selected_alpha"])

        for m in PRIMARY_MODELS:
            pred_out[f"pred_{m.lower()}"] = preds[m]
        for m in PRIMARY_MODELS:
            pred_out[f"error_{m.lower()}"] = y_true - preds[m]
        for m in PRIMARY_MODELS:
            pred_out[f"abs_error_{m.lower()}"] = abs_errs[m]

        pred_rel_key = f"predictions/predictions_test_{orig_str}.csv"
        pred_path = pred_dir / f"predictions_test_{orig_str}.csv"
        pred_out.to_csv(pred_path, index=False, lineterminator="\n")
        outputs_meta[pred_rel_key] = {
            "relative_path": to_repo_posix(pred_path, out_dir),
            "role": "test_predictions",
            "rows": int(pred_out.shape[0]),
            "columns": int(pred_out.shape[1]),
            "sha256": sha256_file(pred_path),
        }

        # Paired Topic Bootstrap: fresh RNG(42) per test origin, shared index matrix across M0–M3.
        rng = np.random.default_rng(BOOTSTRAP_SEED)
        boot_idx = rng.integers(0, n_test, size=(BOOTSTRAP_B, n_test))
        if boot_idx.shape != (BOOTSTRAP_B, n_test):
            raise RuntimeError(f"Unexpected bootstrap matrix shape: {boot_idx.shape}")

        npz_rel_key = f"bootstrap/bootstrap_indices_{orig_str}.npz"
        npz_path = boot_dir / f"bootstrap_indices_{orig_str}.npz"
        save_deterministic_npz(npz_path, {"indices": boot_idx})
        outputs_meta[npz_rel_key] = {
            "relative_path": to_repo_posix(npz_path, out_dir),
            "role": "bootstrap_index_matrix",
            "shape": [int(boot_idx.shape[0]), int(boot_idx.shape[1])],
            "dtype": str(boot_idx.dtype),
            "sha256": sha256_file(npz_path),
        }

        observed_maes: dict[str, float] = {}
        boot_maes: dict[str, np.ndarray] = {}
        model_ci_meta: dict[str, Any] = {}

        for m in PRIMARY_MODELS:
            mae_obs = float(np.mean(abs_errs[m]))
            mae_draws = np.mean(abs_errs[m][boot_idx], axis=1, dtype=np.float64)
            ci_low, ci_high = np.percentile(
                mae_draws, PERCENTILE_LEVELS, method=PERCENTILE_METHOD
            )
            observed_maes[m] = mae_obs
            boot_maes[m] = mae_draws

            mae_summary_rows.append(
                {
                    "test_origin": test_origin,
                    "experiment_id": cfg["experiment_id"],
                    "model": m,
                    "n_features": int(len(LOCKED_MODEL_SPECS[m])),
                    "fitted": m != "M0",
                    "selected_alpha": selected_alphas[m] if selected_alphas[m] is not None else "",
                    "n_test": n_test,
                    "mae": mae_obs,
                    "ci_95_low": float(ci_low),
                    "ci_95_high": float(ci_high),
                    "ci_95_width": float(ci_high - ci_low),
                    "bootstrap_b": BOOTSTRAP_B,
                    "bootstrap_seed": BOOTSTRAP_SEED,
                }
            )
            mae_ci_rows.append(
                {
                    "test_origin": test_origin,
                    "experiment_id": cfg["experiment_id"],
                    "model": m,
                    "n_test": n_test,
                    "mae_observed": mae_obs,
                    "boot_mean_mae": float(np.mean(mae_draws)),
                    "boot_sd_mae": float(np.std(mae_draws, ddof=1)),
                    "boot_median_mae": float(np.median(mae_draws)),
                    "ci_95_low": float(ci_low),
                    "ci_95_high": float(ci_high),
                    "ci_95_width": float(ci_high - ci_low),
                    "bootstrap_b": BOOTSTRAP_B,
                    "bootstrap_seed": BOOTSTRAP_SEED,
                    "percentile_method": PERCENTILE_METHOD,
                }
            )
            model_ci_meta[m] = {
                "n_features": int(len(LOCKED_MODEL_SPECS[m])),
                "selected_alpha": selected_alphas[m],
                "mae": mae_obs,
                "boot_mean_mae": float(np.mean(mae_draws)),
                "boot_sd_mae": float(np.std(mae_draws, ddof=1)),
                "ci_95_low": float(ci_low),
                "ci_95_high": float(ci_high),
            }

        paired_meta: dict[str, Any] = {}
        for comp_id, aug_m, ref_m, desc in PRESPECIFIED_COMPARISONS:
            delta_obs = float(observed_maes[aug_m] - observed_maes[ref_m])
            delta_draws = boot_maes[aug_m] - boot_maes[ref_m]
            ci_low, ci_high = np.percentile(
                delta_draws, PERCENTILE_LEVELS, method=PERCENTILE_METHOD
            )
            excludes_zero = bool((ci_high < 0.0) or (ci_low > 0.0))
            pct_neg = float(np.mean(delta_draws < 0.0) * 100.0)
            direction_text = interpret_delta_direction(delta_obs, float(ci_low), float(ci_high))

            paired_diff_rows.append(
                {
                    "test_origin": test_origin,
                    "experiment_id": cfg["experiment_id"],
                    "comparison_id": comp_id,
                    "comparison_label": f"{aug_m} vs {ref_m}",
                    "augmented_model": aug_m,
                    "reference_model": ref_m,
                    "definition": f"MAE({aug_m}) - MAE({ref_m})",
                    "description": desc,
                    "n_test": n_test,
                    "mae_reference": observed_maes[ref_m],
                    "mae_augmented": observed_maes[aug_m],
                    "delta_mae_observed": delta_obs,
                    "ci_95_low": float(ci_low),
                    "ci_95_high": float(ci_high),
                    "ci_95_excludes_zero": excludes_zero,
                    "direction_interpretation": direction_text,
                }
            )
            paired_ci_rows.append(
                {
                    "test_origin": test_origin,
                    "experiment_id": cfg["experiment_id"],
                    "comparison_id": comp_id,
                    "comparison_label": f"{aug_m} vs {ref_m}",
                    "augmented_model": aug_m,
                    "reference_model": ref_m,
                    "n_test": n_test,
                    "delta_mae_observed": delta_obs,
                    "boot_mean_delta": float(np.mean(delta_draws)),
                    "boot_sd_delta": float(np.std(delta_draws, ddof=1)),
                    "boot_median_delta": float(np.median(delta_draws)),
                    "ci_95_low": float(ci_low),
                    "ci_95_high": float(ci_high),
                    "ci_95_width": float(ci_high - ci_low),
                    "ci_95_excludes_zero": excludes_zero,
                    "pct_bootstrap_draws_negative": pct_neg,
                    "bootstrap_b": BOOTSTRAP_B,
                    "bootstrap_seed": BOOTSTRAP_SEED,
                    "percentile_method": PERCENTILE_METHOD,
                }
            )
            paired_meta[comp_id] = {
                "augmented_model": aug_m,
                "reference_model": ref_m,
                "mae_reference": observed_maes[ref_m],
                "mae_augmented": observed_maes[aug_m],
                "delta_mae_observed": delta_obs,
                "boot_mean_delta": float(np.mean(delta_draws)),
                "boot_sd_delta": float(np.std(delta_draws, ddof=1)),
                "ci_95_low": float(ci_low),
                "ci_95_high": float(ci_high),
                "ci_95_excludes_zero": excludes_zero,
                "pct_bootstrap_draws_negative": pct_neg,
                "direction_interpretation": direction_text,
            }

        bootstrap_meta["experiments"][orig_str] = {
            "test_origin": test_origin,
            "n_test": n_test,
            "index_matrix_relative_path": to_repo_posix(npz_path, out_dir),
            "index_matrix_sha256": outputs_meta[npz_rel_key]["sha256"],
            "index_matrix_shape": [BOOTSTRAP_B, n_test],
            "index_min": int(boot_idx.min()),
            "index_max": int(boot_idx.max()),
        }

        experiments_meta[orig_str] = {
            "experiment_id": cfg["experiment_id"],
            "test_origin": test_origin,
            "train_origins": cfg["train_origins"],
            "target_window": cfg["target_window"],
            "n_test": n_test,
            "predictions_relative_path": to_repo_posix(pred_path, out_dir),
            "predictions_sha256": outputs_meta[pred_rel_key]["sha256"],
            "models": model_ci_meta,
            "paired_comparisons": paired_meta,
        }

    # Write bootstrap_metadata.json and metrics/*.csv files.
    boot_meta_path = boot_dir / "bootstrap_metadata.json"
    boot_meta_path.write_text(json.dumps(bootstrap_meta, indent=2) + "\n", encoding="utf-8", newline="\n")
    outputs_meta["bootstrap/bootstrap_metadata.json"] = {
        "relative_path": to_repo_posix(boot_meta_path, out_dir),
        "role": "bootstrap_metadata",
        "sha256": sha256_file(boot_meta_path),
    }

    metric_tables: list[tuple[str, str, list[dict[str, Any]]]] = [
        ("metrics/mae_summary.csv", "mae_summary", mae_summary_rows),
        ("metrics/mae_bootstrap_ci.csv", "mae_bootstrap_ci", mae_ci_rows),
        ("metrics/paired_mae_differences.csv", "paired_mae_differences", paired_diff_rows),
        ("metrics/paired_mae_bootstrap_ci.csv", "paired_mae_bootstrap_ci", paired_ci_rows),
    ]
    for rel_key, role, rows in metric_tables:
        df_m = pd.DataFrame(rows)
        m_path = out_dir / rel_key
        df_m.to_csv(m_path, index=False, lineterminator="\n")
        outputs_meta[rel_key] = {
            "relative_path": to_repo_posix(m_path, out_dir),
            "role": role,
            "rows": int(df_m.shape[0]),
            "columns": int(df_m.shape[1]),
            "sha256": sha256_file(m_path),
        }

    # Build Chapter 5 thesis tables and figures strictly from written Stage 3.4 metrics.
    if not ASSETS_SCRIPT_PATH.is_file():
        raise FileNotFoundError(f"Missing thesis assets generator: {ASSETS_SCRIPT_PATH.name}")
    subprocess.run(
        [sys.executable, "-B", str(ASSETS_SCRIPT_PATH), "--eval-dir", str(out_dir)],
        cwd=str(REPO_ROOT),
        check=True,
    )
    thesis_asset_specs = [
        ("thesis_assets/tables/table_5_1_rq2_mae_performance.csv", "thesis_table_csv"),
        ("thesis_assets/tables/table_5_1_rq2_mae_performance.tex", "thesis_table_tex"),
        ("thesis_assets/tables/table_5_2_rq2_paired_comparisons.csv", "thesis_table_csv"),
        ("thesis_assets/tables/table_5_2_rq2_paired_comparisons.tex", "thesis_table_tex"),
        ("thesis_assets/figures/fig_5_1_rq2_mae_comparison.pdf", "thesis_figure_pdf"),
        ("thesis_assets/figures/fig_5_1_rq2_mae_comparison.svg", "thesis_figure_svg"),
        ("thesis_assets/figures/fig_5_1_rq2_mae_comparison.png", "thesis_figure_png"),
        ("thesis_assets/figures/fig_5_2_rq2_paired_mae_differences.pdf", "thesis_figure_pdf"),
        ("thesis_assets/figures/fig_5_2_rq2_paired_mae_differences.svg", "thesis_figure_svg"),
        ("thesis_assets/figures/fig_5_2_rq2_paired_mae_differences.png", "thesis_figure_png"),
        ("thesis_assets/README.md", "thesis_assets_readme"),
    ]
    for rel_key, role in thesis_asset_specs:
        asset_path = out_dir / rel_key
        if not asset_path.is_file():
            raise FileNotFoundError(f"Missing generated thesis asset: {rel_key}")
        outputs_meta[rel_key] = {
            "relative_path": to_repo_posix(asset_path, out_dir),
            "role": role,
            "sha256": sha256_file(asset_path),
        }

    # Assemble Stage 3.4 manifest.
    manifest: dict[str, Any] = {
        "stage": "3.4",
        "title": "RQ2 Held-Out Test Evaluation (M0–M3)",
        "execution_timestamp_utc": timestamp_utc,
        "git_commit_hash": git_hash,
        "environment": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "scipy": scipy.__version__,
            "scikit_learn": sklearn.__version__,
            "joblib": joblib.__version__,
            "sklearn_min_required": "1.6",
        },
        "validation_status": {
            "preflight_passed": True,
            "refit_occurred": False,
            "retuning_occurred": False,
            "ranking_evaluated": False,
            "alternative_specs_evaluated": False,
        },
        "upstream_references": {
            "stage3_2_manifest": {
                "relative_path": to_repo_posix(STAGE3_2_MANIFEST_PATH),
                "sha256": LOCKED_STAGE3_2_MANIFEST_SHA256,
            },
            "stage3_3_manifest": {
                "relative_path": to_repo_posix(STAGE3_3_MANIFEST_PATH),
                "sha256": sha256_file(STAGE3_3_MANIFEST_PATH),
            },
            "stage3_3_summary": {
                "relative_path": to_repo_posix(STAGE3_3_SUMMARY_PATH),
                "sha256": sha256_file(STAGE3_3_SUMMARY_PATH),
            },
            "test_inputs": {
                orig: {
                    "features_path": to_repo_posix(SPLITS_DIR / cfg["features_file"]),
                    "features_sha256": cfg["features_sha256"],
                    "targets_path": to_repo_posix(SPLITS_DIR / cfg["targets_file"]),
                    "targets_sha256": cfg["targets_sha256"],
                    "n_test": cfg["expected_rows"],
                }
                for orig, cfg in LOCKED_TEST_EXPERIMENTS.items()
            },
            "stage3_3_pipelines": {
                orig: {
                    m: {
                        "relative_path": stage3_3_manifest["experiments"][orig]["models"][m][
                            "pipeline_relative_path"
                        ],
                        "sha256": LOCKED_PIPELINE_SHA256[orig][m],
                        "selected_alpha": stage3_3_manifest["experiments"][orig]["models"][m][
                            "selected_alpha"
                        ],
                    }
                    for m in RIDGE_MODELS
                }
                for orig in ("2018", "2021")
            },
        },
        "model_specifications": {
            m: {
                "description": MODEL_DESCRIPTIONS[m],
                "feature_columns": LOCKED_MODEL_SPECS[m],
                "n_features": int(len(LOCKED_MODEL_SPECS[m])),
                "fitted": m != "M0",
            }
            for m in PRIMARY_MODELS
        },
        "evaluation_protocol": {
            "research_question": "RQ2",
            "metric": "MAE = mean(abs(y_true - y_pred))",
            "pooled_test_estimate": False,
            "bootstrap": {
                "replicates_B": BOOTSTRAP_B,
                "random_seed": BOOTSTRAP_SEED,
                "rng_constructor": "np.random.default_rng(42)",
                "percentile_levels": PERCENTILE_LEVELS,
                "percentile_method": PERCENTILE_METHOD,
                "paired_design": "Single shared (5000, N) index matrix across M0–M3 per origin",
                "delta_definition": "MAE(augmented) - MAE(reference)",
            },
        },
        "experiments": experiments_meta,
        "outputs": outputs_meta,
        "source_scripts": {
            "builder": {
                "relative_path": to_repo_posix(BUILDER_SCRIPT_PATH),
                "sha256": sha256_file(BUILDER_SCRIPT_PATH),
            },
            "auditor": {
                "relative_path": to_repo_posix(AUDIT_SCRIPT_PATH),
                "sha256": sha256_file(AUDIT_SCRIPT_PATH),
            },
            "thesis_assets_generator": {
                "relative_path": to_repo_posix(ASSETS_SCRIPT_PATH),
                "sha256": sha256_file(ASSETS_SCRIPT_PATH),
            },
        },
        "boundary_assertions": {
            "strict_stage3_4_rq2_only": True,
            "models_refitted": False,
            "scalers_refitted": False,
            "alpha_retuned": False,
            "candidate_pool_ranked": False,
            "alternative_specs_evaluated": False,
        },
    }

    manifest_path = out_dir / "stage3_4_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
    return manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Execute Stage 3.4 RQ2 held-out test evaluation (M0–M3 ONLY)."
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=DEFAULT_OUT_DIR,
        help="Output directory for Stage 3.4 evaluation artifacts.",
    )
    parser.add_argument(
        "--timestamp-utc",
        type=str,
        default=None,
        help="Optional fixed ISO8601 UTC timestamp for deterministic testing.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    manifest = build_stage3_4(args.out_dir, execution_timestamp_utc=args.timestamp_utc)
    for orig_str in ("2018", "2021"):
        exp = manifest["experiments"][orig_str]
        print(f"[Stage 3.4] Test Origin {orig_str} (N={exp['n_test']}):")
        for m in PRIMARY_MODELS:
            info = exp["models"][m]
            print(
                f"  {m}: MAE={info['mae']:.6f} "
                f"(95% CI [{info['ci_95_low']:.6f}, {info['ci_95_high']:.6f}])"
            )
        for comp_id, aug_m, ref_m, _ in PRESPECIFIED_COMPARISONS:
            c = exp["paired_comparisons"][comp_id]
            print(
                f"  {aug_m} vs {ref_m}: Delta_MAE={c['delta_mae_observed']:+.6f} "
                f"(95% CI [{c['ci_95_low']:+.6f}, {c['ci_95_high']:+.6f}])"
            )
    print(f"[Stage 3.4] Manifest written to {to_repo_posix(args.out_dir / 'stage3_4_manifest.json')}")


if __name__ == "__main__":
    main()
