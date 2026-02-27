import pandas as pd
from decimal import Decimal, getcontext, ROUND_HALF_UP

getcontext().prec = 10

input_path = "../../Data/Raw/"
output_path = "../../Data/Intermediate/"

input_file = "UNRATE.csv"
output_file = "unemp_rate_cleaned.csv"

df = pd.read_csv(input_path + input_file)

df['observation_date'] = pd.to_datetime(df['observation_date'])
df = df[(df['observation_date'] >= '2003-01-01') &
        (df['observation_date'] <= '2025-12-01')]

df = df.sort_values('observation_date').reset_index(drop=True)

# Convert to Decimal (string first to avoid float artifacts)
df['UNRATE'] = df['UNRATE'].astype(str).map(Decimal)

df['unrate_mom_change'] = df['UNRATE'].diff(1)
df['unrate_yoy_change'] = df['UNRATE'].diff(12)

# Quantize to 1 decimal place (percentage points)
q = Decimal("0.1")
df['UNRATE'] = df['UNRATE'].map(lambda x: x.quantize(q, ROUND_HALF_UP) if pd.notna(x) else x)
df['unrate_mom_change'] = df['unrate_mom_change'].map(lambda x: x.quantize(q, ROUND_HALF_UP) if pd.notna(x) else x)
df['unrate_yoy_change'] = df['unrate_yoy_change'].map(lambda x: x.quantize(q, ROUND_HALF_UP) if pd.notna(x) else x)

df = df[df['observation_date'] >= '2004-01-01']
df = df.dropna(subset=['UNRATE'])

df['observation_date'] = df['observation_date'].dt.strftime('%Y-%m-%d')
df = df.rename(columns={'observation_date': 'date'})

df.to_csv(output_path + output_file, index=False)
print(f"\nCleaned data saved to: {output_path + output_file}")