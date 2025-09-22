import os
import time
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

import MetaTrader5 as mt5
from connector import initialize, shutdown, get_account_info, get_positions, symbol_select, get_candles
from strategy import detect_signal
from trader import send_market_order
from risk_manager import lot_by_risk
from notifier import notify_console
from monitor import run_loop, running

# ================================
# === CONFIG DARI .env ===========
# ================================
SYMBOL = os.getenv('SYMBOL')
TIMEFRAME = os.getenv('TIMEFRAME')
RISK_PERCENT = float(os.getenv('RISK_PERCENT'))
DAILY_LOSS_LIMIT = float(os.getenv('DAILY_LOSS_LIMIT'))
MAX_TRADES_PER_DAY = int(os.getenv('MAX_TRADES_PER_DAY'))
POLL_INTERVAL = int(os.getenv('POLL_INTERVAL'))
MIN_LOT = float(os.getenv('MIN_LOT'))

MT5_LOGIN = os.getenv('MT5_LOGIN')
MT5_PASSWORD = os.getenv('MT5_PASSWORD')
MT5_SERVER = os.getenv('MT5_SERVER')
MT5_PATH = os.getenv('MT5_PATH')

TIMEFRAMES = {
    "M1": mt5.TIMEFRAME_M1,
    "M5": mt5.TIMEFRAME_M5,
    "M15": mt5.TIMEFRAME_M15,
    "H1": mt5.TIMEFRAME_H1,
    "D1": mt5.TIMEFRAME_D1,
}


def map_timeframe(tf):
    return TIMEFRAMES.get(tf.upper(), mt5.TIMEFRAME_M5)


# ================================
# === STATE CONTROL ==============
# ================================
trades_today = 0
loss_today = 0.0
start_balance = None
target_balance = None
min_balance = None
start_time = None


# ================================
# === CALLBACK ==================
# ================================
def on_tick(account_info, candles, positions):
    global trades_today, loss_today, running

    # Jika bot sudah stop, jangan proses lagi
    if not running:
        return

    # Double check untuk memastikan loop berhenti segera
    if not running:
        return

    balance = account_info.get("balance", 0)
    equity = account_info.get("equity", 0)

    notify_console(
        f"Balance={balance} "
        f"Equity={equity} "
        f"OpenPositions={len(positions)}"
    )

    # stop jika sudah loss melebihi limit harian
    if loss_today <= -abs(DAILY_LOSS_LIMIT):
        notify_console("Daily loss limit reached, stopping new entries.")
        running = False
        return

    # stop jika sudah mencapai max trade per hari
    if trades_today >= MAX_TRADES_PER_DAY:
        notify_console("Max trades per day reached, skipping entries.")
        running = False
        return

    # stop jika sudah mencapai target balance
    if balance >= target_balance:
        notify_console(f"Target balance {target_balance} reached ✅. Stopping bot.")
        running = False
        return

    # stop jika sudah mencapai batas bawah saldo
    if balance <= min_balance:
        notify_console(f"Min balance {min_balance} reached ❌. Stopping bot.")
        running = False
        return

    # cari sinyal baru hanya kalau masih running
    if running:
        sig = detect_signal(candles)
        if sig:
            entry = sig["price"]
            stop_loss = sig["sl_band"]
            take_profit = sig["tp_band"]

            lot = lot_by_risk(SYMBOL, entry, stop_loss, RISK_PERCENT, min_lot=MIN_LOT)
            notify_console(
                f"Signal {sig['action']} {SYMBOL} "
                f"price={entry} sl={stop_loss} tp={take_profit} lot={lot}"
            )

            res = send_market_order(SYMBOL, sig["action"], lot, stop_loss, take_profit)
            notify_console(f"Order send result: {getattr(res,'retcode',None)} {getattr(res,'comment',None)}")

            if getattr(res, "retcode", None) == mt5.TRADE_RETCODE_DONE:
                trades_today += 1



# ================================
# === MAIN LOOP =================
# ================================
def main():
    global start_balance, target_balance, min_balance, start_time, running

    print("Starting MT5 Python Autobot")

    initialize(path=MT5_PATH, login=MT5_LOGIN, password=MT5_PASSWORD, server=MT5_SERVER)

    # Ambil saldo awal dari akun
    acc = get_account_info()
    start_balance = acc.get("balance", 0)
    print(f"Saldo awal dari akun MT5: {start_balance}")

    # Input target saldo atas & bawah
    target_balance = float(input("Masukkan target saldo atas: "))
    min_balance = float(input("Masukkan batas saldo bawah: "))
    start_time = datetime.now()

    try:
        tf = map_timeframe(TIMEFRAME)
        run_loop(SYMBOL, tf, on_tick)
    finally:
        shutdown()
        # === Summary ===
        end_time = datetime.now()
        duration = end_time - start_time
        acc = get_account_info()
        final_balance = acc.get("balance", 0)
        profit = final_balance - start_balance

        print("\n===== BOT SUMMARY =====")
        print(f"Start Balance : {start_balance}")
        print(f"End Balance   : {final_balance}")
        print(f"Profit/Loss   : {profit}")
        print(f"Total Trades  : {trades_today}")
        print(f"Runtime       : {duration}")
        print("=======================")


if __name__ == "__main__":
    main()
