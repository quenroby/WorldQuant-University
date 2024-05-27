from oanda_backtest import Backtest
from pathlib import Path
import pandas as pd
import talib as ta
import numpy as np
import os

##################################################
# 1. Setting intial parameters
access_token = "2c8d32a134f3450b3a32ea04d5ef75d3-6bd075399bc865ab3fa3a771ce7846f5"
bt = Backtest(access_token=access_token, environment='practice')

path = str(Path(__file__).parent.absolute())
path=path.replace("\\","\\\\")

results = []

###################################################
# 2. Getting the pairs to test stragety on
fx_pairs = 'AUDJPY CADJPY CHFJPY EURJPY NZDJPY USDJPY GBPJPY AUDUSD EURUSD GBPUSD NZDUSD USDCAD USDCHF AUDCAD CADCHF EURCAD GBPCAD NZDCAD AUDCHF EURCHF GBPCHF NZDCHF EURAUD EURGBP EURNZD GBPNZD GBPAUD AUDNZD'
#fx_pairs = 'AUDNZD'
fx_pairs = fx_pairs.replace(' ','')
run_Pairs = (len(fx_pairs)-1)

while len(fx_pairs)>0: 
    string=fx_pairs[-6:]
    fx_pairs=fx_pairs[0:-6]
    dummyString = string[0:3] + "_" + string[3:6]
    
    
    params = {
        "granularity": "D",  # Daily candlesticks 
        "count": 3000 # 3000 candlesticks --> 3000 days data
    }
    
    bt.candles(dummyString, params)
    bt.to_csv(path+'\\Forex_BackTest\\'+string+'.csv')
    df = pd.read_csv(path+'\\Forex_BackTest\\'+string+'.csv')

######################################
# 4. Setting up the indicators to test the straetgy before going live
    # Tenkan-sen (Conversion Line): (9-period high + 9-period low)/2))
    nine_period_high = df['H'].rolling(window= 9).max()
    nine_period_low = df['L'].rolling(window= 9).min()
    tenkanSen = (nine_period_high + nine_period_low) /2
    
    # Kijun-sen (Base Line): (26-period high + 26-period low)/2))
    period26_high = df['H'].rolling(window=26).max()
    period26_low = df['L'].rolling(window=26).min()
    kijunSen = (period26_high + period26_low) / 2
    
    # Senkou Span A (Leading Span A): (Conversion Line + Base Line)/2))
    senkouSpan_A = ((tenkanSen + kijunSen) / 2).shift(26)
    
    # Senkou Span B (Leading Span B): (52-period high + 52-period low)/2))
    period52_high = df['H'].rolling(window=52).max()
    period52_low = df['L'].rolling(window=52).min()
    senkouSpan_B = ((period52_high + period52_low) / 2).shift(26)
    
    #Candlestick Patterns
    # BULLISH
    candleEngulfing = ta.CDLENGULFING(df['O'], df['H'], df['L'], df['C'])  #(+100 is bullish engulfing and -100 is bearish engulfing)
    candlePiercing = ta.CDLPIERCING(df['O'], df['H'], df['L'], df['L'])    #(+100 is confirmation of a piercing line)
    candleMorningStar = ta.CDLMORNINGSTAR(df['O'], df['H'], df['L'], df['C'], penetration=0) #(+100 is confirmation of a morning star)
    candle3WhiteSoldiers = ta.CDL3WHITESOLDIERS(df['O'], df['H'], df['L'], df['C'])
    
    #BEARISH
    candleShootingStar = ta.CDLSHOOTINGSTAR(df['O'], df['H'], df['L'], df['C'])
    candleEveningStar = ta.CDLEVENINGSTAR(df['O'], df['H'], df['L'], df['C'], penetration=0)
    candleDarkCloudCover = ta.CDLDARKCLOUDCOVER(df['O'], df['H'], df['L'], df['C'], penetration=0)
    candle3BlackCrows = ta.CDL3BLACKCROWS(df['O'], df['H'], df['L'], df['C'])

    indiBuyEntry = np.logical_and(np.logical_and(tenkanSen > kijunSen, tenkanSen > senkouSpan_A), tenkanSen > senkouSpan_B)
    indiSellEntry = np.logical_and(np.logical_and(tenkanSen < kijunSen, tenkanSen < senkouSpan_A), tenkanSen < senkouSpan_B)

#######################################################
# 4. Entry and Exit Logic  
    bt.buy_entry = np.logical_and(indiBuyEntry, ((candleEngulfing == 100) | (candlePiercing == 100) | (candleMorningStar == 100) | (candle3WhiteSoldiers == 100)))
    bt.sell_entry = np.logical_and(indiSellEntry, ((candleEngulfing == -100) | (candleShootingStar == -100) | (candleEveningStar == -100) | (candleDarkCloudCover == -100) | (candle3BlackCrows == -100)))
  
    bt.buy_exit = (tenkanSen < kijunSen) | (tenkanSen < senkouSpan_A) | (tenkanSen < senkouSpan_B)
    bt.sell_exit = (tenkanSen > kijunSen) | (tenkanSen > senkouSpan_A) | (tenkanSen > senkouSpan_B)  
    
  
########################################################
# 5. Portfolio $100,000 and buying 1000 units of the currency with a 2 to 1 risk to reward ratio
    bt.initial_deposit = 100000 # default=0
    bt.units = 1000 # currency unit (default=10000)
    bt.stop_loss = 50 # stop loss pips (default=0)
    bt.take_profit = 100 # take profit pips (default=0)
    
    
    results.append(bt.run())
    #bt.plot(dummyString+".png")
    

results1 = pd.DataFrame(results, index=['AUDJPY', 'CADJPY', 'CHFJPY', 'EURJPY', 'NZDJPY', 'USDJPY', 'GBPJPY', 'AUDUSD', 'EURUSD', 'GBPUSD', 'NZDUSD', 'USDCAD', 'USDCHF', 'AUDCAD', 'CADCHF', 'EURCAD', 'GBPCAD', 'NZDCAD', 'AUDCHF', 'EURCHF', 'GBPCHF', 'NZDCHF', 'EURAUD', 'EURGBP', 'EURNZD', 'GBPNZD', 'GBPAUD', 'AUDNZD'])
results1.to_csv('results.csv')


