import talib
import numpy
import collections
import pprint
import threading
import websocket

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException

class TradingBot:

	def __init__(self, apiKey, apiSecret):

		self.client = Client(apiKey, apiSecret)
		self.queue = collections.deque()
		self.candles = []
		self.rsi = []
		self.macd = []

		self.THREADS = collections.deque()
		self.mode = None
		self.is_running = False

		self.orders = {}

		self.ws = ""
		self.WEBSOCKETS = ["wss://stream.binance.com:9443/ws/ethusdt@kline_1m"] # strings

		self.current_candle = []



	def crawl_klines(self):

		# CALCULATE EVERY MINTUE
		print("crawlKlines")
		

	def calculate_rsi(self):

		# CALCULATE EVERY MINTUE
		print("calculate rsi")
		

	def calculate_macd(self):

		# CALCULATE EVERY MINTUE
		print("calculate macd")

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

		# self.candles = self.client.get_klines(symbol='BNBBTC', interval=Client.KLINE_INTERVAL_1MINUTE)
		# thread = threading.Thread(target=crawKlinesHandler, args=(len(self.THREADS) + 1))
		# self.THREAD.append(thread)
		# thread.start()
		print("run socket")
		self.candle_websocket(self.WEBSOCKETS[0])

		print("run")

	def crawlKlinesHandler(self, threadId):
		while True:
			print("crawling candles")
		# helper function for threading

	def crawlPriceHandler(self, symbol):
		# helper function for threading
		pass

	def candle_websocket(self, socket):
		print(socket)
		self.ws = websocket.WebSocketApp(socket, 
										on_open=self.ws_on_open,
										on_close=self.ws_on_close,
										on_error=self.ws_on_error,
										on_message=self.ws_on_message)
		print("created websocket")
		self.ws.run_forever()
		print("now running weboscket")
		# thread = threading.Thread(target=crawlKlinesHandler, args=(len(self.THREADS) + 1,))
		# self.THREADS.append(thread)
		# thread.start()

	def ws_on_open(ws):
		print("websocket open: ", ws)

	def ws_on_close (ws):
		print("websocket close ", ws)

	def ws_on_error(ws, error):
		print("websocket error")
		print(error)
		print("from ", ws)

	def ws_on_message(ws, msg):
		pprint.pprint(msg)
		print(type(msg))
		self.current_candle = msg

if __name__ == "__main__":
	bot = TradingBot("TFWFmx5lPFNkkQnEIQsl2596kr1errGmaabzC3bFWI17mifeIYmnBybtU4Opkkyp", "kBzXtdMQsOVCrfV9qwyCabshmyALX3ABNjzGJF2a7ZoHF7oh6lzh4gEuvHOwQBSR")
	bot.run()
