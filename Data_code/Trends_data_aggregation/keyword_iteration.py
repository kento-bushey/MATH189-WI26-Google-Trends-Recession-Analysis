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

input_csv = "../../Data_code/Trends_data_aggregation/Keywords/frugality.csv"
output_folder = "../../Data/Raw/Keywords/Frugality"
os.makedirs(output_folder, exist_ok=True)

timeframe = "2004-01-01 2025-12-31"
sleep_seconds = 5
start_row = 0   # skip first <start_row> rows (after header)
max_iters = 50   # number of keywords to process after start_row

keywords = pd.read_csv(input_csv)['keyword'].dropna().tolist()

# Slice keywords to start from start_row and limit to max_iters
keywords_to_process = keywords[start_row:start_row + max_iters]

total = len(keywords_to_process)
for i, kw in enumerate(keywords_to_process, 1):
    try:
        pytrends.build_payload([kw], timeframe=timeframe, geo="US")
        data = pytrends.interest_over_time()
        if "isPartial" in data.columns:
            data = data.drop(columns=["isPartial"])
        data.to_csv(os.path.join(output_folder, f"{kw.replace(' ','_')}.csv"))
    except Exception as e:
        print(f"\nError with keyword '{kw}': {e}")

    # Progress update
    percent_done = (i / total) * 100
    sys.stdout.write(f"\rProgress: {percent_done:.1f}% ({i}/{total})")
    sys.stdout.flush()
    
    time.sleep(sleep_seconds)

print("\nDone.")