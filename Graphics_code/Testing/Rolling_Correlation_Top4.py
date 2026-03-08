import pandas as pd
import os
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

unrate_path = "../../Data/Intermediate/unemp_rate_cleaned.csv"
output_dir = "../../Graphics/Testing/Rolling_correlation/Report_figures"
os.makedirs(output_dir, exist_ok=True)

unrate_df = pd.read_csv(unrate_path, parse_dates=["date"])
unrate_df = unrate_df.sort_values("date")

# Recession periods
recessions = [
    ("2007-12-01", "2009-06-01"),
    ("2020-02-01", "2020-04-01"),
]

# The 4 most notable keywords for the report (seasonally corrected)
report_keywords = [
    ("../../Data/Corrected_for_yearly_pattern/Keywords/Government_support", "disability_benefits",       "Government Support"),
    ("../../Data/Corrected_for_yearly_pattern/Keywords/Credit_and_debt",    "chapter_7_bankruptcy",      "Credit & Debt"),
    ("../../Data/Corrected_for_yearly_pattern/Keywords/Luxuries",           "designer_handbag",          "Luxuries"),
    ("../../Data/Corrected_for_yearly_pattern/Keywords/Housing_rent_and_stress", "cost_of_living",       "Housing & Stress"),
]

results = []
for keyword_folder, keyword, label in report_keywords:
    file_path = os.path.join(keyword_folder, keyword + ".csv")
    if not os.path.exists(file_path):
        print(f"  [WARN] File not found: {file_path}")
        continue

    keyword_df = pd.read_csv(file_path, parse_dates=["date"])
    keyword_df = keyword_df.sort_values("date")
    keyword_col = keyword_df.columns[1]

    merged = pd.merge(
        keyword_df[["date", keyword_col]],
        unrate_df[["date", "UNRATE"]],
        on="date",
        how="inner"
    ).dropna()

    if len(merged) < 24:
        print(f"  [WARN] Not enough data for {keyword}")
        continue

    merged["rolling_corr"] = merged[keyword_col].rolling(window=12).corr(merged["UNRATE"])

    results.append({
        "keyword": keyword,
        "label": label,
        "dates": merged["date"],
        "rolling_corr": merged["rolling_corr"],
    })

fig, axes = plt.subplots(2, 2, figsize=(12, 7))
axes = axes.flatten()

for i, r in enumerate(results):
    ax = axes[i]
    ax.plot(r["dates"], r["rolling_corr"], color="steelblue", linewidth=1.2)

    for start, end in recessions:
        ax.axvspan(pd.to_datetime(start), pd.to_datetime(end),
                   color="lightcoral", alpha=0.3)

    ax.axhline(0, color="black", linewidth=0.6, linestyle="--")
    ax.set_ylim(-1, 1)
    ax.set_title(f"{r['label']} — {r['keyword'].replace('_', ' ')}", fontsize=10)
    ax.tick_params(labelsize=7)
    ax.set_xlabel("Date", fontsize=7)
    ax.set_ylabel("Rolling Corr (r)", fontsize=7)

recession_patch = mpatches.Patch(color="lightcoral", alpha=0.3, label="Recession")
fig.legend(handles=[recession_patch], loc="lower center", fontsize=8)
fig.suptitle("Selected Keyword Rolling Correlations vs Unemployment Rate\n(12-Month Window, Seasonally Corrected)", fontsize=12)
plt.tight_layout(rect=[0, 0.04, 1, 1])

output_path = os.path.join(output_dir, "report_figure_top4.png")
plt.savefig(output_path, dpi=150)
plt.close()
print(f"Saved: {output_path}")

print("\nDone.")