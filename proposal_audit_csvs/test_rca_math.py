import pandas as pd
import numpy as np

df = pd.read_csv(r'openalex_feasibility_audit\openalex_master_panel_1025topics.csv')

print("=== CHECKING RCA DISCREPANCIES ACROSS ALL ROWS ===")
for c in ['de', 'cn', 'jp']:
    # Fractional RCA
    calc_rca_frac = np.where(
        (df['global_count'] > 0) & (df[f'{c}_allsci_frac_denom'] > 0) & (df[f'{c}_frac_count'] > 0),
        (df[f'{c}_frac_count'] / df[f'{c}_allsci_frac_denom']) / (df['global_count'] / df['global_allsci_denom']),
        0.0
    )
    diff = np.abs(calc_rca_frac - df[f'rca_frac_{c}'])
    max_idx = np.argmax(diff)
    max_diff = diff[max_idx]
    row = df.iloc[max_idx]
    print(f"\nCountry {c.upper()} Fractional RCA:")
    print(f"  Max Diff: {max_diff:.8f}")
    print(f"  Topic: {row['topic_id']} ({row['topic_name']}), Year: {row['year']}")
    print(f"  Stored {c}_frac_count: {row[f'{c}_frac_count']}")
    print(f"  Stored {c}_allsci_frac_denom: {row[f'{c}_allsci_frac_denom']}")
    print(f"  Stored global_count: {row['global_count']}")
    print(f"  Stored global_allsci_denom: {row['global_allsci_denom']}")
    print(f"  Stored rca_frac_{c}: {row[f'rca_frac_{c}']:.5f}")
    print(f"  Recalculated RCA (from stored): {calc_rca_frac[max_idx]:.8f}")

    # Whole RCA
    calc_rca_whole = np.where(
        (df['global_count'] > 0) & (df[f'{c}_allsci_whole_denom'] > 0) & (df[f'{c}_whole_count'] > 0),
        (df[f'{c}_whole_count'] / df[f'{c}_allsci_whole_denom']) / (df['global_count'] / df['global_allsci_denom']),
        0.0
    )
    diff_w = np.abs(calc_rca_whole - df[f'rca_whole_{c}'])
    max_idx_w = np.argmax(diff_w)
    row_w = df.iloc[max_idx_w]
    print(f"Country {c.upper()} Whole RCA Max Diff: {diff_w[max_idx_w]:.8f}")
    print(f"  Stored rca_whole_{c}: {row_w[f'rca_whole_{c}']:.5f}")
    print(f"  Recalculated Whole RCA: {calc_rca_whole[max_idx_w]:.8f}")
