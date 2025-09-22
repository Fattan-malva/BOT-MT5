import pandas as pd
import numpy as np

def ema(series, period):
    return series.ewm(span=period, adjust=False).mean()

def macd(closes, fast=6, slow=13, signal=5):
    fast_ema = ema(closes, fast)
    slow_ema = ema(closes, slow)
    macd_line = fast_ema - slow_ema
    signal_line = ema(macd_line, signal)
    hist = macd_line - signal_line
    return macd_line, signal_line, hist

def bollinger(closes, period=10, dev=1.8):
    ma = closes.rolling(window=period, min_periods=1).mean()
    std = closes.rolling(window=period, min_periods=1).std(ddof=0).fillna(0)
    upper = ma + dev * std
    lower = ma - dev * std
    return upper, ma, lower

def rsi(series, period=14):
    delta = series.diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    ma_up = up.ewm(alpha=1/period, adjust=False).mean()
    ma_down = down.ewm(alpha=1/period, adjust=False).mean()
    rs = ma_up / (ma_down + 1e-9)
    return 100 - (100 / (1 + rs))

def calculate_lot(balance, risk_pct, entry, sl,
                  account_currency="USD", pair_currency="USD",
                  fx_rate=15000, pip_size=0.0001, contract_size=100000):
    """
    Hitung lot dinamis bisa untuk akun USD / IDR.
    """
    # Risiko nominal dalam currency akun
    risk_amount = balance * risk_pct

    # Jarak SL
    sl_distance = abs(entry - sl)
    if sl_distance == 0:
        return 0.01

    # Pip count
    pip_count = sl_distance / pip_size

    # Pip value untuk 1 lot (default USD)
    pip_value_usd = contract_size * pip_size

    # Konversi pip value sesuai akun
    if account_currency == "USD":
        pip_value_account = pip_value_usd
    elif account_currency == "IDR":
        pip_value_account = pip_value_usd * fx_rate
    else:
        pip_value_account = pip_value_usd  # fallback

    # Lot calculation
    lot = risk_amount / (pip_count * pip_value_account)
    return max(0.01, round(lot, 2))


def detect_signal(df, balance=1000, risk_pct=0.01,
                  account_currency="USD", fx_rate=15000,
                  mode="scalping"):
    closes = df['close'].astype(float)
    if len(closes) < 30:
        return None

    # Indikator cepat
    macd_line, signal_line, hist = macd(closes, fast=3, slow=8, signal=3)
    rsi_vals = rsi(closes, period=7)

    macd_now, macd_prev = macd_line.iloc[-1], macd_line.iloc[-2]
    sig_now, sig_prev = signal_line.iloc[-1], signal_line.iloc[-2]
    hist_now = hist.iloc[-1]
    close_now = closes.iloc[-1]
    rsi_now = rsi_vals.iloc[-1]

    # Kondisi buy/sell agak longgar biar sering entry
    buy = ((macd_prev < sig_prev) and (macd_now > sig_now)) and (rsi_now < 70)
    sell = ((macd_prev > sig_prev) and (macd_now < sig_now)) and (rsi_now > 30)

    # --- MODE HANDLER ---
    if mode == "normal":
        tp_pct = 0.0005   # 0.05%
        sl_pct = 0.0010   # 0.1%
    elif mode == "scalping":
        tp_pct = 0.0002   # 0.02% (2 pip XAUUSD ~ 0.2)
        sl_pct = 0.0004   # 0.04% (4 pip)
    else:
        tp_pct = 0.0005
        sl_pct = 0.0010

    if buy:
        sl = float(close_now * (1 - sl_pct))
        tp = float(close_now * (1 + tp_pct))

        lot = calculate_lot(balance, risk_pct, close_now, sl,
                            account_currency=account_currency,
                            fx_rate=fx_rate)

        return {'action': 'BUY', 'price': float(close_now),
                'sl_band': sl, 'tp_band': tp, 'lot': lot, 'mode': mode}

    if sell:
        sl = float(close_now * (1 + sl_pct))
        tp = float(close_now * (1 - tp_pct))

        lot = calculate_lot(balance, risk_pct, close_now, sl,
                            account_currency=account_currency,
                            fx_rate=fx_rate)

        return {'action': 'SELL', 'price': float(close_now),
                'sl_band': sl, 'tp_band': tp, 'lot': lot, 'mode': mode}

    return None
