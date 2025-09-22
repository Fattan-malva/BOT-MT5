import MetaTrader5 as mt5

def send_market_order(symbol, action, volume, sl, tp, deviation=20, comment='python-mt5-bot'):
    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        raise RuntimeError('No tick for ' + symbol)
    price = tick.ask if action == 'BUY' else tick.bid
    order_type = mt5.ORDER_TYPE_BUY if action == 'BUY' else mt5.ORDER_TYPE_SELL
    request = {
        'action': mt5.TRADE_ACTION_DEAL,
        'symbol': symbol,
        'volume': float(volume),
        'type': order_type,
        'price': float(price),
        'sl': float(sl) if sl else 0.0,
        'tp': float(tp) if tp else 0.0,
        'deviation': deviation,
        'magic': 234000,
        'comment': comment,
        'type_filling': mt5.ORDER_FILLING_FOK,
    }
    result = mt5.order_send(request)
    return result

def close_position(position):
    symbol = position.symbol
    volume = position.volume
    action = 'SELL' if position.type == 0 else 'BUY'
    tick = mt5.symbol_info_tick(symbol)
    price = tick.bid if action == 'SELL' else tick.ask
    order_type = mt5.ORDER_TYPE_SELL if action == 'SELL' else mt5.ORDER_TYPE_BUY
    request = {
        'action': mt5.TRADE_ACTION_DEAL,
        'position': int(position.ticket),
        'symbol': symbol,
        'volume': float(volume),
        'type': order_type,
        'price': float(price),
        'deviation': 20,
        'magic': 234000,
        'comment': 'close by python'
    }
    res = mt5.order_send(request)
    return res

def modify_sl_tp(position_ticket, symbol, sl=None, tp=None):
    request = {
        'action': mt5.TRADE_ACTION_SLTP,
        'position': int(position_ticket),
        'symbol': symbol,
        'sl': float(sl) if sl else 0.0,
        'tp': float(tp) if tp else 0.0,
    }
    res = mt5.order_send(request)
    return res
