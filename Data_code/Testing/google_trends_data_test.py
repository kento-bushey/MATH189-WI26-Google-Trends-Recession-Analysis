from pytrends.request import TrendReq
import pandas as pd
from datetime import datetime, timedelta
import time

pytrends = TrendReq(
    hl="en-US",
    tz=360,
    timeout=(10, 25),
    retries=3,
    backoff_factor=0.5
)

kw_list = ["bagel"]

start = datetime(2004,1,1)
end   = datetime(2026,12,31)

delta = timedelta(days=60)

frames = []

total_chunks = ((end - start).days // delta.days) + 1
completed = 0

cur = start
while cur < end:
    nxt = min(cur + delta, end)
    timeframe = f"{cur.date()} {nxt.date()}"

    try:
        pytrends.build_payload(kw_list, timeframe=timeframe)
        df = pytrends.interest_over_time()
        if not df.empty:
            df = df.drop(columns=["isPartial"], errors="ignore")
            frames.append(df)
    except Exception as e:
        print("Chunk failed:", timeframe)
        print(e)

    completed += 1
    percent = 100 * completed / total_chunks
    print(f"{percent:.1f}% complete")

    time.sleep(2)
    cur = nxt + timedelta(days=1)

final = pd.concat(frames)
final = final[~final.index.duplicated(keep="first")]
final.to_csv("../Data/Raw/bagel_trends_2004_2026.csv")

print("Saved ../Data/Raw/bagel_trends_2004_2026.csv")
