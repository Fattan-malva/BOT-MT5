import math
import MetaTrader5 as mt5

def lot_by_risk(symbol, entry_price, stop_loss_price, risk_percent=0.5, min_lot=0.01):
    account = mt5.account_info()
    if account is None:
        raise RuntimeError('No account info from MT5.')
    equity = account.equity
    # Untuk modal kecil, risk_percent default 0.5% per entry
    risk_amount = equity * (risk_percent / 100.0)
    sym = mt5.symbol_info(symbol)
    if sym is None:
        raise RuntimeError('symbol_info returned None for ' + symbol)
    point = getattr(sym, 'point', None) or 0.00001
    tick_value = getattr(sym, 'trade_tick_value', None) or getattr(sym, 'tick_value', None)
    tick_size = getattr(sym, 'trade_tick_size', None) or getattr(sym, 'tick_size', None)
    if tick_value and tick_size:
        pip_value = tick_value / tick_size
    else:
        contract_size = getattr(sym, 'trade_contract_size', None) or getattr(sym, 'contract_size', None) or 100000
        pip_value = contract_size * point
    pips_risk = abs(entry_price - stop_loss_price)
    if pips_risk <= 0:
        # Jika SL terlalu dekat, tetap entry dengan lot minimum
        return min_lot
    value_per_lot = pips_risk * pip_value
    if value_per_lot == 0:
        return min_lot
    raw_lots = risk_amount / value_per_lot
    lot_step = getattr(sym, 'volume_step', None) or getattr(sym, 'trade_volume_step', None) or 0.01
    min_volume = getattr(sym, 'volume_min', None) or getattr(sym, 'trade_volume_min', None) or min_lot
    max_volume = getattr(sym, 'volume_max', None) or getattr(sym, 'trade_volume_max', None) or 100.0
    lots = math.floor(raw_lots / lot_step) * lot_step
    lots = max(lots, min_volume, min_lot)
    lots = min(lots, max_volume)
    if lots <= 0:
        lots = min_lot
    # Untuk modal kecil, jangan lebih dari 0.05 lot
    lots = min(lots, 0.05)
    return round(lots, 2)
