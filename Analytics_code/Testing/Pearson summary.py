import pandas as pd
import os
import glob

input_dir = "../Output"
output_dir = "../Output"

# Load all keyword-level CSVs
kw_files = glob.glob(os.path.join(input_dir, "pearson_keywords_*.csv"))
kw_all = []
for f in kw_files:
    df = pd.read_csv(f)
    name = os.path.splitext(os.path.basename(f))[0]
    parts = name.replace("pearson_keywords_", "").rsplit("_", 2)
    df["macro"] = parts[0]
    df["period"] = parts[1] + "_" + parts[2]
    kw_all.append(df)

kw_df = pd.concat(kw_all, ignore_index=True)
kw_sig = kw_df[kw_df["significant"] == True].copy()
kw_sig["abs_r"] = kw_sig["pearson_r"].abs()

# Top 20 strongest positive correlations (unique keywords)
print("\nTop 20 positive correlations (unique keywords):")
top20 = kw_sig.sort_values("pearson_r", ascending=False).drop_duplicates(subset="keyword").head(20)
print(top20[["macro", "period", "category", "keyword", "pearson_r", "p_adj_bh"]].to_string(index=False))

# Top 20 strongest negative correlations (unique keywords)
print("\nTop 20 negative correlations (unique keywords):")
bot20 = kw_sig.sort_values("pearson_r", ascending=True).drop_duplicates(subset="keyword").head(20)
print(bot20[["macro", "period", "category", "keyword", "pearson_r", "p_adj_bh"]].to_string(index=False))

# Most consistent keywords — significant across all 3 periods
print("\nMost consistent keywords (significant in all 3 periods):")
periods = kw_sig["period"].unique()
for macro in kw_sig["macro"].unique():
    macro_df = kw_sig[kw_sig["macro"] == macro]
    period_sets = [set(macro_df[macro_df["period"] == p]["keyword"]) for p in periods if p in macro_df["period"].values]
    if len(period_sets) < 2:
        continue
    consistent = period_sets[0].intersection(*period_sets[1:])
    if consistent:
        consistent_df = macro_df[macro_df["keyword"].isin(consistent)].groupby(["category", "keyword"]).agg(
            avg_r=("pearson_r", "mean"),
            avg_abs_r=("abs_r", "mean"),
        ).round(4).sort_values("avg_abs_r", ascending=False).reset_index()
        print(f"\n  {macro} — {len(consistent)} keywords significant in all periods:")
        print(consistent_df.head(15)[["category", "keyword", "avg_r", "avg_abs_r"]].to_string(index=False))

# Keywords that strengthened most during 2008 vs full period
print("\nKeywords with biggest correlation shift (full period vs. 2008 window):")
for macro in kw_sig["macro"].unique():
    full = kw_df[(kw_df["macro"] == macro) & (kw_df["period"] == "2004_2025")][["keyword", "category", "pearson_r"]].rename(columns={"pearson_r": "r_full"})
    rec  = kw_df[(kw_df["macro"] == macro) & (kw_df["period"] == "2006_2011")][["keyword", "pearson_r"]].rename(columns={"pearson_r": "r_2008"})
    if full.empty or rec.empty:
        continue
    merged = full.merge(rec, on="keyword", how="inner")
    merged["abs_shift"] = (merged["r_2008"].abs() - merged["r_full"].abs()).round(4)
    merged = merged.sort_values("abs_shift", ascending=False)
    print(f"\n  {macro} — top 10 keywords that strengthened most during 2008:")
    print(merged.head(10)[["category", "keyword", "r_full", "r_2008", "abs_shift"]].to_string(index=False))

# Save top 50 unique keywords
kw_sig.sort_values("abs_r", ascending=False).drop_duplicates(subset="keyword").head(50)[["macro", "period", "category", "keyword", "pearson_r", "p_adj_bh"]].to_csv(
    os.path.join(output_dir, "summary_top50_keywords.csv"), index=False)

print("\nSaved: summary_top50_keywords.csv")