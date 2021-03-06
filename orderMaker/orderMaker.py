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
		print("...order maker created")
		self.orders = {}

	def create_order_buy_market(self):


		if self.is_in_position == False:
			order_market_buy = self.client.order_market_buy(
					    symbol= self.symbol.upper(),
					    quoteOrderQty= self.stake)
			print("...order buy created")
			self.orders[order_market_buy['orderId']] = [order_market_buy]

			buy_price, quantity = self._get_buy_price(order_market_buy)

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


			print("buy price: ", buy_price)
			print("quantity: ", quantity)
			print("stop loss: ", self.get_stop_loss_price(buy_price))
			print("take profit: ", self.get_take_profit_price(buy_price))

			self.is_in_position = True



			order_oco_sell = self.client.create_oco_order(
										symbol=self.symbol.upper(),
										side=SIDE_SELL,
										quantity=quantity,
										stopLimitTimeInForce=TIME_IN_FORCE_GTC,
										stopPrice=self.get_stop_loss_price(buy_price),    # <= stopPrice will trigger stopLimitPrice
										stopLimitPrice=self.get_stop_loss_price(buy_price),  # stop loss price
										price=self.get_take_profit_price(buy_price))  # take profit price)

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

			
			print("...order sell created")
			while True:
				time.sleep(6)
				orderId = int(order_oco_sell['orderReports'][0]['orderId'])
				transactions = self.client.get_all_orders(symbol = self.symbol, orderId = orderId)
				status = (transactions[0]['status'], transactions[1]['status'])
				print(status)
				for trans in transactions:
					if trans['status'] == 'FILLED':
						self.orders[order_market_buy['orderId']].append(trans)
						pprint.pprint(self.orders[order_market_buy['orderId']])
						self.is_in_position = False
						self._log_temp()
						print("...order sell finished")	

						return

	def stop(self):
		#TODO: cancel any
		print("order maker stop")

	def _get_buy_price(self, order):

		totalQty = 0
		totalVolume = 0

		for i in order['fills']:
			
			totalQty += float(i['qty'])
			totalVolume += float(i['price'])*float(i['qty'])

		return math.ceil(totalVolume/totalQty*10000)/10000, totalQty

	def _back_test_callback(self):

		print("....place fake order")

	def log(self):

		directory_path = os.path.dirname(os.path.dirname(__file__))

		os.makedirs(directory_path+"\\loggings". exist_ok = True)

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

	def back_test_log(self):

		directory_path = os.path.dirname(os.path.dirname(__file__))

		os.makedirs(directory_path+"\\loggings". exist_ok = True)

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



	def _log_temp(self):


		directory_path = os.path.dirname(os.path.dirname(__file__))

		os.makedirs(directory_path+"\\loggings". exist_ok = True)

		with open(
				os.path.join(directory_path,"loggings\\temp_order_log_.json"),'w', encoding='utf-8') as file:
			json.dump(self.orders,file)

		print("temporarily logged")


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

	
