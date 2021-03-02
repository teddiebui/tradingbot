import threading
import websocket
import time
import pprint
import queue
import json


class CandleCrawler:

	def __init__(self, client):

		self.client = client
		self.symbol = ""
		self.is_running = False

		self.WEBSOCKETS = ["wss://stream.binance.com:9443/ws/symbol@kline_1m"]
		self.THREADS = []

		self.candles = queue.Queue()
		self.candle = None

		self.ws = None

	def start_crawling(self, symbol):
		self.symbol = symbol
		self.is_running = True

		thread = threading.Thread(target=self._start_crawling_handler, args=(self.symbol,))
		thread.start()
		self.THREADS.append(thread)

	def get_candle(self):

		try:
			self.candle = self.candles.get(timeout=5)
			return self.candle
		except Exception as e:
			print(repr(e))

	def _start_crawling_handler(self, symbol):

		self.symbol = symbol

		socket = self.WEBSOCKETS[-1].replace("symbol", symbol.lower())
		print(socket)
		self.ws = websocket.WebSocketApp(socket,
											on_open = lambda ws: self._wss_on_open(ws),
											on_error = lambda ws, error: self._wss_on_error(ws, error),
											on_close = lambda ws: self._wss_on_close(ws),
											on_message = lambda ws,msg: self._wss_on_message(ws, msg))
		self.ws.run_forever()


	def _wss_on_open(self, ws):

		print("open")

	def _wss_on_close(self, ws):

		print("close")

	def _wss_on_error(self, ws, error):

		print("error: ", error)

	def _wss_on_message(self, ws, msg):

		self.candles.put(msg)
		msg = json.loads(msg)
		if msg['k']['x'] == True:
			pprint.pprint(msg)
		else:
			print("..received")


	def terminate(self):
		print("terminate")
		self.ws.keep_running = False
		self.is_running = False

def handler():
	count = 0
	def connect():
		print("connecting")
	while True:
		print("hello")
		count += 1
		time.sleep(0.25)

		if count % 10 == 0:
			connect()


if __name__ == "__main__":

	## BACK TESTING

	from binance.client import Client

	client = Client("TFWFmx5lPFNkkQnEIQsl2596kr1errGmaabzC3bFWI17mifeIYmnBybtU4Opkkyp", "kBzXtdMQsOVCrfV9qwyCabshmyALX3ABNjzGJF2a7ZoHF7oh6lzh4gEuvHOwQBSR")

	c = CandleCrawler(client)

	c.start_crawling("BNBUSDT")

	count = 0

	a= time.time()

	while True:
		count+=1
		c.get_candle()
		print("count: ", 1)
		if count == 100:
			b = time.time()
			c.terminate()
			print("terminate ws")
			time.sleep(0.25)
			break

	cc = time.time()
	print("time lapsed: ", cc - a)
	print("time terminating ws: ", cc - b)


