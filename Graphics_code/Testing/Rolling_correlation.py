import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import math

# Keywords
keyword_folder_list = [
    "../../Data/Raw/Keywords/credit_and_debt",
    "../../Data/Raw/Keywords/frugality",
    "../../Data/Raw/Keywords/government_support",
    "../../Data/Raw/Keywords/housing_rent_and_stress",
    "../../Data/Raw/Keywords/inflation",
    "../../Data/Raw/Keywords/insurance",
    "../../Data/Raw/Keywords/investing_and_markets",
    "../../Data/Raw/Keywords/jobs",
    "../../Data/Raw/Keywords/luxuries",
    "../../Data/Raw/Keywords/travel"
]

gdp_path = "../../Data/Intermediate/GDP_YoY_pct_cleaned.csv"
unrate_path = "../../Data/Intermediate/unemp_rate_cleaned.csv"
unemploy_path = "../../Data/Intermediate/unemp_level_cleaned.csv"
output_dir = "../../Graphics/Testing/Rolling_correlation"
os.makedirs(output_dir, exist_ok=True)

# Macros
gdp_df = pd.read_csv(gdp_path, parse_dates=["date"])
gdp_df = gdp_df.sort_values("date")

unrate_df = pd.read_csv(unrate_path, parse_dates=["date"])
unrate_df = unrate_df.sort_values("date")

unemploy_df = pd.read_csv(unemploy_path, parse_dates=["date"])
unemploy_df = unemploy_df.sort_values("date")

macro_targets = [
    (gdp_df, "gdp_yoy_pct_change", "GDP YoY %"),
    (unrate_df, "UNRATE", "Unemployment Rate"),
    (unemploy_df, "UNEMPLOY", "Unemployment Level"),
]

# Recession periods
recessions = [
    ("2007-12-01", "2009-06-01"),
    ("2020-02-01", "2020-04-01"),
]

for keyword_folder in keyword_folder_list:
    for macro_df, macro_col, macro_label in macro_targets:

        results = []

        # Compute rolling correlations
        for filename in os.listdir(keyword_folder):
            if not filename.endswith(".csv"):
                continue

            file_path = os.path.join(keyword_folder, filename)
            keyword_df = pd.read_csv(file_path, parse_dates=["date"])
            keyword_df = keyword_df.sort_values("date")
            keyword_col = keyword_df.columns[1]

            merged = pd.merge(
                keyword_df[["date", keyword_col]],
                macro_df[["date", macro_col]],
                on="date",
                how="inner"
            ).dropna()

            if len(merged) < 24:
                continue

            merged["rolling_corr"] = merged[keyword_col].rolling(window=12).corr(merged[macro_col])

            results.append({
                "keyword": os.path.splitext(filename)[0],
                "dates": merged["date"],
                "rolling_corr": merged["rolling_corr"]
            })

        if not results:
            continue

        # Plot rolling correlations
        n = len(results)
        cols = 4
        rows = math.ceil(n / cols)
        fig_width = 5 * cols
        fig_height = 3 * rows

        fig, axes = plt.subplots(rows, cols, figsize=(fig_width, fig_height))
        axes = axes.flatten()

        for i, r in enumerate(results):
            ax = axes[i]
            ax.plot(r["dates"], r["rolling_corr"], color="steelblue", linewidth=1)

            for start, end in recessions:
                ax.axvspan(pd.to_datetime(start), pd.to_datetime(end),
                           color="lightcoral", alpha=0.3)

            ax.axhline(0, color="black", linewidth=0.6, linestyle="--")
            ax.set_ylim(-1, 1)
            ax.set_title(r["keyword"], fontsize=7)
            ax.tick_params(labelsize=5)
            ax.set_xticks([])

        # Hide empty subplots
        for j in range(i + 1, len(axes)):
            axes[j].axis("off")

        folder_name = os.path.basename(keyword_folder.rstrip("/"))
        fig.suptitle(f"{folder_name} — 12-Month Rolling Correlation vs {macro_label}", fontsize=12)
        plt.tight_layout()

        # Save plot
        output_path = os.path.join(output_dir, f"{folder_name}_rolling_corr_vs_{macro_col}.png")
        plt.savefig(output_path, dpi=150)
        plt.close()
        print(f"Saved: {output_path}")

print("\nAll rolling correlation matrix plots saved.")