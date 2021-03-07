from datetime import datetime as dt
def run(candles, indicator):
	#initiation
	closes = [i['close'] for i in candles]
	cross_over = False
	above_ema = False

	indicator.refresh_macd(closes)

	if len(indicator.macd) < 26:
		return False

	if indicator.macd[-2] >= 0 or indicator.macd_signal[-2] >= 0: #filter
		return False

	if indicator.macd[-1] >= 0 or indicator.macd_signal[-1] >= 0: #filter
		return False

	candle_time = dt.fromtimestamp(float(candles[-1]['time'])/1000)
	# print(candle_time," macd: ", indicator.macd[-1], "macd_signal: ", indicator.macd_signal[-1])



	# macd_go_up = (indicator.macd[-1] - indicator.macd[-2]) > 0
	# signal_go_down = (indicator.macd_signal[-1] - indicator.macd_signal[-2]) < 0
	cross_over = indicator.macd[-2] < indicator.macd_signal[-2] and indicator.macd[-1] > indicator.macd_signal[-1]

	# cross_over = macd
	if cross_over :
		# print(candle_time, " cross over happened")
		indicator.refresh_ema_200(closes)
		if closes[-1] > indicator.ema_200[-1]:
			above_ema = True
			print(dt.fromtimestamp(float(candles[-1]['time'])/1000), "... price above EMA200 + cross over happened")
			
			return True


	# if indicator.macd[-1] - indicator.macd[-2] > 0 and indicator.macd_signal[-1] - indicator.macd[-2] < 0:
	# 	print(dt.fromtimestamp(float(candles[-1]['time'])/1000), "... MACD cross over happened")
	# 	cross_over = True

	# 	indicator.refresh_ema_200(closes)
	# 	if closes[-1] > indicator.ema_200[-1]:
	# 		above_ema = True
	# 		print(dt.fromtimestamp(float(candles[-1]['time'])/1000), "... price above EMA200")
			
	# 		return True


	# 	return True