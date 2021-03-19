import pprint
import math
import datetime
import time
import json
import os

from binance.enums import *
from binance.exceptions import BinanceAPIException, BinanceOrderException

from ..priceMaker import priceMaker as pm


class OrderMaker(pm.PriceMaker):

    def __init__(self, client, symbol, stake, take_profit, stop_loss, fee, discount, trailing_stop_mode = False):

        pm.PriceMaker.__init__(self, stake, take_profit, stop_loss, fee, discount)
        self.client = client
        self.symbol = symbol

        self.current_position = None
        

        self.open_orders = []
        self.orders = []
        
        #flags
        self.is_in_position = False
        self.trailing_stop_mode = trailing_stop_mode

    def buy_with_stop_limit(self, current_price = 0):
        
        if self.is_in_position == False:
            
            order_market_buy = self.client.order_market_buy(
                        symbol= self.symbol.upper(),
                        quoteOrderQty= self.stake)
                        
            buy_price, qty, vol = self._extract_filled_order(order_market_buy)
            stop_loss_price = self.get_stop_loss_price(buy_price)
            
            order_limit_sell = self.client.create_order(
                symbol= self.symbol,
                side=SIDE_SELL,
                type='STOP_LOSS_LIMIT',
                timeInForce=TIME_IN_FORCE_GTC,
                price = stop_loss_price, 
                stopPrice = stop_loss_price,
                quantity=qty,
                newOrderRespType = 'FULL')
                
            print("#######################################")
            pprint.pprint(order_limit_sell)
            
            record = {
            
                'recordId' : order_market_buy['orderId'],
                'recordData': [order_market_buy, order_limit_sell]
            }
            
            self.orders.append(record)
            self.open_orders.append(self.orders[-1]['recordData'])
            self.is_in_position = True
            
            self._log_temp()
                    
    def buy_with_oco(self, current_price = 0.00):
        
        if self.is_in_position == False:
            self.is_in_position = True


            order_market_buy = self.client.order_market_buy(
                        symbol= self.symbol.upper(),
                        quoteOrderQty= self.stake)
                        
            buy_price, quantity, volume = self._extract_filled_order(order_market_buy)

            # self.orders[str(len(self.orders) + 1)] = [order_market_buy]

            

            # EXAMPLE OF ORDER_MARKET_BUY

            # {'clientOrderId': 'ZeKx4wrRZdYL3idkcPbaON',
            # 'cummulativeQuoteQty': '10.84427520',
            # 'executedQty': '0.04800000',
            # 'fills': [{'commission': '0.00003600',
            #            'commissionAsset': 'BNB',
            #            'price': '225.92240000',
            #            'qty': '0.04800000',
            #            'tradeId': 165914884}],
            # 'orderId': 1639119357,
            # 'orderListId': -1,
            # 'origQty': '0.04800000',
            # 'price': '0.00000000',
            # 'side': 'BUY',
            # 'status': 'FILLED',
            # 'symbol': 'BNBUSDT',
            # 'timeInForce': 'GTC',
            # 'transactTime': 1614958605886,
            # 'type': 'MARKET'}

            
            take_profit_price = self.get_take_profit_price(buy_price)
            stop_loss_price = self.get_stop_loss_price(buy_price)
            

            order_oco_sell =  self.client.create_oco_order(
                    symbol=self.symbol,
                    side=SIDE_SELL,
                    stopLimitTimeInForce=TIME_IN_FORCE_GTC,
                    quantity=quantity,
                    stopLimitPrice = stop_loss_price,
                    stopPrice= stop_loss_price,
                    
                    price=take_profit_price)
                    
                

            
            record = {
                'recordId' : order_market_buy['orderId'],
                'recordData': [order_market_buy, order_oco_sell['orderReports']]
            }
            self.orders.append(record)
            self.open_orders.append(self.orders[-1]['recordData'])
            
            self._log_temp()
            
            

            # EXAMPLE OF ORDER OCO SELL JSON

            # {'contingencyType': 'OCO',
            # 'listClientOrderId': 'xM4mCPJDxhoLLGBkVKsYt2',
            # 'listOrderStatus': 'EXECUTING',
            # 'listStatusType': 'EXEC_STARTED',
            # 'orderListId': 18376122,
            # 'orderReports': [{'clientOrderId': 'HvmvPgfPLccLBH4ppwM4CW',
            #                   'cummulativeQuoteQty': '0.00000000',
            #                   'executedQty': '0.00000000',
            #                   'orderId': 1639119368,
            #                   'orderListId': 18376122,
            #                   'origQty': '0.04800000',
            #                   'price': '224.02310000',
            #                   'side': 'SELL',
            #                   'status': 'NEW',
            #                   'stopPrice': '224.02310000',
            #                   'symbol': 'BNBUSDT',
            #                   'timeInForce': 'GTC',
            #                   'transactTime': 1614958606001,
            #                   'type': 'STOP_LOSS_LIMIT'},
            #                  {'clientOrderId': 'zfqMnRIjspbaNIoX4NcrM3',
            #                   'cummulativeQuoteQty': '0.00000000',
            #                   'executedQty': '0.00000000',
            #                   'orderId': 1639119369,
            #                   'orderListId': 18376122,
            #                   'origQty': '0.04800000',
            #                   'price': '228.52250000',
            #                   'side': 'SELL',
            #                   'status': 'NEW',
            #                   'symbol': 'BNBUSDT',
            #                   'timeInForce': 'GTC',
            #                   'transactTime': 1614958606001,
            #                   'type': 'LIMIT_MAKER'}],
            # 'orders': [{'clientOrderId': 'HvmvPgfPLccLBH4ppwM4CW',
            #             'orderId': 1639119368,
            #             'symbol': 'BNBUSDT'},
            #            {'clientOrderId': 'zfqMnRIjspbaNIoX4NcrM3',
            #             'orderId': 1639119369,
            #             'symbol': 'BNBUSDT'}],
            # 'symbol': 'BNBUSDT',
            # 'transactionTime': 1614958606001}
            
    def check_current_position2(self, current_price):
        
        if self.is_in_position:
            
            for orders in self.open_orders[:]:
                order = orders[1]
                if type(order) == list and len(order) > 1:
                    #THIS IS OCO ORDER
                    order = order[0]
                
                #check for stop loss
                if current_price <= float(order['price']) and order[status] != 'FILLED':
                    stop_loss_order = self.client.get_order(symbol = self.symbol, orderId=order['orderId'])
                    if stop_loss_order['status'] == 'FILLED':
                        #update records
                        orders.pop()
                        orders.append(stop_loss_order)
                        #update stake
                        price, qty, vol = self._extract_filled_order(take_profit_order)
                        self.stake = vol
                        #update flag
                        self.is_in_position = False
                        
                        self.open_orders.remove(orders)
                        return

    def check_current_position(self, current_price):

        if self.is_in_position:
            
            for orders in self.open_orders:
                stop_loss_order, take_profit_order = orders # returns 2 orders 
                
                #check for take profit
                if current_price >= float(take_profit_order['price']):
                    order = self.client.get_order(symbol = self.symbol, orderId=take_profit_order['orderId'])
                    if order['status'] == 'FILLED':
                        price, qty, vol = self._extract_filled_order(take_profit_order)
                        self.stake = vol
                        order['status'] = 'FILLED'
                        self.is_in_position = False
                        del self.open_orders[0]
                        return
            
                #check for stop loss
                if current_price <= float(stop_loss_order['price']):
                    stop_loss_order = self.client.get_order(symbol = self.symbol, orderId=stop_loss_order['orderId'])
                    if stop_loss_order['status'] == 'FILLED':
                        price, qty, vol = self._extract_filled_order(take_profit_order)
                        self.stake = vol
                        self.orders[-1]['recordData'].append(stop_loss_order)
                        self.is_in_position = False
                        self.was_stop_loss = True
                        del self.open_orders[0]
                        return
                        
    def trailing_stop(self, current_price):
        
        if self.is_in_position:
            for orders in self.open_orders[:]:

                order = orders[1]
                
                if type(order) == list and len(order) > 1:
                    #THIS IS OCO ORDER
                    order = order[0]

                if orders[0]['symbol'].upper() == self.symbol.upper() and orders[1]['status'] != 'FILLED':
                    
                    #cancel previous stop loss
                    orderId = order['orderId']
                    cancel_order = self.client.cancel_order(symbol = self.symbol, orderId = orderId)
                    
                    while len(orders) > 1:
                        orders.pop()
                        
                    #add new stop loss
                    price, qty, vol = self._extract_filled_order(orders[0])
                    new_order_limit_sell = self.client.create_order(
                        symbol= self.symbol,
                        side=SIDE_SELL,
                        type='STOP_LOSS_LIMIT',
                        timeInForce=TIME_IN_FORCE_GTC,
                        price = round(float(order['price']) + (current_price - price),4), 
                        stopPrice = round((float(order['price']) + (current_price - price))*1.005,4),
                        quantity=qty,
                        newOrderRespType = 'FULL')

                    orders.append(new_order_limit_sell)

    def _extract_filled_order(self, order):

        totalQty = 0
        totalVolume = 0
        avgPrice = 0

        for i in order['fills']:
            
            totalQty += float(i['qty'])
            totalVolume += float(i['price'])*float(i['qty'])

        avgPrice = math.ceil(totalVolume/totalQty*10000)/10000
        return avgPrice, totalQty, totalVolume


    def _log_temp(self):


        directory_path = os.path.dirname(os.path.dirname(__file__))

        os.makedirs(directory_path+"\\loggings", exist_ok = True)

        with open(
                os.path.join(directory_path,"loggings\\temp_order_log_.json"),'w', encoding='utf-8') as file:
            json.dump(self.orders,file)

    def log(self, metadata):

        directory_path = os.path.dirname(os.path.dirname(__file__))

        os.makedirs(directory_path+"\\loggings", exist_ok = True)

        date_time = datetime.datetime.fromtimestamp(round(time.time()))

        path = "loggings\\{symbol}_{year}_{month}_{date}_{hour}_{minute}_{second}_order_log.json".format(
                    symbol=self.symbol, 
                    year = date_time.year,
                    month = date_time.month,
                    date = date_time.day,
                    hour = date_time.hour,
                    minute = date_time.minute,
                    second = date_time.second
                )

        with open(os.path.join(directory_path, path), 'w', encoding='utf-8') as file:
            json.dump([metadata, self.orders],file)

        print("order maker logged")


    def stop(self):
        #TODO: cancel any
        print("order maker stop")

    def get_config(self):

        return {
            'discount': self.discount,
            'fee': self.fee,
            'stake': self.stake,
            'stopLoss': self.stop_loss,
            'takeProfit': self.take_profit
        }


if __name__ == "__main__":

    pass
    
