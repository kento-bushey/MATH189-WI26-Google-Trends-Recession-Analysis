import pandas as pd
import os
from scipy import stats

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

unemp_path = "../../Data/Intermediate/unemp_rate_cleaned.csv"
base_output_dir = "../../Data/Intermediate/Keywords/First_differences_percent_lead+lag"

unemp_df = pd.read_csv(unemp_path, parse_dates=["date"])
unemp_df = unemp_df.sort_values("date").reset_index(drop=True)

for lag in range(-3, 4):  # -3, -2, -1, 0, 1, 2, 3

    # Folder name: lag_-3, lag_-2, ..., lag_0, ..., lag_3
    lag_label = f"lag_{lag:+d}"  # e.g. lag_-3, lag_+0, lag_+3
    output_dir = os.path.join(base_output_dir, lag_label)
    os.makedirs(output_dir, exist_ok=True)

    # Shift unemployment series by lag
    # Positive lag: unemp leads keyword (unemp moves first)
    # Negative lag: keyword leads unemp (keyword moves first)
    unemp_shifted = unemp_df.copy()
    unemp_shifted["unrate_mom_change"] = unemp_shifted["unrate_mom_change"].shift(lag)

    for csv_path in input_csvs:

        category_name = os.path.splitext(os.path.basename(csv_path))[0]
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
                keyword_df[value_col] = keyword_df[value_col].replace(0, 1)
                keyword_df["first_diff"] = keyword_df[value_col].pct_change() * 100

                merged = pd.merge(
                    keyword_df[["date", "first_diff"]],
                    unemp_shifted[["date", "unrate_mom_change"]],
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

    print(f"Saved all categories for {lag_label}")