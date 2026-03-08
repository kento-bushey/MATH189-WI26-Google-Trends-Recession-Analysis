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

# Most consistent keywords — significant across both recession windows
print("\nMost consistent keywords (significant in both recession windows):")
for macro in kw_sig["macro"].unique():
    macro_df = kw_sig[kw_sig["macro"] == macro]
    set_2006 = set(macro_df[macro_df["period"] == "2006_2011"]["keyword"])
    set_2018 = set(macro_df[macro_df["period"] == "2018_2023"]["keyword"])
    consistent = set_2006.intersection(set_2018)
    if consistent:
        consistent_df = macro_df[macro_df["keyword"].isin(consistent)].groupby(["category", "keyword"]).agg(
            avg_r=("pearson_r", "mean"),
            avg_abs_r=("abs_r", "mean"),
        ).round(4).sort_values("avg_abs_r", ascending=False).reset_index()
        print(f"\n  {macro} — {len(consistent)} keywords significant in both recession windows:")
        print(consistent_df.head(15)[["category", "keyword", "avg_r", "avg_abs_r"]].to_string(index=False))

# Save top 50 unique keywords
kw_sig.sort_values("abs_r", ascending=False).drop_duplicates(subset="keyword").head(50)[["macro", "period", "category", "keyword", "pearson_r", "p_adj_bh"]].to_csv(
    os.path.join(output_dir, "summary_top50_keywords.csv"), index=False)

print("\nSaved: summary_top50_keywords.csv")