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



class MainApplication:

	def __init__(self,apiKey, apiSecret):

		self.client = Client(apiKey, apiSecret)

		self.BOTS = []
		self.THREADS = []

		self.symbols=['BNBUSDT', 'BTCUSDT', 'ADAUSDT', 'DOTUSDT', 'LITUSDT']



	def run(self):
		print("main run")

		bot = tb.TradingBot(self.client, self.symbols[0])
		bot.start()

		self.BOTS.append(bot)


if __name__ == "__main__":

	apiKey = "TFWFmx5lPFNkkQnEIQsl2596kr1errGmaabzC3bFWI17mifeIYmnBybtU4Opkkyp"
	apiSecret = "kBzXtdMQsOVCrfV9qwyCabshmyALX3ABNjzGJF2a7ZoHF7oh6lzh4gEuvHOwQBSR"

	main = MainApplication(apiKey, apiSecret)
	main.run()
	


