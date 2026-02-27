import pandas as pd
import os
from scipy import stats

# List of category CSV definitions
input_csvs = [
    "../../Data_code/Trends_data_aggregation/Keywords/credit_and_debt.csv",
    "../../Data_code/Trends_data_aggregation/Keywords/frugality.csv",
    "../../Data_code/Trends_data_aggregation/Keywords/insurance.csv",
    "../../Data_code/Trends_data_aggregation/Keywords/investing_and_markets.csv",
    "../../Data_code/Trends_data_aggregation/Keywords/government_support.csv",
    "../../Data_code/Trends_data_aggregation/Keywords/jobs.csv",
    "../../Data_code/Trends_data_aggregation/Keywords/housing_rent_and_stress.csv",
    "../../Data_code/Trends_data_aggregation/Keywords/luxuries.csv",
    "../../Data_code/Trends_data_aggregation/Keywords/inflation.csv",
    "../../Data_code/Trends_data_aggregation/Keywords/travel.csv"
]

# Unemployment data
unemp_path = "../../Data/Intermediate/unemp_rate_cleaned.csv"

# Output directory
output_dir = "../../Data/Intermediate/Keywords"
os.makedirs(output_dir, exist_ok=True)

# Load unemployment data once
unemp_df = pd.read_csv(unemp_path, parse_dates=["date"])
unemp_df = unemp_df.sort_values("date")

for csv_path in input_csvs:

    # Derive category name from CSV filename
    category_name = os.path.splitext(os.path.basename(csv_path))[0]

    # Corresponding folder containing keyword time series
    keyword_folder = f"../../Data/Raw/Keywords/{category_name.capitalize() if category_name != 'investing_and_markets' else 'Investing_and_markets'}"

    results = []

    if not os.path.exists(keyword_folder):
        print(f"Folder not found: {keyword_folder}")
        continue

    for filename in os.listdir(keyword_folder):
        if not filename.endswith(".csv"):
            continue

        file_path = os.path.join(keyword_folder, filename)

        try:
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

            if len(merged) < 5:
                continue

            x = merged["first_diff"].values
            y = merged["unrate_mom_change"].values

            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)

            results.append({
                "keyword": os.path.splitext(filename)[0],
                "intercept": intercept,
                "slope": slope,
                "r_squared": r_value**2,
                "p_value": p_value,
                "std_error": std_err,
                "n_obs": len(merged)
            })

        except Exception as e:
            print(f"Error processing {filename}: {e}")

    summary_df = pd.DataFrame(results)

    output_path = os.path.join(output_dir, f"{category_name.capitalize()}_regression_summary.csv")
    summary_df.to_csv(output_path, index=False)

    print(f"Saved {output_path}")