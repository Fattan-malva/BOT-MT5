import time
import os
import signal
import sys
from connector import get_candles, get_account_info, symbol_select, get_positions, get_history
from tabulate import tabulate
from datetime import datetime, date

POLL_INTERVAL = int(os.getenv('POLL_INTERVAL', '30'))  # Match main.py setting

# Global flag untuk kontrol running state
running = True

def signal_handler(signum, frame):
    """Handle Ctrl+C signal"""
    global running
    print(f"\n{YELLOW}Received interrupt signal, stopping gracefully...{RESET}")
    running = False
    # Give the loop a moment to stop gracefully
    time.sleep(1)
    print(f"{YELLOW}Forcing exit if still running...{RESET}")
    sys.exit(0)

# ANSI color
GREEN = '\033[92m'
RED = '\033[91m'
CYAN = '\033[96m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
MAGENTA = '\033[95m'
RESET = '\033[0m'

def format_currency(value):
    """Format nilai dengan 2 digit desimal, pakai titik sebagai pemisah ribuan"""
    return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def format_profit(value):
    """Format nilai profit dengan warna"""
    color = GREEN if value >= 0 else RED
    return f"{color}{format_currency(value)}{RESET}"

def format_percentage(value, total):
    """Format persentase"""
    if total == 0:
        return "0.00%"
    percentage = (value / total) * 100
    return f"{percentage:.2f}%"

def print_monitor(account, positions, history):
    os.system('cls' if os.name == 'nt' else 'clear')
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{CYAN}=== TRADING MONITOR [{current_time}] ==={RESET}")
    print()
    
    # Account Information - Tabel
    print(f"{BLUE}=== ACCOUNT INFORMATION ==={RESET}")
    account_data = [
        ["Balance", format_currency(account['balance'])],
        ["Equity", format_currency(account['equity'])],
        ["Free Margin", format_currency(account['free_margin'])],
        ["Margin Used", format_currency(account['balance'] - account['free_margin'])],
        ["Margin Level", format_percentage(account['equity'], account['balance'] - account['free_margin']) if account['balance'] - account['free_margin'] > 0 else "N/A"]
    ]
    print(tabulate(account_data, tablefmt="grid"))
    print()
    
    # Open Positions - Tabel dengan ringkasan
    print(f"{BLUE}=== OPEN POSITIONS ==={RESET}")
    if positions:
        # Ringkasan posisi
        total_profit = sum(pos['profit'] for pos in positions)
        total_volume = sum(pos['volume'] for pos in positions)
        
        # Data untuk tabel
        positions_data = []
        for pos in positions:
            profit_color = GREEN if pos['profit'] >= 0 else RED
            positions_data.append([
                pos['type'],
                pos['symbol'],
                pos['volume'],
                format_currency(pos['price_open']),
                format_currency(pos['sl']) if pos['sl'] else "N/A",
                format_currency(pos['tp']) if pos['tp'] else "N/A",
                f"{profit_color}{format_currency(pos['profit'])}{RESET}"
            ])
        
        # Header tabel
        headers = ["Type", "Symbol", "Volume", "Open Price", "SL", "TP", "Profit"]
        print(tabulate(positions_data, headers=headers, tablefmt="grid"))
        
        # Ringkasan
        print(f"\n{YELLOW}Summary:{RESET}")
        print(f"Total Positions: {len(positions)}")
        print(f"Total Volume: {format_currency(total_volume)}")
        print(f"Total Profit/Loss: {format_profit(total_profit)}")
    else:
        print("No open positions.")
    print()
    
    # Trading History - Tabel dengan ringkasan
    print(f"{BLUE}=== TRADING HISTORY (Last 10) ==={RESET}")
    if history:
        # Urutkan history dari terbaru ke terlama (pastikan history sudah diurutkan)
        sorted_history = sorted(history, key=lambda h: h.get('time_close', 0), reverse=True)
        recent_history = sorted_history[:10]

        # Hitung total profit/loss hari ini
        today = date.today()
        daily_trades = [h for h in history if 'time_close' in h and datetime.fromtimestamp(h['time_close']).date() == today]
        daily_profit = sum(h['profit'] for h in daily_trades)
        daily_loss = sum(h['profit'] for h in daily_trades if h['profit'] < 0)
        daily_win = sum(h['profit'] for h in daily_trades if h['profit'] > 0)

        # Ringkasan history
        total_history_profit = sum(h['profit'] for h in recent_history)
        winning_trades = sum(1 for h in recent_history if h['profit'] >= 0)
        losing_trades = sum(1 for h in recent_history if h['profit'] < 0)
        win_rate = (winning_trades / len(recent_history)) * 100 if recent_history else 0

        # Data untuk tabel
        history_data = []
        for h in recent_history:
            profit_color = GREEN if h['profit'] >= 0 else RED
            close_time_str = datetime.fromtimestamp(h['time_close']).strftime('%Y-%m-%d %H:%M') if 'time_close' in h else '-'
            history_data.append([
                h['type'],
                h['symbol'],
                h['volume'],
                format_currency(h['price_open']),
                format_currency(h['price_close']),
                close_time_str,
                f"{profit_color}{format_currency(h['profit'])}{RESET}"
            ])

        headers = ["Type", "Symbol", "Volume", "Open Price", "Close Price", "Close Time", "Profit"]
        print(tabulate(history_data, headers=headers, tablefmt="grid"))

        # Ringkasan
        print(f"\n{YELLOW}Summary (Last 10 Trades):{RESET}")
        print(f"Total Trades: {len(recent_history)}")
        print(f"Winning Trades: {winning_trades}")
        print(f"Losing Trades: {losing_trades}")
        print(f"Win Rate: {win_rate:.2f}%")
        print(f"Total Profit/Loss: {format_profit(total_history_profit)}")
        print(f"Average Profit/Trade: {format_profit(total_history_profit/len(recent_history)) if recent_history else 0}")

        # Tambahan: Ringkasan harian
        print(f"\n{MAGENTA}Today's P/L: {format_profit(daily_profit)} | Win: {format_profit(daily_win)} | Loss: {format_profit(daily_loss)}{RESET}")

    else:
        print("No history yet.")
    print()
    
    # System Information
    print(f"{BLUE}=== SYSTEM INFORMATION ==={RESET}")
    system_data = [
        ["Poll Interval", f"{POLL_INTERVAL} seconds"],
        ["Next Update", f"in {POLL_INTERVAL} seconds"]
    ]
    print(tabulate(system_data, tablefmt="grid"))
    print()

def run_loop(symbol, timeframe, on_tick):
    global running

    if not symbol_select(symbol):
        print(f'Warning: cannot select symbol {symbol} in MarketWatch. Make sure symbol available in terminal.')

    # Register signal handler untuk graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)

    print(f"{YELLOW}Starting monitoring for {symbol} on {timeframe} timeframe...{RESET}")
    print(f"{YELLOW}Press Ctrl+C to stop monitoring.{RESET}")
    time.sleep(2)

    try:
        while running:
            account = get_account_info()
            candles = get_candles(symbol, timeframe, n=500)
            positions = get_positions(symbol)
            history = get_history(symbol)
            print_monitor(account, positions, history)
            on_tick(account, candles, positions)
            time.sleep(POLL_INTERVAL)
    except Exception as e:
        print(f'{RED}Monitor loop error: {e}{RESET}')
    finally:
        print(f"\n{YELLOW}Monitoring stopped.{RESET}")
