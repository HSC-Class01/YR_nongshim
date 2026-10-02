from __future__ import annotations
import json
from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
df = pd.read_json(ROOT / "data/financials.json")
if df.empty:
    raise SystemExit("financials.json is empty")

def ratio(a, b):
    try:
        if pd.isna(a) or pd.isna(b) or float(b) == 0:
            return None
        return float(a / b)
    except Exception:
        return None

numeric = ["revenue","gross_profit","operating_income","pretax_income","net_income",
"controlling_net_income","total_assets","total_liabilities","equity","cash","borrowings",
"interest_expense","depreciation","amortization","cfo","cfi","cff","inventory","receivables","ppe"]
for c in numeric:
    if c not in df:
        df[c] = np.nan

df["gross_margin"] = [ratio(a,b) for a,b in zip(df.gross_profit, df.revenue)]
df["operating_margin"] = [ratio(a,b) for a,b in zip(df.operating_income, df.revenue)]
df["net_margin"] = [ratio(a,b) for a,b in zip(df.net_income, df.revenue)]
df["debt_ratio"] = [ratio(a,b) for a,b in zip(df.total_liabilities, df.equity)]
df["equity_ratio"] = [ratio(a,b) for a,b in zip(df.equity, df.total_assets)]
df["borrowing_dependency"] = [ratio(a,b) for a,b in zip(df.borrowings, df.total_assets)]
df["interest_coverage"] = [ratio(a,b) for a,b in zip(df.operating_income, df.interest_expense)]
df["net_debt"] = df.borrowings - df.cash
df["fcf"] = df.cfo + df.cfi
df["cfo_to_net_income"] = [ratio(a,b) for a,b in zip(df.cfo, df.net_income)]

annual = df[df.period.eq("annual") & df.status.eq("ok")].sort_values("year").copy()
annual["revenue_growth"] = annual.revenue.pct_change()
growth = annual.set_index("year")["revenue_growth"].to_dict()
df["revenue_growth"] = df.apply(lambda r: growth.get(r.year) if r.period == "annual" else None, axis=1)

df.to_json(ROOT / "data/analysis.json", orient="records", force_ascii=False, indent=2)
print("Ratio analysis written to data/analysis.json")
