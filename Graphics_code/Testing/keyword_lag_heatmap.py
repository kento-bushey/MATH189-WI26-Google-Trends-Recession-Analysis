import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import os

# ====== PATHS ======
base_data_dir = "../../Data/Intermediate/Keywords/First_differences_percent_lead+lag"
output_dir = "../../Graphics/Testing/Keyword_regression_heat_map"
os.makedirs(output_dir, exist_ok=True)

lags = range(-3, 4)  # -3 to +3
lag_labels = [f"lag_{l:+d}" for l in lags]

categories = [
    "credit_and_debt",
    "frugality",
    "government_support",
    "housing_rent_and_stress",
    "inflation",
    "insurance",
    "investing_and_markets",
    "jobs",
    "luxuries",
    "travel"
]

# ====== COLLECT ALL KEYWORDS ACROSS ALL CATEGORIES ======
# Structure: { keyword -> { lag -> {p_value, r_squared, slope} } }
all_data = {}  # { (category, keyword) -> {lag -> row} }

for lag in lags:
    lag_label = f"lag_{lag:+d}"
    lag_dir = os.path.join(base_data_dir, lag_label)

    for category in categories:
        csv_path = os.path.join(lag_dir, f"{category.capitalize()}_regression_summary.csv")

        if not os.path.exists(csv_path):
            print(f"Missing: {csv_path}")
            continue

        df = pd.read_csv(csv_path)

        for _, row in df.iterrows():
            key = (category, row["keyword"])
            if key not in all_data:
                all_data[key] = {}
            all_data[key][lag] = {
                "p_value": row["p_value"],
                "r_squared": row["r_squared"],
                "slope": row["slope"]
            }

# ====== BUILD HEATMAP MATRIX PER CATEGORY ======
for category in categories:

    # Filter keys for this category
    cat_keys = [(c, kw) for (c, kw) in all_data if c == category]
    if not cat_keys:
        print(f"No data for {category}")
        continue

    keywords = sorted([kw for (_, kw) in cat_keys])
    n_keywords = len(keywords)
    n_lags = len(lags)

    # Build matrices
    pval_matrix = np.full((n_keywords, n_lags), np.nan)
    slope_matrix = np.full((n_keywords, n_lags), np.nan)

    for i, kw in enumerate(keywords):
        key = (category, kw)
        for j, lag in enumerate(lags):
            if lag in all_data.get(key, {}):
                pval_matrix[i, j] = all_data[key][lag]["p_value"]
                slope_matrix[i, j] = all_data[key][lag]["slope"]

    # ====== PLOT ======
    fig_height = max(4, n_keywords * 0.45 + 2)
    fig, ax = plt.subplots(figsize=(10, fig_height))

    # Switch to log norm for order-of-magnitude color scaling
    log_pval = -np.log10(np.clip(pval_matrix, 1e-10, 1))
    vmax = max(4, np.nanmax(log_pval))

    cmap = plt.cm.RdYlGn
    im = ax.imshow(log_pval, aspect="auto", cmap=cmap, vmin=0, vmax=vmax)

    # Overlay p-value text
    for i in range(n_keywords):
        for j in range(n_lags):
            if not np.isnan(pval_matrix[i, j]):
                pval = pval_matrix[i, j]
                # Format: scientific notation
                text = f"{pval:.2e}"
                # White text on dark cells, black on light
                cell_brightness = log_pval[i, j] / vmax
                txt_color = "white" if cell_brightness > 0.6 else "black"
                ax.text(j, i, text, ha="center", va="center",
                        fontsize=6, color=txt_color,
                        fontweight="bold" if pval < 0.05 else "normal")

    # Axes
    ax.set_xticks(range(n_lags))
    ax.set_xticklabels([f"{l:+d}" for l in lags], fontsize=9)
    ax.set_yticks(range(n_keywords))
    ax.set_yticklabels(keywords, fontsize=8)
    ax.set_xlabel("Lag (negative = keyword leads unemployment)", fontsize=10)
    ax.set_title(f"{category.replace('_', ' ').title()} — Keyword vs. Unemployment\n"
                 f"Color: −log₁₀(p-value)   bold = p < 0.05",
                 fontsize=11, pad=12)

    # Significance threshold line on colorbar
    cbar = fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
    cbar.set_label("-log₁₀(p-value)", fontsize=9)
    cbar.ax.axhline(-np.log10(0.05), color="black", linewidth=1.5, linestyle="--")
    cbar.ax.text(2.6, -np.log10(0.05), "p=0.05", va="center", fontsize=7)

    plt.tight_layout()

    out_path = os.path.join(output_dir, f"{category}_lag_heatmap.png")
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out_path}")

print("Done.")