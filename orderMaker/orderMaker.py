import pprint
import math
import datetime
import time
import json
import os

from binance.enums import *
from binance.exceptions import BinanceAPIException, BinanceOrderException

from ..priceMaker import priceMaker as pm


class OrderMaker(pm.PriceMaker):

	def __init__(self, client, symbol, stake, take_profit, stop_loss, fee, discount):

		pm.PriceMaker.__init__(self, stake, take_profit, stop_loss, fee, discount)
		self.client = client
		self.symbol = symbol
		self.is_in_position = False
		self.current_position = None

		self.orders = {}


	def buy(self, test_mode = False, buy_price = 0.00):

		if self.is_in_position == False:

			order_market_buy = None

			quantity = 0

			if not test_mode:
				order_market_buy = self.client.order_market_buy(
						    symbol= self.symbol.upper(),
						    quoteOrderQty= self.stake)
				buy_price, quantity = self._get_buy_price(order_market_buy)
			else:
				order_market_buy = {'orderId' : len(self.orders) + 1, 'price' :  str(buy_price)}

			self.orders[order_market_buy['orderId']] = [order_market_buy]

			

			# EXAMPLE OF ORDER_MARKET_BUY

			# {'clientOrderId': 'ZeKx4wrRZdYL3idkcPbaON',
			# 'cummulativeQuoteQty': '10.84427520',
			# 'executedQty': '0.04800000',
			# 'fills': [{'commission': '0.00003600',
			#            'commissionAsset': 'BNB',
			#            'price': '225.92240000',
			#            'qty': '0.04800000',
			#            'tradeId': 165914884}],
			# 'orderId': 1639119357,
			# 'orderListId': -1,
			# 'origQty': '0.04800000',
			# 'price': '0.00000000',
			# 'side': 'BUY',
			# 'status': 'FILLED',
			# 'symbol': 'BNBUSDT',
			# 'timeInForce': 'GTC',
			# 'transactTime': 1614958605886,
			# 'type': 'MARKET'}

			self.is_in_position = True

			take_profit_price = self.get_stop_loss_price(buy_price)
			stop_loss_price = self.get_take_profit_price(buy_price)

			order_oco_sell = None

			if not test_mode:
				order_oco_sell = self.client.create_oco_order(
										symbol=self.symbol.upper(),
										side=SIDE_SELL,
										quantity=quantity,
										stopLimitTimeInForce=TIME_IN_FORCE_GTC,
										stopPrice=stop_loss_price,    # <= stopPrice will trigger stopLimitPrice
										stopLimitPrice=stop_loss_price,  # stop loss price
										price=take_profit_price)  # take profit price)
			else:	
				order_oco_sell =  {'orderReports' : [{'type' : 'STOP_LOSS_LIMIT', 'status' : 'NEW', 'price' : str(take_profit_price)}, 
									{'type' : 'LIMIT_MAKER', 'status' : 'NEW', 'price' : str(stop_loss_price)}]}

			self.open_orders = { order_market_buy['orderId'] : order_oco_sell['orderReports']} # the list contains 2 dicts of TP and SL order
			self._log_temp()

			# EXAMPLE OF ORDER OCO SELL JSON

			# {'contingencyType': 'OCO',
			# 'listClientOrderId': 'xM4mCPJDxhoLLGBkVKsYt2',
			# 'listOrderStatus': 'EXECUTING',
			# 'listStatusType': 'EXEC_STARTED',
			# 'orderListId': 18376122,
			# 'orderReports': [{'clientOrderId': 'HvmvPgfPLccLBH4ppwM4CW',
			#                   'cummulativeQuoteQty': '0.00000000',
			#                   'executedQty': '0.00000000',
			#                   'orderId': 1639119368,
			#                   'orderListId': 18376122,
			#                   'origQty': '0.04800000',
			#                   'price': '224.02310000',
			#                   'side': 'SELL',
			#                   'status': 'NEW',
			#                   'stopPrice': '224.02310000',
			#                   'symbol': 'BNBUSDT',
			#                   'timeInForce': 'GTC',
			#                   'transactTime': 1614958606001,
			#                   'type': 'STOP_LOSS_LIMIT'},
			#                  {'clientOrderId': 'zfqMnRIjspbaNIoX4NcrM3',
			#                   'cummulativeQuoteQty': '0.00000000',
			#                   'executedQty': '0.00000000',
			#                   'orderId': 1639119369,
			#                   'orderListId': 18376122,
			#                   'origQty': '0.04800000',
			#                   'price': '228.52250000',
			#                   'side': 'SELL',
			#                   'status': 'NEW',
			#                   'symbol': 'BNBUSDT',
			#                   'timeInForce': 'GTC',
			#                   'transactTime': 1614958606001,
			#                   'type': 'LIMIT_MAKER'}],
			# 'orders': [{'clientOrderId': 'HvmvPgfPLccLBH4ppwM4CW',
			#             'orderId': 1639119368,
			#             'symbol': 'BNBUSDT'},
			#            {'clientOrderId': 'zfqMnRIjspbaNIoX4NcrM3',
			#             'orderId': 1639119369,
			#             'symbol': 'BNBUSDT'}],
			# 'symbol': 'BNBUSDT',
			# 'transactionTime': 1614958606001}

	def check_current_position(self, current_price):
		if self.is_in_position:
			for key, value in self.open_orders.items():
				orderId = key
				order_oco_sell = value

			stop_loss_order, take_profit_order = order_oco_sell

			if current_price >= float(take_profit_order['price']):
				take_profit_order['status'] = 'FILLED'
				self.orders[orderId].append(take_profit_order)
				self.is_in_position = False
				self._log_temp()
				return

			if current_price <= float(stop_loss_order['price']):
				stop_loss_order['status'] = 'FILLED'
				self.orders[orderId].append(stop_loss_order)
				self.is_in_position = False
				self._log_temp()
				return

	def _get_buy_price(self, order):

		totalQty = 0
		totalVolume = 0

		for i in order['fills']:
			
			totalQty += float(i['qty'])
			totalVolume += float(i['price'])*float(i['qty'])

		return math.ceil(totalVolume/totalQty*10000)/10000, totalQty


	def log(self):

		directory_path = os.path.dirname(os.path.dirname(__file__))

		os.makedirs(directory_path+"\\loggings", exist_ok = True)

		date_time = datetime.datetime.fromtimestamp(round(time.time()))

		path = "loggings\\{symbol}_{year}_{month}_{date}_{hour}_{minute}_{second}_order_log.json".format(
					symbol=self.symbol, 
					year = date_time.year,
					month = date_time.month,
					date = date_time.day,
					hour = date_time.hour,
					minute = date_time.minute,
					second = date_time.second
				)

		with open(os.path.join(directory_path, path), 'w', encoding='utf-8') as file:
			json.dump(self.orders,file)

		print("order maker logged")

	def _log_temp(self):


		directory_path = os.path.dirname(os.path.dirname(__file__))

		os.makedirs(directory_path+"\\loggings", exist_ok = True)

		with open(
				os.path.join(directory_path,"loggings\\temp_order_log_.json"),'w', encoding='utf-8') as file:
			json.dump(self.orders,file)

		print("temporarily logged")

	def back_test_log(self):

		directory_path = os.path.dirname(os.path.dirname(__file__))

		os.makedirs(directory_path+"\\test", exist_ok = True)

		date_time = datetime.datetime.fromtimestamp(round(time.time()))

		path = "test\\{symbol}_{year}_{month}_{date}_{hour}_{minute}_{second}_order_log.json".format(
					symbol=self.symbol, 
					year = date_time.year,
					month = date_time.month,
					date = date_time.day,
					hour = date_time.hour,
					minute = date_time.minute,
					second = date_time.second
				)

		with open(os.path.join(directory_path, path), 'w', encoding='utf-8') as file:
			json.dump(self.orders,file)

		print("back test order logged")

	def stop(self):
		#TODO: cancel any
		print("order maker stop")


if __name__ == "__main__":

	symbol = 'BNBUSDT'

	import pprint
	import datetime
	
	from binance.enums import *
	from binance.client import Client
	from binance.exceptions import BinanceAPIException, BinanceOrderException


	client = Client("TFWFmx5lPFNkkQnEIQsl2596kr1errGmaabzC3bFWI17mifeIYmnBybtU4Opkkyp","kBzXtdMQsOVCrfV9qwyCabshmyALX3ABNjzGJF2a7ZoHF7oh6lzh4gEuvHOwQBSR")

	# orders = client.get_all_orders(symbol='BNBUSDT', limit=5)
	# pprint.pprint(orders)

	# order = client.get_order(symbol='BNBUSDT', orderId='1630905114')
	# pprint.pprint(order)

	# trades = client.get_recent_trades(symbol=symbol)

	# trades = client.get_historical_trades(symbol=symbol)


	# trades = client.get_aggregate_trades(symbol=symbol)

	trades = client.get_my_trades(symbol=symbol)
	pprint.pprint(trades)

	
