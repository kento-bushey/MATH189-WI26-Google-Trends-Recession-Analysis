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
fig, ax = plt.subplots(figsize=(14, 7))

# Faded individual keyword lines
for col in data.columns:
    ax.plot(data.index, data[col], color="steelblue", alpha=0.15, linewidth=0.8)

# Bold average line on top
ax.plot(average.index, average, color="crimson", linewidth=2.5, label="Category average", zorder=5)

ax.set_xlabel("Date")
ax.set_ylabel("Google Trends Interest")
ax.set_title("Credit & Debt Keywords (Monthly, 2004-2026)")
ax.legend(fontsize="small")
plt.tight_layout()
plt.show()