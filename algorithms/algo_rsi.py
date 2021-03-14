from datetime import datetime as dt
def run(candles, indicator):
	try:
		validated = indicator.validate_rsi(candles)

		if validated:
			print(dt.fromtimestamp(float(candles[-1]['time'])/1000), indicator.rsi[-1])
			return True
	except Exception as e:
		print("...algo_rsi: ", e)
	
	return False

