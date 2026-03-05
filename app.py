import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import io
import re
from datetime import datetime

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ATR Extension Screener",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS (dark, trading-terminal aesthetic) ─────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;700&family=IBM+Plex+Sans:wght@300;400;600&display=swap');

:root {
    --bg:        #0a0c0f;
    --bg2:       #111418;
    --bg3:       #181c22;
    --border:    #1f2530;
    --text:      #c8d0dc;
    --muted:     #4a5568;
    --accent:    #00e5ff;
    --green:     #00ff88;
    --red:       #ff4757;
    --yellow:    #ffd700;
    --orange:    #ff8c42;
}

html, body, [class*="css"] {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'IBM Plex Sans', sans-serif;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: var(--bg2) !important;
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] * { color: var(--text) !important; }

/* Main area */
.main .block-container { padding-top: 1.5rem; max-width: 100%; }

/* Header */
.screener-header {
    display: flex; align-items: center; gap: 12px;
    padding: 1.2rem 0 0.5rem 0;
    border-bottom: 1px solid var(--border);
    margin-bottom: 1.5rem;
}
.screener-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: clamp(1.1rem, 3vw, 1.6rem);
    font-weight: 700;
    color: var(--accent);
    letter-spacing: 0.04em;
    margin: 0;
}
.screener-subtitle {
    font-size: 0.75rem;
    color: var(--muted);
    font-family: 'IBM Plex Mono', monospace;
    margin: 0;
}

/* Status bar */
.status-bar {
    display: flex; flex-wrap: wrap; gap: 12px;
    background: var(--bg2); border: 1px solid var(--border);
    border-radius: 6px; padding: 0.6rem 1rem;
    font-family: 'IBM Plex Mono', monospace; font-size: 0.72rem;
    color: var(--muted); margin-bottom: 1rem;
}
.status-item { display: flex; align-items: center; gap: 6px; }
.status-dot  { width: 6px; height: 6px; border-radius: 50%; }
.dot-green   { background: var(--green); box-shadow: 0 0 6px var(--green); }
.dot-yellow  { background: var(--yellow); }
.dot-red     { background: var(--red); }

/* Result cards */
.result-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 12px; margin-top: 1rem;
}
.result-card {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1rem 1.1rem;
    position: relative;
    transition: border-color 0.2s;
}
.result-card:hover { border-color: var(--accent); }
.card-ticker {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.15rem; font-weight: 700;
    color: #fff; letter-spacing: 0.06em;
}
.card-exchange {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem; color: var(--muted);
    text-transform: uppercase;
}
.card-price {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1rem; color: var(--text);
    margin-top: 4px;
}
.atr-badge {
    position: absolute; top: 12px; right: 12px;
    background: rgba(0,229,255,0.12);
    border: 1px solid var(--accent);
    border-radius: 20px;
    padding: 3px 10px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.78rem; font-weight: 700;
    color: var(--accent);
}
.atr-badge.high { background: rgba(255,71,87,0.12); border-color: var(--red); color: var(--red); }
.atr-badge.extreme { background: rgba(255,140,66,0.15); border-color: var(--orange); color: var(--orange); }

.card-stats {
    display: flex; gap: 14px; margin-top: 10px;
    flex-wrap: wrap;
}
.stat { font-size: 0.72rem; font-family: 'IBM Plex Mono', monospace; }
.stat-label { color: var(--muted); display: block; }
.stat-value { color: var(--text); font-weight: 500; }
.stat-value.pos { color: var(--green); }
.stat-value.neg { color: var(--red); }

.type-badge {
    display: inline-block;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.62rem; padding: 2px 7px;
    border-radius: 3px; margin-top: 8px; margin-right: 4px;
    text-transform: uppercase; letter-spacing: 0.08em;
}
.badge-etf  { background: rgba(0,255,136,0.1); color: var(--green); border: 1px solid rgba(0,255,136,0.25); }
.badge-stock{ background: rgba(0,229,255,0.1); color: var(--accent); border: 1px solid rgba(0,229,255,0.25); }

/* Progress bar */
.stProgress > div > div { background-color: var(--accent) !important; }

/* Buttons */
.stButton>button {
    background: transparent !important;
    border: 1px solid var(--accent) !important;
    color: var(--accent) !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.8rem !important;
    border-radius: 4px !important;
    padding: 0.4rem 1rem !important;
    transition: background 0.2s !important;
}
.stButton>button:hover {
    background: rgba(0,229,255,0.1) !important;
}

/* Sliders / selects */
.stSlider label, .stSelectbox label, .stMultiSelect label,
.stRadio label, .stNumberInput label {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.78rem !important;
    color: var(--muted) !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
}

/* Expander */
.streamlit-expanderHeader {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.8rem !important;
    color: var(--muted) !important;
}

/* Dataframe */
.stDataFrame { border: 1px solid var(--border) !important; border-radius: 6px; }

/* Metric */
[data-testid="metric-container"] {
    background: var(--bg2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
    padding: 0.7rem 1rem !important;
}
[data-testid="stMetricLabel"] {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.7rem !important;
    color: var(--muted) !important;
    text-transform: uppercase !important;
}
[data-testid="stMetricValue"] {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 1.3rem !important;
    color: var(--accent) !important;
}

/* Divider */
hr { border-color: var(--border) !important; }

/* No results */
.no-results {
    text-align: center; padding: 3rem 1rem;
    font-family: 'IBM Plex Mono', monospace;
    color: var(--muted); font-size: 0.9rem;
}

/* Scrollbar */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

# ── Helpers ───────────────────────────────────────────────────────────────────

@st.cache_data(ttl=3600)
def fetch_all_us_symbols():
    """Download NASDAQ Trader symbol files covering all US exchanges."""
    symbols = []
    urls = [
        ("https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt", "nasdaq"),
        ("https://www.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt", "other"),
    ]
    for url, src in urls:
        try:
            r = requests.get(url, timeout=15)
            r.raise_for_status()
            df = pd.read_csv(io.StringIO(r.text), sep="|")
            # Drop the trailer row
            df = df[df.iloc[:, 0] != "File Creation Time:"]
            if src == "nasdaq":
                df = df[df["Test Issue"] == "N"]
                col_sym, col_etf, col_exc = "Symbol", "ETF", "Listing Exchange"
                df["Exchange"] = "NASDAQ"
            else:
                df = df[df["Test Issue"] == "N"]
                col_sym, col_etf, col_exc = "ACT Symbol", "ETF", "Exchange"
            df = df.rename(columns={col_sym: "Symbol", col_etf: "IsETF", col_exc: "Exchange"})
            df["IsETF"] = df["IsETF"].astype(str).str.upper() == "Y"
            symbols.append(df[["Symbol", "IsETF", "Exchange"]])
        except Exception as e:
            st.warning(f"Could not fetch {src} symbols: {e}")
    if not symbols:
        return pd.DataFrame(columns=["Symbol", "IsETF", "Exchange"])
    out = pd.concat(symbols, ignore_index=True)
    # Clean: alpha-only, 1-5 chars
    out = out[out["Symbol"].str.match(r"^[A-Z]{1,5}$", na=False)]
    return out.drop_duplicates("Symbol").reset_index(drop=True)


def wilder_atr(high, low, close, period=14):
    """True Wilder smoothed ATR."""
    tr = pd.concat([
        high - low,
        (high - close.shift()).abs(),
        (low  - close.shift()).abs(),
    ], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    return atr


def analyse_ticker(ticker, sma_period=50, atr_period=14, min_price=100.0):
    """Return dict with metrics or None if not qualifying."""
    try:
        df = yf.download(ticker, period="6mo", interval="1d",
                         progress=False, auto_adjust=True)
        if df.empty or len(df) < sma_period + 5:
            return None
        # Flatten MultiIndex if present
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        close = df["Close"].squeeze()
        high  = df["High"].squeeze()
        low   = df["Low"].squeeze()

        last_close = float(close.iloc[-1])
        if last_close < min_price:
            return None

        sma  = close.rolling(sma_period).mean().iloc[-1]
        atr  = wilder_atr(high, low, close, atr_period).iloc[-1]
        if pd.isna(sma) or pd.isna(atr) or atr == 0:
            return None

        atr_mult = (last_close - float(sma)) / float(atr)
        pct_above_sma = (last_close - float(sma)) / float(sma) * 100

        prev_close = float(close.iloc[-2]) if len(close) > 1 else last_close
        day_chg_pct = (last_close - prev_close) / prev_close * 100

        return {
            "ticker":        ticker,
            "price":         round(last_close, 2),
            "atr_mult":      round(atr_mult, 2),
            "sma":           round(float(sma), 2),
            "atr":           round(float(atr), 2),
            "pct_above_sma": round(pct_above_sma, 1),
            "day_chg_pct":   round(day_chg_pct, 2),
        }
    except Exception:
        return None


def run_scan(symbols_df, min_price, min_atr_mult, sma_period, atr_period,
             asset_filter, exchange_filter, workers, progress_cb):
    """Run the full scan with progress updates."""
    # Apply pre-filters
    df = symbols_df.copy()
    if asset_filter == "ETFs Only":
        df = df[df["IsETF"] == True]
    elif asset_filter == "Stocks Only":
        df = df[df["IsETF"] == False]
    if exchange_filter:
        df = df[df["Exchange"].isin(exchange_filter)]

    tickers = df["Symbol"].tolist()
    total = len(tickers)
    results = []
    done = 0

    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(analyse_ticker, t, sma_period, atr_period, min_price): t
                for t in tickers}
        for fut in as_completed(futs):
            done += 1
            progress_cb(done / total, done, total)
            res = fut.result()
            if res and res["atr_mult"] >= min_atr_mult:
                ticker = futs[fut]
                row = symbols_df[symbols_df["Symbol"] == ticker].iloc[0]
                res["is_etf"]   = bool(row["IsETF"])
                res["exchange"] = str(row["Exchange"])
                results.append(res)

    return sorted(results, key=lambda x: x["atr_mult"], reverse=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <p style='font-family:"IBM Plex Mono",monospace;font-size:0.65rem;
    color:#4a5568;text-transform:uppercase;letter-spacing:0.12em;margin-bottom:1rem'>
    ▸ SCAN PARAMETERS</p>
    """, unsafe_allow_html=True)

    min_price    = st.number_input("Min Price ($)", value=100.0, step=10.0, min_value=0.0)
    min_atr_mult = st.number_input("Min ATR Multiple (×)", value=10.0, step=0.5, min_value=0.5)
    sma_period   = st.number_input("SMA Period", value=50, step=5, min_value=5, max_value=200)
    atr_period   = st.number_input("ATR Period", value=14, step=1, min_value=5, max_value=50)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("""
    <p style='font-family:"IBM Plex Mono",monospace;font-size:0.65rem;
    color:#4a5568;text-transform:uppercase;letter-spacing:0.12em;margin-bottom:0.5rem'>
    ▸ UNIVERSE FILTERS</p>
    """, unsafe_allow_html=True)

    asset_filter = st.radio("Asset Type", ["Stocks + ETFs", "ETFs Only", "Stocks Only"], index=0)

    exchange_options = ["NASDAQ", "NYSE", "NYSE Arca", "NYSE American", "BATS", "IEX"]
    exchange_filter  = st.multiselect("Exchanges", exchange_options, default=exchange_options)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("""
    <p style='font-family:"IBM Plex Mono",monospace;font-size:0.65rem;
    color:#4a5568;text-transform:uppercase;letter-spacing:0.12em;margin-bottom:0.5rem'>
    ▸ PERFORMANCE</p>
    """, unsafe_allow_html=True)

    workers = st.slider("Parallel Workers", min_value=1, max_value=15, value=6)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("""
    <p style='font-family:"IBM Plex Mono",monospace;font-size:0.65rem;
    color:#4a5568;text-transform:uppercase;letter-spacing:0.12em;
    margin-bottom:0.4rem'>▸ REFERENCE</p>
    <p style='font-family:"IBM Plex Mono",monospace;font-size:0.68rem;color:#4a5568;line-height:1.6'>
    7× ATR → profit-taking zone<br>
    10× ATR → extreme extension<br>
    Formula: (Close − SMA<sub>N</sub>) / ATR<sub>N</sub>
    </p>
    """, unsafe_allow_html=True)

# ── Main ──────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="screener-header">
  <div>
    <p class="screener-title">📈 ATR EXTENSION SCREENER</p>
    <p class="screener-subtitle">PARABOLIC EXTENSION DETECTOR  ·  ALL US EXCHANGES</p>
  </div>
</div>
""", unsafe_allow_html=True)

# Controls row
col_run, col_dl, col_spacer = st.columns([1, 1, 4])
run_btn = col_run.button("▶  RUN SCAN")

# ── Load symbol universe (cached) ─────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def get_symbols():
    return fetch_all_us_symbols()

with st.spinner("Loading symbol universe…"):
    symbols_df = get_symbols()

total_syms = len(symbols_df)
etf_count  = int(symbols_df["IsETF"].sum())

st.markdown(f"""
<div class="status-bar">
  <span class="status-item"><span class="status-dot dot-green"></span>UNIVERSE LOADED</span>
  <span class="status-item">SYMBOLS: <b style="color:#c8d0dc">{total_syms:,}</b></span>
  <span class="status-item">ETFs: <b style="color:#c8d0dc">{etf_count:,}</b></span>
  <span class="status-item">STOCKS: <b style="color:#c8d0dc">{total_syms - etf_count:,}</b></span>
  <span class="status-item">UPDATED: <b style="color:#c8d0dc">{datetime.now().strftime("%H:%M")}</b></span>
</div>
""", unsafe_allow_html=True)

# ── Run scan ──────────────────────────────────────────────────────────────────
if run_btn:
    st.markdown("---")
    prog_bar   = st.progress(0.0)
    status_txt = st.empty()

    def update_progress(pct, done, total):
        prog_bar.progress(min(pct, 1.0))
        status_txt.markdown(
            f"<span style='font-family:\"IBM Plex Mono\",monospace;font-size:0.75rem;"
            f"color:#4a5568'>SCANNING {done:,} / {total:,}</span>",
            unsafe_allow_html=True,
        )

    with st.spinner(""):
        results = run_scan(
            symbols_df, min_price, min_atr_mult, int(sma_period), int(atr_period),
            asset_filter, exchange_filter, workers, update_progress,
        )

    prog_bar.progress(1.0)
    status_txt.empty()

    st.session_state["results"]    = results
    st.session_state["scan_time"]  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state["scan_params"] = {
        "min_price": min_price, "min_atr_mult": min_atr_mult,
        "sma_period": sma_period, "atr_period": atr_period,
    }

# ── Display results ───────────────────────────────────────────────────────────
if "results" in st.session_state:
    results   = st.session_state["results"]
    scan_time = st.session_state.get("scan_time", "")

    # Summary metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Hits",          len(results))
    m2.metric("Highest ATR×",  f"{results[0]['atr_mult']}×" if results else "—")
    m3.metric("ETF Hits",      sum(1 for r in results if r["is_etf"]))
    m4.metric("Stock Hits",    sum(1 for r in results if not r["is_etf"]))

    # CSV download
    if results:
        df_export = pd.DataFrame(results)
        csv = df_export.to_csv(index=False).encode()
        col_dl.download_button(
            "⬇  CSV",
            data=csv,
            file_name=f"atr_scan_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
        )

    st.markdown(f"<p style='font-family:\"IBM Plex Mono\",monospace;font-size:0.68rem;"
                f"color:#4a5568;margin-top:0.5rem'>SCAN COMPLETED {scan_time}</p>",
                unsafe_allow_html=True)

    if not results:
        st.markdown("""
        <div class="no-results">
            <p style="font-size:2rem">◌</p>
            <p>No symbols match the current criteria.</p>
            <p style="font-size:0.8rem">Try lowering the ATR multiple threshold or adjusting filters.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Card grid
        def badge_class(mult):
            if mult >= 15: return "extreme"
            if mult >= 12: return "high"
            return ""

        cards_html = '<div class="result-grid">'
        for r in results:
            chg_cls  = "pos" if r["day_chg_pct"] >= 0 else "neg"
            chg_sign = "+" if r["day_chg_pct"] >= 0 else ""
            bc       = badge_class(r["atr_mult"])
            type_lbl = "ETF" if r["is_etf"] else "STOCK"
            type_cls = "badge-etf" if r["is_etf"] else "badge-stock"
            cards_html += f"""
            <div class="result-card">
              <span class="atr-badge {bc}">{r['atr_mult']}× ATR</span>
              <div class="card-ticker">{r['ticker']}</div>
              <div class="card-exchange">{r['exchange']}</div>
              <div class="card-price">${r['price']:,.2f}</div>
              <div class="card-stats">
                <div class="stat">
                  <span class="stat-label">DAY CHG</span>
                  <span class="stat-value {chg_cls}">{chg_sign}{r['day_chg_pct']}%</span>
                </div>
                <div class="stat">
                  <span class="stat-label">VS SMA{int(sma_period)}</span>
                  <span class="stat-value pos">+{r['pct_above_sma']}%</span>
                </div>
                <div class="stat">
                  <span class="stat-label">ATR</span>
                  <span class="stat-value">${r['atr']:,.2f}</span>
                </div>
                <div class="stat">
                  <span class="stat-label">SMA{int(sma_period)}</span>
                  <span class="stat-value">${r['sma']:,.2f}</span>
                </div>
              </div>
              <span class="type-badge {type_cls}">{type_lbl}</span>
            </div>
            """
        cards_html += "</div>"
        st.markdown(cards_html, unsafe_allow_html=True)

        # Full table
        with st.expander("▸  FULL RESULTS TABLE"):
            display_df = pd.DataFrame(results).rename(columns={
                "ticker":        "Ticker",
                "exchange":      "Exchange",
                "is_etf":        "ETF",
                "price":         "Price",
                "atr_mult":      "ATR Multiple",
                "sma":           f"SMA{int(sma_period)}",
                "atr":           f"ATR{int(atr_period)}",
                "pct_above_sma": f"% Above SMA{int(sma_period)}",
                "day_chg_pct":   "Day Chg %",
            })
            st.dataframe(display_df, use_container_width=True, hide_index=True)
else:
    st.markdown("""
    <div class="no-results" style="margin-top:3rem">
        <p style="font-size:2.5rem">◈</p>
        <p>Configure parameters in the sidebar and tap <b>RUN SCAN</b></p>
        <p style="font-size:0.8rem;margin-top:0.5rem">
            Full US exchange scan (all NASDAQ, NYSE, NYSE Arca) · leveraged ETFs included
        </p>
    </div>
    """, unsafe_allow_html=True)
