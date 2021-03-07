import math

class PriceMaker():

	def __init__(self, stake, take_profit, stop_loss, fee, discount):

		self.stake = stake
		self.take_profit = take_profit
		self.stop_loss = stop_loss
		self.fee = fee
		self.discount = discount

		print("...price maker created")

	def get_break_even_price(self, buy_price):

		fee = self.fee*(1-self.discount)
		price = buy_price*(1+fee)/(1-fee)
		price = math.ceil(price*1.00001*10000)/10000 # round up to 4 decimal points of float
		return price

	def get_take_profit_price(self, buy_price):

		fee = self.fee*(1-self.discount)
		price =buy_price*(1+fee)/(1-fee) + self.take_profit*buy_price/(1-fee)
		price = math.ceil(price*1.00001*10000)/10000 # round up to 4 decimal points of float
		return price

	def get_stop_loss_price(self, buy_price):

		fee = self.fee*(1-self.discount)
		price = buy_price*(1+fee)/(1-fee) - self.stop_loss/(1+self.stop_loss)*buy_price/(1-fee)
		price = math.ceil(price*1.00001*10000)/10000 # round up to 4 decimal points of float
		return price

if __name__ == "__main__":

	# back testing
	p = PriceMaker(stake=20, 
										take_profit=0.02, 
										stop_loss=0.02, 
										fee=0.000, 
										discount = 0.0)

	buy_price = 100

	print(p.get_take_profit_price(buy_price))
	print(p.get_stop_loss_price(buy_price))


