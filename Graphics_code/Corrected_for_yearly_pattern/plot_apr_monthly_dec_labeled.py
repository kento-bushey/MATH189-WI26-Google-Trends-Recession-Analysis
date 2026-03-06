import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# ====== PATH ======
csv_path = os.path.join(os.path.dirname(__file__), "../../Data/Raw/Keywords/Credit_and_debt/APR.csv")

# ====== LOAD ======
df = pd.read_csv(csv_path, parse_dates=["date"]).set_index("date")
value_col = df.columns[0]

# ====== PLOT ======
fig, ax = plt.subplots(figsize=(14, 7))

ax.plot(df.index, df[value_col], color="steelblue", linewidth=1.5)

ax.set_xlabel("Date")
ax.set_ylabel("Google Trends Interest")
ax.set_title(f"{value_col} — Monthly Search Interest (2004-2026)")

# Label every December point
dec_points = df[df.index.month == 4][value_col]
for date, val in dec_points.items():
    ax.annotate(str(date.year) + "\napril", xy=(date, val), xytext=(4, 4),
                textcoords="offset points", fontsize=6.5,
                color="black", fontweight="bold", zorder=10)
    ax.scatter(date, val, color="black", s=20, zorder=6)

plt.tight_layout()

output_dir = os.path.join(os.path.dirname(__file__), "../../Graphics/Corrected_for_yearly_pattern")
os.makedirs(output_dir, exist_ok=True)
plt.savefig(os.path.join(output_dir, "APR.png"), dpi=150, bbox_inches="tight")
plt.close()
print("Saved to Graphics/Corrected_for_yearly_pattern/APR.png")