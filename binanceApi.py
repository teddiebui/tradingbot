import time
import pprint
import datetime
import os
import talib
import numpy
import threading
import json
import queue
import re
import socket
import collections
import pprint
import os
import tkinter as tk
import websocket
import talib

from tkinter import *
from binance.enums import *
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException

import crawler.priceCrawler as pc
import crawler.candleCrawler as cc



class MainApplication:

	def __init__(self):

		self.w = tk.Tk()
		self.w.geometry('1024x640')
		self.w.title('TRADING BOT for CRYPTOCURRENCY')

		self.addLoginButton()

		self.THREADS = []

		self.price_is_crawling = False
		self.candle_is_crawling = False

		self.candle_crawler = None 
		self.price_crawler = None 

		self.candle_closes = []
		self.rsi = []


	def run(self):
		self.w.mainloop()

	def addLoginButton(self):

		self.loginButton = tk.Button(self.w, 
									text="Log In", 
									command=self.login,
									bg="white",
									width="30",
									height="2", 
									font=("Calibri", 13)).pack()

	def loginProcess(self, apiKey="", apiSecret=""):
		print("log in")

	# define login function
	def login(self):
	    
	    self.loginScreen = Toplevel(self.w)
	    self.loginScreen.title("Login")
	    self.loginScreen.geometry("600x450")
	    Label(self.loginScreen, text="Please enter details below to login").pack()
	    Label(self.loginScreen, text="").pack()

	    global apiKeyEntry
	    global apiSecretEntry
	 
	    Label(self.loginScreen, text="apiKey: ").pack()
	    apiKeyEntry = Entry(self.loginScreen, width="200")
	    apiKeyEntry.pack()

	    Label(self.loginScreen, text="").pack()
	    Label(self.loginScreen, text="apiSecret: ").pack()
	    apiSecretEntry = Entry(self.loginScreen, width="200")
	    apiSecretEntry.pack()

	    Label(self.loginScreen, text="").pack()
	    Button(self.loginScreen, text="Login", width=10, height=1, command=self.login_verification).pack()




	def login_verification(self):

		apiKey = apiKeyEntry.get()
		apiSecret = apiSecretEntry.get()

		print("apiKey: ---{}---".format(apiKey)) #debug
		print("apiSecrect: ---{}---".format(apiSecret)) #debug

		self.client = Client(apiKey, apiSecret)
		self.price_crawler = pc.PriceCrawler(self.client)
		self.candle_crawler = cc.CandleCrawler(self.client)

		# self.client = Client(apiKey, apiSecret, {'verify': True, 'timeout' : 5}) #deprecated
		self.loginScreen.destroy()
		
		info = self.client.get_account() #testing credentials
		pprint.pprint(info)

		# CLEANUP FUNCTION
		self.login_cleaning()


	def login_cleaning(self):

		#cleanup
		self.w.destroy()

		#start window again

		self.w = tk.Tk()
		self.w.geometry('1024x640')
		self.w.title('TRADING BOT for CRYPTOCURRENCY')

		self.add_widgets()


	def add_widgets(self):

		#CRAWL PRICE WIDGETS
		Label(self.w, text="Enter symbol to crawl price (ex: BNBUSDT): ").pack()
		self.symbol_price = Entry(self.w, width="50")
		self.crawl_price_button = Button(self.w, text="Start Price Crawling", command=self.crawl_price)

		self.symbol_price_label = Label(self.w, text="")
		self.price_label = Label(self.w, text="")

		self.symbol_price.pack()
		self.crawl_price_button.pack()
		self.symbol_price_label.pack()
		self.price_label.pack()

		#CRAWL CANDLE WIDGETS
		Label(self.w, text="Enter symbol to crawl candle (ex: BNBUSDT): ").pack()
		self.symbol_candle = Entry(self.w, width="50")
		self.crawl_candle_button = Button(self.w, text="Start Candle Crawling", command=self.crawl_candle)

	
		self.symbol_candle_label = Label(self.w, text="Candle closes price list: ")
		self.candle_label = Label(self.w, text="")

		self.symbol_candle.pack()
		self.crawl_candle_button.pack()
		self.symbol_candle_label.pack()
		self.candle_label.pack()

		#RSI WIDGETS

		self.rsi_label = Label(self.w, text="RSI: ")
		self.rsi_value_label = Label(self.w, text="")

		self.rsi_label.pack()
		self.rsi_value_label.pack()




		self.w.mainloop()

	def crawl_price(self):

		#get symbol input
		symbol_price = self.symbol_price.get()
		print("crawl price, symbol: ", symbol_price)



		self.symbol_price_label.configure(text=symbol_price.upper())
		#start price crawler
		self.price_crawler.start_crawling()

		#create crawl price thread
		thread = threading.Thread(target=self.crawl_price_handler, args=(symbol_price,))
		self.THREADS.append(thread)
		thread.start()

		#configure button from crawl to stop crawl
		self.crawl_price_button.configure(text="Stop Crawling Price", command=self.stop_crawling_price)


	def crawl_price_handler(self, symbol_price):

		self.price_is_crawling = True

		try:
			while self.price_is_crawling == True:
				print(self.price_is_crawling)

				self.prices = self.price_crawler.get_price_list()

				for i in self.prices:
					if i['symbol'] == symbol_price.upper():
						self.price_label.configure(text = i['price'])
				# self.price_label.configure(text = self.price['price'])

				if self.price_is_crawling == False:
					print("crawl price back test done")
					break

				time.sleep(0.25)
		except Exception as e:
			print(repr(e))
		finally:
			self.price_crawler.terminate()

	def stop_crawling_price(self):

		self.price_is_crawling = False
		print("stop crawling price: ", self.price_is_crawling)
		self.crawl_price_button.configure(text="Start PriceCrawling", command=self.crawl_price)
		# self.symbol_price_label.configure(text="")
		# self.price_label.configure(text="")


	def crawl_candle(self):

		#get symbol input
		symbol_candle = self.symbol_candle.get()
		print("crawl candle, symbol: ", symbol_candle)

		#initiation
		klines = client.get_historical_klines(symbol_candle.upper(), Client.KLINE_INTERVAL_1MINUTE, "1 day ago UTC")

		self.candle_closes = [float(i[4]) for i in klines] 
		del self.candle_closes[-1]
		self.rsi = list(talib.RSI(numpy.array(self.candle_closes)))
		self.rsi = list(map(lambda x: round(x,2), self.rsi))

		self.candle_label.configure(text=str(self.candle_closes[-14:]))
		self.rsi_value_label.configure(text=str(self.rsi[-14:]))

		#start price crawler
		self.candle_crawler.start_crawling(symbol_candle)

		#create crawl price thread
		thread = threading.Thread(target=self.crawl_candle_handler, args=(symbol_candle,))
		self.THREADS.append(thread)
		thread.start()

		#configure button from crawl to stop crawl
		self.crawl_candle_button.configure(text="Stop Crawling Candle", command=self.stop_crawling_candle)


	def crawl_candle_handler(self, symbol_candle):
		
		self.candle_is_crawling = True

		try:
			while self.candle_is_crawling == True:

				candle = json.loads(self.candle_crawler.get_candle())

				if candle['k']['x'] == True:
					self.candle_closes.append(float(candle['k']['c']))
					self.candle_label.configure(text=str(self.candle_closes[-14:]))

					self.rsi = list(talib.RSI(numpy.array(self.candle_closes)))
					self.rsi = list(map(lambda x: round(x,2), self.rsi))
					self.rsi_value_label.configure(text=str(self.rsi[-14:]))

					if len(self.candle_closes) > 1440:
						del self.candle_closes[0]

					print("len candles: ", len(self.candle_closes))

				if self.candle_is_crawling == False:
					print("crawl candle back test done")
					break

		except Exception as e:
			print(e)
		finally:
			self.candle_crawler.terminate()

	def stop_crawling_candle(self):

		self.candle_is_crawling = False
		print("stop crawling candle")
		self.crawl_candle_button.configure(text="Start Candle Crawling", command=self.crawl_candle)
	

	def create_websocket(self):
		self.ws = websocket.WebSocketApp()

	def cleanup(self):

		# self.candle_crawler.terminate()
		self.price_crawler.terminate()




if __name__ == "__main__":

	client = Client("TFWFmx5lPFNkkQnEIQsl2596kr1errGmaabzC3bFWI17mifeIYmnBybtU4Opkkyp", "kBzXtdMQsOVCrfV9qwyCabshmyALX3ABNjzGJF2a7ZoHF7oh6lzh4gEuvHOwQBSR")

	# # info = client.get_account() #testing credentials
	# # pprint.pprint(info)
	# client = Client("TFWFmx5lPFNkkQnEIQsl2596kr1errGmaabzC3bFWI17mifeIYmnBybtU4Opkkyp", "kBzXtdMQsOVCrfV9qwyCabshmyALX3ABNjzGJF2a7ZoHF7oh6lzh4gEuvHOwQBSR")


	try:
		main = MainApplication()
		main.run()
	except:
		print("some error occur")
		main.cleanup()

	# try:
	# 	p = pc.PriceCrawler(client)
	# 	p.start_crawling()
	# 	while True:
	# 		p.get_price_list()
	# except KeyboardInterrupt as e:
	# 	print(repr(e))
	# 	print("ENDDDDDDDDDDDDDDD")
	# 	p.terminate()
