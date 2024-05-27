# -*- coding: utf-8 -*-
"""
Created on Sat Apr 11 01:28:51 2020

@author: quentinn.r.roby
"""

import pandas as pd
import oandapyV20
import oandapyV20.endpoints.instruments as instruments
import oandapyV20.endpoints.orders as orders
import oandapyV20.endpoints.pricing as pricing
from oandapyV20.contrib.requests import MarketOrderRequest, TakeProfitDetails, StopLossDetails, TrailingStopLossDetails
import oandapyV20.endpoints.trades as trades
import numpy as np
import os
import json


class Oanda_Connector():
    
      
    #########################################################################
     
    """
       Pulling Candlestick Data from Oanda
    """
    
    def pullCandleData(accessToken, path, fx_pairs, barCount, timeFrame):
        
        if type(timeFrame) != str:
            print("timeFrame needs to be a string (e.g: M15, H1, H4,....)")
            return None
        else:
            timeFrame = timeFrame
            
        if type(accessToken) != str:
            print("accessToken needs to be a string")
            return None
        else:
            accessToken = accessToken
            
    
        if len(fx_pairs) > 6:
            fx_pairs = fx_pairs.replace(' ','')
        else:
            fx_pairs = fx_pairs
        
        runCount = (len(fx_pairs)-1)  
       
        while runCount > 0:
            if len(fx_pairs) == 0:
                print('Downloaded all candlestick data. sleeping unitl I am called again. zzzzzz') 
                return None
            else:            
                string = fx_pairs[-6:]
                fx_pairs = fx_pairs[0:-6]  # Continues to the next currency pair if there is one
                pd.set_option('display.max_rows', 500)
                pd.set_option('display.max_columns', 500)
                pd.set_option('display.width', 1000)
                
                client = oandapyV20.API(access_token=accessToken, headers={"Accept-Datetime-Format":"Unix"})
                
                params = {
                        "count": barCount,
                        "granularity": timeFrame
                        }
                
                print ('Downloading ohlc data for '+string+'!')
                print('...')
                
                r = instruments.InstrumentsCandles(instrument=string[0:3]+'_'+string[3:6] , params=params)
                client.request(r)
                df = pd.DataFrame(r.response['candles'])
                length = (len(df))-1
                low = np.asarray([])
                high = np.asarray([])
                close = np.asarray([])
                openn = np.asarray([])
                while length > 0:
                    specific_candle=pd.DataFrame(r.response['candles'][length])
                    #Getting the low price for each candle
                    obtain_low=specific_candle.tail(2)
                    obtain_low=obtain_low.head(1)
                    obtain_low=obtain_low.mid.values
                    #Getting the close price for each candle
                    obtain_close=specific_candle.head(1)
                    obtain_close=obtain_close.mid.values
                    #Getting the high price for each candle
                    obtain_high=specific_candle.head(2)
                    obtain_high=obtain_high.tail(1)
                    obtain_high=(obtain_high.mid.values)
                    #Getting the open price for each candle
                    obtain_open=specific_candle.tail(1)
                    obtain_open=obtain_open.mid.values
                    
                    low=np.insert(low,0,float(obtain_low))
                    high=np.insert(high,0,float(obtain_high))
                    close=np.insert(close,0,float(obtain_close))
                    openn=np.insert(openn,0,float(obtain_open))
                    kopen= pd.DataFrame(columns=['open'], data=openn)
                    khigh= pd.DataFrame(columns=['high'], data=high)
                    klow=pd.DataFrame(columns=['low'], data=low)
                    kclose=pd.DataFrame(columns=['close'], data=close)
                    klines=pd.concat([kopen,khigh,klow,kclose,df], axis=1)
                    
                    length = length-1
                
                klines.mid=klines.mid.shift(-1)
                klines.complete=klines.complete.shift(-1)
                klines.time=klines.time.shift(-1)
                klines.volume=klines.volume.shift(-1)
                klines=klines.drop(columns=['mid'])
                klines.drop(klines.tail(1).index,inplace=True)
                #print (klines.head(5))
                #print(klines.tail(5))
                if os.name == 'nt':
                    klines.to_csv((path+string+'.csv')) #if using windows do not change  '\\Forex_OHLC\\'
                else:
                    klines.to_csv((r'/home/q/Dropbox/Dracula Blood Money Algo/H1OHLC/'+string+'.csv')) #if using linux/mac change directory
            
    ####################################################################  
    
    """
       Execution of Market Orders in Oanda
    """
    def marketOrder(accessToken, accountID, fx_pairs, position, units, takeProfit=0, stopLoss=0, trailStopLoss=0):
                    
        if type(accessToken) != str:
            print("accessToken needs to be a string")
            return None
            
        if type(accountID) != str:
            print("accountID needs to be a string")
            return None
            
        if type(position) != str:
            print("position needs to be a string (e.g. 'Buy' or 'Sell')")
            return None

            
        if position == "Buy" and units < 0:
            units = abs(units)
        elif position == "Sell" and units > 0:
            units = -units
        else:
            units = units
        
        api = oandapyV20.API(access_token=accessToken)

        params = {
                "instruments": fx_pairs[0:3]+'_'+fx_pairs[3:6]
                }          
        
        rq = pricing.PricingInfo(accountID, params=params)
        request = api.request(rq)
        prices = request.get('prices')
        
        if position == "Buy":
            price = [value['asks'] for value in prices]
            price = price[0]
            Ask = [val['price'] for val in price]
            Ask = float(Ask[0])
            
            if takeProfit > 0:
                if 'JPY' in fx_pairs:
                    Long_TP=Ask+(takeProfit / 100)
                    profitPrice = TakeProfitDetails(price=Long_TP).data
                else:
                    Long_TP=Ask+(takeProfit / 10000)
                    profitPrice = TakeProfitDetails(price=Long_TP).data
            else:
                profitPrice = None
            
            if stopLoss > 0:
                if 'JPY' in fx_pairs:
                    Long_SL=Ask-(stopLoss / 100)
                    lossPrice = StopLossDetails(price=Long_SL).data
                else:
                    Long_SL=Ask-(stopLoss / 10000)
                    lossPrice = StopLossDetails(price=Long_SL).data
            else:
                lossPrice = None
                
            if trailStopLoss > 0:
                if 'JPY' in fx_pairs:
                    Long_TSL=Ask-(trailStopLoss / 100)
                    trailLossPrice = TrailingStopLossDetails(distance=Long_TSL).data
                else:
                    Long_TSL=Ask-(trailStopLoss / 10000)
                    trailLossPrice = TrailingStopLossDetails(distance=Long_TSL).data
            else:
                trailLossPrice = None
            
            mktOrder = MarketOrderRequest(instrument=str(fx_pairs[0:3]+'_'+fx_pairs[3:6]), units=units, takeProfitOnFill=profitPrice, stopLossOnFill=lossPrice, trailingStopLossOnFill=trailLossPrice)
            r = orders.OrderCreate(accountID,data=mktOrder.data)
            try:
                rv = api.request(r)
                return rv
            except oandapyV20.exceptions.V20Error as err:
                print(r.status_code, err)
            else:
                print(json.dumps(rv, indent=2))
        
        if position == "Sell":
            price = [value['bids'] for value in prices]
            price = price[0]
            Bid = [val['price'] for val in price]
            Bid = float(Bid[0])
            
            if takeProfit > 0:
                if 'JPY' in fx_pairs:
                    Short_TP=Bid-(takeProfit / 100)
                    profitPrice = TakeProfitDetails(price=Short_TP).data
                else:
                    Short_TP=Bid-(takeProfit / 10000)
                    profitPrice = TakeProfitDetails(price=Short_TP).data
            else:
                profitPrice = None
            
            if stopLoss > 0:
                if 'JPY' in fx_pairs:
                    Short_SL=Bid+(stopLoss / 100)
                    lossPrice = StopLossDetails(price=Short_SL).data
                else:
                    Short_SL=Bid+(stopLoss / 10000)
                    lossPrice = StopLossDetails(price=Short_SL).data
            else:
                lossPrice = None
                
            if trailStopLoss > 0:
                if 'JPY' in fx_pairs:
                    Short_TSL=Bid+(trailStopLoss / 100)
                    trailLossPrice = TrailingStopLossDetails(distance=Short_TSL).data
                else:
                    Short_TSL=Bid+(trailStopLoss / 10000)
                    trailLossPrice = TrailingStopLossDetails(distance=Short_TSL).data
            else:
                trailLossPrice = None
            
            mktOrder = MarketOrderRequest(instrument=str(fx_pairs[0:3]+'_'+fx_pairs[3:6]), units=units, takeProfitOnFill=profitPrice, stopLossOnFill=lossPrice, trailingStopLossOnFill=trailLossPrice)
            r = orders.OrderCreate(accountID,data=mktOrder.data)
            try:
                rv = api.request(r)
                return rv
            except oandapyV20.exceptions.V20Error as err:
                print(r.status_code, err)
            else:
                print(json.dumps(rv, indent=2))
                
                
    """
       Getting Current Price
    """
    def getPricing(accessToken, accountID, fx_pairs, Bid_Ask):
        
        if type(accessToken) != str:
            print("accessToken needs to be a string")
            return None
            
        if type(accountID) != str:
            print("accountID needs to be a string")
            return None
            
        if type(Bid_Ask) != str:
            print("Bid or Ask needs to be a string (e.g. 'Bid' or 'Ask')")
            return None
        
        api = oandapyV20.API(access_token=accessToken)

        params = {
                "instruments": fx_pairs[0:3]+'_'+fx_pairs[3:6]
                }    
        
        rq = pricing.PricingInfo(accountID, params=params)
        request = api.request(rq)
        prices = request.get('prices')
        
        if Bid_Ask == 'Bid':
            price = [value['bids'] for value in prices]
            price = price[0]
            Bid = [val['price'] for val in price]
            Bid = float(Bid[0])
            return Bid
        
        if Bid_Ask == 'Ask':
            price = [value['asks'] for value in prices]
            price = price[0]
            Ask = [val['price'] for val in price]
            Ask = float(Ask[0])
            return Ask
            
    def getOpenTrades_Mod(accessToken, accountID):
        client = oandapyV20.API(access_token=accessToken)
        r = trades.TradesList(accountID = accountID)
        rv = client.request(r)
        Trades = rv.get('trades')
        Trades = [value['instrument'] for value in Trades]
        
        dummyList = []
        
        for string in Trades:
            stringNew = string.replace("_", " ")
            dummyList.append(stringNew)
        
        openTrades = []
        
        for i in dummyList:
            openTrades.append(i.split(' ', 1)[0])
            openTrades.append(i.split(' ', 1)[1])
         
        
        return openTrades
    
    def getOpenTrades(accessToken, accountID):
        client = oandapyV20.API(access_token=accessToken)
        r = trades.TradesList(accountID = accountID)
        rv = client.request(r)
        Trades = rv.get('trades')
        Trades = [value['instrument'] for value in Trades]

        return Trades
    
    def getSpreads(accessToken, accountID, fx_pairs):
        api = oandapyV20.API(access_token=accessToken)
        params = {
                "instruments": fx_pairs[0:3]+'_'+fx_pairs[3:6]
                }    
        
        rp = pricing.PricingInfo(accountID, params=params)
        request = api.request(rp)
        prices = request.get('prices')
        
        currentBid = [value['bids'] for value in prices]
        currentBid  = currentBid[0]
        Bid = [val['price'] for val in currentBid]
        Bid = float(Bid[0])
        
        currentAsk = [value['asks'] for value in prices]
        currentAsk = currentAsk[0]
        Ask = [val['price'] for val in currentAsk]
        Ask = float(Ask[0])
        
        Spread = Ask - Bid
        
        if 'JPY' in fx_pairs:
            multiplier = 10 ** 3
            Spread = int(Spread * multiplier) / multiplier
        else:
            multiplier = 10 ** 5
            Spread = int(Spread * multiplier) / multiplier
        
        return Spread
    
        
        
              
"""
from pathlib import Path
path = str(Path(__file__).parent.absolute())
path=path.replace("\\","\\\\")
path=path[:path.find("Forex_OHLC")]
from Trading.Python.Template import dataClass

fx_pairs='AUDJPY CADJPY CHFJPY EURJPY NZDJPY USDJPY GBPJPY AUDUSD EURUSD GBPUSD NZDUSD USDCAD USDCHF AUDCAD CADCHF EURCAD GBPCAD NZDCAD AUDCHF EURCHF GBPCHF NZDCHF EURAUD EURGBP EURNZD GBPNZD GBPAUD AUDNZD'
#fx_pairs = 'AUDJPY'
pull = dataClass.Oanda_Connector.pullCandleData(accessToken='6ea870404c4ea29154e479c00d1f3453-9da92f98c084c6d62f2bb60a8ed78931', path=path, fx_pairs=fx_pairs, barCount=200, timeFrame='M15')
pull

order = dataClass.Oanda_Connector.marketOrder('6ea870404c4ea29154e479c00d1f3453-9da92f98c084c6d62f2bb60a8ed78931', '101-001-6994724-001', fx_pairs, "Sell", 1000, 100, 60, 50)
order
"""
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
    
        