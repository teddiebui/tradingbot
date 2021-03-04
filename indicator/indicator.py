import talib
import numpy
import pprint

class Indicator():

	def __init__(self):
		#rsi indicator variables
		self.OVERSOLD_THRESHOLD = 30
		self.OVERBOUGHT_THRESHOLD = 70
		self.rsi = []

		#macd indicator variables
		self.macd = []
		self.macd_signal = []
		self.macd_hist = []

		#ema
		self.ema_200 = []

		#dmi
		self.adx = []
		self.plus_di = []
		self.minus_di = []

		print("...indicator created")

	def refresh_rsi(self, close_list):

		# CALCULATE by callback function _refresh_indicator
		self.rsi = list(talib.RSI(numpy.array(close_list)))
		# just for prettifying
		self.rsi = list(map(lambda x: round(x,2), self.rsi))	
		#DEBUG 
		print()
		print("rsi: ", self.rsi[-4:])

	def refresh_macd(self, close_list):

		# CALCULATE by callback function _refresh_indicator
		self.macd, self.macd_signal, self.macd_hist = talib.MACD(
			numpy.array(close_list),
			fastperiod=12, 
			slowperiod=26, 
			signalperiod=9)

		# just for prettifying
		self.macd = list(map(lambda x: round(x,2), self.macd))
		self.macd_signal = list(map(lambda x: round(x,2), self.macd_signal))
		self.macd_hist = list(map(lambda x: round(x,2), self.macd_hist))

		#DEBUG
		print()
		print("macd: ", self.macd[-4:])	
		print("macd signal: ", self.macd_signal[-4:])	
		print("macd histogram: ", self.macd_hist[-4:])	

	def refresh_ema_200(self, close_list):

		# CALCULATE by callback function _refresh_indicator
		self.ema_200 = talib.EMA(numpy.array(close_list),200)
		# just for prettifying
		self.ema_200 = list(map(lambda x: round(x,2), self.ema_200))

		#DEBUG
		print()
		print("ema 200: ", self.ema_200[-4:])

	def refresh_dmi(self, candles):

		# CALCULATE by callback function _refresh_indicator
		self.adx = talib.ADX(
			numpy.array([i['high'] for i in candles]),
			numpy.array([i['low'] for i in candles]),
			numpy.array([i['close'] for i in candles]),
			14)
		self.plus_di = talib.PLUS_DI(
			numpy.array([i['high'] for i in candles]),
			numpy.array([i['low'] for i in candles]),
			numpy.array([i['close'] for i in candles]),
			14)
		self.minus_di = talib.MINUS_DI(
			numpy.array([i['high'] for i in candles]),
			numpy.array([i['low'] for i in candles]),
			numpy.array([i['close'] for i in candles]),
			14)

		# just for prettifying
		self.adx = list(map(lambda x: round(x,2), self.adx))
		self.plus_di = list(map(lambda x: round(x,2), self.plus_di))
		self.minus_di = list(map(lambda x: round(x,2), self.minus_di))

		#DEBUG 
		print()
		print("adx: ", self.adx[-4:])
		print("+di: ", self.plus_di[-4:])
		print("-di: ", self.minus_di[-4:])

		print()
		print("---------------------")



	def validate_rsi(self):

		#TODO: viet logic validate rsi
		if self.rsi[-1] < self.OVERSOLD_THRESHOLD:
			return True
		return False

	def validate_macd(self):

		#TODO: viet logic validate macd


		if self.macd[-2] < 0 and self.macd_signal[-2] < 0: #filter
			return False

		if self.macd[-1] < 0 and self.macd_signal[-1] < 0: #filter
			return False

		# check if macd crossover signal


		return True


if __name__ == "__main__":
	pass