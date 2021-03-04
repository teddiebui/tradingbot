import pprint

from binance.enums import *
from binance.exceptions import BinanceAPIException, BinanceOrderException

from ..priceMaker import priceMaker as pm


class OrderMaker(pm.PriceMaker):

	def __init__(self, client, symbol, stake, take_profit, stop_loss, fee, discount):

		pm.PriceMaker.__init__(self, stake, take_profit, stop_loss, fee, discount)
		self.client = client
		self.symbol = symbol
		print("...order maker created")

	def create_order_buy_market(self):


		# order = self.client.order_market_buy(
		# 		    symbol= self.symbol.upper(),
		# 		    quoteOrderQty= self.stake)
		# pprint.pprint(order)
		order = None
		print(self.stake)
		print(self.take_profit)
		print(self.stop_loss)
		print(self.fee)
		print(self.discount)
		print()


		print("buy price: ", self.stake)
		print("break even price: ", self.get_break_even_price())

		price = self.get_take_profit_price()
		print("take profit price: ", price)

		price = self.get_stop_loss_price()
		print("stop loss price = ", price)


		# order = self.client.create_oco_order(
		# 							symbol=self.symbol.upper(),
		# 							side=SIDE_SELL,
		# 							quantity=0.05,
		# 							stopLimitTimeInForce=TIME_IN_FORCE_GTC,
		# 							stopPrice=self.get_stop_loss_price(),    # <= stopPrice will trigger stopLimitPrice
		# 							stopLimitPrice=self.get_stop_loss_price(),  # stop loss price
		# 							price=self.get_take_profit_price()) # take profit price)

		return order
	
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

	
