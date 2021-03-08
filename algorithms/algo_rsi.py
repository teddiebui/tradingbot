from datetime import datetime as dt
def run(candles, indicator):

	validated = indicator.validate_rsi(candles)

	if validated:
		print(dt.fromtimestamp(float(candles[-1]['time'])/1000), indicator.rsi[-1])
		return True
	
	return False

