import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import numpy as np
import os

input_dir = "../../Analytics_code/Output"
output_dir = "../../Graphics/Testing/Pearson_correlation"
os.makedirs(output_dir, exist_ok=True)

# Load pearson recession data
df1 = pd.read_csv(os.path.join(input_dir, "pearson_categories_UNRATE_2006_2011.csv"))
df2 = pd.read_csv(os.path.join(input_dir, "pearson_categories_UNRATE_2018_2023.csv"))

# Align categories by 2006_2011 avg_r order
categories = df1.sort_values("avg_r", ascending=True)["category"].tolist()
df1 = df1.set_index("category").reindex(categories)
df2 = df2.set_index("category").reindex(categories)

x = np.arange(len(categories))
bar_width = 0.35

fig, ax = plt.subplots(figsize=(12, 7))

bars1 = ax.barh(x - bar_width/2, df1["avg_r"], height=bar_width,
                color=["firebrick" if r >= 0 else "steelblue" for r in df1["avg_r"]],
                alpha=0.9)
bars2 = ax.barh(x + bar_width/2, df2["avg_r"], height=bar_width,
                color=["firebrick" if r >= 0 else "steelblue" for r in df2["avg_r"]],
                alpha=0.5)

ax.axvline(0, color="black", linewidth=0.8, linestyle="--")
ax.set_yticks(x)
ax.set_yticklabels([c.replace("_", " ") for c in categories], fontsize=9)
ax.set_xlabel("Average Pearson r (signed)", fontsize=11)
ax.set_title("Category Correlation Direction & Strength vs. Unemployment\n2006–2011 vs. 2018–2023 Recession Windows", fontsize=12)

# Value labels
for bar, val in zip(bars1, df1["avg_r"]):
    offset = 0.005 if val >= 0 else -0.005
    ha = "left" if val >= 0 else "right"
    ax.text(val + offset, bar.get_y() + bar.get_height() / 2,
            f"{val:.3f}", va="center", ha=ha, fontsize=7)
for bar, val in zip(bars2, df2["avg_r"]):
    offset = 0.005 if val >= 0 else -0.005
    ha = "left" if val >= 0 else "right"
    ax.text(val + offset, bar.get_y() + bar.get_height() / 2,
            f"{val:.3f}", va="center", ha=ha, fontsize=7)

legend_elements = [
    Patch(facecolor="firebrick", alpha=0.9, label="2006–2011 | Positive"),
    Patch(facecolor="steelblue", alpha=0.9, label="2006–2011 | Negative"),
    Patch(facecolor="firebrick", alpha=0.4, label="2018–2023 | Positive"),
    Patch(facecolor="steelblue", alpha=0.4, label="2018–2023 | Negative"),
]
ax.legend(handles=legend_elements, fontsize=8, loc="lower right")

plt.tight_layout()
plt.savefig(os.path.join(output_dir, "chart1_category_direction.png"), dpi=150)
plt.close()
print("Saved: chart1_category_direction.png")

print("\nDone.")