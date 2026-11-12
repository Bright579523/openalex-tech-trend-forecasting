"""
Stage 3.1 Thesis-Ready Tables Generator
Script: stage3_modeling/thesis_assets/build_thesis_tables.py

Reads verified Stage 3.1 outputs ONLY (read-only):
  - stage3_modeling/stage3_origin_features_targets.csv
  - stage3_modeling/stage3_feature_target_manifest.json
  - stage3_modeling/stage3_feature_target_audit_report.md

Generates publication-ready CSV and LaTeX (uethesis.cls / booktabs) tables in
stage3_modeling/thesis_assets/:
  1. table_4_model_feature_definitions.{csv,tex}
  2. table_4_eligible_topics_by_origin.{csv,tex}
  3. table_a_stage3_1_validation_summary.{csv,tex}
"""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent.parent
STAGE3_DIR = BASE_DIR / "stage3_modeling"
ASSETS_DIR = Path(__file__).resolve().parent

CSV_PATH = STAGE3_DIR / "stage3_origin_features_targets.csv"
MANIFEST_PATH = STAGE3_DIR / "stage3_feature_target_manifest.json"
AUDIT_MD_PATH = STAGE3_DIR / "stage3_feature_target_audit_report.md"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def tex_escape(text: str) -> str:
    """Escape plain-text LaTeX special characters outside math/code commands."""
    replacements = [
        ("\\", "\\textbackslash{}"),
        ("&", "\\&"),
        ("%", "\\%"),
        ("$", "\\$"),
        ("#", "\\#"),
        ("_", "\\_"),
        ("{", "\\{"),
        ("}", "\\}"),
        ("~", "\\textasciitilde{}"),
        ("^", "\\textasciicircum{}"),
    ]
    out = text
    for old, new in replacements:
        out = out.replace(old, new)
    return out


def format_tex_col_list(cols: List[str], model: str) -> str:
    """Format verified feature column names cleanly for LaTeX table cells."""
    if model == "M0":
        return r"\textit{None (unfitted direct rule: } \texttt{m0\_adj}\textit{)}"
    return ", ".join(r"\texttt{" + tex_escape(c) + "}" for c in cols)


def build_table_model_features(manifest: Dict[str, Any], df_stage3: pd.DataFrame) -> None:
    """Generate Table 4.x: Model Feature Definitions (M0-M3 and pre-declared sensitivities)."""
    fsets: Dict[str, List[str]] = manifest["schema_roles"]["model_feature_sets"]
    target_col = manifest["schema_roles"]["target_column"]

    # Confirm every listed feature column actually exists in stage3_origin_features_targets.csv
    csv_cols = set(df_stage3.columns)
    for model_name, cols in fsets.items():
        missing = [c for c in cols if c not in csv_cols]
        if missing:
            raise ValueError(f"Model {model_name} lists columns missing from CSV: {missing}")
        if target_col in cols:
            raise ValueError(f"Target column {target_col} leaked into {model_name}")

    metadata = {
        "M0": (
            "Primary Benchmark",
            "0 (Unfitted)",
            "Direct adjusted past momentum baseline predicting G_adj(i,t) = M0_adj(i,t) without learned parameters.",
            r"Direct adjusted past momentum baseline predicting $G_{\text{adj}}(i,t) = M0_{\text{adj}}(i,t)$ without learned weights.",
        ),
        "M1": (
            "Primary Hierarchy",
            "2",
            "Tests whether linear Ridge weighting of past momentum and global 3-year topic scale improves out-of-sample growth forecasts.",
            r"Ridge regression on past momentum and global 3-year topic scale over $[t-2, t]$.",
        ),
        "M2": (
            "Primary Hierarchy",
            "5",
            "Adds log-transformed 3-year fractional publication volumes for Germany (DE), China (CN), and Japan (JP) beyond M1 global history.",
            r"Adds log 3-year $1/k$ fractional topic counts for DE, CN, and JP to M1.",
        ),
        "M3": (
            "Primary Specification",
            "8",
            "Primary specialisation model adding untransformed, unwinsorized 3-year ratio-of-sums fractional RCA for DE, CN, and JP to M2.",
            r"Primary specification: adds raw 3-year ratio-of-sums fractional RCA for DE, CN, and JP to M2.",
        ),
        "M3-LogRCA": (
            "Sensitivity 1 (Pre-Declared)",
            "8",
            "Replaces raw fractional RCA in M3 with ln(1 + RCA) while holding all M2 count features fixed to test functional-form sensitivity.",
            r"Replaces raw fractional RCA in M3 with $\ln(1 + RCA^{\text{Frac}})$ while holding M2 counts fixed.",
        ),
        "M2-WC": (
            "Sensitivity 2 (Pre-Declared)",
            "5",
            "Whole-counting counterpart to M2 replacing fractional DE, CN, and JP topic counts with whole-count log volumes.",
            r"Whole-counting counterpart to M2 using whole-count log topic volumes for DE, CN, and JP.",
        ),
        "M3-WC": (
            "Sensitivity 2 (Pre-Declared)",
            "8",
            "Full whole-counting counterpart to M3 adding whole-count 3-year ratio-of-sums RCA paired strictly with whole-count all-science denominators.",
            r"Pairs whole-count log volumes with whole-count 3-year ratio-of-sums RCA using consistent whole-count denominators.",
        ),
    }

    order = ["M0", "M1", "M2", "M3", "M3-LogRCA", "M2-WC", "M3-WC"]
    csv_out = ASSETS_DIR / "table_4_model_feature_definitions.csv"
    with open(csv_out, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["model", "role", "n_features", "feature_columns", "purpose"])
        for m in order:
            cols = fsets[m]
            if len(cols) != int(metadata[m][1].split()[0]):
                raise AssertionError(f"Feature count mismatch for {m}")
            col_str = "None (direct rule: m0_adj)" if m == "M0" else ", ".join(cols)
            writer.writerow([m, metadata[m][0], metadata[m][1], col_str, metadata[m][2]])

    tex_lines = [
        r"% Suggested Placement: Chapter 4, Sections 4.4--4.5 (Model Hierarchy and Feature Definitions)",
        r"% Suggested Label: \label{tab:model-features}",
        r"% Verified strictly against stage3_feature_target_manifest.json and stage3_origin_features_targets.csv",
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Feature definitions, counts, and analytical roles for benchmark, primary (\texttt{M0}--\texttt{M3}), and pre-declared sensitivity specifications}",
        r"\label{tab:model-features}",
        r"\footnotesize",
        r"\setlength{\tabcolsep}{3.5pt}",
        r"\begin{tabular}{>{\raggedright\arraybackslash}p{1.75cm} >{\raggedright\arraybackslash}p{2.05cm} c >{\raggedright\arraybackslash}p{4.75cm} >{\raggedright\arraybackslash}p{3.65cm}}",
        r"\toprule",
        r"\textbf{Model} & \textbf{Role} & \textbf{\# Feat.} & \textbf{Feature Columns (\texttt{X})} & \textbf{Analytical Purpose} \\",
        r"\midrule",
    ]
    for i, m in enumerate(order):
        if m == "M3-LogRCA":
            tex_lines.append(r"\midrule")
        cols = fsets[m]
        role_tex = tex_escape(metadata[m][0])
        nfeat_tex = tex_escape(metadata[m][1])
        feat_tex = format_tex_col_list(cols, m)
        purp_tex = metadata[m][3]
        tex_lines.append(
            f"\\texttt{{{tex_escape(m)}}} & {role_tex} & {nfeat_tex} & {feat_tex} & {purp_tex} \\\\"
        )
        if i in (0, 3, 4) and m != "M3-WC":
            tex_lines.append(r"\addlinespace[3pt]")

    tex_lines += [
        r"\bottomrule",
        r"\end{tabular}",
        "",
        r"\vspace{4pt}",
        r"\parbox{14.8cm}{\scriptsize \textit{Notes:} All predictive features are computed strictly from publications in years $\le t$ at forecast origin $t$; future outcome counts ($[t+1, t+3]$) and target \texttt{g\_adj} are excluded from every feature set \texttt{X}. Fitted models (\texttt{M1}--\texttt{M3-WC}) use standardized Ridge regression with \texttt{StandardScaler} estimated strictly within each cross-validation training fold. \texttt{M0} is evaluated directly via \texttt{m0\_adj} without parameter fitting.}",
        r"\end{table}",
    ]
    (ASSETS_DIR / "table_4_model_feature_definitions.tex").write_text(
        "\n".join(tex_lines) + "\n", encoding="utf-8"
    )


def build_table_eligible_topics(manifest: Dict[str, Any], df_stage3: pd.DataFrame) -> None:
    """Generate Table 4.x: Eligible Topics by Forecast Origin directly from canonical CSV."""
    origins = manifest["forecast_origins"]
    rule_text = manifest["eligibility_definition"]["rule"]

    rows = []
    for t in origins:
        sub = df_stage3[df_stage3["forecast_origin"] == t]
        n_total = int(len(sub))
        # Independently verify eligible boolean matches global_topic_3yr >= 50
        calc_elig = (sub["global_topic_3yr"] >= 50).to_numpy()
        if not bool((calc_elig == sub["eligible"].to_numpy()).all()):
            raise AssertionError(f"Origin {t}: eligible mismatch against global_topic_3yr >= 50")
        n_elig = int(sub["eligible"].sum())
        n_inelig = n_total - n_elig
        cov_pct = (n_elig / n_total) * 100.0
        rows.append(
            {
                "forecast_origin": t,
                "momentum_window": f"{t-5}-{t-3}",
                "feature_eligibility_window": f"{t-2}-{t}",
                "target_window": f"{t+1}-{t+3}",
                "total_topics": n_total,
                "eligible_topics": n_elig,
                "ineligible_topics": n_inelig,
                "eligible_pct": f"{cov_pct:.2f}%",
                "eligibility_rule": rule_text,
            }
        )

    csv_out = ASSETS_DIR / "table_4_eligible_topics_by_origin.csv"
    with open(csv_out, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    tot_obs = len(df_stage3)
    tot_elig = int(df_stage3["eligible"].sum())
    tot_inelig = tot_obs - tot_elig

    tex_lines = [
        r"% Suggested Placement: Chapter 4, Section 4.6 (Temporal Train/Test Split and Origin Eligibility)",
        r"% Suggested Label: \label{tab:origin-eligibility}",
        r"% Verified directly from stage3_modeling/stage3_origin_features_targets.csv (7,175 rows)",
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Topic eligibility counts across all valid forecast origins (2015--2021) under the origin-specific historical rule $\sum_{y=t-2}^{t} P_{\text{Global}}(i, y) \ge 50$}",
        r"\label{tab:origin-eligibility}",
        r"\footnotesize",
        r"\setlength{\tabcolsep}{3.5pt}",
        r"\begin{tabular}{c c c c r r r r l}",
        r"\toprule",
        r"\textbf{Origin ($t$)} & \textbf{Momentum} & \textbf{Features/Elig.} & \textbf{Target} & \textbf{Total} & \textbf{Eligible} & \textbf{Ineligible} & \textbf{Share} & \textbf{Stage 3 Role} \\",
        r"\midrule",
    ]

    roles_tex = {
        2015: "Train (2018 \\& 2021)",
        2016: "Train (2021 only)",
        2017: "Train (2021 only)",
        2018: "Test 1 / Train (2021)",
        2019: "Valid origin (non-test)",
        2020: "Valid origin (non-test)",
        2021: "Test 2 (holdout)",
    }

    for r in rows:
        t = r["forecast_origin"]
        tex_lines.append(
            f"\\textbf{{{t}}} & {t-5}--{t-3} & {t-2}--{t} & {t+1}--{t+3} & "
            f"{r['total_topics']:,} & \\textbf{{{r['eligible_topics']:,}}} & {r['ineligible_topics']:,} & "
            f"{r['eligible_pct'].replace('%', r'\%')} & {roles_tex[t]} \\\\"
        )

    tex_lines += [
        r"\midrule",
        f"\\textbf{{All 7 Origins}} & \\multicolumn{{3}}{{c}}{{Pooled canonical Stage 3.1 rows ($7 \\times 1{{,}}025$)}} & "
        f"{tot_obs:,} & \\textbf{{{tot_elig:,}}} & {tot_inelig:,} & {tot_elig/tot_obs*100:.2f}\\% & Canonical Stage 3.1 output \\\\",
        r"\bottomrule",
        r"\end{tabular}",
        "",
        r"\vspace{4pt}",
        r"\parbox{14.8cm}{\scriptsize \textit{Notes:} Eligibility is evaluated strictly from past global selected-work counts in $[t-2, t]$ without future information. All 1,025 technology topics are retained per origin in the canonical Stage 3.1 table via an explicit Boolean \texttt{eligible} indicator; Stage 3.2 constructs the Test 2018 ($N_{\text{train}}=990$, $N_{\text{test}}=992$) and Test 2021 ($N_{\text{train}}=3{,}963$ across 2015--2018, $N_{\text{test}}=995$) modeling subsets from eligible rows only.}",
        r"\end{table}",
    ]
    (ASSETS_DIR / "table_4_eligible_topics_by_origin.tex").write_text(
        "\n".join(tex_lines) + "\n", encoding="utf-8"
    )


def build_table_validation_summary(
    manifest: Dict[str, Any], audit_text: str, df_stage3: pd.DataFrame
) -> None:
    """Generate Table A.x: Stage 3.1 Validation Summary grounded in audit report & manifest."""
    if "**`PASS`** (`19 / 19` checks PASS)" not in audit_text:
        raise AssertionError("Audit report does not show 19 / 19 PASS.")

    out_sha = sha256_file(CSV_PATH)
    if out_sha != manifest["output"]["sha256"]:
        raise AssertionError("Output CSV SHA-256 mismatch against manifest.")

    summary_rows = [
        (
            "Input Integrity",
            "SHA-256 & schema verified pre-run for Synchronized Panel v2 (15,375 x 26) and National Denominators (15 x 10); 0 nulls.",
            "PASS",
            "Panel f0049cd7...; Denoms 9c2d9ccc...; 100% annual denominator sync across 2010-2024.",
        ),
        (
            "Output Dimensions",
            "Canonical Stage 3.1 table shape, origin span (2015-2021), full 1,025-topic balance, and manifest SHA-256 match.",
            "PASS",
            "7,175 x 42; 1,025 unique topics/origin; 0 duplicates; SHA-256 9fc15d6e....",
        ),
        (
            "Formula Verification",
            "Independent stdlib csv.DictReader + math.log1p scalar recomputation across all 7,175 rows; ratio-of-sums RCA & identity check.",
            "PASS",
            "0 meta/bool/int errs; max model abs diff 2.665e-15; max sum rel diff 2.217e-16; G_adj(t)=M0_adj(t+3) max diff 0.00e+00.",
        ),
        (
            "Feature/Target Separation",
            "Canonical schema disjointness between X feature sets (M1-M3-WC) and future/target columns; raw RCA unclipped and non-logged.",
            "PASS",
            "0 overlap with g_adj or target_* columns; M1=2, M2=5, M3=8; max raw JP RCA = 12.4237.",
        ),
        (
            "Time-Window Leakage Tests",
            "Forward-year poisoning test overwriting all source data with year > origin t by 999,999,999 across all 7 origins.",
            "PASS",
            "Scalar feature invariance = 0.00e+00 (CSV max diff = 2.66e-15); target g_adj shifts on every row (min diff = 5.94).",
        ),
        (
            "Missing & Infinite Values",
            "Check for NaN, null, +/-Inf across all 7,175 rows and 6,947 eligible rows, plus 0 <= Frac <= Whole <= Global and RCA >= 0 bounds.",
            "PASS",
            "0 nulls; 0 NaNs; 0 Infs (full & eligible); 100% bound compliance.",
        ),
        (
            "Independent Audit (19/19)",
            "Standalone audit script (no imports from builder) enforcing structural, eligibility, window, numerical, and basis assertions.",
            "PASS",
            "19 / 19 checks PASS (exit code 0); eligibility 2015-2021 = 990, 990, 991, 992, 994, 995, 995.",
        ),
        (
            "Source-Data Preservation",
            "Post-build and post-audit cryptographic SHA-256 re-verification of frozen Stage 2 panel and denominator CSV files.",
            "PASS",
            "Both frozen Stage 2 files remain byte-for-byte unchanged (100% match).",
        ),
    ]

    csv_out = ASSETS_DIR / "table_a_stage3_1_validation_summary.csv"
    with open(csv_out, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["validation_domain", "check_scope", "status", "verified_evidence"])
        writer.writerows(summary_rows)

    tex_rows = [
        (
            "Input Integrity",
            r"Pre-run SHA-256 and structural check on Synchronized Panel v2 ($15{,}375 \times 26$) and National Denominators ($15 \times 10$).",
            r"\textbf{PASS}",
            r"Hashes \texttt{f0049cd7...} and \texttt{9c2d9ccc...}; 0 nulls; 100\% year/denominator alignment.",
        ),
        (
            "Output Dimensions",
            r"Canonical table dimensions, valid origin range (2015--2021), full 1,025-topic retention, and manifest checksum parity.",
            r"\textbf{PASS}",
            r"$7{,}175 \times 42$ rows/cols; 1,025 topics/origin; 0 duplicates; output SHA-256 \texttt{9fc15d6e...}.",
        ),
        (
            "Formula Verification",
            r"Independent scalar recomputation (\texttt{csv.DictReader} + \texttt{math.log1p}) over 7,175 rows; identity $G_{\text{adj}}(i,t)=M0_{\text{adj}}(i,t+3)$.",
            r"\textbf{PASS}",
            r"0 discrete errors; model $\max|\Delta|=2.665\times 10^{-15}$; identity $\max|\Delta|=0.00$.",
        ),
        (
            "Feature/Target Separation",
            r"Schema disjointness between \texttt{X} feature lists and future/target columns; verification of raw unwinsorized M3 RCA.",
            r"\textbf{PASS}",
            r"0 overlap with \texttt{g\_adj} or \texttt{target\_*}; feature counts \texttt{M1}=2, \texttt{M2}=5, \texttt{M3}=8; raw max JP RCA $= 12.4237$.",
        ),
        (
            "Time-Window Leakage Tests",
            r"Forward-year poisoning test replacing all years $> t$ with $999{,}999{,}999$ across every topic and origin.",
            r"\textbf{PASS}",
            r"Scalar feature/eligibility diff $= 0.00$ (CSV $\max|\Delta|=2.66\times 10^{-15}$); target shifts ($\min|\Delta|=5.94$).",
        ),
        (
            r"Missing \& Infinite Values",
            r"Completeness, finiteness, and monotonicity bounds ($0 \le P_{\text{Frac}} \le P_{\text{Whole}} \le P_{\text{Global}}$, $\text{RCA} \ge 0$).",
            r"\textbf{PASS}",
            r"0 nulls; 0 NaNs; 0 $\pm\infty$ (all 7,175 and 6,947 eligible rows); 100\% bound compliance.",
        ),
        (
            "Independent Audit (19/19)",
            r"Standalone audit suite (\texttt{audit\_stage3\_features\_targets.py}, zero builder imports) checking all origin counts and equations.",
            r"\textbf{PASS}",
            r"$19 / 19$ checks PASS (\texttt{exit 0}); eligible counts 2015--2021: 990, 990, 991, 992, 994, 995, 995.",
        ),
        (
            "Source-Data Preservation",
            r"Post-build and post-audit SHA-256 verification ensuring frozen Stage 2 datasets remain unaltered.",
            r"\textbf{PASS}",
            r"Byte-for-byte identical to frozen Stage 2 checksums.",
        ),
    ]

    tex_lines = [
        r"% Suggested Placement: Appendix A (Stage 3.1 Independent Audit Summary)",
        r"% Suggested Label: \label{tab:stage31-validation}",
        r"% Grounded in stage3_feature_target_audit_report.md (19/19 PASS) and stage3_feature_target_manifest.json",
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Summary of Stage 3.1 feature and target construction validation checks and independent leakage audit results}",
        r"\label{tab:stage31-validation}",
        r"\footnotesize",
        r"\setlength{\tabcolsep}{4pt}",
        r"\begin{tabular}{>{\raggedright\arraybackslash}p{2.45cm} >{\raggedright\arraybackslash}p{4.85cm} c >{\raggedright\arraybackslash}p{5.15cm}}",
        r"\toprule",
        r"\textbf{Validation Domain} & \textbf{Verification Scope} & \textbf{Status} & \textbf{Observed Audit Evidence} \\",
        r"\midrule",
    ]
    for dom, scope, status, ev in tex_rows:
        tex_lines.append(f"{dom} & {scope} & {status} & {ev} \\\\")
        tex_lines.append(r"\addlinespace[3pt]")
    if tex_lines[-1].startswith(r"\addlinespace"):
        tex_lines.pop()

    tex_lines += [
        r"\bottomrule",
        r"\end{tabular}",
        "",
        r"\vspace{4pt}",
        r"\parbox{14.8cm}{\scriptsize \textit{Notes:} Verified on \texttt{stage3\_origin\_features\_targets.csv} ($7{,}175 \times 42$; $6{,}947$ eligible observations across origins 2015--2021) at Git checkpoint \texttt{ffc1716}. All sensitivity counting bases (\texttt{M3-LogRCA}, \texttt{M2-WC}, \texttt{M3-WC}) match the Stage 3.1 manifest without post-hoc modification.}",
        r"\end{table}",
    ]
    (ASSETS_DIR / "table_a_stage3_1_validation_summary.tex").write_text(
        "\n".join(tex_lines) + "\n", encoding="utf-8"
    )


def main() -> int:
    for p in (CSV_PATH, MANIFEST_PATH, AUDIT_MD_PATH):
        if not p.exists():
            raise FileNotFoundError(f"Missing required Stage 3.1 verified artifact: {p}")

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    audit_text = AUDIT_MD_PATH.read_text(encoding="utf-8")
    df_stage3 = pd.read_csv(CSV_PATH)

    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    build_table_model_features(manifest, df_stage3)
    build_table_eligible_topics(manifest, df_stage3)
    build_table_validation_summary(manifest, audit_text, df_stage3)

    print("[PASS] Generated all 3 thesis tables (CSV + LaTeX) in stage3_modeling/thesis_assets/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
