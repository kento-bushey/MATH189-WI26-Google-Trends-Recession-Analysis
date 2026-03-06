import pandas as pd
import numpy as np
import os

# ====== PATHS ======
keyword_base = "../../Data/Raw/Keywords"
output_base = "../../Data/Corrected_for_yearly_pattern/Keywords"

folders = [
    "Credit_and_debt", "Frugality", "Government_support",
    "Housing_rent_and_stress", "Inflation", "Insurance",
    "Investing_and_markets", "Jobs", "Luxuries", "Travel"
]

# ====== APPLY CORRECTIONS PER FILE ======
for folder in folders:
    input_folder = os.path.join(keyword_base, folder)
    output_folder = os.path.join(output_base, folder)
    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(input_folder):
        if not filename.endswith(".csv"):
            continue

        input_path  = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, filename)

        try:
            df = pd.read_csv(input_path, parse_dates=["date"])
            value_col = df.columns[1]

            df["month_num"] = df["date"].dt.month

            # Compute this keyword's own monthly means and grand mean
            monthly_means = df.groupby("month_num")[value_col].mean()
            grand_mean = df[value_col].mean()

            # Correction factor per month: inverse of how far that month sits from grand mean
            correction_factors = {
                month: grand_mean / mean
                for month, mean in monthly_means.items()
            }

            # Apply correction
            df[value_col] = df.apply(
                lambda row: row[value_col] * correction_factors[row["month_num"]],
                axis=1
            )

            df = df.drop(columns=["month_num"])
            df.to_csv(output_path, index=False)

        except Exception as e:
            print(f"Error processing {filename}: {e}")

    print(f"Processed {folder}")

print("\nDone. Corrected files saved to Data/Corrected_for_yearly_pattern/Keywords")