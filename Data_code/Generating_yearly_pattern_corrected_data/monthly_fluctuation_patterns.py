import pandas as pd
import numpy as np
import os

keyword_base = "../../Data/Raw/Keywords"

folders = [
    "Credit_and_debt", "Frugality", "Government_support",
    "Housing_rent_and_stress", "Inflation", "Insurance",
    "Investing_and_markets", "Jobs", "Luxuries", "Travel"
]

# Collect all values by month-of-year across every CSV
monthly_totals = {m: [] for m in range(1, 13)}

for folder in folders:
    folder_path = os.path.join(keyword_base, folder)
    for filename in os.listdir(folder_path):
        if not filename.endswith(".csv"):
            continue
        df = pd.read_csv(os.path.join(folder_path, filename), parse_dates=["date"])
        df["month"] = df["date"].dt.month
        value_col = df.columns[1]
        for month, group in df.groupby("month"):
            monthly_totals[month].extend(group[value_col].tolist())

# Compute overall grand mean and per-month means
all_values = [v for vals in monthly_totals.values() for v in vals]
grand_mean = np.mean(all_values)

month_names = ["Jan","Feb","Mar","Apr","May","Jun",
               "Jul","Aug","Sep","Oct","Nov","Dec"]

print(f"Grand mean search value across all keywords/months: {grand_mean:.2f}\n")
print(f"{'Month':<6} {'Mean':>8} {'Diff':>10} {'% vs avg':>10}")
print("-" * 38)

for m in range(1, 13):
    mean = np.mean(monthly_totals[m])
    diff = mean - grand_mean
    pct = (diff / grand_mean) * 100
    flag = " ◀ below avg" if pct < 0 else ""
    print(f"{month_names[m-1]:<6} {mean:>8.2f} {diff:>+10.2f} {pct:>+9.2f}%{flag}")



output_dir = "../../Data/Corrected_for_yearly_pattern"
os.makedirs(output_dir, exist_ok=True)

results_df = pd.DataFrame([{
    "month": month_names[m-1],
    "mean": np.mean(monthly_totals[m]),
    "diff_from_grand_mean": np.mean(monthly_totals[m]) - grand_mean,
    "pct_vs_avg": ((np.mean(monthly_totals[m]) - grand_mean) / grand_mean) * 100
} for m in range(1, 13)])

results_df.to_csv(os.path.join(output_dir, "monthly_seasonal_pattern.csv"), index=False)
print("\nSaved to Data/Corrected_for_yearly_pattern/monthly_seasonal_pattern.csv")