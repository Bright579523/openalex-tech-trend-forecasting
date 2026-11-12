"""
Stage 3.1 Thesis Figure Generator (Editable Source)
Script: stage3_modeling/thesis_assets/fig_4_feature_target_workflow.py

Generates the academic MDPI-style workflow diagram illustrating strict causal
separation between historical inputs/features/eligibility (y <= t) and future
target construction (y in [t+1, t+3]) for Stage 3.1:
  - fig_4_feature_target_workflow.svg (vector)
  - fig_4_feature_target_workflow.pdf (vector for LaTeX)
  - fig_4_feature_target_workflow.png (300 DPI raster)

Intended Thesis Placement: Chapter 4, Sections 4.3--4.4 (Suggested: Figure 4.1)
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ASSETS_DIR = Path(__file__).resolve().parent


def draw_card(
    ax: plt.Axes,
    x: float,
    y: float,
    w: float,
    h: float,
    header_h: float,
    title: str,
    header_color: str,
    border_color: str,
    bullets: List[Tuple[str, float]],
    body_bg: str = "#FFFFFF",
    title_size: float = 10.5,
    body_size: float = 8.9,
) -> None:
    """Draw an MDPI-style rounded card with colored header strip and bullet lines."""
    r = 0.9

    # Main white card body
    outer = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle=f"round,pad=0,rounding_size={r}",
        facecolor=body_bg,
        edgecolor=border_color,
        linewidth=1.5,
        zorder=3,
    )
    ax.add_patch(outer)

    # Top header banner clipped neatly inside top corners
    header_rect = FancyBboxPatch(
        (x, y + h - header_h),
        w,
        header_h,
        boxstyle=f"round,pad=0,rounding_size={r}",
        facecolor=header_color,
        edgecolor=border_color,
        linewidth=1.3,
        zorder=4,
    )
    ax.add_patch(header_rect)
    # Square off bottom edge of header banner seamlessly
    sq_cover = patches.Rectangle(
        (x + 0.08, y + h - header_h),
        w - 0.16,
        min(r + 0.15, header_h * 0.55),
        facecolor=header_color,
        edgecolor="none",
        zorder=4.5,
    )
    ax.add_patch(sq_cover)
    # Horizontal divider line under header
    ax.plot(
        [x, x + w],
        [y + h - header_h, y + h - header_h],
        color=border_color,
        linewidth=1.2,
        zorder=5,
    )

    # Header title text
    ax.text(
        x + w / 2.0,
        y + h - header_h / 2.0,
        title,
        ha="center",
        va="center",
        fontsize=title_size,
        fontweight="bold",
        color="#1A2433",
        zorder=6,
    )

    # Body bullet lines
    top_y = y + h - header_h - 1.55
    for idx, (line, line_step) in enumerate(bullets):
        ax.text(
            x + 1.0,
            top_y,
            line,
            ha="left",
            va="top",
            fontsize=body_size,
            color="#222B35",
            zorder=6,
        )
        top_y -= line_step


def draw_orth_arrow(
    ax: plt.Axes,
    pts: List[Tuple[float, float]],
    color: str = "#2C3E50",
    lw: float = 1.6,
    ls: str = "-",
    zorder: int = 7,
) -> None:
    """Draw multi-segment orthogonal connector ending in a clean arrowhead."""
    if len(pts) >= 2:
        xs = [p[0] for p in pts[:-1]]
        ys = [p[1] for p in pts[:-1]]
        if len(xs) >= 2:
            ax.plot(xs, ys, color=color, linewidth=lw, linestyle=ls, zorder=zorder)
        arr = FancyArrowPatch(
            pts[-2],
            pts[-1],
            arrowstyle="-|>,head_length=6,head_width=3.6",
            color=color,
            linewidth=lw,
            linestyle=ls,
            shrinkA=0,
            shrinkB=0,
            zorder=zorder,
        )
        ax.add_patch(arr)


def generate_workflow_figure() -> None:
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Helvetica"]
    plt.rcParams["mathtext.fontset"] = "dejavusans"

    fig, ax = plt.subplots(figsize=(14.6, 8.4))
    ax.set_xlim(0, 101)
    ax.set_ylim(0, 63)
    ax.axis("off")
    fig.patch.set_facecolor("#FFFFFF")

    # -------------------------------------------------------------------------
    # Zone Backgrounds & Strict Causal Boundary
    # -------------------------------------------------------------------------
    # Historical Zone (Years y <= t)
    hist_zone = FancyBboxPatch(
        (1.2, 27.0),
        70.0,
        34.6,
        boxstyle="round,pad=0,rounding_size=1.1",
        facecolor="#F6F9FE",
        edgecolor="#BFD3EB",
        linewidth=1.2,
        zorder=1,
    )
    ax.add_patch(hist_zone)
    ax.text(
        2.5,
        60.4,
        r"HISTORICAL / ORIGIN-AVAILABLE DATA & FEATURES (Years $y \leq t$)",
        ha="left",
        va="center",
        fontsize=9.2,
        fontweight="bold",
        color="#2B547E",
        zorder=2,
    )

    # Future Evaluation Zone (Years y in [t+1, t+3])
    fut_zone = FancyBboxPatch(
        (1.2, 1.8),
        70.0,
        19.8,
        boxstyle="round,pad=0,rounding_size=1.1",
        facecolor="#FFF7F6",
        edgecolor="#E5C1BD",
        linewidth=1.2,
        zorder=1,
    )
    ax.add_patch(fut_zone)
    ax.text(
        19.8,
        20.3,
        r"FUTURE EVALUATION WINDOW (Years $y \in [t+1,\, t+3]$) — TARGET LABEL ONLY",
        ha="left",
        va="center",
        fontsize=9.2,
        fontweight="bold",
        color="#922B21",
        zorder=2,
    )

    # Causal Cutoff Barrier Line
    ax.plot(
        [1.2, 71.2],
        [24.3, 24.3],
        color="#B03A2E",
        linewidth=1.7,
        linestyle="--",
        zorder=4,
    )
    ax.text(
        42.8,
        24.3,
        r"STRICT CAUSAL ORIGIN CUTOFF ($t$): ZERO FUTURE DATA PERMITTED IN BLOCKS B OR D",
        ha="center",
        va="center",
        fontsize=8.2,
        fontweight="bold",
        color="#922B21",
        bbox=dict(
            boxstyle="round,pad=0.32,rounding_size=0.3",
            facecolor="#FDEDEC",
            edgecolor="#B03A2E",
            linewidth=1.1,
        ),
        zorder=8,
    )

    # -------------------------------------------------------------------------
    # Card A: Historical Input Data (y <= t)
    # -------------------------------------------------------------------------
    draw_card(
        ax,
        x=2.4,
        y=28.8,
        w=26.8,
        h=29.8,
        header_h=4.2,
        title=r"A. Historical Input Data ($y \leq t$)",
        header_color="#DCE8F8",
        border_color="#4A78B8",
        bullets=[
            (r"$\mathbf{Synchronized\ Panel\ v2}$ (2010–2024):", 2.6),
            (r"$\bullet$ Global topic counts: $P_{\mathrm{Global},i,y}$" + "\n   " + r"across $[t-5,t-3]$ and $[t-2,t]$", 4.9),
            (r"$\bullet$ Fractional country topic counts:" + "\n   " + r"$P^{\mathrm{Frac}}_{c,i,y}$ ($1/k$ rule; DE, CN, JP)", 4.9),
            (r"$\bullet$ National all-science denominators:" + "\n   " + r"$P^{\mathrm{Frac}}_{c,\mathrm{All},y}$ and global $W_y$", 4.9),
            (r"$\bullet$ Whole-count sensitivity inputs:" + "\n   " + r"$P^{\mathrm{Whole}}_{c,i,y}$ and $P^{\mathrm{Whole}}_{c,\mathrm{All},y}$", 4.5),
        ],
        title_size=10.1,
        body_size=8.5,
    )

    # -------------------------------------------------------------------------
    # Card D: Eligibility Gate (y in [t-2, t])
    # -------------------------------------------------------------------------
    draw_card(
        ax,
        x=32.8,
        y=46.8,
        w=37.0,
        h=11.8,
        header_h=3.6,
        title=r"D. Origin Eligibility Gate ($y \in [t-2,\, t]$)",
        header_color="#FFF2CC",
        border_color="#B8963A",
        bullets=[
            (r"$\bullet$ Past 3-year sum rule: $\Sigma_{y=t-2}^{t}\, P_{\mathrm{Global},i,y} \geq 50$", 2.45),
            (r"$\bullet$ Assigns Boolean flag $\mathtt{eligible} \in \{\mathrm{True}, \mathrm{False}\}$ (990–995/origin)", 2.45),
            (r"$\bullet$ Retains all 1,025 topics per origin (Stage 3.2 filters train/test sets)", 2.2),
        ],
        title_size=9.9,
        body_size=8.2,
    )

    # -------------------------------------------------------------------------
    # Card B: Feature Construction X (y <= t Only)
    # -------------------------------------------------------------------------
    draw_card(
        ax,
        x=32.8,
        y=28.2,
        w=37.0,
        h=17.2,
        header_h=3.6,
        title=r"B. Feature Construction $X$ ($y \leq t$ Only)",
        header_color="#DCF2DC",
        border_color="#4E8E50",
        bullets=[
            (r"$\bullet$ $\mathbf{M0\_adj}$: adjusted past momentum ($[t-2,t]$ vs. $[t-5,t-3]$)", 2.55),
            (r"$\bullet$ $\mathbf{M1\ (2\ feat.)}$: $M0_{\mathrm{adj}}$ + global scale $\ln(1+P_{\mathrm{Global},i,[t-2,t]})$", 2.55),
            (r"$\bullet$ $\mathbf{M2\ (5\ feat.)}$: M1 + $\ln(1+P^{\mathrm{Frac}}_{c,i,[t-2,t]})$ for DE, CN, JP", 2.55),
            (r"$\bullet$ $\mathbf{M3\ (8\ feat.)}$: M2 + 3-yr ratio-of-sums raw $RCA^{\mathrm{Frac}}_{c,i,[t-2,t]}$", 2.65),
            (r"$\bullet$ $\mathbf{Sensitivities}$: M3-LogRCA, M2-WC, M3-WC (matched WC base)", 2.2),
        ],
        title_size=9.9,
        body_size=8.15,
    )

    # -------------------------------------------------------------------------
    # Card C: Future Target Construction (y in [t+1, t+3])
    # -------------------------------------------------------------------------
    draw_card(
        ax,
        x=19.8,
        y=3.0,
        w=50.0,
        h=15.6,
        header_h=3.7,
        title=r"C. Future Target Construction ($y \in [t+1,\, t+3]$, Target Only)",
        header_color="#FADBD8",
        border_color="#B85450",
        bullets=[
            (r"$\bullet$ Future global topic counts $P_{\mathrm{Global},i,[t+1,t+3]}$ & global all-science counts $W_{[t+1,t+3]}$", 2.65),
            (r"$\bullet$ Normalized against base window $[t-2, t]$ counts ($P_{\mathrm{Global},i,[t-2,t]},\ W_{[t-2,t]}$):", 2.65),
            (r"   $G_{\mathrm{adj}}(i,t) = [\ln(1+P_{[t+1,t+3]}^{(i)}) - \ln(1+P_{[t-2,t]}^{(i)})] - [\ln(1+W_{[t+1,t+3]}) - \ln(1+W_{[t-2,t]})]$", 2.95),
            (r"$\bullet$ Stored solely as target vector $y = \mathtt{g\_adj}$ (excluded from $X$ and eligibility)", 2.3),
        ],
        title_size=9.9,
        body_size=8.25,
    )

    # -------------------------------------------------------------------------
    # Card E: Final Output (Stage 3.1 Canonical Origin-Level Dataset)
    # -------------------------------------------------------------------------
    draw_card(
        ax,
        x=74.0,
        y=3.0,
        w=25.6,
        h=55.6,
        header_h=4.6,
        title="E. Stage 3.1 Canonical Output\n" + r"($7{,}175 \times 42$ | Origins 2015–2021)",
        header_color="#E8DDF5",
        border_color="#7D5BA6",
        bullets=[],
        title_size=9.4,
        body_size=8.3,
    )

    # Internal Compartments inside Card E separating Schema Roles explicitly
    comp_specs = [
        (
            45.8,
            7.2,
            "#FFF9E6",
            "#B8963A",
            "Identifiers & Eligibility Flag",
            r"$\mathtt{forecast\_origin}$, $\mathtt{topic\_id}$, $\mathtt{field\_name}$"
            + "\n"
            + r"$\mathtt{eligible}$ (all 1,025 topics retained)",
        ),
        (
            26.8,
            17.2,
            "#EFF9EF",
            "#4E8E50",
            r"Separated Predictors $X$ ($y \leq t$)",
            r"$\bullet$ Benchmark: M0 ($\mathtt{m0\_adj}$)"
            + "\n"
            + r"$\bullet$ Primary: M1 (2), M2 (5), M3 (8)"
            + "\n"
            + r"$\bullet$ Sensitivity: M3-LogRCA (8)"
            + "\n"
            + r"$\bullet$ Sensitivity: M2-WC (5), M3-WC (8)"
            + "\n"
            + r"$\bullet$ Past $[t-5, t]$ audit sums only",
        ),
        (
            9.6,
            15.2,
            "#FDF0EE",
            "#B85450",
            r"Separated Target $y$ ($[t+1, t+3]$)",
            r"$\bullet$ Outcome: $\mathtt{g\_adj}$ ($G_{\mathrm{adj}}(i,t)$)"
            + "\n"
            + r"$\bullet$ Future target sums: $\mathtt{target\_*}$"
            + "\n"
            + r"$\bullet$ Disjoint from all feature sets $X$"
            + "\n"
            + r"   (verified zero future overlap)",
        ),
    ]
    for cy, ch, bg, ec, ctitle, ctext in comp_specs:
        box = FancyBboxPatch(
            (75.3, cy),
            23.0,
            ch,
            boxstyle="round,pad=0,rounding_size=0.6",
            facecolor=bg,
            edgecolor=ec,
            linewidth=1.1,
            zorder=5,
        )
        ax.add_patch(box)
        ax.text(
            76.2,
            cy + ch - 1.15,
            ctitle,
            ha="left",
            va="top",
            fontsize=8.7,
            fontweight="bold",
            color="#1A2433",
            zorder=6,
        )
        ax.text(
            76.2,
            cy + ch - 3.35,
            ctext,
            ha="left",
            va="top",
            fontsize=7.95,
            color="#222B35",
            linespacing=1.32,
            zorder=6,
        )

    # Audit Verification Badge at bottom of Card E
    audit_badge = FancyBboxPatch(
        (75.3, 4.2),
        23.0,
        3.8,
        boxstyle="round,pad=0,rounding_size=0.5",
        facecolor="#EBF5FB",
        edgecolor="#2E86C1",
        linewidth=1.0,
        zorder=5,
    )
    ax.add_patch(audit_badge)
    ax.text(
        86.8,
        6.1,
        "Independent Audit: 19 / 19 PASS\n" + r"Poisoning ($y > t$) $\Rightarrow \Delta X = 0.00$",
        ha="center",
        va="center",
        fontsize=7.9,
        fontweight="bold",
        color="#1B4F72",
        zorder=6,
    )

    # -------------------------------------------------------------------------
    # Arrows (Explicit Causal Flow)
    # -------------------------------------------------------------------------
    # A -> D (Past [t-2,t] counts to Eligibility)
    draw_orth_arrow(ax, [(29.2, 52.3), (32.8, 52.3)], color="#2C3E50", lw=1.7)
    # A -> B (Historical inputs to Feature Construction)
    draw_orth_arrow(ax, [(29.2, 36.8), (32.8, 36.8)], color="#2C3E50", lw=1.7)

    # A -> C (Thin dashed grey downward-only reference for base [t-2, t] scaling in G_adj)
    draw_orth_arrow(
        ax,
        [(10.0, 28.8), (10.0, 10.8), (19.8, 10.8)],
        color="#666666",
        lw=1.35,
        ls="--",
    )
    ax.text(
        10.0,
        15.6,
        "Base $[t-2, t]$\nscaling only\n(downward)",
        ha="center",
        va="center",
        fontsize=7.6,
        color="#4D5656",
        bbox=dict(
            boxstyle="round,pad=0.28,rounding_size=0.25",
            facecolor="#FFFFFF",
            edgecolor="#B2BABB",
            linewidth=0.85,
        ),
        zorder=8,
    )

    # D -> E1 (Eligibility flag into Output Identifier/Eligibility compartment)
    draw_orth_arrow(ax, [(69.8, 49.6), (75.3, 49.6)], color="#B8963A", lw=1.7)
    # B -> E2 (Feature sets into Output X compartment)
    draw_orth_arrow(ax, [(69.8, 35.6), (75.3, 35.6)], color="#3D8B40", lw=1.7)
    # C -> E3 (Target g_adj into Output Target y compartment)
    draw_orth_arrow(ax, [(69.8, 14.5), (75.3, 14.5)], color="#B85450", lw=1.7)

    # Save SVG, PDF, and 300-DPI PNG from the identical vector figure
    svg_path = ASSETS_DIR / "fig_4_feature_target_workflow.svg"
    pdf_path = ASSETS_DIR / "fig_4_feature_target_workflow.pdf"
    png_path = ASSETS_DIR / "fig_4_feature_target_workflow.png"

    fig.savefig(svg_path, format="svg", bbox_inches="tight", pad_inches=0.18)
    fig.savefig(pdf_path, format="pdf", bbox_inches="tight", pad_inches=0.18)
    fig.savefig(png_path, format="png", dpi=300, bbox_inches="tight", pad_inches=0.18)
    plt.close(fig)

    print(f"[PASS] Saved workflow figure: {svg_path.name}, {pdf_path.name}, {png_path.name}")


if __name__ == "__main__":
    generate_workflow_figure()
