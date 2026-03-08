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
output_dir = "../Output"
os.makedirs(output_dir, exist_ok=True)

unrate_df = pd.read_csv(unrate_path, parse_dates=["date"])
unrate_df = unrate_df.sort_values("date").reset_index(drop=True)

# Lags to test: negative = search leads unemployment, positive = search lags unemployment
lags = [-3, -2, -1, 0, 1, 2, 3]

ALPHA = 0.05

# Store category-level summary across all lags
all_lag_summaries = []

for lag in lags:

    rows = []

    # Shift unemployment by lag months
    # lag < 0: search leads unemployment (search at t predicts unemployment at t + |lag|)
    # lag > 0: search lags unemployment (unemployment at t predicts search at t + lag)
    unrate_lagged = unrate_df.copy()
    unrate_lagged["date"] = unrate_lagged["date"] + pd.DateOffset(months=lag)

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
                unrate_lagged[["date", "UNRATE"]],
                on="date",
                how="inner"
            ).dropna()

            # Focus on recession window where signal is strongest
            merged = merged[
                (merged["date"] >= "2006-01-01") &
                (merged["date"] <= "2011-12-01")
            ]

            if len(merged) < 12:
                continue
            if merged[keyword_col].std() < 0.01:
                continue

            # Pearson correlation test
            # H0: rho = 0 (no relationship between search and unemployment at this lag)
            # Ha: rho != 0
            # Test statistic: t = r * sqrt(n-2) / sqrt(1-r^2) ~ t(n-2) under H0
            r, p = stats.pearsonr(merged[keyword_col], merged["UNRATE"])
            n = len(merged)
            t_stat = r * np.sqrt(n - 2) / np.sqrt(1 - r**2)

            rows.append({
                "lag": lag,
                "category": category,
                "keyword": os.path.splitext(filename)[0],
                "pearson_r": round(r, 4),
                "t_stat": round(t_stat, 4),
                "p_value": p,
                "n_months": n,
            })

    if not rows:
        continue

    result_df = pd.DataFrame(rows)

    # BH FDR correction across all keywords at this lag
    reject, p_adj, _, _ = multipletests(result_df["p_value"], alpha=ALPHA, method="fdr_bh")
    result_df["p_adj_bh"] = p_adj.round(6)
    result_df["significant"] = reject
    result_df["p_value"] = result_df["p_value"].round(6)

    # Category summary at this lag
    cat_summary = result_df.groupby("category").apply(
        lambda x: pd.Series({
            "lag": lag,
            "n_keywords": len(x),
            "n_significant": x["significant"].sum(),
            "pct_significant": round(x["significant"].mean() * 100, 1),
            "avg_abs_r": round(x["pearson_r"].abs().mean(), 4),
            "avg_r": round(x["pearson_r"].mean(), 4),
        })
    ).reset_index()

    all_lag_summaries.append(cat_summary)

    # Print summary for this lag
    label = f"Search LEADS unemployment by {abs(lag)} month(s)" if lag < 0 else \
            f"Contemporaneous (lag=0)" if lag == 0 else \
            f"Search LAGS unemployment by {lag} month(s)"
    print(f"\n{'='*65}")
    print(f"Lag {lag:+d} | {label}")
    print(f"{'='*65}")
    print(cat_summary[["category", "n_significant", "pct_significant", "avg_abs_r", "avg_r"]].to_string(index=False))

    # Save keyword-level results
    out_path = os.path.join(output_dir, f"lag_pearson_keywords_lag{lag:+d}.csv")
    result_df.sort_values(["category", "pearson_r"], ascending=[True, False]).to_csv(out_path, index=False)

# Save combined category summary across all lags
combined = pd.concat(all_lag_summaries, ignore_index=True)
combined_path = os.path.join(output_dir, "lag_pearson_category_summary.csv")
combined.to_csv(combined_path, index=False)
print(f"\nSaved combined lag summary: {combined_path}")

# Print the best lag per category (highest avg |r|)
print(f"\n{'='*65}")
print("Best lag per category (highest avg |r|):")
print(f"{'='*65}")
best = combined.loc[combined.groupby("category")["avg_abs_r"].idxmax()]
print(best[["category", "lag", "avg_abs_r", "pct_significant"]].sort_values("avg_abs_r", ascending=False).to_string(index=False))

print("\nDone.")