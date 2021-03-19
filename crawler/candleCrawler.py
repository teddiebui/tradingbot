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
            "wss://stream.binance.com:9443/ws/{}@kline_15m".format(symbol.lower()),
            "wss://stream.binance.com:9443/ws/!miniTicker@arr"
            ]
        
        self.FWEBSOCKETS = [
            "wss://fstream.binance.com/ws/!markPrice@arr@1s".format(symbol.lower())
        ]
        self.THREADS = []

        
        self.candles_15m, self.candles_1h, self.candles_4h = self.build_candle(symbol)

        self.ws = []
        self.is_running = False
        
        self.data=[]
       
        


    def candle_initiation(self,interval, time):

        # return  a list
        klines = self.client.get_historical_klines(self.symbol.upper(), interval, time)

        return [{'time': float(i[0])/1000,
                'open' : float(i[1]), 
                'high' : float(i[2]), 
                'low' : float(i[3]), 
                'close' :float(i[4])
                } for i in klines]
        
    def build_candle(self, symbol):

        candle_15m = []
        candle_1h = []
        candle_4h = []
        
        klines = self.client.get_historical_klines(symbol.upper(), Client.KLINE_INTERVAL_15MINUTE , "3 day ago UTC")

        for i in klines[:]:
            
            t = datetime.datetime.fromtimestamp(i[0]/1000)
            
            candle = {'time': float(i[0])/1000,
                'open' : float(i[1]), 
                'high' : float(i[2]), 
                'low' : float(i[3]), 
                'close' :float(i[4])
                }
                
            candle_15m.append(candle)
        
            #1h
            if t.minute == 0:
                candle_1h.append(dict.copy(candle))
            if len(candle_1h) > 0:
                if candle['high'] > candle_1h[-1]['high']:
                    candle_1h[-1]['high'] = float(candle['high'])
                if candle['low'] < candle_1h[-1]['low']:
                    candle_1h[-1]['low'] = candle['low']
                
                candle_1h[-1]['close'] = candle['close']
                
            #4h
            if t.minute == 0 and t.hour % 4 == 0:
                candle_4h.append(dict.copy(candle))
            if len(candle_4h) > 0:
                if candle['high'] > candle_4h[-1]['high']:
                    candle_4h[-1]['high'] = candle['high']
                if candle['low'] < candle_4h[-1]['low']:
                    candle_4h[-1]['low'] = candle['low']
                
                candle_4h[-1]['close'] = candle['close']

        return candle_15m, candle_1h, candle_4h
        

    def start_crawling(self, callback1 = None, callback2 = None):

        self.is_running = True
        
        def _private_on_message(ws, msg, callback1 = None, callback2 = None):

            msg = json.loads(msg)

            candle =    {'time': float(msg['k']['t'])/1000,
                            'open' : float(msg['k']['o']), 
                            'high' : float(msg['k']['h']), 
                            'low' : float(msg['k']['l']), 
                            'close' :float(msg['k']['c'])}
            
            self.candles_15m[-1] = candle
            print(candle)
            if msg['k']['x'] == True:
                
                
                if candle['close'] > self.candle_15m[-1]['close']:
                    
                    if callback2 != None:
                        if callback2.trailing_stop_mode == True:
                            callback2.trailing_stop_mode(candle['close'])
                        else:
                            callback2.check_current_position(candle['close'])
                    
                del self.candles_15m[0]
                self.candles_15m.append(candle)


            if callback1 != None:
                callback1()

            if callback2 != None:
                callback2(float(msg['k']['c']))
            

        thread = threading.Thread(target=self._start_crawling_handler, args=(self.WEBSOCKETS[1], _private_on_message, callback1, callback2))
        thread.start()
        self.THREADS.append(thread)
        
    def start_all_ticker(self, algorithm):
        
        from time import time
        import talib
        import numpy
        
        tickers = self.client.get_ticker()
        
        c = time()
        symbols = [i['symbol'] for i in tickers if i['symbol'].endswith("USDT")]
        d = time()
        
        total = time()
        #LUU Y: vong lap sau day trich xuat chi ten symbol thoi
        for symbol in symbols:
            a = time()
            candles_15m, candles_1h, candles_4h = self.build_candle(symbol.upper()) 
            
            try:
                rsi_15m = talib.RSI(numpy.array([i['close'] for i in candles_1h]))
                rsi_1h = talib.RSI(numpy.array([i['close'] for i in candles_1h]))
                temp = {'symbol': symbol.upper(), 'candles' : [candles_15m, candles_1h, candles_4h], 'rsi' : [rsi_15m,rsi_1h]}
                self.data.append(temp)
            except Exception as e:
                print(repr(e))
                print(symbol, [i['close'] for i in candles_15m][-10:])
            
            b = time()
            print("symbol candle buil time: ", b-a)
        total = time() - total
        print("total symbols: ", len(symbols))
        print("total time: ", total)
        
        return
        
        
        
        def _private_on_message(ws, msg, callback1 = None,  callback2 = None):
            msg = json.loads(msg)
            # pprint.pprint(msg[-1])
            t = datetime.datetime.fromtimestamp(msg[-1]['E']/1000)
            # print(datetime.datetime.fromtimestamp(msg[-1]['E']/1000), datetime.datetime.fromtimestamp(msg[-5]['E']/1000))
            for i in msg:
                if i['s'] == "BNBUSDT":
                    print(i['c'], datetime.datetime.fromtimestamp(round(i['E']/1000)))
            # for i in self.data:
                
                # if callback1 != None:
                    # algorithm.run(i['candles'][0])
        
        self.is_running = True
        
        thread = threading.Thread(target=self._start_crawling_handler, args=(self.WEBSOCKETS[2], _private_on_message, algorithm))
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
    
    crawler = CandleCrawler(client, "bnbusdt")
    crawler.start_all_ticker(None)
    try:
        while True:
            time.sleep(3)
    except:
        crawler.stop()
    
    
    
    #####################################
    # from time import time
    # a = time()
    # tickers = client.get_ticker()
    # b = time()
    # c = time()
    # symbols = [i['symbol'] for i in tickers if i['symbol'].endswith("USDT")]
    # d = time()
    
    # total = time()
    # for symbol in symbols:
        # crawler.backtesting(symbol)
    # total = time() - total
    # print("total time: ", total)
    
    
    
    
    # print("symbols total: ", len(symbols))
    # print("crawl ticker time: ", b-a)
    # print("filter timeL ", d-c)
    
    # pprint.pprint(symbols)s
    ##########################################
    
    # c = CandleCrawler(client, "bnbusdt")
    
    
    # c.start_futures_all_tickers()
    
    # import time
    # try:
        # while True:
            # time.sleep(3)
    # except:
        # c.stop()
    