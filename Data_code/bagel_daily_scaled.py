import pandas as pd

daily = pd.read_csv("../Data/Raw/bagel_daily_2004_2026.csv")
yearly = pd.read_csv("../Data/Raw/bagel_yearly_2004_2026.csv")

daily["date"] = pd.to_datetime(daily["date"])
yearly["date"] = pd.to_datetime(yearly["date"])

daily["year"] = daily["date"].dt.year
yearly["year"] = yearly["date"].dt.year

yearly = yearly[["year", "bagel"]].rename(columns={"bagel": "year_avg"})

merged = daily.merge(yearly, on="year", how="left")

merged["bagel_scaled"] = merged["bagel"] * (merged["year_avg"] / 100)

out = merged[["date", "bagel_scaled"]]

path = "../Data/Intermediate/bagel_daily_scaled.csv"

out.to_csv(path, index=False)

print("Saved "+path)
