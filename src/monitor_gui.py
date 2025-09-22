import tkinter as tk
from tkinter import ttk
from datetime import datetime, date
import time
import os
from connector import get_candles, get_account_info, symbol_select, get_positions, get_history

POLL_INTERVAL = int(os.getenv('POLL_INTERVAL', '10')) * 1000  # ms

class TradingMonitor(tk.Tk):
    def __init__(self, symbol, timeframe, on_tick):
        super().__init__()
        self.symbol = symbol
        self.timeframe = timeframe
        self.on_tick = on_tick
        self.title("Trading Monitor")
        self.geometry("1000x700")

        # Tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        self.account_tab = ttk.Frame(self.notebook)
        self.positions_tab = ttk.Frame(self.notebook)
        self.history_tab = ttk.Frame(self.notebook)
        self.system_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.account_tab, text="Account Info")
        self.notebook.add(self.positions_tab, text="Open Positions")
        self.notebook.add(self.history_tab, text="Trading History")
        self.notebook.add(self.system_tab, text="System Info")

        # Tables
        self.account_table = self._create_table(self.account_tab, ["Field", "Value"])
        self.positions_table = self._create_table(self.positions_tab, ["Type", "Symbol", "Volume", "Open Price", "SL", "TP", "Profit"])
        self.history_table = self._create_table(self.history_tab, ["Type", "Symbol", "Volume", "Open Price", "Close Price", "Close Time", "Profit"])
        self.system_table = self._create_table(self.system_tab, ["Key", "Value"])

        # Start loop
        self.update_data()

    def _create_table(self, parent, columns):
        tree = ttk.Treeview(parent, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120, anchor="center")
        tree.pack(fill="both", expand=True)
        return tree

    def update_data(self):
        try:
            account = get_account_info()
            candles = get_candles(self.symbol, self.timeframe, n=500)
            positions = get_positions(self.symbol)
            history = get_history(self.symbol)

            # update account table
            self._update_table(self.account_table, [
                ["Balance", f"{account['balance']:.2f}"],
                ["Equity", f"{account['equity']:.2f}"],
                ["Free Margin", f"{account['free_margin']:.2f}"],
                ["Margin Used", f"{account['balance'] - account['free_margin']:.2f}"],
            ])

            # update positions
            positions_data = []
            for pos in positions:
                positions_data.append([
                    pos['type'], pos['symbol'], pos['volume'],
                    f"{pos['price_open']:.2f}",
                    f"{pos['sl']:.2f}" if pos['sl'] else "N/A",
                    f"{pos['tp']:.2f}" if pos['tp'] else "N/A",
                    f"{pos['profit']:.2f}"
                ])
            self._update_table(self.positions_table, positions_data)

            # update history
            history_data = []
            recent_history = sorted(history, key=lambda h: h.get('time_close', 0), reverse=True)[:10]
            for h in recent_history:
                close_time_str = datetime.fromtimestamp(h['time_close']).strftime('%Y-%m-%d %H:%M') if 'time_close' in h else "-"
                history_data.append([
                    h['type'], h['symbol'], h['volume'],
                    f"{h['price_open']:.2f}", f"{h['price_close']:.2f}",
                    close_time_str, f"{h['profit']:.2f}"
                ])
            self._update_table(self.history_table, history_data)

            # update system
            self._update_table(self.system_table, [
                ["Poll Interval", f"{POLL_INTERVAL//1000} seconds"],
                ["Last Update", datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
            ])

            # run strategy tick
            self.on_tick(account, candles, positions)

        except Exception as e:
            print("GUI update error:", e)

        # schedule next update
        self.after(POLL_INTERVAL, self.update_data)

    def _update_table(self, tree, rows):
        tree.delete(*tree.get_children())
        for row in rows:
            tree.insert("", "end", values=row)

def run_gui(symbol, timeframe, on_tick):
    if not symbol_select(symbol):
        print(f"Warning: cannot select symbol {symbol}. Make sure available in MarketWatch.")

    app = TradingMonitor(symbol, timeframe, on_tick)
    app.mainloop()


if __name__ == "__main__":
    symbol = os.getenv("SYMBOL", "BTCUSDm")
    timeframe = os.getenv("TIMEFRAME", "M1")
    def dummy_on_tick(account, candles, positions):
        pass
    run_gui(symbol, timeframe, dummy_on_tick)