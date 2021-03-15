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

    def __init__(self, client, symbol, algorithm, order_maker, indicatore):
        threading.Thread.__init__(self)
        self.is_running = False

        #initiating fields
        self.test_mode = test_mode
        self.client = client
        self.symbol = symbol
        self.algorithm = algorithm
        self.order_maker = order_maker
        self.indicator = indicator

        #initiating objects
        self.alert_bot = AlertBot()
        self.candle_crawler = cc.CandleCrawler(client, symbol)

    def crawl_klines(self):
        # CALCULATE EVERY MINTUE
        self.candle_crawler.start_crawling(callback1=self._check_if_can_buy, callback2=self.order_maker.check_current_position)
        
    def _check_if_can_buy(self):

        #TODO: finish trading algorithm for bot
        if not self.order_maker.is_in_position:
            # find a signal to buy if currently not in position
            try:
                signal = self.algorithm.run(self.candle_crawler.candles_15m, self.indicator)
                print(self.indicator.rsi[-7:])
                if signal == True:
                    self.alert_bot.run()
                    #MAKE ORDER
                    pass
            except Exception as e:
                print("..._chcek if can buy: ", e)

    def run(self):
        self.is_running = True
        self.crawl_klines()


    def stop(self):
        self.report()
        self.is_running = False

        self.candle_crawler.stop()
        self.order_maker.stop()
        

if __name__ == "__main__":
    pass
