from datetime import datetime as dt
def run(candles, indicator):

	indicator.refresh_rsi([i['close'] for i in candles])

	# print(indicator.rsi)

	if indicator.rsi[-1] < indicator.OVERSOLD_THRESHOLD:
		print(dt.fromtimestamp(float(candles[-1]['time'])/1000), indicator.rsi[-1])
		return True

