import time
import pprint
import datetime
import talib
import numpy
import threading
import json
import queue
import collections
import pprint
import websocket
import talib
import tkinter as tk

import os
import sys

sys.path[0] = os.path.dirname(sys.path[0])


from tkinter import *
from binance.enums import *
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException

import binanceApi.crawler.priceCrawler as pc
import binanceApi.crawler.candleCrawler as cc
import binanceApi.tradingBot.tradingBot as tb



class MainApplication:

	def __init__(self,apiKey, apiSecret):

		self.client = Client(apiKey, apiSecret)

		self.BOTS = []
		self.THREADS = []

		self.symbols=['BNBUSDT', 'BTCUSDT', 'ADAUSDT', 'DOTUSDT', 'LITUSDT']


	def run(self):

		for symbol in (self.symbols):

			bot = tb.TradingBot(self.client, symbol)
			bot.start()

			self.BOTS.append(bot)
			break

if __name__ == "__main__":

	apiKey = "TFWFmx5lPFNkkQnEIQsl2596kr1errGmaabzC3bFWI17mifeIYmnBybtU4Opkkyp"
	apiSecret = "kBzXtdMQsOVCrfV9qwyCabshmyALX3ABNjzGJF2a7ZoHF7oh6lzh4gEuvHOwQBSR"

	main = MainApplication(apiKey, apiSecret)
	main.run()


	


