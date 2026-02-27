from pytrends.request import TrendReq
import pandas as pd
import os
import time
import sys

pytrends = TrendReq(
    hl="en-US",
    tz=360,
    timeout=(10,25),
    retries=3,
    backoff_factor=0.5,
    requests_args={'headers':{'User-Agent':'Mozilla/5.0'}}
)

# List of input CSV files
input_csvs = [
    "../../Data_code/Trends_data_aggregation/Keywords/insurance.csv",
    "../../Data_code/Trends_data_aggregation/Keywords/investing_and_markets.csv",
    "../../Data_code/Trends_data_aggregation/Keywords/government_support.csv",
    "../../Data_code/Trends_data_aggregation/Keywords/jobs.csv",
    "../../Data_code/Trends_data_aggregation/Keywords/housing_rent_and_stress.csv",
    "../../Data_code/Trends_data_aggregation/Keywords/luxuries.csv",
    "../../Data_code/Trends_data_aggregation/Keywords/inflation.csv",
    "../../Data_code/Trends_data_aggregation/Keywords/travel.csv"
]

# Corresponding output folders
output_folders = [
    "../../Data/Raw/Keywords/Insurance",
    "../../Data/Raw/Keywords/Investing_and_markets",
    "../../Data/Raw/Keywords/Government_support",
    "../../Data/Raw/Keywords/Jobs",
    "../../Data/Raw/Keywords/Housing_rent_and_stress",
    "../../Data/Raw/Keywords/Luxuries",
    "../../Data/Raw/Keywords/Inflation",
    "../../Data/Raw/Keywords/Travel"
]

timeframe = "2004-01-01 2025-12-31"
sleep_seconds = 5
start_row = 0   # skip first <start_row> rows
max_iters = 50  # max keywords per CSV

for csv_path, out_folder in zip(input_csvs, output_folders):
    os.makedirs(out_folder, exist_ok=True)
    
    keywords = pd.read_csv(csv_path)['keyword'].dropna().tolist()
    keywords_to_process = keywords[start_row:start_row + max_iters]
    total = len(keywords_to_process)
    
    for i, kw in enumerate(keywords_to_process, 1):
        try:
            pytrends.build_payload([kw], timeframe=timeframe, geo="US")
            data = pytrends.interest_over_time()
            if "isPartial" in data.columns:
                data = data.drop(columns=["isPartial"])
            data.to_csv(os.path.join(out_folder, f"{kw.replace(' ','_')}.csv"))
        except Exception as e:
            print(f"\nError with keyword '{kw}': {e}")
        
        # Progress update
        percent_done = (i / total) * 100
        sys.stdout.write(f"\rProcessing {os.path.basename(csv_path)}: {percent_done:.1f}% ({i}/{total})")
        sys.stdout.flush()
        
        time.sleep(sleep_seconds)

print("\nAll CSV files processed.")