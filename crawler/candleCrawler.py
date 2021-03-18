import threading
import websocket
import time
import pprint
import json
import datetime
from collections import deque


from binance.client import Client


class CandleCrawler:

    def __init__(self, client, symbol):

        self.client = client
        self.symbol = symbol
        

        self.WEBSOCKETS = [
            "wss://stream.binance.com:9443/ws/{}@kline_1m".format(symbol.lower()),
            "wss://stream.binance.com:9443/ws/{}@kline_15m".format(symbol.lower())
            ]
        
        self.FWEBSOCKETS = [
            "wss://fstream.binance.com/ws/!markPrice@arr@1s".format(symbol.lower())
        ]
        self.THREADS = []

        a = time.time()
        self.candles_1m = self.candle_initiation(Client.KLINE_INTERVAL_1MINUTE, "1 day ago UTC")
        self.candles_15m = self.candle_initiation(Client.KLINE_INTERVAL_15MINUTE, "1 day ago UTC")
        self.candles_30m = []
        self.candles_1h = self.candle_initiation(Client.KLINE_INTERVAL_1HOUR, "1 day ago UTC")
        self.candles_2h = []
        self.candles_4h = self.candle_initiation(Client.KLINE_INTERVAL_1HOUR, "4 day ago UTC")
        self.candles_1d = []
        self.candles_3d = []
        self.candles_1w = []

        self.ws = []
        self.is_running = False
        
        self.backtesting()


    def candle_initiation(self,interval, time):

        # return  a list
        klines = self.client.get_historical_klines(self.symbol.upper(), interval, time)

        return [{'time': float(i[0])/1000,
                'open' : float(i[1]), 
                'high' : float(i[2]), 
                'low' : float(i[3]), 
                'close' :float(i[4])
                } for i in klines]
        
    def backtesting(self):
        import datetime
        from time import time
        
        candle_5m = []
        candle_15m = []
        candle_30m = []
        candle_1h = []
        candle_2h = []
        candle_4h = []
        
        klines = self.client.get_historical_klines(self.symbol.upper(), Client.KLINE_INTERVAL_1MINUTE , "1 day ago UTC")
        
        a = time()
        for i in klines:
            
            t = datetime.datetime.fromtimestamp(i[0]/1000)
            
            #1m
      
            #15m
            if t.minute % 15 == 0:
                candle_15m.append(i)
            
            if len(candle_15m) > 0: 
                if i[2] > candle_15m[-1][2]:
                    candle_15m[-1][2] = i[2]
                if i[3] < candle_15m[-1][3]:
                    candle_15m[-1][3] = i[3]
                    
                candle_15m[-1][4] = i[4]
                    
            #1h
            if t.minute == 0:
                candle_1h.append(i)
            if len(candle_1h) > 0:
                if i[2] > candle_1h[-1][2]:
                    candle_1h[-1][2] = i[2]
                if i[3] < candle_1h[-1][3]:
                    candle_1h[-1][3] = i[3]
                
                candle_1h[-1][4] = i[4]
        b = time()
        
        pprint.pprint(candle_15m[-12:])
        pprint.pprint(candle_1h[-4:])
        print("loop time: ", b - a)
        print("len ", len(candle_15m))
        print("len ", len(candle_1h))


    def start_crawling(self, callback1 = None, callback2 = None):

        self.is_running = True

        thread = threading.Thread(target=self._start_crawling_handler, args=(self.WEBSOCKETS[-1], self._wss_on_message, callback1, callback2))
        thread.start()
        self.THREADS.append(thread)
        
    def start_futures_all_tickers(self):
        
        self.is_running = True
        
        thread = threading.Thread(target=self._start_crawling_handler, args=(self.FWEBSOCKETS[0], self._futures_on_message))
        thread.start()
        self.THREADS.append(thread)


    def _start_crawling_handler(self, socket, callback, callback1 = None, callback2 = None):

        ws = websocket.WebSocketApp(socket,
                                            on_open = lambda ws: self._wss_on_open(ws),
                                            on_error = lambda ws, error: self._wss_on_error(ws, error),
                                            on_close = lambda ws: self._wss_on_close(ws),
                                            on_message = lambda ws,msg: callback(ws, msg, callback1, callback2))
        self.ws.append(ws)
        ws.run_forever()
        


    def _wss_on_open(self, ws):
        print("open")
        pass

    def _wss_on_close(self, ws):
        print("stopped")
        pass

    def _wss_on_error(self, ws, error):
        print("error: ", error)

    def _wss_on_message(self, ws, msg, callback1 = None, callback2 = None):

        msg = json.loads(msg)
        pprint.pprint('hi...' + self.symbol.upper())
        # pprint.pprint(msg)
        # pprint.pprint(self.candles_15m)
        candle =    {'time': float(msg['k']['t'])/1000,
                        'open' : float(msg['k']['o']), 
                        'high' : float(msg['k']['h']), 
                        'low' : float(msg['k']['l']), 
                        'close' :float(msg['k']['c'])}
        
        self.candles_15m[-1] = candle
        print(candle)
        if msg['k']['x'] == True:
            del self.candles[0]
            self.candles_15m.append(candle)


        if callback1 != None:
            callback1()

        if callback2 != None:
            callback2(float(msg['k']['c']))

    def _futures_on_message(self, ws, msg, callback1 = None, callback2 = None):
        print("hi...")
        msg = json.loads(msg)
        pprint.pprint(msg)
        

        # pprint.pprint([[datetime.datetime.fromtimestamp(i['time']), i['close']] for i in self.candles_15m[-7:]])

    def stop(self):
        pprint.pprint(self.ws)
        for i in self.ws:
            i.keep_running = False
            self.is_running = False
        print("candle crawler stopped")

if __name__ == "__main__":
    from binance.client import Client
    apiKey = "TFWFmx5lPFNkkQnEIQsl2596kr1errGmaabzC3bFWI17mifeIYmnBybtU4Opkkyp"
    apiSecret = "kBzXtdMQsOVCrfV9qwyCabshmyALX3ABNjzGJF2a7ZoHF7oh6lzh4gEuvHOwQBSR"
    client = Client(apiKey, apiSecret)
    
    socket = "wss://fstream.binance.com/ws/bnbusdt@kline_15m"
    
    c = CandleCrawler(client, "bnbusdt")
    # c.start_futures_all_tickers()
    
    import time
    try:
        while True:
            time.sleep(3)
    except:
        c.stop()
    