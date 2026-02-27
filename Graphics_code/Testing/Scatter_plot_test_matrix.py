import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import matplotlib.cm as cm
import math

# ====== INPUT ======
keyword_folder = "../../Data/Raw/Keywords/Luxuries"
unemp_path = "../../Data/Intermediate/unemp_rate_cleaned.csv"

# Output directory
output_dir = "../../Graphics/Testing"
os.makedirs(output_dir, exist_ok=True)

# ====== LOAD UNEMPLOYMENT ======
unemp_df = pd.read_csv(unemp_path, parse_dates=["date"])
unemp_df = unemp_df.sort_values("date")

results = []

# ====== RUN REGRESSIONS ======
for filename in os.listdir(keyword_folder):
    if not filename.endswith(".csv"):
        continue

    file_path = os.path.join(keyword_folder, filename)

    keyword_df = pd.read_csv(file_path, parse_dates=["date"])
    keyword_df = keyword_df.sort_values("date")

    value_col = keyword_df.columns[1]
    keyword_df["first_diff"] = keyword_df[value_col].diff()

    merged = pd.merge(
        keyword_df[["date", "first_diff"]],
        unemp_df[["date", "unrate_mom_change"]],
        on="date",
        how="inner"
    ).dropna()

    if len(merged) < 10:
        continue

    x = merged["first_diff"].values
    y = merged["unrate_mom_change"].values

    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)

    results.append({
        "keyword": os.path.splitext(filename)[0],
        "x": x,
        "y": y,
        "slope": slope,
        "intercept": intercept,
        "p_value": p_value
    })

# ====== SORT BY P-VALUE ======
results = sorted(results, key=lambda d: d["p_value"])

# ====== GRID SIZE ======
n = len(results)
cols = 4
rows = math.ceil(n / cols)

# Scale figure size by number of rows/cols
fig_width = 4 * cols
fig_height = 3 * rows
fig, axes = plt.subplots(rows, cols, figsize=(fig_width, fig_height))
axes = axes.flatten()

# Normalize p-values for color scaling
pvals = np.array([r["p_value"] for r in results])
norm = plt.Normalize(vmin=pvals.min(), vmax=pvals.max())
cmap = cm.get_cmap("Reds_r")  # darker = lower p

for i, r in enumerate(results):
    ax = axes[i]

    color = cmap(norm(r["p_value"]))

    ax.scatter(r["x"], r["y"], alpha=0.5)

    # Regression line
    x_line = np.linspace(min(r["x"]), max(r["x"]), 100)
    y_line = r["intercept"] + r["slope"] * x_line
    ax.plot(x_line, y_line)

    # Highlight background by p-value
    ax.set_facecolor(color)

    ax.set_title(f"{r['keyword']}\np={r['p_value']:.3f}", fontsize=8)
    ax.tick_params(labelsize=6)

# Hide unused subplots
for j in range(i+1, len(axes)):
    axes[j].axis("off")

plt.tight_layout()

# ====== SAVE FIGURE ======
folder_name = os.path.basename(keyword_folder.rstrip("/"))
output_path = os.path.join(output_dir, f"{folder_name}_regression_matrix_p_value_colored.png")
plt.savefig(output_path, dpi=300)
plt.close()

print(f"Saved figure to {output_path}")