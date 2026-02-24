from pytrends.request import TrendReq
import pandas as pd

pytrends = TrendReq(hl="en-US", tz=360)

kw_list = ["bagel"]
timeframe = "2004-01-01 2026-12-31"

pytrends.build_payload(kw_list, timeframe=timeframe)
data = pytrends.interest_over_time()

data = data.drop(columns=["isPartial"], errors="ignore")
data.to_csv("../Data/Raw/bagel_monthly_2004_2026.csv")

print("Saved ../Data/Raw/bagel_monthly_2004_2026.csv")
