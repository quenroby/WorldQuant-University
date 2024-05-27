###############################################
# Import Necessary Libraries 
import oandapyV20
from oandapyV20 import API
from Oanda_Connector.oandaClass import Oanda_Connector
from oandapyV20.contrib.requests import MarketOrderRequest, TradeCloseRequest, TrailingStopLossOrderRequest, StopLossOrderRequest, TakeProfitDetails, StopLossDetails, TrailingStopLossDetails
import oandapyV20.endpoints.orders as orders 
import oandapyV20.endpoints.trades as trades
import oandapyV20.endpoints.pricing as pricing
import oandapyV20.endpoints.accounts as accounts


import datetime as dt
import pandas as pd
import talib as ta
import numpy as np
import time
from pathlib import Path

import fx_Econcalendar_2


from plotly.subplots import make_subplots
import json
import plotly.graph_objs as go
from plotly.offline import plot
import matplotlib.pyplot as plt

from oanda_backtest import Backtest

################################################
riskPercent = .02
openTradesList = []
openTradesList_BE = []

# Defining Path That Will Be Needed to Grab Currency Data
path = str(Path(__file__).parent.absolute())
path=path.replace("\\","\\\\")
#path=path[:path.find("** Enter Folder Here **")]
print(path)

################################################
# Access to Oanda API

access_token = "---Add Access Token---"
accountID = "--Add Account ID---"
client = API(access_token = access_token)
openTrades = Oanda_Connector.getOpenTrades(access_token, accountID)
     

###############################################
# 0. Logic for News Impacted Currencies (1 Script to Include 1 Function) 
"""
    * Pull Economic Calendar to Check High Impact News Events on Currencies 
    * Check the Currencies that are Highly Impacted for Previous, Current, and Next Day
    * Store Those Currencies Into a Log (string or list...)
    * Ensure That Currency Pairs with that contain a Highly Impacted Currency is Not Traded
    * Ensure That this Calendar is Checked Every Day
    * ? Need to Figure Out How To Decide On # Currency Pairs to Trade ? *
"""


# Pullin Forex Calendar and Getting the High Impact Events
calendar = fx_Econcalendar_2.FXEconomic_Connector.getEconomicCalendar()
noTradeCurrencies = fx_Econcalendar_2.FXEconomic_Connector.getImpactedCurrencies()


###############################################
###########################################################
# 1. Logic for Trade Management
###########################################################
# Trade Management while waiting to evaluate trades
for trade in openTradesList:
    if trade['instrument'] in openTrades:
        # Long Trades
        if int(trade['units']) > 0:
            print("Trade {} is a Long".format(trade['instrument']))
            fx_pair = trade['instrument'][0:3]+trade['instrument'][4:7]
            Bid = Oanda_Connector.getPricing(access_token, accountID, fx_pair, "Bid")
            diffPrice = Bid - float(trade['openPrice'])
            if 'JPY' in fx_pair:
                pips = diffPrice * 100 
                df = pd.read_csv(path+'\\Forex_OHLC\\'+fx_pair+'.csv')
                ATR = ta.ATR(df['high'], df['low'], df['close'], timeperiod=14)
                tempATR = ATR.iloc[-1] * 100
                
                if pips <= tempATR:
                    if trade['instrument'] not in openTradesList_BE:
                        print("Taking half the Trade off and Adjusting Stop Loss")
                        unitsProfit = int(trade['units']) / 2
                        cOrder = TradeCloseRequest(units = unitsProfit)
                        rt = trades.TradeClose(accountID=accountID, tradeID=trade["tradeID"], data=cOrder.data)
                        client.request(rt)
                        Bid = Oanda_Connector.getPricing(access_token, accountID, fx_pair, "Bid")
                        Ask = Oanda_Connector.getPricing(access_token, accountID, fx_pair, "Ask")
                        spread = Ask - Bid
                        price = float(trade['openPrice']) + spread + 0.01
                        ordr = StopLossOrderRequest(tradeID=trade["tradeID"], price=price)
                        orderID = str(int(trade["tradeID"])+2)
                        r = orders.OrderReplace(accountID, orderID=orderID, data=ordr.data)
                        client.request(r)
                        openTradesList_BE.append(trade['instrument'])
                        print(openTradesList_BE)
                        
                        """
                        # Remove Trade from Open Trades List
                        for i in range(len(openTradesList)):
                            if openTradesList[i]['instrument'] == trade["instrument"]:
                                print("Removed from openTradesList.....")
                                del openTradesList[i]
                                print(openTradesList)
                                break
                            else:
                                continue
                           
                        # Remove Trade from Open Trades Breakeven List Pip Adjustment
                        for i in range(len(openTradesList_BE)):
                            if openTradesList_BE[i]['instrument'] == trade["instrument"]:
                                print("Removed from openTradesList 15 pips.....")
                                del openTradesList_BE[i]
                                print(openTradesList_BE)
                                break
                            else:
                                continue
                          """ 
                          
                else:  
                    print("No Trade Management Needed At This Time........")
            else:
                pips = diffPrice * 10000
                df = pd.read_csv(path+'\\Forex_OHLC\\'+fx_pair+'.csv')
                ATR = ta.ATR(df['high'], df['low'], df['close'], timeperiod=14)
                tempATR = ATR.iloc[-1] * 10000
                
                if pips <= tempATR:
                    if trade['instrument'] not in openTradesList_BE:
                        print("Taking half the Trade off and Adjusting Stop Loss")
                        unitsProfit = int(trade['units']) / 2
                        cOrder = TradeCloseRequest(units = unitsProfit)
                        rt = trades.TradeClose(accountID=accountID, tradeID=trade["tradeID"], data=cOrder.data)
                        client.request(rt)
                        Bid = Oanda_Connector.getPricing(access_token, accountID, fx_pair, "Bid")
                        Ask = Oanda_Connector.getPricing(access_token, accountID, fx_pair, "Ask")
                        spread = Ask - Bid
                        price = float(trade['openPrice']) + spread + 0.0001
                        ordr = StopLossOrderRequest(tradeID=trade["tradeID"], price=price)
                        orderID = str(int(trade["tradeID"])+2)
                        r = orders.OrderReplace(accountID, orderID=orderID, data=ordr.data)
                        client.request(r)
                        openTradesList_BE.append(trade['instrument'])
                        print(openTradesList_BE)
                    
                    """
                    # Remove Trade from Open Trades List
                    for i in range(len(openTradesList)):
                        if openTradesList[i]['instrument'] == trade["instrument"]:
                            print("Removed from openTradesList.....")
                            del openTradesList[i]
                            print(openTradesList)
                            break
                        else: 
                            continue
                               
                    # Remove Trade from Open Trades Breakeven List Pip Adjustment
                    for i in range(len(openTradesList_BE)):
                        if openTradesList_BE[i]['instrument'] == trade["instrument"]:
                            print("Removed from openTradesList 15 pips.....")
                            del openTradesList_BE[i]
                            print(openTradesList_BE)
                            break
                        else:
                            continue
                    """
                    
                else:
                    print("No Trade Management Needed At This Time........")
                    
                    
        # Short Trades        
        elif int(trade['units']) < 0:
            print("Trade {} is a Short".format(trade['instrument']))
            fx_pair = trade['instrument'][0:3]+trade['instrument'][4:7]
            Ask = Oanda_Connector.getPricing(access_token, accountID, fx_pair, "Ask")
            diffPrice = float(trade['openPrice']) - Ask
            if 'JPY' in fx_pair:
                pips = diffPrice * 100 
                df = pd.read_csv(path+'\\Forex_OHLC\\'+fx_pair+'.csv')
                ATR = ta.ATR(df['high'], df['low'], df['close'], timeperiod=14)
                tempATR = ATR.iloc[-1] * 100
                
                if pips <= tempATR:
                    if trade['instrument'] not in openTradesList_BE:
                        print("Taking half the Trade off and Adjusting Stop Loss")
                        unitsProfit = int(trade['units']) / 2
                        rt = trades.TradeClose(accountID=accountID, tradeID=trade["tradeID"], data=cOrder.data)
                        client.request(rt)
                        Bid = Oanda_Connector.getPricing(access_token, accountID, fx_pair, "Bid")
                        Ask = Oanda_Connector.getPricing(access_token, accountID, fx_pair, "Ask")
                        spread = Ask - Bid
                        price = float(trade['openPrice']) - spread - 0.01
                        ordr = StopLossOrderRequest(tradeID=trade["tradeID"], price=price)
                        orderID = str(int(trade["tradeID"])+2)
                        r = orders.OrderReplace(accountID, orderID=orderID, data=ordr.data)
                        client.request(r)
                        openTradesList_BE.append(trade['instrument'])
                        print(openTradesList_BE)
                        
                        """
                        # Remove Trade from Open Trades List
                        for i in range(len(openTradesList)):
                            if openTradesList[i]['instrument'] == trade["instrument"]:
                                print("Removed from openTradesList.....")
                                del openTradesList[i]
                                print(openTradesList)
                                break
                            else:
                                continue
                           
                        # Remove Trade from Open Trades Breakeven List Pip Adjustment
                        for i in range(len(openTradesList_BE)):
                            if openTradesList_BE[i]['instrument'] == trade["instrument"]:
                                print("Removed from openTradesList 15 pips.....")
                                del openTradesList_BE[i]
                                print(openTradesList_BE)
                                break
                            else:
                                continue
                        """
            
            else:
                pips = diffPrice * 10000
                df = pd.read_csv(path+'\\Forex_OHLC\\'+fx_pair+'.csv')
                ATR = ta.ATR(df['high'], df['low'], df['close'], timeperiod=14)
                tempATR = ATR.iloc[-1] * 10000
                
                if pips <= tempATR:
                    if trade['instrument'] not in openTradesList_BE:
                        print("Taking half the Trade off and Adjusting Stop Loss")
                        unitsProfit = int(trade['units']) / 2
                        rt = trades.TradeClose(accountID=accountID, tradeID=trade["tradeID"], data=cOrder.data)
                        client.request(rt)
                        Bid = Oanda_Connector.getPricing(access_token, accountID, fx_pair, "Bid")
                        Ask = Oanda_Connector.getPricing(access_token, accountID, fx_pair, "Ask")
                        spread = Ask - Bid
                        price = float(trade['openPrice']) - spread - 0.01
                        ordr = StopLossOrderRequest(tradeID=trade["tradeID"], price=price)
                        orderID = str(int(trade["tradeID"])+2)
                        r = orders.OrderReplace(accountID, orderID=orderID, data=ordr.data)
                        client.request(r)
                        openTradesList_BE.append(trade['instrument'])
                        print(openTradesList_BE)
                        
                        """
                        # Remove Trade from Open Trades List
                        for i in range(len(openTradesList)):
                            if openTradesList[i]['instrument'] == trade["instrument"]:
                                print("Removed from openTradesList.....")
                                del openTradesList[i]
                                print(openTradesList)
                                break
                            else:
                                continue
                           
                        # Remove Trade from Open Trades Breakeven List Pip Adjustment
                        for i in range(len(openTradesList_BE)):
                            if openTradesList_BE[i]['instrument'] == trade["instrument"]:
                                print("Removed from openTradesList 15 pips.....")
                                del openTradesList_BE[i]
                                print(openTradesList_BE)
                                break
                            else:
                                continue
                        """
                        
                        
                        
    elif trade['instrument'] not in openTrades:   
        # Remove Trade from Open Trades List
        print("Trade is not in Open Trades and Need to Remove From List")
        for i in range(len(openTradesList)):
            if openTradesList[i]['instrument'] == trade["instrument"]:
                print("Removed from openTradesList.....")
                del openTradesList[i]
                break
            else: 
                continue  
    
    # Remove Trade from Open Trades Breakeven List Pip Adjustment
        for i in range(len(openTradesList_BE)):
            if openTradesList_BE[i]['instrument'] == trade["instrument"]:
                print("Removed from openTradesList 15 pips.....")
                del openTradesList_BE[i]
                break
            else:
                continue
    else:
                    continue
                
print("Im Done with Managing Each Trade!")
print("==============================")                   
                        
                               
    

            
###############################################
# 1. Logic for Getting Data for the 1-Day Prices 
# (4 Scripts to Include 4 Functions)
"""
    * Create a List (or string) of Currencies to Trade Based on the Econ Calendar Logic
    * Pull 1-Day Pricing Data
    * Save Data For Each TimeFrame to a DataFrame Variable 
"""

# Getting Currency Pairs To Evaluate
logs = ''     #fetch oanda current open orders data with your own api key, convert data to string and check if the pair is inside string object


"""
   28 Major Currency Pairs: 
   AUDJPY CADJPY CHFJPY EURJPY NZDJPY USDJPY GBPJPY AUDUSD EURUSD GBPUSD NZDUSD USDCAD USDCHF AUDCAD CADCHF EURCAD GBPCAD NZDCAD AUDCHF EURCHF GBPCHF NZDCHF EURAUD EURGBP EURNZD GBPNZD GBPAUD AUDNZD
"""


fx_pairs = 'AUDJPY CADJPY CHFJPY EURJPY NZDJPY USDJPY GBPJPY AUDUSD EURUSD GBPUSD NZDUSD USDCAD USDCHF AUDCAD CADCHF EURCAD GBPCAD NZDCAD AUDCHF EURCHF GBPCHF NZDCHF EURAUD EURGBP EURNZD GBPNZD GBPAUD AUDNZD'
#fx_pairs = 'AUDNZD'
fx_pairs = fx_pairs.replace(' ','')
run_Pairs = (len(fx_pairs)-1)

while len(fx_pairs)>0:  
    
    string=fx_pairs[-6:]
    fx_pairs=fx_pairs[0:-6]
    dummyString = string[0:3] + "_" + string[3:6]
    df = pd.read_csv(path+'\\Forex_OHLC\\'+string+'.csv')
    df=df.drop('Unnamed: 0', 1)
    df=df.drop('complete', 1)
    #df=df.drop('time', 1)
    df=df.drop('volume', 1)
    #print('Obtained ', string, 'data!')
    
    Oanda_Connector.pullCandleData(access_token, path+'\\Forex_OHLC\\', string, 1000, "D")
    
    df['time'] = pd.to_datetime(df['time'],unit='s')
    df.set_index('time')
    
    
    ###############################################
    # 2. Logic for Exiting an Exising Trade
    """
        * Exit Exisiting Buy Orders:
            The Tenkan-sen crosses under the Kijun-sen
            or candlestick patterns forms in a reversal (Sell Side)
            
        * Exit Exisiting Sell Orders:
            The Tenkan-sen crosses above the Kijun-sen
            or candlestick patterns forms in a reversal (Buy Side)
    
    """
    # Indicators
    ATR = ta.ATR(df['high'], df['low'], df['close'], timeperiod=14)   # ATR for trade management (Stop lose to 1.5xATR and TP_1 to 1xATR)
    
    
    # Tenkan-sen (Conversion Line): (9-period high + 9-period low)/2))
    nine_period_high = df['high'].rolling(window= 9).max()
    nine_period_low = df['low'].rolling(window= 9).min()
    tenkanSen = (nine_period_high + nine_period_low) /2
    
    # Kijun-sen (Base Line): (26-period high + 26-period low)/2))
    period26_high = df['high'].rolling(window=26).max()
    period26_low = df['low'].rolling(window=26).min()
    kijunSen = (period26_high + period26_low) / 2
    
    # Senkou Span A (Leading Span A): (Conversion Line + Base Line)/2))
    senkouSpan_A = ((tenkanSen + kijunSen) / 2).shift(26)
    
    # Senkou Span B (Leading Span B): (52-period high + 52-period low)/2))
    period52_high = df['high'].rolling(window=52).max()
    period52_low = df['low'].rolling(window=52).min()
    senkouSpan_B = ((period52_high + period52_low) / 2).shift(26)
    
    #Candlestick Patterns
    # BULLISH
    candleEngulfing = ta.CDLENGULFING(df['open'], df['high'], df['low'], df['close'])  #(+100 is bullish engulfing and -100 is bearish engulfing)
    candlePiercing = ta.CDLPIERCING(df['open'], df['high'], df['low'], df['close'])    #(+100 is confirmation of a piercing line)
    candleMorningStar = ta.CDLMORNINGSTAR(df['open'], df['high'], df['low'], df['close'], penetration=0) #(+100 is confirmation of a morning star)
    candle3WhiteSoldiers = ta.CDL3WHITESOLDIERS(df['open'], df['high'], df['low'], df['close'])
    
    #BEARISH
    candleShootingStar = ta.CDLSHOOTINGSTAR(df['open'], df['high'], df['low'], df['close'])
    candleEveningStar = ta.CDLEVENINGSTAR(df['open'], df['high'], df['low'], df['close'], penetration=0)
    candleDarkCloudCover = ta.CDLDARKCLOUDCOVER(df['open'], df['high'], df['low'], df['close'], penetration=0)
    candle3BlackCrows = ta.CDL3BLACKCROWS(df['open'], df['high'], df['low'], df['close'])
    
    for trade in openTradesList:
        if trade['instrument'] == dummyString:
            print("Found Trade in List!!!!")
            units = int(trade['units'])
            
            # If Trade is a Long
            if units > 0:
                print("Its a Long!!!....")
                firstExitConfirmation = np.logical_and(tenkanSen.iloc[-1] < kijunSen.iloc[-1], tenkanSen.iloc[-2] > kijunSen.iloc[-2]) # Tenkan Sen and Kijun Sen lines cross
                
                if firstExitConfirmation:
                    print("Need to Exit Long!!!!!.....")
                    cOrder = TradeCloseRequest(units = units)
                    rt = trades.TradeClose(accountID=accountID, tradeID=trade["tradeID"], data=cOrder.data)
                    client.request(rt)
                    
                    # Remove Trade from Open Trades List
                    for i in range(len(openTradesList)):
                        if openTradesList[i]['instrument'] == dummyString:
                            print("Removed from openTradesList.....")
                            del openTradesList[i]
                            print(openTradesList)
                            break
                        else:
                            continue
                         
                    # Remove Trade from Open Trades Breakeven List Pip Adjustment
                    for i in range(len(openTradesList_BE)):
                        if openTradesList_BE[i]['instrument'] == dummyString:
                            print("Removed from openTradesList_15pips..........")
                            del openTradesList_BE[i]
                            print(openTradesList_BE)
                            break
                        else:
                            continue
                
                if candleEngulfing.iloc[-1] == -100:
                    print("Bearish Engulfing Found")
                    print("Need to Exit Long!!!!!.....")
                    cOrder = TradeCloseRequest(units = units)
                    rt = trades.TradeClose(accountID=accountID, tradeID=trade["tradeID"], data=cOrder.data)
                    client.request(rt)
                    
                    # Remove Trade from Open Trades List
                    for i in range(len(openTradesList)):
                        if openTradesList[i]['instrument'] == dummyString:
                            print("Removed from openTradesList.....")
                            del openTradesList[i]
                            print(openTradesList)
                            break
                        else:
                            continue
                         
                    # Remove Trade from Open Trades Breakeven List Pip Adjustment
                    for i in range(len(openTradesList_BE)):
                        if openTradesList_BE[i]['instrument'] == dummyString:
                            print("Removed from openTradesList_15pips..........")
                            del openTradesList_BE[i]
                            print(openTradesList_BE)
                            break
                        else:
                            continue
                    
                
            
                elif candleShootingStar.iloc[-1] == -100:
                    print("Shooting Star Found")
                    print("Need to Exit Long!!!!!.....")
                    cOrder = TradeCloseRequest(units = units)
                    rt = trades.TradeClose(accountID=accountID, tradeID=trade["tradeID"], data=cOrder.data)
                    client.request(rt)
                    
                    # Remove Trade from Open Trades List
                    for i in range(len(openTradesList)):
                        if openTradesList[i]['instrument'] == dummyString:
                            print("Removed from openTradesList.....")
                            del openTradesList[i]
                            print(openTradesList)
                            break
                        else:
                            continue
                         
                    # Remove Trade from Open Trades Breakeven List Pip Adjustment
                    for i in range(len(openTradesList_BE)):
                        if openTradesList_BE[i]['instrument'] == dummyString:
                            print("Removed from openTradesList_15pips..........")
                            del openTradesList_BE[i]
                            print(openTradesList_BE)
                            break
                        else:
                            continue
                    
                    
                elif candleEveningStar.iloc[-1] == -100:
                    print("Evening Star Found")
                    print("Need to Exit Long!!!!!.....")
                    cOrder = TradeCloseRequest(units = units)
                    rt = trades.TradeClose(accountID=accountID, tradeID=trade["tradeID"], data=cOrder.data)
                    client.request(rt)
                    
                    # Remove Trade from Open Trades List
                    for i in range(len(openTradesList)):
                        if openTradesList[i]['instrument'] == dummyString:
                            print("Removed from openTradesList.....")
                            del openTradesList[i]
                            print(openTradesList)
                            break
                        else:
                            continue
                         
                    # Remove Trade from Open Trades Breakeven List Pip Adjustment
                    for i in range(len(openTradesList_BE)):
                        if openTradesList_BE[i]['instrument'] == dummyString:
                            print("Removed from openTradesList_15pips..........")
                            del openTradesList_BE[i]
                            print(openTradesList_BE)
                            break
                        else:
                            continue
                    
                    
                elif candleDarkCloudCover.iloc[-1] == -100:
                    print("Dark Cloud Cover Found")
                    print("Need to Exit Long!!!!!.....")
                    cOrder = TradeCloseRequest(units = units)
                    rt = trades.TradeClose(accountID=accountID, tradeID=trade["tradeID"], data=cOrder.data)
                    client.request(rt)
                    
                    # Remove Trade from Open Trades List
                    for i in range(len(openTradesList)):
                        if openTradesList[i]['instrument'] == dummyString:
                            print("Removed from openTradesList.....")
                            del openTradesList[i]
                            print(openTradesList)
                            break
                        else:
                            continue
                         
                    # Remove Trade from Open Trades Breakeven List Pip Adjustment
                    for i in range(len(openTradesList_BE)):
                        if openTradesList_BE[i]['instrument'] == dummyString:
                            print("Removed from openTradesList_15pips..........")
                            del openTradesList_BE[i]
                            print(openTradesList_BE)
                            break
                        else:
                            continue
                   
                    
                elif candle3BlackCrows.iloc[-1] == -100:
                    print("Black Crows Found")
                    print("Need to Exit Long!!!!!.....")
                    cOrder = TradeCloseRequest(units = units)
                    rt = trades.TradeClose(accountID=accountID, tradeID=trade["tradeID"], data=cOrder.data)
                    client.request(rt)
                    
                    # Remove Trade from Open Trades List
                    for i in range(len(openTradesList)):
                        if openTradesList[i]['instrument'] == dummyString:
                            print("Removed from openTradesList.....")
                            del openTradesList[i]
                            print(openTradesList)
                            break
                        else:
                            continue
                         
                    # Remove Trade from Open Trades Breakeven List Pip Adjustment
                    for i in range(len(openTradesList_BE)):
                        if openTradesList_BE[i]['instrument'] == dummyString:
                            print("Removed from openTradesList_15pips..........")
                            del openTradesList_BE[i]
                            print(openTradesList_BE)
                            break
                        else:
                            continue
                        
                print('=======================')
             
            # If Trade is a Short             
            elif units < 0: 
                print("Its a Short!!!......")
                firstExitConfirmation = np.logical_and(tenkanSen.iloc[-1] > kijunSen.iloc[-1], tenkanSen.iloc[-2] < kijunSen.iloc[-2]) # Tenkan Sen and Kijun Sen lines cross
                
                if firstExitConfirmation:
                    print("Need to Exit Short!!!!!.....")
                    cOrder = TradeCloseRequest(units = units)
                    rt = trades.TradeClose(accountID=accountID, tradeID=trade["tradeID"], data=cOrder.data)
                    client.request(rt)
                    
                    # Remove Trade from Open Trades List
                    for i in range(len(openTradesList)):
                        if openTradesList[i]['instrument'] == dummyString:
                            print("Removed from openTradesList.....")
                            del openTradesList[i]
                            print(openTradesList)
                            break
                        else:
                            continue
                         
                    # Remove Trade from Open Trades Breakeven List Pip Adjustment
                    for i in range(len(openTradesList_BE)):
                        if openTradesList_BE[i]['instrument'] == dummyString:
                            print("Removed from openTradesList_15pips..........")
                            del openTradesList_BE[i]
                            print(openTradesList_BE)
                            break
                        else:
                            continue
                    
                if candleEngulfing.iloc[-1] == -100:
                    print("Bearish Engulfing Found")
                    print("Need to Exit Short!!!!!.....")
                    cOrder = TradeCloseRequest(units = units)
                    rt = trades.TradeClose(accountID=accountID, tradeID=trade["tradeID"], data=cOrder.data)
                    client.request(rt)
                    
                    # Remove Trade from Open Trades List
                    for i in range(len(openTradesList)):
                        if openTradesList[i]['instrument'] == dummyString:
                            print("Removed from openTradesList.....")
                            del openTradesList[i]
                            print(openTradesList)
                            break
                        else:
                            continue
                         
                    # Remove Trade from Open Trades Breakeven List Pip Adjustment
                    for i in range(len(openTradesList_BE)):
                        if openTradesList_BE[i]['instrument'] == dummyString:
                            print("Removed from openTradesList_15pips..........")
                            del openTradesList_BE[i]
                            print(openTradesList_BE)
                            break
                        else:
                            continue
                
            
                elif candleShootingStar.iloc[-1] == -100:
                    print("Shooting Star Found")
                    print("Need to Exit Short!!!!!.....")
                    cOrder = TradeCloseRequest(units = units)
                    rt = trades.TradeClose(accountID=accountID, tradeID=trade["tradeID"], data=cOrder.data)
                    client.request(rt)
                    
                    # Remove Trade from Open Trades List
                    for i in range(len(openTradesList)):
                        if openTradesList[i]['instrument'] == dummyString:
                            print("Removed from openTradesList.....")
                            del openTradesList[i]
                            print(openTradesList)
                            break
                        else:
                            continue
                         
                    # Remove Trade from Open Trades Breakeven List Pip Adjustment
                    for i in range(len(openTradesList_BE)):
                        if openTradesList_BE[i]['instrument'] == dummyString:
                            print("Removed from openTradesList_15pips..........")
                            del openTradesList_BE[i]
                            print(openTradesList_BE)
                            break
                        else:
                            continue
                    
                    
                elif candleEveningStar.iloc[-1] == -100:
                    print("Evening Star Found")
                    print("Need to Exit Short!!!!!.....")
                    cOrder = TradeCloseRequest(units = units)
                    rt = trades.TradeClose(accountID=accountID, tradeID=trade["tradeID"], data=cOrder.data)
                    client.request(rt)
                    
                    # Remove Trade from Open Trades List
                    for i in range(len(openTradesList)):
                        if openTradesList[i]['instrument'] == dummyString:
                            print("Removed from openTradesList.....")
                            del openTradesList[i]
                            print(openTradesList)
                            break
                        else:
                            continue
                         
                    # Remove Trade from Open Trades Breakeven List Pip Adjustment
                    for i in range(len(openTradesList_BE)):
                        if openTradesList_BE[i]['instrument'] == dummyString:
                            print("Removed from openTradesList_15pips..........")
                            del openTradesList_BE[i]
                            print(openTradesList_BE)
                            break
                        else:
                            continue
                    
                    
                elif candleDarkCloudCover.iloc[-1] == -100:
                    print("Dark Cloud Cover Found")
                    print("Need to Exit Short!!!!!.....")
                    cOrder = TradeCloseRequest(units = units)
                    rt = trades.TradeClose(accountID=accountID, tradeID=trade["tradeID"], data=cOrder.data)
                    client.request(rt)
                    
                    # Remove Trade from Open Trades List
                    for i in range(len(openTradesList)):
                        if openTradesList[i]['instrument'] == dummyString:
                            print("Removed from openTradesList.....")
                            del openTradesList[i]
                            print(openTradesList)
                            break
                        else:
                            continue
                         
                    # Remove Trade from Open Trades Breakeven List Pip Adjustment
                    for i in range(len(openTradesList_BE)):
                        if openTradesList_BE[i]['instrument'] == dummyString:
                            print("Removed from openTradesList_15pips..........")
                            del openTradesList_BE[i]
                            print(openTradesList_BE)
                            break
                        else:
                            continue
                    
                    
                elif candle3BlackCrows.iloc[-1] == -100:
                    print("Black Crows Found")
                    print("Need to Exit Short!!!!!.....")
                    cOrder = TradeCloseRequest(units = units)
                    rt = trades.TradeClose(accountID=accountID, tradeID=trade["tradeID"], data=cOrder.data)
                    client.request(rt)
                    
                    # Remove Trade from Open Trades List
                    for i in range(len(openTradesList)):
                        if openTradesList[i]['instrument'] == dummyString:
                            print("Removed from openTradesList.....")
                            del openTradesList[i]
                            print(openTradesList)
                            break
                        else:
                            continue
                         
                    # Remove Trade from Open Trades Breakeven List Pip Adjustment
                    for i in range(len(openTradesList_BE)):
                        if openTradesList_BE[i]['instrument'] == dummyString:
                            print("Removed from openTradesList_15pips..........")
                            del openTradesList_BE[i]
                            print(openTradesList_BE)
                            break
                        else:
                            continue
                    
                    
                print("========================")
                
            else:
                print("Not Found in this iteration.....")
                            
        else:
            continue
                    
               
                   
    
    
        
    
    
    ###############################################
    # 3. Logic for Buying and Selling New Opportunities
    """
        * Buy Signals:
            - Tenkan Sen needs to be above the Kijun Sen, Senkou Span A, Senkou Span B and a bullish candlestick pattern confirmation
            - Buying Logic (Tenkan-sen needs to be above the Kijun-sen, Senkou Span A, and Senkou Span B plus a candlestick pattern for confirmation)
            - Candlestick Pattern Confirmation for Bullish (Bullish Engulfing, Hammer, Piercing Line, Morning Star, or Three White Soldiers)
    
                                
        * Sell Signals:
            - Tenkan Sen needs to be below the Kijun Sen, Senkou Span A, Senkou Span B and a bearish candlestick pattern confirmation 
            - Tenkan-sen needs to be below the Kijun-sen, Senkou Span A, and Senkou Span B plus a candlestick pattern for confirmation)
            - Candlestick Pattern Confirmation for Bullish (Bearish Engulfing, Shooting Star, Evening Star, Dark Cloud Cover, or Three Black Crows)

    """
    indiBuyEntry = np.logical_and(np.logical_and(tenkanSen > kijunSen, tenkanSen > senkouSpan_A), tenkanSen > senkouSpan_B)
    
    if indiBuyEntry.iloc[-1] == True:             # Checking the last candle for entries
        currenciesInTrade = Oanda_Connector.getOpenTrades(access_token, accountID)
        firstCurr = [string[0:3] for string in currenciesInTrade if(string in currenciesInTrade)]
        secondCurr = [string[4:7] for string in currenciesInTrade if(string in currenciesInTrade)]
        if (string[0:3] in firstCurr) or (string[3:6] in secondCurr):
            print("Already in a Trade with Another Pair... Sorry!")
    
            
        request = accounts.AccountSummary(accountID)
        rv = client.request(request)
        balance = rv['account']['balance']
        amountRisk = float(balance) * riskPercent

        pipValue = 0
        if string[3:6] == 'USD':
            pipValue = 0.10
            
        elif string[0:3] == 'USD':
            if string[3:6] == 'JPY':
                Ask = Oanda_Connector.getPricing(access_token, accountID, string, "Ask")
                pipValue = 10/Ask
            else:
                Ask = Oanda_Connector.getPricing(access_token, accountID, string, "Ask")
                pipValue = .1/Ask
        
        elif (string[0:3] != 'USD') and (string[3:6] == 'JPY'):
            Ask = Oanda_Connector.getPricing(access_token, accountID, 'USDJPY', "Ask")
            pipValue = 10/Ask
            
        elif (string[0:3] != 'USD') and (string[3:6] == 'CAD'):
            Ask = Oanda_Connector.getPricing(access_token, accountID, 'USDCAD', "Ask")
            pipValue = .1/Ask
            
        elif (string[0:3] != 'USD') and (string[3:6] == 'CHF'):
            Ask = Oanda_Connector.getPricing(access_token, accountID, 'USDCHF', "Ask")
            pipValue = .1/Ask
            
        elif (string[0:3] != 'USD') and (string[3:6] == 'NZD'):
            Bid = Oanda_Connector.getPricing(access_token, accountID, 'NZDUSD', "Bid")
            pipValue = .1*Bid
        
        elif (string[0:3] != 'USD') and (string[3:6] == 'AUD'):
            Bid = Oanda_Connector.getPricing(access_token, accountID, 'AUDUSD', "Bid")
            pipValue = .1*Bid
        
        elif (string[0:3] != 'USD') and (string[3:6] == 'GBP'):
            Bid = Oanda_Connector.getPricing(access_token, accountID, 'GBPUSD', "Bid")
            pipValue = .1*Bid
        
        else:
            print("Something is wrong!!!")
        
        unitsForTrade = int((amountRisk / (30 * pipValue)) * 100)
        
        # Need to include ATR values for the take profit and stop loss parameters on the market orders

    
        if candleEngulfing.iloc[-1] == 100:
            # Execute Market Order Logic
            print("Bullish Engulfing Found")
            print('Entering A Buy!!!!')
            r = Oanda_Connector.marketOrder(access_token, accountID, string, "Buy", unitsForTrade, takeProfit = 0, stopLoss = 0)
            R = r
            instrument = R['orderCreateTransaction']['instrument']
            openPrice = R['orderFillTransaction']['price']
            takeProfit = R['orderCreateTransaction']['takeProfitOnFill']['price']
            stopLoss = R['orderCreateTransaction']['stopLossOnFill']['price']
            tradeID = R['orderFillTransaction']['tradeOpened']['tradeID']
            units = R['orderFillTransaction']['units']
           
            dict_  = {
                    "instrument": instrument,
                    "openPrice": openPrice,
                    "takeProfit": takeProfit,
                    "stopLoss": stopLoss,
                    "tradeID": tradeID,
                    "units": units
                    }
   
            openTradesList.append(dict_)
            print(dict_)
            print(openTradesList)
            print('=======================')
            
            
        elif candlePiercing.iloc[-1] == 100:
            # Execute Market Order Logic
            print("Piercing Candle Found")
            print('Entering A Buy!!!!')
            r = Oanda_Connector.marketOrder(access_token, accountID, string, "Buy", unitsForTrade, takeProfit = 0, stopLoss = 0)
            R = r
            instrument = R['orderCreateTransaction']['instrument']
            openPrice = R['orderFillTransaction']['price']
            takeProfit = R['orderCreateTransaction']['takeProfitOnFill']['price']
            stopLoss = R['orderCreateTransaction']['stopLossOnFill']['price']
            tradeID = R['orderFillTransaction']['tradeOpened']['tradeID']
            units = R['orderFillTransaction']['units']
           
            dict_  = {
                    "instrument": instrument,
                    "openPrice": openPrice,
                    "takeProfit": takeProfit,
                    "stopLoss": stopLoss,
                    "tradeID": tradeID,
                    "units": units
                    }
   
            openTradesList.append(dict_)
            print(dict_)
            print(openTradesList)
            print('=======================')
            
        elif candleMorningStar.iloc[-1] == 100:
            # Execute Market Order Logic
            print("Morning Star Found")
            print('Entering A Buy!!!!')
            r = Oanda_Connector.marketOrder(access_token, accountID, string, "Buy", unitsForTrade, takeProfit = 0, stopLoss = 0)
            R = r
            instrument = R['orderCreateTransaction']['instrument']
            openPrice = R['orderFillTransaction']['price']
            takeProfit = R['orderCreateTransaction']['takeProfitOnFill']['price']
            stopLoss = R['orderCreateTransaction']['stopLossOnFill']['price']
            tradeID = R['orderFillTransaction']['tradeOpened']['tradeID']
            units = R['orderFillTransaction']['units']
           
            dict_  = {
                    "instrument": instrument,
                    "openPrice": openPrice,
                    "takeProfit": takeProfit,
                    "stopLoss": stopLoss,
                    "tradeID": tradeID,
                    "units": units
                    }
   
            openTradesList.append(dict_)
            print(dict_)
            print(openTradesList)
            print('=======================')
            
        elif candle3WhiteSoldiers.iloc[-1] == 100:
            # Execute Market Order Logic
            print("White Soldiers Found")
            print('Entering A Buy!!!!')
            r = Oanda_Connector.marketOrder(access_token, accountID, string, "Buy", unitsForTrade, takeProfit = 0, stopLoss = 0)
            R = r
            print(R)
            
            instrument = R['orderCreateTransaction']['instrument']
            openPrice = R['orderFillTransaction']['price']
            takeProfit = R['orderCreateTransaction']['takeProfitOnFill']['price']
            stopLoss = R['orderCreateTransaction']['stopLossOnFill']['price']
            tradeID = R['orderFillTransaction']['tradeOpened']['tradeID']
            units = R['orderFillTransaction']['units']
           
            dict_  = {
                    "instrument": instrument,
                    "openPrice": openPrice,
                    "takeProfit": takeProfit,
                    "stopLoss": stopLoss,
                    "tradeID": tradeID,
                    "units": units
                    }
   
            openTradesList.append(dict_)
            print(dict_)
            print(openTradesList)
            
            print('=======================')
            
        else:
            print("No Confirmations at this time")
                   
    else:
        print("No Buy Signal.....")
        print(openTradesList)
        print('=======================')
    
   
    
    indiSellEntry = np.logical_and(np.logical_and(tenkanSen < kijunSen, tenkanSen < senkouSpan_A), tenkanSen < senkouSpan_B)
    
    
    if indiSellEntry.iloc[-1] == True:             # Checking the last candle for entries      
        currenciesInTrade = Oanda_Connector.getOpenTrades(access_token, accountID)
        firstCurr = [string[0:3] for string in currenciesInTrade if(string in currenciesInTrade)]
        secondCurr = [string[4:7] for string in currenciesInTrade if(string in currenciesInTrade)]
        if (string[0:3] in firstCurr) or (string[3:6] in secondCurr):
            print("Already in a Trade with Another Pair... Sorry!")
    
    
        else:
            request = accounts.AccountSummary(accountID)
            rv = client.request(request)
            balance = rv['account']['balance']
            amountRisk = float(balance) * riskPercent
            
            pipValue = 0
            if string[3:6] == 'USD':
                pipValue = 0.10
                
            elif string[0:3] == 'USD':
                if string[3:6] == 'JPY':
                    Ask = Oanda_Connector.getPricing(access_token, accountID, string, "Ask")
                    pipValue = 10/Ask
                else:
                    Ask = Oanda_Connector.getPricing(access_token, accountID, string, "Ask")
                    pipValue = .1/Ask
            
            elif (string[0:3] != 'USD') and (string[3:6] == 'JPY'):
                Ask = Oanda_Connector.getPricing(access_token, accountID, 'USDJPY', "Ask")
                pipValue = 10/Ask
                
            elif (string[0:3] != 'USD') and (string[3:6] == 'CAD'):
                Ask = Oanda_Connector.getPricing(access_token, accountID, 'USDCAD', "Ask")
                pipValue = .1/Ask
                
            elif (string[0:3] != 'USD') and (string[3:6] == 'CHF'):
                Ask = Oanda_Connector.getPricing(access_token, accountID, 'USDCHF', "Ask")
                pipValue = .1/Ask
                
            elif (string[0:3] != 'USD') and (string[3:6] == 'NZD'):
                Bid = Oanda_Connector.getPricing(access_token, accountID, 'NZDUSD', "Bid")
                pipValue = .1*Bid
            
            elif (string[0:3] != 'USD') and (string[3:6] == 'AUD'):
                Bid = Oanda_Connector.getPricing(access_token, accountID, 'AUDUSD', "Bid")
                pipValue = .1*Bid
            
            elif (string[0:3] != 'USD') and (string[3:6] == 'GBP'):
                Bid = Oanda_Connector.getPricing(access_token, accountID, 'GBPUSD', "Bid")
                pipValue = .1*Bid
            
            else:
                print("Something is wrong!!!")
            
            unitsForTrade = int((amountRisk / (30 * pipValue)) * 100)
            
            testing = Oanda_Connector.marketOrder(access_token, accountID, string, "Sell", unitsForTrade, takeProfit = 0, stopLoss = 0)
            print("====================")
            print(testing)
            
            if candleEngulfing.iloc[-1] == -100:
                # Execute Market Order Logic
                print("Bearish Engulfing Found")
                print('Entering A Sell!!!!')
                r = Oanda_Connector.marketOrder(access_token, accountID, string, "Sell", unitsForTrade, takeProfit = 0, stopLoss = 0)
                R = r
                instrument = R['orderCreateTransaction']['instrument']
                openPrice = R['orderFillTransaction']['price']
                takeProfit = R['orderCreateTransaction']['takeProfitOnFill']['price']
                stopLoss = R['orderCreateTransaction']['stopLossOnFill']['price']
                tradeID = R['orderFillTransaction']['tradeOpened']['tradeID']
                units = R['orderFillTransaction']['units']
               
                dict_  = {
                        "instrument": instrument,
                        "openPrice": openPrice,
                        "takeProfit": takeProfit,
                        "stopLoss": stopLoss,
                        "tradeID": tradeID,
                        "units": units
                        }
   
                openTradesList.append(dict_)
                print(dict_)
                print(openTradesList)
                print('=======================')
            
            elif candleShootingStar.iloc[-1] == -100:
                # Execute Market Order Logic
                print("Shooting Star Found")
                print('Entering A Sell!!!!')
                r = Oanda_Connector.marketOrder(access_token, accountID, string, "Sell", unitsForTrade, takeProfit = 0, stopLoss = 0)
                R = r
                instrument = R['orderCreateTransaction']['instrument']
                openPrice = R['orderFillTransaction']['price']
                takeProfit = R['orderCreateTransaction']['takeProfitOnFill']['price']
                stopLoss = R['orderCreateTransaction']['stopLossOnFill']['price']
                tradeID = R['orderFillTransaction']['tradeOpened']['tradeID']
                units = R['orderFillTransaction']['units']
               
                dict_  = {
                        "instrument": instrument,
                        "openPrice": openPrice,
                        "takeProfit": takeProfit,
                        "stopLoss": stopLoss,
                        "tradeID": tradeID,
                        "units": units
                        }
   
                openTradesList.append(dict_)
                print(dict_)
                print(openTradesList)
                print('=======================')
                
            elif candleEveningStar.iloc[-1] == -100:
                # Execute Market Order Logic
                print("Evening Star Found")
                print('Entering A Sell!!!!')
                r = Oanda_Connector.marketOrder(access_token, accountID, string, "Sell", unitsForTrade, takeProfit = 0, stopLoss = 0)
                R = r
                instrument = R['orderCreateTransaction']['instrument']
                openPrice = R['orderFillTransaction']['price']
                takeProfit = R['orderCreateTransaction']['takeProfitOnFill']['price']
                stopLoss = R['orderCreateTransaction']['stopLossOnFill']['price']
                tradeID = R['orderFillTransaction']['tradeOpened']['tradeID']
                units = R['orderFillTransaction']['units']
               
                dict_  = {
                        "instrument": instrument,
                        "openPrice": openPrice,
                        "takeProfit": takeProfit,
                        "stopLoss": stopLoss,
                        "tradeID": tradeID,
                        "units": units
                        }
   
                openTradesList.append(dict_)
                print(dict_)
                print(openTradesList)
                print('=======================')
                
            elif candleDarkCloudCover.iloc[-1] == -100:
                # Execute Market Order Logic
                print("Dark Cloud Cover Found")
                print('Entering A Sell!!!!')
                r = Oanda_Connector.marketOrder(access_token, accountID, string, "Sell", unitsForTrade, takeProfit = 0, stopLoss = 0)
                R = r
                instrument = R['orderCreateTransaction']['instrument']
                openPrice = R['orderFillTransaction']['price']
                takeProfit = R['orderCreateTransaction']['takeProfitOnFill']['price']
                stopLoss = R['orderCreateTransaction']['stopLossOnFill']['price']
                tradeID = R['orderFillTransaction']['tradeOpened']['tradeID']
                units = R['orderFillTransaction']['units']
               
                dict_  = {
                        "instrument": instrument,
                        "openPrice": openPrice,
                        "takeProfit": takeProfit,
                        "stopLoss": stopLoss,
                        "tradeID": tradeID,
                        "units": units
                        }
   
                openTradesList.append(dict_)
                print(dict_)
                print(openTradesList)
                print('=======================')
                
            elif candle3BlackCrows.iloc[-1] == -100:
                # Execute Market Order Logic
                print("Black Crows Found")
                print('Entering A Sell!!!!')
                r = Oanda_Connector.marketOrder(access_token, accountID, string, "Sell", unitsForTrade, takeProfit = 0, stopLoss = 0)
                R = r
                instrument = R['orderCreateTransaction']['instrument']
                openPrice = R['orderFillTransaction']['price']
                takeProfit = R['orderCreateTransaction']['takeProfitOnFill']['price']
                stopLoss = R['orderCreateTransaction']['stopLossOnFill']['price']
                tradeID = R['orderFillTransaction']['tradeOpened']['tradeID']
                units = R['orderFillTransaction']['units']
               
                dict_  = {
                        "instrument": instrument,
                        "openPrice": openPrice,
                        "takeProfit": takeProfit,
                        "stopLoss": stopLoss,
                        "tradeID": tradeID,
                        "units": units
                        }
   
                openTradesList.append(dict_)
                print(dict_)
                print(openTradesList)
                print('=======================')
                
            else:
                print("No Confirmations at this time")
                
       
    else:
        print("No Sell Signal.....")
        print(openTradesList)
        print('=======================')
    
    
    
    
    data = [go.Candlestick(x = df['time'],
                            open=df['open'],
                            high=df['high'],
                            low=df['low'],
                            close=df['close'])]
    
    data.append(dict(x=df['time'], y=tenkanSen, type='scatter', mode='lines', line=dict(width=1), marker=dict(color='#33BDFF'), name='Tenkan Sen'))
    data.append(dict(x=df['time'], y=kijunSen, type='scatter', mode='lines', line=dict(width=1), marker=dict(color='#F1F316'), name='Kijun Sen'))
    data.append(dict(x=df['time'], y=senkouSpan_A, type='scatter', mode='lines', line=dict(width=1), marker=dict(color='#228B22'), name='Senkou Span A'))
    data.append(dict(x=df['time'], y=senkouSpan_B, type='scatter', mode='lines', fill='tonexty', line=dict(width=1), marker=dict(color='#FF3342'), name='Senkou Span B'))

                                
    
    layout = dict(title=string,
                  xaxis=go.layout.XAxis(title=go.layout.xaxis.Title(text="Time"), rangeslider=dict(visible=False)),
                  yaxis=go.layout.YAxis(title=go.layout.yaxis.Title(text="Price")))
                                        
    fig = dict(data=data, layout=layout)
    plot(fig)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    """
    tenkanSen = pd.DataFrame(columns=['Tenkan Sen'], data=tenkanSen)
    kijunSen = pd.DataFrame(columns=['Kijun Sen'], data=kijunSen)
    senkouSpan_A = pd.DataFrame(columns=['Senkou Span A'], data=senkouSpan_A)
    senkouSpan_B = pd.DataFrame(columns=['Senkou Span B'], data=senkouSpan_B)
    indiBuyEntry = pd.DataFrame(columns=['Buy Entry Confirmation 1'], data=indiBuyEntry)
    indiSellEntry = pd.DataFrame(columns=['Sell Entry Confirmation 1'], data=indiSellEntry)
    candleEngulfing = pd.DataFrame(columns=['Engulfing Candle'], data=candleEngulfing)
    candlePiercing = pd.DataFrame(columns=['Piercing Candle'], data=candlePiercing)
    candleMorningStar = pd.DataFrame(columns=['Morning Star'], data=candleMorningStar)
    candle3WhiteSoldiers = pd.DataFrame(columns=['3 White Soldiers'], data=candle3WhiteSoldiers)
    candleShootingStar = pd.DataFrame(columns=['Shooting Star'], data=candleShootingStar)
    candleEveningStar = pd.DataFrame(columns=['Evening Star'], data=candleEveningStar)
    candleDarkCloudCover = pd.DataFrame(columns=['Dark Cloud Cover'], data=candleDarkCloudCover)
    candle3BlackCrows = pd.DataFrame(columns=['3 Black Crows'], data=candle3BlackCrows)


    
    jump = pd.concat([df,tenkanSen, kijunSen, senkouSpan_A, senkouSpan_B, 
                        indiBuyEntry, indiSellEntry, candleEngulfing, candlePiercing, candleMorningStar, candle3WhiteSoldiers,
                        candleShootingStar, candleEveningStar, candleDarkCloudCover, candle3BlackCrows], axis=1)
    jump.to_csv('Next.csv')
    """
    #print('................')
    
    
    
    
    
    
    
    
    
    
    
    
    
    

    



###############################################
# 3. Logic for Loop
"""
    * Create Loop to Repeat Steps 1 & 2 for Each Currency Pair in Defined in Steps 0 & 1
    * Once All Currency Pairs Have Been Checked For That Hour, Go Back to Timer Loop in Step 1
        * Needs to Start Again in the Next Hour
"""










###################################################
# Not needed for now
"""
# list of requests
lor = []

# request trades list
lor.append(trades.TradesList(accountID))

# request account list
lor.append(accounts.AccountList())

# request pricing info
params = {"instruments": "DE30_EUR, EUR_GBP"}
lor.append(pricing.PricingInfo(accountID, params= params))


for r in lor:
    try:
        rv = client.request(r)
        # put request and response in 1 JSON structure
        print("{}".format(json.dumps({"request": "{}".format(r),
                                     "response": rv}, indent= 2)))
    
    except V20Error as e:
        print("OOPS: {:d} {:s}".format(e.code, e.msg))
        
"""










