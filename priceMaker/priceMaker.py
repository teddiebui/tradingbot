import math

class PriceMaker():

	def __init__(self, stake, take_profit, stop_loss, fee, discount):

		self.stake = stake
		self.take_profit = take_profit
		self.stop_loss = stop_loss
		self.fee = fee
		self.discount = discount	
		print("...price maker created")

	def get_break_even_price(self):

		fee = self.fee*(1-self.discount)
		price = self.stake*(1+fee)/(1-fee)
		price = math.ceil(price*10000)/10000 # round up to 4 decimal points of float
		return price

	def get_take_profit_price(self):

		fee = self.fee*(1-self.discount)
		price = self.stake*(1+fee)/(1-fee) + self.take_profit*self.stake/(1-fee)
		price = math.ceil(price*10000)/10000 # round up to 4 decimal points of float
		return price

	def get_stop_loss_price(self):

		fee = self.fee*(1-self.discount)
		price = self.stake*(1+fee)/(1-fee) - self.take_profit*self.stake/(1-fee)
		price = math.ceil(price*10000)/10000 # round up to 4 decimal points of float
		return price

if __name__ == "__main__":

	# back testing
	
	pm = PriceMaker()
	pm.discount = 0

	print(pm.get_break_even_price())
	print(pm.get_take_profit_price())
	print(pm.get_stop_loss_price())

