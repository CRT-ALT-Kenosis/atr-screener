# 📈 ATR Extension Screener

A real-time, mobile-friendly stock and ETF screener that identifies securities
trading at extreme extensions above their moving average — measured in ATR multiples.
Built for identifying parabolic price moves across all US exchanges.

---

## What It Does

Finds stocks and ETFs where:

```
(Close Price − SMA_N) / ATR_N  ≥  threshold
```

- **7×** = classic profit-taking zone
- **10×** = extreme parabolic extension (blow-off tops, short-squeeze events)

---

## Features

- 📱 Mobile-first dark terminal UI
- 🌐 Full US exchange coverage — NASDAQ, NYSE, NYSE Arca (includes SOXL, TQQQ, UPRO, etc.)
- ⚡ Parallel scanning with configurable worker threads
- 🏷️ ETF / Stock type badges with exchange labels
- 📊 Sortable full results table
- 📥 One-tap CSV export

---

## Scan Parameters

| Setting | Default | Description |
|---|---|---|
| Min Price ($) | 100 | Drops symbols below this price |
| Min ATR Multiple | 10× | Extension threshold |
| SMA Period | 50 | Baseline moving average |
| ATR Period | 14 | Volatility lookback (Wilder method) |
| Asset Type | Both | Stocks, ETFs, or both |
| Exchanges | All US | NASDAQ, NYSE, NYSE Arca, etc. |
| Parallel Workers | 6 | Higher = faster, but risks Yahoo rate limits |

---

## Installation (local)

```bash
git clone https://github.com/yourusername/atr-screener
cd atr-screener
pip install -r requirements.txt
streamlit run app.py
```

---

## Deploy — Streamlit Community Cloud (free, permanent)

1. Push this repo to GitHub (public)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub → select repo → set main file: `app.py`
4. **Deploy** — live in ~60 seconds

---

## Deploy — Replit

1. Create a new Python Repl at [replit.com](https://replit.com)
2. Upload `app.py`, `requirements.txt`, `.replit`
3. Hit ▶ Run — dependencies install automatically (~60 sec)
4. Get a public URL from the preview panel

---

## Notes

- ATR uses Wilder's exponential smoothing method (same as IBD / Minervini references)
- Full universe scan (~8,000–10,000 symbols) takes 8–15 min at 6 workers
- **ETFs Only** mode reduces universe to ~2,000–3,000 symbols (~3 min)
- Reduce workers to 4–6 if Yahoo Finance rate-limiting causes missing results

---

## Background

ATR-multiple extensions from the SMA are used by institutional and IBD-style momentum
traders to identify when a stock has moved "too far, too fast." The 7–10× ATR range
historically precedes mean-reversion or consolidation — useful for profit-taking signals
and identifying short candidates.

---

Built with Streamlit · Data via Yahoo Finance · Symbol universe via NASDAQ Trader
