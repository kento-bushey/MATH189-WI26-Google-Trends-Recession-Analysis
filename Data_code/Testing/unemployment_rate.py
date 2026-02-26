import pandas as pd

input_path = "../Data/Raw/"
output_path = "../Data/Intermediate/"

input_file = "UNRATE.csv" #FRED
output_file = "unemp_rate_cleaned.csv"

df = pd.read_csv(input_path + input_file)

# Convert observation_date to datetime and filter for 2004 onwards
df['observation_date'] = pd.to_datetime(df['observation_date'])
df = df[df['observation_date'] >= '2004-01-01']
df = df[df['observation_date'] <= '2025-12-01']

# Sort and compute changes (MoM/YoY in percentage points)
df = df.sort_values('observation_date').reset_index(drop=True)
df['unrate_mom_change'] = df['UNRATE'].diff(periods=1)
df['unrate_yoy_change'] = df['UNRATE'].diff(periods=12)

# Drop rows with empty/null values in unemployment rate
df = df.dropna(subset=['UNRATE'])

# Format dates as YYYY-MM-DD
df['observation_date'] = df['observation_date'].dt.strftime('%Y-%m-%d')
df = df.rename(columns={'observation_date': 'date'})

# Save cleaned data to a new file
df.to_csv(output_path + output_file, index=False)

print(f"\nCleaned data saved to: {output_path + output_file}")
