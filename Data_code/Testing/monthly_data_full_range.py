from pytrends.request import TrendReq
import pandas as pd

pytrends = TrendReq(
    hl="en-US",
    tz=360,
    timeout=(10,25),
    retries=3,
    backoff_factor=0.5
)

kw_list = ["bagel"]
timeframe = "2004-01-01 2025-12-31"

pytrends.build_payload(
    kw_list=kw_list,
    timeframe=timeframe,
    geo="US"
)

data = pytrends.interest_over_time()
data = data.drop(columns=["isPartial"], errors="ignore")

data.to_csv("../../Data/Raw/bagel_2004_2025_full_query.csv")

print("Saved ../../Data/Raw/bagel_2004_2025_full_query.csv")