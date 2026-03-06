import pandas as pd
import matplotlib.pyplot as plt
import os

# ====== VARIABLE: change this to check different keywords ======
csv_file = "apr.csv"

# ====== PATHS ======
before_path = os.path.join(os.path.dirname(__file__),
    f"../../Data/Raw/Keywords/Credit_and_debt/{csv_file}")
after_path = os.path.join(os.path.dirname(__file__),
    f"../../Data/Corrected_for_yearly_pattern/Keywords/Credit_and_debt/{csv_file}")
output_dir = os.path.join(os.path.dirname(__file__),
    "../../Graphics/Corrected_for_yearly_pattern/Before_and_after")
os.makedirs(output_dir, exist_ok=True)

# ====== LOAD ======
before_df = pd.read_csv(before_path, parse_dates=["date"]).set_index("date")
after_df  = pd.read_csv(after_path,  parse_dates=["date"]).set_index("date")
value_col = before_df.columns[0]

# ====== HELPER: label a specific month ======
def label_month(ax, series, month=4, month_name="apr"):
    points = series[series.index.month == month]
    for date, val in points.items():
        ax.annotate(f"{date.year}\n{month_name}", xy=(date, val), xytext=(4, 4),
                    textcoords="offset points", fontsize=6.5,
                    color="black", fontweight="bold", zorder=10)
        ax.scatter(date, val, color="black", s=20, zorder=6)

# ====== PLOT ======
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5), sharey=True)

ax1.plot(before_df.index, before_df[value_col], color="steelblue", linewidth=1.2)
label_month(ax1, before_df[value_col])
ax1.set_title("Before correction")
ax1.set_xlabel("Date")
ax1.set_ylabel("Google Trends Interest")

ax2.plot(after_df.index, after_df[value_col], color="crimson", linewidth=1.2)
label_month(ax2, after_df[value_col])
ax2.set_title("After correction")
ax2.set_xlabel("Date")

title = os.path.splitext(csv_file)[0]
fig.suptitle(f"{title} — seasonal correction before & after", fontsize=13, fontweight="bold")
plt.tight_layout()

out_path = os.path.join(output_dir, f"{title}_before_and_after.png")
plt.savefig(out_path, dpi=150, bbox_inches="tight")
plt.close()
print(f"Saved: {out_path}")