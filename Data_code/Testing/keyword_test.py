import pandas as pd
import warnings

pd.set_option('future.no_silent_downcasting', True)
warnings.filterwarnings("ignore", category=FutureWarning)
from pytrends.request import TrendReq
import time
import os

# Path to keyword CSV
keyword_file = "Keywords/credit_and_debt.csv"

# Output path
output_file = "../../Data/Raw/credit_and_debt_monthly_2004_2026.csv"

# Load keywords
keywords_df = pd.read_csv(keyword_file)
kw_list = keywords_df["keyword"].dropna().tolist()

# Initialize pytrends
pytrends = TrendReq(
    hl="en-US",
    tz=360,
    timeout=(10,25),
    retries=3,
    backoff_factor=0.5
)

timeframe = "2004-01-01 2026-12-31"

all_data = pd.DataFrame()

total_keywords = len(kw_list)

for idx, keyword in enumerate(kw_list, 1):

    pytrends.build_payload(
        kw_list=[keyword],   # <-- ONE keyword at a time
        timeframe=timeframe,
        geo="US"
    )

    data = pytrends.interest_over_time()
    data = data.drop(columns=["isPartial"], errors="ignore")

    if not data.empty:
        if all_data.empty:
            all_data = data
        else:
            all_data = all_data.join(data, how="outer")

    progress = (idx / total_keywords) * 100
    print(f"Progress: {progress:.1f}% ({idx}/{total_keywords})   ", end="\r")

    time.sleep(2)

all_data = all_data.reset_index()

os.makedirs(os.path.dirname(output_file), exist_ok=True)
all_data.to_csv(output_file, index=False)

print(f"\nSaved {output_file}")