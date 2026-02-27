"""
Stitch all Google Trends keyword CSVs into a single long-format DataFrame.

Output columns: date, keyword, category, search_interest
- keyword:         derived from filename (e.g. "bankruptcy")
- category:        derived from parent directory (e.g. "Credit_and_debt")
- search_interest: the Google Trends index value (0–100)

Outputs:
  Data/Intermediate/all_keywords_long.csv
"""

import os
import pandas as pd
from pathlib import Path

# ── Config ──────────────────────────────────────────────────────────────
KEYWORDS_DIR = Path("Data/Raw/Keywords")
OUTPUT_DIR   = Path("Data/Intermediate")
OUTPUT_FILE  = OUTPUT_DIR / "all_keywords_long.csv"

# ── Collect all CSVs ────────────────────────────────────────────────────
frames = []
skipped = []

for category_dir in sorted(KEYWORDS_DIR.iterdir()):
    if not category_dir.is_dir():
        continue

    category = category_dir.name  # e.g. "Credit_and_debt"

    for csv_file in sorted(category_dir.glob("*.csv")):
        keyword = csv_file.stem  # filename without .csv

        try:
            df = pd.read_csv(csv_file)

            # The value column is whatever isn't "date"
            value_col = [c for c in df.columns if c.lower() != "date"]
            if not value_col:
                skipped.append((csv_file, "no value column found"))
                continue

            df = df.rename(columns={
                "date": "date",
                value_col[0]: "search_interest"
            })

            # Coerce to numeric — Google Trends sometimes has "<1" or missing
            df["search_interest"] = pd.to_numeric(df["search_interest"], errors="coerce")
            df["date"]     = pd.to_datetime(df["date"], errors="coerce")
            df["keyword"]  = keyword
            df["category"] = category

            frames.append(df[["date", "keyword", "category", "search_interest"]])

        except Exception as e:
            skipped.append((csv_file, str(e)))

# ── Concatenate & save ──────────────────────────────────────────────────
combined = pd.concat(frames, ignore_index=True)
combined = combined.sort_values(["category", "keyword", "date"]).reset_index(drop=True)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
combined.to_csv(OUTPUT_FILE, index=False)

# ── Summary ─────────────────────────────────────────────────────────────
print(f"Saved {OUTPUT_FILE}")
print(f"   Rows:       {len(combined):,}")
print(f"   Keywords:   {combined['keyword'].nunique()}")
print(f"   Categories: {combined['category'].nunique()}")
print(f"   Date range: {combined['date'].min().date()} → {combined['date'].max().date()}")
print(f"\nCategories breakdown:")
print(combined.groupby("category")["keyword"].nunique().to_string())

if skipped:
    print(f"\n⚠️  Skipped {len(skipped)} files:")
    for path, reason in skipped:
        print(f"   {path}: {reason}")