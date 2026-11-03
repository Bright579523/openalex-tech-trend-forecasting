"""
OpenAlex Master Panel Production Extraction Script (1,025 Topics x 15 Years)
Methodology: Country-Level Equal Fractional Counting (Option C: 1/k) + Whole Counting Reference
Author: Bright / Thesis Project
Date: November 2026

Usage:
    python extract_master_panel_1025topics.py [--api-key YOUR_API_KEY] [--max-topics N]
"""

import os
import sys
import time
import argparse
from pathlib import Path
import requests
import pandas as pd
import numpy as np

MAILTO = "student@ue-germany.de"

def parse_args():
    parser = argparse.ArgumentParser(description="Extract 1,025-topic master panel from OpenAlex using Option C.")
    parser.add_argument("--api-key", default=os.environ.get("OPENALEX_API_KEY", ""), help="OpenAlex Free API Key")
    parser.add_argument("--max-topics", type=int, default=None, help="Limit number of topics for dry run")
    parser.add_argument("--delay", type=float, default=0.04, help="Delay between API requests in seconds")
    return parser.parse_args()

def main():
    args = parse_args()
    headers = {"User-Agent": f"ThesisMasterExtraction/1.0 (mailto:{MAILTO})"}
    if args.api_key:
        headers["Authorization"] = f"Bearer {args.api_key}"
        print(f"Using OpenAlex API Key authentication (Higher rate limits & 10,000 req/day allowance).")
    else:
        print(f"Running in Polite Pool without API Key (mailto:{MAILTO}).")

    base_dir = Path(__file__).resolve().parent
    audit_dir = base_dir / "openalex_feasibility_audit"
    proposal_dir = base_dir / "proposal_audit_csvs"
    
    # 1. Load Taxonomy (1,025 topics)
    tax_path = audit_dir / "all_tech_topics_taxonomy.csv"
    if not tax_path.exists():
        print(f"Error: Taxonomy file not found at {tax_path}")
        sys.exit(1)
        
    df_tax = pd.read_csv(tax_path)
    if args.max_topics:
        df_tax = df_tax.head(args.max_topics)
    print(f"Loaded {len(df_tax)} topics from taxonomy.")
    
    # 2. Load All-Science Denominators (2010-2024)
    allsci_path = audit_dir / "all_science_national_denominators_fractional.csv"
    if not allsci_path.exists():
        print(f"Error: All-Science denominators file not found at {allsci_path}")
        sys.exit(1)
        
    df_allsci = pd.read_csv(allsci_path).set_index("year")
    print("Loaded 15-year All-Science national denominators.")
    
    years = list(range(2010, 2025))
    output_rows = []
    
    t0 = time.time()
    total_topics = len(df_tax)
    api_calls_made = 0
    
    print("\nStarting extraction of 1,025 topics across 2010-2024...")
    print("Each topic requires 4 requests: Global, DE, CN, JP (all 15 years retrieved per request).")
    print("-" * 80)
    
    for idx, row in df_tax.iterrows():
        tid = row["topic_id"]
        tname = row["display_name"]
        field_name = row["field_name"]
        subfield_name = row["subfield_name"]
        
        # 1. Global counts across 15 years
        url_glob = "https://api.openalex.org/works"
        params_glob = {
            "filter": f"primary_topic.id:{tid},publication_year:2010-2024",
            "group_by": "publication_year"
        }
        try:
            r_glob = requests.get(url_glob, params=params_glob, headers=headers)
            api_calls_made += 1
            glob_groups = r_glob.json().get("group_by", [])
            glob_by_yr = {int(g["key"]): g["count"] for g in glob_groups if g["key"]}
        except Exception as e:
            print(f"  [Warning] Global {tid}: {e}")
            glob_by_yr = {}
            
        time.sleep(args.delay)
        
        # 2. Country counts for DE, CN, JP
        country_data = {"DE": {}, "CN": {}, "JP": {}}
        for c_code in ["DE", "CN", "JP"]:
            url_c = "https://api.openalex.org/works"
            params_c = {
                "filter": f"primary_topic.id:{tid},publication_year:2010-2024,authorships.institutions.country_code:{c_code}",
                "group_by": "publication_year,countries_distinct_count"
            }
            try:
                r_c = requests.get(url_c, params=params_c, headers=headers)
                api_calls_made += 1
                c_groups = r_c.json().get("group_by", [])
                for g in c_groups:
                    if not g.get("key"):
                        continue
                    yr = int(g["key"])
                    whole_c = g.get("count", 0)
                    frac_c = sum(sub["count"] / float(sub["key"]) for sub in g.get("groups", []) if float(sub.get("key", 1)) > 0)
                    country_data[c_code][yr] = {"whole": whole_c, "frac": frac_c}
            except Exception as e:
                print(f"  [Warning] {c_code} {tid}: {e}")
            time.sleep(args.delay)
            
        # Assemble 15 annual rows for this topic
        for y in years:
            p_glob = glob_by_yr.get(y, 0)
            glob_allsci = df_allsci.loc[y, "global_allsci"]
            
            row_dict = {
                "topic_id": tid,
                "topic_name": tname,
                "field_name": field_name,
                "subfield_name": subfield_name,
                "year": y,
                "global_count": p_glob
            }
            
            # For each country: record whole, frac, and compute whole RCA & frac RCA
            for c_code in ["de", "cn", "jp"]:
                C_CODE = c_code.upper()
                c_stat = country_data[C_CODE].get(y, {"whole": 0, "frac": 0.0})
                p_c_whole = c_stat["whole"]
                p_c_frac = c_stat["frac"]
                
                c_allsci_whole = df_allsci.loc[y, f"{c_code}_whole"]
                c_allsci_frac = df_allsci.loc[y, f"{c_code}_frac"]
                
                # Fractional RCA (Primary Feature)
                if p_glob > 0 and c_allsci_frac > 0:
                    rca_frac = (p_c_frac / c_allsci_frac) / (p_glob / glob_allsci)
                else:
                    rca_frac = 0.0
                    
                # Whole RCA (Reference Feature)
                if p_glob > 0 and c_allsci_whole > 0:
                    rca_whole = (p_c_whole / c_allsci_whole) / (p_glob / glob_allsci)
                else:
                    rca_whole = 0.0
                    
                row_dict[f"{c_code}_whole_count"] = p_c_whole
                row_dict[f"{c_code}_frac_count"] = round(p_c_frac, 2)
                row_dict[f"rca_frac_{c_code}"] = round(rca_frac, 4)
                row_dict[f"rca_whole_{c_code}"] = round(rca_whole, 4)
                
            output_rows.append(row_dict)
            
        if (idx + 1) % 50 == 0 or (idx + 1) == total_topics:
            elapsed = time.time() - t0
            rate = api_calls_made / elapsed if elapsed > 0 else 0
            pct = ((idx + 1) / total_topics) * 100
            print(f"Progress: [{idx+1:>4}/{total_topics}] ({pct:>5.1f}%) | Calls: {api_calls_made:>5} | Time: {elapsed:>5.1f}s | Speed: {rate:>4.1f} req/s")

    df_out = pd.DataFrame(output_rows)
    print("\n" + "=" * 80)
    print("EXTRACTION COMPLETED SUCCESSFULLY!")
    print(f"Total Rows Extracted: {len(df_out):,} rows ({df_out['topic_id'].nunique()} topics x {df_out['year'].nunique()} years)")
    print(f"Total API Calls:      {api_calls_made:,} calls in {time.time()-t0:.1f} seconds")
    
    # Save master panel to both locations
    out_file1 = audit_dir / "openalex_master_panel_1025topics.csv"
    out_file2 = proposal_dir / "openalex_master_panel_1025topics.csv"
    
    df_out.to_csv(out_file1, index=False)
    df_out.to_csv(out_file2, index=False)
    print(f"Saved Master Panel to:\n  - {out_file1}\n  - {out_file2}")
    print(f"File Size: {out_file1.stat().st_size / (1024*1024):.2f} MB")
    print("=" * 80)

if __name__ == "__main__":
    main()
