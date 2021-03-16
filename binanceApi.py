import time
import pprint
import threading
import json
import queue
import collections
import pprint
import os
import sys

sys.path[0] = os.path.dirname(sys.path[0])
module_name = os.path.basename(sys.path[0])

from binance.enums import *
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException

import tradingbot.indicator.indicator as ind
import tradingbot.tradingBot.tradingBot as tb
import tradingbot.tradingBot.testBot as testBot
import tradingbot.tradingBot.alertBot as ab
import tradingbot.orderMaker.orderMaker as om
import tradingbot.orderMaker.testOrderMaker as testOm
from tradingbot.algorithms import *

class MainApplication:

    def __init__(self,apiKey, apiSecret):
        self.client = Client(apiKey, apiSecret)


        self.BOTS = []
        self.symbols=['BNBUSDT', 'BTCUSDT', 'LUNAUSDT']

        self.algorithm = algo_rsi



    def run(self):

        for symbol in self.symbols[:]:
            
            indicator = ind.Indicator(oversold_threshold = 30.666, overbought_threshold = 70)

            #BACK TEST BOT
            #BACK TEST BOT
            order_maker = testOm.OrderMaker(self.client, symbol, stake=20, take_profit=0.06, stop_loss=0.01, fee=0.001, discount = 0)
            bot = testBot.TestBot(self.client, symbol, self.algorithm, order_maker = order_maker, indicator = indicator)
            
            #REAL BOT
            # order_maker = om.OrderMaker(self.client, symbol, stake=10.5, take_profit=0.015, stop_loss=0.01, fee=0.001, discount = 0)
            # bot = tb.TradingBot(self.client, symbol, self.algorithm, order_maker = order_maker, indicator = indicator)
            self.BOTS.append(bot)
            bot.start()
            
            return

    def log(self):

        for bot in self.BOTS:
            bot.log()

    def stop(self):

        for bot in self.BOTS:
            bot.stop()


if __name__ == "__main__":

    apiKey = "TFWFmx5lPFNkkQnEIQsl2596kr1errGmaabzC3bFWI17mifeIYmnBybtU4Opkkyp"
    apiSecret = "kBzXtdMQsOVCrfV9qwyCabshmyALX3ABNjzGJF2a7ZoHF7oh6lzh4gEuvHOwQBSR"

    main = MainApplication(apiKey, apiSecret)
    main.run()

    # klines = main.client.get_historical_klines("SFPUSDT", Client.KLINE_INTERVAL_1MINUTE, "8 Feb, 2021")
    # pprint.pprint(klines[0])
    try:
        while True:
            time.sleep(1)
    
    except KeyboardInterrupt:
        for bot in main.BOTS:
            bot.stop()
        

