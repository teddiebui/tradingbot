import threading
import websocket
import time
import pprint
import queue
import json
import datetime


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
		a = time. time()
		klines = self.client.get_historical_klines(self.symbol.upper(), Client.KLINE_INTERVAL_1MINUTE, "1 day ago UTC")
		b = time.time()
		candles = [{
						'open' : float(i[1]), 
						'high' : float(i[2]), 
						'low' : float(i[3]), 
						'close' :float(i[4])
					} for i in klines]

		c = time.time()
		closes = [float(i[4]) for i in klines]
		d = time.time()

		print("\t\tlen(klines): ", len(klines))
		print("\t\tlen(candles): ", len(candles))
		print("\t\tlen(closes): ", len(closes))
		print(b,c,d)
		print("total: {:000.02f}, fetch time: {:000.02f}, _candles: {:000.02f}, _closes: {:000.02f}".format(time.time()-a, b-a, c-b, d-c))
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
			pprint.pprint(msg)
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
		
		if self.ws:
			self.ws.keep_running = False
			self.is_running = False
			print("candle crawler stopped")

if __name__ == "__main__":
	
	pass