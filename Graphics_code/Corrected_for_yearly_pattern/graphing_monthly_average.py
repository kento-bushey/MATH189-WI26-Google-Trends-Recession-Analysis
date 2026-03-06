import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# ====== PATHS ======
data_path = "../../Data/Corrected_for_yearly_pattern/monthly_seasonal_pattern.csv"
output_dir = "../../Graphics/Corrected_for_yearly_pattern"
os.makedirs(output_dir, exist_ok=True)

# ====== LOAD ======
df = pd.read_csv(data_path)
month_names = df["month"].tolist()
monthly_means = df["mean"].tolist()
grand_mean = df["mean"].mean()

# ====== PLOT ======
fig, ax = plt.subplots(figsize=(10, 5))
bars = ax.bar(month_names, monthly_means, color=[
    "tomato" if v < grand_mean else "steelblue" for v in monthly_means
])

ax.axhline(grand_mean, color="black", linewidth=1.2, linestyle="--", label=f"Grand mean ({grand_mean:.2f})")

for bar, mean in zip(bars, monthly_means):
    pct = ((mean - grand_mean) / grand_mean) * 100
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
            f"{pct:+.1f}%", ha="center", va="bottom", fontsize=8)

ax.set_xlabel("Month")
ax.set_ylabel("Mean Search Value")
ax.set_title("Average Search Volume by Month (all keywords)\nRed = below grand mean, Blue = above")
ax.legend()

plt.tight_layout()
plt.savefig(os.path.join(output_dir, "monthly_seasonal_pattern.png"), dpi=150)
plt.close()
print("Saved to Graphics/Corrected_for_yearly_pattern/monthly_seasonal_pattern.png")


# Figure generated via Project/Graphics_code/Corrected_for_yearly_pattern/graphing_monthly_average.py