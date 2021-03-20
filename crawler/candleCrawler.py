import threading
import websocket
import time
import pprint
import json
import datetime
from collections import deque
import traceback
from math import floor


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
        
        self.data={}
       
        


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

        def _private_on_message(ws, msg, callback1 = None, callback2 = None):

            msg = json.loads(msg)

            candle =    {'time': float(msg['k']['t'])/1000,
                            'open' : float(msg['k']['o']), 
                            'high' : float(msg['k']['h']), 
                            'low' : float(msg['k']['l']), 
                            'close' :float(msg['k']['c'])}
            
            self.candles_15m[-1] = candle
            # print(candle['close'])
            
            try:
                if msg['k']['x'] == True:
                    del self.candles_15m[0]
                    self.candles_15m.append(candle)
                    
            except Exception as e:
                print("error from 'start_crawling' in 'candleCrawler'...see below: ") 
                print(repr(e))
                      
            try:
                
                callback1()
            except Exception as e:
                print("error from 'callback1' in 'candleCrawler'...see below: ") 
                traceback.print_tb(e.__traceback__)
            try:
                callback2()
            except Exception as e:
                print("error from 'callback2' in 'candleCrawler'...see below: ") 
                print(repr(e))
                        
            
            
            return
        
        self.is_running = True
                
        thread = threading.Thread(target=self._start_crawling_handler, args=(self.WEBSOCKETS[1], _private_on_message, callback1, callback2))
        thread.start()
        self.THREADS.append(thread)
        
    def start_all_symbol(self, callback1 = None, callback2 = None):
        
        
        
        def _private_on_message(ws, msg, callback1 = None,  callback2 = None):
             
            # TODO LATER: build up candle 15m
            ###
            # for i in msg:
                # pprint.pprint(i)
            # return
            msg = json.loads(msg)
            # FILTER PAIR USDT AND STILL ACTIVE ON BINANCE
            msg = [i for i in msg if i['s'].endswith("USDT") and "UPUSDT" not in i['s'] and "DOWNUSDT" not in i['s']]
                
            t = datetime.datetime.fromtimestamp(msg[-1]['E']/1000)

            # print("....received msg, ", t)
            if floor(t.second) % 2 == 0:
                # print(t)

                for i in msg:
                    try:
                        symbol = i['s'].upper()
                        close = round(float(i['c']),4) #TEMPORARILY USE CLOSE PRICE ONLY
                        candles_15m = self.data[symbol]['candles'][0]
                        
                        candles_15m[-1]['close'] = close #change close price of the last candles until every 15min
                        candles_15m[-1]['time'] = msg[-1]['E']/1000 
                        
                        if t.minute % 15 == 0 and floor(t.second) == 0:
                            del candles_15m[0]
                            candles_15m.append({'close' : close, 'time' : msg[-1]['E']/1000})
                            print("....inside 15 min, print t: ", t)
                            
                        callback1(symbol, candles_15m)
                    except KeyError as e:
                        pass
                        
                if t.minute % 15 == 0 and floor(t.second) == 0:
                    print("...15min passed away.. ", str(t))
                        
            if floor(t.second) == 0:
                print("...hi, 1 minute passed away - ", t)
                
        # self._get_all_symbol_spot() # populate self.data with all symbols appearing in spot market
        self._get_all_symbol_futures() # populate self.data with all symbols in futures BUT use candle from spot
            
        self.is_running = True
        
        thread = threading.Thread(target=self._start_crawling_handler, args=(self.WEBSOCKETS[2], _private_on_message, callback1))
        thread.start()
        self.THREADS.append(thread)
        
    def _get_all_symbol_futures(self):
    
        from time import time
    
        print(" get all symbol futures ")
        
        tickers = self.client.futures_ticker()
        
        symbols = [i['symbol'] for i in tickers if i['symbol'].endswith("USDT") and i['count'] != 1]

        total = time()
        for symbol in symbols:
            try:
                a = time()
            
                candles_15m, candles_1h, candles_4h = self.build_candle(symbol.upper())
                self.data[symbol.upper()] = {'candles' : [candles_15m, candles_1h, candles_4h]}
                
                b = time()
                print("symbol candle build time: ", b-a)
            except Exception as e:
                import traceback
                traceback.print_tb(e.__traceback__)
                print("\t", symbol, " not support in this app")
            
        
        total = time() - total
        print("total symbols: ", len(symbols))
        print("total time: ", total)
            
        print("len symbols: ", len(symbols))
            
        
    def _get_all_symbol_spot(self):

        from time import time
        
        tickers = self.client.get_ticker()
        
        c = time()
        symbols = [i['symbol'] for i in tickers if i['symbol'].endswith("USDT") and i['count'] != 1 and "UPUSDT" not in i['symbol'] and "DOWNUSDT" not in i['symbol']]
        d = time()
        
        total = time()
        # LUU Y: chi lay ten symbol trong bien tickers
        for symbol in symbols:
            
            a = time()
            candles_15m, candles_1h, candles_4h = self.build_candle(symbol.upper())
            
            try:
                self.data[symbol.upper()] = {'candles' : [candles_15m, candles_1h, candles_4h]}

            except Exception as e:
                print("...error occured in \"start_all_symbol\" inside \"CandleCrawler\"... see below:")
                print(repr(e))
                
            
            b = time()
            print("symbol candle build time: ", b-a)
        total = time() - total
        print("total symbols: ", len(symbols))
        print("total time: ", total)
        
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
    crawler._get_all_symbol_futures()
    
    # crawler.start_all_symbol(None)
    # try:
        # while True:
            # time.sleep(3)
    # except:
        # crawler.stop()
    
    
    
    #####################################
    # from time import time
    # from time import sleep
    
    # a = time()
    # tickers = client.get_ticker()
    # b = time()
    # c = time()
    # tickers = [i for i in tickers if i['symbol'].endswith("USDT") if i['count'] != 1]
    # d = time()
    
    # total = time()
    # for symbol in tickers:
        # if symbol['count'] == 1:
            # pprint.pprint(symbol)
        # sleep(0.1)
    # total = time() - total
    # print("total time: ", total)
    
    
    
    
    # print("symbols total: ", len(tickers))
    # print("crawl ticker time: ", b-a)
    # print("filter timeL ", d-c)
    
    # pprint.pprint(symbols)
    ##########################################
    