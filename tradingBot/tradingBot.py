import talib
import numpy
import collections
import pprint
import threading
import websocket

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException

from ..crawler import candleCrawler as cc

class TradingBot(threading.Thread):

	def __init__(self, client, symbol):

		threading.Thread.__init__(self)

		self.OVERBOUGHT_THRESHOLD = 70
		self.OVERSOLD_THRESHOLD = 30

		self.client = client
		self.symbol = symbol

		#indicator lists
		self.rsi = []
		self.macd = []
		self.macd_signal = []
		self.macd_hist = []


		self.candle_crawler = cc.CandleCrawler(client, symbol)
		self._refresh_indicator()

		print("bot created")


	

	def crawl_klines(self):

		# CALCULATE EVERY MINTUE
		self.candle_crawler.start_crawling(callback=self._refresh_indicator)
		print("crawling candle")
		
	def _refresh_indicator(self):
		print("refresing indicator...")

		self._refresh_rsi()
		self._refresh_macd()


		print("...done")

		print("len rsi: ",len(self.rsi), self.rsi[-4:])

		print("len macd: ",len(self.macd), self.macd[-4:])
		print("len macd_signal: ",len(self.macd_signal), self.macd_signal[-4:])
		print("len macd_hist: ",len(self.macd_hist), self.macd_hist[-4:])
		print("len candles: ", len(self.candle_crawler.candle_closes), self.candle_crawler.candle_closes[-4:])

		print(self._check())


	def _refresh_rsi(self):

		print("calculate rsi")	
		# CALCULATE EVERY MINTUE
		self.rsi = list(talib.RSI(numpy.array(self.candle_crawler.candle_closes)))
		self.rsi = list(map(lambda x: round(x,2), self.rsi))	

	def _check(self):
		print("check if can buy")

		last_rsi = self.rsi[-1]
		last_close = self.candle_crawler.candle_closes[-1]

		last_macd = self.macd[-1]
		last_macd_signal = self.macd_signal[-1]
		last_macd_hist = self.macd_hist[-1]

		print("""
	- last RSI :				{}
	- last price :				{}

	- last MACD :				{}
	- last MACD signal :		{}
	- last MACD histogram :		{}
			""".format(last_rsi,last_close,last_macd,last_macd_signal,last_macd_hist))

		validate_rsi = self.validate_rsi()
		validate_macd = self.validate_macd()

		if validate_rsi == True and validate_macd == True:
			("BUY BUY BUY")


	def _refresh_macd(self):

		# CALCULATE EVERY MINTUE
		self.macd, self.macd_signal, self.macd_hist = talib.MACD(
			numpy.array(self.candle_crawler.candle_closes),
			fastperiod=12, 
			slowperiod=26, 
			signalperiod=9)

		#prettifying
		self.macd = list(map(lambda x: round(x,2), self.macd))
		self.macd_signal = list(map(lambda x: round(x,2), self.macd_signal))
		self.macd_hist = list(map(lambda x: round(x,2), self.macd_hist))

		print("calculate macd")

		

	def validate_rsi(self):
		#TODO: viet logic validate rsi

		if self.rsi[-1] < self.OVERSOLD_THRESHOLD:
			return True

		return False

	def validate_macd(self):

		#TODO: viet logic validate macd

		if self.macd[-2] < 0 and self.macd_signal[-2] < 0:
			return False

		if self.macd[-1] < 0 and self.macd_signal[-1] < 0:
			return False

		return True

	def order_buy_market(self):

		# IF RSI AND MACD IS GOOD
		print("buy market")

	def order_buy_limit(self):

		# IF RSI AND MACD IS GOOD
		print("buy limit")

	def order_sell_limit(self):

		# IF PLACE ORDER BUY SUCCESSFULLY
		print("sell")

	def order_stop_limit(self):

		# IF PLACE ORDER BUY SUCCESSFULLY
		print("stoploss")

	def run(self):
		self.crawl_klines()



if __name__ == "__main__":
	pass
