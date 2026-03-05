import streamlit as st
import streamlit.components.v1 as st_components
import yfinance as yf
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# ─────────────────────────────────────────────────────────────────────────────

st.set_page_config(
page_title=“ATR Screener”,
page_icon=“◈”,
layout=“wide”,
initial_sidebar_state=“expanded”,
)

# ─────────────────────────────────────────────────────────────────────────────

# DESIGN SYSTEM — refined institutional terminal

# Deep slate · warm amber accents · Geist Mono + DM Sans

# ─────────────────────────────────────────────────────────────────────────────

st.markdown(”””

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

.chart-container {
  background: var(--bg1);
  border: 1px solid var(--line2);
  border-radius: var(--r);
  padding: 0;
  margin-bottom: 1.4rem;
  overflow: hidden;
}
.chart-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 0.65rem 1rem;
  border-bottom: 1px solid var(--line);
  background: var(--bg2);
}
.chart-ticker-label {
  font-family: 'Geist Mono', monospace;
  font-size: 1rem; font-weight: 700; color: var(--bright);
  letter-spacing: 0.04em;
}
.chart-meta {
  font-family: 'Geist Mono', monospace;
  font-size: 0.65rem; color: var(--muted);
}

.sector-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 8px;
  margin-bottom: 1.4rem;
}
.sector-card {
  background: var(--bg1);
  border: 1px solid var(--line);
  border-radius: var(--r);
  padding: 0.65rem 0.75rem;
  position: relative;
  overflow: hidden;
}
.sector-card::before {
  content: '';
  position: absolute; left: 0; top: 0; bottom: 0;
  width: 3px;
}
.sector-card.s-cold  { border-color: var(--line); }
.sector-card.s-warm  { border-color: rgba(45,212,191,.3); }
.sector-card.s-hot   { border-color: rgba(245,158,11,.4); }
.sector-card.s-fire  { border-color: rgba(248,113,113,.5); }
.sector-card.s-cold::before  { background: var(--dim); }
.sector-card.s-warm::before  { background: var(--teal); }
.sector-card.s-hot::before   { background: var(--amber); }
.sector-card.s-fire::before  { background: var(--red); }
.sector-name {
  font-family: 'Geist Mono', monospace;
  font-size: 0.62rem; font-weight: 600;
  color: var(--body); letter-spacing: 0.04em;
  text-transform: uppercase; margin-bottom: 0.3rem;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.sector-mult {
  font-family: 'Geist Mono', monospace;
  font-size: 1.1rem; font-weight: 700; line-height: 1;
}
.sector-mult.s-cold  { color: var(--muted); }
.sector-mult.s-warm  { color: var(--teal); }
.sector-mult.s-hot   { color: var(--amber); }
.sector-mult.s-fire  { color: var(--red); }
.sector-sub {
  font-family: 'Geist Mono', monospace;
  font-size: 0.58rem; color: var(--dim); margin-top: 0.2rem;
}
.sector-bar {
  height: 2px; border-radius: 1px;
  margin-top: 0.45rem;
  background: var(--line);
  position: relative;
}
.sector-bar-fill {
  height: 100%; border-radius: 1px;
  position: absolute; left: 0; top: 0;
}

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

“””, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────

# SCAN ENGINE — TWO-PHASE

# ─────────────────────────────────────────────────────────────────────────────

# TradingView exchange name mapping

TV_EXCHANGE_MAP = {
“NASDAQ”:        “NASDAQ”,
“NYSE”:          “NYSE”,
“NYSE Arca”:     “AMEX”,   # TV calls NYSE Arca “AMEX”
“NYSE American”: “AMEX”,
“BATS”:          “BATS”,
“IEX”:           None,     # not in TV screener
}

# Exchange → TradingView symbol prefix

TV_PREFIX = {
“NASDAQ”:        “NASDAQ”,
“NYSE”:          “NYSE”,
“NYSE Arca”:     “AMEX”,
“NYSE American”: “AMEX”,
“AMEX”:          “AMEX”,
“BATS”:          “BATS”,
“IEX”:           “NYSE”,   # fallback
}

def tv_symbol(ticker: str, exchange: str) -> str:
prefix = TV_PREFIX.get(exchange, “NYSE”)
return f”{prefix}:{ticker}”

def render_tv_chart(ticker: str, exchange: str, theme: str = “dark”) -> str:
“”“Return self-contained HTML for a TradingView Advanced Chart widget.”””
sym      = tv_symbol(ticker, exchange)
cid      = f”tv_{ticker.replace(’.’, ‘_’)}”
return f”””

<div id="{cid}" style="height:520px;border-radius:6px;overflow:hidden;"></div>
<script src="https://s3.tradingview.com/tv.js"></script>
<script>
new TradingView.widget({{
  container_id: "{cid}",
  autosize: true,
  symbol: "{sym}",
  interval: "D",
  timezone: "America/New_York",
  theme: "dark",
  style: "1",
  locale: "en",
  toolbar_bg: "#0e1114",
  backgroundColor: "#080a0c",
  gridColor: "#232a38",
  hide_top_toolbar: false,
  hide_legend: false,
  save_image: false,
  studies: [
    "MASimple@tv-basicstudies",
    "ATR@tv-basicstudies"
  ],
  studies_overrides: {{
    "moving average.length": 50,
    "moving average.plot.color": "rgb(245, 158, 11)"
  }},
  overrides: {{
    "paneProperties.background": "#080a0c",
    "paneProperties.backgroundType": "solid",
    "paneProperties.vertGridProperties.color": "#1c2130",
    "paneProperties.horzGridProperties.color": "#1c2130",
    "scalesProperties.textColor": "#607080",
    "mainSeriesProperties.candleStyle.upColor":   "#34d399",
    "mainSeriesProperties.candleStyle.downColor": "#f87171",
    "mainSeriesProperties.candleStyle.borderUpColor":   "#34d399",
    "mainSeriesProperties.candleStyle.borderDownColor": "#f87171",
    "mainSeriesProperties.candleStyle.wickUpColor":   "#34d399",
    "mainSeriesProperties.candleStyle.wickDownColor": "#f87171"
  }}
}});
</script>
"""

# Market cap tier definitions (USD)

MCAP_TIERS = {
“All”:        (0,             None),
“Micro”:      (0,             300_000_000),
“Small”:      (300_000_000,   2_000_000_000),
“Mid”:        (2_000_000_000, 10_000_000_000),
“Large”:      (10_000_000_000,200_000_000_000),
“Mega”:       (200_000_000_000, None),
}

def phase1_tradingview(min_price: float, min_vol: int, prescreen_mult: float,
asset_filter: str, exchange_filter: list,
mcap_tiers: list | None = None) -> tuple[list, str | None]:
“””
Phase 1 — TradingView scanner API.
Single fast call covering all US exchanges. Returns candidate dicts.
Uses an 80% pre-screen threshold to avoid missing boundary cases.
“””
try:
from tradingview_screener import Query, Column
except ImportError:
return [], “tradingview-screener not installed”

```
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
```

def wilder_atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
tr = pd.concat([
high - low,
(high - close.shift()).abs(),
(low  - close.shift()).abs(),
], axis=1).max(axis=1)
return tr.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()

# Sector ETF proxies — liquid, covers all 11 GICS sectors

SECTOR_ETFS = {
“Technology”:       “XLK”,
“Healthcare”:       “XLV”,
“Financials”:       “XLF”,
“Consumer Disc”:    “XLY”,
“Industrials”:      “XLI”,
“Communication”:    “XLC”,
“Consumer Staples”: “XLP”,
“Energy”:           “XLE”,
“Utilities”:        “XLU”,
“Real Estate”:      “XLRE”,
“Materials”:        “XLB”,
}

@st.cache_data(ttl=900)   # 15-min cache
def fetch_sector_heatmap(sma_period: int = 50, atr_period: int = 14) -> list[dict]:
“””
Fetch OHLCV for each sector ETF, compute ATR× extension,
return sorted list for heatmap display.
“””
results = []
tickers = list(SECTOR_ETFS.values())
try:
raw = yf.download(tickers, period=“6mo”, interval=“1d”,
progress=False, auto_adjust=False, group_by=“ticker”)
except Exception:
return []

```
sector_name = {v: k for k, v in SECTOR_ETFS.items()}

for etf in tickers:
    try:
        if isinstance(raw.columns, pd.MultiIndex):
            df = raw[etf].dropna(how="all")
        else:
            df = raw.dropna(how="all")

        close = df["Close"].squeeze().dropna()
        high  = df["High"].squeeze()
        low   = df["Low"].squeeze()
        if len(close) < sma_period + 5:
            continue

        last  = float(close.iloc[-1])
        sma   = float(close.rolling(sma_period).mean().iloc[-1])
        atr   = float(wilder_atr(high, low, close, atr_period).iloc[-1])

        if sma <= 0 or atr <= 0 or last <= 0:
            continue

        atr_pct  = atr / last
        pct_sma  = (last - sma) / sma
        if atr_pct == 0:
            continue
        mult = round(pct_sma / atr_pct, 2)

        prev    = float(close.iloc[-2]) if len(close) > 1 else last
        day_chg = round((last - prev) / prev * 100, 2)

        results.append({
            "sector":   sector_name.get(etf, etf),
            "etf":      etf,
            "price":    round(last, 2),
            "mult":     mult,
            "pct_sma":  round(pct_sma * 100, 1),
            "atr_pct":  round(atr_pct * 100, 2),
            "day_chg":  day_chg,
            "sma":      round(sma, 2),
        })
    except Exception:
        continue

return sorted(results, key=lambda x: x["mult"], reverse=True)
```

def sector_heat_class(mult: float) -> str:
if mult >= 10:  return “s-fire”
if mult >= 5:   return “s-hot”
if mult >= 2:   return “s-warm”
return “s-cold”

def sector_bar_color(mult: float) -> str:
if mult >= 10:  return “var(–red)”
if mult >= 5:   return “var(–amber)”
if mult >= 2:   return “var(–teal)”
return “var(–dim)”

def sector_bar_pct(mult: float, max_mult: float = 20.0) -> int:
return min(int(max(mult, 0) / max_mult * 100), 100)

def phase2_confirm(candidate: dict, sma_period: int, atr_period: int,
min_price: float, min_vol: int, min_atr_mult: float) -> dict | None:
“””
Phase 2 — enrich TV candidates with yfinance volume + day change only.

```
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
```

def run_two_phase_scan(min_price, min_atr_mult, sma_period, atr_period,
asset_filter, exchange_filter, workers, min_vol,
mcap_tiers, phase1_status_cb, phase2_progress_cb):
“””
Full two-phase scan.
phase1_status_cb(msg, n_candidates) — called once after Phase 1 completes.
phase2_progress_cb(pct, done, total) — called after each Phase 2 ticker.
“””
# ── Phase 1 ──────────────────────────────────────────────────────────────
prescreen_mult = min_atr_mult * 0.80   # 20% buffer for boundary cases
candidates, err = phase1_tradingview(
min_price, min_vol, prescreen_mult, asset_filter, exchange_filter, mcap_tiers
)

```
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

return sorted(results, key=lambda x: x["atr_mult"], reverse=True)
```

# ─────────────────────────────────────────────────────────────────────────────

# EPISODIC PIVOT SCANNER

# ─────────────────────────────────────────────────────────────────────────────

def phase1_ep(min_gap_pct: float, min_vol: int, min_price: float,
asset_filter: str, exchange_filter: list,
mcap_tiers: list | None = None) -> tuple[list, str | None]:
“”“Phase 1 — TradingView EP scan: gap >= threshold, high rel vol, price > min.”””
try:
from tradingview_screener import Query, Column
except ImportError:
return [], “tradingview-screener not installed”

```
tv_exchanges = list({TV_EXCHANGE_MAP[e] for e in exchange_filter
                     if e in TV_EXCHANGE_MAP and TV_EXCHANGE_MAP[e]})
try:
    q = (
        Query()
        .set_markets("america")
        .select("name", "close", "gap", "relative_volume_10d_calc",
                "volume", "change", "Perf.3M", "Perf.6M", "type", "exchange",
                "market_cap_basic", "SMA50", "ATR")
        .where(
            Column("close") > min_price,
            Column("volume") > min_vol,
            Column("gap") >= min_gap_pct,
            Column("relative_volume_10d_calc") >= 2.0,
        )
        .order_by("relative_volume_10d_calc", ascending=False)
        .limit(500)
    )
    if asset_filter == "ETFs Only":
        q = q.where(Column("type").isin(["fund", "etf"]))
    elif asset_filter == "Stocks Only":
        q = q.where(Column("type") == "stock")
    if tv_exchanges:
        q = q.where(Column("exchange").isin(tv_exchanges))
    if mcap_tiers and "All" not in mcap_tiers:
        cap_conditions = []
        for tier in mcap_tiers:
            lo, hi = MCAP_TIERS.get(tier, (0, None))
            if lo and hi:
                cap_conditions.append((Column("market_cap_basic") >= lo) & (Column("market_cap_basic") < hi))
            elif lo:
                cap_conditions.append(Column("market_cap_basic") >= lo)
            elif hi:
                cap_conditions.append(Column("market_cap_basic") < hi)
        if cap_conditions:
            combined = cap_conditions[0]
            for c in cap_conditions[1:]: combined = combined | c
            q = q.where(combined)

    _, df = q.get_scanner_data()
except Exception as e:
    return [], f"TradingView API error: {e}"

if df is None or df.empty:
    return [], None

for col in ["gap", "relative_volume_10d_calc", "change", "Perf.3M", "Perf.6M", "SMA50", "ATR"]:
    if col not in df.columns: df[col] = 0.0
df = df.fillna(0.0)
df["is_etf"] = df["type"].isin(["fund", "etf", "dr"])

return (
    df[["name", "close", "gap", "relative_volume_10d_calc", "change",
        "Perf.3M", "Perf.6M", "exchange", "is_etf", "SMA50", "ATR"]]
    .rename(columns={"name": "ticker", "close": "tv_close",
                     "relative_volume_10d_calc": "rel_vol",
                     "change": "day_chg", "Perf.3M": "gain_3m",
                     "Perf.6M": "gain_6m", "SMA50": "tv_sma50", "ATR": "tv_atr"})
    .to_dict("records"),
    None,
)
```

def phase2_ep_confirm(candidate: dict, min_vol: int) -> dict | None:
“”“Phase 2 EP — enrich with yfinance: avg vol, streak, prior consolidation check.”””
ticker   = candidate[“ticker”]
tv_close = float(candidate.get(“tv_close”) or 0)
gap_pct  = float(candidate.get(“gap”) or 0)
rel_vol  = float(candidate.get(“rel_vol”) or 0)

```
if tv_close <= 0:
    return None

# Was stock in consolidation before the EP? (low 3M gain before today = good EP)
gain_3m = float(candidate.get("gain_3m") or 0)

avg_vol  = None
consec   = 0
day_chg  = float(candidate.get("day_chg") or 0)

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
            if len(volumes) >= 5:
                avg_vol = float(volumes.tail(20).mean())
            if len(closes) >= 2:
                for i in range(len(closes) - 1, 0, -1):
                    if float(closes.iloc[i]) > float(closes.iloc[i - 1]):
                        consec += 1
                    else:
                        break
except Exception:
    pass

if avg_vol is not None and avg_vol >= 1_000_000:
    avg_vol_disp = f"{avg_vol/1_000_000:.1f}M"
elif avg_vol is not None and avg_vol >= 1_000:
    avg_vol_disp = f"{avg_vol/1_000:.0f}K"
else:
    avg_vol_disp = "N/A"

# Quality score: higher gap + higher rel_vol + low prior gain (neglected stock) = better EP
neglect_bonus = 1.0 if gain_3m < 20 else 0.0  # stock was sideways → true EP
ep_score = round(gap_pct * 0.5 + rel_vol * 2 + neglect_bonus * 10, 1)

return {
    "ticker":     ticker,
    "price":      round(tv_close, 2),
    "gap_pct":    round(gap_pct, 1),
    "rel_vol":    round(rel_vol, 2),
    "day_chg":    round(float(day_chg), 2),
    "gain_3m":    round(gain_3m, 1),
    "gain_6m":    round(float(candidate.get("gain_6m") or 0), 1),
    "avg_vol":    avg_vol_disp,
    "consec_days": consec,
    "is_day1":    consec <= 1,
    "ep_score":   ep_score,
    "neglected":  gain_3m < 20,   # True = stock was basing → ideal EP
    "is_etf":     candidate["is_etf"],
    "exchange":   candidate["exchange"],
}
```

def run_ep_scan(min_gap_pct, min_price, asset_filter, exchange_filter,
min_vol, mcap_tiers, workers, p1_cb, p2_cb):
candidates, err = phase1_ep(min_gap_pct, min_vol, min_price,
asset_filter, exchange_filter, mcap_tiers)
if err:
p1_cb(f”Phase 1 warning: {err}”, 0)
candidates = []
p1_cb(None, len(candidates))
if not candidates:
return []

```
total, done, results = len(candidates), 0, []
with ThreadPoolExecutor(max_workers=workers) as ex:
    futs = {ex.submit(phase2_ep_confirm, c, min_vol): c for c in candidates}
    for fut in as_completed(futs):
        done += 1
        p2_cb(done / total, done, total)
        res = fut.result()
        if res:
            results.append(res)
return sorted(results, key=lambda x: x["ep_score"], reverse=True)
```

# ─────────────────────────────────────────────────────────────────────────────

# MOMENTUM BREAKOUT SCANNER

# ─────────────────────────────────────────────────────────────────────────────

def phase1_breakout(min_perf_1m: float, min_vol: int, min_price: float,
asset_filter: str, exchange_filter: list,
mcap_tiers: list | None = None) -> tuple[list, str | None]:
“”“Phase 1 — TradingView breakout scan: strong 1-3M gainers near MAs.”””
try:
from tradingview_screener import Query, Column
except ImportError:
return [], “tradingview-screener not installed”

```
tv_exchanges = list({TV_EXCHANGE_MAP[e] for e in exchange_filter
                     if e in TV_EXCHANGE_MAP and TV_EXCHANGE_MAP[e]})
try:
    q = (
        Query()
        .set_markets("america")
        .select("name", "close", "SMA10", "SMA20", "SMA50", "ATR",
                "volume", "relative_volume_10d_calc", "change",
                "Perf.1M", "Perf.3M", "Perf.6M", "type", "exchange",
                "market_cap_basic")
        .where(
            Column("close") > min_price,
            Column("volume") > min_vol,
            Column("Perf.1M") >= min_perf_1m,
            Column("close") > Column("SMA50"),      # above long-term MA
            Column("relative_volume_10d_calc") < 1.5,  # volume drying up = consolidation
        )
        .order_by("Perf.3M", ascending=False)
        .limit(500)
    )
    if asset_filter == "ETFs Only":
        q = q.where(Column("type").isin(["fund", "etf"]))
    elif asset_filter == "Stocks Only":
        q = q.where(Column("type") == "stock")
    if tv_exchanges:
        q = q.where(Column("exchange").isin(tv_exchanges))
    if mcap_tiers and "All" not in mcap_tiers:
        cap_conditions = []
        for tier in mcap_tiers:
            lo, hi = MCAP_TIERS.get(tier, (0, None))
            if lo and hi:
                cap_conditions.append((Column("market_cap_basic") >= lo) & (Column("market_cap_basic") < hi))
            elif lo:
                cap_conditions.append(Column("market_cap_basic") >= lo)
            elif hi:
                cap_conditions.append(Column("market_cap_basic") < hi)
        if cap_conditions:
            combined = cap_conditions[0]
            for c in cap_conditions[1:]: combined = combined | c
            q = q.where(combined)

    _, df = q.get_scanner_data()
except Exception as e:
    return [], f"TradingView API error: {e}"

if df is None or df.empty:
    return [], None

for col in ["SMA10", "SMA20", "SMA50", "ATR", "relative_volume_10d_calc",
            "change", "Perf.1M", "Perf.3M", "Perf.6M"]:
    if col not in df.columns: df[col] = 0.0
df = df.fillna(0.0)
df["is_etf"] = df["type"].isin(["fund", "etf", "dr"])

return (
    df[["name", "close", "SMA10", "SMA20", "SMA50", "ATR",
        "relative_volume_10d_calc", "change",
        "Perf.1M", "Perf.3M", "Perf.6M", "exchange", "is_etf"]]
    .rename(columns={"name": "ticker", "close": "tv_close",
                     "relative_volume_10d_calc": "rel_vol",
                     "change": "day_chg",
                     "Perf.1M": "gain_1m", "Perf.3M": "gain_3m", "Perf.6M": "gain_6m"})
    .to_dict("records"),
    None,
)
```

def phase2_breakout_confirm(candidate: dict, min_vol: int) -> dict | None:
“”“Phase 2 Breakout — check consolidation tightness, proximity to MAs.”””
ticker   = candidate[“ticker”]
tv_close = float(candidate.get(“tv_close”) or 0)
sma10    = float(candidate.get(“SMA10”) or 0)
sma20    = float(candidate.get(“SMA20”) or 0)
sma50    = float(candidate.get(“SMA50”) or 0)
tv_atr   = float(candidate.get(“ATR”)   or 0)

```
if tv_close <= 0:
    return None

# Distance from key MAs
dist_10 = round((tv_close - sma10) / sma10 * 100, 1) if sma10 > 0 else None
dist_20 = round((tv_close - sma20) / sma20 * 100, 1) if sma20 > 0 else None
dist_50 = round((tv_close - sma50) / sma50 * 100, 1) if sma50 > 0 else None

# Proximity score: closer to 10/20 MA = better consolidation near MA
ma_prox = min(abs(dist_10 or 99), abs(dist_20 or 99))

avg_vol  = None
range_tightness = None
consec   = 0
day_chg  = float(candidate.get("day_chg") or 0)

try:
    df = yf.download(ticker, period="3mo", interval="1d",
                     progress=False, auto_adjust=False)
    if not df.empty:
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        close_col = "Close" if "Close" in df.columns else "Adj Close"
        high_col  = "High"
        low_col   = "Low"
        if all(c in df.columns for c in [close_col, high_col, low_col, "Volume"]):
            closes  = df[close_col].squeeze().dropna()
            highs   = df[high_col].squeeze()
            lows    = df[low_col].squeeze()
            volumes = df["Volume"].squeeze()
            if len(volumes) >= 5:
                avg_vol = float(volumes.tail(20).mean())
            # Range tightness: avg (H-L)/close over last 10 days — lower = tighter base
            if len(closes) >= 10:
                recent_range = ((highs.tail(10) - lows.tail(10)) / closes.tail(10)).mean()
                range_tightness = round(float(recent_range) * 100, 1)
            if len(closes) >= 2:
                for i in range(len(closes) - 1, 0, -1):
                    if float(closes.iloc[i]) > float(closes.iloc[i - 1]):
                        consec += 1
                    else:
                        break
except Exception:
    pass

if avg_vol is not None and avg_vol >= 1_000_000:
    avg_vol_disp = f"{avg_vol/1_000_000:.1f}M"
elif avg_vol is not None and avg_vol >= 1_000:
    avg_vol_disp = f"{avg_vol/1_000:.0f}K"
else:
    avg_vol_disp = "N/A"

# Setup quality: tight range + near MA + strong prior move = higher score
tightness_score = max(0, 10 - (range_tightness or 10))
proximity_score = max(0, 10 - ma_prox)
momentum_score  = min(float(candidate.get("gain_3m") or 0) / 10, 10)
setup_score     = round(tightness_score * 0.4 + proximity_score * 0.4 + momentum_score * 0.2, 1)

return {
    "ticker":           ticker,
    "price":            round(tv_close, 2),
    "day_chg":          round(day_chg, 2),
    "gain_1m":          round(float(candidate.get("gain_1m") or 0), 1),
    "gain_3m":          round(float(candidate.get("gain_3m") or 0), 1),
    "gain_6m":          round(float(candidate.get("gain_6m") or 0), 1),
    "sma10":            round(sma10, 2),
    "sma20":            round(sma20, 2),
    "sma50":            round(sma50, 2),
    "dist_10":          dist_10,
    "dist_20":          dist_20,
    "dist_50":          dist_50,
    "ma_proximity":     round(ma_prox, 1),
    "range_tightness":  range_tightness,
    "rel_vol":          round(float(candidate.get("rel_vol") or 0), 2),
    "avg_vol":          avg_vol_disp,
    "consec_days":      consec,
    "setup_score":      setup_score,
    "is_etf":           candidate["is_etf"],
    "exchange":         candidate["exchange"],
}
```

def run_breakout_scan(min_perf_1m, min_price, asset_filter, exchange_filter,
min_vol, mcap_tiers, workers, p1_cb, p2_cb):
candidates, err = phase1_breakout(min_perf_1m, min_vol, min_price,
asset_filter, exchange_filter, mcap_tiers)
if err:
p1_cb(f”Phase 1 warning: {err}”, 0)
candidates = []
p1_cb(None, len(candidates))
if not candidates:
return []

```
total, done, results = len(candidates), 0, []
with ThreadPoolExecutor(max_workers=workers) as ex:
    futs = {ex.submit(phase2_breakout_confirm, c, min_vol): c for c in candidates}
    for fut in as_completed(futs):
        done += 1
        p2_cb(done / total, done, total)
        res = fut.result()
        if res:
            results.append(res)
return sorted(results, key=lambda x: x["setup_score"], reverse=True)
```

# ─────────────────────────────────────────────────────────────────────────────

# PARABOLIC LONG SCANNER

# Inverse of Parabolic Short: stocks down 40%+ in ≤10 days, vol spiking,

# first green day = bounce entry on ORH. Targets 50-100% bounce.

# ─────────────────────────────────────────────────────────────────────────────

def phase1_parabolic_long(min_drop_5d: float, min_vol: int, min_price: float,
asset_filter: str, exchange_filter: list,
mcap_tiers: list | None = None) -> tuple[list, str | None]:
“”“Phase 1 — TV scan: stocks down sharply in 5 days, high rel vol today.”””
try:
from tradingview_screener import Query, Column
except ImportError:
return [], “tradingview-screener not installed”

```
tv_exchanges = list({TV_EXCHANGE_MAP[e] for e in exchange_filter
                     if e in TV_EXCHANGE_MAP and TV_EXCHANGE_MAP[e]})
try:
    q = (
        Query()
        .set_markets("america")
        .select("name", "close", "change", "Perf.5D", "Perf.1M",
                "relative_volume_10d_calc", "volume", "SMA10", "SMA20",
                "ATR", "gap", "type", "exchange", "market_cap_basic")
        .where(
            Column("close") > min_price,
            Column("volume") > min_vol,
            Column("Perf.5D") <= -min_drop_5d,       # down hard in 5 days
            Column("relative_volume_10d_calc") >= 1.5, # vol spiking = real panic
            Column("change") >= 0,                    # today is green (first bounce)
        )
        .order_by("Perf.5D", ascending=True)           # worst drops first
        .limit(300)
    )
    if asset_filter == "ETFs Only":
        q = q.where(Column("type").isin(["fund", "etf"]))
    elif asset_filter == "Stocks Only":
        q = q.where(Column("type") == "stock")
    if tv_exchanges:
        q = q.where(Column("exchange").isin(tv_exchanges))
    if mcap_tiers and "All" not in mcap_tiers:
        cap_conditions = []
        for tier in mcap_tiers:
            lo, hi = MCAP_TIERS.get(tier, (0, None))
            if lo and hi:
                cap_conditions.append((Column("market_cap_basic") >= lo) & (Column("market_cap_basic") < hi))
            elif lo:
                cap_conditions.append(Column("market_cap_basic") >= lo)
            elif hi:
                cap_conditions.append(Column("market_cap_basic") < hi)
        if cap_conditions:
            combined = cap_conditions[0]
            for c in cap_conditions[1:]: combined = combined | c
            q = q.where(combined)

    _, df = q.get_scanner_data()
except Exception as e:
    return [], f"TradingView API error: {e}"

if df is None or df.empty:
    return [], None

for col in ["change", "Perf.5D", "Perf.1M", "relative_volume_10d_calc",
            "SMA10", "SMA20", "ATR", "gap"]:
    if col not in df.columns: df[col] = 0.0
df = df.fillna(0.0)
df["is_etf"] = df["type"].isin(["fund", "etf", "dr"])

return (
    df[["name", "close", "change", "Perf.5D", "Perf.1M",
        "relative_volume_10d_calc", "SMA10", "SMA20", "ATR",
        "gap", "exchange", "is_etf"]]
    .rename(columns={"name": "ticker", "close": "tv_close",
                     "change": "day_chg", "Perf.5D": "drop_5d",
                     "Perf.1M": "drop_1m",
                     "relative_volume_10d_calc": "rel_vol"})
    .to_dict("records"),
    None,
)
```

def phase2_pl_confirm(candidate: dict, min_vol: int) -> dict | None:
“”“Phase 2 Parabolic Long — measure collapse speed, prior trend, bounce quality.”””
ticker   = candidate[“ticker”]
tv_close = float(candidate.get(“tv_close”) or 0)
drop_5d  = float(candidate.get(“drop_5d”) or 0)
rel_vol  = float(candidate.get(“rel_vol”) or 0)
day_chg  = float(candidate.get(“day_chg”) or 0)
sma10    = float(candidate.get(“SMA10”) or 0)
sma20    = float(candidate.get(“SMA20”) or 0)
atr      = float(candidate.get(“ATR”) or 0)

```
if tv_close <= 0:
    return None

consec_down  = 0
prior_high   = None
drop_from_high = None
avg_vol      = None

try:
    df = yf.download(ticker, period="3mo", interval="1d",
                     progress=False, auto_adjust=False)
    if not df.empty:
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        close_col = "Close" if "Close" in df.columns else "Adj Close"
        high_col  = "High"
        if all(c in df.columns for c in [close_col, "Volume"]):
            closes  = df[close_col].squeeze().dropna()
            volumes = df["Volume"].squeeze()
            highs   = df[high_col].squeeze() if high_col in df.columns else closes

            if len(volumes) >= 5:
                avg_vol = float(volumes.tail(20).mean())

            # Count consecutive down days before today
            if len(closes) >= 3:
                for i in range(len(closes) - 2, 0, -1):
                    if float(closes.iloc[i]) < float(closes.iloc[i - 1]):
                        consec_down += 1
                    else:
                        break

            # Prior high in the past 3 months → how far did it drop?
            if len(highs) >= 10:
                prior_high   = float(highs.tail(65).max())
                drop_from_high = round((tv_close - prior_high) / prior_high * 100, 1)

except Exception:
    pass

if avg_vol is not None and avg_vol >= 1_000_000:
    avg_vol_disp = f"{avg_vol/1_000_000:.1f}M"
elif avg_vol is not None and avg_vol >= 1_000:
    avg_vol_disp = f"{avg_vol/1_000:.0f}K"
else:
    avg_vol_disp = "N/A"

# Bounce score: sharper drop + more down days + higher vol = more coiled spring
speed_score   = min(abs(drop_5d) / 5, 10)          # 50% drop in 5d = 10
streak_score  = min(consec_down * 1.5, 10)
vol_score     = min((rel_vol - 1) * 3, 10)
bounce_score  = round((speed_score * 0.4 + streak_score * 0.3 + vol_score * 0.3), 1)

# Distance from MAs — below both = more room to snap back
dist_10 = round((tv_close - sma10) / sma10 * 100, 1) if sma10 > 0 else None
dist_20 = round((tv_close - sma20) / sma20 * 100, 1) if sma20 > 0 else None

return {
    "ticker":           ticker,
    "price":            round(tv_close, 2),
    "day_chg":          round(day_chg, 2),
    "drop_5d":          round(drop_5d, 1),
    "drop_1m":          round(float(candidate.get("drop_1m") or 0), 1),
    "drop_from_high":   drop_from_high,
    "consec_down":      consec_down,
    "rel_vol":          round(rel_vol, 2),
    "avg_vol":          avg_vol_disp,
    "bounce_score":     bounce_score,
    "dist_10":          dist_10,
    "dist_20":          dist_20,
    "atr":              round(atr, 2),
    "is_etf":           candidate["is_etf"],
    "exchange":         candidate["exchange"],
}
```

def run_parabolic_long_scan(min_drop_5d, min_price, asset_filter, exchange_filter,
min_vol, mcap_tiers, workers, p1_cb, p2_cb):
candidates, err = phase1_parabolic_long(min_drop_5d, min_vol, min_price,
asset_filter, exchange_filter, mcap_tiers)
if err:
p1_cb(f”Phase 1 warning: {err}”, 0)
candidates = []
p1_cb(None, len(candidates))
if not candidates:
return []

```
total, done, results = len(candidates), 0, []
with ThreadPoolExecutor(max_workers=workers) as ex:
    futs = {ex.submit(phase2_pl_confirm, c, min_vol): c for c in candidates}
    for fut in as_completed(futs):
        done += 1
        p2_cb(done / total, done, total)
        res = fut.result()
        if res:
            results.append(res)
return sorted(results, key=lambda x: x["bounce_score"], reverse=True)
```

# ─────────────────────────────────────────────────────────────────────────────

# SIDEBAR

# ─────────────────────────────────────────────────────────────────────────────

with st.sidebar:
st.markdown(”””
<p style="font-family:'Geist Mono',monospace;font-size:1rem;font-weight:700;
color:#e2e8f0;letter-spacing:-0.01em;margin:0 0 0.15rem">◈ ATR Screener</p>
<p style="font-family:'Geist Mono',monospace;font-size:0.58rem;color:#3d4f6b;
letter-spacing:0.13em;margin:0 0 0.8rem">TWO-PHASE · TV + YFINANCE</p>
“””, unsafe_allow_html=True)

```
st.markdown('<span class="sec-label">Universe</span>', unsafe_allow_html=True)
min_price = st.number_input("Min Price ($)", value=10.0, step=5.0, min_value=0.0,
                             help="Applied to all scanners")
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
if "All" in mcap_tiers or not mcap_tiers:
    mcap_tiers = ["All"]

min_vol = st.number_input(
    "Min Avg Volume", value=500_000, step=100_000, min_value=0,
    help="Filters warrants, ghost tickers, and illiquid symbols",
)

st.markdown('<span class="sec-label">System</span>', unsafe_allow_html=True)
workers = st.slider("Workers", 1, 15, 6, label_visibility="collapsed")
st.markdown(
    f"<p style='font-family:\"Geist Mono\",monospace;font-size:0.63rem;"
    f"color:#3d4f6b'>{workers} parallel workers (Phase 2 only)</p>",
    unsafe_allow_html=True,
)

# Setup-specific defaults (used if tabs haven't rendered their inputs yet)
if "ps_atr_mult" not in st.session_state:  st.session_state["ps_atr_mult"] = 10.0
if "ps_sma_period" not in st.session_state: st.session_state["ps_sma_period"] = 50
if "ps_atr_period" not in st.session_state: st.session_state["ps_atr_period"] = 14
if "pl_drop" not in st.session_state:       st.session_state["pl_drop"] = 30.0
if "ep_gap" not in st.session_state:        st.session_state["ep_gap"] = 10.0
if "bo_perf" not in st.session_state:       st.session_state["bo_perf"] = 25.0
```

# ─────────────────────────────────────────────────────────────────────────────

# MAIN — TABBED LAYOUT

# ─────────────────────────────────────────────────────────────────────────────

st.markdown(”””

<div class="page-header">
  <div class="page-title">◈ Qullamaggie <span>Screener</span></div>
  <div class="page-sub">PARABOLIC SHORT  ·  EPISODIC PIVOT  ·  MOMENTUM BREAKOUT  ·  TV + WILDER ATR</div>
</div>
""", unsafe_allow_html=True)

# Resolve PS-specific params from session_state (set by tab widgets, fallback to defaults)

sma_period   = int(st.session_state.get(“ps_sma_period”, 50))
atr_period   = int(st.session_state.get(“ps_atr_period”, 14))
min_atr_mult = float(st.session_state.get(“ps_atr_mult”,  10.0))

tab_ps, tab_ep, tab_bo, tab_pl, tab_guide = st.tabs([
“📉  Parabolic Short”,
“⚡  Episodic Pivot”,
“🚀  Momentum Breakout”,
“📈  Parabolic Long”,
“📖  Playbook”,
])

# ══════════════════════════════════════════════════════════════════════════════

# SHARED HELPERS for card/results display

# ══════════════════════════════════════════════════════════════════════════════

def _status_row(label_a, label_b):
st.markdown(f”””

<div class="status-row">
  <span class="status-kv"><span class="pulse"></span>READY</span>
  <span class="status-kv">PHASE 1 <b>TradingView API</b></span>
  <span class="status-kv">PHASE 2 <b>yfinance · {label_b}</b></span>
  <span class="status-kv">AS OF <b>{datetime.now().strftime('%H:%M')}</b></span>
</div>
""", unsafe_allow_html=True)

def _run_phase_ui(scan_fn, scan_kwargs, state_key):
“”“Run a two-phase scan showing progress UI, store in session_state.”””
ph1 = st.empty(); ph2b = st.empty(); ph2p = st.empty(); ph2i = st.empty()
p1n = [0]; p1w = [None]

```
def p1_cb(warn, n):
    p1n[0] = n; p1w[0] = warn
    status = f"<b>{n}</b> candidates" if n else "no candidates"
    ph1.markdown(f"""
```

<div class="phase-banner">
  <span class="phase-num done">P1</span>
  <span class="phase-label">TradingView pre-screen complete</span>
  <span class="phase-detail">{status}</span>
</div>""", unsafe_allow_html=True)

```
def p2_cb(pct, done, total):
    ph2b.markdown(f"""
```

<div class="phase-banner">
  <span class="phase-num active">P2</span>
  <span class="phase-label">yfinance confirmation</span>
  <span class="phase-detail">{done} / {total}</span>
</div>""", unsafe_allow_html=True)
        ph2p.progress(min(pct, 1.0))
        ph2i.markdown(f"<span style='font-family:\"Geist Mono\",monospace;font-size:0.7rem;color:#607080'>Validating {done:,} / {total:,}…</span>", unsafe_allow_html=True)

```
ph1.markdown("""
```

<div class="phase-banner">
  <span class="phase-num active">P1</span>
  <span class="phase-label">Querying <b>TradingView</b>…</span>
</div>""", unsafe_allow_html=True)

```
results = scan_fn(p1_cb, p2_cb) if not scan_kwargs else scan_fn(**scan_kwargs, p1_cb=p1_cb, p2_cb=p2_cb)
ph2p.empty(); ph2i.empty()
ph2b.markdown(f"""
```

<div class="phase-banner">
  <span class="phase-num done">P2</span>
  <span class="phase-label">Confirmation complete</span>
  <span class="phase-detail"><b>{len(results)}</b> confirmed hits</span>
</div>""", unsafe_allow_html=True)
    if p1w[0]: st.warning(p1w[0])
    st.session_state[state_key] = results
    st.session_state[f"{state_key}_ts"]  = datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
    st.session_state[f"{state_key}_p1n"] = p1n[0]
    return results

def *show_chart_panel(state_prefix):
“”“Render TradingView chart panel for a given tab.”””
ct = st.session_state.get(f”chart_ticker*{state_prefix}”)
ce = st.session_state.get(f”chart_exchange_{state_prefix}”)
if not ct:
return
cl_col, _ = st.columns([1, 11])
if cl_col.button(“✕  Close”, key=f”close_chart_{state_prefix}”):
st.session_state[f”chart_ticker_{state_prefix}”]  = None
st.session_state[f”chart_exchange_{state_prefix}”] = None
st.rerun()
st.markdown(f”””

<div class="chart-header">
  <span class="chart-ticker-label">{ct}</span>
  <span class="chart-meta">{tv_symbol(ct, ce)}  ·  Daily  ·  SMA10 + SMA20 + SMA50 + ATR</span>
</div>""", unsafe_allow_html=True)
    st_components.html(render_tv_chart(ct, ce), height=540, scrolling=False)

# ══════════════════════════════════════════════════════════════════════════════

# TAB 1 — PARABOLIC SHORT

# ══════════════════════════════════════════════════════════════════════════════

with tab_ps:
_status_row(“Parabolic Short”, “Wilder ATR confirm”)

```
# Sector heatmap
st.markdown("""
```

<div style="display:flex;align-items:baseline;gap:0.75rem;margin-bottom:0.6rem">
  <span style="font-family:'Geist Mono',monospace;font-size:0.6rem;font-weight:600;
  letter-spacing:0.14em;color:#3d4f6b;text-transform:uppercase">Sector Extension Heatmap</span>
  <span style="font-family:'Geist Mono',monospace;font-size:0.58rem;color:#232a38">
  ATR× from SMA50 · GICS sector ETFs · 15-min cache</span>
</div>
""", unsafe_allow_html=True)

```
with st.spinner(""):
    sectors = fetch_sector_heatmap(int(sma_period), int(atr_period))

if sectors:
    max_mult = max(s["mult"] for s in sectors) if sectors else 15.0
    sector_html = '<div class="sector-grid">'
    for s in sectors:
        hc  = sector_heat_class(s["mult"])
        bc  = sector_bar_color(s["mult"])
        bp  = sector_bar_pct(s["mult"], max(max_mult, 1))
        sgn = "+" if s["day_chg"] >= 0 else ""
        chg_col = "var(--green)" if s["day_chg"] >= 0 else "var(--red)"
        mult_disp = f"{s['mult']}×" if s["mult"] > 0 else "—"
        sector_html += f"""
```

<div class="sector-card {hc}">
  <div class="sector-name">{s['sector']}</div>
  <div class="sector-mult" style="color:{bc}">{mult_disp} ATR</div>
  <div class="sector-sub">
    <span style="color:{chg_col}">{sgn}{s['day_chg']}%</span>
    &nbsp;·&nbsp; {s['etf']} ${s['price']:.0f}
  </div>
  <div class="sector-bar">
    <div class="sector-bar-fill" style="width:{bp}%;background:{bc}"></div>
  </div>
</div>"""
        sector_html += "</div>"
        st.markdown(sector_html, unsafe_allow_html=True)
        top = sectors[0]
        others = [s["sector"] for s in sectors[1:] if s["mult"] >= 5]
        others_txt = (", ".join(others[:3])) if others else "none"
        st.markdown(f"""
<p style="font-family:'Geist Mono',monospace;font-size:0.62rem;color:#607080;margin:0.4rem 0 1rem">
◈ <b style="color:#e2e8f0">{top['sector']}</b> is the most extended sector at
<b style="color:#f59e0b">{top['mult']}× ATR</b> from its SMA{sma_period}.
Also elevated: {others_txt}
</p>""", unsafe_allow_html=True)

```
# ── Setup-specific controls ──────────────────────────────────────────────
ps_c1, ps_c2, ps_c3, ps_c4 = st.columns(4)
min_atr_mult = ps_c1.number_input("Min ATR Multiple (×)", value=10.0, step=0.5, min_value=0.5, key="ps_atr_mult")
sma_period   = ps_c2.number_input("SMA Period",            value=50,   step=5,   min_value=5, max_value=200, key="ps_sma_period")
atr_period   = ps_c3.number_input("ATR Period",            value=14,   step=1,   min_value=5, max_value=50,  key="ps_atr_period")

ps_btn_col, ps_dl_col, _ = st.columns([1, 1, 7])
run_ps = ps_btn_col.button("▶  RUN SCAN", key="run_ps")

_show_chart_panel("ps")

if run_ps:
    results_ps = _run_phase_ui(
        lambda p1_cb, p2_cb: run_two_phase_scan(
            min_price, min_atr_mult,
            int(sma_period), int(atr_period),
            asset_filter, exchange_filter,
            workers, int(min_vol), mcap_tiers,
            p1_cb, p2_cb,
        ),
        {},
        "results_ps",
    )

if "results_ps" in st.session_state:
    results  = st.session_state["results_ps"]
    scan_ts  = st.session_state.get("results_ps_ts", "")
    n_hits   = len(results)

    top_mult  = f"{results[0]['atr_mult']}×" if results else "—"
    n_etf_hit = sum(1 for r in results if r["is_etf"])
    n_stk_hit = n_hits - n_etf_hit
    p1_count  = st.session_state.get("results_ps_p1n", "—")

    st.markdown(f"""
```

<div class="metric-row">
  <div class="metric-box hi"><div class="metric-label">Confirmed Hits</div>
    <div class="metric-value amber">{n_hits}</div>
    <div class="metric-sub">{scan_ts}</div></div>
  <div class="metric-box"><div class="metric-label">Peak Extension</div>
    <div class="metric-value">{top_mult}</div>
    <div class="metric-sub">highest confirmed ATR×</div></div>
  <div class="metric-box"><div class="metric-label">ETF Hits</div>
    <div class="metric-value">{n_etf_hit}</div>
    <div class="metric-sub">incl. leveraged ETFs</div></div>
  <div class="metric-box"><div class="metric-label">TV Candidates</div>
    <div class="metric-value">{p1_count}</div>
    <div class="metric-sub">Phase 1 pre-screen</div></div>
</div>""", unsafe_allow_html=True)

```
    if results:
        df_exp = pd.DataFrame(results)
        ps_dl_col.download_button("↓ CSV", data=df_exp.to_csv(index=False).encode(),
            file_name=f"ps_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", mime="text/csv")

    if not results:
        st.markdown("""
```

<div class="empty-state">
  <div class="empty-icon">◈</div>
  <div class="empty-text">No confirmed parabolic short candidates</div>
  <div class="empty-hint">Try lowering Min ATR Multiple or broadening universe filters</div>
</div>""", unsafe_allow_html=True)
        else:
            def atr_cls(m):
                if m >= 15: return "atr-extreme"
                if m >= 10: return "atr-high"
                return "atr-norm"

```
        if "chart_ticker_ps" not in st.session_state:
            st.session_state["chart_ticker_ps"]   = None
            st.session_state["chart_exchange_ps"] = None

        COLS = 3
        for i in range(0, len(results), COLS):
            chunk = results[i:i + COLS]
            cols  = st.columns(COLS)
            for col, r in zip(cols, chunk):
                day_chg_val  = round(float(r["day_chg"]), 2)
                chg_cls      = "pos" if day_chg_val >= 0 else "neg"
                chg_sign     = "+" if day_chg_val >= 0 else ""
                type_lbl     = "ETF" if r["is_etf"] else "STOCK"
                type_cls     = "tag-etf" if r["is_etf"] else "tag-stock"
                gain_5d_val  = round(float(r["gain_5d"]), 1)
                gain_cls     = "pos" if gain_5d_val >= 0 else "neg"
                gain_sign    = "+" if gain_5d_val >= 0 else ""
                rvol_cls     = "warn" if r["rel_vol"] >= 2 else ""
                streak       = int(r["consec_days"])
                badge_day1   = '<span class="tag tag-day1">⚠ DAY 1</span>' if r["is_day1"] else ""
                badge_streak = f'<span class="tag tag-streak">🔥 {streak}d</span>' if streak >= 3 else ""
                badge_rvol   = f'<span class="tag tag-rvol">RVOL {r["rel_vol"]}×</span>' if r["rel_vol"] >= 1.5 else ""
                atr_badge    = atr_cls(r["atr_mult"])
                btn_key      = f"ps_chart_{r['ticker']}_{i}"
                col.markdown(f"""
```

<div class="card">
  <span class="atr-badge {atr_badge}">{r['atr_mult']}×</span>
  <div class="card-ticker">{r['ticker']}</div>
  <div class="card-price">${r['price']:,.2f}</div>
  <div class="card-divider"></div>
  <div class="card-stats">
    <div><span class="stat-k">Day Chg</span><span class="stat-v {chg_cls}">{chg_sign}{day_chg_val}%</span></div>
    <div><span class="stat-k">vs SMA{sma_period}</span><span class="stat-v pos">+{r['pct_sma']}%</span></div>
    <div><span class="stat-k">ATR%</span><span class="stat-v">{r['atr_pct']}%</span></div>
    <div><span class="stat-k">Avg Vol</span><span class="stat-v">{r['avg_vol']}</span></div>
  </div>
  <div class="signal-row">
    <div class="sig-cell"><span class="sig-label">5D Gain</span><span class="sig-val {gain_cls}">{gain_sign}{gain_5d_val}%</span></div>
    <div class="sig-cell"><span class="sig-label">Rel Vol</span><span class="sig-val {rvol_cls}">{r['rel_vol']}×</span></div>
    <div class="sig-cell"><span class="sig-label">Streak</span><span class="sig-val warn">{streak}d ↑</span></div>
  </div>
  <div class="card-tags">
    <span class="tag {type_cls}">{type_lbl}</span>
    <span class="tag tag-exch">{r['exchange']}</span>
    {badge_day1}{badge_streak}{badge_rvol}
  </div>
</div>""", unsafe_allow_html=True)
                    if col.button(f"📈  {r['ticker']}", key=btn_key, use_container_width=True):
                        st.session_state["chart_ticker_ps"]   = r["ticker"]
                        st.session_state["chart_exchange_ps"] = r["exchange"]
                        st.rerun()

```
        with st.expander(f"▸  Full Results  ({n_hits} rows)"):
            disp = pd.DataFrame(results).rename(columns={
                "ticker": "Ticker", "exchange": "Exchange", "is_etf": "ETF",
                "price": "Price", "atr_mult": "ATR×", "pct_sma": "% Above SMA (B)",
                "day_chg": "Day Chg %", "avg_vol": "Avg Volume",
                "consec_days": "Streak (days)", "gain_5d": "5D Gain %",
                "gain_1m": "1M Gain %", "rel_vol": "Rel Vol",
                "tv_gap": "Gap %", "is_day1": "Day 1?",
            })
            st.dataframe(disp, use_container_width=True, hide_index=True)
else:
    st.markdown("""
```

<div class="empty-state" style="margin-top:3rem">
  <div class="empty-icon">📉</div>
  <div class="empty-text">Parabolic Short Scanner</div>
  <div class="empty-hint">Finds stocks extended 7–15× ATR from their SMA50 · classic rubber-band reversal setup</div>
</div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════

# TAB 2 — EPISODIC PIVOT

# ══════════════════════════════════════════════════════════════════════════════

with tab_ep:
_status_row(“Episodic Pivot”, “yfinance enrich”)

```
ep_c1, ep_c2, _ = st.columns([1, 1, 5])
min_gap_ep = ep_c1.number_input("Min Gap %", value=10.0, step=1.0, min_value=3.0, key="ep_gap")
ep_btn_col, ep_dl_col, _ = st.columns([1, 1, 7])
run_ep = ep_btn_col.button("▶  RUN SCAN", key="run_ep")

_show_chart_panel("ep")

if run_ep:
    results_ep = _run_phase_ui(
        lambda p1_cb, p2_cb: run_ep_scan(
            min_gap_ep, min_price, asset_filter, exchange_filter,
            int(min_vol), mcap_tiers, workers, p1_cb, p2_cb,
        ),
        {},
        "results_ep",
    )

if "results_ep" in st.session_state:
    results  = st.session_state["results_ep"]
    scan_ts  = st.session_state.get("results_ep_ts", "")
    n_hits   = len(results)
    p1_count = st.session_state.get("results_ep_p1n", "—")

    top_gap   = f"{results[0]['gap_pct']}%" if results else "—"
    top_rvol  = f"{results[0]['rel_vol']}×" if results else "—"
    neglected = sum(1 for r in results if r.get("neglected"))

    st.markdown(f"""
```

<div class="metric-row">
  <div class="metric-box hi"><div class="metric-label">EP Signals</div>
    <div class="metric-value amber">{n_hits}</div>
    <div class="metric-sub">{scan_ts}</div></div>
  <div class="metric-box"><div class="metric-label">Biggest Gap</div>
    <div class="metric-value">{top_gap}</div>
    <div class="metric-sub">gap at open today</div></div>
  <div class="metric-box"><div class="metric-label">Peak Rel Vol</div>
    <div class="metric-value">{top_rvol}</div>
    <div class="metric-sub">vs 10-day avg</div></div>
  <div class="metric-box"><div class="metric-label">Neglected Stocks</div>
    <div class="metric-value">{neglected}</div>
    <div class="metric-sub">was sideways → ideal EP</div></div>
</div>""", unsafe_allow_html=True)

```
    if results:
        df_exp = pd.DataFrame(results)
        ep_dl_col.download_button("↓ CSV", data=df_exp.to_csv(index=False).encode(),
            file_name=f"ep_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", mime="text/csv")

    if not results:
        st.markdown("""
```

<div class="empty-state">
  <div class="empty-icon">⚡</div>
  <div class="empty-text">No Episodic Pivots found today</div>
  <div class="empty-hint">Best results during earnings season · try lowering Min Gap %</div>
</div>""", unsafe_allow_html=True)
        else:
            if "chart_ticker_ep" not in st.session_state:
                st.session_state["chart_ticker_ep"]   = None
                st.session_state["chart_exchange_ep"] = None

```
        COLS = 3
        for i in range(0, len(results), COLS):
            chunk = results[i:i + COLS]
            cols  = st.columns(COLS)
            for col, r in zip(cols, chunk):
                gap_val   = r["gap_pct"]
                rvol_val  = r["rel_vol"]
                day_chg   = round(float(r["day_chg"]), 2)
                chg_cls   = "pos" if day_chg >= 0 else "neg"
                chg_sign  = "+" if day_chg >= 0 else ""
                type_lbl  = "ETF" if r["is_etf"] else "STOCK"
                type_cls  = "tag-etf" if r["is_etf"] else "tag-stock"
                ep_score  = r["ep_score"]
                score_col = "#34d399" if ep_score >= 20 else "#f59e0b" if ep_score >= 10 else "#607080"
                neglect_b = '<span class="tag tag-streak">🏆 NEGLECTED</span>' if r.get("neglected") else ""
                btn_key   = f"ep_chart_{r['ticker']}_{i}"
                col.markdown(f"""
```

<div class="card">
  <span class="atr-badge atr-norm" style="background:rgba(99,102,241,0.15);color:#818cf8;border-color:#4f46e5">EP</span>
  <div class="card-ticker">{r['ticker']}</div>
  <div class="card-price">${r['price']:,.2f}</div>
  <div class="card-divider"></div>
  <div class="card-stats">
    <div><span class="stat-k">Gap</span><span class="stat-v pos">+{gap_val}%</span></div>
    <div><span class="stat-k">Day Chg</span><span class="stat-v {chg_cls}">{chg_sign}{day_chg}%</span></div>
    <div><span class="stat-k">Rel Vol</span><span class="stat-v warn">{rvol_val}×</span></div>
    <div><span class="stat-k">3M Prior</span><span class="stat-v">{r['gain_3m']}%</span></div>
  </div>
  <div class="signal-row">
    <div class="sig-cell"><span class="sig-label">EP Score</span><span class="sig-val" style="color:{score_col}">{ep_score}</span></div>
    <div class="sig-cell"><span class="sig-label">6M Perf</span><span class="stat-v pos">{r['gain_6m']}%</span></div>
    <div class="sig-cell"><span class="sig-label">Streak</span><span class="sig-val">{r['consec_days']}d ↑</span></div>
  </div>
  <div class="card-tags">
    <span class="tag {type_cls}">{type_lbl}</span>
    <span class="tag tag-exch">{r['exchange']}</span>
    {neglect_b}
  </div>
</div>""", unsafe_allow_html=True)
                    if col.button(f"📈  {r['ticker']}", key=btn_key, use_container_width=True):
                        st.session_state["chart_ticker_ep"]   = r["ticker"]
                        st.session_state["chart_exchange_ep"] = r["exchange"]
                        st.rerun()

```
        with st.expander(f"▸  Full Results  ({n_hits} rows)"):
            disp = pd.DataFrame(results).rename(columns={
                "ticker": "Ticker", "exchange": "Exchange", "is_etf": "ETF",
                "price": "Price", "gap_pct": "Gap %", "rel_vol": "Rel Vol",
                "day_chg": "Day Chg %", "gain_3m": "3M Prior %",
                "gain_6m": "6M %", "ep_score": "EP Score",
                "neglected": "Was Neglected", "consec_days": "Streak",
            })
            st.dataframe(disp, use_container_width=True, hide_index=True)
else:
    st.markdown("""
```

<div class="empty-state" style="margin-top:3rem">
  <div class="empty-icon">⚡</div>
  <div class="empty-text">Episodic Pivot Scanner</div>
  <div class="empty-hint">Finds stocks gapping 10%+ on massive volume · best run during earnings season</div>
</div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════

# TAB 3 — MOMENTUM BREAKOUT

# ══════════════════════════════════════════════════════════════════════════════

with tab_bo:
_status_row(“Momentum Breakout”, “yfinance enrich”)

```
bo_c1, bo_c2, _ = st.columns([1, 1, 5])
min_perf_bo = bo_c1.number_input("Min 1M Gain %", value=25.0, step=5.0, min_value=5.0, key="bo_perf")
bo_btn_col, bo_dl_col, _ = st.columns([1, 1, 7])
run_bo = bo_btn_col.button("▶  RUN SCAN", key="run_bo")

_show_chart_panel("bo")

if run_bo:
    results_bo = _run_phase_ui(
        lambda p1_cb, p2_cb: run_breakout_scan(
            min_perf_bo, min_price, asset_filter, exchange_filter,
            int(min_vol), mcap_tiers, workers, p1_cb, p2_cb,
        ),
        {},
        "results_bo",
    )

if "results_bo" in st.session_state:
    results  = st.session_state["results_bo"]
    scan_ts  = st.session_state.get("results_bo_ts", "")
    n_hits   = len(results)
    p1_count = st.session_state.get("results_bo_p1n", "—")

    top_score = f"{results[0]['setup_score']}" if results else "—"
    tight     = sum(1 for r in results if (r.get("range_tightness") or 99) < 3)
    near_ma   = sum(1 for r in results if (r.get("ma_proximity") or 99) < 3)

    st.markdown(f"""
```

<div class="metric-row">
  <div class="metric-box hi"><div class="metric-label">Setups Found</div>
    <div class="metric-value amber">{n_hits}</div>
    <div class="metric-sub">{scan_ts}</div></div>
  <div class="metric-box"><div class="metric-label">Top Setup Score</div>
    <div class="metric-value">{top_score}</div>
    <div class="metric-sub">tightness + MA proximity</div></div>
  <div class="metric-box"><div class="metric-label">Tight Bases</div>
    <div class="metric-value">{tight}</div>
    <div class="metric-sub">range &lt;3% daily avg</div></div>
  <div class="metric-box"><div class="metric-label">Near MA</div>
    <div class="metric-value">{near_ma}</div>
    <div class="metric-sub">within 3% of 10/20 EMA</div></div>
</div>""", unsafe_allow_html=True)

```
    if results:
        df_exp = pd.DataFrame(results)
        bo_dl_col.download_button("↓ CSV", data=df_exp.to_csv(index=False).encode(),
            file_name=f"bo_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", mime="text/csv")

    if not results:
        st.markdown("""
```

<div class="empty-state">
  <div class="empty-icon">🚀</div>
  <div class="empty-text">No Momentum Breakout setups found</div>
  <div class="empty-hint">Try lowering Min 1M Gain % or broadening universe filters</div>
</div>""", unsafe_allow_html=True)
        else:
            if "chart_ticker_bo" not in st.session_state:
                st.session_state["chart_ticker_bo"]   = None
                st.session_state["chart_exchange_bo"] = None

```
        COLS = 3
        for i in range(0, len(results), COLS):
            chunk = results[i:i + COLS]
            cols  = st.columns(COLS)
            for col, r in zip(cols, chunk):
                day_chg   = round(float(r["day_chg"]), 2)
                chg_cls   = "pos" if day_chg >= 0 else "neg"
                chg_sign  = "+" if day_chg >= 0 else ""
                type_lbl  = "ETF" if r["is_etf"] else "STOCK"
                type_cls  = "tag-etf" if r["is_etf"] else "tag-stock"
                sc        = r["setup_score"]
                score_col = "#34d399" if sc >= 7 else "#f59e0b" if sc >= 4 else "#607080"
                tight_val = r.get("range_tightness") or 0
                tight_cls = "pos" if tight_val < 3 else "warn" if tight_val < 6 else "neg"
                dist20    = r.get("dist_20") or 0
                dist_cls  = "pos" if abs(dist20) < 3 else "warn" if abs(dist20) < 8 else "neg"
                btn_key   = f"bo_chart_{r['ticker']}_{i}"
                col.markdown(f"""
```

<div class="card">
  <span class="atr-badge atr-norm" style="background:rgba(52,211,153,0.12);color:#34d399;border-color:#059669">{sc}</span>
  <div class="card-ticker">{r['ticker']}</div>
  <div class="card-price">${r['price']:,.2f}</div>
  <div class="card-divider"></div>
  <div class="card-stats">
    <div><span class="stat-k">1M Gain</span><span class="stat-v pos">+{r['gain_1m']}%</span></div>
    <div><span class="stat-k">3M Gain</span><span class="stat-v pos">+{r['gain_3m']}%</span></div>
    <div><span class="stat-k">Day Chg</span><span class="stat-v {chg_cls}">{chg_sign}{day_chg}%</span></div>
    <div><span class="stat-k">vs SMA20</span><span class="stat-v {dist_cls}">{dist20:+.1f}%</span></div>
  </div>
  <div class="signal-row">
    <div class="sig-cell"><span class="sig-label">Tightness</span><span class="sig-val {tight_cls}">{tight_val}%</span></div>
    <div class="sig-cell"><span class="sig-label">Rel Vol</span><span class="sig-val">{r['rel_vol']}×</span></div>
    <div class="sig-cell"><span class="sig-label">Streak</span><span class="sig-val">{r['consec_days']}d ↑</span></div>
  </div>
  <div class="card-tags">
    <span class="tag {type_cls}">{type_lbl}</span>
    <span class="tag tag-exch">{r['exchange']}</span>
  </div>
</div>""", unsafe_allow_html=True)
                    if col.button(f"📈  {r['ticker']}", key=btn_key, use_container_width=True):
                        st.session_state["chart_ticker_bo"]   = r["ticker"]
                        st.session_state["chart_exchange_bo"] = r["exchange"]
                        st.rerun()

```
        with st.expander(f"▸  Full Results  ({n_hits} rows)"):
            disp = pd.DataFrame(results).rename(columns={
                "ticker": "Ticker", "exchange": "Exchange", "is_etf": "ETF",
                "price": "Price", "gain_1m": "1M %", "gain_3m": "3M %",
                "gain_6m": "6M %", "day_chg": "Day Chg %",
                "dist_10": "vs SMA10 %", "dist_20": "vs SMA20 %",
                "dist_50": "vs SMA50 %", "range_tightness": "Range Tight %",
                "rel_vol": "Rel Vol", "setup_score": "Setup Score",
            })
            st.dataframe(disp, use_container_width=True, hide_index=True)
else:
    st.markdown("""
```

<div class="empty-state" style="margin-top:3rem">
  <div class="empty-icon">🚀</div>
  <div class="empty-text">Momentum Breakout Scanner</div>
  <div class="empty-hint">Finds stocks in tight consolidation after big moves · surfing 10/20 MA · ready to break</div>
</div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════

# TAB 4 — PLAYBOOK (GUIDE)

# ══════════════════════════════════════════════════════════════════════════════

# ══════════════════════════════════════════════════════════════════════════════

# TAB 4 — PARABOLIC LONG

# ══════════════════════════════════════════════════════════════════════════════

with tab_pl:
_status_row(“Parabolic Long”, “yfinance enrich”)

```
pl_c1, pl_c2, _ = st.columns([1, 1, 5])
min_drop_pl = pl_c1.number_input("Min 5D Drop %", value=30.0, step=5.0, min_value=10.0, key="pl_drop",
                                  help="Stock must be down at least this much in 5 days")
pl_btn_col, pl_dl_col, _ = st.columns([1, 1, 7])
run_pl = pl_btn_col.button("▶  RUN SCAN", key="run_pl")

_show_chart_panel("pl")

if run_pl:
    results_pl = _run_phase_ui(
        lambda p1_cb, p2_cb: run_parabolic_long_scan(
            min_drop_pl, min_price, asset_filter, exchange_filter,
            int(min_vol), mcap_tiers, workers, p1_cb, p2_cb,
        ),
        {},
        "results_pl",
    )

if "results_pl" in st.session_state:
    results  = st.session_state["results_pl"]
    scan_ts  = st.session_state.get("results_pl_ts", "")
    n_hits   = len(results)
    p1_count = st.session_state.get("results_pl_p1n", "—")

    top_drop  = f"{results[0]['drop_5d']}%" if results else "—"
    top_score = f"{results[0]['bounce_score']}" if results else "—"
    coiled    = sum(1 for r in results if r["bounce_score"] >= 7)

    st.markdown(f"""
```

<div class="metric-row">
  <div class="metric-box hi"><div class="metric-label">Bounce Candidates</div>
    <div class="metric-value amber">{n_hits}</div>
    <div class="metric-sub">{scan_ts}</div></div>
  <div class="metric-box"><div class="metric-label">Sharpest Drop</div>
    <div class="metric-value">{top_drop}</div>
    <div class="metric-sub">5-day collapse</div></div>
  <div class="metric-box"><div class="metric-label">Top Bounce Score</div>
    <div class="metric-value">{top_score}</div>
    <div class="metric-sub">speed × streak × vol</div></div>
  <div class="metric-box"><div class="metric-label">Highly Coiled</div>
    <div class="metric-value">{coiled}</div>
    <div class="metric-sub">score ≥ 7 / 10</div></div>
</div>""", unsafe_allow_html=True)

```
    if results:
        df_exp = pd.DataFrame(results)
        pl_dl_col.download_button("↓ CSV", data=df_exp.to_csv(index=False).encode(),
            file_name=f"pl_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", mime="text/csv")

    if not results:
        st.markdown("""
```

<div class="empty-state">
  <div class="empty-icon">📈</div>
  <div class="empty-text">No Parabolic Long candidates today</div>
  <div class="empty-hint">Try lowering Min 5D Drop % or waiting for a market sell-off day</div>
</div>""", unsafe_allow_html=True)
        else:
            if "chart_ticker_pl" not in st.session_state:
                st.session_state["chart_ticker_pl"]   = None
                st.session_state["chart_exchange_pl"] = None

```
        COLS = 3
        for i in range(0, len(results), COLS):
            chunk = results[i:i + COLS]
            cols  = st.columns(COLS)
            for col, r in zip(cols, chunk):
                day_chg   = round(float(r["day_chg"]), 2)
                chg_cls   = "pos" if day_chg >= 0 else "neg"
                chg_sign  = "+" if day_chg >= 0 else ""
                drop_val  = r["drop_5d"]
                sc        = r["bounce_score"]
                score_col = "#34d399" if sc >= 7 else "#f59e0b" if sc >= 4 else "#607080"
                type_lbl  = "ETF" if r["is_etf"] else "STOCK"
                type_cls  = "tag-etf" if r["is_etf"] else "tag-stock"
                dfh       = r.get("drop_from_high")
                dfh_str   = f"{dfh}%" if dfh is not None else "N/A"
                dist20    = r.get("dist_20") or 0
                dist_cls  = "neg" if dist20 < -5 else "warn" if dist20 < 0 else "pos"
                high_score = sc >= 7
                badge_coil = '<span class="tag tag-streak">🔥 COILED</span>' if high_score else ""
                btn_key   = f"pl_chart_{r['ticker']}_{i}"
                col.markdown(f"""
```

<div class="card">
  <span class="atr-badge atr-norm" style="background:rgba(52,211,153,0.12);color:#34d399;border-color:#059669">{sc}</span>
  <div class="card-ticker">{r['ticker']}</div>
  <div class="card-price">${r['price']:,.2f}</div>
  <div class="card-divider"></div>
  <div class="card-stats">
    <div><span class="stat-k">5D Drop</span><span class="stat-v neg">{drop_val}%</span></div>
    <div><span class="stat-k">Today</span><span class="stat-v {chg_cls}">{chg_sign}{day_chg}%</span></div>
    <div><span class="stat-k">Rel Vol</span><span class="stat-v warn">{r['rel_vol']}×</span></div>
    <div><span class="stat-k">vs SMA20</span><span class="stat-v {dist_cls}">{dist20:+.1f}%</span></div>
  </div>
  <div class="signal-row">
    <div class="sig-cell"><span class="sig-label">Bounce Score</span><span class="sig-val" style="color:{score_col}">{sc}</span></div>
    <div class="sig-cell"><span class="sig-label">Down Days</span><span class="sig-val neg">{r['consec_down']}d ↓</span></div>
    <div class="sig-cell"><span class="sig-label">From High</span><span class="sig-val neg">{dfh_str}</span></div>
  </div>
  <div class="card-tags">
    <span class="tag {type_cls}">{type_lbl}</span>
    <span class="tag tag-exch">{r['exchange']}</span>
    {badge_coil}
  </div>
</div>""", unsafe_allow_html=True)
                    if col.button(f"📈  {r['ticker']}", key=btn_key, use_container_width=True):
                        st.session_state["chart_ticker_pl"]   = r["ticker"]
                        st.session_state["chart_exchange_pl"] = r["exchange"]
                        st.rerun()

```
        with st.expander(f"▸  Full Results  ({n_hits} rows)"):
            disp = pd.DataFrame(results).rename(columns={
                "ticker": "Ticker", "exchange": "Exchange", "is_etf": "ETF",
                "price": "Price", "day_chg": "Day Chg %",
                "drop_5d": "5D Drop %", "drop_1m": "1M Drop %",
                "drop_from_high": "Drop from High %",
                "consec_down": "Down Days", "rel_vol": "Rel Vol",
                "avg_vol": "Avg Volume", "bounce_score": "Bounce Score",
                "dist_10": "vs SMA10 %", "dist_20": "vs SMA20 %",
            })
            st.dataframe(disp, use_container_width=True, hide_index=True)
else:
    st.markdown("""
```

<div class="empty-state" style="margin-top:3rem">
  <div class="empty-icon">📈</div>
  <div class="empty-text">Parabolic Long Scanner</div>
  <div class="empty-hint">Finds stocks collapsed 30%+ in 5 days — first green day bounce. Entry on opening range highs. Targets 50–100%.</div>
</div>""", unsafe_allow_html=True)

with tab_guide:
st.markdown(”””

<style>
.pb-hero {
  background: linear-gradient(135deg, #0e1114 0%, #111827 100%);
  border: 1px solid #1e2d3d;
  border-radius: 10px;
  padding: 2rem 2.5rem;
  margin-bottom: 2rem;
  position: relative;
  overflow: hidden;
}
.pb-hero::before {
  content: '';
  position: absolute;
  top: -40px; right: -40px;
  width: 200px; height: 200px;
  background: radial-gradient(circle, rgba(245,158,11,0.08) 0%, transparent 70%);
  pointer-events: none;
}
.pb-hero-title {
  font-family: 'Geist Mono', monospace;
  font-size: 1.5rem; font-weight: 700;
  color: #e2e8f0; letter-spacing: -0.02em;
  margin-bottom: 0.4rem;
}
.pb-hero-sub {
  font-family: 'DM Sans', sans-serif;
  font-size: 0.85rem; color: #607080;
  line-height: 1.6;
}
.pb-stat-row {
  display: grid; grid-template-columns: repeat(4, 1fr);
  gap: 0.75rem; margin: 1.5rem 0;
}
.pb-stat {
  background: #080a0c;
  border: 1px solid #1a2332;
  border-radius: 6px; padding: 0.8rem;
  text-align: center;
}
.pb-stat-num {
  font-family: 'Geist Mono', monospace;
  font-size: 1.5rem; font-weight: 700; color: #f59e0b;
}
.pb-stat-lbl {
  font-family: 'DM Sans', sans-serif;
  font-size: 0.65rem; color: #3d4f6b;
  text-transform: uppercase; letter-spacing: 0.1em;
}
.pb-setup-card {
  background: #080a0c;
  border: 1px solid #1a2332;
  border-left: 3px solid;
  border-radius: 8px; padding: 1.5rem 1.8rem;
  margin-bottom: 1.5rem;
}
.pb-setup-card.ps { border-left-color: #f87171; }
.pb-setup-card.ep { border-left-color: #818cf8; }
.pb-setup-card.bo { border-left-color: #34d399; }
.pb-setup-title {
  font-family: 'Geist Mono', monospace;
  font-size: 1rem; font-weight: 700; color: #e2e8f0;
  margin-bottom: 0.2rem;
}
.pb-setup-tagline {
  font-family: 'DM Sans', sans-serif;
  font-size: 0.78rem; color: #607080;
  margin-bottom: 1rem;
}
.pb-rule-grid {
  display: grid; grid-template-columns: 1fr 1fr;
  gap: 0.6rem 1.5rem;
}
.pb-rule {
  display: flex; gap: 0.6rem; align-items: flex-start;
}
.pb-rule-icon {
  font-family: 'Geist Mono', monospace;
  font-size: 0.65rem; font-weight: 700;
  padding: 0.15rem 0.4rem; border-radius: 3px;
  flex-shrink: 0; margin-top: 0.1rem;
}
.pb-rule-icon.scan  { background: rgba(99,102,241,0.2); color: #818cf8; }
.pb-rule-icon.entry { background: rgba(52,211,153,0.15); color: #34d399; }
.pb-rule-icon.stop  { background: rgba(248,113,113,0.15); color: #f87171; }
.pb-rule-icon.exit  { background: rgba(245,158,11,0.15); color: #f59e0b; }
.pb-rule-icon.avoid { background: rgba(239,68,68,0.1); color: #ef4444; }
.pb-rule-icon.tip   { background: rgba(45,212,191,0.1); color: #2dd4bf; }
.pb-rule-text {
  font-family: 'DM Sans', sans-serif;
  font-size: 0.78rem; color: #8899aa; line-height: 1.5;
}
.pb-rule-text b { color: #c8d5e0; }
.pb-quote {
  background: #0a0d10;
  border-left: 3px solid #f59e0b;
  border-radius: 0 6px 6px 0;
  padding: 0.9rem 1.2rem;
  margin: 1rem 0;
  font-family: 'DM Sans', sans-serif;
  font-size: 0.82rem; color: #8899aa;
  font-style: italic; line-height: 1.6;
}
.pb-quote span { color: #f59e0b; font-style: normal; font-size: 0.65rem; }
.pb-section-hdr {
  font-family: 'Geist Mono', monospace;
  font-size: 0.6rem; font-weight: 700;
  color: #3d4f6b; letter-spacing: 0.16em;
  text-transform: uppercase;
  margin: 0.8rem 0 0.5rem;
  border-bottom: 1px solid #111827;
  padding-bottom: 0.3rem;
}
.pb-formula-box {
  background: #0a0d10;
  border: 1px solid #1e2d3d;
  border-radius: 6px; padding: 1.2rem 1.5rem;
  font-family: 'Geist Mono', monospace;
  font-size: 0.72rem; line-height: 2;
  margin: 1rem 0;
}
.pb-checklist {
  list-style: none; padding: 0; margin: 0.5rem 0;
}
.pb-checklist li {
  display: flex; align-items: flex-start; gap: 0.5rem;
  font-family: 'DM Sans', sans-serif;
  font-size: 0.78rem; color: #8899aa;
  padding: 0.25rem 0; line-height: 1.4;
}
.pb-checklist li::before {
  content: '□';
  color: #2dd4bf; flex-shrink: 0; margin-top: 0.05rem;
}
.pb-checklist li.checked::before { content: '✓'; }
.pb-risk-table {
  width: 100%; border-collapse: collapse;
  font-family: 'Geist Mono', monospace; font-size: 0.7rem;
}
.pb-risk-table th {
  color: #3d4f6b; font-weight: 600; letter-spacing: 0.1em;
  text-transform: uppercase; padding: 0.4rem 0.8rem;
  border-bottom: 1px solid #1a2332; text-align: left;
}
.pb-risk-table td {
  padding: 0.4rem 0.8rem; color: #8899aa;
  border-bottom: 1px solid #0e1114;
}
.pb-risk-table td:first-child { color: #e2e8f0; }
</style>

<div class="pb-hero">
  <div class="pb-hero-title">The Qullamaggie Playbook</div>
  <div class="pb-hero-sub">
    Kristjan Kullamägi turned $9,100 → $82M in 8 years trading 3 simple, timeless setups.
    This guide distils every rule from his blog posts, Swing Trading School videos, and Twitch streams
    into one reference. No fluff — just the rules.
  </div>
  <div class="pb-stat-row">
    <div class="pb-stat"><div class="pb-stat-num">3</div><div class="pb-stat-lbl">Core Setups</div></div>
    <div class="pb-stat"><div class="pb-stat-num">268%</div><div class="pb-stat-lbl">Avg CAGR 2013–19</div></div>
    <div class="pb-stat"><div class="pb-stat-num">25–30%</div><div class="pb-stat-lbl">Win Rate</div></div>
    <div class="pb-stat"><div class="pb-stat-num">10–20×</div><div class="pb-stat-lbl">R/R on winners</div></div>
  </div>
</div>
""", unsafe_allow_html=True)

```
# ── Universal Rules ────────────────────────────────────────────────────────
st.markdown('<div class="pb-section-hdr">Universal Principles — apply to all 3 setups</div>', unsafe_allow_html=True)
st.markdown("""
```

<div class="pb-setup-card bo" style="border-left-color:#2dd4bf">
  <div class="pb-setup-title">Before You Trade Anything</div>
  <div class="pb-setup-tagline">Market conditions first. A mediocre setup in a good market beats a great setup in a bad market.</div>
  <div class="pb-rule-grid">
    <div class="pb-rule">
      <span class="pb-rule-icon scan">MKTCT</span>
      <div class="pb-rule-text"><b>Check market first.</b> 10-day above 20-day, both rising = momentum market. Trade freely. Flat or down = be selective.</div>
    </div>
    <div class="pb-rule">
      <span class="pb-rule-icon scan">STOCK</span>
      <div class="pb-rule-text"><b>Top 1–2% stocks only.</b> Up most over 1M, 3M, 6M. ADR > 5% (average daily range). Min $20M daily dollar volume.</div>
    </div>
    <div class="pb-rule">
      <span class="pb-rule-icon stop">RISK</span>
      <div class="pb-rule-text"><b>Risk 0.25–1% per trade.</b> Never more. Position size 10–20% of account. Max 30% in any one stock overnight.</div>
    </div>
    <div class="pb-rule">
      <span class="pb-rule-icon tip">WIN%</span>
      <div class="pb-rule-text"><b>Expect 25–30% win rate.</b> You lose 7 out of 10. That's fine. Winners must be 10–20× your risk.</div>
    </div>
  </div>
</div>
<div class="pb-quote">
"Most trading problems — entries, stops, discipline, profitability — stem from not having mastered any specific setup. Once you understand a setup in depth, you will never have these issues again."
<span>— Kristjan Kullamägi</span>
</div>
""", unsafe_allow_html=True)

```
# ── Setup 1: Parabolic Short ───────────────────────────────────────────────
st.markdown('<div class="pb-section-hdr">Setup 1 · Parabolic Short (& Long) · already running in Tab 1</div>', unsafe_allow_html=True)
st.markdown("""
```

<div class="pb-setup-card ps">
  <div class="pb-setup-title">📉 Parabolic Short</div>
  <div class="pb-setup-tagline">Stock goes up too far too fast. Physics takes over. You short the euphoria peak.</div>
  <div class="pb-rule-grid">
    <div class="pb-rule">
      <span class="pb-rule-icon scan">SCAN</span>
      <div class="pb-rule-text"><b>ATR Formula:</b> A = ATR÷Price, B = (Price−SMA50)÷SMA50. Multiple = B÷A. Look for 7× minimum, 10–15× = ideal.</div>
    </div>
    <div class="pb-rule">
      <span class="pb-rule-icon scan">QUAL</span>
      <div class="pb-rule-text"><b>Streak 3+ days</b> up in a row. Rel Vol 1.5–3×. Large cap 50–100%+ in days. Small cap 300–1000%+.</div>
    </div>
    <div class="pb-rule">
      <span class="pb-rule-icon entry">ENTRY</span>
      <div class="pb-rule-text"><b>Never short Day 1.</b> Wait for Day 2–3 gap-up. Short opening range lows (5-min) or first red 5-min candle.</div>
    </div>
    <div class="pb-rule">
      <span class="pb-rule-icon entry">ENTRY</span>
      <div class="pb-rule-text"><b>VWAP failure</b> = highest conviction. Stock bounces to VWAP, stalls, fails. That's your entry.</div>
    </div>
    <div class="pb-rule">
      <span class="pb-rule-icon avoid">AVOID</span>
      <div class="pb-rule-text"><b>Never short at day's highs.</b> "That's how you get crushed." Let it roll over first.</div>
    </div>
    <div class="pb-rule">
      <span class="pb-rule-icon stop">STOP</span>
      <div class="pb-rule-text"><b>Stop = day's highs.</b> Tight. Honour it immediately. Target 5–10× R/R. Cover fast, don't get greedy.</div>
    </div>
    <div class="pb-rule">
      <span class="pb-rule-icon exit">EXIT</span>
      <div class="pb-rule-text"><b>Large caps:</b> expect 5–15% down. <b>Mid/small caps:</b> 20–30%+. Cover before they reverse.</div>
    </div>
    <div class="pb-rule">
      <span class="pb-rule-icon tip">LONG</span>
      <div class="pb-rule-text"><b>Parabolic Long:</b> After a stock drops 50–60%+ in days, the bounce can be 50–100%. First green day = entry on ORH.</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

```
# ── Setup 2: Episodic Pivot ────────────────────────────────────────────────
st.markdown('<div class="pb-section-hdr">Setup 2 · Episodic Pivot · running in Tab 2</div>', unsafe_allow_html=True)
st.markdown("""
```

<div class="pb-setup-card ep">
  <div class="pb-setup-title">⚡ Episodic Pivot (EP)</div>
  <div class="pb-setup-tagline">Unexpected news forces institutions to revalue a stock overnight. They can't buy it all in one day — that's your multi-week edge.</div>
  <div class="pb-rule-grid">
    <div class="pb-rule">
      <span class="pb-rule-icon scan">SCAN</span>
      <div class="pb-rule-text"><b>Gap 10%+</b> at open. That's the minimum. Less than 10% = not an EP, even on great earnings.</div>
    </div>
    <div class="pb-rule">
      <span class="pb-rule-icon scan">VOL</span>
      <div class="pb-rule-text"><b>Volume is #1.</b> Stock should trade its entire average daily volume in the first 15–20 minutes. Ideally already huge in pre-market.</div>
    </div>
    <div class="pb-rule">
      <span class="pb-rule-icon tip">IDEAL</span>
      <div class="pb-rule-text"><b>Best EPs:</b> stocks that went sideways 3–6 months before. Neglected stocks with huge catalysts = biggest moves.</div>
    </div>
    <div class="pb-rule">
      <span class="pb-rule-icon scan">FUND</span>
      <div class="pb-rule-text"><b>Earnings EPs:</b> triple-digit YoY EPS/Sales ideal. Big analyst beat + big guidance raise. Many small caps have no analysts — that's fine.</div>
    </div>
    <div class="pb-rule">
      <span class="pb-rule-icon entry">ENTRY</span>
      <div class="pb-rule-text"><b>Opening Range Highs (ORH).</b> Wait for the 1-min candle to form, watch volume closely. Buy when it breaks the 1-min high.</div>
    </div>
    <div class="pb-rule">
      <span class="pb-rule-icon entry">ADD</span>
      <div class="pb-rule-text"><b>Can add on 5-min and 60-min ORH</b> for more size and confirmation. No need to be first. Add through the day if it acts well.</div>
    </div>
    <div class="pb-rule">
      <span class="pb-rule-icon stop">STOP</span>
      <div class="pb-rule-text"><b>Stop = lows of the day.</b> Maximum 1–1.5× ADR or ATR wide. If stop is wider, skip the trade.</div>
    </div>
    <div class="pb-rule">
      <span class="pb-rule-icon exit">EXIT</span>
      <div class="pb-rule-text"><b>Sell 1/3–1/2 after 3–5 days.</b> Move stop to break even. Trail rest with 10-day MA. Exit on first close below 10-day.</div>
    </div>
    <div class="pb-rule">
      <span class="pb-rule-icon avoid">AVOID</span>
      <div class="pb-rule-text"><b>Second EPs.</b> Stock already made a big move, now gaps again. Failure rate is higher and move smaller.</div>
    </div>
    <div class="pb-rule">
      <span class="pb-rule-icon tip">TYPES</span>
      <div class="pb-rule-text">Earnings · FDA decisions · Gov regulation · Contracts · Sector EPs (whole sector moves without specific news)</div>
    </div>
  </div>
</div>
<div class="pb-quote">
"EP is the most infrequent, the one you can get the best risk/reward, and they mostly occur in a concentrated 3–4 week window every quarter. For a working person, this makes the ultimate setup."
<span>— Kristjan Kullamägi</span>
</div>
""", unsafe_allow_html=True)

```
# ── Setup 3: Momentum Breakout ─────────────────────────────────────────────
st.markdown('<div class="pb-section-hdr">Setup 3 · Momentum Breakout · running in Tab 3</div>', unsafe_allow_html=True)
st.markdown("""
```

<div class="pb-setup-card bo">
  <div class="pb-setup-title">🚀 Momentum Breakout (High Tight Flag)</div>
  <div class="pb-setup-tagline">Stocks move in staircase steps. You buy the beginning of the next step, just as it forms.</div>
  <div class="pb-rule-grid">
    <div class="pb-rule">
      <span class="pb-rule-icon scan">SCAN</span>
      <div class="pb-rule-text"><b>Top 1–2% gainers</b> over 1M, 3M, 6M. This identifies the leaders. ADR > 5%. Volume > $20M daily.</div>
    </div>
    <div class="pb-rule">
      <span class="pb-rule-icon scan">PHASE1</span>
      <div class="pb-rule-text"><b>Big first leg:</b> 30–100%+ move in past 1–3 months. The more explosive the first leg, the more powerful the next leg.</div>
    </div>
    <div class="pb-rule">
      <span class="pb-rule-icon scan">PHASE2</span>
      <div class="pb-rule-text"><b>Tight consolidation:</b> Higher lows. Range narrows. "Surfs" the rising 10- and 20-day MA. 2 weeks to 2 months long.</div>
    </div>
    <div class="pb-rule">
      <span class="pb-rule-icon tip">5-STAR</span>
      <div class="pb-rule-text"><b>Best setups show relative strength.</b> Market sells off, this stock won't break. That's institutional accumulation.</div>
    </div>
    <div class="pb-rule">
      <span class="pb-rule-icon entry">ENTRY</span>
      <div class="pb-rule-text"><b>Opening Range Highs.</b> Wait for the range top to break on the 1-min, 5-min, or 60-min chart. Most breakouts happen in first 30 min.</div>
    </div>
    <div class="pb-rule">
      <span class="pb-rule-icon entry">PRICE</span>
      <div class="pb-rule-text"><b>Best buy zone:</b> half to two-thirds of the ATR above the breakout point. Don't chase beyond 1× ATR.</div>
    </div>
    <div class="pb-rule">
      <span class="pb-rule-icon stop">STOP</span>
      <div class="pb-rule-text"><b>Stop = lows of the day.</b> No wider than 1× ADR or ATR. If the range lows are too far, wait for a tighter day.</div>
    </div>
    <div class="pb-rule">
      <span class="pb-rule-icon exit">EXIT</span>
      <div class="pb-rule-text"><b>Sell 1/3–1/2 after 3–5 days.</b> Move stop to break even. Trail rest with 10-day MA. Exit on first close below 10-day.</div>
    </div>
    <div class="pb-rule">
      <span class="pb-rule-icon avoid">AVOID</span>
      <div class="pb-rule-text"><b>Random up days.</b> Needs to be coming off a solid tight range. Low ADR stocks. Long candle the day before the breakout.</div>
    </div>
    <div class="pb-rule">
      <span class="pb-rule-icon tip">HTF</span>
      <div class="pb-rule-text"><b>High Tight Flag variant:</b> first leg 100%+ in days/weeks. Flag only 5–10 sessions. Rarest but most powerful setup.</div>
    </div>
  </div>
</div>
<div class="pb-quote">
"Flag patterns are very powerful — the more powerful the first leg higher, the more powerful the next leg higher will be most of the time."
<span>— Kristjan Kullamägi</span>
</div>
""", unsafe_allow_html=True)

```
# ── Risk Management Table ──────────────────────────────────────────────────
st.markdown('<div class="pb-section-hdr">Risk Management — the same rules across all setups</div>', unsafe_allow_html=True)
st.markdown("""
```

<table class="pb-risk-table">
  <tr><th>Parameter</th><th>Rule</th><th>Why</th></tr>
  <tr><td>Position size</td><td>10–20% of account</td><td>Big enough to matter, small enough to survive</td></tr>
  <tr><td>Max single stock overnight</td><td>30% of account</td><td>Gap risk protection</td></tr>
  <tr><td>Risk per trade</td><td>0.25–1% of account</td><td>Lets you take 100–400 losses before ruin</td></tr>
  <tr><td>Stop width</td><td>≤ 1× ADR or ATR</td><td>Wider stop = R/R gets out of whack</td></tr>
  <tr><td>First partial exit</td><td>Sell 1/3–1/2 after 3–5 days</td><td>Locks in profit, removes pressure</td></tr>
  <tr><td>Move stop</td><td>To break even after first partial</td><td>Now you can't lose on this trade</td></tr>
  <tr><td>Trail remainder</td><td>10-day MA (fast) or 20-day (slow)</td><td>Catches 10–20× R moves</td></tr>
  <tr><td>Final exit trigger</td><td>First CLOSE below 10-day MA</td><td>Intraday dips don't count</td></tr>
</table>
""", unsafe_allow_html=True)

```
# ── ATR Formula ───────────────────────────────────────────────────────────
st.markdown('<div class="pb-section-hdr" style="margin-top:1.5rem">The ATR Extension Formula — how the Parabolic Short scanner works</div>', unsafe_allow_html=True)
st.markdown("""
```

<div class="pb-formula-box">
  <span style="color:#3d4f6b">// Adapted from jfsrev / fred6724 on TradingView</span><br>
  <span style="color:#818cf8">A</span> = ATR(14) ÷ Price &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span style="color:#3d4f6b">← volatility normalised to % of price</span><br>
  <span style="color:#818cf8">B</span> = (Price − SMA50) ÷ SMA50 &nbsp;&nbsp;<span style="color:#3d4f6b">← how far above the 50-MA in %</span><br>
  <span style="color:#f59e0b">Multiple</span> = B ÷ A &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span style="color:#3d4f6b">← how many ATR units above SMA50</span><br><br>
  <span style="color:#2dd4bf">7×</span> &nbsp;&nbsp;→ Start watching · profit-taking zone<br>
  <span style="color:#f59e0b">10×</span> &nbsp;→ Extreme · high reversal probability<br>
  <span style="color:#f87171">15×</span> &nbsp;→ Blow-off / climax top · short aggressively<br><br>
  <span style="color:#3d4f6b">Think of it as a rubber band: the further it stretches from the 50-MA,
  measured in units of its own volatility, the harder the inevitable snap-back.</span>
</div>
""", unsafe_allow_html=True)

```
# ── Study Guide ───────────────────────────────────────────────────────────
st.markdown('<div class="pb-section-hdr" style="margin-top:1.5rem">How to Master a Setup — Kristjan\'s Method</div>', unsafe_allow_html=True)
st.markdown("""
```

<div class="pb-setup-card bo" style="border-left-color:#818cf8">
  <div class="pb-setup-title">The Deep Dive Process</div>
  <div class="pb-setup-tagline">Kristjan built an Evernote database of thousands of historical examples before he ever traded a setup live.</div>
  <ul class="pb-checklist">
    <li>Go through all 6,000+ US stocks on the monthly chart. Look for 100%+ moves.</li>
    <li>For each big mover, pull up the intraday chart. Find the exact day the move started.</li>
    <li>Look up the news catalyst (Briefing.com, SEC filings, company press releases).</li>
    <li>Screenshot it. Log: setup type, catalyst, volume, gap %, MA proximity, outcome.</li>
    <li>Do this for 500–1,000 examples. You will start to see the patterns that actually work.</li>
    <li>Study what the chart looked like the day BEFORE the move. That's your entry signal.</li>
    <li>Study failures too. Know what a bad version of the setup looks like.</li>
    <li>Only after hundreds of examples are you ready to trade it with real size.</li>
  </ul>
</div>
<div class="pb-quote">
"It will take 3–4 earnings seasons to get good at trading EP, 5–6 if you are a moron. For me it probably took 7 or 8."
<span>— Kristjan Kullamägi</span>
</div>
""", unsafe_allow_html=True)
