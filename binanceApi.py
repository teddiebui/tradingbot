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


from binance.enums import *
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException


import binanceApi.tradingBot.tradingBot as tb
import binanceApi.tradingBot.alertBot as ab
import binanceApi.orderMaker.orderMaker as om
from binanceApi.algorithms import *

class MainApplication:

	def __init__(self,apiKey, apiSecret):

		self.client = Client(apiKey, apiSecret)

		self.BOTS = []
		self.THREADS = []

		self.symbols=['BNBUSDT', 'BTCUSDT', 'ADAUSDT', 'DOTUSDT', 'LITUSDT']

		#TEST MODE
		self.algorithm = algo_rsi



	def run(self):

		order_maker = om.OrderMaker(self.client, 
									self.symbols[0], 
									stake=20, 
									take_profit=0.05, 
									stop_loss=0.025, 
									fee=0.001, 
									discount = 0.25)

		bot = tb.TradingBot(self.client, 
			self.symbols[0], 
			self.algorithm, 
			test_mode = True, 
			order_maker = order_maker)

		
		self.BOTS.append(bot)

		bot.start()

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
	try:
		while True:
			time.sleep(10)
	except KeyboardInterrupt as e:
		

		print('...main program stopped: ',repr(e))
		main.stop()
		main.log()

