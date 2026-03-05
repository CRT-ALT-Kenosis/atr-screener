import streamlit as st
import yfinance as yf
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ATR Screener",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
#  DESIGN SYSTEM — refined institutional terminal
#  Deep slate · warm amber accents · Geist Mono + DM Sans
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Geist+Mono:wght@300;400;500;600;700&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
  --bg0:   #080a0c;
  --bg1:   #0e1114;
  --bg2:   #141820;
  --bg3:   #1c2130;
  --line:  #232a38;
  --line2: #2d3748;
  --dim:   #3d4f6b;
  --muted: #607080;
  --body:  #94a3b8;
  --text:  #cbd5e1;
  --bright:#e2e8f0;
  --amber: #f59e0b;
  --amb2:  #fbbf24;
  --teal:  #2dd4bf;
  --green: #34d399;
  --red:   #f87171;
  --blue:  #60a5fa;
  --r:     6px;
}

*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"], .stApp {
  background: var(--bg0) !important;
  color: var(--text) !important;
  font-family: 'DM Sans', sans-serif !important;
}

[data-testid="stSidebar"] {
  background: var(--bg1) !important;
  border-right: 1px solid var(--line) !important;
}
[data-testid="stSidebar"] > div { padding: 1.2rem 1rem !important; }
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label { color: var(--body) !important; }

.main .block-container {
  padding: 1.5rem 2rem 3rem !important;
  max-width: 1400px !important;
}

.sec-label {
  font-family: 'Geist Mono', monospace;
  font-size: 0.6rem; font-weight: 600;
  letter-spacing: 0.14em; color: var(--dim);
  text-transform: uppercase; margin: 1.4rem 0 0.5rem; display: block;
}

.page-header { padding-bottom: 1rem; border-bottom: 1px solid var(--line); margin-bottom: 1.4rem; }
.page-title {
  font-family: 'Geist Mono', monospace;
  font-size: clamp(1.3rem, 2.5vw, 1.9rem); font-weight: 700;
  color: var(--bright); letter-spacing: -0.02em; line-height: 1; margin: 0;
}
.page-title span { color: var(--amber); }
.page-sub {
  font-family: 'Geist Mono', monospace; font-size: 0.65rem;
  color: var(--dim); letter-spacing: 0.1em; margin-top: 0.4rem;
}

/* ── Phase banner ── */
.phase-banner {
  display: flex; align-items: center; gap: 0.75rem;
  background: var(--bg2); border: 1px solid var(--line2);
  border-radius: var(--r); padding: 0.65rem 1rem; margin-bottom: 0.75rem;
}
.phase-num {
  font-family: 'Geist Mono', monospace; font-size: 0.65rem; font-weight: 700;
  color: var(--bg0); background: var(--amber); border-radius: 3px;
  padding: 0.1rem 0.45rem; flex-shrink: 0; letter-spacing: 0.06em;
}
.phase-num.done { background: var(--green); }
.phase-num.active { background: var(--amber); }
.phase-label {
  font-family: 'Geist Mono', monospace; font-size: 0.72rem; color: var(--body);
}
.phase-label b { color: var(--bright); }
.phase-detail { font-family: 'Geist Mono', monospace; font-size: 0.65rem; color: var(--muted); margin-left: auto; }

.status-row {
  display: flex; flex-wrap: wrap; align-items: center;
  gap: 0.5rem 1.5rem; background: var(--bg1);
  border: 1px solid var(--line); border-radius: var(--r);
  padding: 0.5rem 1rem; margin-bottom: 1.2rem;
}
.status-kv {
  font-family: 'Geist Mono', monospace; font-size: 0.68rem;
  color: var(--muted); display: flex; align-items: center; gap: 0.4rem;
}
.status-kv b { color: var(--text); font-weight: 500; }
.pulse {
  width: 5px; height: 5px; border-radius: 50%;
  background: var(--green); box-shadow: 0 0 6px var(--green); flex-shrink: 0;
}

.metric-row {
  display: grid; grid-template-columns: repeat(4, 1fr);
  gap: 10px; margin-bottom: 1.4rem;
}
@media (max-width: 700px) { .metric-row { grid-template-columns: 1fr 1fr; } }

.metric-box { background: var(--bg1); border: 1px solid var(--line); border-radius: var(--r); padding: 0.9rem 1rem; }
.metric-box.hi { border-color: rgba(245,158,11,0.3); }
.metric-label { font-family: 'Geist Mono', monospace; font-size: 0.6rem; color: var(--dim); letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 0.4rem; }
.metric-value { font-family: 'Geist Mono', monospace; font-size: 1.7rem; font-weight: 700; color: var(--bright); line-height: 1; }
.metric-value.amber { color: var(--amber); }
.metric-sub { font-size: 0.65rem; color: var(--muted); margin-top: 0.25rem; }

.card { background: var(--bg1); border: 1px solid var(--line); border-radius: var(--r); padding: 1rem 1rem 0.85rem; position: relative; }
.card:hover { border-color: var(--line2); background: var(--bg2); }

.atr-badge {
  position: absolute; top: 0.85rem; right: 0.85rem;
  font-family: 'Geist Mono', monospace; font-size: 0.72rem; font-weight: 700;
  padding: 0.18rem 0.55rem; border-radius: 20px; line-height: 1.4;
}
.atr-norm    { background:rgba(45,212,191,.1);  color:var(--teal);  border:1px solid rgba(45,212,191,.25); }
.atr-high    { background:rgba(245,158,11,.1);  color:var(--amber); border:1px solid rgba(245,158,11,.3); }
.atr-extreme { background:rgba(248,113,113,.1); color:var(--red);   border:1px solid rgba(248,113,113,.3); }

.card-ticker { font-family: 'Geist Mono', monospace; font-size: 1.2rem; font-weight: 700; color: var(--bright); letter-spacing: 0.04em; }
.card-price  { font-family: 'Geist Mono', monospace; font-size: 1rem; color: var(--text); font-weight: 500; margin-top: 0.4rem; }
.card-divider { height: 1px; background: var(--line); margin: 0.6rem 0; }

.card-stats { display: grid; grid-template-columns: 1fr 1fr; gap: 0.45rem 0.6rem; }
.stat-k { font-family: 'Geist Mono', monospace; font-size: 0.57rem; color: var(--dim); letter-spacing: 0.1em; text-transform: uppercase; display: block; margin-bottom: 1px; }
.stat-v { font-family: 'Geist Mono', monospace; font-size: 0.8rem; font-weight: 500; color: var(--text); }
.stat-v.pos { color: var(--green); }
.stat-v.neg { color: var(--red); }

/* TV vs confirmed ATR comparison */
.atr-compare {
  display: flex; align-items: center; gap: 0.4rem;
  margin-top: 0.5rem; padding-top: 0.5rem;
  border-top: 1px solid var(--line);
}
.atr-compare-item { font-family: 'Geist Mono', monospace; font-size: 0.62rem; }
.atr-compare-label { color: var(--dim); display: block; font-size: 0.55rem; }
.atr-compare-val   { color: var(--text); font-weight: 500; }
.atr-compare-sep   { color: var(--line2); font-size: 0.7rem; }

.card-tags { margin-top: 0.65rem; display: flex; gap: 0.35rem; flex-wrap: wrap; }
.tag { font-family: 'Geist Mono', monospace; font-size: 0.57rem; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; padding: 0.12rem 0.45rem; border-radius: 3px; }
.tag-etf   { background:rgba(52,211,153,.08);  color:var(--green); border:1px solid rgba(52,211,153,.2); }
.tag-stock { background:rgba(96,165,250,.08);  color:var(--blue);  border:1px solid rgba(96,165,250,.2); }
.tag-exch  { background:rgba(100,116,139,.08); color:var(--muted); border:1px solid var(--line); }
.tag-day1  { background:rgba(248,113,113,.12); color:var(--red);   border:1px solid rgba(248,113,113,.3); }
.tag-streak{ background:rgba(245,158,11,.10);  color:var(--amber); border:1px solid rgba(245,158,11,.25); }
.tag-rvol  { background:rgba(96,165,250,.10);  color:var(--blue);  border:1px solid rgba(96,165,250,.25); }

/* Qullamaggie signal row */
.signal-row {
  display:grid; grid-template-columns:repeat(3,1fr); gap:0.35rem;
  margin-top:0.55rem; padding-top:0.55rem; border-top:1px solid var(--line);
}
.sig-cell { text-align:center; }
.sig-label { font-family:'Geist Mono',monospace; font-size:0.52rem; color:var(--dim);
             letter-spacing:0.08em; text-transform:uppercase; display:block; }
.sig-val   { font-family:'Geist Mono',monospace; font-size:0.78rem; font-weight:600; color:var(--text); }
.sig-val.pos { color:var(--green); }
.sig-val.neg { color:var(--red); }
.sig-val.warn{ color:var(--amber); }

.empty-state { text-align: center; padding: 4rem 1rem; font-family: 'Geist Mono', monospace; color: var(--dim); }
.empty-icon  { font-size: 2.4rem; margin-bottom: 0.8rem; opacity: .35; }
.empty-text  { font-size: 0.85rem; }
.empty-hint  { font-size: 0.7rem; margin-top: 0.35rem; color: var(--line2); }

.stButton > button {
  font-family: 'Geist Mono', monospace !important; font-size: 0.78rem !important;
  font-weight: 600 !important; letter-spacing: 0.08em !important;
  background: var(--amber) !important; color: var(--bg0) !important;
  border: none !important; border-radius: 5px !important; padding: 0.5rem 1.3rem !important;
}
.stButton > button:hover { opacity: 0.86 !important; }

[data-testid="stDownloadButton"] > button {
  background: transparent !important; color: var(--muted) !important;
  border: 1px solid var(--line2) !important;
  font-family: 'Geist Mono', monospace !important; font-size: 0.72rem !important;
}

label[data-testid="stWidgetLabel"] p {
  font-family: 'Geist Mono', monospace !important; font-size: 0.67rem !important;
  font-weight: 500 !important; color: var(--muted) !important;
  letter-spacing: 0.1em !important; text-transform: uppercase !important;
}
[data-baseweb="input"] input { background: var(--bg2) !important; border-color: var(--line2) !important; color: var(--text) !important; font-family: 'Geist Mono', monospace !important; font-size: 0.88rem !important; }
[data-baseweb="select"] > div { background: var(--bg2) !important; border-color: var(--line2) !important; }
[data-baseweb="tag"] { background: var(--bg3) !important; border: 1px solid var(--line2) !important; }
[data-baseweb="tag"] span { color: var(--body) !important; font-family: 'Geist Mono', monospace !important; font-size: 0.68rem !important; }

[data-testid="stProgressBar"] > div { background: var(--line) !important; border-radius: 2px; }
[data-testid="stProgressBar"] > div > div { background: linear-gradient(90deg,var(--amber),var(--amb2)) !important; }

[data-testid="stExpander"] { background: var(--bg1) !important; border: 1px solid var(--line) !important; border-radius: var(--r) !important; }
[data-testid="stExpander"] summary { font-family: 'Geist Mono', monospace !important; font-size: 0.72rem !important; color: var(--muted) !important; }

.stRadio label { font-family: 'DM Sans', sans-serif !important; font-size: 0.82rem !important; }
hr { border-color: var(--line) !important; margin: 0.6rem 0 !important; }
#MainMenu, footer, [data-testid="stDecoration"] { display: none !important; }
header[data-testid="stHeader"] { background: transparent !important; }
::-webkit-scrollbar { width: 3px; height: 3px; }
::-webkit-scrollbar-track { background: var(--bg0); }
::-webkit-scrollbar-thumb { background: var(--line2); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  SCAN ENGINE — TWO-PHASE
# ─────────────────────────────────────────────────────────────────────────────

# TradingView exchange name mapping
TV_EXCHANGE_MAP = {
    "NASDAQ":        "NASDAQ",
    "NYSE":          "NYSE",
    "NYSE Arca":     "AMEX",   # TV calls NYSE Arca "AMEX"
    "NYSE American": "AMEX",
    "BATS":          "BATS",
    "IEX":           None,     # not in TV screener
}


# Market cap tier definitions (USD)
MCAP_TIERS = {
    "All":        (0,             None),
    "Micro":      (0,             300_000_000),
    "Small":      (300_000_000,   2_000_000_000),
    "Mid":        (2_000_000_000, 10_000_000_000),
    "Large":      (10_000_000_000,200_000_000_000),
    "Mega":       (200_000_000_000, None),
}

def phase1_tradingview(min_price: float, min_vol: int, prescreen_mult: float,
                       asset_filter: str, exchange_filter: list,
                       mcap_tiers: list | None = None) -> tuple[list, str | None]:
    """
    Phase 1 — TradingView scanner API.
    Single fast call covering all US exchanges. Returns candidate dicts.
    Uses an 80% pre-screen threshold to avoid missing boundary cases.
    """
    try:
        from tradingview_screener import Query, Column
    except ImportError:
        return [], "tradingview-screener not installed"

    # Map exchange selections to TV names (deduplicated, None filtered)
    tv_exchanges = list({TV_EXCHANGE_MAP[e] for e in exchange_filter
                         if e in TV_EXCHANGE_MAP and TV_EXCHANGE_MAP[e]})

    try:
        q = (
            Query()
            .set_markets("america")
            .select("name", "close", "SMA50", "ATR", "volume", "type", "exchange",
                     "Perf.5D", "Perf.1M", "relative_volume_10d_calc", "change", "gap")
            .where(
                Column("close") > min_price,
                Column("volume") > min_vol,
                Column("close") > Column("SMA50"),  # must be above SMA to have positive multiple
            )
            .order_by("volume", ascending=False)
            .limit(2000)
        )

        if asset_filter == "ETFs Only":
            q = q.where(Column("type").isin(["fund", "etf"]))
        elif asset_filter == "Stocks Only":
            q = q.where(Column("type") == "stock")

        if tv_exchanges:
            q = q.where(Column("exchange").isin(tv_exchanges))

        # Market cap tier filter — apply each selected tier as an OR block
        if mcap_tiers and "All" not in mcap_tiers:
            from tradingview_screener import Or
            cap_conditions = []
            for tier in mcap_tiers:
                lo, hi = MCAP_TIERS.get(tier, (0, None))
                if lo and hi:
                    cap_conditions.append(
                        (Column("market_cap_basic") >= lo) & (Column("market_cap_basic") < hi)
                    )
                elif lo:
                    cap_conditions.append(Column("market_cap_basic") >= lo)
                elif hi:
                    cap_conditions.append(Column("market_cap_basic") < hi)
            if cap_conditions:
                combined = cap_conditions[0]
                for c in cap_conditions[1:]:
                    combined = combined | c
                q = q.where(combined)

        _, df = q.get_scanner_data()

    except Exception as e:
        return [], f"TradingView API error: {e}"

    if df is None or df.empty:
        return [], None

    df = df.dropna(subset=["close", "SMA50", "ATR"])
    df = df[df["ATR"] > 0]
    # Fill optional fields with safe defaults
    for col in ["Perf.5D", "Perf.1M", "relative_volume_10d_calc", "change", "gap"]:
        if col not in df.columns:
            df[col] = 0.0
    df = df.fillna({"Perf.5D": 0.0, "Perf.1M": 0.0,
                    "relative_volume_10d_calc": 1.0, "change": 0.0, "gap": 0.0})

    # Compute rough ATR multiple using the correct jfsrev/fred6724 formula:
    #   A = ATR% = ATR / Close
    #   B = % gain from SMA50 = (Close - SMA50) / SMA50
    #   Multiple = B / A
    df["tv_atr_mult"] = ((df["close"] - df["SMA50"]) / df["SMA50"]) / (df["ATR"] / df["close"])

    # Pre-filter at 80% of threshold — catches exact-boundary cases
    df = df[df["tv_atr_mult"] >= prescreen_mult]

    if df.empty:
        return [], None

    df["is_etf"] = df["type"].isin(["fund", "etf", "dr"])

    return (
        df[["name", "close", "SMA50", "ATR", "tv_atr_mult", "exchange", "is_etf",
            "Perf.5D", "Perf.1M", "relative_volume_10d_calc", "change", "gap"]]
        .rename(columns={"name": "ticker", "close": "tv_close",
                         "SMA50": "tv_sma50", "ATR": "tv_atr",
                         "Perf.5D": "gain_5d", "Perf.1M": "gain_1m",
                         "relative_volume_10d_calc": "rel_vol",
                         "change": "tv_day_chg", "gap": "tv_gap"})
        .to_dict("records"),
        None,
    )


def wilder_atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    tr = pd.concat([
        high - low,
        (high - close.shift()).abs(),
        (low  - close.shift()).abs(),
    ], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()


def phase2_confirm(candidate: dict, sma_period: int, atr_period: int,
                   min_price: float, min_vol: int, min_atr_mult: float) -> dict | None:
    """
    Phase 2 — enrich TV candidates with yfinance volume + day change only.

    The ATR multiple is computed entirely from TV ground-truth values
    (tv_close, tv_sma50, tv_atr) which already match the chart exactly.
    yfinance is only used for avg_vol and day_chg — fields TV doesn't expose
    in the screener API. If yfinance data is unusable we fall back to TV values.
    """
    ticker   = candidate["ticker"]
    tv_close = float(candidate.get("tv_close") or 0)
    tv_sma50 = float(candidate.get("tv_sma50") or 0)
    tv_atr   = float(candidate.get("tv_atr")   or 0)

    # Guard: need valid TV values to compute the multiple
    if tv_close <= 0 or tv_sma50 <= 0 or tv_atr <= 0:
        return None
    if tv_close < min_price:
        return None

    # ── Correct formula: jfsrev/fred6724 script ──────────────────────────────
    #   A = ATR%           = TV_ATR / TV_Close
    #   B = % gain from SMA = (TV_Close - TV_SMA50) / TV_SMA50
    #   Multiple = B / A
    atr_pct  = tv_atr / tv_close                         # A
    pct_sma  = (tv_close - tv_sma50) / tv_sma50          # B (decimal)

    if atr_pct == 0:
        return None

    atr_mult = pct_sma / atr_pct                         # B / A

    if atr_mult < min_atr_mult:
        return None

    # ── yfinance: avg volume + day change + consecutive green days ───────────
    avg_vol     = None
    day_chg     = None
    consec_days = 0   # consecutive green closes

    try:
        df = yf.download(ticker, period="3mo", interval="1d",
                         progress=False, auto_adjust=False)
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            close_col = "Close" if "Close" in df.columns else "Adj Close"
            if close_col in df.columns and "Volume" in df.columns:
                closes  = df[close_col].squeeze().dropna()
                volumes = df["Volume"].squeeze()
                if len(closes) >= 2:
                    prev    = float(closes.iloc[-2])
                    last_yf = float(closes.iloc[-1])
                    if prev > 0:
                        day_chg = round((last_yf - prev) / prev * 100, 2)
                if len(volumes) >= 5:
                    avg_vol = float(volumes.tail(20).mean())
                # Consecutive green days (close > prior close)
                if len(closes) >= 2:
                    for i in range(len(closes) - 1, 0, -1):
                        if float(closes.iloc[i]) > float(closes.iloc[i - 1]):
                            consec_days += 1
                        else:
                            break
    except Exception:
        pass

    # Fallback values if yfinance failed
    if avg_vol is None or avg_vol < min_vol:
        avg_vol_display = "N/A"
    else:
        if avg_vol >= 1_000_000:
            avg_vol_display = f"{avg_vol/1_000_000:.1f}M"
        elif avg_vol >= 1_000:
            avg_vol_display = f"{avg_vol/1_000:.0f}K"
        else:
            avg_vol_display = str(int(avg_vol))

    if day_chg is None:
        day_chg = candidate.get("tv_day_chg", 0.0)

    return {
        "ticker":      ticker,
        "price":       round(tv_close, 2),
        "atr_mult":    round(atr_mult, 2),
        "tv_atr_mult": round(candidate["tv_atr_mult"], 2),
        "sma":         round(tv_sma50, 2),
        "atr":         round(tv_atr, 2),
        "atr_pct":     round(atr_pct * 100, 2),
        "pct_sma":     round(pct_sma * 100, 1),
        "day_chg":     day_chg,
        "avg_vol":     avg_vol_display,
        "is_etf":      candidate["is_etf"],
        "exchange":    candidate["exchange"],
        # Qullamaggie parabolic short signal fields
        "consec_days": consec_days,
        "gain_5d":     round(float(candidate.get("gain_5d") or 0), 1),
        "gain_1m":     round(float(candidate.get("gain_1m") or 0), 1),
        "rel_vol":     round(float(candidate.get("rel_vol") or 1.0), 2),
        "tv_gap":      round(float(candidate.get("tv_gap")  or 0), 2),
        "is_day1":     consec_days <= 1,   # Qullamaggie: never short day 1
    }
def run_two_phase_scan(min_price, min_atr_mult, sma_period, atr_period,
                       asset_filter, exchange_filter, workers, min_vol,
                       mcap_tiers, min_consec_days, min_gain_5d, min_rel_vol,
                       hide_day1, phase1_status_cb, phase2_progress_cb):
    """
    Full two-phase scan.
    phase1_status_cb(msg, n_candidates) — called once after Phase 1 completes.
    phase2_progress_cb(pct, done, total) — called after each Phase 2 ticker.
    """
    # ── Phase 1 ──────────────────────────────────────────────────────────────
    prescreen_mult = min_atr_mult * 0.80   # 20% buffer for boundary cases
    candidates, err = phase1_tradingview(
        min_price, min_vol, prescreen_mult, asset_filter, exchange_filter, mcap_tiers
    )

    if err:
        phase1_status_cb(f"Phase 1 warning: {err}", 0)
        candidates = []

    phase1_status_cb(None, len(candidates))

    if not candidates:
        return []

    # ── Phase 2 ──────────────────────────────────────────────────────────────
    total, done, results = len(candidates), 0, []

    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {
            ex.submit(phase2_confirm, c, sma_period, atr_period,
                      min_price, min_vol, min_atr_mult): c
            for c in candidates
        }
        for fut in as_completed(futs):
            done += 1
            phase2_progress_cb(done / total, done, total)
            res = fut.result()
            if res:
                results.append(res)

    # ── Post-scan Qullamaggie filters ─────────────────────────────────────────
    if hide_day1:
        results = [r for r in results if not r["is_day1"]]
    if min_consec_days > 0:
        results = [r for r in results if r["consec_days"] >= min_consec_days]
    if min_gain_5d > 0:
        results = [r for r in results if r["gain_5d"] >= min_gain_5d]
    if min_rel_vol > 0:
        results = [r for r in results if r["rel_vol"] >= min_rel_vol]

    return sorted(results, key=lambda x: x["atr_mult"], reverse=True)


# ─────────────────────────────────────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <p style="font-family:'Geist Mono',monospace;font-size:1rem;font-weight:700;
    color:#e2e8f0;letter-spacing:-0.01em;margin:0 0 0.15rem">◈ ATR Screener</p>
    <p style="font-family:'Geist Mono',monospace;font-size:0.58rem;color:#3d4f6b;
    letter-spacing:0.13em;margin:0 0 0.8rem">TWO-PHASE · TV + YFINANCE</p>
    """, unsafe_allow_html=True)

    st.markdown('<span class="sec-label">Thresholds</span>', unsafe_allow_html=True)
    min_price    = st.number_input("Min Price ($)",        value=100.0, step=10.0, min_value=0.0)
    min_atr_mult = st.number_input("Min ATR Multiple (×)", value=10.0,  step=0.5,  min_value=0.5)

    st.markdown('<span class="sec-label">Indicators</span>', unsafe_allow_html=True)
    sma_period = st.number_input("SMA Period", value=50, step=5,  min_value=5,  max_value=200)
    atr_period = st.number_input("ATR Period", value=14, step=1,  min_value=5,  max_value=50)

    st.markdown('<span class="sec-label">Universe</span>', unsafe_allow_html=True)
    asset_filter = st.radio(
        "Asset Type",
        ["Stocks + ETFs", "ETFs Only", "Stocks Only"],
        index=0, label_visibility="collapsed",
    )
    exchange_opts   = ["NASDAQ", "NYSE", "NYSE Arca", "NYSE American", "BATS", "IEX"]
    exchange_filter = st.multiselect(
        "Exchanges", exchange_opts, default=exchange_opts,
        label_visibility="collapsed",
    )
    st.markdown("""
    <p style='font-family:"Geist Mono",monospace;font-size:0.6rem;font-weight:600;
    letter-spacing:0.14em;color:#3d4f6b;text-transform:uppercase;
    margin:0.9rem 0 0.3rem;display:block'>Market Cap</p>
    <p style='font-family:"Geist Mono",monospace;font-size:0.6rem;color:#3d4f6b;
    margin:0 0 0.4rem'>
    Micro &lt;$300M &nbsp;·&nbsp; Small $300M–$2B<br>
    Mid $2B–$10B &nbsp;·&nbsp; Large $10B–$200B<br>
    Mega &gt;$200B
    </p>
    """, unsafe_allow_html=True)
    mcap_tiers = st.multiselect(
        "Market Cap Tiers",
        ["All", "Micro", "Small", "Mid", "Large", "Mega"],
        default=["All"],
        label_visibility="collapsed",
    )
    # If "All" is selected alongside others, treat as All
    if "All" in mcap_tiers or not mcap_tiers:
        mcap_tiers = ["All"]

    min_vol = st.number_input(
        "Min Avg Volume", value=500_000, step=100_000, min_value=0,
        help="Filters warrants, ghost tickers, and illiquid symbols",
    )

    st.markdown('<span class="sec-label">Qullamaggie Filters</span>', unsafe_allow_html=True)
    hide_day1 = st.toggle(
        "Hide Day 1 setups",
        value=True,
        help="Qullamaggie never shorts day 1 — too erratic. Hides stocks where streak = 1.",
    )
    min_consec_days = st.slider(
        "Min consecutive green days", 0, 7, 3,
        help="Qullamaggie requires 3–5+ days up in a row before considering a short.",
        label_visibility="visible",
    )
    min_gain_5d = st.number_input(
        "Min 5-day gain (%)", value=0.0, step=5.0, min_value=0.0,
        help="Large caps need 50–100%+ in days/weeks. Small caps 300–1000%+.",
    )
    min_rel_vol = st.number_input(
        "Min Relative Volume", value=1.0, step=0.5, min_value=0.0,
        help="High rel vol (1.5–3×+) confirms the parabolic is real, not drift.",
    )

    st.markdown('<span class="sec-label">Performance</span>', unsafe_allow_html=True)
    workers = st.slider("Workers", 1, 15, 6, label_visibility="collapsed")
    st.markdown(
        f"<p style='font-family:\"Geist Mono\",monospace;font-size:0.63rem;"
        f"color:#3d4f6b'>{workers} parallel workers (Phase 2 only)</p>",
        unsafe_allow_html=True,
    )

    st.markdown('<span class="sec-label">How it works</span>', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-family:'Geist Mono',monospace;font-size:0.63rem;
    color:#3d4f6b;line-height:2;border:1px solid #232a38;border-radius:5px;
    padding:0.55rem 0.8rem;background:#0e1114">
    <span style="color:#f59e0b">Phase 1</span> TradingView API<br>
    <span style="color:#607080">→ ~2 sec, all US exchanges</span><br>
    <span style="color:#607080">→ rough ATR× pre-screen</span><br><br>
    <span style="color:#f59e0b">Phase 2</span> yfinance confirm<br>
    <span style="color:#607080">→ Wilder exact ATR</span><br>
    <span style="color:#607080">→ survivors only (~20-100)</span><br><br>
    <span style="color:#2dd4bf">7×</span>  profit-taking zone<br>
    <span style="color:#f59e0b">10×</span> extreme extension<br>
    <span style="color:#f87171">15×</span> blow-off / climax
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
  <div class="page-title">ATR <span>Extension</span> Screener</div>
  <div class="page-sub">PARABOLIC MOVES  ·  ALL US EXCHANGES  ·  TV PRE-SCREEN + WILDER CONFIRM</div>
</div>
""", unsafe_allow_html=True)

btn_col, dl_col, _ = st.columns([1, 1, 7])
run_btn = btn_col.button("▶  RUN SCAN")

st.markdown(f"""
<div class="status-row">
  <span class="status-kv"><span class="pulse"></span>READY</span>
  <span class="status-kv">PHASE 1 <b>TradingView API</b></span>
  <span class="status-kv">PHASE 2 <b>yfinance Wilder ATR</b></span>
  <span class="status-kv">AS OF <b>{datetime.now().strftime('%H:%M')}</b></span>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  SCAN
# ─────────────────────────────────────────────────────────────────────────────
if run_btn:
    # Phase 1 indicators
    ph1_banner = st.empty()
    ph1_banner.markdown("""
    <div class="phase-banner">
      <span class="phase-num active">P1</span>
      <span class="phase-label">Querying <b>TradingView</b> — all US exchanges…</span>
    </div>
    """, unsafe_allow_html=True)

    ph2_banner  = st.empty()
    ph2_prog    = st.empty()
    ph2_info    = st.empty()

    p1_candidates = [0]
    p1_warning    = [None]

    def phase1_cb(warning, n):
        p1_warning[0]    = warning
        p1_candidates[0] = n
        status = f"found <b>{n}</b> candidates" if n else "no candidates above pre-screen threshold"
        ph1_banner.markdown(f"""
        <div class="phase-banner">
          <span class="phase-num done">P1</span>
          <span class="phase-label">TradingView pre-screen complete</span>
          <span class="phase-detail">{status}</span>
        </div>
        """, unsafe_allow_html=True)

    def phase2_cb(pct, done, total):
        ph2_banner.markdown(f"""
        <div class="phase-banner">
          <span class="phase-num active">P2</span>
          <span class="phase-label">yfinance Wilder ATR confirmation</span>
          <span class="phase-detail">{done} / {total}</span>
        </div>
        """, unsafe_allow_html=True)
        ph2_prog.progress(min(pct, 1.0))
        ph2_info.markdown(
            f"<span style='font-family:\"Geist Mono\",monospace;font-size:0.7rem;"
            f"color:#607080'>Validating {done:,} / {total:,} candidates…</span>",
            unsafe_allow_html=True,
        )

    results = run_two_phase_scan(
        min_price, min_atr_mult,
        int(sma_period), int(atr_period),
        asset_filter, exchange_filter,
        workers, int(min_vol),
        mcap_tiers,
        int(min_consec_days), float(min_gain_5d), float(min_rel_vol),
        hide_day1,
        phase1_cb, phase2_cb,
    )

    # Clean up progress elements
    ph2_prog.empty()
    ph2_info.empty()

    # Mark phase 2 done
    ph2_banner.markdown(f"""
    <div class="phase-banner">
      <span class="phase-num done">P2</span>
      <span class="phase-label">yfinance confirmation complete</span>
      <span class="phase-detail"><b>{len(results)}</b> confirmed hits</span>
    </div>
    """, unsafe_allow_html=True)

    if p1_warning[0]:
        st.warning(p1_warning[0])

    st.session_state["results"]   = results
    st.session_state["scan_ts"]   = datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
    st.session_state["sma_label"] = int(sma_period)
    st.session_state["atr_label"] = int(atr_period)
    st.session_state["p1_count"]  = p1_candidates[0]


# ─────────────────────────────────────────────────────────────────────────────
#  RESULTS
# ─────────────────────────────────────────────────────────────────────────────
if "results" in st.session_state:
    results  = st.session_state["results"]
    scan_ts  = st.session_state.get("scan_ts", "")
    sma_lbl  = st.session_state.get("sma_label", 50)
    atr_lbl  = st.session_state.get("atr_label", 14)
    p1_count = st.session_state.get("p1_count", "—")

    n_hits    = len(results)
    top_mult  = f"{results[0]['atr_mult']}×" if results else "—"
    n_etf_hit = sum(1 for r in results if r["is_etf"])
    n_stk_hit = n_hits - n_etf_hit

    # Summary metrics
    st.markdown(f"""
    <div class="metric-row">
      <div class="metric-box hi">
        <div class="metric-label">Confirmed Hits</div>
        <div class="metric-value amber">{n_hits}</div>
        <div class="metric-sub">{scan_ts}</div>
      </div>
      <div class="metric-box">
        <div class="metric-label">Peak Extension</div>
        <div class="metric-value">{top_mult}</div>
        <div class="metric-sub">highest confirmed ATR×</div>
      </div>
      <div class="metric-box">
        <div class="metric-label">ETF Hits</div>
        <div class="metric-value">{n_etf_hit}</div>
        <div class="metric-sub">incl. leveraged ETFs</div>
      </div>
      <div class="metric-box">
        <div class="metric-label">TV Candidates</div>
        <div class="metric-value">{p1_count}</div>
        <div class="metric-sub">Phase 1 pre-screen</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # CSV export
    if results:
        df_exp = pd.DataFrame(results)
        dl_col.download_button(
            "↓ CSV",
            data=df_exp.to_csv(index=False).encode(),
            file_name=f"atr_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
        )

    if not results:
        st.markdown("""
        <div class="empty-state">
          <div class="empty-icon">◌</div>
          <div class="empty-text">No symbols confirmed at the current threshold.</div>
          <div class="empty-hint">Try lowering the ATR multiple — 7× catches the profit-taking zone.</div>
        </div>
        """, unsafe_allow_html=True)

    else:
        def atr_cls(m):
            if m >= 15: return "atr-extreme"
            if m >= 10: return "atr-high"
            return "atr-norm"

        COLS = 3
        for i in range(0, len(results), COLS):
            chunk = results[i:i + COLS]
            cols  = st.columns(COLS)
            for col, r in zip(cols, chunk):
                chg_cls  = "pos" if r["day_chg"] >= 0 else "neg"
                chg_sign = "+" if r["day_chg"] >= 0 else ""
                type_lbl = "ETF" if r["is_etf"] else "STOCK"
                type_cls = "tag-etf" if r["is_etf"] else "tag-stock"

                col.markdown(f"""
<div class="card">
  <span class="atr-badge {atr_cls(r['atr_mult'])}">{r['atr_mult']}×</span>
  <div class="card-ticker">{r['ticker']}</div>
  <div class="card-price">${r['price']:,.2f}</div>
  <div class="card-divider"></div>
  <div class="card-stats">
    <div>
      <span class="stat-k">Day Chg</span>
      <span class="stat-v {chg_cls}">{chg_sign}{r['day_chg']}%</span>
    </div>
    <div>
      <span class="stat-k">vs SMA{sma_lbl}</span>
      <span class="stat-v pos">+{r['pct_sma']}%</span>
    </div>
    <div>
      <span class="stat-k">ATR%</span>
      <span class="stat-v">{r['atr_pct']}%</span>
    </div>
    <div>
      <span class="stat-k">Avg Vol</span>
      <span class="stat-v">{r['avg_vol']}</span>
    </div>
  </div>
  <div class="signal-row">
    <div class="sig-cell">
      <span class="sig-label">5D Gain</span>
      <span class="sig-val {'pos' if r['gain_5d']>=0 else 'neg'}">{'+' if r['gain_5d']>=0 else ''}{r['gain_5d']}%</span>
    </div>
    <div class="sig-cell">
      <span class="sig-label">Rel Vol</span>
      <span class="sig-val {'warn' if r['rel_vol']>=2 else ''}">{r['rel_vol']}×</span>
    </div>
    <div class="sig-cell">
      <span class="sig-label">Streak</span>
      <span class="sig-val warn">{r['consec_days']}d ↑</span>
    </div>
  </div>
  <div class="card-tags">
    <span class="tag {type_cls}">{type_lbl}</span>
    <span class="tag tag-exch">{r['exchange']}</span>
    {'<span class="tag tag-day1">⚠ DAY 1</span>' if r['is_day1'] else ''}
    {'<span class="tag tag-streak">🔥 ' + str(r['consec_days']) + 'd</span>' if r['consec_days'] >= 3 else ''}
    {'<span class="tag tag-rvol">RVOL ' + str(r['rel_vol']) + '×</span>' if r['rel_vol'] >= 1.5 else ''}
  </div>
</div>
""", unsafe_allow_html=True)

        with st.expander(f"▸  Full Results  ({n_hits} rows)"):
            disp = pd.DataFrame(results).rename(columns={
                "ticker":      "Ticker",
                "exchange":    "Exchange",
                "is_etf":      "ETF",
                "price":       "Price",
                "atr_mult":    "ATR× (B/A)",
                "tv_atr_mult": "TV ATR× (pre-screen)",
                "sma":         f"SMA{sma_lbl}",
                "atr":         f"ATR{atr_lbl} $",
                "atr_pct":     "ATR% (A)",
                "pct_sma":     "% Above SMA (B)",
                "day_chg":     "Day Chg %",
                "avg_vol":     "Avg Volume",
                "consec_days": "Streak (days)",
                "gain_5d":     "5D Gain %",
                "gain_1m":     "1M Gain %",
                "rel_vol":     "Rel Vol",
                "tv_gap":      "Gap %",
                "is_day1":     "Day 1?",
            })
            st.dataframe(disp, use_container_width=True, hide_index=True)

else:
    st.markdown("""
    <div class="empty-state" style="margin-top:4rem">
      <div class="empty-icon">◈</div>
      <div class="empty-text">Configure parameters in the sidebar and tap <b>RUN SCAN</b></div>
      <div class="empty-hint">Phase 1 TradingView pre-screen completes in ~2 sec · Phase 2 validates survivors only</div>
    </div>
    """, unsafe_allow_html=True)
