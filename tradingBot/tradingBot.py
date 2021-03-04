import talib
import numpy
import collections
import pprint
import threading
import websocket

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException

from ..crawler import candleCrawler as cc
from ..indicator import indicator as ind
from ..orderMaker import orderMaker as om

from .alertBot import AlertBot

class TradingBot(threading.Thread):

	def __init__(self, client, symbol):
		threading.Thread.__init__(self)

		self.client = client
		self.symbol = symbol

		self.alert_bot = AlertBot()
		self.indicator = ind.Indicator()
		self.candle_crawler = cc.CandleCrawler(client, symbol) #initiate candle crawler for the bot
		self.order_maker = om.OrderMaker(client, 
										symbol, 
										stake=100, 
										take_profit=0.01, 
										stop_loss=0.01, 
										fee=0.001, 
										discount = 0.25)
		
		self.ORDERS = []

		print("...trading bot created")
		self._refresh_indicator() #initiate indicator lists

	def crawl_klines(self):

		# CALCULATE EVERY MINTUE
		self.candle_crawler.start_crawling(callback=self._refresh_indicator)
		
	def _refresh_indicator(self):

		# this is a callback function passed to candle crawler object
		# refreshes indicator after receiving new candle
		self.indicator.refresh_rsi(self.candle_crawler.closes)
		self.indicator.refresh_macd(self.candle_crawler.closes)
		self.indicator.refresh_ema_200(self.candle_crawler.closes)
		self.indicator.refresh_dmi(self.candle_crawler.candles)

		# check for buying signal
		print(self._check_if_can_buy())


	def _check_if_can_buy(self):

		validate_rsi = self.indicator.validate_rsi()
		validate_macd = self.indicator.validate_macd()

		if validate_rsi == True:
			self.alert_bot.alert()
		if validate_rsi == True and validate_macd == True:
			self.alert_bot.alert()
			# order = self.order_maker.create_order_buy_market()



	def run(self):
		self.crawl_klines()

	def stop(self):
		self.candle_crawler.stop()
		pass





if __name__ == "__main__":
	pass
