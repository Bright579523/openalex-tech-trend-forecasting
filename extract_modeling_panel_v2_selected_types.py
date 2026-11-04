"""
OpenAlex Modeling Panel v2 Extraction Script (Selected Types)
Document Scope: Articles, Conference Papers, and Reviews (type:article|conference-paper|review)
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
LOG_FILE = AUDIT_DIR / "extraction_run_v2.log"
CHECKPOINT_FILE = AUDIT_DIR / "checkpoint_v2_extraction.json"
DENOM_FILE = AUDIT_DIR / "all_science_national_denominators_fractional_v2_selected_types.csv"
OUTPUT_PANEL_CSV = AUDIT_DIR / "openalex_modeling_panel_1025topics_v2_selected_types.csv"

DOC_TYPE_FILTER = "type:article|conference-paper|review"

def get_secure_api_key(cmd_arg_key: str = "") -> str:
    if cmd_arg_key:
        return cmd_arg_key.strip()
    if os.environ.get("OPENALEX_API_KEY"):
        return os.environ.get("OPENALEX_API_KEY").strip()
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

class DataIntegrityError(Exception):
    pass

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

def extract_and_validate_topic_v2(tid: str, tname: str, field_name: str, subfield_name: str, 
                                  headers: dict, df_allsci: pd.DataFrame, delay: float = 0.04):
    retrieval_time = datetime.datetime.now().isoformat()
    years = list(range(2010, 2025))
    
    # 1. Global Counts across 15 years (Filtered by selected doc types)
    url_glob = "https://api.openalex.org/works"
    params_glob = {
        "filter": f"primary_topic.id:{tid},publication_year:2010-2024,{DOC_TYPE_FILTER}",
        "group_by": "publication_year"
    }
    data_glob, hdrs_glob = fetch_with_retry(url_glob, params_glob, headers)
    groups_glob = data_glob.get("group_by", [])
    meta_glob = data_glob.get("meta", {}).get("count", 0)
    sum_glob = sum(g["count"] for g in groups_glob)
    
    if meta_glob != sum_glob:
        err = f"Global Completeness Mismatch for {tid}: meta={meta_glob} != sum_groups={sum_glob}"
        log_msg(f"  [FAIL-FAST] {err}")
        raise DataIntegrityError(err)
        
    glob_by_year = {int(g["key"]): g["count"] for g in groups_glob if g.get("key") is not None}
    
    # 2. National 2D Aggregation across 15 years for DE, CN, JP
    country_data = {}
    countries = ["DE", "CN", "JP"]
    
    for c_code in countries:
        time.sleep(delay)
        params_c = {
            "filter": f"primary_topic.id:{tid},publication_year:2010-2024,authorships.institutions.country_code:{c_code},{DOC_TYPE_FILTER}",
            "group_by": "publication_year,countries_distinct_count"
        }
        data_c, hdrs_c = fetch_with_retry(url_glob, params_c, headers)
        meta_c = data_c.get("meta", {}).get("count", 0)
        groups_c = data_c.get("group_by", [])
        
        sum_parent = sum(g["count"] for g in groups_c)
        sum_nested = sum(sum(sub["count"] for sub in g.get("groups", [])) for g in groups_c)
        
        if meta_c != sum_parent or meta_c != sum_nested:
            err = f"Country {c_code} 2D Mismatch for {tid}: meta={meta_c}, sum_parent={sum_parent}, sum_nested={sum_nested}"
            log_msg(f"  [FAIL-FAST] {err}")
            raise DataIntegrityError(err)
            
        c_by_year = {}
        for parent_g in groups_c:
            if parent_g.get("key") is None:
                continue
            yr = int(parent_g["key"])
            w_count = parent_g["count"]
            f_count = 0.0
            for sub_g in parent_g.get("groups", []):
                k = float(sub_g["key"])
                if k > 0:
                    f_count += sub_g["count"] / k
            c_by_year[yr] = {"whole": w_count, "frac": f_count}
            
        country_data[c_code] = c_by_year

    # 3. Assemble 15 Annual Records with Exact Denominators and RCA Formulas
    topic_records = []
    for yr in years:
        row_allsci = df_allsci[df_allsci["year"] == yr].iloc[0]
        glob_allsci = float(row_allsci["global_allsci"])
        
        p_glob = int(glob_by_year.get(yr, 0))
        
        record = {
            "topic_id": tid,
            "topic_name": tname,
            "field_name": field_name,
            "subfield_name": subfield_name,
            "year": yr,
            "retrieval_timestamp": retrieval_time,
            "global_count": p_glob,
            "global_allsci_denom": int(glob_allsci)
        }
        
        for c_code in ["DE", "CN", "JP"]:
            c_code_l = c_code.lower()
            c_stat = country_data[c_code].get(yr, {"whole": 0, "frac": 0.0})
            p_c_whole = int(c_stat["whole"])
            p_c_frac = float(c_stat["frac"])
            
            c_allsci_whole = float(row_allsci[f"{c_code_l}_whole"])
            c_allsci_frac = float(row_allsci[f"{c_code_l}_frac"])
            
            # Exact Fractional RCA Formula
            if p_glob > 0 and c_allsci_frac > 0 and p_c_frac > 0:
                rca_frac = (p_c_frac / c_allsci_frac) / (p_glob / glob_allsci)
            else:
                rca_frac = 0.0
                
            # Exact Whole RCA Formula
            if p_glob > 0 and c_allsci_whole > 0 and p_c_whole > 0:
                rca_whole = (p_c_whole / c_allsci_whole) / (p_glob / glob_allsci)
            else:
                rca_whole = 0.0
                
            record[f"{c_code_l}_whole_count"] = p_c_whole
            # Store fractional count with 6 decimal places to eliminate intermediate rounding error
            record[f"{c_code_l}_frac_count"] = round(p_c_frac, 6)
            record[f"{c_code_l}_allsci_whole_denom"] = int(c_allsci_whole)
            record[f"{c_code_l}_allsci_frac_denom"] = round(c_allsci_frac, 4)
            record[f"rca_frac_{c_code_l}"] = round(rca_frac, 5)
            record[f"rca_whole_{c_code_l}"] = round(rca_whole, 5)
            
        topic_records.append(record)
        
    return topic_records

def run_v2_extraction(args):
    api_key = get_secure_api_key(args.api_key)
    masked = mask_key(api_key) if api_key else "None (Unauthenticated)"
    log_msg(f"Initiating Modeling Panel v2 Extraction (Selected Types: article|conference-paper|review)")
    log_msg(f"Authenticated Key: {masked}")
    
    headers = {"User-Agent": f"ThesisMasterExtractionV2/1.0 (mailto:{MAILTO})"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
        
    # Check rate limit
    try:
        r_chk = requests.get("https://api.openalex.org/works?filter=publication_year:2020", headers=headers, timeout=10)
        daily_lim = r_chk.headers.get("X-RateLimit-Limit", "Unknown")
        rem_lim = r_chk.headers.get("X-RateLimit-Remaining", "Unknown")
        log_msg(f"API Rate Limits -> Limit: {daily_lim} calls/day | Remaining: {rem_lim} calls")
    except Exception as e:
        log_msg(f"Warning: Could not check rate limit header: {e}")
        
    # Load Denominators
    if not DENOM_FILE.exists():
        raise FileNotFoundError(f"Missing denominator file: {DENOM_FILE}")
    df_allsci = pd.read_csv(DENOM_FILE)
    log_msg(f"Loaded v2 All-Science Denominators from {DENOM_FILE} ({len(df_allsci)} years).")
    
    # Load 1,025 Topics Taxonomy
    tax_path = AUDIT_DIR / "all_tech_topics_taxonomy.csv"
    if not tax_path.exists():
        raise FileNotFoundError(f"Missing taxonomy file: {tax_path}")
    df_topics = pd.read_csv(tax_path)
    total_topics = len(df_topics)
    log_msg(f"Loaded {total_topics} topics from {tax_path}.")
    
    if args.limit and args.limit > 0:
        df_topics = df_topics.head(args.limit)
        log_msg(f"Execution limited to first {len(df_topics)} topics by --limit {args.limit}.")
        
    # Checkpoint setup
    processed_records = []
    completed_topics = set()
    if CHECKPOINT_FILE.exists() and not args.force:
        try:
            with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
                ckpt_data = json.load(f)
                completed_topics = set(ckpt_data.get("completed_topics", []))
                processed_records = ckpt_data.get("records", [])
                log_msg(f"Resuming from checkpoint: {len(completed_topics)} topics already completed ({len(processed_records)} rows).")
        except Exception as e:
            log_msg(f"Could not read checkpoint, starting fresh: {e}")
            
    t0 = time.time()
    extracted_now = 0
    
    for idx, row in df_topics.iterrows():
        tid = row["topic_id"]
        tname = row.get("display_name", row.get("topic_name", ""))
        fname = row.get("field_name", "")
        sfname = row.get("subfield_name", "")
        
        if tid in completed_topics:
            continue
            
        try:
            topic_rows = extract_and_validate_topic_v2(tid, tname, fname, sfname, headers, df_allsci, delay=args.delay)
            processed_records.extend(topic_rows)
            completed_topics.add(tid)
            extracted_now += 1
            
            # Save checkpoint every 25 topics or on last
            if extracted_now % 25 == 0 or idx == len(df_topics) - 1:
                with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
                    json.dump({"completed_topics": list(completed_topics), "records": processed_records}, f)
                elapsed = time.time() - t0
                log_msg(f"Progress: [{len(completed_topics)}/{len(df_topics)}] topics ({len(processed_records)} rows) | Elapsed: {elapsed:.1f}s")
                
        except DataIntegrityError as die:
            log_msg(f"CRITICAL DATA INTEGRITY ERROR for topic {tid}: {die}")
            raise
        except Exception as ex:
            log_msg(f"Unexpected error on topic {tid}: {ex}")
            raise
            
    # Save Final Dataset
    df_final = pd.DataFrame(processed_records)
    df_final.to_csv(OUTPUT_PANEL_CSV, index=False)
    log_msg(f"Saved {len(df_final)} rows to {OUTPUT_PANEL_CSV}")
    
    if len(completed_topics) == len(df_topics) and CHECKPOINT_FILE.exists():
        try:
            CHECKPOINT_FILE.unlink()
            log_msg("Cleaned up checkpoint file after successful completion.")
        except Exception:
            pass
    
    # Run Structural & Precision Validation
    validate_dataset(df_final)

def validate_dataset(df: pd.DataFrame):
    log_msg("=== FINAL AUDIT & VALIDATION OF MODELING PANEL V2 ===")
    rows_passed = (len(df) == 15375) or (len(df) > 0 and len(df) % 15 == 0)
    log_msg(f"1. Total Row Count: {len(df)} | Status: {'PASS' if rows_passed else 'CHECK'}")
    
    dup_count = df.duplicated(subset=["topic_id", "year"]).sum()
    log_msg(f"2. Duplicate Topic-Years: {dup_count} | Status: {'PASS' if dup_count == 0 else 'FAIL'}")
    
    null_count = df.isnull().sum().sum()
    log_msg(f"3. Missing / Null Values: {null_count} | Status: {'PASS' if null_count == 0 else 'FAIL'}")
    
    # Recalculate RCA and check maximum discrepancy
    for c in ["de", "cn", "jp"]:
        calc_rca_frac = np.where(
            (df['global_count'] > 0) & (df[f'{c}_allsci_frac_denom'] > 0) & (df[f'{c}_frac_count'] > 0),
            (df[f'{c}_frac_count'] / df[f'{c}_allsci_frac_denom']) / (df['global_count'] / df['global_allsci_denom']),
            0.0
        )
        diff = np.abs(calc_rca_frac - df[f'rca_frac_{c}'])
        max_diff = diff.max()
        log_msg(f"4. Recalculation Discrepancy RCA Frac {c.upper()}: {max_diff:.8f} | Bound <= 0.00000500: {'PASS' if max_diff <= 0.000005001 else 'CHECK'}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract OpenAlex Modeling Panel v2 (Selected Types)")
    parser.add_argument("--api-key", type=str, default="", help="OpenAlex API key")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of topics for dry run")
    parser.add_argument("--delay", type=float, default=0.03, help="Delay between country queries")
    parser.add_argument("--force", action="store_true", help="Force restart from scratch")
    args = parser.parse_args()
    
    run_v2_extraction(args)

