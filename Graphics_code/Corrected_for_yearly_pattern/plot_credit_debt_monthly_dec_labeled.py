import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# ====== PATH ======
folder_path = os.path.join(os.path.dirname(__file__), "../../Data/Raw/Keywords/Credit_and_debt")

# ====== LOAD ALL CSVs IN FOLDER ======
all_series = {}

for filename in os.listdir(folder_path):
    if not filename.endswith(".csv"):
        continue
    df = pd.read_csv(os.path.join(folder_path, filename), parse_dates=["date"])
    df = df.set_index("date")
    value_col = df.columns[0]
    all_series[os.path.splitext(filename)[0]] = df[value_col]

data = pd.DataFrame(all_series).sort_index()
average = data.mean(axis=1)

# ====== PLOT ======
fig, ax = plt.subplots(figsize=(18, 9))

# Faded individual keyword lines
for col in data.columns:
    ax.plot(data.index, data[col], color="steelblue", alpha=0.15, linewidth=0.8)

# Bold average line on top
ax.plot(average.index, average, color="orange", linewidth=2.5, label="Category average", zorder=5)

ax.set_ylim(20, 80)
ax.set_xlabel("Date", fontsize=16)
ax.set_ylabel("Google Trends Interest", fontsize=16)
ax.set_title("Credit & Debt Keywords (Monthly, 2004-2026)", fontsize=20)
ax.tick_params(axis="both", labelsize=13)
ax.legend(fontsize=14)

# Label every December point on the average line
dec_points = average[average.index.month == 12]
for date, val in dec_points.items():
    ax.annotate(str(date.year) + "\ndec", xy=(date, val), xytext=(4, 4),
                textcoords="offset points", fontsize=11,
                color="black", fontweight="bold", zorder=10)
    ax.scatter(date, val, color="black", s=20, zorder=6)

plt.tight_layout()
output_dir = os.path.join(os.path.dirname(__file__), "../../Graphics/Corrected_for_yearly_pattern")
os.makedirs(output_dir, exist_ok=True)
plt.savefig(os.path.join(output_dir, "credit_and_debt_average.png"), dpi=300, bbox_inches="tight")
plt.close()
print("Saved to Graphics/Corrected_for_yearly_pattern/credit_and_debt_average.png")