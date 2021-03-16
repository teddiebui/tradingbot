import collections
import pprint
import threading
import time
import datetime
import os
import re
import math

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException

from ..crawler import candleCrawler as cc
from ..indicator import indicator as ind
from ..orderMaker import orderMaker as om

from .alertBot import AlertBot

class TestBot(threading.Thread):

    def __init__(self, client, symbol, algorithm, order_maker, indicator):
        threading.Thread.__init__(self)
        self.is_running = False

        #initiating fields
        self.client = client
        self.symbol = symbol
        self.algorithm = algorithm
        self.order_maker = order_maker
        self.indicator = indicator
        
    def _back_test_algorithm(self, interval):

        import json
        from collections import deque

        candles = deque(maxlen = 400)
        files = self._get_json_data_from_storage()
        directory_path = os.path.dirname(os.path.dirname(__file__)) + "\\candle_data\\" + self.symbol.lower()
        # directory_path = []

        total = time.time()
        candle_time = 0
        algorithm_time = 0
        order_time = 0
        load_json = 0	

        #MAIN START HERE
        #TODO: load json data
        for file in files:
            file = directory_path + "\\" + file

            with open(file, "r") as f:
                global klines
                a = time.time()
                klines = json.load(f)
                # print(file)
                # print("load json file time: ", time.time() - a)

                a=time.time()
                
                klines = self.client.get_historical_klines(self.symbol.upper(), interval, "7 day ago UTC")
                print("load json data time: {:0.02f}".format(time.time()-a))
                load_json = time.time() - a
                #TODO: loop thru candle lines. For each candle, update indicator and run algorithm
                for each in klines[:]:
                    if self.is_running == False:
                        return
                    # print(datetime.datetime.fromtimestamp(float(each[0])/1000))

                    a=time.time()
                    candle = {'time' : float(each[0]),
                    'open' : float(each[1]), 
                    'high' : float(each[2]), 
                    'low' : float(each[3]), 
                    'close' :float(each[4])
                    }

                    candles.append(candle)
                    candle_time += (time.time() - a)

                    if not self.order_maker.is_in_position:
                        #TODO: run algorithm
                        c=time.time()
                        signal = self.algorithm.run(candles, self.indicator)
                        algorithm_time += (time.time() - c)
                        d = time.time()

                        if signal == True:
                            #create fake order if signal is true
                            self.order_maker.buy(candle['close'])
                            print(datetime.datetime.fromtimestamp(float(candle['time'])/1000), "...place fake order, buy price: ", candle['close'])
                    else:
                        self.order_maker.check_current_position(candle['close'])
                        if not self.order_maker.is_in_position:
                            print(datetime.datetime.fromtimestamp(float(candle['time'])/1000), "...{}, price: {},candle low: {}, candle high: {}\n".format(
                            self.order_maker.orders[-1]['recordData'][1]['type'],
                            self.order_maker.orders[-1]['recordData'][1]['price'],
                            candle['low'],
                            candle['high']))
                            # pprint.pprint(self.order_maker.orders[len(self.order_maker.orders)])

                            order_time += (time.time() - d)

                #on inner loop exit, do back test log
                self.order_maker.back_test_log(self.report(interval = interval), )
                

                #debug
                print("total: {:0.04f}--load_json: {:0.02f}--candle: {:0.04f}--algorithm: {:0.02f}--order: {:0.02f}".format(
                time.time() - total,
                load_json,
                candle_time,
                algorithm_time,
                order_time)
                )
            return

        return

    def _get_json_data_from_storage(self):
        #for back test at a long period

        directory_path = os.path.dirname(os.path.dirname(__file__)) + "\\candle_data\\" + self.symbol.lower()

        #SORT ALL THE FILES IN DIRECTORY ABOVE
        a = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        b = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

        def callback(filename):
            month = re.findall(r"[A-Z][a-z]{2}", filename)[0]
            year = int(re.findall(r"\d{4}", filename)[0])
            return (year,b[a.index(month)])
        files = os.listdir(directory_path)
        files.sort(key=callback)

        return files


    def log(self):

        self.order_maker.log()


    def run(self):
        self.is_running = True
        self._back_test_algorithm(self.client.KLINE_INTERVAL_15MINUTE)




    def stop(self):
        self.report()
        self.is_running = False


    def report(self, interval):
        
        # RETURN JSON TYPE METADATA ABOUT SESSION
        count = 0
        _count = 0
        loss = 0
        gain = 0
        win_streak = 0
        lose_streak = 0
        start_time = str(datetime.datetime.fromtimestamp(klines[0][0]/1000))
        end_time = str(datetime.datetime.fromtimestamp(klines[-1][0]/1000))
        temp = self.order_maker.orders[0]['recordData'][1]['type']
        
        for i in self.order_maker.orders:
            _count += 1
            if len(i['recordData']) == 2:
                
                if i['recordData'][1]['type'] != temp:
                    
                    
                    if i['recordData'][1]['type'] == 'STOP_LOSS_LIMIT':
                        if _count > lose_streak:
                            lose_streak = _count
                        loss += _count
                    else:
                        if _count > win_streak:
                            win_streak = _count
                        gain += _count
                    count += _count
                    temp = i['recordData'][1]['type']
                    _count = 0
        if count > 0:
            winRate = gain/count*100
            pnl = math.pow(1+self.order_maker.take_profit,gain)/math.pow(1+self.order_maker.stop_loss,loss)*100 - 100
        else:
            winRate = 0
            pnl = 0
        
        print("Symbol :\t\t {}\nOrders :\t\t {}\nGain:    \t\t {}\nLoss:    \t\t {}\nWin Rate:\t\t {}\nPNL:    \t\t {}\nWin streak:\t\t {}\nLose streak:\t\t {}\n\
Start time:\t\t {}\nEnd Time:\t\t {}\nInterval:\t\t {}\nOrder Maker:\t\t {}\nIndicator:\t\t {}\n".format(
        self.symbol, count, gain, loss, round(winRate,2), round(pnl,2), win_streak,
        lose_streak, start_time, end_time, interval, self.order_maker.get_config(), self.indicator.get_config()
        ))
        metadata = {
            'pnlPercentage' : pnl,
            'symbol' : self.symbol,
            'orders' : count,
            'gain' : gain,
            'loss' : loss,
            'winRate' : winRate,
            'orderMaker' : self.order_maker.get_config(),
            'indicator' : self.indicator.get_config(),
            'winStreak' : win_streak,
            'loseStreak' : lose_streak,
            'startTime': start_time,
            'end_time' : end_time,
            'candleInterval' : interval
            }
        
        return metadata


if __name__ == "__main__":
    t = TestBot(None)
    
