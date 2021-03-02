
import threading
import time
import queue



import pprint

class PriceCrawler:

	def __init__(self, client):

		self.prices_list=queue.Queue()
		self.prices=[]
		self.client = client
		self.THREADS = []
		self.is_running = False


	def price(self,symbol):

		for i in self.price_list:
			if i['symbol'] == symbol:
				return i['price'][:-4]

	def start_crawling_handler(self):

		self.is_running = True
		count = 0
		a = time.time()
		while self.is_running == True:
			b = time.time()
			self.prices_list.put(self.client.get_all_tickers())
			count += 1
			done = time.time() - b
			print("--time: {:5.2f} -- lapsed: {:5.2f} -- count: {}--".format(
				done, 
				time.time() - a,
				count))
			if done < 0.25:
				time.sleep(0.25-done)
			### FOLLOWING LOGIC IS NOT WORKING
			# if done > 0.25:
			# 	print("connection slow, trying another..")
			# 	self.terminate()
			# 	self.get_price_list()
			#   return

	def start_crawling(self):

		thread = threading.Thread(target=self.start_crawling_handler, args=())
		thread.start()
		self.THREADS.append(thread)

	def get_price_list(self):

		try:
			self.prices = self.prices_list.get(timeout=1)
			return self.prices
		except Exception as e:
			print(repr(e))

	def terminate(self):

		print("terminate")
		self.is_running = False

			

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
	
