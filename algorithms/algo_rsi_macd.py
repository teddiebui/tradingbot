from datetime import datetime as dt
def run(candles, indicator):

	closes = [i['close'] for i in candles]

	indicator.refresh_rsi(closes)

	indicator.refresh_macd(closes)

	if indicator.rsi[-1] < indicator.OVERSOLD_THRESHOLD:
		print(dt.fromtimestamp(float(candles[-1]['time'])/1000), indicator.rsi[-1])
		return True