"""
Stock Market Analysis Dashboard
================================
4-panel matplotlib dashboard:
  - Panel 1: Price + Moving Averages (MA5 / MA20 / MA50)
  - Panel 2: Volume
  - Panel 3: RSI (14-period)
  - Panel 4: MACD (12, 26, 9)

Usage:
    python dashboard.py
    python dashboard.py --ticker MSFT --start 2024-01-01 --end 2024-06-30
"""

import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import mysql.connector
from datetime import datetime, timedelta


# ── DB Config ──────────────────────────────────────────────────────────────
DB_CONFIG = {
    "host":     "localhost",
    "user":     "root",
    "password": "",          # set your MySQL password here
    "database": "stock_market",
}


def fetch_data(ticker: str, start: str, end: str) -> pd.DataFrame:
    """Fetch OHLCV data from MySQL for a given ticker and date range."""
    conn = mysql.connector.connect(**DB_CONFIG)
    query = """
        SELECT sp.trading_date AS date,
               sp.open_price   AS open,
               sp.high_price   AS high,
               sp.low_price    AS low,
               sp.close_price  AS close,
               sp.volume       AS volume
        FROM   stock_prices sp
        JOIN   companies c USING (company_id)
        WHERE  c.ticker = %s
          AND  sp.trading_date BETWEEN %s AND %s
        ORDER  BY sp.trading_date
    """
    df = pd.read_sql(query, conn, params=(ticker, start, end), parse_dates=["date"])
    conn.close()
    return df


def generate_sample_data(ticker: str = "AAPL", n: int = 252) -> pd.DataFrame:
    """Generate realistic sample OHLCV data (fallback when no DB available)."""
    np.random.seed(42)
    dates = pd.bdate_range(end=pd.Timestamp.today(), periods=n)
    price = 150.0
    prices = []
    for _ in range(n):
        price *= np.exp(np.random.normal(0.0003, 0.015))
        prices.append(price)

    prices = np.array(prices)
    df = pd.DataFrame({
        "date":   dates,
        "open":   prices * (1 + np.random.uniform(-0.005, 0.005, n)),
        "high":   prices * (1 + np.random.uniform(0.002, 0.015, n)),
        "low":    prices * (1 - np.random.uniform(0.002, 0.015, n)),
        "close":  prices,
        "volume": np.random.randint(5_000_000, 80_000_000, n),
    })
    return df


# ── Technical Indicators ───────────────────────────────────────────────────

def compute_moving_averages(df: pd.DataFrame) -> pd.DataFrame:
    df["ma5"]  = df["close"].rolling(5).mean()
    df["ma20"] = df["close"].rolling(20).mean()
    df["ma50"] = df["close"].rolling(50).mean()
    return df


def compute_rsi(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    delta = df["close"].diff()
    gain  = delta.clip(lower=0)
    loss  = -delta.clip(upper=0)
    avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
    avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()
    rs = avg_gain / avg_loss
    df["rsi"] = 100 - (100 / (1 + rs))
    return df


def compute_macd(df: pd.DataFrame, fast=12, slow=26, signal=9) -> pd.DataFrame:
    ema_fast   = df["close"].ewm(span=fast,   adjust=False).mean()
    ema_slow   = df["close"].ewm(span=slow,   adjust=False).mean()
    df["macd"] = ema_fast - ema_slow
    df["macd_signal"] = df["macd"].ewm(span=signal, adjust=False).mean()
    df["macd_hist"]   = df["macd"] - df["macd_signal"]
    return df


# ── Dashboard ──────────────────────────────────────────────────────────────

DARK_BG   = "#0d1117"
PANEL_BG  = "#161b22"
TEXT_COL  = "#c9d1d9"
GRID_COL  = "#21262d"
PRICE_COL = "#58a6ff"
MA5_COL   = "#f0883e"
MA20_COL  = "#3fb950"
MA50_COL  = "#bc8cff"
VOL_UP    = "#3fb950"
VOL_DOWN  = "#f85149"
RSI_COL   = "#79c0ff"
MACD_COL  = "#58a6ff"
SIG_COL   = "#f0883e"


def plot_dashboard(df: pd.DataFrame, ticker: str):
    fig = plt.figure(figsize=(16, 10), facecolor=DARK_BG)
    fig.suptitle(f"{ticker} — Technical Analysis Dashboard",
                 color=TEXT_COL, fontsize=16, fontweight="bold", y=0.97)

    gs = gridspec.GridSpec(4, 1, figure=fig,
                           height_ratios=[3, 1.2, 1.2, 1.2],
                           hspace=0.06)

    axes = [fig.add_subplot(gs[i]) for i in range(4)]
    for ax in axes:
        ax.set_facecolor(PANEL_BG)
        ax.tick_params(colors=TEXT_COL, labelsize=9)
        ax.yaxis.label.set_color(TEXT_COL)
        for spine in ax.spines.values():
            spine.set_edgecolor(GRID_COL)
        ax.grid(True, color=GRID_COL, linewidth=0.5, linestyle="--", alpha=0.6)
        if ax is not axes[-1]:
            ax.set_xticklabels([])

    x = df["date"]

    # ── Panel 1: Price + MAs ──
    ax1 = axes[0]
    ax1.plot(x, df["close"], color=PRICE_COL, lw=1.5, label="Close")
    ax1.plot(x, df["ma5"],   color=MA5_COL,  lw=1.0, linestyle="--", label="MA5")
    ax1.plot(x, df["ma20"],  color=MA20_COL, lw=1.0, linestyle="-.", label="MA20")
    ax1.plot(x, df["ma50"],  color=MA50_COL, lw=1.0, linestyle=":",  label="MA50")
    ax1.set_ylabel("Price (USD)", color=TEXT_COL, fontsize=10)
    ax1.legend(facecolor=PANEL_BG, edgecolor=GRID_COL,
               labelcolor=TEXT_COL, fontsize=9, loc="upper left")

    # ── Panel 2: Volume ──
    ax2 = axes[1]
    colors = [VOL_UP if c >= o else VOL_DOWN
              for c, o in zip(df["close"], df["open"])]
    ax2.bar(x, df["volume"], color=colors, width=1.0, alpha=0.8)
    ax2.set_ylabel("Volume", color=TEXT_COL, fontsize=10)
    ax2.yaxis.set_major_formatter(
        plt.FuncFormatter(lambda v, _: f"{v/1e6:.0f}M"))

    # ── Panel 3: RSI ──
    ax3 = axes[2]
    ax3.plot(x, df["rsi"], color=RSI_COL, lw=1.3)
    ax3.axhline(70, color="#f85149", lw=0.8, linestyle="--", alpha=0.7)
    ax3.axhline(30, color="#3fb950", lw=0.8, linestyle="--", alpha=0.7)
    ax3.fill_between(x, df["rsi"], 70,
                     where=df["rsi"] >= 70, alpha=0.15, color="#f85149")
    ax3.fill_between(x, df["rsi"], 30,
                     where=df["rsi"] <= 30, alpha=0.15, color="#3fb950")
    ax3.set_ylim(0, 100)
    ax3.set_ylabel("RSI (14)", color=TEXT_COL, fontsize=10)

    # ── Panel 4: MACD ──
    ax4 = axes[3]
    ax4.plot(x, df["macd"],        color=MACD_COL, lw=1.3, label="MACD")
    ax4.plot(x, df["macd_signal"], color=SIG_COL,  lw=1.0, label="Signal")
    hist_colors = [VOL_UP if h >= 0 else VOL_DOWN for h in df["macd_hist"]]
    ax4.bar(x, df["macd_hist"], color=hist_colors, width=1.0, alpha=0.5)
    ax4.axhline(0, color=GRID_COL, lw=0.8)
    ax4.set_ylabel("MACD", color=TEXT_COL, fontsize=10)
    ax4.legend(facecolor=PANEL_BG, edgecolor=GRID_COL,
               labelcolor=TEXT_COL, fontsize=9, loc="upper left")
    ax4.tick_params(axis="x", colors=TEXT_COL, labelsize=8, rotation=30)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig(f"{ticker}_dashboard.png", dpi=150, bbox_inches="tight",
                facecolor=DARK_BG)
    print(f"Dashboard saved → {ticker}_dashboard.png")
    plt.show()


# ── Main ───────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Stock Market Analysis Dashboard")
    parser.add_argument("--ticker", default="AAPL")
    parser.add_argument("--start",  default=(datetime.today() - timedelta(days=365)).strftime("%Y-%m-%d"))
    parser.add_argument("--end",    default=datetime.today().strftime("%Y-%m-%d"))
    parser.add_argument("--sample", action="store_true",
                        help="Use generated sample data instead of DB")
    args = parser.parse_args()

    print(f"Loading data for {args.ticker} ({args.start} → {args.end})...")

    if args.sample:
        df = generate_sample_data(args.ticker)
    else:
        try:
            df = fetch_data(args.ticker, args.start, args.end)
        except Exception as e:
            print(f"DB connection failed ({e}), using sample data instead.")
            df = generate_sample_data(args.ticker)

    if df.empty:
        print("No data found. Using sample data.")
        df = generate_sample_data(args.ticker)

    df = compute_moving_averages(df)
    df = compute_rsi(df)
    df = compute_macd(df)

    plot_dashboard(df, args.ticker)


if __name__ == "__main__":
    main()
