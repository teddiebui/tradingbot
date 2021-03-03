import tkinter as tk
import time
import threading

class PriceMaker():

	def __init__(self):

		self.fee_spot = 0.001
		self.discount = 0.25
		self.target_profit = 0.01
		self.stop_loss = 0.01

		print("price maker created")

	def get_break_even_price(self, buy_price):

		fee = self.fee_spot*(1-self.discount)
		return round(buy_price*(1+fee)/(1-fee),4)

	def get_take_profit_price(self, buy_price):

		fee = self.fee_spot*(1-self.discount)
		return round(buy_price*(1+fee)/(1-fee) + self.target_profit*buy_price/(1-fee),4)

	def get_stop_loss_price(self, buy_price):

		fee = self.fee_spot*(1-self.discount)

		return round(buy_price*(1+fee)/(1-fee) - self.stop_loss*buy_price/(1-fee),4)



if __name__ == "__main__":

	# back testing
	
	pm = PriceMaker()

	pm.discount = 0
	def back_test(old_price, new_price):
		total_fee = round(pm.fee_spot*(1-pm.discount)*(old_price + new_price),4)
		print("total fee: ", total_fee)
		print("new_price - old_price: ", round(new_price - old_price,4))
		print("net PNL: ", round(new_price - old_price - total_fee,2))

	buy_price = 200

	print("buy price: ", buy_price)

	print()
	break_even_price = pm.get_break_even_price(buy_price)
	print("break even price: ", break_even_price)
	back_test(buy_price, break_even_price)

	print()
	target_price = pm.get_take_profit_price(buy_price)
	print("take profit price: ", target_price)
	back_test(buy_price, target_price)

	print()
	stop_loss_price = pm.get_stop_loss_price(buy_price)
	print("stop loss price: ", stop_loss_price)
	back_test(buy_price, stop_loss_price)