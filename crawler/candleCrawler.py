import threading
import websocket
import time
import pprint
import queue
import json


from binance.client import Client


class CandleCrawler:

	def __init__(self, client, symbol):

		self.client = client
		self.symbol = symbol
		

		self.WEBSOCKETS = ["wss://stream.binance.com:9443/ws/{}@kline_1m".format(symbol.lower())]

		self.THREADS = []

		self.candles, self.closes = self.candle_initiation()

		self.ws = None
		self.is_running = False

		print("---candle crawler created")

	def candle_initiation(self):

		# return list
		klines = self.client.get_historical_klines(self.symbol.upper(), Client.KLINE_INTERVAL_1MINUTE, "1 day ago UTC")
		candles = [{
						'open' : float(i[1]), 
						'high' : float(i[2]), 
						'low' : float(i[3]), 
						'close' :float(i[4])
					} for i in klines]

		closes = [float(i[4]) for i in klines]


		return candles, closes[:-1] 

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
											on_message = lambda ws,msg: self._wss_on_message(ws, msg, callback))
		self.ws.run_forever()


	def _wss_on_open(self, ws):

		print("open")

	def _wss_on_close(self, ws):

		print("close")

	def _wss_on_error(self, ws, error):

		print("error: ", error)

	def _wss_on_message(self, ws, msg, callback):

		msg = json.loads(msg)

		if msg['k']['x'] == True:
			candle = {
						'open' : float(msg['k']['o']), 
						'high' : float(msg['k']['h']), 
						'low' : float(msg['k']['l']), 
						'close' :float(msg['k']['c'])
					}

			self.candles.append(candle)
			self.closes.append(float(msg['k']['c']))

			if len(self.closes) > 1440:
				del self.closes[0]

			callback()

	def stop(self):

		self.ws.keep_running = False
		self.is_running = False

if __name__ == "__main__":
	pass