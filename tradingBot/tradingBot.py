import collections
import pprint
import threading
import time
import datetime
import os
import re
import math
import traceback

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
            try:
                if self.order_manager.is_in_position == True:
                
                    if self.order_manager.trailing_stop_mode == True:
                        result = self.order_manager.check_current_position2(self.candle_crawler.candles_15m[-1]['close'])
                        print("_check current_position done ...result:", result)
                    else:
                        result = self.order_manager.check_current_position(self.candle_crawler.candles_15m[-1]['close'])
            except Exception as e:
                print("'_check_current_position' in 'tradingbot':", e)
        
        self.candle_crawler.start_crawling(callback1=self._check_if_can_buy, callback2=_check_current_position)
    
    def crawl_all_symbols(self):
        
        #EVERY 15MIN INVERTAL WILL CHECK ALL SYMBOL IF ANY BUY SIGNAL (BASED ON GIVEN ALGORITM)
        
        def _private_callback(symbol, candles_15m):
            try:
  
                signal, rsi_value = self.algorithm.run(candles_15m, self.indicator)
                if signal == True:
                    print(symbol, candles_15m[-1]['close'], rsi_value, datetime.datetime.fromtimestamp(candles_15m[-1]['time']), len(candles_15m))
                    print(self.indicator.rsi[-7:])
                    self.alert_bot.run()
                
                return
            except Exception as e:
                print("_private_callback in 'crawl_all_symbols' inside 'TradingBot' error... see below: ")
                traceback.print_tb(e.__traceback__)
            
        self.candle_crawler.start_all_symbol(callback1=_private_callback)
        
    def _check_if_can_buy(self):

        # FOR DEBUG PURPOSE
        try:
            temp, rsi = self.algorithm.run(self.candle_crawler.candles_15m, self.indicator)
            print("symbol: {}, price: {}, rsi: {}, time: {}".format(self.symbol, 
                self.candle_crawler.candles_15m[-1]['close'], 
                rsi, 
                datetime.datetime.fromtimestamp(self.candle_crawler.candles_15m[-1]['time'])))
        except Exception as e:
            print(e)
            
        
        if not self.order_manager.is_in_position:
            signal, rsi = self.algorithm.run(self.candle_crawler.candles_15m, self.indicator)
            
            if signal == True:
                
                self.alert_bot.run()
                
                #MAKE ORDER
                if self.order_manager.trailing_stop_mode == True:
                    print("....buy time ", datetime.datetime.fromtimestamp(self.candle_crawler.candles_15m[-1]['time']))
                    self.order_manager.buy_with_stop_limit()
                else:
                    self.order_manager.buy_with_oco()
        else:
            
            #then check trailing stop mode
            if self.order_manager.trailing_stop_mode == True:
            
                #firstly check current position
                result = self.order_manager.check_current_position2(self.candle_crawler.candles_15m[-1]['close'])
                
                if result == True:
                    print("_check current_position done ...result:", result)
                    return
                    
                current_candle = self.candle_crawler.candles_15m[-1]
                if current_candle['close'] > self.order_manager.prev_price:
                    result = self.order_manager.trailing_stop(current_candle['close'])
                    print("..checked trailing stop: prev_price: {}, current_price: {}, result: {}".format(self.order_manager.prev_price, current_candle['close'], result))
            
            

    def run(self):
        self.is_running = True
        self.crawl_klines()
        
    def log(self):
        print(".... still not have loggin function..")


    def stop(self):
        self.is_running = False

        self.candle_crawler.stop()
        self.order_manager.stop()
        

if __name__ == "__main__":
    pass
