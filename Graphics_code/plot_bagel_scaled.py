import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv("../Data/Intermediate/bagel_daily_scaled.csv")

data["date"] = pd.to_datetime(data["date"])

plt.figure()
plt.plot(data["date"], data["bagel_scaled"])
plt.xlabel("Date")
plt.ylabel("Scaled Search Interest")
plt.title("Google Trends: Bagel (Daily, Year-Scaled)")

plt.show()
