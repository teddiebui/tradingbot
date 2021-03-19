from binance.enums import *
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException

import json
import pprint
import time
import os
import re

client = Client("TFWFmx5lPFNkkQnEIQsl2596kr1errGmaabzC3bFWI17mifeIYmnBybtU4Opkkyp", "kBzXtdMQsOVCrfV9qwyCabshmyALX3ABNjzGJF2a7ZoHF7oh6lzh4gEuvHOwQBSR")
symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'LTCUSDT', 'BNBUSDT']
date = [["1 Feb, 2021", "1 Mar, 2021"],
		["1 Jan, 2021", "1 Feb, 2021"],
		["1 Dec, 2020", "1 Jan, 2021"],
		["1 Nov, 2020", "1 Dec, 2020"],
		["1 Oct, 2020", "1 Nov, 2020"],
		["1 Sep, 2020", "1 Oct, 2020"],
		["1 Aug, 2020", "1 Sep, 2020"],
		["1 Jul, 2020", "1 Aug, 2020"],
		["1 Jun, 2020", "1 Jul, 2020"],
		["1 May, 2020", "1 Jun, 2020"],
		["1 Apr, 2020", "1 May, 2020"],
		["1 Mar, 2020", "1 Apr, 2020"],
		["1 Feb, 2020", "1 Mar, 2020"],
		["1 Jan, 2020", "1 Feb, 2020"]]

for symbol in symbols[-1:]:
	path = os.path.dirname(os.path.dirname(__file__))
	os.makedirs(path+"\\candle_data\\"+symbol.lower(), exist_ok = True)
	for d in date[-1:]:
		a = time.time()
		klines = client.get_historical_klines(symbol, Client.KLINE_INTERVAL_1MINUTE, d[0], d[1])
		b = time.time()
		# klines = ['a']
		pprint.pprint("{} fetch time: {:0.02f}".format(symbol, b-a))

		
		
		year = re.findall(r"\d{4}", d[0])[0]
		month = re.findall(r"\w{3}", d[0])[0]
		with open(path+"\\candle_data\\{}\\{}_data_{}_{}.json".format(symbol.lower(),symbol.lower(),year,month), "w") as file:
			json.dump(klines, file)
