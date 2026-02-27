import pandas as pd
import os
from scipy import stats
import numpy as np

# Keyword folder (Jobs)
keyword_folder = "../../Data/Raw/Keywords/Jobs"

# Unemployment data
unemp_path = "../../Data/Intermediate/unemp_rate_cleaned.csv"

# Output directory
output_dir = "../../Data/Intermediate/Keywords"
os.makedirs(output_dir, exist_ok=True)

# Load unemployment data once
unemp_df = pd.read_csv(unemp_path, parse_dates=["date"])
unemp_df = unemp_df.sort_values("date")

results = []

for filename in os.listdir(keyword_folder):
    if not filename.endswith(".csv"):
        continue

    file_path = os.path.join(keyword_folder, filename)

    try:
        keyword_df = pd.read_csv(file_path, parse_dates=["date"])
        keyword_df = keyword_df.sort_values("date")

        value_col = keyword_df.columns[1]
        keyword_df["first_diff"] = keyword_df[value_col].diff()

        merged = pd.merge(
            keyword_df[["date", "first_diff"]],
            unemp_df[["date", "unrate_mom_change"]],
            on="date",
            how="inner"
        ).dropna()

        if len(merged) < 5:
            continue

        x = merged["first_diff"].values
        y = merged["unrate_mom_change"].values

        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)

        results.append({
            "keyword": os.path.splitext(filename)[0],
            "intercept": intercept,
            "slope": slope,
            "r_squared": r_value**2,
            "p_value": p_value,
            "std_error": std_err,
            "n_obs": len(merged)
        })

    except Exception as e:
        print(f"Error processing {filename}: {e}")

summary_df = pd.DataFrame(results)

folder_name = os.path.basename(keyword_folder)
output_path = os.path.join(output_dir, f"{folder_name}_regression_summary.csv")

summary_df.to_csv(output_path, index=False)

print(f"Saved regression summary to {output_path}")