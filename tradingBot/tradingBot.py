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
        self.candle_crawler.start_crawling(callback1=self._check_if_can_buy, callback2=self.order_maker)
        
    def _check_if_can_buy(self):

        # RUN ALGPRITHM CHECK
        signal = self.algorithm.run(self.candle_crawler.candles_15m, self.indicator)
        
        if signal == True:
            self.alert_bot.run()
            #MAKE ORDER
            self.order_manager.buy()
            pass

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
