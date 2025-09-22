# Emojis untuk notifikasi
EMOJI_BUY = "🟢"
EMOJI_SELL = "🔴"
EMOJI_ARROW_UP = "⬆️"
EMOJI_ARROW_DOWN = "⬇️"
EMOJI_TARGET = "🎯"
EMOJI_STOP = "🛑"
EMOJI_PROFIT = "💚"
EMOJI_LOSS = "❤️"

def notify_console(message):
    print('[NOTIFY]', message)

def notify_signal(action, symbol, price, sl, tp, lot):
    """Notifikasi khusus untuk signal dengan emoji"""
    if action.lower() == 'buy':
        emoji_action = f"{EMOJI_BUY} BUY"
    elif action.lower() == 'sell':
        emoji_action = f"{EMOJI_SELL} SELL"
    else:
        emoji_action = action

    print(f"🎯 SIGNAL DETECTED: {emoji_action} {symbol}")
    print(f"💰 Entry: {price} | 🛑 SL: {sl} | 🎯 TP: {tp} | 📊 Lot: {lot}")
    print("-" * 50)
