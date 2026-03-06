import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv("../../Data/Raw/Test/bagel_2004_2025_full_query.csv") # Project/Data/Raw/Test/bagel_2004_2025_full_query.csv

data["date"] = pd.to_datetime(data["date"])

plt.figure()
plt.plot(data["date"], data["bagel"])
plt.xlabel("Date")
plt.ylabel("Search Interest")
plt.title("Google Trends: Bagel (Daily)")

plt.show()
