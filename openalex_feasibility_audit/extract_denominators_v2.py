import os
from datetime import datetime, timezone
from pathlib import Path
import requests
import pandas as pd
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")
api_key = os.getenv('OPENALEX_API_KEY')
headers = {'User-Agent': 'ThesisAudit/1.0 (mailto:student@ue-germany.de)'}
if api_key:
    headers['Authorization'] = f'Bearer {api_key.strip("\"\'")}'

years = list(range(2010, 2025))
countries = ['DE', 'CN', 'JP']
records = []

print("Fetching All-Science Denominators for Selected Scholarly Work Types (2010-2024)...")
for yr in years:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    query_filter = f"publication_year:{yr},type:article|conference-paper|review"
    
    # 1. Global All-Science (Selected Scholarly Work Types)
    url_g = f"https://api.openalex.org/works?filter={query_filter}"
    rg = requests.get(url_g, headers=headers).json()
    glob_count = rg['meta']['count']
    
    row = {
        'year': yr,
        'retrieval_timestamp_utc': ts,
        'query_filter': query_filter,
        'global_allsci': glob_count
    }
    
    # 2. National All-Science (Selected Scholarly Work Types)
    for c in countries:
        url_c = f"https://api.openalex.org/works?filter=publication_year:{yr},authorships.institutions.country_code:{c},type:article|conference-paper|review&group_by=countries_distinct_count"
        rc = requests.get(url_c, headers=headers).json()
        groups = rc.get('group_by', [])
        
        whole = sum(g['count'] for g in groups)
        frac = sum(g['count'] / float(g['key']) for g in groups if float(g['key']) > 0)
        
        row[f'{c.lower()}_whole'] = whole
        row[f'{c.lower()}_frac'] = round(frac, 4)
        
    records.append(row)
    print(f"Year {yr} ({ts}): Global={glob_count}, DE={row['de_whole']}, CN={row['cn_whole']}, JP={row['jp_whole']}")

df = pd.DataFrame(records)
out_path = BASE_DIR / "openalex_feasibility_audit" / "all_science_national_denominators_fractional_v2_live_recheck_20261105.csv"
df.to_csv(out_path, index=False)
print(f"Saved {out_path} successfully!")
