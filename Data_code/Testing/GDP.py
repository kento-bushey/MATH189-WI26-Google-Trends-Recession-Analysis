import pandas as pd

input_path = "../Data/Raw/"
output_path = "../Data/Intermediate/"

input_file = "A191RO1Q156NBEA.csv" #FRED
output_file = "GDP_YoY_pct_cleaned.csv"

df = pd.read_csv(input_path + input_file)

# Convert observation_date to datetime and filter for 2004 onwards
df['observation_date'] = pd.to_datetime(df['observation_date'])
df = df[df['observation_date'] >= '2004-01-01']

# Sorting
df = df.sort_values('observation_date').reset_index(drop=True)
df = df.rename(columns={'A191RO1Q156NBEA': 'gdp_yoy_pct_change'})

monthly_index = pd.date_range(
    start='2004-01-01',
    end='2025-12-01',
    freq='MS'  # Month Start frequency
)

# Forward-fill quarterly values across empty months
df = df.set_index('observation_date')
df = df.reindex(monthly_index)
df = df.ffill()
df.index.name = 'observation_date'
df = df.reset_index()

df = df.dropna(subset=['gdp_yoy_pct_change'])

# Format dates as YYYY-MM-DD
df['observation_date'] = df['observation_date'].dt.strftime('%Y-%m-%d')
df = df.rename(columns={'observation_date': 'date'})

# Save cleaned data to a new file
df.to_csv(output_path + output_file, index=False)
print(f"\nCleaned data saved to: {output_path + output_file}")