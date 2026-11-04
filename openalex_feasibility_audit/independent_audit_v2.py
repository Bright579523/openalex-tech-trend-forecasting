import pandas as pd
import numpy as np

def run_audit():
    print("=" * 80)
    print("INDEPENDENT FINAL AUDIT: MODELING PANEL V2 (SELECTED TYPES)")
    print("=" * 80)
    
    csv_v2 = r"openalex_feasibility_audit\openalex_modeling_panel_1025topics_v2_selected_types.csv"
    csv_v1 = r"openalex_feasibility_audit\openalex_master_panel_1025topics.csv"
    denom_v2 = r"openalex_feasibility_audit\all_science_national_denominators_fractional_v2_selected_types.csv"
    
    df_v2 = pd.read_csv(csv_v2)
    df_v1 = pd.read_csv(csv_v1)
    df_denom = pd.read_csv(denom_v2)
    
    # 1. Structural Completeness
    print("\n[1] STRUCTURAL COMPLETENESS")
    print(f"Total Rows: {len(df_v2)} (Expected: 15,375)")
    print(f"Total Columns: {len(df_v2.columns)} (Expected: 26)")
    print(f"Unique Topics: {df_v2['topic_id'].nunique()} (Expected: 1,025)")
    years_found = sorted(df_v2['year'].unique())
    print(f"Years: {years_found[0]} - {years_found[-1]} ({len(years_found)} years)")
    print(f"Duplicate (topic_id, year): {df_v2.duplicated(subset=['topic_id', 'year']).sum()}")
    print(f"Total Missing / Null: {df_v2.isnull().sum().sum()}")
    
    # Check zero counts
    zero_topics = df_v2.groupby('topic_id')['global_count'].sum()
    zero_topic_ids = zero_topics[zero_topics == 0].index.tolist()
    print(f"Zero-volume Topics across all 15 years: {len(zero_topic_ids)} topics")
    
    # 2. Denominator Consistency
    print("\n[2] DENOMINATOR CONSISTENCY")
    denom_match = True
    for yr in range(2010, 2025):
        v2_sub = df_v2[df_v2['year'] == yr].iloc[0]
        denom_sub = df_denom[df_denom['year'] == yr].iloc[0]
        if v2_sub['global_allsci_denom'] != denom_sub['global_allsci']:
            denom_match = False
            print(f"Global denom mismatch in {yr}!")
        if v2_sub['de_allsci_whole_denom'] != denom_sub['de_whole']:
            denom_match = False
        if abs(v2_sub['de_allsci_frac_denom'] - denom_sub['de_frac']) > 1e-4:
            denom_match = False
    print(f"Denominator Sync Check across all 15 years: {'PASS (100% Match)' if denom_match else 'FAIL'}")
    
    # 3. Fractional vs Whole Counts Credit Retention
    print("\n[3] FRACTIONAL ATTRIBUTION & CREDIT RETENTION")
    for c in ['de', 'cn', 'jp']:
        tot_whole = df_v2[f'{c}_whole_count'].sum()
        tot_frac = df_v2[f'{c}_frac_count'].sum()
        ratio = (tot_frac / tot_whole) * 100 if tot_whole > 0 else 0
        print(f"Country {c.upper()}: Whole Sum = {tot_whole:,} | Frac Sum = {tot_frac:,.2f} | Retention = {ratio:.2f}%")
        
    # Check Fractional <= Whole
    frac_le_whole = True
    for c in ['de', 'cn', 'jp']:
        violations = (df_v2[f'{c}_frac_count'] > df_v2[f'{c}_whole_count'] + 1e-5).sum()
        if violations > 0:
            frac_le_whole = False
            print(f"Violation: {c}_frac_count > {c}_whole_count in {violations} rows!")
    print(f"Constraint (Frac <= Whole count for all rows): {'PASS' if frac_le_whole else 'FAIL'}")

    # 4. RCA Recalculation Audit
    print("\n[4] RCA RECALCULATION & NUMERICAL PRECISION AUDIT")
    for c in ['de', 'cn', 'jp']:
        # Recalculate Fractional RCA
        calc_rca_frac = np.where(
            (df_v2['global_count'] > 0) & (df_v2[f'{c}_allsci_frac_denom'] > 0) & (df_v2[f'{c}_frac_count'] > 0),
            (df_v2[f'{c}_frac_count'] / df_v2[f'{c}_allsci_frac_denom']) / (df_v2['global_count'] / df_v2['global_allsci_denom']),
            0.0
        )
        diff_frac = np.abs(calc_rca_frac - df_v2[f'rca_frac_{c}'])
        max_idx_f = np.argmax(diff_frac)
        max_diff_f = diff_frac[max_idx_f]
        row_f = df_v2.iloc[max_idx_f]
        
        # Recalculate Whole RCA
        calc_rca_whole = np.where(
            (df_v2['global_count'] > 0) & (df_v2[f'{c}_allsci_whole_denom'] > 0) & (df_v2[f'{c}_whole_count'] > 0),
            (df_v2[f'{c}_whole_count'] / df_v2[f'{c}_allsci_whole_denom']) / (df_v2['global_count'] / df_v2['global_allsci_denom']),
            0.0
        )
        diff_whole = np.abs(calc_rca_whole - df_v2[f'rca_whole_{c}'])
        max_idx_w = np.argmax(diff_whole)
        max_diff_w = diff_whole[max_idx_w]
        
        print(f"\nCountry {c.upper()}:")
        print(f"  Whole RCA Max Discrepancy:      {max_diff_w:.8f} (Theoretical Bound <= 0.00000500)")
        print(f"  Fractional RCA Max Discrepancy: {max_diff_f:.8f}")
        print(f"  Max Diff Location: Topic {row_f['topic_id']}, Year {row_f['year']}")
        print(f"    global_count: {row_f['global_count']}, global_allsci: {row_f['global_allsci_denom']}")
        print(f"    {c}_frac_count: {row_f[f'{c}_frac_count']}, {c}_allsci_frac: {row_f[f'{c}_allsci_frac_denom']}")
        print(f"    Stored rca_frac: {row_f[f'rca_frac_{c}']:.5f} | Recalculated: {calc_rca_frac[max_idx_f]:.8f}")
        
    # 5. Comparison v1 vs v2
    print("\n[5] COMPARISON: MASTER PANEL V1 (ALL TYPES) VS MODELING PANEL V2 (SELECTED TYPES)")
    tot_glob_v1 = df_v1['global_count'].sum()
    tot_glob_v2 = df_v2['global_count'].sum()
    print(f"Total Global Works: v1 = {tot_glob_v1:,} | v2 = {tot_glob_v2:,} | Retention: {tot_glob_v2/tot_glob_v1:.2%}")
    for c in ['de', 'cn', 'jp']:
        w_v1 = df_v1[f'{c}_whole_count'].sum()
        w_v2 = df_v2[f'{c}_whole_count'].sum()
        f_v1 = df_v1[f'{c}_frac_count'].sum()
        f_v2 = df_v2[f'{c}_frac_count'].sum()
        corr_rca = df_v1[f'rca_frac_{c}'].corr(df_v2[f'rca_frac_{c}'])
        print(f"Country {c.upper()}: Whole Ret = {w_v2/w_v1:.2%} | Frac Ret = {f_v2/f_v1:.2%} | RCA Correlation (v1 vs v2) = {corr_rca:.4f}")

if __name__ == "__main__":
    run_audit()
