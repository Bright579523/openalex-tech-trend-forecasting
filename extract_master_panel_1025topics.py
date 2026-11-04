"""
OpenAlex Master Panel Production Extraction & Data Quality Audit
Universe: 1,025 Technology Topics across 15 Annual Intervals (2010–2024)
Primary Attribution: Country-Level Equal Fractional Counting (Option C: 1/k)
Reference Baseline: Whole Counting
Primary Feature: Fractional All-Science RCA (RCA_Frac)

Fail-Fast Completeness Check:
    meta.count == sum(parent group counts) == sum(nested subgroup counts)

Author: Bright / M.Sc. Data Science Thesis Project
Date: November 2026
"""

import os
import sys
import time
import json
import argparse
import datetime
from pathlib import Path
import requests
import pandas as pd
import numpy as np

MAILTO = "student@ue-germany.de"
BASE_DIR = Path(__file__).resolve().parent
AUDIT_DIR = BASE_DIR / "openalex_feasibility_audit"
LOG_FILE = AUDIT_DIR / "extraction_run.log"

def get_secure_api_key(cmd_arg_key: str = "") -> str:
    # 1. Command-line argument
    if cmd_arg_key:
        return cmd_arg_key.strip()
    # 2. Environment variable
    if os.environ.get("OPENALEX_API_KEY"):
        return os.environ.get("OPENALEX_API_KEY").strip()
    # 3. Secure local .env file (excluded from Git and backups)
    env_path = BASE_DIR / ".env"
    if env_path.exists():
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("OPENALEX_API_KEY="):
                        val = line.split("=", 1)[1].strip()
                        return val.strip("\"'")
        except Exception as e:
            log_msg(f"Could not read .env: {e}")
    return ""

def mask_key(k: str) -> str:
    if len(k) <= 8:
        return "***"
    return f"{k[:4]}...{k[-4:]}"

def log_msg(msg: str):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{timestamp}] {msg}"
    print(formatted)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(formatted + "\n")

def fetch_with_retry(url: str, params: dict, headers: dict, max_retries: int = 4, backoff: float = 1.0):
    for attempt in range(1, max_retries + 1):
        try:
            r = requests.get(url, params=params, headers=headers, timeout=20)
            if r.status_code == 200:
                return r.json(), r.headers
            elif r.status_code == 429:
                reset_wait = int(r.headers.get("X-RateLimit-Reset", 5))
                log_msg(f"  [Rate Limit 429] Waiting {reset_wait}s (attempt {attempt}/{max_retries})...")
                time.sleep(reset_wait + 1)
            elif r.status_code == 401:
                log_msg(f"  [Auth 401] Unauthorized on {url}: {r.text[:200]}")
                raise DataIntegrityError(f"OpenAlex 401 Unauthorized: {r.text[:200]}")
            else:
                log_msg(f"  [HTTP {r.status_code}] Attempt {attempt}/{max_retries} on {url}: {r.text[:150]}")
                time.sleep(backoff * (2 ** (attempt - 1)))
        except requests.exceptions.RequestException as e:
            log_msg(f"  [Network Error] Attempt {attempt}/{max_retries}: {e}")
            time.sleep(backoff * (2 ** (attempt - 1)))
            
    raise DataIntegrityError(f"Failed to fetch {url} with params {params} after {max_retries} retries.")

def extract_and_validate_topic(tid: str, tname: str, field_name: str, subfield_name: str, 
                               headers: dict, df_allsci: pd.DataFrame, delay: float = 0.04):
    retrieval_time = datetime.datetime.now().isoformat()
    years = list(range(2010, 2025))
    
    # -------------------------------------------------------------------------
    # 1. Global Counts across 15 years
    # -------------------------------------------------------------------------
    url_glob = "https://api.openalex.org/works"
    params_glob = {
        "filter": f"primary_topic.id:{tid},publication_year:2010-2024",
        "group_by": "publication_year"
    }
    data_glob, hdrs_glob = fetch_with_retry(url_glob, params_glob, headers)
    meta_glob = data_glob.get("meta", {}).get("count", 0)
    groups_glob = data_glob.get("group_by", [])
    
    # Fail-fast check for Global query
    sum_parent_glob = sum(g["count"] for g in groups_glob)
    if meta_glob != sum_parent_glob:
        err = f"FAIL-FAST MISMATCH (Global {tid}): meta.count ({meta_glob}) != sum(parent) ({sum_parent_glob})"
        log_msg(f"  [ERROR] {err}")
        raise DataIntegrityError(err)
        
    glob_by_yr = {int(g["key"]): g["count"] for g in groups_glob if g.get("key")}
    time.sleep(delay)
    
    # -------------------------------------------------------------------------
    # 2. Country Counts for DE, CN, JP with 2D GroupBy & Fail-Fast Check
    # -------------------------------------------------------------------------
    country_data = {"DE": {}, "CN": {}, "JP": {}}
    for c_code in ["DE", "CN", "JP"]:
        url_c = "https://api.openalex.org/works"
        params_c = {
            "filter": f"primary_topic.id:{tid},publication_year:2010-2024,authorships.institutions.country_code:{c_code}",
            "group_by": "publication_year,countries_distinct_count"
        }
        data_c, hdrs_c = fetch_with_retry(url_c, params_c, headers)
        meta_c = data_c.get("meta", {}).get("count", 0)
        c_groups = data_c.get("group_by", [])
        
        sum_parent_c = sum(g["count"] for g in c_groups)
        sum_sub_c = sum(sum(sub["count"] for sub in g.get("groups", [])) for g in c_groups)
        
        # Strict Fail-Fast Check: meta.count == sum(parent) == sum(sub)
        if (meta_c != sum_parent_c) or (sum_parent_c != sum_sub_c):
            err = (f"FAIL-FAST MISMATCH ({c_code} {tid}): meta.count ({meta_c}) "
                   f"!= sum(parent) ({sum_parent_c}) != sum(sub) ({sum_sub_c})")
            log_msg(f"  [ERROR] {err}")
            log_msg(f"  Query Params: {params_c}")
            raise DataIntegrityError(err)
            
        for g in c_groups:
            if not g.get("key"):
                continue
            yr = int(g["key"])
            whole_c = g.get("count", 0)
            
            # Check for invalid k <= 0
            frac_c = 0.0
            for sub in g.get("groups", []):
                k_val = float(sub.get("key", 1))
                if k_val <= 0:
                    k_val = 1.0
                frac_c += (sub["count"] / k_val)
                
            country_data[c_code][yr] = {"whole": whole_c, "frac": frac_c}
        time.sleep(delay)
        
    # -------------------------------------------------------------------------
    # 3. Assemble 15 Annual Records with Exact Denominators and RCA Formulas
    # -------------------------------------------------------------------------
    topic_rows = []
    for y in years:
        p_glob = glob_by_yr.get(y, 0)
        glob_allsci = df_allsci.loc[y, "global_allsci"]
        
        record = {
            "topic_id": tid,
            "topic_name": tname,
            "field_name": field_name,
            "subfield_name": subfield_name,
            "year": y,
            "retrieval_timestamp": retrieval_time,
            "global_count": p_glob,
            "global_allsci_denom": glob_allsci
        }
        
        for c_code in ["de", "cn", "jp"]:
            C_CODE = c_code.upper()
            c_stat = country_data[C_CODE].get(y, {"whole": 0, "frac": 0.0})
            p_c_whole = c_stat["whole"]
            p_c_frac = c_stat["frac"]
            
            c_allsci_whole = df_allsci.loc[y, f"{c_code}_whole"]
            c_allsci_frac = df_allsci.loc[y, f"{c_code}_frac"]
            
            # Exact Fractional RCA Formula
            # Both national topic volume and national all-science volume use 1/k fractional counting
            if p_glob > 0 and c_allsci_frac > 0 and p_c_frac > 0:
                rca_frac = (p_c_frac / c_allsci_frac) / (p_glob / glob_allsci)
            else:
                rca_frac = 0.0
                
            # Exact Whole RCA Formula (Preserved for sensitivity comparison)
            if p_glob > 0 and c_allsci_whole > 0 and p_c_whole > 0:
                rca_whole = (p_c_whole / c_allsci_whole) / (p_glob / glob_allsci)
            else:
                rca_whole = 0.0
                
            record[f"{c_code}_whole_count"] = p_c_whole
            record[f"{c_code}_frac_count"] = round(p_c_frac, 4)
            record[f"{c_code}_allsci_whole_denom"] = c_allsci_whole
            record[f"{c_code}_allsci_frac_denom"] = c_allsci_frac
            record[f"rca_frac_{c_code}"] = round(rca_frac, 5)
            record[f"rca_whole_{c_code}"] = round(rca_whole, 5)
            
        topic_rows.append(record)
        
    return topic_rows

def run_post_extraction_validation(df: pd.DataFrame, expected_topics: int = 1025):
    log_msg("\n" + "=" * 80)
    log_msg("STARTING COMPREHENSIVE DATA QUALITY AUDIT ON FINAL MASTER PANEL")
    log_msg("=" * 80)
    
    expected_rows = expected_topics * 15
    actual_rows = len(df)
    unique_topics = df["topic_id"].nunique()
    unique_years = df["year"].nunique()
    
    # 1. Row counts check
    rows_passed = (actual_rows == expected_rows)
    log_msg(f"1. Row Counts: Expected {expected_rows:,} | Actual {actual_rows:,} | Verdict: {'PASS' if rows_passed else 'FAIL'}")
    log_msg(f"   Topics: {unique_topics}/{expected_topics} | Years: {unique_years}/15 (2010–2024)")
    
    # 2. Duplicate topic-year check
    dup_count = int(df.duplicated(subset=["topic_id", "year"]).sum())
    dup_passed = (dup_count == 0)
    log_msg(f"2. Duplicate Topic-Year Records: {dup_count} | Verdict: {'PASS' if dup_passed else 'FAIL'}")
    
    # 3. Missing values check
    missing_by_col = df.isna().sum()
    total_missing = int(missing_by_col.sum())
    missing_passed = (total_missing == 0)
    log_msg(f"3. Missing Values: Total {total_missing} nulls across {len(df.columns)} columns | Verdict: {'PASS' if missing_passed else 'FAIL'}")
    if total_missing > 0:
        log_msg("   Missing columns detail:\n" + missing_by_col[missing_by_col > 0].to_string())
        
    # 4. Invalid RCA calculation check (inf, -inf, NaN, negative)
    rca_cols = [c for c in df.columns if "rca_" in c]
    rca_invalid_count = 0
    for rc in rca_cols:
        invalid_mask = np.isinf(df[rc]) | np.isnan(df[rc]) | (df[rc] < 0)
        invalid_in_col = int(invalid_mask.sum())
        rca_invalid_count += invalid_in_col
        if invalid_in_col > 0:
            log_msg(f"   [Alert] Column {rc} has {invalid_in_col} invalid/infinite values.")
            
    rca_passed = (rca_invalid_count == 0)
    log_msg(f"4. Invalid RCA Values (inf, -inf, NaN, <0): {rca_invalid_count} | Verdict: {'PASS' if rca_passed else 'FAIL'}")
    
    # 5. Numerical sanity statistics
    log_msg("\n5. Numerical Summary of Features & Denominators:")
    num_cols = ["global_count", "de_frac_count", "cn_frac_count", "jp_frac_count", "rca_frac_de", "rca_frac_cn", "rca_frac_jp"]
    summary_txt = df[num_cols].describe().round(3).to_string()
    log_msg(summary_txt)
    
    all_passed = rows_passed and dup_passed and missing_passed and rca_passed
    log_msg("-" * 80)
    log_msg(f"OVERALL FINAL DATA QUALITY AUDIT DECISION: {'PASSED & FROZEN' if all_passed else 'FAILED'}")
    log_msg("=" * 80)
    
    # Save machine-readable audit report
    audit_report = {
        "timestamp": datetime.datetime.now().isoformat(),
        "total_rows": actual_rows,
        "expected_rows": expected_rows,
        "unique_topics": unique_topics,
        "unique_years": unique_years,
        "duplicate_rows": dup_count,
        "missing_values": total_missing,
        "invalid_rca_values": rca_invalid_count,
        "audit_decision": "PASS" if all_passed else "FAIL",
        "primary_counting": "Country-Level Equal Fractional Counting (1/k)",
        "reference_counting": "Whole Counting",
        "rca_primary_feature": "Fractional All-Science RCA"
    }
    with open(AUDIT_DIR / "final_data_quality_audit.json", "w", encoding="utf-8") as f:
        json.dump(audit_report, f, indent=2)
        
    return all_passed

def main():
    parser = argparse.ArgumentParser(description="Controlled Master Panel Extraction")
    parser.add_argument("--api-key", default="", help="OpenAlex API Key")
    parser.add_argument("--max-topics", type=int, default=None, help="Limit number of topics")
    parser.add_argument("--checkpoint-interval", type=int, default=25, help="Save intermediate progress every N topics")
    args = parser.parse_args()
    
    api_key = get_secure_api_key(args.api_key)
    headers = {"User-Agent": f"ThesisMasterExtraction/1.0 (mailto:{MAILTO})"}
    
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
        log_msg(f"Running with secure OpenAlex API Key: {mask_key(api_key)}")
        # Verify rate limits at startup
        try:
            r_chk = requests.get("https://api.openalex.org/works?per_page=1", headers=headers, timeout=10)
            lim = r_chk.headers.get("X-RateLimit-Limit", "Unknown")
            rem = r_chk.headers.get("X-RateLimit-Remaining", "Unknown")
            log_msg(f"API Quota Verified: Daily Limit = {lim} calls | Remaining Today = {rem} calls")
        except Exception as e:
            log_msg(f"Could not verify rate limit headers: {e}")
    else:
        log_msg("Running in Polite Pool without API Key.")
        
    tax_path = AUDIT_DIR / "all_tech_topics_taxonomy.csv"
    allsci_path = AUDIT_DIR / "all_science_national_denominators_fractional.csv"
    
    df_tax = pd.read_csv(tax_path)
    df_allsci = pd.read_csv(allsci_path).set_index("year")
    
    if args.max_topics:
        df_tax = df_tax.head(args.max_topics)
        
    total_topics = len(df_tax)
    log_msg(f"Loaded {total_topics} topics to extract.")
    
    checkpoint_csv = AUDIT_DIR / "master_panel_checkpoint.csv"
    extracted_topic_ids = set()
    all_rows = []
    
    if checkpoint_csv.exists():
        try:
            df_ckpt = pd.read_csv(checkpoint_csv)
            extracted_topic_ids = set(df_ckpt["topic_id"].unique())
            all_rows = df_ckpt.to_dict("records")
            log_msg(f"Resumed from checkpoint: {len(extracted_topic_ids)} topics ({len(all_rows)} rows) already extracted.")
        except Exception as e:
            log_msg(f"Could not load checkpoint: {e}. Starting fresh.")
            
    t0 = time.time()
    completed_topics = len(extracted_topic_ids)
    
    try:
        for idx, row in df_tax.iterrows():
            tid = row["topic_id"]
            if tid in extracted_topic_ids:
                continue
                
            tname = row["display_name"]
            field_name = row["field_name"]
            subfield_name = row["subfield_name"]
            
            topic_records = extract_and_validate_topic(
                tid=tid,
                tname=tname,
                field_name=field_name,
                subfield_name=subfield_name,
                headers=headers,
                df_allsci=df_allsci,
                delay=0.03
            )
            
            all_rows.extend(topic_records)
            extracted_topic_ids.add(tid)
            completed_topics += 1
            
            # Progress print
            if completed_topics % 10 == 0 or completed_topics == total_topics:
                elapsed = time.time() - t0
                pct = (completed_topics / total_topics) * 100
                log_msg(f"Progress: [{completed_topics:>4}/{total_topics}] ({pct:>5.1f}%) | Time: {elapsed:.1f}s")
                
            # Periodic Checkpoint
            if completed_topics % args.checkpoint_interval == 0 or completed_topics == total_topics:
                pd.DataFrame(all_rows).to_csv(checkpoint_csv, index=False)
                
    except Exception as e:
        log_msg(f"\n[CRITICAL ERROR / STOPPED] Extraction interrupted: {e}")
        pd.DataFrame(all_rows).to_csv(checkpoint_csv, index=False)
        log_msg(f"Checkpoint saved ({len(extracted_topic_ids)} topics). Re-run script to resume.")
        sys.exit(1)
        
    # Save Final Master Panel
    df_final = pd.DataFrame(all_rows)
    final_csv = AUDIT_DIR / "openalex_master_panel_1025topics.csv"
    df_final.to_csv(final_csv, index=False)
    log_msg(f"Saved master dataset to {final_csv}")
    
    # Run Final Quality Audit
    run_post_extraction_validation(df_final, expected_topics=total_topics)
    
    # Clean up checkpoint on full completion
    if completed_topics == total_topics and checkpoint_csv.exists():
        checkpoint_csv.unlink()
        log_msg("Full universe completed: Checkpoint file cleaned up.")

if __name__ == "__main__":
    main()
