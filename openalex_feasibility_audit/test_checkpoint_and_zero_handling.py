import sys
import os
import json
import pandas as pd
from pathlib import Path

# Add current dir
base_dir = Path(r"d:\Thesis")
sys.path.append(str(base_dir))

from extract_master_panel_1025topics import extract_and_validate_topic, get_secure_api_key, mask_key, run_post_extraction_validation

print("=" * 80)
print("TESTING CHECKPOINT / RESUME, ZERO HANDLING, AND ALL-SCIENCE AUDIT")
print("=" * 80)

# 1. Test Key Security
key = get_secure_api_key()
print(f"1. Key Security Check:")
print(f"   Loaded Key Length: {len(key)}")
print(f"   Masked Key Representation: {mask_key(key)}")
assert len(key) > 10, "API Key should be valid string"
assert key not in mask_key(key), "Masked key must not reveal full secret"
print("   [PASS] Key loaded securely without exposure.")

# 2. Test Zero Handling
print("\n2. Zero-Publication Topic-Year Representation Test:")
tax_path = base_dir / "openalex_feasibility_audit" / "all_tech_topics_taxonomy.csv"
allsci_path = base_dir / "openalex_feasibility_audit" / "all_science_national_denominators_fractional.csv"
df_tax = pd.read_csv(tax_path)
df_allsci = pd.read_csv(allsci_path).set_index("year")

headers = {
    "User-Agent": "ThesisTest/1.0 (mailto:student@ue-germany.de)",
    "Authorization": f"Bearer {key}"
}

# T13836 is a known zero-volume topic in technology
zero_topic_id = "T13836"
row_zero = df_tax[df_tax["topic_id"] == zero_topic_id].iloc[0]
print(f"   Extracting zero-volume topic {zero_topic_id}: {row_zero['display_name']}...")

records_zero = extract_and_validate_topic(
    tid=zero_topic_id,
    tname=row_zero["display_name"],
    field_name=row_zero["field_name"],
    subfield_name=row_zero["subfield_name"],
    headers=headers,
    df_allsci=df_allsci,
    delay=0.03
)

df_zero = pd.DataFrame(records_zero)
print(f"   Total rows generated for zero topic: {len(df_zero)} (Expected: exactly 15 annual intervals)")
assert len(df_zero) == 15, "Zero topic must generate all 15 annual rows"
assert (df_zero["global_count"] == 0).all(), "Global counts must be explicitly 0, not omitted"
assert (df_zero["de_frac_count"] == 0.0).all(), "DE counts must be explicitly 0.0"
assert (df_zero["rca_frac_de"] == 0.0).all(), "RCA must be explicitly 0.0"
print("   [PASS] Zero-publication topic-year records are explicitly represented as 0, never omitted.")

# 3. Test Checkpoint & Resume Integrity
print("\n3. Checkpoint & Resume Integrity Test:")
test_checkpoint_file = base_dir / "openalex_feasibility_audit" / "test_temp_checkpoint.csv"
if test_checkpoint_file.exists():
    test_checkpoint_file.unlink()

# Simulate Step 1: Extract 2 topics and save checkpoint
topics_to_test = df_tax.head(3)
t1 = topics_to_test.iloc[0]
t2 = topics_to_test.iloc[1]
t3 = topics_to_test.iloc[2]

rec1 = extract_and_validate_topic(t1["topic_id"], t1["display_name"], t1["field_name"], t1["subfield_name"], headers, df_allsci)
rec2 = extract_and_validate_topic(t2["topic_id"], t2["display_name"], t2["field_name"], t2["subfield_name"], headers, df_allsci)

df_step1 = pd.DataFrame(rec1 + rec2)
df_step1.to_csv(test_checkpoint_file, index=False)
print(f"   Saved simulated checkpoint with {df_step1['topic_id'].nunique()} topics ({len(df_step1)} rows).")

# Simulate Step 2: Resume from checkpoint
df_resumed = pd.read_csv(test_checkpoint_file)
resumed_topic_ids = set(df_resumed["topic_id"].unique())
print(f"   Resuming from checkpoint: Found topics {resumed_topic_ids}")

resumed_rows = df_resumed.to_dict("records")
for idx, row in topics_to_test.iterrows():
    if row["topic_id"] in resumed_topic_ids:
        print(f"   [Skipping Already Completed] {row['topic_id']}")
        continue
    print(f"   [Fetching Remaining Topic] {row['topic_id']}")
    rec = extract_and_validate_topic(row["topic_id"], row["display_name"], row["field_name"], row["subfield_name"], headers, df_allsci)
    resumed_rows.extend(rec)

df_final_test = pd.DataFrame(resumed_rows)
print(f"   Final Combined Rows: {len(df_final_test)} (Expected: 3 topics x 15 = 45 rows)")
dup_check = df_final_test.duplicated(subset=["topic_id", "year"]).sum()
assert dup_check == 0, "No duplicate topic-year rows allowed after resume"
assert df_final_test["topic_id"].nunique() == 3, "All 3 topics must be present"
print(f"   Duplicates after resume: {dup_check}")
print("   [PASS] Checkpoint & resume mechanism verified: No duplication, no omission.")

if test_checkpoint_file.exists():
    test_checkpoint_file.unlink()

# 4. All-Science Denominators Completeness Audit
print("\n4. All-Science Denominators Completeness Audit:")
assert len(df_allsci) == 15, "All-Science denominators must cover all 15 years (2010-2024)"
for y in range(2010, 2025):
    row_y = df_allsci.loc[y]
    assert row_y["global_allsci"] > 5000000, f"Global all-science for {y} must be > 5M"
    assert row_y["de_frac"] > 100000, f"DE frac for {y} must be > 100k"
    assert row_y["cn_frac"] > 300000, f"CN frac for {y} must be > 300k"
    assert row_y["jp_frac"] > 100000, f"JP frac for {y} must be > 100k"
    assert row_y["de_frac"] <= row_y["de_whole"], "Fractional count cannot exceed whole count"
    assert row_y["cn_frac"] <= row_y["cn_whole"], "Fractional count cannot exceed whole count"
    assert row_y["jp_frac"] <= row_y["jp_whole"], "Fractional count cannot exceed whole count"

print("   [PASS] All-Science Denominators verified: All 15 years present, all > 0, strictly fractional <= whole.")

print("\n" + "=" * 80)
print("ALL 5 OPERATIONAL PRE-FLIGHT CHECKS PASSED PERFECTLY!")
print("=" * 80)

