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

pprint.pprint(sys.path)
import binanceApi as b
pprint.pprint(dir(b))

from binance.enums import *
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException

import binanceApi.crawler.priceCrawler as pc
import binanceApi.crawler.candleCrawler as cc
import binanceApi.tradingBot.tradingBot as tb
import binanceApi.tradingBot.alertBot as ab



print("binanceApi")
class MainApplication:

	def __init__(self,apiKey, apiSecret):

		self.client = Client(apiKey, apiSecret)

		self.BOTS = []
		self.THREADS = []

		self.symbols=['BNBUSDT', 'BTCUSDT', 'ADAUSDT', 'DOTUSDT', 'LITUSDT']



	def run(self):
		print("main run")

		for symbol in (self.symbols):

			bot = tb.TradingBot(self.client, symbol)
			self.BOTS.append(bot)
			# bot.start()
			break

		bot.order_maker.create_order_buy_market()
		# self.alert_bot.alert()

		#TESTING PURPOSE
		# orders = self.client.get_all_orders(symbol='BNBUSDT', limit=10)

		# order_status = self.client.get_order(
		#     symbol='BNBUSDT',
		#     orderId='1629496042')

		# fees = self.client.get_trade_fee()

		# #TESING PURPOSE
		# order = client.create_order(
  #   symbol='BNBBTC',
  #   side=SIDE_BUY,
  #   type=ORDER_TYPE_LIMIT,
  #   timeInForce=TIME_IN_FORCE_GTC,
  #   quantity=1,
  #   price=100)


		# # pprint.pprint(order_status)
		# # pprint.pprint(orders[:])
		# pprint.pprint(fees)

		

if __name__ == "__main__":

	apiKey = "TFWFmx5lPFNkkQnEIQsl2596kr1errGmaabzC3bFWI17mifeIYmnBybtU4Opkkyp"
	apiSecret = "kBzXtdMQsOVCrfV9qwyCabshmyALX3ABNjzGJF2a7ZoHF7oh6lzh4gEuvHOwQBSR"

	main = MainApplication(apiKey, apiSecret)
	main.run()
	


