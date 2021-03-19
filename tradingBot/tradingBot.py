import collections
import pprint
import threading
import time
import datetime
import os
import re
import math

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException

from ..crawler import candleCrawler as cc
from ..indicator import indicator as ind
from ..orderMaker import orderMaker as om

from .alertBot import AlertBot

class TradingBot(threading.Thread):

    def __init__(self, client, symbol, algorithm, indicator, order_maker = None, order_manager = None):
        threading.Thread.__init__(self)
        self.is_running = False

        #initiating fields
        self.client = client
        self.symbol = symbol
        self.algorithm = algorithm
        self.order_maker = order_maker
        self.indicator = indicator
        self.order_manager = order_manager

        #initiating objects
        self.alert_bot = AlertBot()
        self.candle_crawler = cc.CandleCrawler(client, symbol)

    def crawl_klines(self):
        
        # CALCULATE EVERY INTERVAL TIME
        
        def _check_current_position():
            print("check current position")
            if self.order_manager.is_in_position == True:
            
                if self.order_manager.trailing_stop_mode == True:
                    self.order_manager.check_current_position2(self.candle_crawler.candles_15m[-1]['close'])
                else:
                    self.order_manager.check_current_position(self.candle_crawler.candles_15m[-1]['close'])
        
        self.candle_crawler.start_crawling(callback1=self._check_if_can_buy, callback2=_check_current_position)
    
    def crawl_all_symbols(self):
        
        #EVERY 15MIN INVERTAL WILL CHECK ALL SYMBOL IF ANY BUY SIGNAL (BASED ON GIVEN ALGORITM)
        
        def _private_callback(symbol, candles_15m):
  
            signal, rsi_value = self.algorithm.run(candles_15m, self.indicator)
            
            if signal == True:
                print(symbol, rsi_value)
                self.alert_bot.run()
            
            return
            
        self.candle_crawler.start_all_symbol(callback1=_private_callback)
        
    def _check_if_can_buy(self, current_price):

        # RUN ALGPRITHM CHECK
        if not self.order_manager.is_in_position:
            signal = self.algorithm.run(self.candle_crawler.candles_15m, self.indicator)
            
            if signal == True:
                self.alert_bot.run()
                
                #MAKE ORDER
                if self.order_manager.trailing_stop_mode == True:
                    self.order_manager.buy_with_stop_limit()
                else:
                    self.order_manager.buy_with_oco()
                pass
        else:
            if self.order_manager.trailing_stop_mode == True:
                current_candle = self.candle_crawler.candles_15m[-1]
                prev_candle = self.candle_crawler.candles_15m[-2]
                if current_candle['close'] > prev_candle['close']:
                    self.order_manager.trailing_stop(current_candle)
            
            

    def run(self):
        self.is_running = True
        self.crawl_klines()
        
    def log(self):
        print(".... still not have loggin function..")


    def stop(self):
        self.is_running = False

        self.candle_crawler.stop()
        self.order_maker.stop()
        

if __name__ == "__main__":
    pass
