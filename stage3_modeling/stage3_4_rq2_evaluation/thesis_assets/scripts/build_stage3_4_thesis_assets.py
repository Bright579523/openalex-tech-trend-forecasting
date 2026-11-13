#!/usr/bin/env python3
"""Stage 3.4 Thesis-Ready Table & Figure Generator (Chapter 5, RQ2 ONLY).

Reads strictly verified Stage 3.4 metric CSVs and manifest (read-only) to produce:
  1. thesis_assets/tables/table_5_1_rq2_mae_performance.{csv,tex}
  2. thesis_assets/tables/table_5_2_rq2_paired_comparisons.{csv,tex}
  3. thesis_assets/figures/fig_5_1_rq2_mae_comparison.{pdf,svg,png}
  4. thesis_assets/figures/fig_5_2_rq2_paired_mae_differences.{pdf,svg,png}
  5. thesis_assets/README.md (with live preview tables derived from audited CSVs)
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

DEFAULT_EVAL_DIR = Path(__file__).resolve().parent.parent.parent

MODEL_ORDER = ["M0", "M1", "M2", "M3"]
MODEL_LABELS_SHORT = {
    "M0": "M0\n(Momentum)",
    "M1": "M1\n(+Global)",
    "M2": "M2\n(+Counts)",
    "M3": "M3\n(+RCA)",
}
MODEL_PREDICTOR_NOTE = {
    "M0": "M0_adj only (unfitted)",
    "M1": "M0_adj + ln_global (p=2)",
    "M2": "M1 + DE/CN/JP log counts (p=5)",
    "M3": "M2 + DE/CN/JP raw RCA (p=8)",
}
MODEL_COLORS = {
    "M0": "#475569",  # Slate
    "M1": "#2563EB",  # Blue
    "M2": "#0D9488",  # Teal
    "M3": "#D97706",  # Amber
}
COMPARISON_ORDER = ["M1_vs_M0", "M2_vs_M1", "M3_vs_M2", "M3_vs_M0"]
COMPARISON_LABELS = {
    "M1_vs_M0": "M1 vs M0 (+Global History)",
    "M2_vs_M1": "M2 vs M1 (+Country Counts)",
    "M3_vs_M2": "M3 vs M2 (+National RCA)",
    "M3_vs_M0": "M3 vs M0 (Overall vs M0)",
}


def save_deterministic_figure(fig: plt.Figure, stem_path: Path) -> None:
    """Save PDF, SVG, and PNG deterministically."""
    stem_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(
        stem_path.with_suffix(".pdf"),
        bbox_inches="tight",
        metadata={"Creator": "Stage 3.4 Pipeline", "Producer": "Matplotlib", "CreationDate": None},
    )
    fig.savefig(
        stem_path.with_suffix(".svg"),
        bbox_inches="tight",
        metadata={"Date": None, "Creator": "Stage 3.4 Pipeline"},
    )
    fig.savefig(
        stem_path.with_suffix(".png"),
        dpi=300,
        bbox_inches="tight",
        metadata={"Software": "Matplotlib"},
    )


def build_table_5_1(mae_df: pd.DataFrame, tables_dir: Path) -> pd.DataFrame:
    """Create Table 5.1 (Held-Out Forecasting Performance MAE & 95% CI)."""
    rows = []
    for orig in (2018, 2021):
        sub = mae_df[mae_df["test_origin"] == orig].set_index("model").loc[MODEL_ORDER]
        eval_win = "2019–2021" if orig == 2018 else "2022–2024"
        exp_label = "Experiment A (2018)" if orig == 2018 else "Experiment B (2021)"
        for m in MODEL_ORDER:
            r = sub.loc[m]
            alpha_str = "Unfitted" if not bool(r["fitted"]) else f"{float(r['selected_alpha']):.6g}"
            rows.append(
                {
                    "Experiment": exp_label,
                    "Test Origin": int(orig),
                    "Evaluation Window": eval_win,
                    "Model": m,
                    "Specification": MODEL_PREDICTOR_NOTE[m],
                    "Selected alpha": alpha_str,
                    "Test N": int(r["n_test"]),
                    "Test MAE": float(r["mae"]),
                    "CI 95% Low": float(r["ci_95_low"]),
                    "CI 95% High": float(r["ci_95_high"]),
                    "MAE (95% Bootstrap CI)": (
                        f"{float(r['mae']):.4f} [{float(r['ci_95_low']):.4f}, {float(r['ci_95_high']):.4f}]"
                    ),
                }
            )

    t_df = pd.DataFrame(rows)
    t_df.to_csv(tables_dir / "table_5_1_rq2_mae_performance.csv", index=False, lineterminator="\n")

    tex_lines = [
        r"% Auto-generated strictly from Stage 3.4 audited metrics/mae_summary.csv",
        r"\begin{table}[htbp]",
        r"    \centering",
        r"    \small",
        r"    \caption{Held-Out Forecasting Accuracy (MAE) with Conditional 95\% Topic Bootstrap Confidence Intervals across Test Forecast Origins 2018 and 2021}",
        r"    \label{tab:rq2-mae-performance}",
        r"    \begin{tabular}{llcccc}",
        r"        \toprule",
        r"        \textbf{Test Origin (Window)} & \textbf{Model} & \textbf{Predictors ($p$)} & \textbf{Tuned $\alpha$} & \textbf{$N_{\text{test}}$} & \textbf{Test MAE [95\% CI]} \\",
        r"        \midrule",
    ]
    for idx_orig, orig in enumerate((2018, 2021)):
        sub = t_df[t_df["Test Origin"] == orig]
        win = "2019--2021" if orig == 2018 else "2022--2024"
        for i, (_, row) in enumerate(sub.iterrows()):
            orig_col = f"{orig} ({win})" if i == 0 else ""
            m = row["Model"]
            p_val = "0 (benchmark)" if m == "M0" else ("2" if m == "M1" else ("5" if m == "M2" else "8"))
            alpha_tex = r"\textemdash" if row["Selected alpha"] == "Unfitted" else row["Selected alpha"]
            mae_str = f"{row['Test MAE']:.4f} [{row['CI 95% Low']:.4f}, {row['CI 95% High']:.4f}]"
            tex_lines.append(
                f"        {orig_col} & {m} & {p_val} & {alpha_tex} & {row['Test N']} & {mae_str} \\\\"
            )
        if idx_orig == 0:
            tex_lines.append(r"        \midrule")

    tex_lines.extend(
        [
            r"        \bottomrule",
            r"    \end{tabular}",
            r"    \begin{minipage}{0.94\textwidth}",
            r"    \vspace{0.35em}\footnotesize",
            r"    \textit{Note:} Target is future 3-year global-adjusted log growth $G_{\text{adj}}(i, t)$. $M0$ is the unfitted adjusted-momentum benchmark ($\hat{G}_{\text{adj}}^{(M0)} = M0_{\text{adj}}$); $M1$--$M3$ are frozen \texttt{StandardScaler}--\texttt{Ridge} pipelines fitted strictly on Stage 3.3 training splits (Origin 2015 for Test 2018; pooled Origins 2015--2018 for Test 2021). Confidence intervals are 95\% percentile intervals ($B = 5{,}000$, \texttt{seed = 42}, \texttt{method='linear'}) conditional on the fitted models and selected $\alpha$.",
            r"    \end{minipage}",
            r"\end{table}",
        ]
    )
    (tables_dir / "table_5_1_rq2_mae_performance.tex").write_text(
        "\n".join(tex_lines) + "\n", encoding="utf-8", newline="\n"
    )
    return t_df


def build_table_5_2(paired_df: pd.DataFrame, tables_dir: Path) -> pd.DataFrame:
    """Create Table 5.2 (Prespecified Paired MAE Differences & 95% Bootstrap CIs)."""
    rows = []
    for orig in (2018, 2021):
        sub = (
            paired_df[paired_df["test_origin"] == orig]
            .set_index("comparison_id")
            .loc[COMPARISON_ORDER]
        )
        exp_label = "Experiment A (2018)" if orig == 2018 else "Experiment B (2021)"
        for comp_id in COMPARISON_ORDER:
            r = sub.loc[comp_id]
            rows.append(
                {
                    "Experiment": exp_label,
                    "Test Origin": int(orig),
                    "Comparison": str(r["comparison_label"]),
                    "Definition": str(r["definition"]),
                    "Test N": int(r["n_test"]),
                    "Observed Delta MAE": float(r["delta_mae_observed"]),
                    "CI 95% Low": float(r["ci_95_low"]),
                    "CI 95% High": float(r["ci_95_high"]),
                    "Excludes Zero": bool(r["ci_95_excludes_zero"]),
                    "Delta MAE (95% Paired CI)": (
                        f"{float(r['delta_mae_observed']):+.4f} "
                        f"[{float(r['ci_95_low']):+.4f}, {float(r['ci_95_high']):+.4f}]"
                    ),
                    "Direction Interpretation": str(r["direction_interpretation"]),
                }
            )

    t_df = pd.DataFrame(rows)
    t_df.to_csv(tables_dir / "table_5_2_rq2_paired_comparisons.csv", index=False, lineterminator="\n")

    tex_lines = [
        r"% Auto-generated strictly from Stage 3.4 audited metrics/paired_mae_differences.csv",
        r"\begin{table}[htbp]",
        r"    \centering",
        r"    \small",
        r"    \caption{Prespecified Nested Paired MAE Comparisons ($\Delta\text{MAE} = \text{MAE}_{\text{aug}} - \text{MAE}_{\text{ref}}$) with 95\% Paired Topic Bootstrap Confidence Intervals}",
        r"    \label{tab:rq2-paired-comparisons}",
        r"    \begin{tabular}{llcl}",
        r"        \toprule",
        r"        \textbf{Test Origin} & \textbf{Comparison} & \textbf{Observed $\Delta\text{MAE}$ [95\% Paired CI]} & \textbf{Interpretation} \\",
        r"        \midrule",
    ]
    for idx_orig, orig in enumerate((2018, 2021)):
        sub = t_df[t_df["Test Origin"] == orig]
        for i, (_, row) in enumerate(sub.iterrows()):
            orig_col = f"{orig} ($N={row['Test N']}$)" if i == 0 else ""
            delta_str = (
                f"{row['Observed Delta MAE']:+.4f} "
                f"[{row['CI 95% Low']:+.4f}, {row['CI 95% High']:+.4f}]"
            )
            interp_tex = (
                str(row["Direction Interpretation"])
                .replace("%", r"\%")
                .replace(" < ", " $<$ ")
                .replace(" > ", " $>$ ")
            )
            tex_lines.append(
                f"        {orig_col} & {row['Comparison']} & {delta_str} & {interp_tex} \\\\"
            )
        if idx_orig == 0:
            tex_lines.append(r"        \midrule")

    tex_lines.extend(
        [
            r"        \bottomrule",
            r"    \end{tabular}",
            r"    \begin{minipage}{0.94\textwidth}",
            r"    \vspace{0.35em}\footnotesize",
            r"    \textit{Note:} Negative values ($\Delta\text{MAE} < 0$) indicate lower forecasting error for the augmented model relative to the reference model. Each experiment uses a shared paired bootstrap index matrix ($B = 5{,}000$, \texttt{seed = 42}, \texttt{method='linear'}) across $M0$--$M3$; CIs quantify test-topic sampling uncertainty conditional on fitted Stage 3.3 models.",
            r"    \end{minipage}",
            r"\end{table}",
        ]
    )
    (tables_dir / "table_5_2_rq2_paired_comparisons.tex").write_text(
        "\n".join(tex_lines) + "\n", encoding="utf-8", newline="\n"
    )
    return t_df


def build_figure_5_1(mae_df: pd.DataFrame, figures_dir: Path) -> None:
    """Create Figure 5.1 — Side-by-side MAE comparison with 95% bootstrap CIs."""
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.edgecolor": "#475569",
            "axes.linewidth": 0.9,
            "svg.hashsalt": "stage3_4_rq2_fig51",
            "savefig.dpi": 300,
        }
    )

    fig, axes = plt.subplots(1, 2, figsize=(12.0, 5.2), sharey=True)
    fig.subplots_adjust(wspace=0.16, bottom=0.22)

    all_low = float(mae_df["ci_95_low"].min())
    all_high = float(mae_df["ci_95_high"].max())
    span = max(all_high - all_low, 0.01)
    y_min = max(0.0, all_low - 0.22 * span)
    y_max = all_high + 0.30 * span

    panels = [
        (axes[0], 2018, "(a) Origin 2018 (Eval 2019–2021, N = 992)"),
        (axes[1], 2021, "(b) Origin 2021 (Eval 2022–2024, N = 995)"),
    ]

    x_pos = np.arange(len(MODEL_ORDER))
    for ax, orig, title in panels:
        sub = mae_df[mae_df["test_origin"] == orig].set_index("model").loc[MODEL_ORDER]
        maes = sub["mae"].to_numpy(dtype=np.float64)
        lows = sub["ci_95_low"].to_numpy(dtype=np.float64)
        highs = sub["ci_95_high"].to_numpy(dtype=np.float64)

        ax.plot(x_pos, maes, color="#CBD5E1", linewidth=1.4, linestyle="-", zorder=1)
        for i, m in enumerate(MODEL_ORDER):
            yerr = np.array([[maes[i] - lows[i]], [highs[i] - maes[i]]], dtype=np.float64)
            ax.errorbar(
                x_pos[i],
                maes[i],
                yerr=yerr,
                fmt="o",
                color=MODEL_COLORS[m],
                ecolor=MODEL_COLORS[m],
                elinewidth=2.0,
                capsize=5,
                capthick=1.6,
                markersize=7.5,
                zorder=3,
                label=m if orig == 2018 else None,
            )
            ax.text(
                x_pos[i],
                highs[i] + 0.04 * span,
                f"{maes[i]:.4f}",
                ha="center",
                va="bottom",
                fontsize=8.5,
                fontweight="bold",
                color=MODEL_COLORS[m],
            )

        ax.set_title(title, fontsize=10.2, fontweight="bold", pad=10, color="#0F172A")
        ax.set_xticks(x_pos)
        ax.set_xticklabels([MODEL_LABELS_SHORT[m] for m in MODEL_ORDER], fontsize=9)
        ax.set_ylim(y_min, y_max)
        ax.grid(axis="y", linestyle=":", alpha=0.55, color="#94A3B8")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    axes[0].set_ylabel("Mean Absolute Error (MAE)", fontsize=10, fontweight="bold", color="#0F172A")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(
        handles,
        labels,
        loc="lower center",
        bbox_to_anchor=(0.5, 0.01),
        ncol=4,
        frameon=True,
        facecolor="white",
        edgecolor="#CBD5E1",
        fontsize=8.5,
        title="Model Specification",
        title_fontsize=8.5,
    )
    fig.suptitle(
        "Figure 5.1: Held-Out Forecasting Accuracy (MAE) Across Models with 95% Conditional Bootstrap CIs",
        fontsize=11.5,
        fontweight="bold",
        y=0.99,
        color="#0F172A",
    )
    save_deterministic_figure(fig, figures_dir / "fig_5_1_rq2_mae_comparison")
    plt.close(fig)


def build_figure_5_2(paired_df: pd.DataFrame, figures_dir: Path) -> None:
    """Create Figure 5.2 — Paired MAE differences (Delta_MAE) with 95% paired CIs."""
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.edgecolor": "#475569",
            "axes.linewidth": 0.9,
            "svg.hashsalt": "stage3_4_rq2_fig52",
            "savefig.dpi": 300,
        }
    )

    fig, axes = plt.subplots(1, 2, figsize=(12.4, 4.7), sharey=True, sharex=True)
    fig.subplots_adjust(wspace=0.16)

    all_low = float(paired_df["ci_95_low"].min())
    all_high = float(paired_df["ci_95_high"].max())
    abs_max = max(abs(all_low), abs(all_high), 0.005)
    x_lim = abs_max * 1.35

    y_pos = np.arange(len(COMPARISON_ORDER))[::-1]
    panels = [
        (axes[0], 2018, "(a) Test Origin 2018 (N = 992)"),
        (axes[1], 2021, "(b) Test Origin 2021 (N = 995)"),
    ]

    for ax, orig, title in panels:
        sub = (
            paired_df[paired_df["test_origin"] == orig]
            .set_index("comparison_id")
            .loc[COMPARISON_ORDER]
        )
        ax.axvline(0.0, color="#64748B", linestyle="--", linewidth=1.3, zorder=1)
        for i, comp_id in enumerate(COMPARISON_ORDER):
            r = sub.loc[comp_id]
            d = float(r["delta_mae_observed"])
            lo = float(r["ci_95_low"])
            hi = float(r["ci_95_high"])
            if hi < 0.0:
                color = "#059669"  # Emerald: CI strictly < 0
            elif lo > 0.0:
                color = "#DC2626"  # Red: CI strictly > 0
            else:
                color = "#475569"  # Neutral slate: spans 0

            xerr = np.array([[d - lo], [hi - d]], dtype=np.float64)
            ax.errorbar(
                d,
                y_pos[i],
                xerr=xerr,
                fmt="s",
                color=color,
                ecolor=color,
                elinewidth=2.0,
                capsize=4.5,
                capthick=1.6,
                markersize=6.5,
                zorder=3,
            )
            ax.text(
                d,
                y_pos[i] + 0.19,
                f"{d:+.4f} [{lo:+.4f}, {hi:+.4f}]",
                ha="center",
                va="bottom",
                fontsize=8.2,
                color=color,
                fontweight="bold",
                zorder=4,
                bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.88, "pad": 1.2},
            )

        ax.set_title(title, fontsize=10.5, fontweight="bold", pad=10, color="#0F172A")
        ax.set_xlim(-x_lim, x_lim)
        ax.set_ylim(-0.65, len(COMPARISON_ORDER) - 0.3)
        ax.set_yticks(y_pos)
        ax.set_yticklabels([COMPARISON_LABELS[c] for c in COMPARISON_ORDER], fontsize=9)
        ax.set_xlabel(r"$\Delta\mathrm{MAE} = \mathrm{MAE}(\mathrm{aug}) - \mathrm{MAE}(\mathrm{ref})$", fontsize=9.5)
        ax.grid(axis="x", linestyle=":", alpha=0.55, color="#94A3B8")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    fig.suptitle(
        "Figure 5.2: Prespecified Paired MAE Differences with 95% Paired Topic Bootstrap CIs (< 0 = Lower Error)",
        fontsize=11.5,
        fontweight="bold",
        y=1.02,
        color="#0F172A",
    )
    save_deterministic_figure(fig, figures_dir / "fig_5_2_rq2_paired_mae_differences")
    plt.close(fig)


def write_assets_readme(t1: pd.DataFrame, t2: pd.DataFrame, assets_dir: Path) -> None:
    """Write thesis_assets/README.md with exact audited table previews."""
    lines = [
        "# Stage 3.4 Thesis Assets — Chapter 5 (RQ2 Forecasting Accuracy)",
        "",
        "Generated strictly from audited Stage 3.4 outputs (`metrics/mae_summary.csv` and `metrics/paired_mae_differences.csv`).",
        "",
        "## Table 5.1 — Held-Out Forecasting Performance",
        "",
        "| Experiment | Model | Tuned alpha | Test N | MAE (95% Bootstrap CI) |",
        "| --- | :---: | ---: | ---: | --- |",
    ]
    for _, r in t1.iterrows():
        lines.append(
            f"| {r['Experiment']} | {r['Model']} | {r['Selected alpha']} | {r['Test N']} | {r['MAE (95% Bootstrap CI)']} |"
        )
    lines.extend(
        [
            "",
            "* **Files:** `tables/table_5_1_rq2_mae_performance.csv`, `tables/table_5_1_rq2_mae_performance.tex`",
            "",
            "## Table 5.2 — Prespecified Paired MAE Comparisons",
            "",
            "| Experiment | Comparison | Delta_MAE (95% Paired CI) | Direction Interpretation |",
            "| --- | --- | --- | --- |",
        ]
    )
    for _, r in t2.iterrows():
        lines.append(
            f"| {r['Experiment']} | {r['Comparison']} | {r['Delta MAE (95% Paired CI)']} | {r['Direction Interpretation']} |"
        )
    lines.extend(
        [
            "",
            "* **Files:** `tables/table_5_2_rq2_paired_comparisons.csv`, `tables/table_5_2_rq2_paired_comparisons.tex`",
            "",
            "## Figures",
            "- `figures/fig_5_1_rq2_mae_comparison.{pdf,svg,png}` — Held-out MAE comparison across M0–M3 for Test Origins 2018 and 2021.",
            "- `figures/fig_5_2_rq2_paired_mae_differences.{pdf,svg,png}` — Paired Delta_MAE intervals for the four prespecified nested comparisons.",
            "",
        ]
    )
    (assets_dir / "README.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")


def build_all_assets(eval_dir: Path) -> None:
    """Build all Stage 3.4 thesis tables, figures, and asset README."""
    metrics_dir = eval_dir / "metrics"
    assets_dir = eval_dir / "thesis_assets"
    tables_dir = assets_dir / "tables"
    figures_dir = assets_dir / "figures"
    for d in (assets_dir, tables_dir, figures_dir):
        d.mkdir(parents=True, exist_ok=True)

    mae_df = pd.read_csv(metrics_dir / "mae_summary.csv", float_precision="round_trip")
    paired_df = pd.read_csv(metrics_dir / "paired_mae_differences.csv", float_precision="round_trip")

    t1 = build_table_5_1(mae_df, tables_dir)
    t2 = build_table_5_2(paired_df, tables_dir)
    build_figure_5_1(mae_df, figures_dir)
    build_figure_5_2(paired_df, figures_dir)
    write_assets_readme(t1, t2, assets_dir)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Stage 3.4 RQ2 thesis tables and figures.")
    parser.add_argument(
        "--eval-dir",
        type=Path,
        default=DEFAULT_EVAL_DIR,
        help="Directory containing Stage 3.4 outputs.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    build_all_assets(args.eval_dir)
    print(f"[Stage 3.4 Assets] Wrote tables and figures under {args.eval_dir / 'thesis_assets'}")


if __name__ == "__main__":
    main()
