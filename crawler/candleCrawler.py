import threading
import websocket
import time
import pprint
import json
import datetime
from collections import deque


from binance.client import Client


class CandleCrawler:

	def __init__(self, client, symbol):

		self.client = client
		self.symbol = symbol
		

		self.WEBSOCKETS = ["wss://stream.binance.com:9443/ws/{}@kline_1m".format(symbol.lower())]

		self.THREADS = []

		self.candles = self.candle_initiation()

		self.ws = None
		self.is_running = False


	def candle_initiation(self):

		# return  a list
		klines = self.client.get_historical_klines(self.symbol.upper(), Client.KLINE_INTERVAL_1MINUTE, "1 day ago UTC")

		candles = deque(maxlen= 1440) #doubly ended queue
		candles.extend([{
						'open' : float(i[1]), 
						'high' : float(i[2]), 
						'low' : float(i[3]), 
						'close' :float(i[4])
						} for i in klines][:-1])
		return candles

	def start_crawling(self, callback = None):

		self.is_running = True

		thread = threading.Thread(target=self._start_crawling_handler, args=(callback, ))
		thread.start()
		self.THREADS.append(thread)

	

	def _start_crawling_handler(self, callback = None):


		socket = self.WEBSOCKETS[-1]
		self.ws = websocket.WebSocketApp(socket,
											on_open = lambda ws: self._wss_on_open(ws),
											on_error = lambda ws, error: self._wss_on_error(ws, error),
											on_close = lambda ws: self._wss_on_close(ws),
											on_message = lambda ws,msg: self._wss_on_message(ws, msg, callback1, callback2))
		self.ws.run_forever()


	def _wss_on_open(self, ws):
		pass

	def _wss_on_close(self, ws):
		pass

	def _wss_on_error(self, ws, error):
		print("error: ", error)

	def _wss_on_message(self, ws, msg, callback1, callback2):

		msg = json.loads(msg)
		

		if msg['k']['x'] == True:
			candle = 	{'open' : float(msg['k']['o']), 
						'high' : float(msg['k']['h']), 
						'low' : float(msg['k']['l']), 
						'close' :float(msg['k']['c'])}

			self.candles.append(candle)

			callback1()
		callback2(float(msg['k']['c']))

	def stop(self):
		
		if self.ws:
			self.ws.keep_running = False
			self.is_running = False
			print("candle crawler stopped")

if __name__ == "__main__":
	
	pass