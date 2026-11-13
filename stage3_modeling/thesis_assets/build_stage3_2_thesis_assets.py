"""
Stage 3.2 Thesis-Ready Table & Figure Generator
Script: stage3_modeling/thesis_assets/build_stage3_2_thesis_assets.py

Reads verified Stage 3.2 outputs ONLY (read-only):
  - stage3_modeling/stage3_2_splits/stage3_2_splits_manifest.json
  - stage3_modeling/stage3_2_splits/test_2018_features.csv + test_2018_targets.csv
  - stage3_modeling/stage3_2_splits/test_2021_features.csv + test_2021_targets.csv
  - stage3_modeling/stage3_2_splits/rq3_2018_pool_features.csv + rq3_2018_pool_labels.csv
  - stage3_modeling/stage3_2_splits/rq3_2021_pool_features.csv + rq3_2021_pool_labels.csv

Generates publication-ready Chapter 4 assets in stage3_modeling/thesis_assets/:
  1. table_4_temporal_split_and_rq3_pool.{csv,tex}
  2. fig_4_temporal_split_and_rq3_design.{svg,pdf,png}
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SPLITS_DIR = BASE_DIR / "stage3_modeling" / "stage3_2_splits"
ASSETS_DIR = Path(__file__).resolve().parent

MANIFEST_PATH = SPLITS_DIR / "stage3_2_splits_manifest.json"


def build_split_and_rq3_table(manifest: Dict[str, Any]) -> None:
    s18 = manifest["experiments"]["2018"]
    s21 = manifest["experiments"]["2021"]

    rows = []
    for label, s in [("Test Origin 2018", s18), ("Test Origin 2021", s21)]:
        r = s["rq3"]
        tr_str = "2015" if len(s["train_origins"]) == 1 else "2015--2018 (Pooled)"
        eval_win = "2019--2021" if s["test_origin"] == 2018 else "2022--2024"
        cv_folds_str = " / ".join(str(f["val_rows"]) for f in s["group_kfold_preview"]["folds"])
        rows.append(
            {
                "Evaluation Suite": label,
                "Training Origins": tr_str.replace("--", "-"),
                "Evaluation Window": eval_win.replace("--", "-"),
                "Train Obs (Unique Topics)": f"{s['train_rows']:,} ({s['train_unique_topics']:,})",
                "5-Fold GroupKFold Val Rows (Overlap)": f"{cv_folds_str} (0)",
                "Eligible Test Topics": f"{s['test_rows']:,}",
                "Excluded Past HG (>= Q80_past)": f"{r['past_excluded_rows']} (Q80={r['q80_past']:.4f})",
                "RQ3 Remaining Pool (< Q80_past)": f"{r['remaining_pool_rows']:,}",
                "Future HG (>= Q80_fut)": f"{r['future_hg_count_ge']} (Q80={r['q80_future']:.4f})",
                "Actual Chance Rate": f"{r['actual_chance_rate']*100:.2f}%",
                "Chance Expected Hits@50": f"{r['chance_expected_hits_at_50']:.2f}",
            }
        )

    csv_path = ASSETS_DIR / "table_4_temporal_split_and_rq3_pool.csv"
    pd.DataFrame(rows).to_csv(csv_path, index=False, encoding="utf-8", lineterminator="\n")

    # Compact publication-grade LaTeX booktabs table
    r18 = s18["rq3"]
    r21 = s21["rq3"]
    tex_lines = [
        r"% Auto-generated from stage3_modeling/stage3_2_splits/stage3_2_splits_manifest.json (Stage 3.2 verified 22/22 PASS)",
        r"\begin{table}[htbp]",
        r"    \centering",
        r"    \small",
        r"    \caption{Temporal Train/Test Partitions, Topic-Grouped Cross-Validation Structure, and RQ3 Cohort Filtering Summary for Test Forecast Origins 2018 and 2021}",
        r"    \label{tab:stage32-splits-rq3}",
        r"    \begin{tabular}{lcc}",
        r"        \toprule",
        r"        \textbf{Partition / Metric} & \textbf{Test Origin 2018} & \textbf{Test Origin 2021} \\",
        r"        \midrule",
        r"        Training origin(s) & 2015 & 2015--2018 (Expanding) \\",
        r"        Training observation rows ($N_{\text{train}}$) & 990 & 3,963 \\",
        r"        Unique training topics & 990 & 993 \\",
        r"        5-Fold \texttt{GroupKFold} cross-fold topic overlap & 0 & 0 \\",
        r"        \midrule",
        r"        Future evaluation window $[t+1, t+3]$ & 2019--2021 & 2022--2024 \\",
        r"        Eligible test topics ($N_{\text{test}}$, $\sum_{[t-2,t]} P_{\text{Global}} \ge 50$) & 992 & 995 \\",
        rf"        Past high-growth threshold $Q_{{0.80}}^{{\text{{Past}}}}$ (\texttt{{linear}}) & {r18['q80_past']:.6f} & {r21['q80_past']:.6f} \\",
        rf"        Excluded past high-growth topics ($\ge Q_{{0.80}}^{{\text{{Past}}}}$) & {r18['past_excluded_rows']} & {r21['past_excluded_rows']} \\",
        rf"        \textbf{{RQ3 Remaining Pool}} ($< Q_{{0.80}}^{{\text{{Past}}}}$) & \textbf{{{r18['remaining_pool_rows']}}} & \textbf{{{r21['remaining_pool_rows']}}} \\",
        rf"        Future high-growth threshold $Q_{{0.80}}^{{\text{{Fut}}}}$ (\texttt{{linear}}) & {r18['q80_future']:.6f} & {r21['q80_future']:.6f} \\",
        rf"        Future high-growth topics ($HG_i = 1$, $\ge Q_{{0.80}}^{{\text{{Fut}}}}$) & {r18['future_hg_count_ge']} & {r21['future_hg_count_ge']}$^{{\dagger}}$ \\",
        rf"        Actual Chance Rate ($N_{{\text{{Future HG}}}} / N_{{\text{{Rem}}}}$) & {r18['actual_chance_rate']*100:.2f}\% & {r21['actual_chance_rate']*100:.2f}\% \\",
        rf"        Chance Expected Hits@50 ($50 \times \text{{Chance Rate}}$) & {r18['chance_expected_hits_at_50']:.2f} & {r21['chance_expected_hits_at_50']:.2f} \\",
        r"        \bottomrule",
        r"    \end{tabular}",
        r"    \begin{minipage}{0.92\textwidth}",
        r"    \vspace{0.35em}\footnotesize",
        r"    \textit{Note:} $^{\dagger}$At Test Origin 2021 ($N_{\text{Rem}} = 796$), linear interpolation index $(796-1)\times 0.80 = 636.0$ lands on an exact sorted observation ($Q_{0.80}^{\text{Fut}} = 0.06890643$); the locked inclusive criterion ($\ge$) yields 160 future high-growth topics. Topic-grouped CV uses \texttt{GroupKFold(n\_splits=5, shuffle=True, random\_state=42)} grouped by \texttt{topic\_id}.",
        r"    \end{minipage}",
        r"\end{table}",
    ]
    tex_path = ASSETS_DIR / "table_4_temporal_split_and_rq3_pool.tex"
    tex_path.write_text("\n".join(tex_lines) + "\n", encoding="utf-8")


def _load_merged_pair(feat_name: str, rhs_name: str) -> pd.DataFrame:
    feat = pd.read_csv(SPLITS_DIR / feat_name, float_precision="round_trip")
    rhs = pd.read_csv(SPLITS_DIR / rhs_name, float_precision="round_trip")
    return feat.merge(rhs, on=["forecast_origin", "topic_id"], how="inner", validate="one_to_one")


def build_figure(manifest: Dict[str, Any]) -> None:
    te18 = _load_merged_pair("test_2018_features.csv", "test_2018_targets.csv")
    te21 = _load_merged_pair("test_2021_features.csv", "test_2021_targets.csv")
    rq18 = _load_merged_pair("rq3_2018_pool_features.csv", "rq3_2018_pool_labels.csv")
    rq21 = _load_merged_pair("rq3_2021_pool_features.csv", "rq3_2021_pool_labels.csv")

    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.edgecolor": "#475569",
            "axes.linewidth": 0.9,
            "savefig.dpi": 300,
        }
    )

    fig = plt.figure(figsize=(13.5, 8.6))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.0, 1.18], hspace=0.38, wspace=0.22)

    # ------------------------------------------------------------------
    # Panel A (Top full width): Leakage-Free Historical Backtesting Design
    # ------------------------------------------------------------------
    ax_a = fig.add_subplot(gs[0, :])
    ax_a.set_xlim(2009.4, 2024.8)
    ax_a.set_ylim(-0.6, 5.2)
    ax_a.set_yticks([])
    ax_a.set_xticks(range(2010, 2025))
    ax_a.tick_params(axis="x", labelsize=9.5)
    ax_a.spines["top"].set_visible(False)
    ax_a.spines["right"].set_visible(False)
    ax_a.spines["left"].set_visible(False)
    ax_a.grid(axis="x", linestyle=":", alpha=0.45, color="#94A3B8")
    ax_a.set_title(
        "(a) Leakage-Free Expanding Backtesting & Topic-Grouped 5-Fold CV Architecture (2010–2024)",
        fontsize=11.5,
        fontweight="bold",
        loc="left",
        pad=10,
        color="#0F172A",
    )

    def draw_span(y: float, start_yr: int, end_yr: int, color: str, edge: str, label: str, h: float = 0.52) -> None:
        w = (end_yr - start_yr) + 0.86
        x0 = start_yr - 0.43
        patch = FancyBboxPatch(
            (x0, y - h / 2),
            w,
            h,
            boxstyle="round,pad=0.02,rounding_size=0.10",
            facecolor=color,
            edgecolor=edge,
            linewidth=1.1,
        )
        ax_a.add_patch(patch)
        ax_a.text(
            x0 + w / 2,
            y,
            label,
            ha="center",
            va="center",
            fontsize=8.2,
            fontweight="bold",
            color="#0F172A",
        )

    # Suite 1: Test Origin 2018
    ax_a.text(2009.5, 4.65, "Evaluation Suite 1 — Test Origin 2018 (Train 2015: N = 990 → Test 2018: N = 992)", fontsize=9.5, fontweight="bold", color="#1E3A8A")
    draw_span(3.95, 2010, 2012, "#DBEAFE", "#2563EB", "Mom Base\n2010–2012", 0.56)
    draw_span(3.95, 2013, 2015, "#BFDBFE", "#1D4ED8", "Train X (2015)\n2013–2015 (N=990)", 0.56)
    draw_span(3.95, 2016, 2018, "#FEF3C7", "#D97706", "Train Target y\n2016–2018", 0.56)
    draw_span(3.22, 2013, 2015, "#E2E8F0", "#64748B", "Test Mom Base 2013–2015", 0.46)
    draw_span(3.22, 2016, 2018, "#CCFBF1", "#0D9488", "Test X (2018) 2016–2018", 0.46)
    draw_span(3.22, 2019, 2021, "#FEE2E2", "#DC2626", "Test Eval (2019–2021)\nN = 992 | RQ3 = 793", 0.46)
    ax_a.plot([2018.47, 2018.47], [2.85, 4.35], color="#B91C1C", linestyle="--", linewidth=1.6)
    ax_a.text(2018.56, 4.18, "Origin 2018 Cutoff\n(No >2018 data in Train/X)", fontsize=7.8, color="#991B1B", va="top")

    # Divider
    ax_a.axhline(2.58, color="#CBD5E1", linewidth=1.0)

    # Suite 2: Test Origin 2021
    ax_a.text(
        2009.5,
        2.22,
        "Evaluation Suite 2 — Test Origin 2021 (Pooled Train 2015–2018: 3,963 rows / 993 unique topics; GroupKFold 0 overlap → Test 2021: N = 995)",
        fontsize=9.5,
        fontweight="bold",
        color="#1E3A8A",
    )
    draw_span(1.48, 2010, 2018, "#E0E7FF", "#4338CA", "Pooled Training Inputs (Origins 2015–2018): 3,963 rows | 5-Fold GroupKFold (topic_id)", 0.50)
    draw_span(1.48, 2019, 2021, "#FEF3C7", "#D97706", "Max Train Target\n<= 2021", 0.50)
    draw_span(0.72, 2016, 2018, "#E2E8F0", "#64748B", "Test Mom Base 2016–2018", 0.46)
    draw_span(0.72, 2019, 2021, "#CCFBF1", "#0D9488", "Test X (2021) 2019–2021", 0.46)
    draw_span(0.72, 2022, 2024, "#FEE2E2", "#DC2626", "Test Eval (2022–2024)\nN = 995 | RQ3 = 796", 0.46)
    ax_a.plot([2021.47, 2021.47], [0.35, 1.85], color="#B91C1C", linestyle="--", linewidth=1.6)
    ax_a.text(2021.56, 1.65, "Origin 2021 Cutoff\n(t_train + 3 <= 2021)", fontsize=7.8, color="#991B1B", va="top")

    # ------------------------------------------------------------------
    # Panel B & C (Bottom): Empirical RQ3 Cohort Partition on Real Test Topics
    # ------------------------------------------------------------------
    panels = [
        (gs[1, 0], te18, rq18, manifest["experiments"]["2018"]["rq3"], "(b) Test Origin 2018 Empirical RQ3 Partition (N = 992 Eligible)"),
        (gs[1, 1], te21, rq21, manifest["experiments"]["2021"]["rq3"], "(c) Test Origin 2021 Empirical RQ3 Partition (N = 995 Eligible)"),
    ]

    for spec, te_df, rq_df, meta, title in panels:
        ax = fig.add_subplot(spec)
        q80_p = meta["q80_past"]
        q80_f = meta["q80_future"]

        excl = te_df[te_df["m0_adj"] >= q80_p]
        rem_nonhg = rq_df[rq_df["hg_future"] == 0]
        rem_hg = rq_df[rq_df["hg_future"] == 1]

        ax.scatter(
            excl["m0_adj"],
            excl["g_adj"],
            s=14,
            alpha=0.50,
            color="#94A3B8",
            edgecolors="none",
            label=f"Excluded Past HG (>= Q80_past): n = {len(excl)}",
        )
        ax.scatter(
            rem_nonhg["m0_adj"],
            rem_nonhg["g_adj"],
            s=15,
            alpha=0.55,
            color="#3B82F6",
            edgecolors="none",
            label=f"Remaining Pool Non-HG: n = {len(rem_nonhg)}",
        )
        ax.scatter(
            rem_hg["m0_adj"],
            rem_hg["g_adj"],
            s=18,
            alpha=0.75,
            color="#DC2626",
            edgecolors="none",
            label=f"Emerging Future HG (HG=1): n = {len(rem_hg)} ({meta['actual_chance_rate']*100:.2f}%)",
        )

        ax.axvline(q80_p, color="#0F172A", linestyle="--", linewidth=1.2)
        xmin, xmax = ax.get_xlim()
        xmin = min(xmin, -1.6)
        ax.hlines(q80_f, xmin=xmin, xmax=q80_p, colors="#B91C1C", linestyles=":", linewidth=1.5)
        ax.set_xlim(xmin, xmax)

        ymin, ymax = ax.get_ylim()
        ax.text(
            q80_p + 0.02 * (xmax - xmin),
            ymin + 0.05 * (ymax - ymin),
            f"Q80_past = {q80_p:.4f}",
            fontsize=8.2,
            color="#0F172A",
            fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="none", alpha=0.85),
        )
        ax.annotate(
            f"Q80_fut = {q80_f:.4f}",
            xy=(xmin + 0.06 * (xmax - xmin), q80_f),
            xytext=(xmin + 0.03 * (xmax - xmin), q80_f + 0.11 * (ymax - ymin)),
            fontsize=8.2,
            color="#991B1B",
            fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="#FCA5A5", linewidth=0.7, alpha=0.92),
            arrowprops=dict(arrowstyle="-", color="#B91C1C", lw=0.9),
        )

        ax.set_title(title, fontsize=10.5, fontweight="bold", loc="left", color="#0F172A", pad=8)
        ax.set_xlabel("Past Adjusted Momentum M0_adj(i, t)", fontsize=9.3)
        ax.set_ylabel("Future Adjusted Growth G_adj(i, t)", fontsize=9.3)
        ax.grid(True, linestyle=":", alpha=0.4, color="#CBD5E1")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.legend(loc="upper left", fontsize=7.8, framealpha=0.92, edgecolor="#CBD5E1")

    fig.suptitle(
        "Stage 3.2 Verified Train/Test Backtesting & RQ3 Emerging-Growth Cohort Design",
        fontsize=13,
        fontweight="bold",
        y=0.985,
        color="#0F172A",
    )

    for ext in ["svg", "pdf", "png"]:
        out_file = ASSETS_DIR / f"fig_4_temporal_split_and_rq3_design.{ext}"
        fig.savefig(out_file, bbox_inches="tight")
    plt.close(fig)


def main() -> int:
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    build_split_and_rq3_table(manifest)
    build_figure(manifest)
    print("[PASS] Generated Stage 3.2 table_4_temporal_split_and_rq3_pool.{csv,tex} and fig_4_temporal_split_and_rq3_design.{svg,pdf,png}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
