import pandas as pd
import matplotlib.pyplot as plt
import math
import os

# ====== PATHS ======
raw_base = os.path.join(os.path.dirname(__file__), "../../Data/Raw/Keywords")
corrected_base = os.path.join(os.path.dirname(__file__), "../../Data/Corrected_for_yearly_pattern/Keywords")
output_dir = os.path.join(os.path.dirname(__file__), "../../Graphics/Corrected_for_yearly_pattern/Before_and_after/Keywords")
os.makedirs(output_dir, exist_ok=True)

folders = [
    "Credit_and_debt", "Frugality", "Government_support",
    "Housing_rent_and_stress", "Inflation", "Insurance",
    "Investing_and_markets", "Jobs", "Luxuries", "Travel"
]

for folder in folders:
    raw_folder = os.path.join(raw_base, folder)
    corrected_folder = os.path.join(corrected_base, folder)

    csvfiles = sorted([f for f in os.listdir(raw_folder) if f.endswith(".csv")])
    n = len(csvfiles)

    # Each keyword gets 2 side-by-side subplots; lay them out in rows of 4 keywords (8 cols)
    keywords_per_row = 4
    cols = keywords_per_row * 2  # 8 columns (before/after pairs)
    rows = math.ceil(n / keywords_per_row)

    fig, axes = plt.subplots(rows, cols, figsize=(cols * 2.2, rows * 2.8))
    axes = axes.flatten()

    for i, filename in enumerate(csvfiles):
        keyword = os.path.splitext(filename)[0]
        before_path = os.path.join(raw_folder, filename)
        after_path  = os.path.join(corrected_folder, filename)

        ax_before = axes[i * 2]
        ax_after  = axes[i * 2 + 1]

        try:
            before_df = pd.read_csv(before_path, parse_dates=["date"]).set_index("date")
            after_df  = pd.read_csv(after_path,  parse_dates=["date"]).set_index("date")
            value_col = before_df.columns[0]

            ax_before.plot(before_df.index, before_df[value_col], color="steelblue", linewidth=0.7)
            ax_after.plot(after_df.index,   after_df[value_col],  color="crimson",   linewidth=0.7)

        except Exception as e:
            ax_before.text(0.5, 0.5, "error", ha="center", va="center", fontsize=6)
            ax_after.text( 0.5, 0.5, "error", ha="center", va="center", fontsize=6)
            print(f"Error: {filename}: {e}")

        ax_before.set_title(f"{keyword}\nbefore", fontsize=5.5)
        ax_after.set_title( f"{keyword}\nafter",  fontsize=5.5)
        ax_before.tick_params(labelsize=4)
        ax_after.tick_params( labelsize=4)

    # Hide any unused axes
    for j in range(i * 2 + 2, len(axes)):
        axes[j].axis("off")

    fig.suptitle(f"{folder} — Before & After Seasonal Correction", fontsize=13, fontweight="bold")
    plt.tight_layout(rect=[0, 0, 1, 0.97])

    out_path = os.path.join(output_dir, f"{folder}_before_and_after.png")
    plt.savefig(out_path, dpi=300, bbox_inches="tight")

    out_path = os.path.join(output_dir, f"{folder}_before_and_after.png")
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out_path}")

print("Done.")