import pandas as pd
import os

# Folder containing regression summaries
summary_folder = "../../Data/Intermediate/Keywords"

all_results = []

for filename in os.listdir(summary_folder):
    if not filename.endswith(".csv"):
        continue

    file_path = os.path.join(summary_folder, filename)

    df = pd.read_csv(file_path)

    # Add category name from filename
    category_name = os.path.splitext(filename)[0].replace("_regression_summary", "")
    df["category"] = category_name

    all_results.append(df)

# Combine all summaries
combined_df = pd.concat(all_results, ignore_index=True)

# Sort by p-value (ascending)
top_3 = combined_df.sort_values("p_value").head(3)

pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.width", None)
pd.set_option("display.max_colwidth", None)

print(top_3[[
    "category",
    "keyword",
    "p_value",
    "slope",
]])