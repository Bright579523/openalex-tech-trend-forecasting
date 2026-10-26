from pathlib import Path
import pandas as pd

FILES = [
    "model_pilot_results_allsci_consistent.csv",
    "full_universe_origin_eligibility.csv",
    "full_1025_topics_historical_volumes.csv",
    "openalex_master_panel_1025topics.csv",
]

for filename in FILES:
    path = Path(filename)
    print("\n" + "=" * 80)
    print(f"FILE: {filename}")
    if not path.exists():
        print("NOT FOUND")
        continue
    try:
        df = pd.read_csv(path)
        print("Shape:", df.shape)
        print("Columns:", df.columns.tolist())
        print("Duplicate rows:", int(df.duplicated().sum()))
        print("Missing values by column:")
        print(df.isna().sum().to_string())
        if "model_pilot_results" in filename:
            print("\nFULL CONTENT:")
            print(df.to_string(index=False))
        elif "eligibility" in filename:
            print("\nALL ROWS:")
            print(df.to_string(index=False))
        else:
            print("\nFIRST 10 ROWS:")
            print(df.head(10).to_string(index=False))
            print("\nLAST 10 ROWS:")
            print(df.tail(10).to_string(index=False))
            numeric = df.select_dtypes(include="number")
            if not numeric.empty:
                print("\nNUMERIC SUMMARY:")
                print(numeric.describe().round(4).to_string())
    except Exception as e:
        print("ERROR:", repr(e))
