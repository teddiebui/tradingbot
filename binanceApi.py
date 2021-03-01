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
from tkinter import *
from binance.enums import *
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException



class MainApplication:

	def __init__(self):

		self.w = tk.Tk()
		self.w.geometry('1024x640')
		self.w.title('TRADING BOT for CRYPTOCURRENCY')

		self.addLoginButton()

		self.THREADS = []

		self.is_crawling = False


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
		# self.client = Client(apiKey, apiSecret, {'verify': True, 'timeout' : 5}) #deprecated
		self.loginScreen.destroy()
		
		info = self.client.get_account() #testing credentials
		pprint.pprint(info)

		del apiKey
		del apiSecret

		self.login_done()


	def login_done(self):

		self.w.destroy()

		self.w = tk.Tk()
		self.w.geometry('1024x640')
		self.w.title('TRADING BOT for CRYPTOCURRENCY')

		Label(self.w, text="Welcome to Trading BOT. let's get started").pack()
		Label(self.w, text="Enter symbol to crawl price(ex: BNBUSDT): ").pack()
		self.symbol = Entry(self.w, width="50", text="HELLO")
		self.symbol.pack()
		self.crawlPriceButton = Button(self.w, text="Crawl", command=self.crawlPrice)
		self.crawlPriceButton.pack()


		self.w.mainloop()

	def crawlPrice(self):

		#get symbol input
		symbol = self.symbol.get()
		print("crawl price, symbol: ", symbol)

		#create crawl price thread
		thread = threading.Thread(target=self.crawlPriceHandler, args=(symbol, len(self.THREADS) + 1),)
		self.THREADS.append(thread)
		thread.start()

		#delete controller
		self.crawlPriceButton.destroy()
		self.stopCrawlPriceButton = Button(self.w, text="Stop Crawling", command=self.stopCrawlPrice)
		self.stopCrawlPriceButton.pack()

		self.symbolLabel = Label(self.w, text="{}: ".format(symbol))
		self.priceLabel = Label(self.w, text="")

		self.symbolLabel.pack()
		self.priceLabel.pack()

	def crawlPriceHandler(self, symbol, threadID):

		print("thread {} start".format(threadID))

		self.is_crawling = True

		while True:

			self.price = self.client.get_symbol_ticker(symbol=symbol)
			print(self.price)

			self.priceLabel.configure(text = self.price['price'])

			if self.is_crawling == False:
				self.symbolLabel.destroy()
				self.priceLabel.destroy()
				print("crawl back test done")
				return

			time.sleep(0.25)

	def stopCrawlPrice(self):
		self.is_crawling = False
		print("stop crawling price")
		self.stopCrawlPriceButton.destroy()
		self.symbolLabel.configure(text="")
		self.priceLabel.copnfigure(text="")
		self.crawlPriceButton = Button(self.w, text="Crawl", command=self.crawlPrice)
		self.crawlPriceButton.pack()

if __name__ == "__main__":

	# info = client.get_account() #testing credentials
	# pprint.pprint(info)


	main = MainApplication()


	main.run()