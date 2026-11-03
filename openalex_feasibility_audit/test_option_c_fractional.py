import requests
import json
import time
import pandas as pd
import numpy as np

MAILTO = "student@ue-germany.de"
HEADERS = {"User-Agent": f"ThesisOptionCAudit/1.0 (mailto:{MAILTO})"}

print("=" * 80)
print("EMPIRICAL TEST OF OPTION C: AGGREGATED FRACTIONAL COUNTING IN OPENALEX")
print("=" * 80)

# -----------------------------------------------------------------------------
# STEP 1: Test 2D GroupBy API on 5 Diverse Sample Topics
# -----------------------------------------------------------------------------
print("\n--- STEP 1: API MULTI-FIELD GROUPBY INTEGRITY (5 TOPICS x 3 COUNTRIES) ---")
test_topics = [
    ("T10281", "Advanced Battery Materials"),
    ("T10181", "Natural Language Processing"),
    ("T10586", "Robotics and Path Planning"),
    ("T10682", "Quantum Computing Algorithms"),
    ("T12510", "Computational Engineering / Control")
]

step1_results = []
for tid, tname in test_topics:
    for c_code, c_name in [("DE", "Germany"), ("CN", "China"), ("JP", "Japan")]:
        url = "https://api.openalex.org/works"
        params = {
            "filter": f"primary_topic.id:{tid},publication_year:2010-2024,authorships.institutions.country_code:{c_code}",
            "group_by": "publication_year,countries_distinct_count"
        }
        r = requests.get(url, params=params, headers=HEADERS)
        if r.status_code != 200:
            print(f"  [ERROR] {tid} {c_code}: Status {r.status_code}")
            continue
            
        data = r.json()
        groups = data.get("group_by", [])
        
        # Check years completeness
        years_found = [g["key"] for g in groups]
        all_15_years = len(years_found) == 15
        
        # Check count conservation: sum of sub-groups == parent count
        conservation_perfect = True
        total_whole = 0
        total_fc = 0.0
        
        for g in groups:
            parent_count = g["count"]
            total_whole += parent_count
            sub_count_sum = sum(sub["count"] for sub in g.get("groups", []))
            if parent_count != sub_count_sum:
                conservation_perfect = False
            
            # Option C fractional sum: count / k
            for sub in g.get("groups", []):
                k = float(sub["key"])
                if k > 0:
                    total_fc += sub["count"] / k
                    
        ratio = total_fc / total_whole if total_whole > 0 else 1.0
        step1_results.append({
            "topic_id": tid,
            "topic_name": tname,
            "country": c_code,
            "years_count": len(years_found),
            "whole_count": total_whole,
            "frac_count": round(total_fc, 2),
            "deflation_ratio": round(ratio, 3),
            "conservation": conservation_perfect
        })
        time.sleep(0.05)

df_s1 = pd.DataFrame(step1_results)
print(df_s1.to_string(index=False))

# -----------------------------------------------------------------------------
# STEP 2: Ground Truth Comparison on Work-level Metadata (Sample 150 Works)
# -----------------------------------------------------------------------------
print("\n--- STEP 2: GROUND TRUTH VALIDATION (WORK-LEVEL METADATA SAMPLE) ---")
print("Sampling 50 works each from DE, CN, JP across technology topics...")

sample_comparisons = []
for c_code in ["DE", "CN", "JP"]:
    url = "https://api.openalex.org/works"
    params = {
        "filter": f"primary_topic.id:T10281,publication_year:2020-2023,authorships.institutions.country_code:{c_code}",
        "per_page": 50
    }
    r = requests.get(url, params=params, headers=HEADERS)
    works = r.json().get("results", [])
    
    for w in works:
        wid = w.get("id")
        k = w.get("countries_distinct_count", 1)
        if not k or k == 0:
            k = 1
            
        opt_c_weight = 1.0 / k
        
        authorships = w.get("authorships", [])
        total_authors = len(authorships)
        c_authors = 0
        
        total_insts = 0
        c_insts = 0
        
        for a in authorships:
            is_c = False
            for inst in a.get("institutions", []):
                total_insts += 1
                if inst.get("country_code") == c_code:
                    c_insts += 1
                    is_c = True
            if is_c:
                c_authors += 1
                
        author_weight = (c_authors / total_authors) if total_authors > 0 else opt_c_weight
        inst_weight = (c_insts / total_insts) if total_insts > 0 else opt_c_weight
        
        sample_comparisons.append({
            "work_id": wid,
            "country": c_code,
            "distinct_countries": k,
            "whole_weight": 1.0,
            "opt_c_weight": opt_c_weight,
            "author_weight": author_weight,
            "inst_weight": inst_weight
        })

df_s2 = pd.DataFrame(sample_comparisons)
print(f"Total sampled works analyzed: {len(df_s2)}")

for c_code in ["DE", "CN", "JP"]:
    df_c = df_s2[df_s2["country"] == c_code]
    print(f"\nCountry {c_code} (N={len(df_c)}):")
    print(f"  Whole Count Sum:           {df_c['whole_weight'].sum():.1f}")
    print(f"  Option C (1/k) Sum:        {df_c['opt_c_weight'].sum():.3f}")
    print(f"  Author-level Frac Sum:     {df_c['author_weight'].sum():.3f}")
    print(f"  Institution-level Frac Sum:{df_c['inst_weight'].sum():.3f}")
    
    # Correlation between Option C and Author-level Ground Truth
    corr_opt_author = df_c['opt_c_weight'].corr(df_c['author_weight'])
    corr_whole_author = df_c['whole_weight'].corr(df_c['author_weight'])
    mae_opt_author = (df_c['opt_c_weight'] - df_c['author_weight']).abs().mean()
    mae_whole_author = (df_c['whole_weight'] - df_c['author_weight']).abs().mean()
    
    print(f"  Correlation (Option C vs Author-GroundTruth):     r = {corr_opt_author:.4f} (MAE = {mae_opt_author:.4f})")
    print(f"  Comparison  (Whole Count vs Author-GroundTruth): MAE = {mae_whole_author:.4f}")

# -----------------------------------------------------------------------------
# STEP 3: Fractional RCA Consistency Check
# -----------------------------------------------------------------------------
print("\n--- STEP 3: FRACTIONAL RCA VS WHOLE COUNT RCA CONSISTENCY CHECK ---")

# Let's fetch national all-science totals for Whole and Fractional
allsci_totals = {}
for c_code in ["DE", "CN", "JP"]:
    url = "https://api.openalex.org/works"
    params = {
        "filter": f"publication_year:2020,authorships.institutions.country_code:{c_code}",
        "group_by": "countries_distinct_count"
    }
    r = requests.get(url, params=params, headers=HEADERS)
    groups = r.json().get("group_by", [])
    whole_tot = sum(g["count"] for g in groups)
    frac_tot = sum(g["count"] / float(g["key"]) for g in groups if float(g["key"]) > 0)
    allsci_totals[c_code] = {"whole": whole_tot, "frac": frac_tot}

# Global all-science 2020
r_glob = requests.get("https://api.openalex.org/works?filter=publication_year:2020", headers=HEADERS)
glob_total_2020 = r_glob.json()["meta"]["count"]

print(f"Global All-Science 2020 Works: {glob_total_2020:,}")
for c, d in allsci_totals.items():
    print(f"  {c}: Whole All-Science = {d['whole']:,} | Frac All-Science = {d['frac']:,.2f} (Ratio = {d['frac']/d['whole']:.3f})")

# Calculate RCA for the 5 sample topics in 2020 under both Whole and Fractional
rca_comp = []
for tid, tname in test_topics:
    # Get global count for topic in 2020
    r_gt = requests.get(f"https://api.openalex.org/works?filter=primary_topic.id:{tid},publication_year:2020", headers=HEADERS)
    p_glob = r_gt.json()["meta"]["count"]
    
    for c_code in ["DE", "CN", "JP"]:
        row = df_s1[(df_s1["topic_id"] == tid) & (df_s1["country"] == c_code)].iloc[0]
        # Query 2020 specific counts for this topic
        r_c = requests.get(
            f"https://api.openalex.org/works?filter=primary_topic.id:{tid},publication_year:2020,authorships.institutions.country_code:{c_code}&group_by=countries_distinct_count",
            headers=HEADERS
        )
        c_groups = r_c.json().get("group_by", [])
        p_c_whole = sum(g["count"] for g in c_groups)
        p_c_frac = sum(g["count"] / float(g["key"]) for g in c_groups if float(g["key"]) > 0)
        
        # Whole RCA
        rca_whole = (p_c_whole / allsci_totals[c_code]["whole"]) / (p_glob / glob_total_2020) if p_glob > 0 else 0
        # Fractional RCA
        rca_frac = (p_c_frac / allsci_totals[c_code]["frac"]) / (p_glob / glob_total_2020) if p_glob > 0 else 0
        
        rca_comp.append({
            "topic_id": tid,
            "topic_name": tname,
            "country": c_code,
            "p_c_whole": p_c_whole,
            "p_c_frac": round(p_c_frac, 2),
            "rca_whole": round(rca_whole, 3),
            "rca_frac": round(rca_frac, 3),
            "diff_pct": round(((rca_frac - rca_whole) / rca_whole * 100) if rca_whole > 0 else 0, 1)
        })

df_rca = pd.DataFrame(rca_comp)
print("\nComparison of Whole RCA vs Fractional RCA (Year 2020):")
print(df_rca.to_string(index=False))

corr_rca = df_rca["rca_whole"].corr(df_rca["rca_frac"])
print(f"\nOverall Pearson Correlation between Whole RCA and Fractional RCA across topics: r = {corr_rca:.4f}")

