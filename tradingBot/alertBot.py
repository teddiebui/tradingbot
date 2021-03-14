import playsound
import os
import time
import threading

class AlertBot:

	def __init__(self):
		pass
	def alert(self):
		try:
			path = os.path.dirname(__file__) + "\\alert.m4a"
			for i in range(3):
				playsound.playsound(path)
				time.time()
		except Exception as e:
			print(e)
	
	def run(self):
		threading.Thread(target=self.alert, args=()).start()

if __name__ == "__main__":

	# back testing
	
	a = AlertBot()
	a.run()
