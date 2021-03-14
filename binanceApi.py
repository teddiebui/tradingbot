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
import tradingbot.tradingBot.alertBot as ab
import tradingbot.orderMaker.orderMaker as om
from tradingbot.algorithms import *

class MainApplication:

	def __init__(self,apiKey, apiSecret):

		self.client = Client(apiKey, apiSecret)

		self.BOTS = []
		self.THREADS = []

		self.symbols=['BNBUSDT', 'BTCUSDT', 'LUNAUSDT']

		#TEST MODE
		self.algorithm = algo_rsi



	def run(self):

		for symbol in self.symbols[:]:

			order_maker = om.OrderMaker(self.client, 
										symbol, 
										stake=20, 
										take_profit=0.04, 
										stop_loss=0.01, 
										fee=0.001, 
										discount = 0.25)

			indicator = ind.Indicator(oversold_threshold = 30.666, overbought_threshold = 70)

			bot = tb.TradingBot(self.client, 
				symbol, 
				self.algorithm, 
				test_mode = True, 
				order_maker = order_maker,
				indicator = indicator)
			
			self.BOTS.append(bot)

			bot.start()
			break

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
		

