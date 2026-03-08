import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import os

input_dir = "../../Analytics_code/Output"
output_dir = "../../Graphics/Testing/Pearson_correlation"
os.makedirs(output_dir, exist_ok=True)

# Chart 1: Average Pearson r by category, 2006-2011
cat_df = pd.read_csv(os.path.join(input_dir, "pearson_categories_UNRATE_2006_2011.csv"))
cat_df = cat_df.sort_values("avg_r", ascending=True)

colors = ["steelblue" if r < 0 else "firebrick" for r in cat_df["avg_r"]]

fig, ax = plt.subplots(figsize=(9, 6))
bars = ax.barh(cat_df["category"], cat_df["avg_r"], color=colors)
ax.axvline(0, color="black", linewidth=0.8, linestyle="--")
ax.set_xlabel("Average Pearson r (signed)", fontsize=11)
ax.set_title("Category Correlation Direction & Strength vs. Unemployment\n2006–2011 Recession Window", fontsize=12)

# Add value labels
for bar, val in zip(bars, cat_df["avg_r"]):
    offset = 0.005 if val >= 0 else -0.005
    ha = "left" if val >= 0 else "right"
    ax.text(val + offset, bar.get_y() + bar.get_height() / 2,
            f"{val:.3f}", va="center", ha=ha, fontsize=8)

legend_elements = [Patch(facecolor="firebrick", label="Positive — rises with unemployment"),
                   Patch(facecolor="steelblue", label="Negative — falls with unemployment")]
ax.legend(handles=legend_elements, fontsize=8, loc="lower right")

plt.tight_layout()
plt.savefig(os.path.join(output_dir, "chart1_category_direction.png"), dpi=150)
plt.close()
print("Saved: chart1_category_direction.png")

# Chart 2: Lag profile for top categories, 2006-2011
lag_df = pd.read_csv(os.path.join(input_dir, "lag_pearson_category_summary.csv"))

top_categories = ["Government_support", "Credit_and_debt", "Luxuries"]
lag_df = lag_df[lag_df["category"].isin(top_categories)]
lags = sorted(lag_df["lag"].unique())

fig, ax = plt.subplots(figsize=(10, 5))

bar_width = 0.25
x = range(len(lags))
colors_cat = ["firebrick", "steelblue", "seagreen"]

for i, (cat, color) in enumerate(zip(top_categories, colors_cat)):
    cat_data = lag_df[lag_df["category"] == cat].sort_values("lag")
    offset = [pos + i * bar_width for pos in x]
    ax.bar(offset, cat_data["avg_r"], width=bar_width,
           label=cat.replace("_", " "), color=color, alpha=0.85)

ax.set_xticks([pos + bar_width for pos in x])
ax.set_xticklabels([f"Lag {int(l):+d}" for l in lags], fontsize=9)
ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
ax.set_xlabel("Lag (months)", fontsize=11)
ax.set_ylabel("Average Pearson r (signed)", fontsize=11)
ax.set_title("Lag Profile — Selected Categories vs. Unemployment\n2006–2011 Recession Window", fontsize=12)
ax.legend(fontsize=9)

plt.tight_layout()
plt.savefig(os.path.join(output_dir, "chart2_lag_profile.png"), dpi=150)
plt.close()
print("Saved: chart2_lag_profile.png")

print("\nDone.")