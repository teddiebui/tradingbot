

import threading
import time
import queue



import pprint

class PriceCrawler:

	def __init__(self, client):

		self.prices_list = []
		self.prices=[]
		self.client = client
		self.THREADS = []
		self.is_running = False


	def price(self,symbol):

		for i in self.price_list:
			if i['symbol'] == symbol:
				return i['price'][:-4]

	def start_crawling(self):

		thread = threading.Thread(target=self._start_crawling_handler, args=())
		thread.start()
		self.THREADS.append(thread)


	def get(self, symbol=""):

		if not symbol: #return a dict
			return self.prices_list.get(timeout=1)

		#return a float 
		self.prices = self.prices_list.get(timeout=1)
		for i in self.prices:
			if i['symbol'].upper() == symbol.upper():
				return float(i['price'])

		return 0

	def terminate(self):

		print("terminate")
		self.is_running = False


	def _start_crawling_handler(self):

		self.is_running = True
		count = 0
		a = time.time()
		while self.is_running == True:
			b = time.time()

			self.prices_list.append(self.client.get_all_tickers())

			if len(self.prices_list) > 14:
				del self.prices_list[0]

			#internal counter
			count += 1


			#debug
			done = time.time() - b
			print("--time: {:5.2f} -- lapsed: {:5.2f} -- count: {}--".format(
				done, 
				time.time() - a,
				count))
			if done < 0.25:
				time.sleep(0.25-done)

if __name__ == "__main__":

	## BACK TESTING

	from binance.client import Client

	client = Client("TFWFmx5lPFNkkQnEIQsl2596kr1errGmaabzC3bFWI17mifeIYmnBybtU4Opkkyp", "kBzXtdMQsOVCrfV9qwyCabshmyALX3ABNjzGJF2a7ZoHF7oh6lzh4gEuvHOwQBSR")

	p = PriceCrawler(client)

	p.start_crawling()

	try:
		while True:
			p.get_price_list()
	except KeyboardInterrupt as e:
		print(repr(e))
		p.terminate()
	
