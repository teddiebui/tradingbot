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
		

		self.WEBSOCKETS = [
			"wss://stream.binance.com:9443/ws/{}@kline_1m".format(symbol.lower()),
			"wss://stream.binance.com:9443/ws/{}@kline_15m".format(symbol.lower())
			]
		self.THREADS = []

		a = time.time()
		self.candles_1m = self.candle_initiation(Client.KLINE_INTERVAL_1MINUTE, "1 day ago UTC")
		self.candles_15m = self.candle_initiation(Client.KLINE_INTERVAL_15MINUTE, "1 day ago UTC")
		self.candles_30m = []
		self.candles_1h = self.candle_initiation(Client.KLINE_INTERVAL_1HOUR, "1 day ago UTC")
		self.candles_2h = []
		self.candles_4h = self.candle_initiation(Client.KLINE_INTERVAL_1HOUR, "4 day ago UTC")
		self.candles_1d = []
		self.candles_3d = []
		self.candles_1w = []

		self.ws = None
		self.is_running = False


	def candle_initiation(self,interval, time):

		# return  a list
		klines = self.client.get_historical_klines(self.symbol.upper(), interval, time)

		return [{'time': float(i[0])/1000,
				'open' : float(i[1]), 
				'high' : float(i[2]), 
				'low' : float(i[3]), 
				'close' :float(i[4])
				} for i in klines]

	def start_crawling(self, callback1 = None, callback2 = None):

		self.is_running = True

		thread = threading.Thread(target=self._start_crawling_handler, args=(callback1, callback2))
		thread.start()
		self.THREADS.append(thread)

	

	def _start_crawling_handler(self, callback1 = None, callback2 = None):


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

	def _wss_on_message(self, ws, msg, callback1 = None, callback2 = None):

		msg = json.loads(msg)
		pprint.pprint('hi...' + self.symbol.upper())
		# pprint.pprint(msg)
		# pprint.pprint(self.candles_15m)
		candle = 	{'time': float(msg['k']['t'])/1000,
						'open' : float(msg['k']['o']), 
						'high' : float(msg['k']['h']), 
						'low' : float(msg['k']['l']), 
						'close' :float(msg['k']['c'])}
		
		self.candles_15m[-1] = candle

		if msg['k']['x'] == True:
			del self.candles[0]
			self.candles_15m.append(candle)


		if callback1 != None:
			callback1()

		if callback2 != None:
			callback2(float(msg['k']['c']))

		


		# pprint.pprint([[datetime.datetime.fromtimestamp(i['time']), i['close']] for i in self.candles_15m[-7:]])

	def stop(self):
		
		if self.ws:
			self.ws.keep_running = False
			self.is_running = False
			print("candle crawler stopped")

if __name__ == "__main__":
	
	pass