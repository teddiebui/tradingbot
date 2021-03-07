import talib
import numpy
import pprint

class Indicator():

	def __init__(self):
		#rsi indicator variables
		self.OVERSOLD_THRESHOLD = 16
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

	def update(self, candles):

		closes = [i['close'] for i in candles]

		self.refresh_rsi(closes)
		self.refresh_macd(closes)
		self.refresh_ema_200(closes)
		self.refresh_dmi(candles)

		# print()
		# print("rsi: ", self.rsi[-4:])
		# print()
		# print("macd: ", self.macd[-4:])	
		# print("macd signal: ", self.macd_signal[-4:])	
		# print("macd histogram: ", self.macd_hist[-4:])	
		# print()
		# print("ema 200: ", self.ema_200[-4:]) 
		# print()
		# print("adx: ", self.adx[-4:])
		# print("+di: ", self.plus_di[-4:])
		# print("-di: ", self.minus_di[-4:])
		# print()
		# print("---------------------")


	def refresh_rsi(self, close_list):

		# CALCULATE by callback function _refresh_indicator
		self.rsi = list(talib.RSI(numpy.array(close_list)))
		# just for prettifying
		self.rsi = list(map(lambda x: round(x,2), self.rsi))	
		

	def refresh_macd(self, close_list):

		# CALCULATE by callback function _refresh_indicator
		self.macd, self.macd_signal, self.macd_hist = talib.MACD(
			numpy.array(close_list),
			fastperiod=12, 
			slowperiod=26, 
			signalperiod=9)

		# just for prettifying
		self.macd = list(map(lambda x: round(x,4), self.macd))
		self.macd_signal = list(map(lambda x: round(x,4), self.macd_signal))
		self.macd_hist = list(map(lambda x: round(x,4), self.macd_hist))

	def refresh_ema_200(self, close_list):

		# CALCULATE by callback function _refresh_indicator
		self.ema_200 = talib.EMA(numpy.array(close_list),200)
		# just for prettifying
		self.ema_200 = list(map(lambda x: round(x,2), self.ema_200))

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


if __name__ == "__main__":
	pass