import pandas as pd
import os
import matplotlib.pyplot as plt
from scipy import stats
import numpy as np

#keyword_path = "../../Data/Raw/Keywords/Insurance/claim_status.csv"
#keyword_path = "../../Data/Raw/Keywords/Government_support/pandemic_relief_fund.csv"

keyword_path = "../../Data/Raw/Keywords/Government_support/pandemic_relief_fund.csv"


unemp_path = "../../Data/Intermediate/unemp_rate_cleaned.csv"
output_path = "../../Data/Intermediate/Testing/keyword_first_differences.csv"

os.makedirs("../../Data/Intermediate/Testing", exist_ok=True)

# Load keyword data
keyword_df = pd.read_csv(keyword_path, parse_dates=["date"])
keyword_df = keyword_df.sort_values("date")

value_col = keyword_df.columns[1]

keyword_df["first_diff"] = keyword_df[value_col].diff()
keyword_df.to_csv(output_path, index=False)

# Load unemployment data
unemp_df = pd.read_csv(unemp_path, parse_dates=["date"])
unemp_df = unemp_df.sort_values("date")

merged = pd.merge(
    keyword_df[["date", "first_diff"]],
    unemp_df[["date", "unrate_mom_change"]],
    on="date",
    how="inner"
).dropna()

x = merged["first_diff"].values
y = merged["unrate_mom_change"].values

# Linear regression
slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)

print("Intercept:", intercept)
print("Slope:", slope)
print("R-squared:", r_value**2)
print("P-value (slope):", p_value)
print("Std error:", std_err)

# Scatter plot + regression line
plt.figure()
plt.scatter(x, y)

x_line = np.linspace(min(x), max(x), 100)
y_line = intercept + slope * x_line
plt.plot(x_line, y_line)

plt.xlabel("Keyword First Difference")
plt.ylabel("Unemployment MoM Change")
plt.title("Keyword First Differences vs Unemployment MoM Change")
plt.show()