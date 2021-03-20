import playsound
import os
import time
import threading

class AlertBot:

    def __init__(self):
        pass
    def alert(self):
        try:
            #TEMPORARILY DISABLE THIS FUNCTION
            return
            # path = os.path.dirname(__file__) + "\\alert.m4a"
            # playsound.playsound(path)
        except Exception as e:
            print(e)
    
    def run(self):
        threading.Thread(target=self.alert, args=()).start()

if __name__ == "__main__":

    # back testing
    
    a = AlertBot()
    a.run()
