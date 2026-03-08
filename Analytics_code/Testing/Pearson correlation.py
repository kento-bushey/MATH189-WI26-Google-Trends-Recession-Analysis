import pandas as pd
import os
import numpy as np
from scipy import stats
from statsmodels.stats.multitest import multipletests

# Keywords (seasonally corrected)
keyword_folder_list = [
    "../../Data/Corrected_for_yearly_pattern/Keywords/Credit_and_debt",
    "../../Data/Corrected_for_yearly_pattern/Keywords/Frugality",
    "../../Data/Corrected_for_yearly_pattern/Keywords/Government_support",
    "../../Data/Corrected_for_yearly_pattern/Keywords/Housing_rent_and_stress",
    "../../Data/Corrected_for_yearly_pattern/Keywords/Inflation",
    "../../Data/Corrected_for_yearly_pattern/Keywords/Insurance",
    "../../Data/Corrected_for_yearly_pattern/Keywords/Investing_and_markets",
    "../../Data/Corrected_for_yearly_pattern/Keywords/Jobs",
    "../../Data/Corrected_for_yearly_pattern/Keywords/Luxuries",
    "../../Data/Corrected_for_yearly_pattern/Keywords/Travel"
]

unrate_path = "../../Data/Intermediate/unemp_rate_cleaned.csv"
unemploy_path = "../../Data/Intermediate/unemp_level_cleaned.csv"
output_dir = "../Output"
os.makedirs(output_dir, exist_ok=True)

# Macros
unrate_df = pd.read_csv(unrate_path, parse_dates=["date"])
unrate_df = unrate_df.sort_values("date")

unemploy_df = pd.read_csv(unemploy_path, parse_dates=["date"])
unemploy_df = unemploy_df.sort_values("date")

macro_targets = [
    (unrate_df, "UNRATE", "Unemployment Rate"),
    (unemploy_df, "UNEMPLOY", "Unemployment Level"),
]

# Recession windows only
periods = [
    ("2006-01-01", "2011-12-01", "2006_2011"),
    ("2018-01-01", "2023-12-01", "2018_2023"),
]

ALPHA = 0.05

for macro_df, macro_col, macro_label in macro_targets:
    for period_start, period_end, period_label in periods:

        rows = []

        for keyword_folder in keyword_folder_list:
            category = os.path.basename(keyword_folder.rstrip("/"))

            for filename in os.listdir(keyword_folder):
                if not filename.endswith(".csv"):
                    continue

                file_path = os.path.join(keyword_folder, filename)
                keyword_df = pd.read_csv(file_path, parse_dates=["date"])
                keyword_df = keyword_df.sort_values("date")
                keyword_col = keyword_df.columns[1]

                # Resample to monthly if weekly
                keyword_df["date"] = keyword_df["date"].dt.to_period("M").dt.to_timestamp()
                keyword_df = keyword_df.groupby("date")[keyword_col].mean().reset_index()

                merged = pd.merge(
                    keyword_df[["date", keyword_col]],
                    macro_df[["date", macro_col]],
                    on="date",
                    how="inner"
                ).dropna()

                merged = merged[
                    (merged["date"] >= period_start) &
                    (merged["date"] <= period_end)
                ]

                if len(merged) < 12:
                    continue
                if merged[keyword_col].std() < 0.01:
                    continue

                r, p = stats.pearsonr(merged[keyword_col], merged[macro_col])

                rows.append({
                    "category": category,
                    "keyword": os.path.splitext(filename)[0],
                    "pearson_r": round(r, 4),
                    "p_value": p,
                    "n_months": len(merged),
                })

        if not rows:
            continue

        result_df = pd.DataFrame(rows)

        # BH FDR correction
        reject, p_adj, _, _ = multipletests(result_df["p_value"], alpha=ALPHA, method="fdr_bh")
        result_df["p_adj_bh"] = p_adj.round(6)
        result_df["significant"] = reject
        result_df["p_value"] = result_df["p_value"].round(4)

        # Category summary
        cat_summary = result_df.groupby("category").apply(
            lambda x: pd.Series({
                "n_keywords": len(x),
                "n_significant": x["significant"].sum(),
                "pct_significant": round(x["significant"].mean() * 100, 1),
                "avg_abs_r": round(x["pearson_r"].abs().mean(), 4),
                "avg_r": round(x["pearson_r"].mean(), 4),
                "max_r": round(x["pearson_r"].max(), 4),
                "min_r": round(x["pearson_r"].min(), 4),
            })
        ).sort_values("avg_abs_r", ascending=False).reset_index()

        print(f"\n{'='*60}")
        print(f"{macro_label} | {period_label}")
        print(f"{'='*60}")
        print(cat_summary.to_string(index=False))

        # Save
        keyword_path = os.path.join(output_dir, f"pearson_keywords_{macro_col}_{period_label}.csv")
        result_df.sort_values(["category", "pearson_r"], ascending=[True, False]).to_csv(keyword_path, index=False)

        cat_path = os.path.join(output_dir, f"pearson_categories_{macro_col}_{period_label}.csv")
        cat_summary.to_csv(cat_path, index=False)
        print(f"Saved: {cat_path}")

print("\nDone.")