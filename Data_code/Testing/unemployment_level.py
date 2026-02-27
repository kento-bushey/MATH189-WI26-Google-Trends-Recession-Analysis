import pandas as pd

input_path = "../Data/Raw/"
output_path = "../Data/Intermediate/"

input_file = "UNEMPLOY.csv" #FRED
output_file = "unemp_level_cleaned.csv"

df = pd.read_csv(input_path + input_file)

# Convert observation_date to datetime and filter for 2004 onwards
df['observation_date'] = pd.to_datetime(df['observation_date'])
df = df[df['observation_date'] >= '2004-01-01']

# Sort and compute changes (MoM/YoY in thousands/perecent)
df = df.sort_values('observation_date').reset_index(drop=True)
df['unemploy_mom_change'] = df['UNEMPLOY'].diff(periods=1)
df['unemploy_yoy_change'] = df['UNEMPLOY'].diff(periods=12)
df['unemploy_yoy_pct_change'] = df['UNEMPLOY'].pct_change(periods=12) * 100 

# Format dates as YYYY-MM-DD
df['observation_date'] = df['observation_date'].dt.strftime('%Y-%m-%d')
df = df.rename(columns={'observation_date': 'date'})

# Create a dataframe with rows that have empty values
df_empty = df[df.isna().any(axis=1)]

# Drop rows with empty/null values
df_clean = df = df.dropna(subset=['UNEMPLOY'])

# Save cleaned data to a new file
df_clean.to_csv(output_path + output_file, index=False)

print(f"\nCleaned data saved to: {output_path + output_file}")
