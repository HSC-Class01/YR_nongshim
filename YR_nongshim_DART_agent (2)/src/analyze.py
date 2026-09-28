from __future__ import annotations
import json
from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
df = pd.read_json(ROOT/"data/financials.json")
if df.empty:
    raise SystemExit("financials.json is empty")

def ratio(a,b):
    try:
        if pd.isna(a) or pd.isna(b) or b == 0: return None
        return float(a/b)
    except Exception: return None

# Use annual records for rolling/average balance ratios; period tables retain
# all raw values. For quarterly and half-year records, the ratio is calculated
# against the reported period amount where meaningful.
for col in ["revenue","gross_profit","operating_income","net_income","total_assets","total_liabilities","equity","cash","borrowings","interest_expense","cfo","cfi","cff","inventory","receivables"]:
    if col not in df: df[col] = np.nan

df["gross_margin"] = [ratio(a,b) for a,b in zip(df["gross_profit"],df["revenue"])]
df["operating_margin"] = [ratio(a,b) for a,b in zip(df["operating_income"],df["revenue"])]
df["net_margin"] = [ratio(a,b) for a,b in zip(df["net_income"],df["revenue"])]
df["current_ratio"] = np.nan  # current assets/liabilities need statement subtotals not always returned by API
df["debt_ratio"] = [ratio(a,b) for a,b in zip(df["total_liabilities"],df["equity"])]
df["equity_ratio"] = [ratio(a,b) for a,b in zip(df["equity"],df["total_assets"])]
df["borrowing_dependency"] = [ratio(a,b) for a,b in zip(df["borrowings"],df["total_assets"])]
df["interest_coverage"] = [ratio(a,b) for a,b in zip(df["operating_income"],df["interest_expense"])]
df["net_debt"] = df["borrowings"] - df["cash"]
df["fcf"] = df["cfo"] - (-df["cfi"])  # conservative: CFO less cash investment proxy
df["cfo_to_net_income"] = [ratio(a,b) for a,b in zip(df["cfo"],df["net_income"])]

# YoY revenue growth only when prior annual observation exists.
annual = df[df["period"]=="annual"].sort_values("year").copy()
annual["revenue_growth"] = annual["revenue"].pct_change()
for _, row in annual.iterrows():
    mask=(df["year"]==row["year"]) & (df["period"]=="annual")
    df.loc[mask,"revenue_growth"]=row["revenue_growth"]

df.to_json(ROOT/"data/analysis.json", orient="records", force_ascii=False, indent=2)
print("Ratio analysis written to data/analysis.json")
