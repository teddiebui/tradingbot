import collections
import pprint
import threading
import time
import datetime

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException

from ..crawler import candleCrawler as cc
from ..indicator import indicator as ind
from ..orderMaker import orderMaker as om

from .alertBot import AlertBot

class TradingBot(threading.Thread):

	def __init__(self, client, symbol, algorithm, order_maker = None, test_mode = False):
		threading.Thread.__init__(self)
		self.is_running = False

		self.test_mode = test_mode
		self.client = client
		self.symbol = symbol
		self.algorithm = algorithm

		#initiating objects
		self.alert_bot = AlertBot()
		self.indicator = ind.Indicator()
		self.order_maker = order_maker

		if test_mode == False:
			self.candle_crawler = cc.CandleCrawler(client, symbol)
			self._refresh_indicator() #initiate indicator lists

		print("...trading bot created")
		

	def crawl_klines(self):

		# CALCULATE EVERY MINTUE
		self.candle_crawler.start_crawling(callback=self._refresh_indicator)
		
	def _refresh_indicator(self):

		# this is a callback function passed to candle crawler object
		# refreshes indicator after receiving new candle
		self.indicator.update(self.candle_crawler.candles)

		# check for buying signal
		if self.test_mode == False:
			self._check_if_can_buy()

	def _check_if_can_buy(self):

		#TODO: finish trading algorithm for bot
		if not self.order_maker.is_in_position :
			signal = self.algorithm.run(self.candle_crawler.candles, self.indicator)
			if signal == True:
				#MAKE ORDER
				pass


	def _back_test_algorithm(self):

		print("back test the given algorithm")
		import os
		import json
		from collections import deque
		import re

		#GET PATH TO DIRECTORY "C:\users\{path_to_your_binanceApi}\candle_data\{symbol}\"
		directory_path = os.path.dirname(os.path.dirname(__file__)) + "\\candle_data\\" + self.symbol.lower()

		#SORT ALL THE FILES IN DIRECTORY ABOVE
		a = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
		b = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

		def callback(filename):
			month = re.findall(r"[A-Z][a-z]{2}", filename)[0]
			year = int(re.findall(r"\d{4}", filename)[0])
			return (year,b[a.index(month)])
		files = os.listdir(directory_path)
		files.sort(key=callback)

		#INITIATION

		candles = deque(maxlen = 120)
		counter = 0

		#MAIN START HERE
		#TODO: loop thru every json file
		for file in files[11:]:
			file = directory_path+"\\"+file
			if os.path.isfile(file) and file.endswith(".json"):
				total = time.time()
				candle_time = 0
				algorithm_time = 0
				order_time = 0
				load_json = 0



				#TODO: load json data

				with open(file, "r") as json_file:
					a=time.time()
					# klines = self.client.get_historical_klines(self.symbol.upper(), Client.KLINE_INTERVAL_1MINUTE, "30 day ago UTC")
					klines = json.load(json_file)
					print("load json file time: {:0.02f}".format(time.time()-a))
					print(file)
					load_json = time.time() - a


				#TODO: loop thru candle lines. For each candle, update indicator and run algorithm

				for each in klines[:]:
					if self.is_running == False:
						return
					# print(datetime.datetime.fromtimestamp(float(each[0])/1000))
					a=time.time()
					candle = {
						'time' : float(each[0]),
						'open' : float(each[1]), 
						'high' : float(each[2]), 
						'low' : float(each[3]), 
						'close' :float(each[4])
					}
					candles.append(candle)
					candle_time += (time.time() - a)

					
					if not self.order_maker.is_in_position:

						#TODO: run algorithm
						c=time.time()
						signal = self.algorithm.run(candles, self.indicator)
						algorithm_time += (time.time() - c)
						d = time.time()


						if signal == True:

								#create fake order if signal is true
								self.order_maker.fake_buy(candle['close'])
								print(datetime.datetime.fromtimestamp(float(candle['time'])/1000), "...place fake order, buy price: ", candle['close'])
					else:
						self.order_maker.check_current_fake_position(candle)
						if not self.order_maker.is_in_position:
							print(datetime.datetime.fromtimestamp(float(candle['time'])/1000), "...{}, price: {},candle low: {}, candle high: {}".format(
								self.order_maker.orders[len(self.order_maker.orders)][1]['type'],
								self.order_maker.orders[len(self.order_maker.orders)][1]['price'],
								candle['low'],
								candle['high'])
							)
							# pprint.pprint(self.order_maker.orders[len(self.order_maker.orders)])

					order_time += (time.time() - d)

					#DEBUG
					# print("total: {:0.02f}--candle: {:0.02f}--update: {:0.02f}--algorithm: {:0.02f}--datetime: {}".format(
					# 	time.time() - a,
					# 	b-a,
					# 	c-b,
					# 	d-c,
					# 	str(datetime.datetime.fromtimestamp(float(each[0])/1000))
					# 	))

					

				#on inner loop exit, do back test log
				self.order_maker.back_test_log()
				self.report()
				print("total: {:0.04f}--load_json: {:0.02f}--candle: {:0.04f}--algorithm: {:0.02f}--order: {:0.02f}".format(
						time.time() - total,
						load_json,
						candle_time,
						algorithm_time,
						order_time)
						)

		return
		

	def log(self):

		self.order_maker.log()


	def run(self):
		self.is_running = True

		if not self.test_mode:
			self.crawl_klines()
		else:
			self._back_test_algorithm()

	


	def stop(self):
		self.report()

		self.is_running = False

		if not self.test_mode:
			self.candle_crawler.stop()
			self.order_maker.stop()
			print("..bot stopped")

	def report(self):
		count = 0
		loss = 0
		gain = 0

		for value in self.order_maker.orders.values():
			if len(value) == 2:
				if value[1]['type'] == "STOP_LOSS_LIMIT":
					loss += 1
				else:
					gain += 1
				count += 1

		metadata = {
			'orders' : count,
			'gain' : gain,
			'loss' : loss,
			'winRate' : round(gain/count*100,4),
			'orderMaker' : {
				'stake' : self.order_maker.stake,
				'takeProfit' : self.order_maker.take_profit,
				'stopLoss' : self.order_maker.stop_loss,
				'fee'	: self.order_maker.fee,
				'discount' : self.order_maker.discount}
		}
		# print("-------")
		# print("orders: ", count)
		# print("gain: {}/{}".format(gain, count))
		# print("loss: {}/{}".format(loss, count))
		# print("win rate: {:0.04f}%".format(gain/count*100))

		pprint.pprint(metadata)
		

if __name__ == "__main__":
	pass
