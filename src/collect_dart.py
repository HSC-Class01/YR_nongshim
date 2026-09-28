"""
OpenDART collector for Nongshim.
- Annual: 11011
- Half-year: 11012
- Q1: 11013
- Q3: 11014
- API key is read from DART_API_KEY environment variable.
"""
from __future__ import annotations
import json, os, time
from pathlib import Path
import requests
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CFG = json.loads((ROOT/"config/config.json").read_text(encoding="utf-8"))
OUT = ROOT/"data"
RAW = ROOT/"raw"
OUT.mkdir(exist_ok=True)
RAW.mkdir(exist_ok=True)

API_KEY = os.getenv("DART_API_KEY", "").strip()
BASE = "https://opendart.fss.or.kr/api/fnlttSinglAcntAll.json"

# Main account aliases. The extractor uses account_nm + sj_nm rather than
# fragile row numbers so the code survives changes in ordering.
ALIASES = {
    "total_assets": ["자산총계"],
    "cash": ["현금및현금성자산", "현금및현금성자산 및 단기금융상품"],
    "receivables": ["매출채권", "매출채권및기타채권"],
    "inventory": ["재고자산"],
    "ppe": ["유형자산"],
    "total_liabilities": ["부채총계"],
    "borrowings": ["단기차입금", "장기차입금", "유동성장기차입금", "사채"],
    "equity": ["자본총계"],
    "revenue": ["매출액", "수익(매출액)"],
    "gross_profit": ["매출총이익"],
    "operating_income": ["영업이익", "영업이익(손실)"],
    "pretax_income": ["법인세비용차감전순이익", "법인세비용차감전계속사업이익"],
    "net_income": ["당기순이익", "당기순이익(손실)"],
    "controlling_net_income": ["지배기업의 소유주에게 귀속되는 당기순이익", "지배기업 소유주지분 순이익"],
    "interest_expense": ["이자비용", "금융비용"],
    "depreciation": ["감가상각비"],
    "amortization": ["무형자산상각비"],
    "cfo": ["영업활동으로 인한 현금흐름", "영업활동현금흐름"],
    "cfi": ["투자활동으로 인한 현금흐름", "투자활동현금흐름"],
    "cff": ["재무활동으로 인한 현금흐름", "재무활동현금흐름"],
}

def num(v):
    if v is None or str(v).strip() in ("", "-"): return None
    s = str(v).replace(",", "").replace(" ", "")
    try: return float(s)
    except Exception: return None

def first_match(df, aliases, sj=None):
    if df.empty: return None
    d = df.copy()
    if sj:
        x = d[d["sj_nm"].astype(str).eq(sj)]
        if not x.empty: d = x
    for alias in aliases:
        x = d[d["account_nm"].astype(str).str.strip().eq(alias)]
        if not x.empty:
            # Prefer current-period consolidated row when possible.
            row = x.iloc[0]
            for col in ["thstrm_amount","thstrm_add_amount","frmtrm_amount","bfefrmtrm_amount"]:
                if col in x.columns and pd.notna(row.get(col)):
                    return num(row.get(col))
    return None

def fetch(year, code):
    if year < 2015:
        return {
            "status": "legacy_not_available_via_current_fnltt_api",
            "year": year, "report_code": code,
            "message": "OpenDART 정기보고서 재무 API의 공식 제공 범위는 2015년 이후입니다. 2010~2014는 원문/XBRL legacy 보정 수집 대상으로 표시합니다."
        }
    if not API_KEY:
        raise RuntimeError("DART_API_KEY 환경변수가 없습니다. GitHub Actions Secret에 DART_API_KEY를 등록하세요.")
    params = {
        "crtfc_key": API_KEY,
        "corp_code": CFG["company"]["corp_code"],
        "bsns_year": str(year),
        "reprt_code": code,
        "fs_div": "CFS"
    }
    r = requests.get(BASE, params=params, timeout=60)
    r.raise_for_status()
    data = r.json()
    if data.get("status") != "000":
        return {"status":"api_error","year":year,"report_code":code,
                "message":data.get("message"),"raw_status":data.get("status")}
    rows = data.get("list", [])
    df = pd.DataFrame(rows)
    if df.empty:
        return {"status":"no_data","year":year,"report_code":code}
    for c in ["sj_nm","account_nm","thstrm_amount","thstrm_add_amount","frmtrm_amount","bfefrmtrm_amount"]:
        if c not in df.columns: df[c] = None

    out = {"status":"ok","year":year,"report_code":code,"fs_div":"CFS"}
    for key, aliases in ALIASES.items():
        if key == "borrowings":
            vals = []
            for a in aliases:
                v = first_match(df,[a])
                if v is not None: vals.append(v)
            out[key] = sum(vals) if vals else None
        else:
            out[key] = first_match(df, aliases)
    # Store compact source rows for auditability.
    audit = df[["sj_nm","account_nm","thstrm_amount","thstrm_add_amount","frmtrm_amount","bfefrmtrm_amount"]].to_dict("records")
    out["source_rows"] = audit
    return out

def main():
    start = int(os.getenv("START_YEAR", CFG["collection"]["start_year"]))
    end = int(os.getenv("END_YEAR", pd.Timestamp.now().year))
    codes = CFG["collection"]["report_codes"]
    all_rows = []
    for year in range(start, end+1):
        for period, code in codes.items():
            # Q1/Q3 labels are normalized to quarterly in dashboard.
            period_norm = "annual" if period=="annual" else "half_year" if period=="half_year" else "quarterly"
            try:
                rec = fetch(year, code)
            except Exception as e:
                rec = {"status":"exception","year":year,"report_code":code,"message":str(e)}
            rec["period"] = period_norm
            rec["period_detail"] = period
            all_rows.append(rec)
            time.sleep(0.15)
    # Keep audit/source rows out of the main dashboard JSON.
    public_rows = []
    for r in all_rows:
        x = {k:v for k,v in r.items() if k != "source_rows"}
        public_rows.append(x)
    (OUT/"financials.json").write_text(json.dumps(public_rows, ensure_ascii=False, indent=2), encoding="utf-8")
    # Also save a flat CSV for analysis.
    flat = pd.DataFrame(public_rows)
    flat.to_csv(OUT/"financials.csv", index=False, encoding="utf-8-sig")
    meta = {
        "company": CFG["company"],
        "updated_at": pd.Timestamp.now(tz="Asia/Seoul").isoformat(),
        "start_year": start,
        "end_year": end,
        "api_source": "OpenDART fnlttSinglAcntAll",
        "legacy_note": CFG["collection"]["api_note"]
    }
    (OUT/"metadata.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Collected {len(all_rows)} report-period records.")

if __name__ == "__main__":
    main()
