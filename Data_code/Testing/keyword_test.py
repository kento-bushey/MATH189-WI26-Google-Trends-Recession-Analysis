import pandas as pd
from pytrends.request import TrendReq
import time
import os

# Path to keyword CSV
keyword_file = "Keywords/credit_and_debt.csv"

# Output path
output_file = "../../Data/Raw/credit_and_debt_monthly_2004_2026.csv"

# Load keywords
keywords_df = pd.read_csv(keyword_file)
kw_list = keywords_df["keyword"].tolist()

# Initialize pytrends
pytrends = TrendReq(
    hl="en-US",
    tz=360,
    timeout=(10,25),
    retries=3,
    backoff_factor=0.5
)

# Full timeframe
timeframe = "2004-01-01 2026-12-31"

# Prepare dataframe to accumulate results
all_data = pd.DataFrame()

# Google Trends allows up to ~5 keywords at a time reliably
chunk_size = 5


total_chunks = (len(kw_list) + chunk_size - 1) // chunk_size

for idx, start in enumerate(range(0, len(kw_list), chunk_size), 1):
    chunk = kw_list[start:start+chunk_size]
    
    pytrends.build_payload(
        kw_list=chunk,
        timeframe=timeframe,
        geo="US"
    )
    
    data = pytrends.interest_over_time()
    if not data.empty:
        data = data.drop(columns=["isPartial"], errors="ignore")
        if all_data.empty:
            all_data = data
        else:
            all_data = all_data.join(data, how="outer")
    
    progress = (idx / total_chunks) * 100
    print(f"Progress: {progress:.1f}% ({start+1}-{start+len(chunk)} of {len(kw_list)} keywords)   ", end="\r")
    
    time.sleep(2)

all_data = all_data.reset_index()

# Save CSV
os.makedirs(os.path.dirname(output_file), exist_ok=True)
all_data.to_csv(output_file, index=False)

print(f"Saved {output_file}")