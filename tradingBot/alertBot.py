import playsound
import os
import time

class AlertBot:

	def __init__(self):
		("...alert bot crreated")

	def alert(self):
		print()
		# print(os.getcwd())
		playsound.playsound(os.path.dirname(__file__)+"\\alert.m4a")
		time.sleep(0.5)
		playsound.playsound(os.path.dirname(__file__)+"\\alert.m4a")
		time.sleep(0.5)
		playsound.playsound(os.path.dirname(__file__)+"\\alert.m4a")



if __name__ == "__main__":

	# back testing
	
	a = AlertBot()

	a.alert()
