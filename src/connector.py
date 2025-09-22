import os
import MetaTrader5 as mt5
from dotenv import load_dotenv
from datetime import datetime, timedelta


load_dotenv()

def initialize(path=None, login=None, password=None, server=None):
    if path:
        ok = mt5.initialize(path)
    else:
        ok = mt5.initialize()
    if not ok:
        raise RuntimeError(f"mt5.initialize() failed, error={mt5.last_error()}")
    if login and password:
        logged_in = mt5.login(int(login), password=password, server=server)
        if not logged_in:
            print('Warning: mt5.login() returned False. You may need to login manually in MT5 terminal.')
    return True

def shutdown():
    mt5.shutdown()

def get_account_info():
    info = mt5.account_info()
    if info is None:
        return {}
    return {
        'login': info.login,
        'balance': info.balance,
        'equity': info.equity,
        'margin': info.margin,
        'free_margin': info.margin_free
    }

def get_positions(symbol=None):
    positions = mt5.positions_get(symbol=symbol) if symbol else mt5.positions_get()
    if positions is None:
        return []
    # Konversi ke dict agar mudah diakses
    result = []
    for p in positions:
        result.append({
            'type': 'BUY' if p.type == mt5.ORDER_TYPE_BUY else 'SELL',
            'symbol': p.symbol,
            'volume': p.volume,
            'price_open': p.price_open,
            'sl': p.sl,
            'tp': p.tp,
            'profit': p.profit
        })
    return result

def symbol_select(symbol):
    return mt5.symbol_select(symbol, True)

def get_symbol_info(symbol):
    return mt5.symbol_info(symbol)

def get_tick(symbol):
    return mt5.symbol_info_tick(symbol)

def get_candles(symbol, timeframe, n=500):
    import pandas as pd
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, n)
    if rates is None:
        raise RuntimeError('Failed to get rates for ' + symbol)
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    return df

def get_history(symbol=None, days=7):
    """Ambil closed trade history X hari terakhir (default 7 hari)"""
    utc_from = datetime.now() - timedelta(days=days)
    utc_to = datetime.now()
    deals = mt5.history_deals_get(utc_from, utc_to, group=symbol if symbol else None)
    if deals is None:
        return []
    history = []
    for d in deals:
        # Pastikan field sesuai dengan yang dibutuhkan monitor.py
        history.append({
            'type': 'BUY' if d.type == mt5.ORDER_TYPE_BUY else 'SELL',
            'symbol': d.symbol,
            'volume': d.volume,
            'price_open': d.price,
            'price_close': d.price,  # Atau gunakan price_close jika ada
            'time_close': d.time,    # Pastikan ini UNIX timestamp
            'profit': d.profit
        })
    # Urutkan dari terbaru ke terlama
    history.sort(key=lambda h: h['time_close'], reverse=True)
    return history
