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
		self.rsi = talib.RSI(numpy.array(close_list))

	def refresh_macd(self, close_list):

		# CALCULATE by callback function _refresh_indicator
		self.macd, self.macd_signal, self.macd_hist = talib.MACD(
			numpy.array(close_list),
			fastperiod=12, 
			slowperiod=26, 
			signalperiod=9)

	def refresh_ema_200(self, close_list):

		# CALCULATE by callback function _refresh_indicator
		self.ema_200 = talib.EMA(numpy.array(close_list),200)

	def refresh_dmi(self, candles):

		# CALCULATE by callback function _refresh_indicator

		high = []
		low = []
		close = []

		for i in candles:
			high.append(i['high'])
			low.append(i['low'])
			close.append(i['close'])

		self.adx = talib.ADX(high, low, close, 14)
		self.plus_di = talib.PLUS_DI(high, low, close,14)
		self.minus_di = talib.MINUS_DI(high, low, close,14)

if __name__ == "__main__":
	pass