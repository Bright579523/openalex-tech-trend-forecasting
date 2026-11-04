import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('OPENALEX_API_KEY')
headers = {'User-Agent': 'ThesisAudit/1.0 (mailto:student@ue-germany.de)'}
if api_key:
    headers['Authorization'] = f'Bearer {api_key}'

url = 'https://api.openalex.org/works'

# 1. Global topic comparison
params_all = {'filter': 'primary_topic.id:T10281,publication_year:2020'}
params_types = {'filter': 'primary_topic.id:T10281,publication_year:2020,type:article|conference-paper|review'}

r1 = requests.get(url, params=params_all, headers=headers).json()
r2 = requests.get(url, params=params_types, headers=headers).json()

c_all = r1["meta"]["count"]
c_types = r2["meta"]["count"]

print(f"T10281 (2020) All Types: {c_all}")
print(f"T10281 (2020) Selected Types: {c_types}")
print(f"Ratio: {c_types / c_all:.2%}")

# 2. 2D GroupBy test
params_gb = {
    'filter': 'primary_topic.id:T10281,publication_year:2010-2024,authorships.institutions.country_code:DE,type:article|conference-paper|review',
    'group_by': 'publication_year,countries_distinct_count'
}
r_gb = requests.get(url, params=params_gb, headers=headers).json()
print("2D GroupBy successful:", 'group_by' in r_gb, "Number of parent groups:", len(r_gb.get('group_by', [])))

# 3. Check rate limit header
r_check = requests.get(url, params={'filter': 'publication_year:2020'}, headers=headers)
print("Remaining calls today:", r_check.headers.get("X-RateLimit-Remaining"))
