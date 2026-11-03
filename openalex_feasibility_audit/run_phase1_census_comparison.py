import requests
import json
import time
import pandas as pd
import numpy as np

MAILTO = "student@ue-germany.de"
HEADERS = {"User-Agent": f"ThesisFractionalAudit/1.0 (mailto:{MAILTO})"}

print("=" * 80)
print("PHASE 1: COMPLETE CENSUS BENCHMARK - COUNTRY-BASED VS AUTHOR-BASED FRACTIONAL")
print("=" * 80)

topics = [
    ("T12510", "Control & Systems Engineering"),
    ("T10586", "Robotics and Path Planning"),
    ("T10682", "Quantum Computing Algorithms"),
    ("T10181", "Natural Language Processing"),
    ("T10281", "Advanced Battery Materials")
]

countries = [("DE", "Germany"), ("CN", "China"), ("JP", "Japan")]
year = 2020

# Global All-Science and Global Topic counts
r_glob_as = requests.get(f"https://api.openalex.org/works?filter=publication_year:{year}", headers=HEADERS)
glob_allsci_total = r_glob_as.json()["meta"]["count"]

# National All-Science totals (Whole & Country-based Frac via Option C)
allsci_denoms = {}
for c_code, c_name in countries:
    url = "https://api.openalex.org/works"
    params = {
        "filter": f"publication_year:{year},authorships.institutions.country_code:{c_code}",
        "group_by": "countries_distinct_count"
    }
    r = requests.get(url, params=params, headers=HEADERS)
    groups = r.json().get("group_by", [])
    whole_tot = sum(g["count"] for g in groups)
    frac_c_tot = sum(g["count"] / float(g["key"]) for g in groups if float(g["key"]) > 0)
    allsci_denoms[c_code] = {"whole": whole_tot, "frac_country": frac_c_tot}

results = []

for tid, tname in topics:
    print(f"\nProcessing Topic {tid}: {tname} (Year {year})...")
    # Global topic count in 2020
    r_gt = requests.get(f"https://api.openalex.org/works?filter=primary_topic.id:{tid},publication_year:{year}", headers=HEADERS)
    glob_topic_count = r_gt.json()["meta"]["count"]
    
    for c_code, c_name in countries:
        # 1. Option C (Country-based) via GroupBy
        url_c = "https://api.openalex.org/works"
        params_c = {
            "filter": f"primary_topic.id:{tid},publication_year:{year},authorships.institutions.country_code:{c_code}",
            "group_by": "countries_distinct_count"
        }
        r_c = requests.get(url_c, params=params_c, headers=HEADERS)
        c_groups = r_c.json().get("group_by", [])
        whole_count = sum(g["count"] for g in c_groups)
        country_frac_count = sum(g["count"] / float(g["key"]) for g in c_groups if float(g["key"]) > 0)
        
        # 2. Author-based & Inst-based via Work-Level Pagination (Complete 100% census)
        cursor = "*"
        author_frac_sum = 0.0
        inst_frac_sum = 0.0
        fetched_works = 0
        
        while cursor:
            url_w = "https://api.openalex.org/works"
            params_w = {
                "filter": f"primary_topic.id:{tid},publication_year:{year},authorships.institutions.country_code:{c_code}",
                "select": "id,authorships,countries_distinct_count",
                "per_page": 100,
                "cursor": cursor
            }
            r_w = requests.get(url_w, params=params_w, headers=HEADERS)
            if r_w.status_code != 200:
                print(f"    [Error] cursor {cursor}: status {r_w.status_code}")
                break
                
            res_w = r_w.json()
            works = res_w.get("results", [])
            if not works:
                break
                
            fetched_works += len(works)
            for w in works:
                authorships = w.get("authorships", [])
                total_auth = len(authorships)
                c_auth = 0
                total_inst = 0
                c_inst = 0
                
                for a in authorships:
                    is_c = False
                    for inst in a.get("institutions", []):
                        total_inst += 1
                        if inst.get("country_code") == c_code:
                            c_inst += 1
                            is_c = True
                    if is_c:
                        c_auth += 1
                        
                k_val = w.get("countries_distinct_count", 1) or 1
                if total_auth > 0:
                    author_frac_sum += (c_auth / total_auth)
                else:
                    author_frac_sum += (1.0 / k_val)
                    
                if total_inst > 0:
                    inst_frac_sum += (c_inst / total_inst)
                else:
                    inst_frac_sum += (1.0 / k_val)
                    
            cursor = res_w.get("meta", {}).get("next_cursor")
            time.sleep(0.04)
            
        # RCA calculations
        rca_whole = (whole_count / allsci_denoms[c_code]["whole"]) / (glob_topic_count / glob_allsci_total) if glob_topic_count > 0 else 0
        rca_country = (country_frac_count / allsci_denoms[c_code]["frac_country"]) / (glob_topic_count / glob_allsci_total) if glob_topic_count > 0 else 0
        # For Author-based RCA: we use allsci_denoms frac_country as denominator approximation
        rca_author = (author_frac_sum / allsci_denoms[c_code]["frac_country"]) / (glob_topic_count / glob_allsci_total) if glob_topic_count > 0 else 0
        
        diff_auth_vs_country_pct = ((author_frac_sum - country_frac_count) / country_frac_count * 100) if country_frac_count > 0 else 0
        
        print(f"  {c_code:<2}: Works={fetched_works:>4} | Whole={whole_count:>4} | Country-Frac={country_frac_count:>7.2f} | Author-Frac={author_frac_sum:>7.2f} | Diff={diff_auth_vs_country_pct:>+5.1f}%")
        
        results.append({
            "topic_id": tid,
            "topic_name": tname,
            "country": c_code,
            "census_works": fetched_works,
            "whole_count": whole_count,
            "country_frac": round(country_frac_count, 2),
            "author_frac": round(author_frac_sum, 2),
            "inst_frac": round(inst_frac_sum, 2),
            "diff_auth_vs_ctry_pct": round(diff_auth_vs_country_pct, 1),
            "rca_whole": round(rca_whole, 3),
            "rca_country_frac": round(rca_country, 3),
            "rca_author_frac": round(rca_author, 3)
        })

df_res = pd.DataFrame(results)
df_res.to_csv("d:/Thesis/openalex_feasibility_audit/pilot_fractional_comparison_census.csv", index=False)
print("\n" + "=" * 80)
print("PHASE 1 CENSUS RESULTS SUMMARY TABLE:")
print("=" * 80)
print(df_res[["topic_id", "country", "whole_count", "country_frac", "author_frac", "diff_auth_vs_ctry_pct", "rca_whole", "rca_country_frac", "rca_author_frac"]].to_string(index=False))

corr_counts = df_res["country_frac"].corr(df_res["author_frac"])
corr_rca = df_res["rca_country_frac"].corr(df_res["rca_author_frac"])
mae_rca = (df_res["rca_country_frac"] - df_res["rca_author_frac"]).abs().mean()

print(f"\nPearson Correlation (Country-Frac vs Author-Frac Counts):  r = {corr_counts:.4f}")
print(f"Pearson Correlation (Country-Frac vs Author-Frac RCA):     r = {corr_rca:.4f}")
print(f"Mean Absolute Difference (Country RCA vs Author RCA):      MAE = {mae_rca:.4f}")

