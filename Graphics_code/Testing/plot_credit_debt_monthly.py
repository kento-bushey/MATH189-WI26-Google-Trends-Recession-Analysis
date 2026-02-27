import pandas as pd
import matplotlib.pyplot as plt
import os

# Path to the CSV
csv_file = "credit_and_debt.csv"
csv_path = os.path.join(os.path.dirname(__file__), "../../Data/Raw/Keywords/Credit_and_debt", csv_file)

# Load data
data = pd.read_csv(csv_path)
data["date"] = pd.to_datetime(data["date"])
data = data.set_index("date")

# Plot
plt.figure(figsize=(14, 7))
for col in data.columns:
    plt.plot(data.index, data[col], label=col)

plt.xlabel("Date")
plt.ylabel("Google Trends Interest")
plt.title("Credit & Debt Keywords (Monthly, 2004-2026)")
plt.legend(loc="upper left", fontsize="small", ncol=2)
plt.tight_layout()
plt.show()