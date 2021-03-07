import collections
import pprint
import threading
import time
import datetime
import os
import re

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException

from ..crawler import candleCrawler as cc
from ..indicator import indicator as ind
from ..orderMaker import orderMaker as om

from .alertBot import AlertBot

class TradingBot(threading.Thread):

	def __init__(self, client, symbol, algorithm = None, order_maker = None, test_mode = False):
		threading.Thread.__init__(self)
		self.is_running = False

		#initiating fields
		self.test_mode = test_mode
		self.client = client
		self.symbol = symbol
		self.algorithm = algorithm
		self.order_maker = order_maker

		#initiating objects
		self.alert_bot = AlertBot()
		self.indicator = ind.Indicator()
		
		if not test_mode:
			self.candle_crawler = cc.CandleCrawler(client, symbol)
			self._refresh_indicator() #initiate indicator lists

		print("...trading bot created")
		

	def crawl_klines(self):

		# CALCULATE EVERY MINTUE
		self.candle_crawler.start_crawling(callback1=self._refresh_indicator, callback2=self.order_maker.check_current_position)
		
	def _refresh_indicator(self):

		# this is a callback function passed to candle crawler object
		# refreshes indicator after receiving new candle
		self.indicator.update(self.candle_crawler.candles)

		if not self.order_maker.is_in_position:
			self._check_if_can_buy()

	def _check_if_can_buy(self):

		#TODO: finish trading algorithm for bot
		if not self.order_maker.is_in_position:
			# find a signal to buy if currently not in position
			signal = self.algorithm.run(self.candle_crawler.candles, self.indicator)
			if signal == True:
				#MAKE ORDER
				pass

	def _back_test_algorithm(self):

		import json
		from collections import deque
		

		candles = deque(maxlen = 400)
		counter = 0
		files = self._get_json_data_from_storage()
		directory_path = os.path.dirname(os.path.dirname(__file__)) + "\\candle_data\\" + self.symbol.lower()

		
		total = time.time()
		candle_time = 0
		algorithm_time = 0
		order_time = 0
		load_json = 0	

		#MAIN START HERE
		#TODO: load json data
		for file in files:
			file = directory_path + "\\" + file

			with open(file, "r") as f:
				a = time.time()
				klines = json.load(f)
				print(file)
				print("load json file time: ", time.time() - a)

				# a=time.time()
				klines = self.client.get_historical_klines(self.symbol.upper(), Client.KLINE_INTERVAL_15MINUTE, "360 day ago UTC")
				# print("load json data time: {:0.02f}".format(time.time()-a))
				# load_json = time.time() - a
				#TODO: loop thru candle lines. For each candle, update indicator and run algorithm
				for each in klines[:]:
					if self.is_running == False:
						return
					# print(datetime.datetime.fromtimestamp(float(each[0])/1000))

					a=time.time()
					candle = {'time' : float(each[0]),
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
								self.order_maker.buy(buy_price=candle['close'], test_mode = self.test_mode)
								print(datetime.datetime.fromtimestamp(float(candle['time'])/1000), "...place fake order, buy price: ", candle['close'])
					else:
						self.order_maker.check_current_position(candle['close'])
						if not self.order_maker.is_in_position:

							print(datetime.datetime.fromtimestamp(float(candle['time'])/1000), "...{}, price: {},candle low: {}, candle high: {}".format(
								self.order_maker.orders[len(self.order_maker.orders)][1]['type'],
								self.order_maker.orders[len(self.order_maker.orders)][1]['price'],
								candle['low'],
								candle['high']))
							# pprint.pprint(self.order_maker.orders[len(self.order_maker.orders)])

					order_time += (time.time() - d)

				#on inner loop exit, do back test log
				self.order_maker.back_test_log()
				self.report()

				#debug
				print("total: {:0.04f}--load_json: {:0.02f}--candle: {:0.04f}--algorithm: {:0.02f}--order: {:0.02f}".format(
						time.time() - total,
						load_json,
						candle_time,
						algorithm_time,
						order_time)
						)
			return

		return
		
	def _get_json_data_from_storage(self):
		#for back test at a long period

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

		return files


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
			'pnlPercentage' : (gain*100*self.order_maker.take_profit) - (loss * 100 * self.order_maker.stop_loss),
			'symbol' : self.symbol,
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
