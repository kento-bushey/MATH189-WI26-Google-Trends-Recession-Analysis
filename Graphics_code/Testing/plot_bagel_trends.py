import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv("../Data/Raw/bagel_trends_2004_2026.csv")

data["date"] = pd.to_datetime(data["date"])

plt.figure()
plt.plot(data["date"], data["bagel"])
plt.xlabel("Date")
plt.ylabel("Search Interest")
plt.title("Google Trends: Bagel (Daily)")

plt.show()
