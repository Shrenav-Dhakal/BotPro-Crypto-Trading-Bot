import tkinter as tk
import time
from styling import *
import logging

from binance_futures import BinanceFuturesClient

from logging_component import Logging
from watchlist_component import Watchlist
from trades_component import TradesWatch
from strategy_component import StrategyEditor

logger = logging.getLogger()

class Root(tk.Tk):
    def __init__(self, binance: BinanceFuturesClient):
        super().__init__()

        self.binance = binance

        self.title("Trading Bot")

        self.configure(bg=BG_COLOR)

        self._left_frame = tk.Frame(self,bg=BG_COLOR)
        self._left_frame.pack(side=tk.LEFT)

        self._right_frame = tk.Frame(self,bg=BG_COLOR)
        self._right_frame.pack(side=tk.LEFT)

        self._watchlist_frame = Watchlist(self.binance.contracts, self._left_frame, bg=BG_COLOR)
        self._watchlist_frame.pack(side=tk.TOP)

        self.logging_frame = Logging(self._left_frame, bg=BG_COLOR)
        self.logging_frame.pack(side=tk.TOP)

        self._strategy_frame = StrategyEditor(self, self.binance, self._right_frame, bg=BG_COLOR)
        self._strategy_frame.pack(side=tk.TOP)

        self._trades_frame = TradesWatch(self._right_frame, bg=BG_COLOR)
        self._trades_frame.pack(side=tk.TOP)

        self._update_ui()

    def _update_ui(self):
        
        #logs
        for log in self.binance.logs:
            if not log['displayed']:
                self.logging_frame.add_log(log['log'])
                log['displayed'] = True
        
        # Trades and Logs
        for client in [self.binance]:
            try:
                for b_index , strat in client.strategies.items():
                    for log in strat.logs:
                        if not log['displayed']:
                            self.logging_frame.add_log(log['log'])
                            log['displayed]']=True
                    
                    for trade in strat.trades:
                        if trade.time not in self._trades_frame.body_widgets['symbol']:
                            self._trades_frame.add_trade(trade)
                        
                        precision = trade.contract.price_decimals
                        
                        pnl_str = "{0.:{prec}f".format(trade.pnl, prec=precision)
                        self._trades_frame.body_widgets['pnl_var'][trade.time].set(pnl_str)
                        self._trades_frame.body_widgets['status_var'][trade.time].set(trade.status.capitalize())
                        

            except RuntimeError as e:
                logger.error("Error while looping through strategies dictionary: %s",e)

        
        # Watchlist prices
        try:
            for key, value in self._watchlist_frame.body_widgets['symbol'].items():
                
                symbol = self._watchlist_frame.body_widgets['symbol'][key].cget("text")

                if symbol not in self.binance.contracts:
                    continue
                if symbol not in self.binance.prices:
                    self.binance.get_bid_ask(self.binance.contracts[symbol])
                    continue

                precision = self.binance.contracts[symbol].quantity_decimals

                prices = self.binance.prices[symbol]

                if prices['bid'] is not None:
                    price_str = "{0:.{prec}f}".format(prices['bid'], prec=precision)
                    self._watchlist_frame.body_widgets['bid_var'][key].set(prices['bid'])
                if prices['ask'] is not None:
                    price_str = "{0:.{prec}f}".format(prices['ask'], prec=precision)
                    self._watchlist_frame.body_widgets['ask_var'][key].set(prices['ask'])
        except RuntimeError as e:
            logger.error("Error while looping through the watchlist dictionary: %s",e)

        self.after(1500, self._update_ui)





